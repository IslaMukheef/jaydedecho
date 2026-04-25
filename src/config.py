"""
Configuration management for JaydeEcho
Loads and validates environment variables and settings
"""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class Config:
    """Application configuration"""

    def __init__(self, env_path: str = ".env"):
        """Load configuration from .env file"""
        # Load .env from project root
        env_file = Path(__file__).parent.parent / env_path
        if env_file.exists():
            load_dotenv(env_file)
            logger.info(f"Loaded configuration from {env_file}")
        else:
            logger.warning(f"Config file not found: {env_file}")

        # Validate required API keys
        self._validate_keys()

        # Load all settings
        self._load_settings()

    def _validate_keys(self):
        """Check that required API keys are present"""
        required_keys = ["GEMINI_API_KEY"]
        missing = [k for k in required_keys if not os.getenv(k)]

        if missing:
            logger.warning(f"Missing API keys: {', '.join(missing)}")
            logger.warning("Set these in your .env file or environment variables")

    def _load_settings(self):
        """Load all configuration settings"""
        # API Keys
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")
        self.openrouteservice_api_key = os.getenv("OPENROUTESERVICE_API_KEY", "")

        # Camera
        self.camera_device_id = int(os.getenv("CAMERA_DEVICE_ID", "0"))
        self.camera_width = int(os.getenv("CAMERA_WIDTH", "1280"))
        self.camera_height = int(os.getenv("CAMERA_HEIGHT", "720"))
        self.camera_fps = int(os.getenv("CAMERA_FPS", "30"))

        # Location
        self.default_location_lat = float(os.getenv("DEFAULT_LOCATION_LAT", "43.8509"))
        self.default_location_lng = float(os.getenv("DEFAULT_LOCATION_LNG", "-79.0204"))

        # Audio
        self.audio_output_device = os.getenv("AUDIO_OUTPUT_DEVICE", "default")

        # Game Mode
        self.game_mode_enabled = os.getenv("GAME_MODE_ENABLED", "true").lower() == "true"
        self.default_game = os.getenv("DEFAULT_GAME", "floor_is_lava")

        # Debug
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        self.log_level = os.getenv("LOG_LEVEL", "INFO")

        logger.info(f"Configuration loaded (debug={self.debug}, game_mode={self.game_mode_enabled})")

    def __repr__(self):
        """String representation of config (without sensitive keys)"""
        return (
            f"Config(gemini={'***' if self.gemini_api_key else 'MISSING'}, "
            f"camera={self.camera_device_id}, debug={self.debug})"
        )
