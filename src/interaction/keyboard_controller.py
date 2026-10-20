"""
Keyboard controller for keystroke simulation.
"""

import logging
import time
import pyautogui
from typing import List

logger = logging.getLogger(__name__)


class KeyboardController:
    """Controls keyboard input simulation."""
    
    def __init__(self, dry_run: bool = False):
        """
        Initialize keyboard controller.
        
        Args:
            dry_run: If True, don't actually press keys (testing mode)
        """
        self.dry_run = dry_run
    
    def press_key(self, key: str, duration: float = 0.1) -> bool:
        """
        Press and release a key.
        
        Args:
            key: Key name (e.g., 'enter', 'space', 'a')
            duration: Hold duration in seconds
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.dry_run:
                logger.info(f"[DRY RUN] Would press key: {key}")
                return True
            
            logger.debug(f"Pressing key: {key}")
            pyautogui.press(key)
            time.sleep(duration)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to press key '{key}': {e}")
            return False
    
    def key_combination(self, *keys: str) -> bool:
        """
        Press a combination of keys (e.g., Ctrl+C).
        
        Args:
            *keys: Keys to press together
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.dry_run:
                logger.info(f"[DRY RUN] Would press key combination: {'+'.join(keys)}")
                return True
            
            logger.debug(f"Pressing key combination: {'+'.join(keys)}")
            pyautogui.hotkey(*keys)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to press key combination {keys}: {e}")
            return False
    
    def type_text(self, text: str, interval: float = 0.1) -> bool:
        """
        Type text with natural timing.
        
        Args:
            text: Text to type
            interval: Interval between keystrokes
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.dry_run:
                logger.info(f"[DRY RUN] Would type text: {text}")
                return True
            
            logger.debug(f"Typing text: {text}")
            pyautogui.write(text, interval=interval)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to type text: {e}")
            return False


def create_keyboard_controller(dry_run: bool = False) -> KeyboardController:
    """
    Create a keyboard controller.
    
    Args:
        dry_run: Dry-run mode flag
        
    Returns:
        Configured KeyboardController instance
    """
    return KeyboardController(dry_run)
