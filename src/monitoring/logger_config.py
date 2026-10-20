"""
Logging configuration and setup.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

try:
    import colorlog
    COLORLOG_AVAILABLE = True
except ImportError:
    COLORLOG_AVAILABLE = False

from src.utils.path_utils import get_log_file_path


def setup_logging(level: str = "INFO",
                 console_output: bool = True,
                 file_output: bool = True,
                 log_file_path: Optional[Path] = None) -> logging.Logger:
    """
    Set up logging configuration.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        console_output: Enable console output
        file_output: Enable file output
        log_file_path: Custom log file path (default: auto-generated)
        
    Returns:
        Configured logger instance
    """
    # Get root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        fmt='%(asctime)s [%(levelname)8s] %(name)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler with color (if available)
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, level.upper()))
        
        if COLORLOG_AVAILABLE:
            color_formatter = colorlog.ColoredFormatter(
                fmt='%(log_color)s%(asctime)s [%(levelname)8s]%(reset)s %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S',
                log_colors={
                    'DEBUG': 'cyan',
                    'INFO': 'green',
                    'WARNING': 'yellow',
                    'ERROR': 'red',
                    'CRITICAL': 'red,bg_white',
                }
            )
            console_handler.setFormatter(color_formatter)
        else:
            console_handler.setFormatter(detailed_formatter)
        
        logger.addHandler(console_handler)
    
    # File handler
    if file_output:
        if log_file_path is None:
            log_file_path = get_log_file_path()
        
        # Ensure log directory exists
        log_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file_path, mode='a', encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)  # Always log DEBUG to file
        file_handler.setFormatter(detailed_formatter)
        
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


class LogContext:
    """Context manager for temporary log level changes."""
    
    def __init__(self, logger: logging.Logger, level: str):
        """
        Initialize log context.
        
        Args:
            logger: Logger instance
            level: Temporary log level
        """
        self.logger = logger
        self.new_level = getattr(logging, level.upper())
        self.old_level = logger.level
    
    def __enter__(self):
        """Enter context - set new log level."""
        self.logger.setLevel(self.new_level)
        return self.logger
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context - restore old log level."""
        self.logger.setLevel(self.old_level)


def log_section_header(logger: logging.Logger, title: str, char: str = "="):
    """
    Log a section header.
    
    Args:
        logger: Logger instance
        title: Section title
        char: Character to use for decoration
    """
    width = 60
    logger.info(char * width)
    logger.info(title.center(width))
    logger.info(char * width)


def log_key_value(logger: logging.Logger, key: str, value: str, indent: int = 2):
    """
    Log a key-value pair in a formatted way.
    
    Args:
        logger: Logger instance
        key: Key name
        value: Value
        indent: Indentation spaces
    """
    indent_str = " " * indent
    logger.info(f"{indent_str}{key}: {value}")
