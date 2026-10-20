"""
Cursor controller with natural Bezier movement and overshoot correction.
"""

import logging
import time
import pyautogui
import numpy as np
from typing import Tuple, List, Optional

from src.behavior.randomness_utils import (
    bezier_control_point,
    probability_check,
    random_int_in_range,
    jitter_value
)
from src.utils.screen_utils import clamp_to_screen, distance_between_points

logger = logging.getLogger(__name__)


class CursorController:
    """Controls cursor movement with human-like behavior."""
    
    def __init__(self, cursor_config: dict):
        """
        Initialize cursor controller.
        
        Args:
            cursor_config: Cursor configuration dictionary
        """
        self.config = cursor_config
        self.speed_multiplier = cursor_config.get('speed_multiplier', 1.0)
        self.bezier_control_points = cursor_config.get('bezier_control_points', 3)
        self.movement_fps = cursor_config.get('movement_fps', 60)
        self.jitter_amplitude = cursor_config.get('jitter_amplitude', 1.5)
        self.jitter_frequency = cursor_config.get('jitter_frequency', 0.1)
        self.total_distance_moved = 0.0
        
    def get_position(self) -> Tuple[int, int]:
        """
        Get current cursor position.
        
        Returns:
            Tuple of (x, y) coordinates
        """
        return pyautogui.position()
    
    def move_to(self, target_x: int, target_y: int, 
                overshoot: bool = True,
                overshoot_probability: float = 0.20) -> bool:
        """
        Move cursor to target position with natural Bezier curve movement.
        
        Args:
            target_x: Target X coordinate
            target_y: Target Y coordinate
            overshoot: Whether to allow overshoot correction
            overshoot_probability: Probability of overshooting
            
        Returns:
            True if movement successful, False otherwise
        """
        try:
            # Get start position
            start_x, start_y = self.get_position()
            
            # Check if overshoot should occur
            should_overshoot = overshoot and probability_check(overshoot_probability)
            
            if should_overshoot:
                # Move past target, then correct
                overshoot_distance = random_int_in_range(3, 8)
                overshoot_target = self._calculate_overshoot_point(
                    start_x, start_y, target_x, target_y, overshoot_distance
                )
                
                logger.debug(f"Overshoot enabled: {overshoot_distance}px past target")
                
                # Move to overshoot point
                self._move_along_bezier(start_x, start_y, 
                                       overshoot_target[0], overshoot_target[1])
                
                # Pause briefly
                time.sleep(0.1)
                
                # Correct back to target (slower)
                overshoot_x, overshoot_y = self.get_position()
                self._move_along_bezier(overshoot_x, overshoot_y, 
                                       target_x, target_y,
                                       speed_modifier=0.6)
            else:
                # Normal movement to target
                self._move_along_bezier(start_x, start_y, target_x, target_y)
            
            # Apply final jitter if enabled
            if probability_check(self.jitter_frequency):
                self._apply_jitter()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to move cursor: {e}")
            return False
    
    def _move_along_bezier(self, start_x: int, start_y: int, 
                           end_x: int, end_y: int,
                           speed_modifier: float = 1.0):
        """
        Move cursor along a Bezier curve path.
        
        Args:
            start_x, start_y: Starting coordinates
            end_x, end_y: Ending coordinates
            speed_modifier: Speed adjustment factor
        """
        # Generate Bezier path
        path = self._generate_bezier_path(
            (start_x, start_y), 
            (end_x, end_y)
        )
        
        # Calculate movement duration based on distance
        distance = distance_between_points(start_x, start_y, end_x, end_y)
        base_duration = distance / (500.0 * self.speed_multiplier * speed_modifier)
        duration = max(0.1, base_duration)  # Minimum 100ms
        
        # Time per frame
        frame_time = 1.0 / self.movement_fps
        total_frames = int(duration / frame_time)
        
        if total_frames < 2:
            # Too short, just move directly
            pyautogui.moveTo(end_x, end_y, duration=0.1)
            self.total_distance_moved += distance
            return
        
        # Move along path
        for i, (x, y) in enumerate(path):
            # Clamp to screen
            x, y = clamp_to_screen(int(x), int(y))
            
            # Move to position
            pyautogui.moveTo(x, y, duration=0)
            
            # Sleep for frame time
            time.sleep(frame_time)
        
        # Ensure we end exactly on target
        pyautogui.moveTo(end_x, end_y, duration=0)
        self.total_distance_moved += distance
        
        logger.debug(f"Cursor moved: ({start_x},{start_y}) → ({end_x},{end_y}), "
                    f"distance: {distance:.1f}px, duration: {duration:.2f}s")
    
    def _generate_bezier_path(self, start: Tuple[float, float], 
                             end: Tuple[float, float],
                             num_points: int = 50) -> List[Tuple[float, float]]:
        """
        Generate a Bezier curve path from start to end.
        
        Args:
            start: Starting point (x, y)
            end: Ending point (x, y)
            num_points: Number of points in path
            
        Returns:
            List of (x, y) points along curve
        """
        # Generate control points
        control_points = [start]
        
        for _ in range(self.bezier_control_points - 2):
            cp = bezier_control_point(start, end, variance=0.3)
            control_points.append(cp)
        
        control_points.append(end)
        
        # Generate Bezier curve
        t_values = np.linspace(0, 1, num_points)
        path = []
        
        for t in t_values:
            point = self._bezier_point(control_points, t)
            path.append(point)
        
        return path
    
    def _bezier_point(self, control_points: List[Tuple[float, float]], 
                     t: float) -> Tuple[float, float]:
        """
        Calculate a point on a Bezier curve.
        
        Args:
            control_points: List of control points
            t: Parameter (0 to 1)
            
        Returns:
            Point (x, y) on curve at parameter t
        """
        n = len(control_points) - 1
        x = 0.0
        y = 0.0
        
        for i, (px, py) in enumerate(control_points):
            # Bernstein polynomial
            coeff = self._binomial_coeff(n, i) * (1 - t) ** (n - i) * t ** i
            x += coeff * px
            y += coeff * py
        
        return (x, y)
    
    @staticmethod
    def _binomial_coeff(n: int, k: int) -> int:
        """Calculate binomial coefficient."""
        if k > n:
            return 0
        if k == 0 or k == n:
            return 1
        
        # Use factorial formula
        from math import factorial
        return factorial(n) // (factorial(k) * factorial(n - k))
    
    def _calculate_overshoot_point(self, start_x: int, start_y: int,
                                  target_x: int, target_y: int,
                                  overshoot_distance: int) -> Tuple[int, int]:
        """
        Calculate overshoot point past target.
        
        Args:
            start_x, start_y: Starting coordinates
            target_x, target_y: Target coordinates
            overshoot_distance: Distance past target in pixels
            
        Returns:
            Overshoot point (x, y)
        """
        # Calculate direction vector
        dx = target_x - start_x
        dy = target_y - start_y
        distance = (dx ** 2 + dy ** 2) ** 0.5
        
        if distance == 0:
            return (target_x, target_y)
        
        # Normalize and extend
        ndx = dx / distance
        ndy = dy / distance
        
        overshoot_x = int(target_x + ndx * overshoot_distance)
        overshoot_y = int(target_y + ndy * overshoot_distance)
        
        # Clamp to screen
        return clamp_to_screen(overshoot_x, overshoot_y)
    
    def _apply_jitter(self):
        """Apply small jitter to current cursor position."""
        x, y = self.get_position()
        
        jittered_x = jitter_value(x, self.jitter_amplitude)
        jittered_y = jitter_value(y, self.jitter_amplitude)
        
        jittered_x, jittered_y = clamp_to_screen(int(jittered_x), int(jittered_y))
        
        try:
            pyautogui.moveTo(jittered_x, jittered_y, duration=0.05)
        except Exception:
            pass
    
    def get_total_distance_moved(self) -> float:
        """Get total distance cursor has moved this session."""
        return self.total_distance_moved


def create_cursor_controller(cursor_config: dict) -> CursorController:
    """
    Create a cursor controller from configuration.
    
    Args:
        cursor_config: Cursor configuration dictionary
        
    Returns:
        Configured CursorController instance
    """
    return CursorController(cursor_config)
