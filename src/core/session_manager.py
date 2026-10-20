"""
Session manager for tracking cycles and scheduling bio-breaks.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

from src.behavior.randomness_utils import random_int_in_range, probability_check, gaussian_delay

logger = logging.getLogger(__name__)


class SessionManager:
    """Manages session state, cycle tracking, and bio-breaks."""
    
    def __init__(self, behavior_config: dict):
        """
        Initialize session manager.
        
        Args:
            behavior_config: Behavior configuration dictionary
        """
        self.config = behavior_config
        self.session_start = datetime.now()
        self.cycles_completed = 0
        self.bio_breaks_taken = 0
        self.last_bio_break: Optional[datetime] = None
        
        # Bio-break configuration
        self.bio_break_min_cycles = behavior_config.get('bio_break_after_cycles_min', 6)
        self.bio_break_max_cycles = behavior_config.get('bio_break_after_cycles_max', 9)
        self.bio_break_duration_min = behavior_config.get('bio_break_duration_min', 240)
        self.bio_break_duration_max = behavior_config.get('bio_break_duration_max', 720)
        self.bio_break_probability = behavior_config.get('bio_break_probability', 0.75)
        
        # Next bio-break threshold
        self.next_bio_break_at = random_int_in_range(
            self.bio_break_min_cycles,
            self.bio_break_max_cycles
        )
        
        logger.info(f"Bio-break scheduled after {self.next_bio_break_at} cycles")
    
    def increment_cycle(self):
        """Increment the cycle counter."""
        self.cycles_completed += 1
        logger.info(f"Cycle {self.cycles_completed} completed")
    
    def should_take_bio_break(self) -> bool:
        """
        Determine if a bio-break should be taken.
        
        Returns:
            True if bio-break should occur
        """
        # Check if we've reached the threshold
        if self.cycles_completed < self.next_bio_break_at:
            return False
        
        # Probability check
        should_break = probability_check(self.bio_break_probability)
        
        if should_break:
            logger.info(f"Bio-break triggered after {self.cycles_completed} cycles")
        
        return should_break
    
    def get_bio_break_duration(self) -> float:
        """
        Get a randomized bio-break duration.
        
        Returns:
            Duration in seconds
        """
        # Calculate mean and std
        mean = (self.bio_break_duration_min + self.bio_break_duration_max) / 2
        std = (self.bio_break_duration_max - self.bio_break_duration_min) / 6
        
        duration = gaussian_delay(mean, std, min_val=self.bio_break_duration_min)
        duration = min(duration, self.bio_break_duration_max)
        
        logger.info(f"Bio-break duration: {duration / 60:.1f} minutes")
        return duration
    
    def record_bio_break(self):
        """Record that a bio-break was taken."""
        self.bio_breaks_taken += 1
        self.last_bio_break = datetime.now()
        
        # Schedule next bio-break
        self.next_bio_break_at = self.cycles_completed + random_int_in_range(
            self.bio_break_min_cycles,
            self.bio_break_max_cycles
        )
        
        logger.info(f"Bio-break #{self.bio_breaks_taken} completed. "
                   f"Next break after {self.next_bio_break_at - self.cycles_completed} more cycles")
    
    def get_session_duration(self) -> float:
        """
        Get total session duration.
        
        Returns:
            Duration in seconds
        """
        return (datetime.now() - self.session_start).total_seconds()
    
    def should_stop_session(self, max_runtime_hours: float) -> bool:
        """
        Check if session should stop due to runtime limit.
        
        Args:
            max_runtime_hours: Maximum runtime in hours
            
        Returns:
            True if session should stop
        """
        duration_hours = self.get_session_duration() / 3600
        
        if duration_hours >= max_runtime_hours:
            logger.warning(f"Maximum runtime ({max_runtime_hours}h) reached")
            return True
        
        return False
    
    def get_summary(self) -> dict:
        """
        Get session summary.
        
        Returns:
            Dictionary with session statistics
        """
        return {
            'session_duration': self.get_session_duration(),
            'cycles_completed': self.cycles_completed,
            'bio_breaks_taken': self.bio_breaks_taken,
            'next_bio_break_at': self.next_bio_break_at,
            'cycles_until_break': max(0, self.next_bio_break_at - self.cycles_completed)
        }


def create_session_manager(behavior_config: dict) -> SessionManager:
    """
    Create a session manager instance.
    
    Args:
        behavior_config: Behavior configuration dictionary
        
    Returns:
        Configured SessionManager instance
    """
    return SessionManager(behavior_config)
