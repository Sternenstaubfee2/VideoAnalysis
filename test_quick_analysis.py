"""
Quick test - analyze just a small portion of the video to verify everything works
"""

from main_poker_analyzer import MainPokerAnalyzer
from config import find_tesseract


def test_quick_analysis():
    """Run a quick analysis on a small portion of video"""
    print("=" * 70)
    print("QUICK ANALYSIS TEST - Processing 100 frames")
    print("=" * 70)

    video_path = r"C:\Users\Julia\Downloads\Spin_and_Go.mp4"
    tesseract_path = find_tesseract()

    if not tesseract_path:
        print("ERROR: Tesseract not found!")
        return

    # Create analyzer
    analyzer = MainPokerAnalyzer(
        video_path,
        db_path="test_poker_data.db",
        tesseract_path=tesseract_path
    )

    print(f"\nVideo: {video_path}")
    print(f"Tesseract: {tesseract_path}")
    print(f"Database: test_poker_data.db")
    print()

    # Process just first 100 frames (sample every 30th frame = ~3 frames)
    print("Processing frames...")
    try:
        # Manually process a few frames to test
        game_states = []
        frame_count = 0

        while frame_count < 300:  # Process 300 frames, sampling every 30th
            ret, frame = analyzer.analyzer.cap.read()
            if not ret:
                break

            if frame_count % 30 == 0:
                try:
                    game_state = analyzer.analyzer.analyze_frame(frame, frame_count)
                    game_states.append(game_state)
                    print(f"Frame {frame_count}: {len(game_state.players)} players detected")
                except Exception as e:
                    print(f"Frame {frame_count}: Error - {e}")

            frame_count += 1

        print(f"\nProcessed {len(game_states)} game states successfully!")
        print("\n" + "=" * 70)
        print("SUCCESS!")
        print("=" * 70)
        print("\nThe analyzer is working correctly.")
        print("You can now run the full analysis with:")
        print("  python main_poker_analyzer.py")
        print("\nOr use the quick launcher:")
        print("  run_analyzer.bat")

    except Exception as e:
        print(f"\nERROR during analysis: {e}")
        import traceback
        traceback.print_exc()
    finally:
        analyzer.close()


if __name__ == "__main__":
    test_quick_analysis()
