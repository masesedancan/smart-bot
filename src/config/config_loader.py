"""
Configuration loader - loads and merges YAML config and .env files.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

from src.config.defaults import DEFAULT_CONFIG
from src.config.validator import validate_config


class ConfigLoader:
    """Loads and validates configuration from YAML and .env files."""
    
    @staticmethod
    def load(config_path: str = "config.yaml",
             dry_run: bool = False,
             visual_debug: bool = False,
             single_cycle: bool = False,
             no_bio_breaks: bool = False) -> Dict[str, Any]:
        """
        Load configuration from YAML file and environment variables.
        
        Args:
            config_path: Path to YAML config file
            dry_run: Enable dry-run mode
            visual_debug: Enable visual debugging
            single_cycle: Run single cycle only
            no_bio_breaks: Disable bio-breaks
            
        Returns:
            Merged configuration dictionary
            
        Raises:
            FileNotFoundError: If config file not found
            ValueError: If configuration is invalid
        """
        # Load .env file
        env_path = Path.cwd() / ".env"
        if env_path.exists():
            load_dotenv(env_path)
        
        # Start with defaults
        config = ConfigLoader._deep_copy(DEFAULT_CONFIG)
        
        # Load YAML config
        yaml_config = ConfigLoader._load_yaml(config_path)
        if yaml_config:
            config = ConfigLoader._deep_merge(config, yaml_config)
        
        # Apply command-line overrides
        if dry_run:
            config['debug']['dry_run_mode'] = True
        if visual_debug:
            config['debug']['visual_overlay'] = True
        if single_cycle:
            config['debug']['single_cycle_only'] = True
        if no_bio_breaks:
            config['behavior']['bio_break_probability'] = 0.0
        
        # Load environment variables into config
        config['env'] = ConfigLoader._load_env_vars()
        
        # Validate configuration
        errors = validate_config(config)
        if errors:
            error_msg = "Configuration validation failed:\n" + "\n".join(f"  - {e}" for e in errors)
            raise ValueError(error_msg)
        
        return config
    
    @staticmethod
    def _load_yaml(path: str) -> Optional[Dict[str, Any]]:
        """
        Load YAML configuration file.
        
        Args:
            path: Path to YAML file
            
        Returns:
            Parsed YAML dictionary or None if file not found
        """
        yaml_path = Path(path)
        if not yaml_path.exists():
            # Use defaults if config file doesn't exist
            return None
        
        with open(yaml_path, 'r') as f:
            return yaml.safe_load(f)
    
    @staticmethod
    def _load_env_vars() -> Dict[str, Any]:
        """
        Load relevant environment variables.
        
        Returns:
            Dictionary of environment variables
        """
        return {
            'recorder_app_title': os.getenv('RECORDER_APP_TITLE', ''),
            'browser_window_title': os.getenv('BROWSER_WINDOW_TITLE', ''),
            'start_button_x': int(os.getenv('START_BUTTON_X', 0)),
            'start_button_y': int(os.getenv('START_BUTTON_Y', 0)),
            'stop_button_x': int(os.getenv('STOP_BUTTON_X', 0)),
            'stop_button_y': int(os.getenv('STOP_BUTTON_Y', 0)),
            'minimize_button_x': int(os.getenv('MINIMIZE_BUTTON_X', 0)),
            'minimize_button_y': int(os.getenv('MINIMIZE_BUTTON_Y', 0)),
            'screen_width': int(os.getenv('SCREEN_WIDTH', 1920)),
            'screen_height': int(os.getenv('SCREEN_HEIGHT', 1080)),
            'dpi_scale': float(os.getenv('DPI_SCALE', 1.0)),
        }
    
    @staticmethod
    def _deep_copy(d: Dict[str, Any]) -> Dict[str, Any]:
        """Create a deep copy of a dictionary."""
        import copy
        return copy.deepcopy(d)
    
    @staticmethod
    def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deep merge two dictionaries, with override taking precedence.
        
        Args:
            base: Base dictionary
            override: Override dictionary
            
        Returns:
            Merged dictionary
        """
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = ConfigLoader._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result


def load_config(**kwargs) -> Dict[str, Any]:
    """
    Convenience function to load configuration.
    
    Args:
        **kwargs: Arguments passed to ConfigLoader.load()
        
    Returns:
        Configuration dictionary
    """
    return ConfigLoader.load(**kwargs)
