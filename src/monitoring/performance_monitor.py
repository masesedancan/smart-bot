"""
System performance monitoring for CPU and memory usage.
"""

import psutil
import logging
from typing import Tuple, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ResourceUsage:
    """System resource usage snapshot."""
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_available_mb: float


class PerformanceMonitor:
    """Monitors system resource usage."""
    
    def __init__(self, cpu_threshold: float = 90.0, memory_threshold: float = 90.0):
        """
        Initialize performance monitor.
        
        Args:
            cpu_threshold: CPU usage threshold percentage
            memory_threshold: Memory usage threshold percentage
        """
        self.cpu_threshold = cpu_threshold
        self.memory_threshold = memory_threshold
        self._last_check: Optional[ResourceUsage] = None
    
    def get_resource_usage(self) -> ResourceUsage:
        """
        Get current system resource usage.
        
        Returns:
            ResourceUsage object with current metrics
        """
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        
        usage = ResourceUsage(
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            memory_used_mb=memory.used / (1024 * 1024),
            memory_available_mb=memory.available / (1024 * 1024)
        )
        
        self._last_check = usage
        return usage
    
    def check_thresholds(self) -> Tuple[bool, Optional[str]]:
        """
        Check if resource usage exceeds thresholds.
        
        Returns:
            Tuple of (exceeded, reason)
            - exceeded: True if any threshold exceeded
            - reason: Description of which threshold was exceeded
        """
        usage = self.get_resource_usage()
        
        if usage.cpu_percent >= self.cpu_threshold:
            reason = f"CPU usage ({usage.cpu_percent:.1f}%) exceeds threshold ({self.cpu_threshold}%)"
            logger.warning(reason)
            return (True, reason)
        
        if usage.memory_percent >= self.memory_threshold:
            reason = f"Memory usage ({usage.memory_percent:.1f}%) exceeds threshold ({self.memory_threshold}%)"
            logger.warning(reason)
            return (True, reason)
        
        return (False, None)
    
    def is_safe_to_continue(self) -> bool:
        """
        Check if system resources are within safe operating limits.
        
        Returns:
            True if safe to continue, False otherwise
        """
        exceeded, _ = self.check_thresholds()
        return not exceeded
    
    def get_usage_summary(self) -> str:
        """
        Get a formatted summary of resource usage.
        
        Returns:
            Human-readable resource usage summary
        """
        usage = self._last_check or self.get_resource_usage()
        
        return (
            f"CPU: {usage.cpu_percent:.1f}% | "
            f"Memory: {usage.memory_percent:.1f}% "
            f"({usage.memory_used_mb:.0f}MB used, {usage.memory_available_mb:.0f}MB available)"
        )
    
    def log_resource_usage(self, level: str = "DEBUG"):
        """
        Log current resource usage.
        
        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR)
        """
        summary = self.get_usage_summary()
        log_method = getattr(logger, level.lower())
        log_method(f"Resource usage: {summary}")


def check_system_resources(cpu_threshold: float = 90.0, 
                          memory_threshold: float = 90.0) -> Tuple[bool, Optional[str]]:
    """
    Quick check of system resource usage.
    
    Args:
        cpu_threshold: CPU usage threshold percentage
        memory_threshold: Memory usage threshold percentage
        
    Returns:
        Tuple of (safe, reason)
        - safe: True if resources are within limits
        - reason: Description if threshold exceeded
    """
    monitor = PerformanceMonitor(cpu_threshold, memory_threshold)
    exceeded, reason = monitor.check_thresholds()
    return (not exceeded, reason)
