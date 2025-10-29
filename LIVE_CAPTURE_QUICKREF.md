# Live Capture Quick Reference

## Quick Start (Easiest)

```bash
# Double-click this file:
run_live_capture.bat
```

Then select option 1 (Screen Capture) and press Enter!

---

## Command Line Usage

### Screen Capture (No OBS Required)
```bash
python live_capture_analyzer.py --method screen --interval 2.0
```

### OBS Virtual Camera
```bash
python live_capture_analyzer.py --method obs --interval 2.0
```

### Quick 10-Second Test
```bash
python test_live_capture.py quick
```

---

## All Options

```bash
python live_capture_analyzer.py [OPTIONS]

Options:
  --method screen|obs|window    Capture method (default: screen)
  --interval SECONDS           Seconds between captures (default: 2.0)
  --duration SECONDS           Run for X seconds (default: unlimited)
  --db PATH                    Database path (default: live_poker_data.db)
  --display-interval SECONDS   Console update interval (default: 2.0)
```

---

## Examples

```bash
# Capture every 1 second for maximum accuracy
python live_capture_analyzer.py --interval 1.0

# Run for 30 minutes (1800 seconds)
python live_capture_analyzer.py --duration 1800

# Use custom database name
python live_capture_analyzer.py --db "my_session.db"

# Fast mode (every 3 seconds)
python live_capture_analyzer.py --interval 3.0

# OBS capture, every 1.5 seconds, for 1 hour
python live_capture_analyzer.py --method obs --interval 1.5 --duration 3600
```

---

## What You'll See

```
======================================================================
LIVE POKER CAPTURE - REAL-TIME ANALYSIS
======================================================================
Status: RUNNING
Uptime: 45.3s

STATISTICS:
  Frames captured:  23
  Frames processed: 22
  Hands detected:   5
  Players tracked:  3
  Errors:           0

CURRENT GAME STATE:
  Pot: $12.50
  Blinds: $0.50/$1.00
  Players at table: 3

  PLAYERS:
    PlayerName1: $98.50
    PlayerName2: $105.00
    PlayerName3: $96.50

CONTROLS:
  Press Ctrl+C to stop
======================================================================
```

---

## During Capture

**To Stop:**
- Press `Ctrl+C` (will save everything and close cleanly)

**While Running:**
- Watch the console for real-time stats
- `Frames captured` should be increasing
- `Frames processed` should follow closely
- Check for any errors

**Performance:**
- CPU usage: ~20-30% (normal)
- If higher: increase `--interval` value
- If lagging: close other applications

---

## After Capture

### View Results

**Database file:** `live_poker_data.db`

**Query database:**
```python
from database_handler import PokerDatabase

with PokerDatabase("live_poker_data.db") as db:
    # Get all players
    players = db.get_all_players()
    for p in players:
        print(f"{p['player_name']}: {p['total_hands_played']} hands")
```

**Or use DB Browser:**
1. Download: https://sqlitebrowser.org/
2. Open `live_poker_data.db`
3. Browse tables and data

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Tesseract not found" | `pip install -r requirements.txt` |
| "No frames captured" | Make sure poker window is visible |
| "OBS camera not found" | Start Virtual Camera in OBS |
| High CPU usage | Increase `--interval` to 3.0 or 4.0 |
| OCR inaccurate | Check `OBS_SETUP_GUIDE.md` for calibration |
| Script won't stop | Press `Ctrl+C` (may take 2-3 seconds) |

---

## File Locations

```
VideoAnalysis/
├── live_capture_analyzer.py      # Main live capture script
├── run_live_capture.bat           # Quick launcher
├── test_live_capture.py           # Test scripts
├── OBS_SETUP_GUIDE.md            # Detailed OBS setup
├── live_poker_data.db            # Generated during capture
└── config.py                      # Adjust ROI regions here
```

---

## Tips for Best Results

1. **Resolution:** 1280x720 or higher
2. **Visibility:** Keep poker window visible and unobscured
3. **Stable:** Don't move/resize window during capture
4. **Lighting:** Avoid overlays that obscure text
5. **Testing:** Run `test_live_capture.py` first!

---

## Comparison with Video Analysis

| Feature | Live Capture | Video Analysis |
|---------|-------------|----------------|
| Speed | Real-time | Post-processing |
| Feedback | Immediate | After session |
| Accuracy | ~90% | ~95% |
| CPU | Moderate | High |
| Storage | Database only | Video + Database |
| **Use When** | Playing | Reviewing |

**Best Practice:** Use BOTH!
- Live capture during play for immediate feedback
- Video analysis after session for accurate review

---

## Next Steps

1. **Test it:**
   ```bash
   python test_live_capture.py quick
   ```

2. **Run a session:**
   ```bash
   python live_capture_analyzer.py --interval 2.0 --duration 600
   ```
   (10 minutes)

3. **Check results:**
   - Open `live_poker_data.db` in DB Browser
   - See tracked players and statistics

4. **Optimize:**
   - Adjust `--interval` based on performance
   - Calibrate ROI regions in `config.py` if needed

---

## Support

- Full guide: `OBS_SETUP_GUIDE.md`
- Video analysis: `QUICKSTART.md`
- General docs: `README.md`
- Configuration: `config.py`

**Ready to start?**
```bash
run_live_capture.bat
```

🎰 Happy analyzing!
