"""
Quick test for live capture - Run for 30 seconds to verify setup
"""

from live_capture_analyzer import LiveCaptureAnalyzer, CaptureMethod


def test_screen_capture():
    """Test screen capture mode for 30 seconds"""
    print("=" * 70)
    print("LIVE CAPTURE TEST - SCREEN CAPTURE MODE")
    print("=" * 70)
    print()
    print("This will capture your screen for 30 seconds.")
    print("1. Open GG Poker or any poker client")
    print("2. Make sure the poker table is visible")
    print("3. Press Enter to start...")
    input()

    # Create analyzer with screen capture
    analyzer = LiveCaptureAnalyzer(
        capture_method=CaptureMethod.SCREEN_REGION,
        db_path="test_live_capture.db",
        sample_interval=2.0  # Capture every 2 seconds
    )

    # Run for 30 seconds
    print("\nStarting capture for 30 seconds...")
    analyzer.start(duration=30.0, display_interval=2.0)

    print("\nTest complete! Check test_live_capture.db for results.")


def test_obs_capture():
    """Test OBS virtual camera mode"""
    print("=" * 70)
    print("LIVE CAPTURE TEST - OBS VIRTUAL CAMERA MODE")
    print("=" * 70)
    print()
    print("Prerequisites:")
    print("1. Install OBS Studio (https://obsproject.com/)")
    print("2. Set up a scene with poker game capture")
    print("3. Start OBS Virtual Camera (Tools -> Virtual Camera)")
    print("4. Press Enter when ready...")
    input()

    # Create analyzer with OBS capture
    analyzer = LiveCaptureAnalyzer(
        capture_method=CaptureMethod.OBS_VIRTUAL_CAMERA,
        db_path="test_live_capture.db",
        sample_interval=2.0
    )

    # Run for 30 seconds
    print("\nStarting capture for 30 seconds...")
    analyzer.start(duration=30.0, display_interval=2.0)

    print("\nTest complete! Check test_live_capture.db for results.")


def quick_test():
    """Quick 10-second test"""
    print("=" * 70)
    print("QUICK LIVE CAPTURE TEST (10 seconds)")
    print("=" * 70)
    print()
    print("Starting in 3 seconds...")
    import time
    time.sleep(3)

    analyzer = LiveCaptureAnalyzer(
        capture_method=CaptureMethod.SCREEN_REGION,
        db_path="test_live_capture.db",
        sample_interval=1.0  # Capture every second for testing
    )

    analyzer.start(duration=10.0, display_interval=1.0)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        if mode == "obs":
            test_obs_capture()
        elif mode == "quick":
            quick_test()
        else:
            test_screen_capture()
    else:
        # Default: screen capture test
        print("Usage:")
        print("  python test_live_capture.py         # Test screen capture (30s)")
        print("  python test_live_capture.py obs     # Test OBS virtual camera (30s)")
        print("  python test_live_capture.py quick   # Quick test (10s)")
        print()
        print("Running default: screen capture test")
        print()
        test_screen_capture()
