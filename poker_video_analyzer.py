"""
Poker Video Analyzer
Extracts poker game information from GG Poker videos using OCR and computer vision
"""

import cv2
import numpy as np
import pytesseract
from typing import Dict, List, Optional, Tuple
import re
from dataclasses import dataclass
from enum import Enum
import os


class Action(Enum):
    FOLD = "Fold"
    CALL = "Call"
    CHECK = "Check"
    RAISE = "Raise"
    BET = "Bet"
    ALL_IN = "All-in"


@dataclass
class Player:
    name: str
    country: str = ""
    position: str = ""
    stack: float = 0.0
    seat_number: int = 0


@dataclass
class PlayerAction:
    player_name: str
    action: str
    amount: float = 0.0
    street: str = "preflop"  # preflop, flop, turn, river


@dataclass
class GameState:
    hand_number: int = 0
    big_blind: float = 0.0
    small_blind: float = 0.0
    pot_size: float = 0.0
    players: List[Player] = None
    actions: List[PlayerAction] = None
    community_cards: List[str] = None
    current_street: str = "preflop"

    def __post_init__(self):
        if self.players is None:
            self.players = []
        if self.actions is None:
            self.actions = []
        if self.community_cards is None:
            self.community_cards = []


class PokerVideoAnalyzer:
    def __init__(self, video_path: str, tesseract_path: Optional[str] = None):
        """
        Initialize the poker video analyzer

        Args:
            video_path: Path to the video file
            tesseract_path: Optional path to tesseract executable
        """
        self.video_path = video_path
        self.cap = cv2.VideoCapture(video_path)

        if not self.cap.isOpened():
            raise ValueError(f"Cannot open video file: {video_path}")

        # Set tesseract path - auto-detect if not provided
        if not tesseract_path:
            # Try to find tesseract automatically
            possible_paths = [
                r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
                r"C:\Users\Julia\AppData\Local\Programs\Tesseract-OCR\tesseract.exe",
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    tesseract_path = path
                    break

        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
            print(f"[INFO] Using Tesseract: {tesseract_path}")
        else:
            print("[WARNING] Tesseract not found - OCR may fail")

        # Video properties
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Game state
        self.game_states: List[GameState] = []
        self.current_game_state = GameState()

        # ROI (Region of Interest) definitions for GG Poker
        # These will need to be calibrated based on actual video
        self._setup_roi_regions()

    def _setup_roi_regions(self):
        """Define regions of interest for different UI elements"""
        # These are approximate regions and should be calibrated
        # Format: (x, y, width, height) as percentages of screen

        # Player positions (typical 3-player spin & go layout)
        self.player_regions = {
            'player_1': {  # Bottom (Hero)
                'name': (0.40, 0.85, 0.20, 0.05),
                'stack': (0.40, 0.80, 0.20, 0.04),
                'cards': (0.42, 0.70, 0.16, 0.08),
                'action': (0.40, 0.75, 0.20, 0.04)
            },
            'player_2': {  # Top left
                'name': (0.15, 0.15, 0.20, 0.05),
                'stack': (0.15, 0.20, 0.20, 0.04),
                'cards': (0.17, 0.25, 0.16, 0.08),
                'action': (0.15, 0.30, 0.20, 0.04)
            },
            'player_3': {  # Top right
                'name': (0.65, 0.15, 0.20, 0.05),
                'stack': (0.65, 0.20, 0.20, 0.04),
                'cards': (0.67, 0.25, 0.16, 0.08),
                'action': (0.65, 0.30, 0.20, 0.04)
            }
        }

        # Other important regions
        self.game_info_regions = {
            'pot': (0.45, 0.45, 0.10, 0.04),
            'community_cards': (0.35, 0.40, 0.30, 0.08),
            'blinds': (0.45, 0.05, 0.10, 0.04),
            'hand_number': (0.02, 0.02, 0.15, 0.03)
        }

    def _get_roi(self, frame: np.ndarray, roi_tuple: Tuple[float, float, float, float]) -> np.ndarray:
        """Extract region of interest from frame"""
        x_pct, y_pct, w_pct, h_pct = roi_tuple

        x = int(x_pct * self.width)
        y = int(y_pct * self.height)
        w = int(w_pct * self.width)
        h = int(h_pct * self.height)

        return frame[y:y+h, x:x+w]

    def _preprocess_for_ocr(self, roi: np.ndarray, invert: bool = False) -> np.ndarray:
        """Preprocess image region for better OCR results"""
        # Convert to grayscale
        if len(roi.shape) == 3:
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        else:
            gray = roi

        # Apply thresholding
        if invert:
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        else:
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Denoise
        denoised = cv2.fastNlMeansDenoising(thresh)

        # Resize for better OCR (upscale small text)
        scale_factor = 2
        resized = cv2.resize(denoised, None, fx=scale_factor, fy=scale_factor,
                           interpolation=cv2.INTER_CUBIC)

        return resized

    def _ocr_text(self, roi: np.ndarray, config: str = '--psm 7') -> str:
        """Perform OCR on image region"""
        preprocessed = self._preprocess_for_ocr(roi)
        text = pytesseract.image_to_string(preprocessed, config=config)
        return text.strip()

    def _extract_player_name(self, frame: np.ndarray, player_key: str) -> str:
        """Extract player name from specific region"""
        roi = self._get_roi(frame, self.player_regions[player_key]['name'])
        text = self._ocr_text(roi, config='--psm 7')
        # Clean up the text
        text = re.sub(r'[^a-zA-Z0-9_\-\s]', '', text)
        return text.strip()

    def _extract_stack_amount(self, frame: np.ndarray, player_key: str) -> float:
        """Extract stack amount from specific region"""
        roi = self._get_roi(frame, self.player_regions[player_key]['stack'])
        text = self._ocr_text(roi, config='--psm 7')

        # Extract number from text (handle BB, chips, etc.)
        numbers = re.findall(r'[\d,.]+', text)
        if numbers:
            # Remove commas and convert to float
            amount_str = numbers[0].replace(',', '')
            try:
                return float(amount_str)
            except ValueError:
                return 0.0
        return 0.0

    def _extract_player_action(self, frame: np.ndarray, player_key: str) -> Optional[str]:
        """Extract player action from specific region"""
        roi = self._get_roi(frame, self.player_regions[player_key]['action'])
        text = self._ocr_text(roi, config='--psm 7').lower()

        # Match common actions
        if 'fold' in text:
            return Action.FOLD.value
        elif 'call' in text:
            return Action.CALL.value
        elif 'check' in text:
            return Action.CHECK.value
        elif 'raise' in text or 'bet' in text:
            # Extract amount if possible
            numbers = re.findall(r'[\d,.]+', text)
            if numbers:
                amount_str = numbers[0].replace(',', '')
                return f"Raise {amount_str}"
            return Action.RAISE.value
        elif 'all' in text and 'in' in text:
            return Action.ALL_IN.value

        return None

    def _extract_pot_size(self, frame: np.ndarray) -> float:
        """Extract pot size from frame"""
        roi = self._get_roi(frame, self.game_info_regions['pot'])
        text = self._ocr_text(roi, config='--psm 7')

        numbers = re.findall(r'[\d,.]+', text)
        if numbers:
            amount_str = numbers[0].replace(',', '')
            try:
                return float(amount_str)
            except ValueError:
                return 0.0
        return 0.0

    def _extract_blinds(self, frame: np.ndarray) -> Tuple[float, float]:
        """Extract small blind and big blind amounts"""
        roi = self._get_roi(frame, self.game_info_regions['blinds'])
        text = self._ocr_text(roi, config='--psm 7')

        # Look for pattern like "SB/BB" or "1/2"
        numbers = re.findall(r'[\d,.]+', text)
        if len(numbers) >= 2:
            try:
                sb = float(numbers[0].replace(',', ''))
                bb = float(numbers[1].replace(',', ''))
                return sb, bb
            except ValueError:
                pass

        return 0.0, 0.0

    def _detect_country_flag(self, frame: np.ndarray, player_key: str) -> str:
        """
        Detect country flag (placeholder - would need image matching)
        This is a simplified version - actual implementation would use template matching
        """
        # TODO: Implement flag detection using template matching
        return "Unknown"

    def analyze_frame(self, frame: np.ndarray, frame_number: int) -> GameState:
        """Analyze a single frame and extract game state"""
        game_state = GameState()

        # Extract player information
        for player_key in self.player_regions.keys():
            try:
                name = self._extract_player_name(frame, player_key)
                if name:  # Only add player if name detected
                    stack = self._extract_stack_amount(frame, player_key)
                    country = self._detect_country_flag(frame, player_key)

                    player = Player(
                        name=name,
                        country=country,
                        stack=stack,
                        seat_number=int(player_key.split('_')[1])
                    )
                    game_state.players.append(player)

                    # Extract action
                    action = self._extract_player_action(frame, player_key)
                    if action:
                        player_action = PlayerAction(
                            player_name=name,
                            action=action
                        )
                        game_state.actions.append(player_action)
            except Exception as e:
                print(f"Error processing {player_key}: {e}")
                continue

        # Extract pot size
        game_state.pot_size = self._extract_pot_size(frame)

        # Extract blinds
        sb, bb = self._extract_blinds(frame)
        game_state.small_blind = sb
        game_state.big_blind = bb

        return game_state

    def process_video(self, sample_rate: int = 30, output_dir: Optional[str] = None):
        """
        Process the entire video

        Args:
            sample_rate: Process every Nth frame
            output_dir: Optional directory to save debug images
        """
        frame_count = 0
        processed_count = 0

        print(f"Processing video: {self.video_path}")
        print(f"Total frames: {self.total_frames}, FPS: {self.fps}")
        print(f"Resolution: {self.width}x{self.height}")

        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            # Sample frames
            if frame_count % sample_rate == 0:
                try:
                    game_state = self.analyze_frame(frame, frame_count)
                    self.game_states.append(game_state)
                    processed_count += 1

                    if processed_count % 10 == 0:
                        print(f"Processed {processed_count} frames ({frame_count}/{self.total_frames})")

                    # Optionally save debug images
                    if output_dir:
                        debug_path = f"{output_dir}/frame_{frame_count:06d}.jpg"
                        cv2.imwrite(debug_path, frame)

                except Exception as e:
                    print(f"Error processing frame {frame_count}: {e}")

            frame_count += 1

        print(f"Processing complete. Analyzed {processed_count} frames.")
        return self.game_states

    def get_game_summary(self) -> Dict:
        """Generate a summary of extracted game data"""
        all_players = {}

        for game_state in self.game_states:
            for player in game_state.players:
                if player.name not in all_players:
                    all_players[player.name] = {
                        'name': player.name,
                        'country': player.country,
                        'appearances': 0,
                        'total_actions': 0
                    }
                all_players[player.name]['appearances'] += 1

            all_players[player.name]['total_actions'] += len(game_state.actions)

        return {
            'total_game_states': len(self.game_states),
            'players': list(all_players.values())
        }

    def release(self):
        """Release video capture"""
        if self.cap:
            self.cap.release()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()


if __name__ == "__main__":
    # Test the analyzer
    video_path = r"C:\Users\Julia\Downloads\Spin_and_Go.mp4"

    with PokerVideoAnalyzer(video_path) as analyzer:
        # Process first 100 frames for testing
        analyzer.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

        for i in range(5):  # Test first 5 frames
            ret, frame = analyzer.cap.read()
            if ret:
                game_state = analyzer.analyze_frame(frame, i)
                print(f"\nFrame {i}:")
                print(f"  Players: {len(game_state.players)}")
                for player in game_state.players:
                    print(f"    - {player.name}: ${player.stack}")
                print(f"  Pot: ${game_state.pot_size}")
                print(f"  Blinds: ${game_state.small_blind}/${game_state.big_blind}")
