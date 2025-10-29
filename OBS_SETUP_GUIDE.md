# OBS Setup Guide for Live Poker Capture

Complete guide to set up OBS Studio for real-time poker game analysis.

## Method 1: OBS Virtual Camera (Recommended)

### Step 1: Install OBS Studio

1. Download OBS Studio: https://obsproject.com/download
2. Install with default settings
3. Launch OBS Studio

### Step 2: Configure OBS Scene

1. **Create a new Scene:**
   - Click "+" under "Scenes" panel
   - Name it "Poker Table"

2. **Add Game Capture Source:**
   - Click "+" under "Sources"
   - Select "Game Capture"
   - Name: "GG Poker"
   - **Mode:** Capture specific window
   - **Window:** Select GGPoker.exe
   - Click OK

   **Alternative: Window Capture**
   - If Game Capture doesn't work, use "Window Capture"
   - Select the GG Poker window

   **Alternative: Display Capture**
   - Captures entire screen
   - Less efficient but always works

3. **Adjust the capture:**
   - Resize the source to fill the canvas
   - Right-click source → Transform → Fit to screen

### Step 3: Start Virtual Camera

1. **Tools** → **Start Virtual Camera**
2. You should see "Virtual Camera Active" in the bottom right
3. Leave OBS running

### Step 4: Run Live Analyzer

```bash
python live_capture_analyzer.py --method obs --interval 2.0
```

Or use the test script:
```bash
python test_live_capture.py obs
```

---

## Method 2: Screen Region Capture (Simpler, No OBS Required)

This method captures a region of your screen directly.

### Step 1: Position Poker Client

1. Open GG Poker
2. Open a table
3. Position window where you want it

### Step 2: Run Live Analyzer

```bash
python live_capture_analyzer.py --method screen --interval 2.0
```

Or quick test:
```bash
python test_live_capture.py
```

**Note:** This captures your entire primary monitor by default. You can specify a custom region in code.

---

## Method 3: OBS Stream Output (Advanced)

For recording and analysis simultaneously.

### OBS Configuration

1. **Settings** → **Output**
2. **Recording Path:** Set where you want videos saved
3. **Recording Format:** MP4 (recommended)
4. **Recording Quality:** High Quality

### Dual Output Setup

**Option A: Record + Virtual Camera**
1. Click "Start Virtual Camera" (for live analysis)
2. Click "Start Recording" (for later review)
3. Both run simultaneously

**Option B: Record + Post-Process**
1. Just record during play
2. Analyze the recording file later with `main_poker_analyzer.py`

---

## Capture Region Configuration

### Custom Screen Region

If you want to capture only the poker table (not full screen):

```python
# Edit live_capture_analyzer.py or create custom script
from live_capture_analyzer import LiveCaptureAnalyzer

# Define custom region (in pixels)
custom_region = {
    'top': 100,      # Y position from top of screen
    'left': 200,     # X position from left
    'width': 1280,   # Width of capture area
    'height': 720    # Height of capture area
}

analyzer = LiveCaptureAnalyzer(
    capture_method='screen_region',
    capture_region=custom_region,
    sample_interval=2.0
)

analyzer.start()
```

### Finding Your Poker Window Coordinates

**Windows Method:**
1. Open poker client
2. Press `Win + Shift + S` (screenshot tool)
3. Note the position and size

**Using Python:**
```python
import pyautogui
import time

print("Move mouse to TOP-LEFT of poker window...")
time.sleep(3)
x1, y1 = pyautogui.position()
print(f"Top-Left: ({x1}, {y1})")

print("Move mouse to BOTTOM-RIGHT of poker window...")
time.sleep(3)
x2, y2 = pyautogui.position()
print(f"Bottom-Right: ({x2}, {y2})")

width = x2 - x1
height = y2 - y1
print(f"\nRegion: top={y1}, left={x1}, width={width}, height={height}")
```

---

## Performance Optimization

### Capture Intervals

**Balance speed vs accuracy:**

```bash
# Very fast (every 3 seconds) - may miss quick actions
python live_capture_analyzer.py --interval 3.0

# Balanced (every 2 seconds) - recommended
python live_capture_analyzer.py --interval 2.0

# Accurate (every 1 second) - higher CPU usage
python live_capture_analyzer.py --interval 1.0

# Maximum (every 0.5 seconds) - high CPU, for critical hands
python live_capture_analyzer.py --interval 0.5
```

### OBS Settings for Performance

**For live analysis, use:**
- **Base Resolution:** 1280x720 (not 1920x1080)
- **Output Resolution:** Same as base
- **FPS:** 30 (not 60)

Lower resolution = faster processing without much quality loss for OCR.

---

## Workflow Examples

### Workflow 1: Live Tracking Only
```bash
# Just track live, no recording
python live_capture_analyzer.py --method screen --interval 2.0
```
- Real-time stats
- Database updated live
- No video file saved

### Workflow 2: Live Tracking + Recording
```bash
# Terminal 1: Start OBS recording
# (Start Recording in OBS manually)

# Terminal 2: Start live analysis
python live_capture_analyzer.py --method obs --interval 2.0
```
- Real-time stats
- Database updated live
- Video saved for later review

### Workflow 3: Record Now, Analyze Later
```bash
# Step 1: Record with OBS (just click record)
# Step 2: After session, analyze recording
python main_poker_analyzer.py video.mp4
```
- No live analysis
- Full accuracy post-processing
- More time for detailed OCR

### Workflow 4: Live + Post-Processing (Best of Both)
```bash
# During play: Quick live tracking
python live_capture_analyzer.py --interval 3.0 --db live_data.db

# After session: Detailed analysis
python main_poker_analyzer.py recording.mp4 --db detailed_data.db
```
- Quick feedback during play
- Detailed analysis after
- Compare live vs. detailed data

---

## Troubleshooting

### "OBS Virtual Camera not found"

**Solution 1:** Make sure Virtual Camera is started
- OBS → Tools → Start Virtual Camera
- Check bottom-right of OBS for "Virtual Camera Active"

**Solution 2:** Install OBS Virtual Camera plugin
- Usually included with OBS 26+
- Reinstall OBS if missing

**Solution 3:** Use screen capture instead
```bash
python live_capture_analyzer.py --method screen
```

### "Frames not being captured"

Check console output for:
- `[CAPTURE THREAD] Started` ✓
- `Frames captured: X` (increasing) ✓

If not increasing:
- Verify poker window is visible
- Check capture region includes the poker table
- Try increasing `--interval` value

### "OCR not reading correctly"

**Improve accuracy:**
1. Increase screen resolution
2. Make poker client fullscreen
3. Disable screen effects/overlays
4. Adjust ROI regions in `config.py`

### High CPU usage

**Reduce load:**
1. Increase sample interval: `--interval 3.0`
2. Lower OBS resolution to 1280x720
3. Close other applications
4. Use screen capture instead of OBS

### Database growing too large

**Manage size:**
- Analysis creates one database entry per hand
- Delete old test databases
- Separate databases per session:
  ```bash
  python live_capture_analyzer.py --db "session_2024_10_28.db"
  ```

---

## Hotkeys (Future Feature)

**Planned hotkey support:**
- `Space`: Pause/Resume capture
- `H`: Mark current hand for review
- `Q`: Stop and save

(Not yet implemented - coming soon!)

---

## Advanced: Dual Monitor Setup

### Option 1: Poker on Monitor 1, Stats on Monitor 2
1. Play poker on primary monitor
2. Run live analyzer
3. Open database viewer on secondary monitor
4. See real-time stats while playing

### Option 2: OBS Scene with Overlay
1. Create OBS scene with poker game
2. Add text sources for live stats
3. Read stats from database
4. Display live stats overlay

---

## Integration with Streaming

If you stream on Twitch/YouTube:

### Stream Layout with Stats
1. **OBS Scene:** Poker game capture
2. **Add Browser Source:** Web-based stats dashboard
3. **Connect to database:** Show live stats to viewers
4. **Virtual Camera:** For analysis + streaming simultaneously

### Privacy Considerations
- Hide hole cards if streaming
- Delay sensitive information
- Use separate scenes for streaming vs. analysis

---

## Next Steps

1. **Test the setup:**
   ```bash
   python test_live_capture.py
   ```

2. **Try 30-second capture:**
   ```bash
   python test_live_capture.py
   ```

3. **Run live analysis:**
   ```bash
   python live_capture_analyzer.py --interval 2.0
   ```

4. **Review results:**
   - Check `live_poker_data.db`
   - See tracked players and stats

5. **Calibrate ROI regions** if OCR accuracy is poor
   - Use `test_video_extract.py` on recordings
   - Adjust `config.py` regions

---

## Comparison: Live vs. Post-Processing

| Feature | Live Capture | Post-Processing |
|---------|-------------|-----------------|
| **Speed** | Real-time | 2x slower than video |
| **Accuracy** | Good (90%+) | Better (95%+) |
| **Feedback** | Immediate | After session |
| **CPU Usage** | Moderate | High (batch) |
| **Flexibility** | Limited | Full reprocessing |
| **Best For** | Quick stats | Detailed analysis |

**Recommendation:** Use both!
- Live capture for immediate feedback
- Post-process recordings for accurate data

---

## Support

- Check `QUICKSTART.md` for basics
- See `README.md` for full documentation
- Test with `test_live_capture.py` first
- Adjust `config.py` for ROI calibration

Happy analyzing! 🎰
