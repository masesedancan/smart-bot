"""
Randomness utility functions for generating human-like variance.
"""

import random
import numpy as np
from typing import Tuple, List


def gaussian_delay(mean: float, std: float, min_val: float = 0.0) -> float:
    """
    Generate a delay using Gaussian (normal) distribution.
    
    Args:
        mean: Mean value (center of distribution)
        std: Standard deviation (spread)
        min_val: Minimum allowed value (default: 0)
        
    Returns:
        Random delay value following normal distribution
    """
    value = np.random.normal(mean, std)
    return max(min_val, value)


def random_in_range(min_val: float, max_val: float) -> float:
    """
    Generate a random float in the given range.
    
    Args:
        min_val: Minimum value (inclusive)
        max_val: Maximum value (inclusive)
        
    Returns:
        Random float between min_val and max_val
    """
    return random.uniform(min_val, max_val)


def random_int_in_range(min_val: int, max_val: int) -> int:
    """
    Generate a random integer in the given range.
    
    Args:
        min_val: Minimum value (inclusive)
        max_val: Maximum value (inclusive)
        
    Returns:
        Random integer between min_val and max_val
    """
    return random.randint(min_val, max_val)


def weighted_choice(choices: List[str], weights: List[float]) -> str:
    """
    Make a weighted random choice from a list.
    
    Args:
        choices: List of choice options
        weights: List of weights (must sum to 1.0)
        
    Returns:
        Randomly selected choice based on weights
    """
    return random.choices(choices, weights=weights, k=1)[0]


def probability_check(probability: float) -> bool:
    """
    Check if a random event occurs based on probability.
    
    Args:
        probability: Probability value (0.0 to 1.0)
        
    Returns:
        True if event occurs, False otherwise
    """
    return random.random() < probability


def perlin_noise_1d(x: float, seed: int = 0) -> float:
    """
    Simple 1D Perlin-like noise function.
    
    Args:
        x: Input value
        seed: Random seed for reproducibility
        
    Returns:
        Noise value between -1 and 1
    """
    # Simplified pseudo-Perlin noise
    random.seed(seed + int(x))
    noise = random.uniform(-1, 1)
    random.seed()  # Reset seed
    return noise


def jitter_value(value: float, amplitude: float) -> float:
    """
    Add random jitter to a value.
    
    Args:
        value: Base value
        amplitude: Maximum jitter amplitude
        
    Returns:
        Value with added jitter
    """
    jitter = random.uniform(-amplitude, amplitude)
    return value + jitter


def smooth_random_walk(start: float, end: float, steps: int, 
                       smoothness: float = 0.5) -> List[float]:
    """
    Generate a smooth random walk from start to end.
    
    Args:
        start: Starting value
        end: Ending value
        steps: Number of steps
        smoothness: Smoothness factor (0 = random, 1 = linear)
        
    Returns:
        List of values forming a smooth path
    """
    if steps <= 1:
        return [end]
    
    values = [start]
    current = start
    
    for i in range(1, steps):
        # Linear progression
        linear_target = start + (end - start) * (i / steps)
        
        # Random component
        random_component = random.uniform(-1, 1) * (1 - smoothness)
        
        # Blend linear and random
        step_size = (linear_target - current) * smoothness + random_component
        current += step_size
        values.append(current)
    
    # Ensure we end at the target
    values[-1] = end
    
    return values


def bezier_control_point(start: Tuple[float, float], 
                         end: Tuple[float, float],
                         variance: float = 0.3) -> Tuple[float, float]:
    """
    Generate a random control point for Bezier curve.
    
    Args:
        start: Starting point (x, y)
        end: Ending point (x, y)
        variance: How far control point can deviate (0-1)
        
    Returns:
        Control point coordinates (x, y)
    """
    # Midpoint
    mid_x = (start[0] + end[0]) / 2
    mid_y = (start[1] + end[1]) / 2
    
    # Distance between points
    distance = ((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2) ** 0.5
    
    # Random offset perpendicular to line
    offset = random.uniform(-variance, variance) * distance
    
    # Perpendicular angle
    angle = np.arctan2(end[1] - start[1], end[0] - start[0])
    perp_angle = angle + np.pi / 2
    
    # Apply offset
    control_x = mid_x + offset * np.cos(perp_angle)
    control_y = mid_y + offset * np.sin(perp_angle)
    
    return (control_x, control_y)


class VarianceTracker:
    """Tracks recent values to ensure variance and prevent repetition."""
    
    def __init__(self, history_size: int = 10):
        """
        Initialize variance tracker.
        
        Args:
            history_size: Number of recent values to track
        """
        self.history: List[float] = []
        self.history_size = history_size
    
    def add(self, value: float):
        """Add a value to history."""
        self.history.append(value)
        if len(self.history) > self.history_size:
            self.history.pop(0)
    
    def is_too_similar(self, value: float, threshold: float = 0.05) -> bool:
        """
        Check if a value is too similar to recent history.
        
        Args:
            value: Value to check
            threshold: Similarity threshold (fraction)
            
        Returns:
            True if value is too similar to recent values
        """
        if not self.history:
            return False
        
        for historical_value in self.history[-3:]:  # Check last 3 values
            if abs(value - historical_value) / max(abs(historical_value), 1) < threshold:
                return True
        
        return False
    
    def generate_unique_value(self, mean: float, std: float, 
                            max_attempts: int = 10) -> float:
        """
        Generate a value that's different from recent history.
        
        Args:
            mean: Mean value
            std: Standard deviation
            max_attempts: Maximum generation attempts
            
        Returns:
            Unique value
        """
        for _ in range(max_attempts):
            value = gaussian_delay(mean, std)
            if not self.is_too_similar(value):
                self.add(value)
                return value
        
        # If all attempts failed, just use the last generated value
        self.add(value)
        return value
