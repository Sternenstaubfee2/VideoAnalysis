"""
Quick test to extract and visualize frames from the poker video
This verifies video reading works without requiring Tesseract
"""

import cv2
import os


def extract_sample_frames(video_path, output_dir="sample_frames", num_frames=5):
    """Extract sample frames from video for inspection"""

    # Create output directory
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Open video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Cannot open video file: {video_path}")
        return

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    print("=" * 60)
    print("VIDEO INFORMATION")
    print("=" * 60)
    print(f"File: {video_path}")
    print(f"Resolution: {width}x{height}")
    print(f"FPS: {fps:.2f}")
    print(f"Total frames: {total_frames}")
    print(f"Duration: {total_frames/fps:.2f} seconds")
    print()

    # Calculate frame intervals
    frame_interval = total_frames // (num_frames + 1)

    print("=" * 60)
    print("EXTRACTING SAMPLE FRAMES")
    print("=" * 60)

    for i in range(1, num_frames + 1):
        frame_number = i * frame_interval

        # Set frame position
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

        # Read frame
        ret, frame = cap.read()
        if not ret:
            print(f"Error reading frame {frame_number}")
            continue

        # Save frame
        output_path = os.path.join(output_dir, f"frame_{frame_number:06d}.jpg")
        cv2.imwrite(output_path, frame)

        timestamp = frame_number / fps
        print(f"Frame {frame_number:6d} (@ {timestamp:6.2f}s) -> {output_path}")

        # Draw some sample ROI boxes for visualization
        debug_frame = frame.copy()

        # Player 1 (bottom) name region
        x1, y1 = int(0.40 * width), int(0.85 * height)
        x2, y2 = int(0.60 * width), int(0.90 * height)
        cv2.rectangle(debug_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(debug_frame, "P1 Name", (x1, y1-5),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        # Player 2 (top left) name region
        x1, y1 = int(0.15 * width), int(0.15 * height)
        x2, y2 = int(0.35 * width), int(0.20 * height)
        cv2.rectangle(debug_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(debug_frame, "P2 Name", (x1, y1-5),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        # Player 3 (top right) name region
        x1, y1 = int(0.65 * width), int(0.15 * height)
        x2, y2 = int(0.85 * width), int(0.20 * height)
        cv2.rectangle(debug_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(debug_frame, "P3 Name", (x1, y1-5),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        # Pot region
        x1, y1 = int(0.45 * width), int(0.45 * height)
        x2, y2 = int(0.55 * width), int(0.49 * height)
        cv2.rectangle(debug_frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
        cv2.putText(debug_frame, "Pot", (x1, y1-5),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)

        # Save debug frame with ROI boxes
        debug_path = os.path.join(output_dir, f"debug_{frame_number:06d}.jpg")
        cv2.imwrite(debug_path, debug_frame)

    cap.release()

    print()
    print("=" * 60)
    print("EXTRACTION COMPLETE")
    print("=" * 60)
    print(f"Sample frames saved to: {output_dir}/")
    print(f"- frame_*.jpg: Original frames")
    print(f"- debug_*.jpg: Frames with ROI regions marked")
    print()
    print("Next steps:")
    print("1. Review the debug_*.jpg images to verify ROI regions")
    print("2. If regions don't match, adjust coordinates in config.py")
    print("3. Install Tesseract OCR for text extraction")
    print("4. Run main_poker_analyzer.py for full analysis")


if __name__ == "__main__":
    video_path = r"C:\Users\Julia\Downloads\Spin_and_Go.mp4"
    extract_sample_frames(video_path, num_frames=10)
