"""
Validation utilities for configuration and environment checks.
"""

import os
from pathlib import Path
from typing import List, Optional, Dict, Any
import pyautogui


def validate_environment(config: Dict[str, Any]) -> List[str]:
    """
    Validate that the environment is properly set up.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        List of error messages (empty if valid)
    """
    errors = []
    
    # Check Python version
    import sys
    if sys.version_info < (3, 9):
        errors.append("Python 3.9 or higher required")
    
    # Check required environment variables
    required_env = [
        'RECORDER_APP_TITLE',
        'BROWSER_WINDOW_TITLE',
        'START_BUTTON_X',
        'START_BUTTON_Y',
        'STOP_BUTTON_X',
        'STOP_BUTTON_Y'
    ]
    
    for var in required_env:
        if not os.getenv(var):
            errors.append(f"Missing environment variable: {var}")
    
    # Validate button coordinates are on screen
    try:
        start_x = int(os.getenv('START_BUTTON_X', 0))
        start_y = int(os.getenv('START_BUTTON_Y', 0))
        stop_x = int(os.getenv('STOP_BUTTON_X', 0))
        stop_y = int(os.getenv('STOP_BUTTON_Y', 0))
        
        screen_width, screen_height = pyautogui.size()
        
        if not (0 <= start_x < screen_width and 0 <= start_y < screen_height):
            errors.append(f"START button position ({start_x}, {start_y}) is off screen")
        
        if not (0 <= stop_x < screen_width and 0 <= stop_y < screen_height):
            errors.append(f"STOP button position ({stop_x}, {stop_y}) is off screen")
            
    except (ValueError, TypeError) as e:
        errors.append(f"Invalid button coordinate format: {e}")
    
    # Check PyAutoGUI fail-safe
    if not pyautogui.FAILSAFE:
        errors.append("PyAutoGUI fail-safe is disabled (security risk)")
    
    return errors


def validate_config_value(value: Any, expected_type: type, 
                         min_val: Optional[float] = None,
                         max_val: Optional[float] = None) -> bool:
    """
    Validate a configuration value.
    
    Args:
        value: Value to validate
        expected_type: Expected type
        min_val: Minimum value (for numeric types)
        max_val: Maximum value (for numeric types)
        
    Returns:
        True if valid, False otherwise
    """
    # Type check
    if not isinstance(value, expected_type):
        return False
    
    # Range check for numeric types
    if isinstance(value, (int, float)):
        if min_val is not None and value < min_val:
            return False
        if max_val is not None and value > max_val:
            return False
    
    return True


def validate_probability(value: float) -> bool:
    """
    Validate a probability value (must be between 0 and 1).
    
    Args:
        value: Probability value
        
    Returns:
        True if valid probability, False otherwise
    """
    return isinstance(value, (int, float)) and 0.0 <= value <= 1.0


def validate_timing_config(timing: Dict[str, float]) -> List[str]:
    """
    Validate timing configuration section.
    
    Args:
        timing: Timing configuration dictionary
        
    Returns:
        List of error messages (empty if valid)
    """
    errors = []
    
    required_keys = [
        'watch_duration_mean',
        'watch_duration_std',
        'cooldown_mean',
        'cooldown_std'
    ]
    
    for key in required_keys:
        if key not in timing:
            errors.append(f"Missing timing config: {key}")
            continue
        
        value = timing[key]
        if not isinstance(value, (int, float)) or value < 0:
            errors.append(f"Invalid timing value for {key}: {value}")
    
    # Check that standard deviations are reasonable
    if 'watch_duration_mean' in timing and 'watch_duration_std' in timing:
        mean = timing['watch_duration_mean']
        std = timing['watch_duration_std']
        if std > mean * 0.3:  # Std > 30% of mean is probably too much variance
            errors.append(f"watch_duration_std ({std}) is too large for mean ({mean})")
    
    return errors


def validate_behavior_config(behavior: Dict[str, Any]) -> List[str]:
    """
    Validate behavior configuration section.
    
    Args:
        behavior: Behavior configuration dictionary
        
    Returns:
        List of error messages (empty if valid)
    """
    errors = []
    
    # Validate probabilities
    prob_keys = [
        'overshoot_probability',
        'micro_distraction_probability',
        'bio_break_probability'
    ]
    
    for key in prob_keys:
        if key in behavior and not validate_probability(behavior[key]):
            errors.append(f"Invalid probability for {key}: {behavior[key]}")
    
    # Validate micro-actions sum to 1.0
    if 'micro_actions' in behavior:
        total = sum(behavior['micro_actions'].values())
        if abs(total - 1.0) > 0.01:  # Allow small floating point error
            errors.append(f"Micro-actions probabilities must sum to 1.0 (got {total})")
    
    return errors


def ensure_directory_exists(path: Path) -> bool:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        path: Directory path
        
    Returns:
        True if directory exists or was created, False on error
    """
    try:
        path.mkdir(parents=True, exist_ok=True)
        return True
    except (OSError, PermissionError):
        return False
