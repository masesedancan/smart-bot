"""
Resource guard for monitoring and limiting system resource usage.
"""

import logging
from src.monitoring.performance_monitor import PerformanceMonitor

logger = logging.getLogger(__name__)


class ResourceGuard:
    """Guards against excessive resource usage."""
    
    def __init__(self, safety_config: dict):
        """
        Initialize resource guard.
        
        Args:
            safety_config: Safety configuration dictionary
        """
        self.config = safety_config
        self.monitor = PerformanceMonitor(
            cpu_threshold=safety_config.get('cpu_threshold_percent', 90),
            memory_threshold=safety_config.get('memory_threshold_percent', 90)
        )
        self.auto_stop = safety_config.get('auto_stop_on_threshold', True)
        self.threshold_violations = 0
    
    def check_resources(self) -> tuple[bool, str]:
        """
        Check if it's safe to continue based on resource usage.
        
        Returns:
            Tuple of (safe, message)
            - safe: True if resources are within limits
            - message: Description of status
        """
        exceeded, reason = self.monitor.check_thresholds()
        
        if exceeded:
            self.threshold_violations += 1
            logger.warning(f"Resource threshold exceeded ({self.threshold_violations} times): {reason}")
            
            if self.auto_stop:
                return (False, f"Auto-stop triggered: {reason}")
            else:
                return (False, f"Resource warning: {reason}")
        
        # Reset violation counter on success
        if self.threshold_violations > 0:
            logger.info("Resource usage back to normal")
            self.threshold_violations = 0
        
        return (True, "Resources OK")
    
    def get_usage_summary(self) -> str:
        """Get current resource usage summary."""
        return self.monitor.get_usage_summary()
    
    def log_usage(self):
        """Log current resource usage."""
        self.monitor.log_resource_usage()


def create_resource_guard(safety_config: dict) -> ResourceGuard:
    """
    Create a resource guard instance.
    
    Args:
        safety_config: Safety configuration dictionary
        
    Returns:
        Configured ResourceGuard instance
    """
    return ResourceGuard(safety_config)
