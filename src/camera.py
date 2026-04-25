"""
Camera module - captures frames from connected camera device
Supports Logitech Brio, standard webcams, and mobile cameras
"""

import cv2
import base64
import logging
from typing import Optional, List
import numpy as np

logger = logging.getLogger(__name__)


class Camera:
    """Camera capture and processing"""

    def __init__(self, config):
        """Initialize camera with configuration"""
        self.config = config
        self.cap = None
        self.frame_buffer = []
        self.max_buffer_size = 5
        self.current_device_id = config.camera_device_id

        self._initialize_camera()

    @staticmethod
    def list_available_cameras() -> List[dict]:
        """Detect all available camera devices"""
        available_cameras = []

        # Try first 10 devices
        for device_id in range(10):
            cap = cv2.VideoCapture(device_id)
            if cap is not None and cap.isOpened():
                ret, _ = cap.read()
                if ret:
                    # Get camera info
                    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    fps = int(cap.get(cv2.CAP_PROP_FPS))

                    available_cameras.append({
                        "id": device_id,
                        "name": f"Camera {device_id}",
                        "resolution": f"{width}x{height}",
                        "fps": fps,
                    })
                cap.release()

        return available_cameras

    def _initialize_camera(self):
        """Setup camera device"""
        try:
            self.cap = cv2.VideoCapture(self.current_device_id)

            # Set resolution
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.camera_width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.camera_height)
            self.cap.set(cv2.CAP_PROP_FPS, self.config.camera_fps)

            # Test frame capture
            ret, _ = self.cap.read()
            if ret:
                logger.info(
                    f"Camera initialized: device={self.current_device_id}, "
                    f"resolution={self.config.camera_width}x{self.config.camera_height}, "
                    f"fps={self.config.camera_fps}"
                )
            else:
                logger.error("Camera device found but cannot read frames")
                self.cap = None

        except Exception as e:
            logger.error(f"Failed to initialize camera: {e}")
            self.cap = None

    def switch_camera(self, device_id: int) -> bool:
        """Switch to a different camera device"""
        try:
            # Release current camera
            if self.cap is not None:
                self.cap.release()

            self.current_device_id = device_id
            self._initialize_camera()

            return self.cap is not None and self.cap.isOpened()
        except Exception as e:
            logger.error(f"Error switching camera: {e}")
            return False

    def capture_frame(self) -> Optional[np.ndarray]:
        """Capture single frame from camera"""
        if self.cap is None or not self.cap.isOpened():
            logger.error("Camera not initialized or closed")
            return None

        try:
            ret, frame = self.cap.read()
            if ret:
                # Add to rolling buffer
                self.frame_buffer.append(frame.copy())
                if len(self.frame_buffer) > self.max_buffer_size:
                    self.frame_buffer.pop(0)

                return frame
            else:
                logger.error("Failed to read frame from camera")
                return None

        except Exception as e:
            logger.error(f"Error capturing frame: {e}")
            return None

    def frame_to_base64(self, frame: np.ndarray, format: str = ".jpg") -> str:
        """Convert frame to base64 for API transmission"""
        try:
            _, buffer = cv2.imencode(format, frame)
            encoded = base64.b64encode(buffer).decode("utf-8")
            return encoded
        except Exception as e:
            logger.error(f"Error encoding frame to base64: {e}")
            return ""

    def get_frames_buffer(self) -> List[np.ndarray]:
        """Get rolling buffer of recent frames for context"""
        return self.frame_buffer.copy()

    def cleanup(self):
        """Release camera resources"""
        if self.cap is not None:
            self.cap.release()
            logger.info("Camera released")

