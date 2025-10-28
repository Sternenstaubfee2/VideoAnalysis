# Installing Tesseract OCR for Windows

Tesseract is required for text recognition (OCR) in the poker video analyzer.

## Quick Installation Steps

### 1. Download Tesseract

Visit: https://github.com/UB-Mannheim/tesseract/wiki

**Direct download link for Windows 64-bit:**
https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.3.3.20231005.exe

### 2. Install Tesseract

1. Run the downloaded installer
2. **Important:** During installation, choose one of these locations:
   - `C:\Program Files\Tesseract-OCR` (recommended, default)
   - `C:\Program Files (x86)\Tesseract-OCR`
3. **Optional but recommended:** Check "Add to PATH" during installation

### 3. Verify Installation

After installation, open a new command prompt and run:

```bash
tesseract --version
```

You should see output like:
```
tesseract v5.3.3
```

### 4. Configure the Poker Analyzer

The analyzer will automatically detect Tesseract in these locations:
- `C:\Program Files\Tesseract-OCR\tesseract.exe`
- `C:\Program Files (x86)\Tesseract-OCR\tesseract.exe`
- `C:\Users\Julia\AppData\Local\Programs\Tesseract-OCR\tesseract.exe`

If you installed it elsewhere, update the path in `config.py`:

```python
TESSERACT_PATH = r"C:\Your\Custom\Path\tesseract.exe"
```

### 5. Test the Installation

Run the setup verification script:

```bash
python check_setup.py
```

You should see:
```
Checking Tesseract OCR...
  [OK] Tesseract found at: C:\Program Files\Tesseract-OCR\tesseract.exe
```

## Troubleshooting

### "Tesseract not found" error

1. **Verify installation location:**
   - Check if `tesseract.exe` exists in the installation folder
   - Try running `tesseract --version` in command prompt

2. **Manual path configuration:**
   - Edit `config.py`
   - Set `TESSERACT_PATH` to the full path of `tesseract.exe`

3. **Add to PATH manually (if not done during installation):**
   - Right-click "This PC" → Properties → Advanced System Settings
   - Click "Environment Variables"
   - Under "System variables", find and edit "Path"
   - Add the Tesseract installation directory (e.g., `C:\Program Files\Tesseract-OCR`)
   - Click OK and restart command prompt

### OCR accuracy issues

If OCR is not reading text correctly:

1. **Check video quality:**
   - Higher resolution = better OCR accuracy
   - Ensure video is not too compressed

2. **Adjust ROI regions:**
   - Run `python test_video_extract.py`
   - Check the `debug_*.jpg` images in `sample_frames/`
   - Verify green boxes align with player names/stacks
   - Adjust coordinates in `config.py` if needed

3. **Tune OCR parameters:**
   - In `config.py`, adjust `IMAGE_SCALE_FACTOR` (try 3 or 4)
   - Change `OCR_CONFIG_DEFAULT` settings
   - Experiment with different preprocessing methods

### Alternative: Tesseract from Microsoft Store

You can also install Tesseract from the Microsoft Store:
1. Open Microsoft Store
2. Search for "Tesseract OCR"
3. Click Install
4. Update the path in `config.py` to point to the Store installation

## Language Packs

By default, Tesseract includes English. If you need other languages:

1. During installation, select additional language packs
2. Or download them later from: https://github.com/tesseract-ocr/tessdata

For poker videos, English should be sufficient.

## Next Steps

Once Tesseract is installed:

1. Verify with `python check_setup.py`
2. Test with sample frames: `python test_video_extract.py`
3. Run full analysis: `python main_poker_analyzer.py`
4. Check results in `poker_data.db` and `poker_analysis_report.txt`

## Additional Resources

- Tesseract Documentation: https://tesseract-ocr.github.io/
- Tesseract GitHub: https://github.com/tesseract-ocr/tesseract
- pytesseract (Python wrapper): https://github.com/madmaze/pytesseract
