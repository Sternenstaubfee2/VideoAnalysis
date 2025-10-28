"""
Configuration file for poker video analyzer
Adjust these settings based on your system and video characteristics
"""

import os

# Tesseract OCR Configuration
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Alternate common locations
TESSERACT_ALTERNATIVES = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    r"C:\Users\Julia\AppData\Local\Programs\Tesseract-OCR\tesseract.exe",
]

# Try to find tesseract automatically
def find_tesseract():
    """Find tesseract executable automatically"""
    for path in TESSERACT_ALTERNATIVES:
        if os.path.exists(path):
            return path
    return None

# Video Processing Configuration
VIDEO_SAMPLE_RATE = 30  # Process every Nth frame (higher = faster but less accurate)
VIDEO_DEBUG_MODE = False  # Save debug frames for inspection

# Database Configuration
DATABASE_PATH = "poker_data.db"

# GG Poker UI Configuration (3-player Spin & Go)
# These ROI regions may need adjustment based on video resolution
# Format: (x, y, width, height) as percentages of screen (0.0 to 1.0)

PLAYER_REGIONS = {
    'player_1': {  # Bottom position (usually Hero)
        'name': (0.40, 0.85, 0.20, 0.05),
        'stack': (0.40, 0.80, 0.20, 0.04),
        'cards': (0.42, 0.70, 0.16, 0.08),
        'action': (0.40, 0.75, 0.20, 0.04),
        'country_flag': (0.38, 0.85, 0.03, 0.03)
    },
    'player_2': {  # Top left position
        'name': (0.15, 0.15, 0.20, 0.05),
        'stack': (0.15, 0.20, 0.20, 0.04),
        'cards': (0.17, 0.25, 0.16, 0.08),
        'action': (0.15, 0.30, 0.20, 0.04),
        'country_flag': (0.13, 0.15, 0.03, 0.03)
    },
    'player_3': {  # Top right position
        'name': (0.65, 0.15, 0.20, 0.05),
        'stack': (0.65, 0.20, 0.20, 0.04),
        'cards': (0.67, 0.25, 0.16, 0.08),
        'action': (0.65, 0.30, 0.20, 0.04),
        'country_flag': (0.63, 0.15, 0.03, 0.03)
    }
}

GAME_INFO_REGIONS = {
    'pot': (0.45, 0.45, 0.10, 0.04),
    'community_cards': (0.35, 0.40, 0.30, 0.08),
    'blinds': (0.45, 0.05, 0.10, 0.04),
    'hand_number': (0.02, 0.02, 0.15, 0.03),
    'dealer_button': (0.50, 0.50, 0.05, 0.05)
}

# OCR Configuration
OCR_CONFIG_DEFAULT = '--psm 7'  # Single line of text
OCR_CONFIG_BLOCK = '--psm 6'   # Block of text
OCR_CONFIG_SINGLE_WORD = '--psm 8'  # Single word

# Image Processing
IMAGE_SCALE_FACTOR = 2  # Upscale factor for OCR
IMAGE_THRESHOLD_METHOD = 'otsu'  # 'otsu', 'adaptive', or 'binary'

# Action Keywords
ACTION_KEYWORDS = {
    'fold': ['fold', 'folded'],
    'call': ['call', 'calls', 'called'],
    'check': ['check', 'checks', 'checked'],
    'raise': ['raise', 'raises', 'raised', 'bet', 'bets'],
    'all_in': ['all-in', 'all in', 'allin']
}

# Currency and Number Parsing
CURRENCY_SYMBOLS = ['$', '€', '£', 'BB', 'chips']

# Hand Detection Thresholds
HAND_BOUNDARY_THRESHOLD = 0.1  # Pot reduction threshold for new hand detection
MIN_FRAMES_PER_HAND = 3  # Minimum frames to consider a valid hand

# Calibration Mode
CALIBRATION_MODE = False  # Set to True to show ROI boxes on frames
CALIBRATION_OUTPUT_DIR = "calibration_frames"

# Report Configuration
REPORT_OUTPUT_FILE = "poker_analysis_report.txt"
JSON_OUTPUT_FILE = "poker_hands.json"

# Logging
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_FILE = "poker_analyzer.log"

# Performance
USE_GPU = False  # Use GPU acceleration if available
MAX_WORKERS = 4  # Number of parallel workers for processing


def get_config():
    """Get current configuration as dictionary"""
    return {
        'tesseract_path': find_tesseract() or TESSERACT_PATH,
        'video_sample_rate': VIDEO_SAMPLE_RATE,
        'database_path': DATABASE_PATH,
        'player_regions': PLAYER_REGIONS,
        'game_info_regions': GAME_INFO_REGIONS
    }


def print_config():
    """Print current configuration"""
    config = get_config()
    print("=" * 60)
    print("POKER ANALYZER CONFIGURATION")
    print("=" * 60)
    for key, value in config.items():
        if isinstance(value, dict):
            print(f"{key}:")
            for k, v in value.items():
                print(f"  {k}: {v}")
        else:
            print(f"{key}: {value}")
    print("=" * 60)


if __name__ == "__main__":
    print_config()

    # Check tesseract installation
    tesseract = find_tesseract()
    if tesseract:
        print(f"\n✓ Tesseract found: {tesseract}")
    else:
        print("\n✗ Tesseract not found!")
        print("Please install Tesseract OCR:")
        print("https://github.com/UB-Mannheim/tesseract/wiki")
