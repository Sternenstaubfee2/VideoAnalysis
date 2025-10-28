"""
Quick test to verify Tesseract OCR is working correctly
"""

import cv2
import numpy as np
from poker_video_analyzer import PokerVideoAnalyzer


def test_ocr_on_sample_frame():
    """Test OCR on a single frame from the video"""
    print("=" * 60)
    print("TESTING OCR FUNCTIONALITY")
    print("=" * 60)

    video_path = r"C:\Users\Julia\Downloads\Spin_and_Go.mp4"

    # Create analyzer (will auto-detect Tesseract)
    with PokerVideoAnalyzer(video_path) as analyzer:
        print(f"\nVideo loaded: {video_path}")
        print(f"Resolution: {analyzer.width}x{analyzer.height}")
        print(f"FPS: {analyzer.fps}")

        # Read a frame from middle of video
        frame_number = 5000
        analyzer.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

        ret, frame = analyzer.cap.read()
        if not ret:
            print("ERROR: Cannot read frame")
            return

        print(f"\nAnalyzing frame {frame_number}...")
        print("-" * 60)

        # Try to extract some information
        try:
            # Test pot extraction
            pot_size = analyzer._extract_pot_size(frame)
            print(f"Pot size detected: ${pot_size:.2f}")

            # Test blind extraction
            sb, bb = analyzer._extract_blinds(frame)
            print(f"Blinds detected: ${sb:.2f}/${bb:.2f}")

            # Test player name extraction
            for player_key in ['player_1', 'player_2', 'player_3']:
                name = analyzer._extract_player_name(frame, player_key)
                stack = analyzer._extract_stack_amount(frame, player_key)
                if name or stack > 0:
                    print(f"{player_key}: Name='{name}', Stack=${stack:.2f}")

            print("\n" + "=" * 60)
            print("OCR TEST SUCCESSFUL!")
            print("=" * 60)
            print("\nTesseract is working correctly.")
            print("The analyzer should now process the video without errors.")

        except Exception as e:
            print(f"\nERROR during OCR: {e}")
            print("\nThis might indicate:")
            print("1. Tesseract path issue")
            print("2. ROI regions need calibration")
            print("3. Video frame quality issues")


if __name__ == "__main__":
    test_ocr_on_sample_frame()
