"""
Main Poker Analyzer
Integrates video analysis with database storage for complete poker game tracking
"""

import cv2
import os
from typing import Dict, List, Optional
from datetime import datetime
import json

from database_handler import PokerDatabase
from poker_video_analyzer import PokerVideoAnalyzer, GameState, Player, PlayerAction
from config import find_tesseract


class MainPokerAnalyzer:
    def __init__(self, video_path: str, db_path: str = "poker_data.db",
                 tesseract_path: Optional[str] = None):
        """
        Initialize the main poker analyzer

        Args:
            video_path: Path to the poker video
            db_path: Path to SQLite database
            tesseract_path: Optional path to tesseract executable
        """
        self.video_path = video_path
        self.db = PokerDatabase(db_path)
        self.analyzer = PokerVideoAnalyzer(video_path, tesseract_path)

        # Track game hands
        self.hands: List[Dict] = []
        self.current_hand: Optional[Dict] = None
        self.hand_counter = 0

    def _initialize_hand(self, game_state: GameState) -> Dict:
        """Initialize a new hand with game state"""
        self.hand_counter += 1

        hand = {
            'hand_number': self.hand_counter,
            'timestamp': datetime.now().isoformat(),
            'game_id': f"VIDEO_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'big_blind': game_state.big_blind,
            'small_blind': game_state.small_blind,
            'players': {},
            'pot_size': game_state.pot_size,
            'actions': [],
            'winner': None,
            'total_pot': 0.0
        }

        # Initialize player data
        for player in game_state.players:
            hand['players'][player.name] = {
                'name': player.name,
                'country': player.country,
                'starting_stack': player.stack,
                'final_stack': player.stack,
                'position': f"Seat_{player.seat_number}",
                'actions_preflop': [],
                'actions_flop': [],
                'actions_turn': [],
                'actions_river': [],
                'cards_dealt': None,
                'cards_shown': None,
                'net_winloss': 0.0,
                'win_loss_flag': 'PENDING'
            }

        return hand

    def _update_hand_state(self, hand: Dict, game_state: GameState):
        """Update hand state with new game state information"""
        # Update pot size
        if game_state.pot_size > 0:
            hand['pot_size'] = game_state.pot_size

        # Update player stacks
        for player in game_state.players:
            if player.name in hand['players']:
                hand['players'][player.name]['final_stack'] = player.stack

        # Record actions
        for action in game_state.actions:
            if action.player_name in hand['players']:
                action_data = {
                    'action': action.action,
                    'amount': action.amount,
                    'street': action.street
                }
                hand['actions'].append(action_data)

                # Add to appropriate street
                street_key = f"actions_{action.street}"
                if street_key in hand['players'][action.player_name]:
                    hand['players'][action.player_name][street_key].append(action.action)

    def _finalize_hand(self, hand: Dict):
        """Calculate final results for a hand"""
        # Calculate win/loss for each player
        for player_name, player_data in hand['players'].items():
            starting = player_data['starting_stack']
            final = player_data['final_stack']
            net_winloss = final - starting

            player_data['net_winloss'] = net_winloss

            if net_winloss > 0:
                player_data['win_loss_flag'] = 'WIN'
                if hand['winner'] is None:
                    hand['winner'] = player_name
            elif net_winloss < 0:
                player_data['win_loss_flag'] = 'LOSS'
            else:
                player_data['win_loss_flag'] = 'BREAK_EVEN'

        hand['total_pot'] = hand['pot_size']

    def _save_hand_to_database(self, hand: Dict):
        """Save hand data to database"""
        for player_name, player_data in hand['players'].items():
            # Ensure player exists in stammdaten
            self.db.add_or_update_player(player_name, player_data['country'])

            # Prepare transaction data
            transaction = {
                'timestamp': hand['timestamp'],
                'game_id': hand['game_id'],
                'hand_number': hand['hand_number'],
                'position': player_data['position'],
                'starting_stack': player_data['starting_stack'],
                'big_blind': hand['big_blind'],
                'small_blind': hand['small_blind'],
                'action_preflop': ', '.join(player_data['actions_preflop']) if player_data['actions_preflop'] else None,
                'action_flop': ', '.join(player_data['actions_flop']) if player_data['actions_flop'] else None,
                'action_turn': ', '.join(player_data['actions_turn']) if player_data['actions_turn'] else None,
                'action_river': ', '.join(player_data['actions_river']) if player_data['actions_river'] else None,
                'cards_dealt': player_data['cards_dealt'],
                'cards_shown': player_data['cards_shown'],
                'final_stack': player_data['final_stack'],
                'net_winloss': player_data['net_winloss'],
                'pot_size': hand['total_pot'],
                'win_loss_flag': player_data['win_loss_flag'],
                'notes': f"Winner: {hand['winner']}" if hand['winner'] else None
            }

            # Add transaction to player's table
            self.db.add_transaction(player_name, transaction)

    def _detect_hand_boundaries(self, game_states: List[GameState]) -> List[List[GameState]]:
        """
        Group game states into hands
        This is a heuristic approach - detecting new hands based on:
        - Significant changes in player stacks
        - Changes in player composition
        - Reset of pot size
        """
        if not game_states:
            return []

        hands = []
        current_hand_states = [game_states[0]]

        for i in range(1, len(game_states)):
            current_state = game_states[i]
            previous_state = game_states[i-1]

            # Check for hand boundary indicators
            new_hand = False

            # 1. Player composition changed significantly
            if len(current_state.players) != len(previous_state.players):
                new_hand = True

            # 2. Pot reset to zero or small amount
            if current_state.pot_size < previous_state.pot_size * 0.1:
                new_hand = True

            # 3. Blinds changed
            if (current_state.big_blind != previous_state.big_blind and
                current_state.big_blind > 0):
                new_hand = True

            if new_hand and len(current_hand_states) > 2:
                hands.append(current_hand_states)
                current_hand_states = [current_state]
            else:
                current_hand_states.append(current_state)

        # Add final hand
        if current_hand_states:
            hands.append(current_hand_states)

        return hands

    def analyze_video(self, sample_rate: int = 30, save_debug: bool = False):
        """
        Analyze the entire video and save to database

        Args:
            sample_rate: Process every Nth frame
            save_debug: Save debug images
        """
        print("=" * 60)
        print("POKER VIDEO ANALYSIS")
        print("=" * 60)
        print(f"Video: {self.video_path}")
        print(f"Database: {self.db.db_path}")
        print()

        # Process video
        print("Step 1: Processing video frames...")
        debug_dir = "debug_frames" if save_debug else None
        if debug_dir and not os.path.exists(debug_dir):
            os.makedirs(debug_dir)

        game_states = self.analyzer.process_video(sample_rate, debug_dir)

        print(f"\nExtracted {len(game_states)} game states from video")

        # Group into hands
        print("\nStep 2: Detecting hand boundaries...")
        hand_groups = self._detect_hand_boundaries(game_states)
        print(f"Detected {len(hand_groups)} hands")

        # Process each hand
        print("\nStep 3: Processing hands and saving to database...")
        for hand_idx, hand_states in enumerate(hand_groups):
            if not hand_states:
                continue

            # Initialize hand with first state
            hand = self._initialize_hand(hand_states[0])

            # Update with subsequent states
            for game_state in hand_states[1:]:
                self._update_hand_state(hand, game_state)

            # Finalize and save
            self._finalize_hand(hand)
            self._save_hand_to_database(hand)
            self.hands.append(hand)

            print(f"  Hand {hand_idx + 1}/{len(hand_groups)}: "
                  f"{len(hand['players'])} players, "
                  f"Pot: ${hand['total_pot']:.2f}, "
                  f"Winner: {hand['winner']}")

        print("\n" + "=" * 60)
        print("ANALYSIS COMPLETE")
        print("=" * 60)

    def generate_report(self, output_file: str = "poker_analysis_report.txt"):
        """Generate a detailed report of the analysis"""
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("POKER VIDEO ANALYSIS REPORT")
        report_lines.append("=" * 80)
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"Video: {self.video_path}")
        report_lines.append(f"Total Hands Analyzed: {len(self.hands)}")
        report_lines.append("")

        # Player statistics
        report_lines.append("-" * 80)
        report_lines.append("PLAYER STATISTICS")
        report_lines.append("-" * 80)

        all_players = self.db.get_all_players()
        for player in all_players:
            report_lines.append(f"\nPlayer: {player['player_name']}")
            report_lines.append(f"  Country: {player['country']}")
            report_lines.append(f"  Hands Played: {player['total_hands_played']}")
            report_lines.append(f"  Total Win/Loss: ${player['total_winnings']:.2f}")

            # Get recent transactions
            transactions = self.db.get_player_transactions(player['player_name'], limit=5)
            if transactions:
                report_lines.append(f"  Recent Hands:")
                for trans in transactions[:5]:
                    report_lines.append(
                        f"    Hand #{trans['hand_number']}: "
                        f"{trans['win_loss_flag']} "
                        f"(${trans['net_winloss']:+.2f})"
                    )

        # Hand-by-hand breakdown
        report_lines.append("\n" + "-" * 80)
        report_lines.append("HAND-BY-HAND BREAKDOWN")
        report_lines.append("-" * 80)

        for hand in self.hands:
            report_lines.append(f"\nHand #{hand['hand_number']}")
            report_lines.append(f"  Blinds: ${hand['small_blind']:.2f}/${hand['big_blind']:.2f}")
            report_lines.append(f"  Pot: ${hand['total_pot']:.2f}")
            report_lines.append(f"  Winner: {hand['winner']}")
            report_lines.append(f"  Players:")
            for player_name, player_data in hand['players'].items():
                report_lines.append(
                    f"    {player_name}: "
                    f"${player_data['starting_stack']:.2f} → ${player_data['final_stack']:.2f} "
                    f"({player_data['win_loss_flag']})"
                )

        report_text = "\n".join(report_lines)

        # Save to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report_text)

        print(f"\nReport saved to: {output_file}")
        return report_text

    def export_hands_json(self, output_file: str = "poker_hands.json"):
        """Export all hands to JSON format"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.hands, f, indent=2)
        print(f"Hands exported to: {output_file}")

    def close(self):
        """Clean up resources"""
        self.db.close()
        self.analyzer.release()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Analyze poker video and extract game data')
    parser.add_argument('video', help='Path to poker video file')
    parser.add_argument('--db', default='poker_data.db', help='Database path')
    parser.add_argument('--tesseract', help='Path to tesseract executable')
    parser.add_argument('--sample-rate', type=int, default=30,
                       help='Process every Nth frame (default: 30)')
    parser.add_argument('--debug', action='store_true',
                       help='Save debug frames')
    parser.add_argument('--report', default='poker_analysis_report.txt',
                       help='Output report file')

    args = parser.parse_args()

    # Auto-detect tesseract if not provided
    tesseract_path = args.tesseract or find_tesseract()
    if not tesseract_path:
        print("ERROR: Tesseract not found!")
        print("Please install Tesseract OCR. See INSTALL_TESSERACT.md")
        exit(1)

    print(f"Using Tesseract: {tesseract_path}")

    # Run analysis
    with MainPokerAnalyzer(args.video, args.db, tesseract_path) as analyzer:
        analyzer.analyze_video(sample_rate=args.sample_rate, save_debug=args.debug)
        analyzer.generate_report(args.report)
        analyzer.export_hands_json()

    print("\n✓ Analysis complete!")
    print(f"✓ Database: {args.db}")
    print(f"✓ Report: {args.report}")


if __name__ == "__main__":
    # Quick test mode
    video_path = r"C:\Users\Julia\Downloads\Spin_and_Go.mp4"
    tesseract_path = find_tesseract()

    if not tesseract_path:
        print("ERROR: Tesseract not found!")
        print("Please install Tesseract OCR. See INSTALL_TESSERACT.md")
        exit(1)

    print(f"Using Tesseract: {tesseract_path}")

    with MainPokerAnalyzer(video_path, db_path="poker_data.db", tesseract_path=tesseract_path) as analyzer:
        analyzer.analyze_video(sample_rate=30, save_debug=False)
        report = analyzer.generate_report()
        print("\n" + "=" * 80)
        print(report)
