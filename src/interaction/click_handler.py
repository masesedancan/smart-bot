"""
Click handler with human-like timing and hover behavior.
"""

import logging
import time
import pyautogui
from typing import Tuple

from src.behavior.timing_engine import TimingEngine

logger = logging.getLogger(__name__)


class ClickHandler:
    """Handles mouse clicks with human-like behavior."""
    
    def __init__(self, timing_engine: TimingEngine, dry_run: bool = False):
        """
        Initialize click handler.
        
        Args:
            timing_engine: Timing engine for delays
            dry_run: If True, don't actually click (testing mode)
        """
        self.timing_engine = timing_engine
        self.dry_run = dry_run
        self.total_clicks = 0
    
    def click_at(self, x: int, y: int, button: str = 'left',
                hover_first: bool = True) -> bool:
        """
        Perform a human-like click at specified position.
        
        Args:
            x: X coordinate
            y: Y coordinate
            button: Mouse button ('left', 'right', 'middle')
            hover_first: Whether to hover before clicking
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Move to position if needed
            current_x, current_y = pyautogui.position()
            if (current_x, current_y) != (x, y):
                logger.warning(f"Cursor not at expected position, moving...")
                pyautogui.moveTo(x, y, duration=0.2)
            
            # Hover before clicking
            if hover_first:
                hover_duration = self.timing_engine.get_hover_duration()
                logger.debug(f"Hovering for {hover_duration:.3f}s before click")
                time.sleep(hover_duration)
            
            if self.dry_run:
                logger.info(f"[DRY RUN] Would click {button} button at ({x}, {y})")
                self.total_clicks += 1
                return True
            
            # Get click duration
            click_duration = self.timing_engine.get_click_duration()
            
            # Perform click with hold time
            logger.debug(f"Clicking {button} button at ({x}, {y}), "
                        f"duration: {click_duration:.3f}s")
            
            # Press and hold
            pyautogui.mouseDown(x, y, button=button)
            time.sleep(click_duration)
            pyautogui.mouseUp(x, y, button=button)
            
            self.total_clicks += 1
            
            # Post-click pause
            pause = self.timing_engine.get_post_click_pause()
            logger.debug(f"Post-click pause: {pause:.3f}s")
            time.sleep(pause)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to click at ({x}, {y}): {e}")
            return False
    
    def hover(self, x: int, y: int, duration: float = None):
        """
        Hover at a position for a duration.
        
        Args:
            x: X coordinate
            y: Y coordinate
            duration: Duration in seconds (None = random)
        """
        if duration is None:
            duration = self.timing_engine.get_hover_duration()
        
        try:
            # Move to position
            current_x, current_y = pyautogui.position()
            if (current_x, current_y) != (x, y):
                pyautogui.moveTo(x, y, duration=0.2)
            
            logger.debug(f"Hovering at ({x}, {y}) for {duration:.2f}s")
            time.sleep(duration)
            
        except Exception as e:
            logger.warning(f"Failed to hover at ({x}, {y}): {e}")
    
    def double_click_at(self, x: int, y: int) -> bool:
        """
        Perform a double-click at specified position.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # First click
            if not self.click_at(x, y, hover_first=True):
                return False
            
            # Short pause between clicks
            time.sleep(0.1)
            
            # Second click (no hover)
            if not self.click_at(x, y, hover_first=False):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to double-click at ({x}, {y}): {e}")
            return False
    
    def get_total_clicks(self) -> int:
        """Get total number of clicks performed."""
        return self.total_clicks


def create_click_handler(timing_engine: TimingEngine, 
                        dry_run: bool = False) -> ClickHandler:
    """
    Create a click handler.
    
    Args:
        timing_engine: Timing engine instance
        dry_run: Dry-run mode flag
        
    Returns:
        Configured ClickHandler instance
    """
    return ClickHandler(timing_engine, dry_run)
