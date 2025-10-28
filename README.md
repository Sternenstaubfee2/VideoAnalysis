# Poker Video Analyzer

Automatically extracts poker game data from GG Poker videos using OCR and computer vision.

## Features

- 📹 Processes poker game videos frame-by-frame
- 🔍 Extracts player information (names, countries, chip stacks)
- 🎯 Detects player actions (Fold, Call, Raise, etc.)
- 💰 Tracks pot sizes and win/loss calculations
- 💾 Stores data in structured SQLite database
  - `stammdaten` table: Master player data
  - Player-specific tables: Transaction history for each player
- 📊 Generates detailed analysis reports

## Prerequisites

### 1. Install Tesseract OCR

Tesseract is required for text recognition in the video.

**Windows:**
- Download from: https://github.com/UB-Mannheim/tesseract/wiki
- Install to default location: `C:\Program Files\Tesseract-OCR\`
- Add to system PATH (optional but recommended)

**Alternative locations:** The script will automatically check:
- `C:\Program Files\Tesseract-OCR\tesseract.exe`
- `C:\Program Files (x86)\Tesseract-OCR\tesseract.exe`
- `C:\Users\Julia\AppData\Local\Programs\Tesseract-OCR\tesseract.exe`

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- opencv-python (video processing)
- pytesseract (OCR)
- numpy (numerical operations)
- Pillow (image processing)
- pandas (data processing)

## Quick Start

### Basic Usage

```bash
python main_poker_analyzer.py
```

This will:
1. Process the video at `C:\Users\Julia\Downloads\Spin_and_Go.mp4`
2. Create `poker_data.db` database
3. Generate `poker_analysis_report.txt`
4. Export hands to `poker_hands.json`

### Command Line Options

```bash
python main_poker_analyzer.py <video_path> [options]

Options:
  --db PATH              Database path (default: poker_data.db)
  --tesseract PATH       Path to tesseract executable
  --sample-rate N        Process every Nth frame (default: 30)
  --debug                Save debug frames for inspection
  --report PATH          Output report file path
```

### Examples

```bash
# Process with custom sample rate
python main_poker_analyzer.py video.mp4 --sample-rate 15

# Save debug frames
python main_poker_analyzer.py video.mp4 --debug

# Use custom tesseract path
python main_poker_analyzer.py video.mp4 --tesseract "C:\Tesseract\tesseract.exe"
```

## Database Structure

### stammdaten Table (Player Master Data)
- `player_id`: Unique identifier
- `player_name`: Player name
- `country`: Player country
- `first_seen`: First appearance timestamp
- `last_seen`: Last appearance timestamp
- `total_hands_played`: Total hands count
- `total_winnings`: Cumulative win/loss

### Player Transaction Tables
Each player gets their own table (e.g., `PlayerName` or `player_name`) with:
- `transaction_id`: Unique transaction ID
- `timestamp`: When the hand was played
- `game_id`: Game identifier
- `hand_number`: Hand number
- `position`: Player position (seat)
- `starting_stack`: Stack at hand start
- `big_blind`, `small_blind`: Blind amounts
- `action_preflop`, `action_flop`, `action_turn`, `action_river`: Actions per street
- `cards_dealt`, `cards_shown`: Card information
- `final_stack`: Stack at hand end
- `net_winloss`: Net profit/loss for the hand
- `pot_size`: Total pot size
- `win_loss_flag`: WIN, LOSS, or BREAK_EVEN
- `notes`: Additional notes

## Configuration

Edit `config.py` to adjust:
- Tesseract path
- Video processing settings
- ROI (Region of Interest) coordinates for UI elements
- OCR parameters
- Hand detection thresholds

### Calibrating ROI Regions

If the default regions don't match your video:

1. Set `CALIBRATION_MODE = True` in `config.py`
2. Run the analyzer with `--debug` flag
3. Check saved frames in `calibration_frames/` directory
4. Adjust coordinates in `PLAYER_REGIONS` and `GAME_INFO_REGIONS`

Coordinates are specified as `(x, y, width, height)` where:
- Values are percentages of screen (0.0 to 1.0)
- `(0.5, 0.5, 0.1, 0.1)` = center of screen, 10% width/height

## Project Structure

```
VideoAnalysis/
│
├── main_poker_analyzer.py      # Main entry point
├── poker_video_analyzer.py     # Video processing and OCR
├── database_handler.py         # Database operations
├── config.py                   # Configuration settings
├── requirements.txt            # Python dependencies
├── README.md                   # This file
│
├── poker_data.db              # SQLite database (generated)
├── poker_analysis_report.txt  # Analysis report (generated)
├── poker_hands.json           # JSON export (generated)
└── debug_frames/              # Debug images (if --debug used)
```

## Troubleshooting

### Tesseract Not Found
- Install Tesseract from the link above
- Verify installation: `tesseract --version`
- Update `TESSERACT_PATH` in `config.py`

### Poor OCR Accuracy
- Increase video quality/resolution
- Adjust `IMAGE_SCALE_FACTOR` in config.py
- Calibrate ROI regions for your specific video
- Use lower `--sample-rate` for more frames

### Database Errors
- Check write permissions in directory
- Verify database isn't locked by another process
- Delete `poker_data.db` to start fresh

### Video Won't Open
- Ensure video codec is supported (MP4/H.264 recommended)
- Check file path is correct
- Try converting video with ffmpeg

## Advanced Usage

### Accessing Database Programmatically

```python
from database_handler import PokerDatabase

with PokerDatabase("poker_data.db") as db:
    # Get all players
    players = db.get_all_players()

    # Get specific player stats
    stats = db.get_player_stats("PlayerName")

    # Get player transactions
    transactions = db.get_player_transactions("PlayerName", limit=10)
```

### Custom Analysis

```python
from main_poker_analyzer import MainPokerAnalyzer

with MainPokerAnalyzer("video.mp4") as analyzer:
    analyzer.analyze_video(sample_rate=15)
    analyzer.generate_report("custom_report.txt")

    # Access hands directly
    for hand in analyzer.hands:
        print(f"Hand {hand['hand_number']}: Winner = {hand['winner']}")
```

## Limitations

- Currently optimized for GG Poker 3-player Spin & Go format
- Requires good video quality for accurate OCR
- ROI regions may need calibration for different screen resolutions
- Card recognition at showdown requires clear visibility

## Future Enhancements

- [ ] Automatic ROI calibration
- [ ] Support for 6-max and 9-max tables
- [ ] Card recognition using computer vision
- [ ] Real-time video streaming analysis
- [ ] Tournament tracking with multiple tables
- [ ] Hand range analysis
- [ ] Integration with poker tracking software

## License

This tool is for personal use and analysis purposes only.

## Support

For issues or questions, please check:
1. Tesseract is properly installed
2. Video format is compatible
3. ROI regions are calibrated correctly
4. All dependencies are installed

## Credits

Developed for poker game analysis and tracking.
