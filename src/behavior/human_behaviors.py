"""
Human behavior emulation - micro-distractions and natural actions.
"""

import logging
import pyautogui
from typing import Dict, Any
from enum import Enum

from src.behavior.randomness_utils import (
    weighted_choice,
    probability_check,
    random_int_in_range,
    random_in_range
)

logger = logging.getLogger(__name__)


class MicroAction(Enum):
    """Types of micro-actions that simulate human behavior."""
    IDLE_SCROLL = "idle_scroll"
    CURSOR_DRIFT = "cursor_drift"
    TAB_FOCUS_SHIFT = "tab_focus_shift"
    MICRO_PAUSE = "micro_pause"
    HAND_READJUST = "hand_readjust"


class HumanBehaviors:
    """Simulates natural human behaviors and micro-distractions."""
    
    def __init__(self, behavior_config: Dict[str, Any]):
        """
        Initialize human behaviors module.
        
        Args:
            behavior_config: Behavior configuration dictionary
        """
        self.config = behavior_config
        self.micro_actions = behavior_config.get('micro_actions', {})
        self.micro_distraction_probability = behavior_config.get(
            'micro_distraction_probability', 0.25
        )
    
    def should_perform_micro_distraction(self) -> bool:
        """
        Check if a micro-distraction should occur.
        
        Returns:
            True if micro-distraction should be performed
        """
        return probability_check(self.micro_distraction_probability)
    
    def perform_random_micro_action(self):
        """Perform a random micro-action based on configured probabilities."""
        # Get action choices and weights
        actions = list(self.micro_actions.keys())
        weights = list(self.micro_actions.values())
        
        if not actions:
            return
        
        # Select action
        action_name = weighted_choice(actions, weights)
        action = MicroAction(action_name)
        
        logger.debug(f"Performing micro-action: {action.value}")
        
        # Execute action
        if action == MicroAction.IDLE_SCROLL:
            self._idle_scroll()
        elif action == MicroAction.CURSOR_DRIFT:
            self._cursor_drift()
        elif action == MicroAction.TAB_FOCUS_SHIFT:
            self._tab_focus_shift()
        elif action == MicroAction.MICRO_PAUSE:
            self._micro_pause()
        elif action == MicroAction.HAND_READJUST:
            self._hand_readjust()
    
    def _idle_scroll(self):
        """Simulate idle scrolling (small mouse wheel movement)."""
        # Random scroll amount (1-3 ticks)
        scroll_amount = random_int_in_range(1, 3)
        
        # Random direction (50% up, 50% down)
        direction = 1 if probability_check(0.5) else -1
        
        try:
            pyautogui.scroll(scroll_amount * direction)
            logger.debug(f"Idle scroll: {scroll_amount * direction} ticks")
        except Exception as e:
            logger.warning(f"Failed to perform idle scroll: {e}")
    
    def _cursor_drift(self):
        """Simulate slow cursor drift (hand repositioning)."""
        # Get current position
        current_x, current_y = pyautogui.position()
        
        # Random drift distance (10-30 pixels)
        drift_distance = random_int_in_range(10, 30)
        
        # Random direction
        import math
        angle = random_in_range(0, 2 * math.pi)
        
        # Calculate new position
        new_x = int(current_x + drift_distance * math.cos(angle))
        new_y = int(current_y + drift_distance * math.sin(angle))
        
        # Clamp to screen
        from src.utils.screen_utils import clamp_to_screen
        new_x, new_y = clamp_to_screen(new_x, new_y)
        
        try:
            # Slow movement (1-2 seconds)
            duration = random_in_range(1.0, 2.0)
            pyautogui.moveTo(new_x, new_y, duration=duration)
            logger.debug(f"Cursor drift: ({current_x},{current_y}) -> ({new_x},{new_y})")
        except Exception as e:
            logger.warning(f"Failed to perform cursor drift: {e}")
    
    def _tab_focus_shift(self):
        """Simulate Alt+Tab press without actually switching (just the keystroke)."""
        # This simulates accidentally pressing Alt+Tab but quickly returning
        # In practice, we just do a very brief Alt press
        try:
            import time
            pyautogui.keyDown('alt')
            time.sleep(0.05)  # Very brief
            pyautogui.keyUp('alt')
            logger.debug("Tab focus shift (fake Alt+Tab)")
        except Exception as e:
            logger.warning(f"Failed to perform tab focus shift: {e}")
    
    def _micro_pause(self):
        """Simulate complete stillness (user reading or thinking)."""
        import time
        pause_duration = random_in_range(0.8, 2.0)
        logger.debug(f"Micro-pause: {pause_duration:.2f}s")
        time.sleep(pause_duration)
    
    def _hand_readjust(self):
        """Simulate small hand readjustment on mouse."""
        # Very small position change (5-15 pixels)
        current_x, current_y = pyautogui.position()
        
        offset_x = random_int_in_range(-15, 15)
        offset_y = random_int_in_range(-15, 15)
        
        new_x = current_x + offset_x
        new_y = current_y + offset_y
        
        from src.utils.screen_utils import clamp_to_screen
        new_x, new_y = clamp_to_screen(new_x, new_y)
        
        try:
            # Quick movement
            duration = random_in_range(0.1, 0.3)
            pyautogui.moveTo(new_x, new_y, duration=duration)
            logger.debug(f"Hand readjust: offset ({offset_x},{offset_y})")
        except Exception as e:
            logger.warning(f"Failed to perform hand readjust: {e}")


def create_human_behaviors(behavior_config: Dict[str, Any]) -> HumanBehaviors:
    """
    Create a HumanBehaviors instance from configuration.
    
    Args:
        behavior_config: Behavior configuration dictionary
        
    Returns:
        Configured HumanBehaviors instance
    """
    return HumanBehaviors(behavior_config)
