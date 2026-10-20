"""
Error recovery and retry logic with exponential backoff.
"""

import logging
import time
import functools
from typing import Callable, Optional, Tuple, Any

logger = logging.getLogger(__name__)


class RetryConfig:
    """Configuration for retry behavior."""
    
    def __init__(self, max_attempts: int = 3, backoff_base: float = 2.0):
        """
        Initialize retry configuration.
        
        Args:
            max_attempts: Maximum number of retry attempts
            backoff_base: Base for exponential backoff (seconds)
        """
        self.max_attempts = max_attempts
        self.backoff_base = backoff_base


class ErrorRecovery:
    """Handles error recovery and retry logic."""
    
    def __init__(self, config: RetryConfig):
        """
        Initialize error recovery.
        
        Args:
            config: Retry configuration
        """
        self.config = config
        self.error_count = 0
        self.consecutive_errors = 0
    
    def retry_with_backoff(self, func: Callable, *args, **kwargs) -> Tuple[bool, Optional[Any]]:
        """
        Execute a function with retry and exponential backoff.
        
        Args:
            func: Function to execute
            *args: Positional arguments for function
            **kwargs: Keyword arguments for function
            
        Returns:
            Tuple of (success, result)
            - success: True if function succeeded
            - result: Function return value or None
        """
        for attempt in range(1, self.config.max_attempts + 1):
            try:
                logger.debug(f"Attempt {attempt}/{self.config.max_attempts}")
                
                result = func(*args, **kwargs)
                
                # Success!
                self.consecutive_errors = 0
                return (True, result)
                
            except Exception as e:
                self.error_count += 1
                self.consecutive_errors += 1
                
                logger.warning(f"Attempt {attempt} failed: {e}")
                
                # Check if we should retry
                if attempt < self.config.max_attempts:
                    # Calculate backoff delay
                    delay = self.config.backoff_base ** attempt
                    logger.info(f"Retrying in {delay:.1f} seconds...")
                    time.sleep(delay)
                else:
                    logger.error(f"All {self.config.max_attempts} attempts failed")
                    return (False, None)
        
        return (False, None)
    
    def get_error_stats(self) -> dict:
        """
        Get error statistics.
        
        Returns:
            Dictionary with error counts
        """
        return {
            'total_errors': self.error_count,
            'consecutive_errors': self.consecutive_errors
        }
    
    def reset_consecutive_errors(self):
        """Reset consecutive error counter."""
        self.consecutive_errors = 0


def retry_on_failure(max_attempts: int = 3, backoff_base: float = 2.0, 
                    exceptions: tuple = (Exception,)):
    """
    Decorator for automatic retry with exponential backoff.
    
    Args:
        max_attempts: Maximum number of attempts
        backoff_base: Base for exponential backoff
        exceptions: Tuple of exceptions to catch and retry
        
    Returns:
        Decorated function
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                    
                except exceptions as e:
                    if attempt < max_attempts:
                        delay = backoff_base ** attempt
                        logger.warning(
                            f"{func.__name__} attempt {attempt} failed: {e}. "
                            f"Retrying in {delay:.1f}s..."
                        )
                        time.sleep(delay)
                    else:
                        logger.error(
                            f"{func.__name__} failed after {max_attempts} attempts"
                        )
                        raise
            
            return None
        
        return wrapper
    return decorator


def create_error_recovery(safety_config: dict) -> ErrorRecovery:
    """
    Create an error recovery instance from configuration.
    
    Args:
        safety_config: Safety configuration dictionary
        
    Returns:
        Configured ErrorRecovery instance
    """
    config = RetryConfig(
        max_attempts=safety_config.get('max_retry_attempts', 3),
        backoff_base=safety_config.get('retry_backoff_base', 2.0)
    )
    return ErrorRecovery(config)
