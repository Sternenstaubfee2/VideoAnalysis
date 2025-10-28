"""
Database handler for poker game analysis
Manages player master data (stammdaten) and player-specific transaction tables
"""

import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import os


class PokerDatabase:
    def __init__(self, db_path: str = "poker_data.db"):
        """Initialize database connection and create tables if needed"""
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._create_stammdaten_table()

    def _create_stammdaten_table(self):
        """Create the master data table for player information"""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS stammdaten (
                player_id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_name TEXT UNIQUE NOT NULL,
                country TEXT,
                first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_hands_played INTEGER DEFAULT 0,
                total_winnings REAL DEFAULT 0.0
            )
        """)
        self.conn.commit()

    def _create_player_transaction_table(self, player_name: str):
        """Create a transaction table for a specific player"""
        # Sanitize table name (replace spaces and special chars with underscore)
        table_name = self._sanitize_table_name(player_name)

        self.cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS "{table_name}" (
                transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                game_id TEXT,
                hand_number INTEGER,
                position TEXT,
                starting_stack REAL,
                big_blind REAL,
                small_blind REAL,
                action_preflop TEXT,
                action_flop TEXT,
                action_turn TEXT,
                action_river TEXT,
                cards_dealt TEXT,
                cards_shown TEXT,
                final_stack REAL,
                net_winloss REAL,
                pot_size REAL,
                win_loss_flag TEXT,
                notes TEXT
            )
        """)
        self.conn.commit()
        return table_name

    def _sanitize_table_name(self, name: str) -> str:
        """Convert player name to valid table name"""
        # Replace special characters with underscore
        sanitized = ''.join(c if c.isalnum() else '_' for c in name)
        # Ensure it doesn't start with a number
        if sanitized[0].isdigit():
            sanitized = 'player_' + sanitized
        return sanitized

    def add_or_update_player(self, player_name: str, country: Optional[str] = None) -> int:
        """Add a new player or update existing player information"""
        try:
            # Try to insert new player
            self.cursor.execute("""
                INSERT INTO stammdaten (player_name, country)
                VALUES (?, ?)
            """, (player_name, country))
            player_id = self.cursor.lastrowid
            self.conn.commit()

            # Create transaction table for new player
            self._create_player_transaction_table(player_name)

        except sqlite3.IntegrityError:
            # Player already exists, update last_seen
            self.cursor.execute("""
                UPDATE stammdaten
                SET last_seen = CURRENT_TIMESTAMP
                WHERE player_name = ?
            """, (player_name,))

            # Get player_id
            self.cursor.execute("""
                SELECT player_id FROM stammdaten WHERE player_name = ?
            """, (player_name,))
            player_id = self.cursor.fetchone()[0]

            # Update country if provided and different
            if country:
                self.cursor.execute("""
                    UPDATE stammdaten
                    SET country = ?
                    WHERE player_name = ? AND (country IS NULL OR country != ?)
                """, (country, player_name, country))

            self.conn.commit()

        return player_id

    def add_transaction(self, player_name: str, transaction_data: Dict):
        """Add a transaction record for a specific player"""
        table_name = self._sanitize_table_name(player_name)

        # Ensure player exists in stammdaten
        self.add_or_update_player(player_name, transaction_data.get('country'))

        # Insert transaction
        columns = ', '.join(transaction_data.keys())
        placeholders = ', '.join(['?' for _ in transaction_data])
        values = tuple(transaction_data.values())

        self.cursor.execute(f"""
            INSERT INTO "{table_name}" ({columns})
            VALUES ({placeholders})
        """, values)

        # Update stammdaten statistics
        net_winloss = transaction_data.get('net_winloss', 0.0)
        self.cursor.execute("""
            UPDATE stammdaten
            SET total_hands_played = total_hands_played + 1,
                total_winnings = total_winnings + ?,
                last_seen = CURRENT_TIMESTAMP
            WHERE player_name = ?
        """, (net_winloss, player_name))

        self.conn.commit()

    def get_player_stats(self, player_name: str) -> Optional[Dict]:
        """Get statistics for a specific player"""
        self.cursor.execute("""
            SELECT * FROM stammdaten WHERE player_name = ?
        """, (player_name,))

        row = self.cursor.fetchone()
        if row:
            columns = [description[0] for description in self.cursor.description]
            return dict(zip(columns, row))
        return None

    def get_player_transactions(self, player_name: str, limit: Optional[int] = None) -> List[Dict]:
        """Get transaction history for a specific player"""
        table_name = self._sanitize_table_name(player_name)

        query = f'SELECT * FROM "{table_name}" ORDER BY transaction_id DESC'
        if limit:
            query += f' LIMIT {limit}'

        self.cursor.execute(query)
        rows = self.cursor.fetchall()

        columns = [description[0] for description in self.cursor.description]
        return [dict(zip(columns, row)) for row in rows]

    def get_all_players(self) -> List[Dict]:
        """Get all players from stammdaten"""
        self.cursor.execute("""
            SELECT * FROM stammdaten ORDER BY total_hands_played DESC
        """)

        rows = self.cursor.fetchall()
        columns = [description[0] for description in self.cursor.description]
        return [dict(zip(columns, row)) for row in rows]

    def close(self):
        """Close database connection"""
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


if __name__ == "__main__":
    # Test the database
    with PokerDatabase("poker_data.db") as db:
        # Add some test players
        db.add_or_update_player("TestPlayer1", "USA")
        db.add_or_update_player("TestPlayer2", "Germany")

        # Add a test transaction
        transaction = {
            "game_id": "TEST001",
            "hand_number": 1,
            "position": "BTN",
            "starting_stack": 100.0,
            "big_blind": 2.0,
            "small_blind": 1.0,
            "action_preflop": "Raise",
            "final_stack": 110.0,
            "net_winloss": 10.0,
            "win_loss_flag": "WIN"
        }
        db.add_transaction("TestPlayer1", transaction)

        print("Players:", db.get_all_players())
        print("TestPlayer1 stats:", db.get_player_stats("TestPlayer1"))
        print("TestPlayer1 transactions:", db.get_player_transactions("TestPlayer1"))
