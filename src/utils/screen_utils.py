"""
Screen utility functions for resolution, scaling, and multi-monitor support.
"""

import pyautogui
from typing import Tuple, List, Optional


class ScreenUtils:
    """Utility functions for screen-related operations."""
    
    @staticmethod
    def get_screen_size() -> Tuple[int, int]:
        """
        Get the primary screen resolution.
        
        Returns:
            Tuple of (width, height) in pixels
        """
        size = pyautogui.size()
        return (size.width, size.height)
    
    @staticmethod
    def get_dpi_scale() -> float:
        """
        Detect DPI scaling factor (for high-DPI displays).
        
        Returns:
            Scale factor (1.0 = 100%, 1.5 = 150%, 2.0 = 200%)
        """
        # This is a simplified version - actual DPI detection is OS-specific
        # For now, return 1.0 (can be overridden in .env)
        return 1.0
    
    @staticmethod
    def adjust_for_dpi(x: int, y: int, scale: float = 1.0) -> Tuple[int, int]:
        """
        Adjust coordinates for DPI scaling.
        
        Args:
            x: X coordinate
            y: Y coordinate
            scale: DPI scale factor
            
        Returns:
            Adjusted (x, y) coordinates
        """
        if scale == 1.0:
            return (x, y)
        return (int(x * scale), int(y * scale))
    
    @staticmethod
    def is_point_on_screen(x: int, y: int) -> bool:
        """
        Check if a point is within screen boundaries.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            True if point is on screen, False otherwise
        """
        width, height = ScreenUtils.get_screen_size()
        return 0 <= x < width and 0 <= y < height
    
    @staticmethod
    def clamp_to_screen(x: int, y: int) -> Tuple[int, int]:
        """
        Clamp coordinates to screen boundaries.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            Clamped (x, y) coordinates
        """
        width, height = ScreenUtils.get_screen_size()
        clamped_x = max(0, min(x, width - 1))
        clamped_y = max(0, min(y, height - 1))
        return (clamped_x, clamped_y)
    
    @staticmethod
    def get_center_point() -> Tuple[int, int]:
        """
        Get the center point of the screen.
        
        Returns:
            (x, y) coordinates of screen center
        """
        width, height = ScreenUtils.get_screen_size()
        return (width // 2, height // 2)
    
    @staticmethod
    def distance_between_points(x1: int, y1: int, x2: int, y2: int) -> float:
        """
        Calculate Euclidean distance between two points.
        
        Args:
            x1, y1: First point coordinates
            x2, y2: Second point coordinates
            
        Returns:
            Distance in pixels
        """
        return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5


# Convenience functions
def get_screen_size() -> Tuple[int, int]:
    """Get primary screen size."""
    return ScreenUtils.get_screen_size()


def is_point_on_screen(x: int, y: int) -> bool:
    """Check if point is on screen."""
    return ScreenUtils.is_point_on_screen(x, y)


def clamp_to_screen(x: int, y: int) -> Tuple[int, int]:
    """Clamp coordinates to screen boundaries."""
    return ScreenUtils.clamp_to_screen(x, y)


def distance_between_points(x1: int, y1: int, x2: int, y2: int) -> float:
    """Calculate Euclidean distance between two points."""
    return ScreenUtils.distance_between_points(x1, y1, x2, y2)
