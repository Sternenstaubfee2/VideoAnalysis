"""
Setup verification script for Poker Video Analyzer
Checks all prerequisites and provides installation instructions
"""

import os
import sys


def check_python_packages():
    """Check if required Python packages are installed"""
    print("Checking Python packages...")

    packages = {
        'cv2': 'opencv-python',
        'pytesseract': 'pytesseract',
        'numpy': 'numpy',
        'PIL': 'Pillow',
        'pandas': 'pandas'
    }

    all_installed = True
    for module, package in packages.items():
        try:
            __import__(module)
            print(f"  [OK] {package}")
        except ImportError:
            print(f"  [MISSING] {package}")
            all_installed = False

    return all_installed


def check_tesseract():
    """Check if Tesseract OCR is installed"""
    print("\nChecking Tesseract OCR...")

    possible_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        r"C:\Users\Julia\AppData\Local\Programs\Tesseract-OCR\tesseract.exe",
    ]

    for path in possible_paths:
        if os.path.exists(path):
            print(f"  [OK] Tesseract found at: {path}")
            return True, path

    print("  [MISSING] Tesseract OCR not found")
    return False, None


def check_video_file():
    """Check if the video file exists"""
    print("\nChecking video file...")

    video_path = r"C:\Users\Julia\Downloads\Spin_and_Go.mp4"

    if os.path.exists(video_path):
        size_mb = os.path.getsize(video_path) / (1024 * 1024)
        print(f"  [OK] Video found: {video_path}")
        print(f"      Size: {size_mb:.2f} MB")
        return True
    else:
        print(f"  [MISSING] Video not found at: {video_path}")
        return False


def print_installation_instructions():
    """Print installation instructions for missing components"""
    print("\n" + "=" * 70)
    print("INSTALLATION INSTRUCTIONS")
    print("=" * 70)

    print("\n1. Install Python packages (if missing):")
    print("   pip install -r requirements.txt")

    print("\n2. Install Tesseract OCR (if missing):")
    print("   - Download from: https://github.com/UB-Mannheim/tesseract/wiki")
    print("   - Choose the Windows installer (64-bit recommended)")
    print("   - Install to default location: C:\\Program Files\\Tesseract-OCR")
    print("   - During installation, make sure to check 'Add to PATH'")

    print("\n3. Verify video file:")
    print("   - Ensure Spin_and_Go.mp4 is in C:\\Users\\Julia\\Downloads\\")
    print("   - Or update the path in config.py")


def test_video_reading():
    """Test if we can read the video file"""
    print("\nTesting video reading...")

    try:
        import cv2
        video_path = r"C:\Users\Julia\Downloads\Spin_and_Go.mp4"

        if not os.path.exists(video_path):
            print("  [SKIP] Video file not found")
            return False

        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            print("  [FAIL] Cannot open video file")
            return False

        # Try to read first frame
        ret, frame = cap.read()
        if not ret:
            print("  [FAIL] Cannot read video frames")
            cap.release()
            return False

        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        print(f"  [OK] Video readable")
        print(f"      Resolution: {width}x{height}")
        print(f"      FPS: {fps:.2f}")
        print(f"      Total frames: {total_frames}")
        print(f"      Duration: {total_frames/fps:.2f} seconds")

        cap.release()
        return True

    except Exception as e:
        print(f"  [FAIL] Error: {e}")
        return False


def main():
    """Main setup check"""
    print("=" * 70)
    print("POKER VIDEO ANALYZER - SETUP VERIFICATION")
    print("=" * 70)
    print()

    # Check Python version
    print(f"Python version: {sys.version}")
    print()

    # Check packages
    packages_ok = check_python_packages()

    # Check Tesseract
    tesseract_ok, tesseract_path = check_tesseract()

    # Check video file
    video_ok = check_video_file()

    # Test video reading
    video_readable = test_video_reading()

    # Summary
    print("\n" + "=" * 70)
    print("SETUP STATUS")
    print("=" * 70)
    print(f"Python Packages:  {'[OK]' if packages_ok else '[MISSING]'}")
    print(f"Tesseract OCR:    {'[OK]' if tesseract_ok else '[MISSING]'}")
    print(f"Video File:       {'[OK]' if video_ok else '[MISSING]'}")
    print(f"Video Readable:   {'[OK]' if video_readable else '[FAIL]'}")

    if packages_ok and tesseract_ok and video_ok and video_readable:
        print("\n[SUCCESS] All prerequisites met! Ready to analyze poker videos.")
        print("\nRun the analyzer with:")
        print("  python main_poker_analyzer.py")
        print("\nOr use the quick launcher:")
        print("  run_analyzer.bat")
        return 0
    else:
        print("\n[WARNING] Some prerequisites are missing.")
        print_installation_instructions()
        return 1


if __name__ == "__main__":
    exit_code = main()
    print("\n" + "=" * 70)
    input("Press Enter to exit...")
    sys.exit(exit_code)
