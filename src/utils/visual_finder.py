"""
Visual button finder using pyautogui.locateOnScreen (OpenCV template matching).

Instead of hardcoded pixel coordinates, the bot takes a screenshot of the
current screen and looks for a saved button image inside it. This works
regardless of where the window is positioned.

Usage:
    from src.utils.visual_finder import VisualFinder

    finder = VisualFinder()
    center = finder.find("data/buttons/start_button.png")
    if center:
        pyautogui.click(center)
"""

import time
import logging
import pyautogui
from pathlib import Path
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

# pyautogui.locateOnScreen needs scrot on Linux for screenshots
# and opencv-python-headless for confidence parameter
try:
    import cv2  # noqa: F401
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    logger.warning("opencv not found – confidence matching disabled. "
                   "Install with: pip install opencv-python-headless")


class VisualFinder:
    """
    Finds UI elements on screen by image template matching.

    Parameters
    ----------
    confidence : float
        Match threshold 0–1. 0.8 is a good default; lower if misses occur,
        higher if false positives occur.
    retries : int
        How many times to retry before giving up.
    retry_delay : float
        Seconds to wait between retries.
    grayscale : bool
        Match in grayscale (faster, slightly less accurate).
    """

    def __init__(self,
                 confidence: float = 0.8,
                 retries: int = 5,
                 retry_delay: float = 0.6,
                 grayscale: bool = True):
        self.confidence = confidence if CV2_AVAILABLE else None
        self.retries = retries
        self.retry_delay = retry_delay
        self.grayscale = grayscale

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def find(self, image_path: str,
             confidence: float = None,
             region: Tuple[int, int, int, int] = None
             ) -> Optional[Tuple[int, int]]:
        """
        Find an image on the screen and return its centre coordinates.

        Parameters
        ----------
        image_path : str
            Path to the template image (PNG).
        confidence : float, optional
            Override the default confidence for this call.
        region : tuple (left, top, width, height), optional
            Restrict search to a screen region for speed/accuracy.

        Returns
        -------
        (x, y) centre of the match, or None if not found.
        """
        path = Path(image_path)
        if not path.exists():
            logger.error(f"Button image not found: {image_path}")
            return None

        conf = confidence if confidence is not None else self.confidence
        kwargs = {"grayscale": self.grayscale}
        if conf and CV2_AVAILABLE:
            kwargs["confidence"] = conf
        if region:
            kwargs["region"] = region

        for attempt in range(1, self.retries + 1):
            try:
                location = pyautogui.locateOnScreen(str(path), **kwargs)
                if location is not None:
                    cx = location.left + location.width // 2
                    cy = location.top + location.height // 2
                    logger.debug(
                        f"Found '{path.name}' at centre ({cx}, {cy}) "
                        f"[attempt {attempt}]"
                    )
                    return (cx, cy)
            except pyautogui.ImageNotFoundException:
                pass
            except Exception as exc:
                logger.warning(f"locateOnScreen error: {exc}")

            logger.debug(
                f"'{path.name}' not found (attempt {attempt}/{self.retries}), "
                f"retrying in {self.retry_delay}s …"
            )
            time.sleep(self.retry_delay)

        logger.warning(f"Could not locate '{path.name}' after {self.retries} attempts")
        return None

    def find_and_click(self, image_path: str,
                       confidence: float = None,
                       region: Tuple[int, int, int, int] = None,
                       dry_run: bool = False) -> bool:
        """
        Find an image on screen and click its centre.

        Returns True on success, False if not found.
        """
        centre = self.find(image_path, confidence=confidence, region=region)
        if centre is None:
            return False

        x, y = centre
        if dry_run:
            logger.info(f"[DRY RUN] Would click '{Path(image_path).name}' at ({x}, {y})")
            return True

        logger.info(f"Clicking '{Path(image_path).name}' at ({x}, {y})")
        # Natural hover then click
        pyautogui.moveTo(x, y, duration=0.3)
        time.sleep(0.15)
        pyautogui.click(x, y)
        time.sleep(0.2)
        return True

    def wait_for(self, image_path: str,
                 timeout: float = 10.0,
                 confidence: float = None) -> Optional[Tuple[int, int]]:
        """
        Wait up to `timeout` seconds for an image to appear on screen.

        Useful for waiting until Loggy3 switches from Start → Stop state.
        """
        deadline = time.time() + timeout
        path = Path(image_path)
        conf = confidence if confidence is not None else self.confidence
        kwargs = {"grayscale": self.grayscale}
        if conf and CV2_AVAILABLE:
            kwargs["confidence"] = conf

        while time.time() < deadline:
            try:
                location = pyautogui.locateOnScreen(str(path), **kwargs)
                if location is not None:
                    cx = location.left + location.width // 2
                    cy = location.top + location.height // 2
                    logger.debug(f"'{path.name}' appeared at ({cx}, {cy})")
                    return (cx, cy)
            except (pyautogui.ImageNotFoundException, Exception):
                pass
            time.sleep(0.4)

        logger.warning(f"Timed out waiting for '{path.name}' ({timeout}s)")
        return None
