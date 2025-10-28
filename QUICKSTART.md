# Quick Start Guide - Poker Video Analyzer

Get started analyzing your poker videos in 3 easy steps!

## Step 1: Install Tesseract OCR (Required)

Tesseract is the only external dependency you need to install.

**Quick Install:**
1. Download: https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.3.3.20231005.exe
2. Run installer, use default location: `C:\Program Files\Tesseract-OCR`
3. Done!

See `INSTALL_TESSERACT.md` for detailed instructions.

## Step 2: Verify Setup

```bash
python check_setup.py
```

This will verify:
- ✓ Python packages installed
- ✓ Tesseract OCR installed
- ✓ Video file accessible
- ✓ Video can be read

## Step 3: Analyze Your Video

### Option A: Use the Quick Launcher (Easiest)

```bash
run_analyzer.bat
```

### Option B: Run Python Script Directly

```bash
python main_poker_analyzer.py
```

### Option C: Custom Options

```bash
# Process every 15 frames (faster but less accurate)
python main_poker_analyzer.py --sample-rate 15

# Save debug frames for inspection
python main_poker_analyzer.py --debug

# Use custom video path
python main_poker_analyzer.py "C:\path\to\your\video.mp4"
```

## What Gets Created?

After analysis, you'll find:

1. **poker_data.db** - SQLite database with all extracted data
   - `stammdaten` table: Player master data
   - Player-specific tables: Transaction history

2. **poker_analysis_report.txt** - Human-readable analysis report
   - Player statistics
   - Hand-by-hand breakdown
   - Win/loss summary

3. **poker_hands.json** - JSON export of all hands (for further processing)

## Viewing the Results

### View the Report

```bash
notepad poker_analysis_report.txt
```

### Query the Database

```python
from database_handler import PokerDatabase

with PokerDatabase("poker_data.db") as db:
    # Get all players
    players = db.get_all_players()
    for player in players:
        print(f"{player['player_name']}: ${player['total_winnings']:.2f}")

    # Get transactions for a specific player
    transactions = db.get_player_transactions("PlayerName", limit=10)
    for trans in transactions:
        print(f"Hand {trans['hand_number']}: {trans['win_loss_flag']}")
```

### Open Database in DB Browser

Download DB Browser for SQLite: https://sqlitebrowser.org/
1. Open `poker_data.db`
2. Browse tables: `stammdaten` and player tables
3. Run SQL queries

## Calibration (If Needed)

If OCR accuracy is poor or regions don't match:

1. **Extract sample frames:**
   ```bash
   python test_video_extract.py
   ```

2. **Check debug images:**
   - Open `sample_frames/debug_*.jpg`
   - Verify green boxes align with player names, stacks, etc.

3. **Adjust ROI regions:**
   - Edit `config.py`
   - Update coordinates in `PLAYER_REGIONS` and `GAME_INFO_REGIONS`
   - Coordinates are (x, y, width, height) as percentages (0.0 to 1.0)

4. **Re-run analysis**

## Troubleshooting

### "Tesseract not found"
- Install Tesseract (see Step 1)
- Or update path in `config.py`

### "No module named 'cv2'"
```bash
pip install -r requirements.txt
```

### "Cannot open video file"
- Check video path in `config.py`
- Try different video codec (MP4/H.264 recommended)

### Poor OCR accuracy
- Increase video resolution
- Adjust `IMAGE_SCALE_FACTOR` in `config.py`
- Calibrate ROI regions (see above)

### Database locked
- Close any programs accessing `poker_data.db`
- Or delete and re-run analysis

## Performance Tips

1. **Faster processing:**
   - Increase `--sample-rate` (process fewer frames)
   - Default is 30 (every 30th frame)

2. **Better accuracy:**
   - Decrease `--sample-rate` (process more frames)
   - Use `--sample-rate 10` or lower

3. **Disk space:**
   - Don't use `--debug` unless needed
   - Debug mode saves every processed frame

## Understanding the Data

### Stammdaten Table (Master Data)
Each player has one entry with:
- Name and country
- Total hands played
- Total winnings/losses
- First and last seen timestamps

### Player Transaction Tables
Each hand played creates one transaction with:
- Starting and final stack
- Actions per street (preflop, flop, turn, river)
- Cards dealt/shown
- Net win/loss
- Pot size

## Example Queries

### Total profit/loss by player
```sql
SELECT player_name, total_winnings, total_hands_played
FROM stammdaten
ORDER BY total_winnings DESC;
```

### Biggest wins
```sql
SELECT * FROM "PlayerName"
WHERE win_loss_flag = 'WIN'
ORDER BY net_winloss DESC
LIMIT 10;
```

### Hands played per position
```sql
SELECT position, COUNT(*) as hands
FROM "PlayerName"
GROUP BY position;
```

## Next Steps

- Analyze more videos (they'll be added to the same database)
- Export data to Excel/CSV for further analysis
- Create custom reports and visualizations
- Track performance over time

## Support Files

- `README.md` - Full documentation
- `INSTALL_TESSERACT.md` - Detailed Tesseract installation
- `config.py` - Configuration and calibration
- `check_setup.py` - Verify installation
- `test_video_extract.py` - Extract sample frames

## Have Fun!

Enjoy analyzing your poker games and improving your strategy!
