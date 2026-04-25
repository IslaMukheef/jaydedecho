"""
Game Mode module - interactive games for engagement
Includes "floor is lava" and other accessibility-friendly games
"""

import logging
import random
from typing import Optional
from enum import Enum

logger = logging.getLogger(__name__)


class GameType(Enum):
    """Available game types"""
    FLOOR_IS_LAVA = "floor_is_lava"
    OBSTACLE_COURSE = "obstacle_course"
    SOUND_HUNT = "sound_hunt"


class GameMode:
    """Interactive game system"""

    def __init__(self, config):
        """Initialize game mode"""
        self.config = config
        self.current_game = None
        self.score = 0
        self.game_active = False

        logger.info("Game Mode initialized")

    def start_game(self, game_type: str) -> str:
        """Start a game session"""
        if not self.config.game_mode_enabled:
            return "Game mode is disabled"

        try:
            game = GameType(game_type)
            self.current_game = game
            self.game_active = True
            self.score = 0

            logger.info(f"Starting game: {game_type}")

            if game == GameType.FLOOR_IS_LAVA:
                return self._start_floor_is_lava()
            elif game == GameType.OBSTACLE_COURSE:
                return self._start_obstacle_course()
            elif game == GameType.SOUND_HUNT:
                return self._start_sound_hunt()

        except ValueError:
            return f"Unknown game: {game_type}. Try 'floor_is_lava'"
        except Exception as e:
            logger.error(f"Error starting game: {e}")
            return f"Could not start game: {str(e)}"

    def _start_floor_is_lava(self) -> str:
        """Initialize Floor is Lava game"""
        return (
            "Welcome to Floor is Lava! Move around and avoid the ground. "
            "I'll alert you when lava approaches. Press spacebar to jump. Good luck!"
        )

    def _start_obstacle_course(self) -> str:
        """Initialize Obstacle Course game"""
        return (
            "Welcome to Obstacle Course! Navigate through a series of challenges. "
            "I'll guide you around obstacles. Good luck!"
        )

    def _start_sound_hunt(self) -> str:
        """Initialize Sound Hunt game"""
        return (
            "Welcome to Sound Hunt! Find the hidden sounds by moving around. "
            "The sound will get louder as you get closer. Good luck!"
        )

    def process_move(self, direction: str, distance: float) -> str:
        """
        Process player movement and game logic
        direction: "forward", "left", "right", "back"
        distance: distance moved in meters
        """
        if not self.game_active:
            return "No game in progress"

        try:
            if self.current_game == GameType.FLOOR_IS_LAVA:
                return self._process_floor_is_lava_move(direction, distance)
            elif self.current_game == GameType.OBSTACLE_COURSE:
                return self._process_obstacle_course_move(direction, distance)
            elif self.current_game == GameType.SOUND_HUNT:
                return self._process_sound_hunt_move(direction, distance)

        except Exception as e:
            logger.error(f"Error processing move: {e}")
            return f"Error: {str(e)}"

    def _process_floor_is_lava_move(self, direction: str, distance: float) -> str:
        """Game logic for Floor is Lava"""
        # Simulate random lava hazards
        hazard_chance = random.random()

        if hazard_chance > 0.7:
            self.score += int(distance * 10)  # Reward safe movement
            return f"Good move! You advanced {distance}m safely. Score: {self.score}"
        elif hazard_chance > 0.4:
            return f"Lava coming from the {random.choice(['left', 'right'])}! Jump or move!"
        else:
            self.score += int(distance * 5)
            return f"You moved {distance}m. Keep going! Score: {self.score}"

    def _process_obstacle_course_move(self, direction: str, distance: float) -> str:
        """Game logic for Obstacle Course"""
        # Simulate obstacles
        if random.random() > 0.6:
            return f"Watch out! Obstacle ahead. Try moving {random.choice(['left', 'right'])}!"
        else:
            self.score += int(distance * 15)
            return f"Clear path! You progressed {distance}m. Score: {self.score}"

    def _process_sound_hunt_move(self, direction: str, distance: float) -> str:
        """Game logic for Sound Hunt"""
        # Simulate sound hunting
        proximity = random.random()

        if proximity > 0.8:
            self.score += 100
            return "You found the sound! Congratulations! Score: 100"
        elif proximity > 0.6:
            return "Getting warmer... The sound is close."
        elif proximity > 0.4:
            return "Moving in the right direction..."
        else:
            return "Try a different direction."

    def check_hazard(self, frame) -> Optional[str]:
        """
        Check for hazards in current frame (vision integration)
        Used during gameplay to detect obstacles
        """
        # This would use the vision module to detect hazards
        # Placeholder for integration with vision module
        logger.debug("Checking for hazards in frame")
        return None

    def end_game(self) -> str:
        """End current game session"""
        if not self.game_active:
            return "No game in progress"

        self.game_active = False
        game_name = self.current_game.value if self.current_game else "Unknown"
        result = f"Game Over! Final score: {self.score}"

        logger.info(f"Game ended: {game_name}, score: {self.score}")
        return result

    def get_score(self) -> int:
        """Get current game score"""
        return self.score
