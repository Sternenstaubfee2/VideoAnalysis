"""
Live Poker Capture Analyzer
Analyzes poker games in real-time while recording/playing
"""

import cv2
import numpy as np
import time
import threading
from queue import Queue, Empty
from typing import Optional, Dict, List, Tuple
from datetime import datetime
import mss
import mss.tools

from database_handler import PokerDatabase
from poker_video_analyzer import PokerVideoAnalyzer, GameState
from config import find_tesseract


class CaptureMethod:
    """Enumeration of capture methods"""
    SCREEN_REGION = "screen_region"
    OBS_VIRTUAL_CAMERA = "obs_virtual_camera"
    WINDOW_CAPTURE = "window_capture"


class LiveCaptureAnalyzer:
    def __init__(self,
                 capture_method: str = CaptureMethod.SCREEN_REGION,
                 capture_region: Optional[Dict] = None,
                 db_path: str = "live_poker_data.db",
                 sample_interval: float = 2.0):
        """
        Initialize live capture analyzer

        Args:
            capture_method: Method to capture frames (screen_region, obs_virtual_camera, window_capture)
            capture_region: Dict with {top, left, width, height} for screen region capture
            db_path: Path to database
            sample_interval: Seconds between frame captures (default: 2.0 = capture every 2 seconds)
        """
        self.capture_method = capture_method
        self.capture_region = capture_region or self._detect_poker_window()
        self.db = PokerDatabase(db_path)
        self.sample_interval = sample_interval

        # Get tesseract path
        self.tesseract_path = find_tesseract()
        if not self.tesseract_path:
            raise RuntimeError("Tesseract not found! Install Tesseract OCR.")

        # Initialize capture
        self.sct = mss.mss()
        self.cap = None  # For OBS virtual camera

        # Threading and queues
        self.frame_queue = Queue(maxsize=10)
        self.result_queue = Queue()
        self.running = False
        self.paused = False

        # State tracking
        self.current_game_state = None
        self.previous_frame = None
        self.frame_count = 0
        self.hand_count = 0
        self.last_process_time = 0

        # Statistics
        self.stats = {
            'frames_captured': 0,
            'frames_processed': 0,
            'hands_detected': 0,
            'players_tracked': set(),
            'start_time': None,
            'errors': 0
        }

        print(f"[LIVE CAPTURE] Initialized")
        print(f"  Method: {capture_method}")
        print(f"  Region: {self.capture_region}")
        print(f"  Database: {db_path}")
        print(f"  Sample interval: {sample_interval}s")
        print(f"  Tesseract: {self.tesseract_path}")

    def _detect_poker_window(self) -> Dict:
        """
        Auto-detect GG Poker window or prompt user to define region
        Returns default full screen region as fallback
        """
        # Default to full screen (user can adjust)
        with mss.mss() as sct:
            monitor = sct.monitors[1]  # Primary monitor

        print("\n[SETUP] Screen capture region")
        print(f"Default: Full screen ({monitor['width']}x{monitor['height']})")
        print("\nTo capture specific region, you can:")
        print("1. Use default full screen (press Enter)")
        print("2. Or modify capture_region parameter when starting")

        return {
            'top': monitor['top'],
            'left': monitor['left'],
            'width': monitor['width'],
            'height': monitor['height']
        }

    def _capture_frame_screen(self) -> Optional[np.ndarray]:
        """Capture frame from screen region"""
        try:
            # Capture screen
            screenshot = self.sct.grab(self.capture_region)

            # Convert to numpy array (BGR format for OpenCV)
            frame = np.array(screenshot)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

            return frame
        except Exception as e:
            print(f"[ERROR] Screen capture failed: {e}")
            return None

    def _capture_frame_obs(self) -> Optional[np.ndarray]:
        """Capture frame from OBS virtual camera"""
        if self.cap is None:
            # Try to open OBS virtual camera (usually index 1 or 2)
            for cam_index in range(10):
                cap = cv2.VideoCapture(cam_index)
                if cap.isOpened():
                    # Check if it's likely the OBS camera
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        self.cap = cap
                        print(f"[INFO] Found camera at index {cam_index}")
                        return frame
                    cap.release()

            print("[ERROR] Could not find OBS virtual camera")
            return None

        # Read from existing camera
        ret, frame = self.cap.read()
        if ret:
            return frame
        return None

    def _capture_frame(self) -> Optional[np.ndarray]:
        """Capture frame using configured method"""
        if self.capture_method == CaptureMethod.SCREEN_REGION:
            return self._capture_frame_screen()
        elif self.capture_method == CaptureMethod.OBS_VIRTUAL_CAMERA:
            return self._capture_frame_obs()
        else:
            return self._capture_frame_screen()

    def _frame_changed(self, new_frame: np.ndarray, threshold: float = 0.05) -> bool:
        """
        Detect if frame has changed significantly from previous frame
        This helps avoid processing identical frames
        """
        if self.previous_frame is None:
            return True

        # Resize for faster comparison
        new_small = cv2.resize(new_frame, (320, 180))
        prev_small = cv2.resize(self.previous_frame, (320, 180))

        # Calculate difference
        diff = cv2.absdiff(new_small, prev_small)
        diff_percent = np.sum(diff) / (320 * 180 * 3 * 255)

        return diff_percent > threshold

    def _capture_thread(self):
        """Thread that continuously captures frames"""
        print("[CAPTURE THREAD] Started")

        while self.running:
            if self.paused:
                time.sleep(0.1)
                continue

            try:
                # Capture frame
                frame = self._capture_frame()

                if frame is not None:
                    self.stats['frames_captured'] += 1

                    # Only queue if frame changed significantly
                    if self._frame_changed(frame):
                        # Add to queue (skip if queue is full)
                        try:
                            self.frame_queue.put((time.time(), frame), block=False)
                            self.previous_frame = frame.copy()
                        except:
                            pass  # Queue full, skip this frame

                # Sleep for sample interval
                time.sleep(self.sample_interval)

            except Exception as e:
                print(f"[ERROR] Capture thread: {e}")
                self.stats['errors'] += 1
                time.sleep(1)

        print("[CAPTURE THREAD] Stopped")

    def _process_thread(self):
        """Thread that processes captured frames"""
        print("[PROCESS THREAD] Started")

        # Create a temporary video analyzer for this thread
        # We'll create a dummy video path
        temp_analyzer = PokerVideoAnalyzer.__new__(PokerVideoAnalyzer)
        temp_analyzer.tesseract_path = self.tesseract_path
        temp_analyzer.width = self.capture_region['width']
        temp_analyzer.height = self.capture_region['height']
        temp_analyzer._setup_roi_regions()

        # Set tesseract
        import pytesseract
        pytesseract.pytesseract.tesseract_cmd = self.tesseract_path

        while self.running:
            try:
                # Get frame from queue (with timeout)
                timestamp, frame = self.frame_queue.get(timeout=1.0)

                # Process frame
                try:
                    game_state = temp_analyzer.analyze_frame(frame, self.frame_count)
                    game_state.frame_timestamp = timestamp

                    # Store result
                    self.result_queue.put(game_state)
                    self.stats['frames_processed'] += 1
                    self.frame_count += 1

                except Exception as e:
                    print(f"[ERROR] Processing frame: {e}")
                    self.stats['errors'] += 1

            except Empty:
                continue
            except Exception as e:
                print(f"[ERROR] Process thread: {e}")
                self.stats['errors'] += 1
                time.sleep(1)

        print("[PROCESS THREAD] Stopped")

    def _update_database(self, game_state: GameState):
        """Update database with game state information"""
        try:
            # Update players in stammdaten
            for player in game_state.players:
                if player.name:
                    self.db.add_or_update_player(player.name, player.country)
                    self.stats['players_tracked'].add(player.name)

            # Store game state snapshot (could be expanded to full hand tracking)
            # For now, we'll just update player info and track stats

        except Exception as e:
            print(f"[ERROR] Database update: {e}")

    def _display_console(self):
        """Display live statistics in console"""
        elapsed = time.time() - self.stats['start_time'] if self.stats['start_time'] else 0

        # Clear console (Windows)
        import os
        os.system('cls' if os.name == 'nt' else 'clear')

        print("=" * 70)
        print("LIVE POKER CAPTURE - REAL-TIME ANALYSIS")
        print("=" * 70)
        print(f"Status: {'RUNNING' if self.running else 'STOPPED'} {'(PAUSED)' if self.paused else ''}")
        print(f"Uptime: {elapsed:.1f}s")
        print()

        print("STATISTICS:")
        print(f"  Frames captured:  {self.stats['frames_captured']}")
        print(f"  Frames processed: {self.stats['frames_processed']}")
        print(f"  Hands detected:   {self.stats['hands_detected']}")
        print(f"  Players tracked:  {len(self.stats['players_tracked'])}")
        print(f"  Errors:           {self.stats['errors']}")
        print()

        if self.current_game_state:
            print("CURRENT GAME STATE:")
            print(f"  Pot: ${self.current_game_state.pot_size:.2f}")
            print(f"  Blinds: ${self.current_game_state.small_blind:.2f}/${self.current_game_state.big_blind:.2f}")
            print(f"  Players at table: {len(self.current_game_state.players)}")
            print()

            if self.current_game_state.players:
                print("  PLAYERS:")
                for player in self.current_game_state.players:
                    if player.name:
                        print(f"    {player.name}: ${player.stack:.2f}")
            print()

        print("CONTROLS:")
        print("  Press Ctrl+C to stop")
        print("=" * 70)

    def start(self, duration: Optional[float] = None, display_interval: float = 2.0):
        """
        Start live capture and analysis

        Args:
            duration: Optional duration in seconds (None = run indefinitely)
            display_interval: Seconds between console updates
        """
        print("\n[STARTING LIVE CAPTURE]")
        print("Press Ctrl+C to stop\n")

        self.running = True
        self.stats['start_time'] = time.time()

        # Start threads
        capture_thread = threading.Thread(target=self._capture_thread, daemon=True)
        process_thread = threading.Thread(target=self._process_thread, daemon=True)

        capture_thread.start()
        process_thread.start()

        # Main loop - display stats and process results
        try:
            start_time = time.time()
            last_display = 0

            while self.running:
                current_time = time.time()

                # Check duration limit
                if duration and (current_time - start_time) > duration:
                    print("\n[INFO] Duration limit reached")
                    break

                # Process results
                try:
                    game_state = self.result_queue.get(timeout=0.1)
                    self.current_game_state = game_state
                    self._update_database(game_state)
                except Empty:
                    pass

                # Update display
                if current_time - last_display > display_interval:
                    self._display_console()
                    last_display = current_time

                time.sleep(0.1)

        except KeyboardInterrupt:
            print("\n\n[INFO] Stopped by user (Ctrl+C)")

        finally:
            self.stop()

    def stop(self):
        """Stop capture and clean up"""
        print("\n[STOPPING]")
        self.running = False

        # Wait for threads to finish
        time.sleep(2)

        # Clean up
        if self.cap:
            self.cap.release()

        # Final stats
        self._display_console()

        # Show tracked players
        if self.stats['players_tracked']:
            print("\nPLAYERS TRACKED:")
            all_players = self.db.get_all_players()
            for player in all_players:
                print(f"  {player['player_name']}: {player['total_hands_played']} hands")

        self.db.close()
        print("\n[STOPPED]")

    def pause(self):
        """Pause capture (keep threads running)"""
        self.paused = True
        print("[PAUSED]")

    def resume(self):
        """Resume capture"""
        self.paused = False
        print("[RESUMED]")


def main():
    """Main entry point for live capture"""
    import argparse

    parser = argparse.ArgumentParser(description='Live poker game capture and analysis')
    parser.add_argument('--method', choices=['screen', 'obs', 'window'],
                       default='screen',
                       help='Capture method (default: screen)')
    parser.add_argument('--interval', type=float, default=2.0,
                       help='Seconds between captures (default: 2.0)')
    parser.add_argument('--duration', type=float,
                       help='Duration in seconds (default: unlimited)')
    parser.add_argument('--db', default='live_poker_data.db',
                       help='Database path')
    parser.add_argument('--display-interval', type=float, default=2.0,
                       help='Console update interval (default: 2.0)')

    args = parser.parse_args()

    # Map method name
    method_map = {
        'screen': CaptureMethod.SCREEN_REGION,
        'obs': CaptureMethod.OBS_VIRTUAL_CAMERA,
        'window': CaptureMethod.WINDOW_CAPTURE
    }

    # Create and start analyzer
    analyzer = LiveCaptureAnalyzer(
        capture_method=method_map[args.method],
        db_path=args.db,
        sample_interval=args.interval
    )

    analyzer.start(duration=args.duration, display_interval=args.display_interval)


if __name__ == "__main__":
    main()
