"""
Default configuration values.

These are used as fallbacks when values are not specified in config files.
"""

DEFAULT_CONFIG = {
    "timing": {
        "watch_duration_mean": 120.0,
        "watch_duration_std": 8.0,
        "cooldown_mean": 3.0,
        "cooldown_std": 1.0,
        "click_duration_mean": 0.1,
        "click_duration_std": 0.03,
        "hover_duration_mean": 0.4,
        "hover_duration_std": 0.15,
        "post_click_pause_mean": 0.2,
        "post_click_pause_std": 0.1,
        "window_switch_delay_mean": 1.5,
        "window_switch_delay_std": 0.4,
    },
    "behavior": {
        "overshoot_probability": 0.20,
        "overshoot_distance_min": 3,
        "overshoot_distance_max": 8,
        "overshoot_correction_speed": 0.6,
        "micro_distraction_probability": 0.25,
        "micro_distraction_interval": 30,
        "bio_break_after_cycles_min": 6,
        "bio_break_after_cycles_max": 9,
        "bio_break_duration_min": 240,
        "bio_break_duration_max": 720,
        "bio_break_probability": 0.75,
        "micro_actions": {
            "idle_scroll": 0.35,
            "cursor_drift": 0.25,
            "tab_focus_shift": 0.15,
            "micro_pause": 0.15,
            "hand_readjust": 0.10,
        },
    },
    "cursor": {
        "speed_multiplier": 1.0,
        "bezier_control_points": 3,
        "movement_fps": 60,
        "jitter_amplitude": 1.5,
        "jitter_frequency": 0.1,
        "ease_in_duration": 0.2,
        "ease_out_duration": 0.3,
    },
    "fatigue": {
        "enabled": True,
        "start_after_minutes": 30,
        "max_performance_degradation": 0.15,
        "gradual_onset": True,
        "affects_overshoot": True,
        "affects_timing": True,
    },
    "safety": {
        "max_runtime_hours": 4,
        "cpu_threshold_percent": 90,
        "memory_threshold_percent": 90,
        "auto_stop_on_threshold": True,
        "keyboard_killswitch": "ctrl+shift+q",
        "mouse_corner_killswitch": True,
        "max_retry_attempts": 3,
        "retry_backoff_base": 2,
    },
    "logging": {
        "level": "INFO",
        "console_output": True,
        "file_output": True,
        "rotate_daily": True,
        "keep_logs_days": 7,
        "log_cursor_positions": False,
        "log_timing_values": False,
    },
    "visual_recognition": {
        "enabled": False,
        "confidence_threshold": 0.8,
        "use_ocr_fallback": False,
    },
    "debug": {
        "dry_run_mode": False,
        "visual_overlay": False,
        "slow_motion": False,
        "single_cycle_only": False,
    },
}


def get_default_value(key_path: str, default=None):
    """
    Get a default configuration value by dot-notation key path.
    
    Args:
        key_path: Dot-separated key path (e.g., "timing.watch_duration_mean")
        default: Default value if key not found
        
    Returns:
        Configuration value or default
    """
    keys = key_path.split('.')
    value = DEFAULT_CONFIG
    
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return default
    
    return value
