"""
Timing engine for generating human-like delays with stochastic variance.
"""

import time
import logging
from typing import Optional, Callable
from dataclasses import dataclass

from src.behavior.randomness_utils import gaussian_delay, VarianceTracker

logger = logging.getLogger(__name__)


@dataclass
class TimingConfig:
    """Configuration for timing engine."""
    watch_duration_mean: float = 120.0
    watch_duration_std: float = 8.0
    cooldown_mean: float = 3.0
    cooldown_std: float = 1.0
    click_duration_mean: float = 0.1
    click_duration_std: float = 0.03
    hover_duration_mean: float = 0.4
    hover_duration_std: float = 0.15
    post_click_pause_mean: float = 0.2
    post_click_pause_std: float = 0.1
    window_switch_delay_mean: float = 1.5
    window_switch_delay_std: float = 0.4


class TimingEngine:
    """Generates human-like timing delays with variance."""
    
    def __init__(self, config: TimingConfig):
        """
        Initialize timing engine.
        
        Args:
            config: Timing configuration
        """
        self.config = config
        self.watch_variance = VarianceTracker(history_size=10)
        self.cooldown_variance = VarianceTracker(history_size=10)
        self._log_timings = False
    
    def enable_timing_logs(self, enabled: bool = True):
        """Enable or disable timing value logging."""
        self._log_timings = enabled
    
    def get_watch_duration(self) -> float:
        """
        Get a randomized watch duration.
        
        Returns:
            Duration in seconds
        """
        duration = self.watch_variance.generate_unique_value(
            self.config.watch_duration_mean,
            self.config.watch_duration_std
        )
        
        if self._log_timings:
            logger.debug(f"Generated watch duration: {duration:.2f}s")
        
        return duration
    
    def get_cooldown_duration(self) -> float:
        """
        Get a randomized cooldown duration.
        
        Returns:
            Duration in seconds
        """
        duration = self.cooldown_variance.generate_unique_value(
            self.config.cooldown_mean,
            self.config.cooldown_std
        )
        
        if self._log_timings:
            logger.debug(f"Generated cooldown duration: {duration:.2f}s")
        
        return duration
    
    def get_click_duration(self) -> float:
        """
        Get a randomized click duration (mouse button hold time).
        
        Returns:
            Duration in seconds
        """
        duration = gaussian_delay(
            self.config.click_duration_mean,
            self.config.click_duration_std,
            min_val=0.05  # Minimum 50ms
        )
        
        if self._log_timings:
            logger.debug(f"Generated click duration: {duration:.3f}s")
        
        return duration
    
    def get_hover_duration(self) -> float:
        """
        Get a randomized hover duration (pause before click).
        
        Returns:
            Duration in seconds
        """
        duration = gaussian_delay(
            self.config.hover_duration_mean,
            self.config.hover_duration_std,
            min_val=0.1  # Minimum 100ms
        )
        
        if self._log_timings:
            logger.debug(f"Generated hover duration: {duration:.3f}s")
        
        return duration
    
    def get_post_click_pause(self) -> float:
        """
        Get a randomized post-click pause duration.
        
        Returns:
            Duration in seconds
        """
        duration = gaussian_delay(
            self.config.post_click_pause_mean,
            self.config.post_click_pause_std,
            min_val=0.05
        )
        
        if self._log_timings:
            logger.debug(f"Generated post-click pause: {duration:.3f}s")
        
        return duration
    
    def get_window_switch_delay(self) -> float:
        """
        Get a randomized window switch delay.
        
        Returns:
            Duration in seconds
        """
        duration = gaussian_delay(
            self.config.window_switch_delay_mean,
            self.config.window_switch_delay_std,
            min_val=0.5  # Minimum 500ms
        )
        
        if self._log_timings:
            logger.debug(f"Generated window switch delay: {duration:.2f}s")
        
        return duration
    
    def wait(self, duration: float):
        """
        Wait for a specified duration.
        
        Args:
            duration: Duration in seconds
        """
        if duration > 0:
            time.sleep(duration)
    
    def chunked_wait(self, duration: float, check_interval: float = 1.0,
                    check_callback: Optional[Callable[[], bool]] = None):
        """
        Wait for a duration in chunks, optionally checking a condition.
        
        This allows interrupting long waits and performing periodic checks.
        
        Args:
            duration: Total duration in seconds
            check_interval: Interval between checks in seconds
            check_callback: Optional callback that returns True to continue, False to abort
        """
        elapsed = 0.0
        
        while elapsed < duration:
            # Calculate sleep time for this chunk
            remaining = duration - elapsed
            sleep_time = min(check_interval, remaining)
            
            # Sleep
            time.sleep(sleep_time)
            elapsed += sleep_time
            
            # Check callback if provided
            if check_callback and not check_callback():
                logger.debug(f"Chunked wait aborted after {elapsed:.1f}s")
                return
    
    def wait_with_variance(self, base_duration: float, variance: float = 0.1):
        """
        Wait for a duration with added variance.
        
        Args:
            base_duration: Base duration in seconds
            variance: Variance as fraction of base (default: 10%)
        """
        std = base_duration * variance
        duration = gaussian_delay(base_duration, std, min_val=0)
        self.wait(duration)


def create_timing_engine(timing_config: dict) -> TimingEngine:
    """
    Create a timing engine from configuration dictionary.
    
    Args:
        timing_config: Timing configuration dictionary
        
    Returns:
        Configured TimingEngine instance
    """
    config = TimingConfig(
        watch_duration_mean=timing_config.get('watch_duration_mean', 120.0),
        watch_duration_std=timing_config.get('watch_duration_std', 8.0),
        cooldown_mean=timing_config.get('cooldown_mean', 3.0),
        cooldown_std=timing_config.get('cooldown_std', 1.0),
        click_duration_mean=timing_config.get('click_duration_mean', 0.1),
        click_duration_std=timing_config.get('click_duration_std', 0.03),
        hover_duration_mean=timing_config.get('hover_duration_mean', 0.4),
        hover_duration_std=timing_config.get('hover_duration_std', 0.15),
        post_click_pause_mean=timing_config.get('post_click_pause_mean', 0.2),
        post_click_pause_std=timing_config.get('post_click_pause_std', 0.1),
        window_switch_delay_mean=timing_config.get('window_switch_delay_mean', 1.5),
        window_switch_delay_std=timing_config.get('window_switch_delay_std', 0.4),
    )
    
    return TimingEngine(config)
