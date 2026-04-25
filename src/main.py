"""
JaydeEcho - Voice-first AI assistant for visually impaired navigation
Main entry point for the application
"""

import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from config import Config
from camera import Camera
from vision import Vision
from speech import Speech
from router import Router
from game_mode import GameMode

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class JaydeEcho:
    """Main application controller"""

    def __init__(self):
        """Initialize all components"""
        self.config = Config()
        self.camera = Camera(self.config)
        self.vision = Vision(self.config)
        self.speech = Speech(self.config)
        self.router = Router(self.config)
        self.game_mode = GameMode(self.config)
        self.running = False
        self.current_mode = "navigation"  # "navigation" or "game"

        logger.info("JaydeEcho initialized successfully")

    def start(self):
        """Start the main application loop"""
        self.running = True
        logger.info("JaydeEcho started. Listening for commands...")

        try:
            self._main_loop()
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            self.stop()

    def _main_loop(self):
        """Main event loop - respond to user commands"""
        while self.running:
            try:
                # Listen for trigger (keypress or voice command)
                command = self._wait_for_trigger()

                if command == "quit":
                    break
                elif command.startswith("navigate:"):
                    destination = command.replace("navigate:", "").strip()
                    self._handle_navigation(destination)
                elif command.startswith("describe"):
                    self._handle_scene_description()
                elif command.startswith("game:"):
                    game_type = command.replace("game:", "").strip()
                    self._handle_game_mode(game_type)
                else:
                    self._handle_query(command)

            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                self.speech.speak(f"Error: {str(e)}")

    def _wait_for_trigger(self) -> str:
        """Wait for user trigger (simplified placeholder)"""
        # TODO: Implement voice command detection or keypress listener
        print("\n[Press SPACE + letter for command, or enter command text]")
        print("  d = describe scene")
        print("  n = navigate (enter destination)")
        print("  g = game mode")
        print("  q = quit")

        user_input = input("> ").strip().lower()

        if user_input == "d":
            return "describe"
        elif user_input == "n":
            dest = input("Destination: ").strip()
            return f"navigate:{dest}"
        elif user_input == "g":
            game = input("Game (floor_is_lava): ").strip() or "floor_is_lava"
            return f"game:{game}"
        elif user_input == "q":
            return "quit"
        else:
            return user_input

    def _handle_scene_description(self):
        """Capture frame and describe surroundings"""
        logger.info("Capturing scene...")
        frame = self.camera.capture_frame()

        if frame is None:
            self.speech.speak("Could not capture camera frame")
            return

        response = self.vision.describe_scene(frame)
        logger.info(f"Vision response: {response}")
        self.speech.speak(response)

    def _handle_navigation(self, destination: str):
        """Plan and announce route"""
        logger.info(f"Planning route to {destination}...")
        route_text = self.router.plan_route(destination)

        if route_text:
            self.speech.speak(route_text)
        else:
            self.speech.speak(f"Could not find route to {destination}")

    def _handle_query(self, query: str):
        """Handle natural language query with vision context"""
        logger.info(f"User query: {query}")
        frame = self.camera.capture_frame()

        if frame is None:
            self.speech.speak("Could not capture camera frame")
            return

        response = self.vision.get_guidance(frame, query)
        logger.info(f"Vision response: {response}")
        self.speech.speak(response)

    def _handle_game_mode(self, game_type: str):
        """Start interactive game"""
        logger.info(f"Starting game: {game_type}")
        game_message = self.game_mode.start_game(game_type)
        if game_message:
            self.speech.speak(game_message)

    def stop(self):
        """Clean up and shut down"""
        self.running = False
        self.camera.cleanup()
        logger.info("JaydeEcho shutdown complete")


def main():
    """Application entry point"""
    app = JaydeEcho()
    app.start()


if __name__ == "__main__":
    main()
