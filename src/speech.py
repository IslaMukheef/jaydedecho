"""
Speech module - text-to-speech synthesis using system voices
Uses pyttsx3 for cross-platform TTS (Windows, macOS, Linux)
"""

import logging
from typing import Optional

try:
    import pyttsx3
except ImportError:
    logger = logging.getLogger(__name__)
    logger.warning("pyttsx3 not installed. Install with: pip install pyttsx3")
    pyttsx3 = None

logger = logging.getLogger(__name__)


class Speech:
    """Text-to-speech synthesis using system voices (pyttsx3)"""

    def __init__(self, config):
        """Initialize TTS engine"""
        self.config = config

        if pyttsx3 is None:
            logger.error("pyttsx3 module not available")
            self.available = False
            self.engine = None
            return

        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty("rate", 150)  # Speed of speech
            self.engine.setProperty("volume", 0.9)  # Volume (0.0-1.0)
            self.available = True
            logger.info("System TTS initialized (pyttsx3)")
        except Exception as e:
            logger.error(f"Failed to initialize TTS: {e}")
            self.available = False
            self.engine = None

    def speak(self, text: str, tone: str = "neutral") -> bool:
        """
        Synthesize and play text as speech using system TTS
        tone: "neutral", "urgent", "calm", "informative"
        """
        if not self.available or self.engine is None:
            logger.error("Speech service unavailable")
            return False

        if not text or not text.strip():
            logger.warning("Empty text provided to speak()")
            return False

        try:
            logger.info(f"Speaking: {text[:50]}...")

            # Adjust speech rate based on tone
            if tone == "urgent":
                self.engine.setProperty("rate", 200)  # Faster
            elif tone == "calm":
                self.engine.setProperty("rate", 120)  # Slower
            else:
                self.engine.setProperty("rate", 150)  # Normal

            # Speak the text
            self.engine.say(text)
            self.engine.runAndWait()

            return True

        except Exception as e:
            logger.error(f"Error in speak: {e}")
            return False

    def speak_async(self, text: str, tone: str = "neutral") -> bool:
        """
        Synthesize speech (pyttsx3 is blocking, so async is same as speak)
        """
        return self.speak(text, tone)

    def get_voice_id(self, voice_name: str = "default") -> str:
        """Get available system voice"""
        if self.engine is None:
            return "default"

        try:
            voices = self.engine.getProperty("voices")
            if len(voices) > 1:
                # Return second voice if available (usually female)
                return voices[1].id
            elif len(voices) > 0:
                return voices[0].id
        except:
            pass

        return "default"
