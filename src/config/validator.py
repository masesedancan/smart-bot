"""
Configuration validation module.
"""

from typing import Dict, Any, List
from src.utils.validation_utils import (
    validate_probability,
    validate_timing_config,
    validate_behavior_config
)


class ConfigValidator:
    """Validates configuration dictionaries."""
    
    @staticmethod
    def validate(config: Dict[str, Any]) -> List[str]:
        """
        Validate entire configuration.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            List of error messages (empty if valid)
        """
        errors = []
        
        # Validate required sections exist
        required_sections = ['timing', 'behavior', 'cursor', 'safety', 'logging']
        for section in required_sections:
            if section not in config:
                errors.append(f"Missing configuration section: {section}")
        
        # Validate timing section
        if 'timing' in config:
            errors.extend(validate_timing_config(config['timing']))
        
        # Validate behavior section
        if 'behavior' in config:
            errors.extend(validate_behavior_config(config['behavior']))
        
        # Validate cursor section
        if 'cursor' in config:
            errors.extend(ConfigValidator._validate_cursor(config['cursor']))
        
        # Validate safety section
        if 'safety' in config:
            errors.extend(ConfigValidator._validate_safety(config['safety']))
        
        # Validate fatigue section (optional)
        if 'fatigue' in config:
            errors.extend(ConfigValidator._validate_fatigue(config['fatigue']))
        
        return errors
    
    @staticmethod
    def _validate_cursor(cursor: Dict[str, Any]) -> List[str]:
        """Validate cursor configuration."""
        errors = []
        
        if 'speed_multiplier' in cursor:
            speed = cursor['speed_multiplier']
            if not isinstance(speed, (int, float)) or speed <= 0 or speed > 5:
                errors.append(f"Invalid speed_multiplier: {speed} (must be 0-5)")
        
        if 'bezier_control_points' in cursor:
            points = cursor['bezier_control_points']
            if not isinstance(points, int) or points < 2 or points > 5:
                errors.append(f"Invalid bezier_control_points: {points} (must be 2-5)")
        
        if 'movement_fps' in cursor:
            fps = cursor['movement_fps']
            if not isinstance(fps, int) or fps < 30 or fps > 120:
                errors.append(f"Invalid movement_fps: {fps} (must be 30-120)")
        
        if 'jitter_amplitude' in cursor:
            amp = cursor['jitter_amplitude']
            if not isinstance(amp, (int, float)) or amp < 0 or amp > 10:
                errors.append(f"Invalid jitter_amplitude: {amp} (must be 0-10)")
        
        if 'jitter_frequency' in cursor:
            freq = cursor['jitter_frequency']
            if not validate_probability(freq):
                errors.append(f"Invalid jitter_frequency: {freq} (must be 0-1)")
        
        return errors
    
    @staticmethod
    def _validate_safety(safety: Dict[str, Any]) -> List[str]:
        """Validate safety configuration."""
        errors = []
        
        if 'max_runtime_hours' in safety:
            hours = safety['max_runtime_hours']
            if not isinstance(hours, (int, float)) or hours <= 0 or hours > 24:
                errors.append(f"Invalid max_runtime_hours: {hours} (must be 0-24)")
        
        if 'cpu_threshold_percent' in safety:
            cpu = safety['cpu_threshold_percent']
            if not isinstance(cpu, (int, float)) or cpu < 50 or cpu > 100:
                errors.append(f"Invalid cpu_threshold_percent: {cpu} (must be 50-100)")
        
        if 'memory_threshold_percent' in safety:
            mem = safety['memory_threshold_percent']
            if not isinstance(mem, (int, float)) or mem < 50 or mem > 100:
                errors.append(f"Invalid memory_threshold_percent: {mem} (must be 50-100)")
        
        if 'max_retry_attempts' in safety:
            retries = safety['max_retry_attempts']
            if not isinstance(retries, int) or retries < 1 or retries > 10:
                errors.append(f"Invalid max_retry_attempts: {retries} (must be 1-10)")
        
        return errors
    
    @staticmethod
    def _validate_fatigue(fatigue: Dict[str, Any]) -> List[str]:
        """Validate fatigue configuration."""
        errors = []
        
        if 'start_after_minutes' in fatigue:
            minutes = fatigue['start_after_minutes']
            if not isinstance(minutes, (int, float)) or minutes < 0:
                errors.append(f"Invalid start_after_minutes: {minutes} (must be >= 0)")
        
        if 'max_performance_degradation' in fatigue:
            deg = fatigue['max_performance_degradation']
            if not isinstance(deg, (int, float)) or deg < 0 or deg > 1:
                errors.append(f"Invalid max_performance_degradation: {deg} (must be 0-1)")
        
        return errors


def validate_config(config: Dict[str, Any]) -> List[str]:
    """
    Validate configuration dictionary.
    
    Args:
        config: Configuration to validate
        
    Returns:
        List of error messages (empty if valid)
    """
    return ConfigValidator.validate(config)
