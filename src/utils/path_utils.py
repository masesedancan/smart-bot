"""
Path utility functions for file and directory management.
"""

from pathlib import Path
from datetime import datetime
from typing import Optional


class PathUtils:
    """Utility functions for path management."""
    
    @staticmethod
    def get_project_root() -> Path:
        """
        Get the project root directory.
        
        Returns:
            Path to project root
        """
        # Assumes this file is in src/utils/
        return Path(__file__).parent.parent.parent
    
    @staticmethod
    def get_logs_dir() -> Path:
        """Get the logs directory, creating it if necessary."""
        logs_dir = PathUtils.get_project_root() / "logs"
        logs_dir.mkdir(exist_ok=True)
        return logs_dir
    
    @staticmethod
    def get_data_dir() -> Path:
        """Get the data directory, creating it if necessary."""
        data_dir = PathUtils.get_project_root() / "data"
        data_dir.mkdir(exist_ok=True)
        return data_dir
    
    @staticmethod
    def get_calibration_dir() -> Path:
        """Get the calibration data directory."""
        calib_dir = PathUtils.get_data_dir() / "calibration" / "profiles"
        calib_dir.mkdir(parents=True, exist_ok=True)
        return calib_dir
    
    @staticmethod
    def get_screenshots_dir() -> Path:
        """Get the screenshots directory."""
        screenshots_dir = PathUtils.get_data_dir() / "screenshots"
        screenshots_dir.mkdir(exist_ok=True)
        return screenshots_dir
    
    @staticmethod
    def get_sessions_dir() -> Path:
        """Get the sessions directory."""
        sessions_dir = PathUtils.get_data_dir() / "sessions"
        sessions_dir.mkdir(exist_ok=True)
        return sessions_dir
    
    @staticmethod
    def get_log_file_path(date: Optional[datetime] = None) -> Path:
        """
        Get the log file path for a specific date.
        
        Args:
            date: Date for log file (default: today)
            
        Returns:
            Path to log file
        """
        if date is None:
            date = datetime.now()
        
        filename = f"bot_{date.strftime('%Y%m%d')}.log"
        return PathUtils.get_logs_dir() / filename
    
    @staticmethod
    def get_stats_file_path() -> Path:
        """
        Get the statistics JSON file path.
        
        Returns:
            Path to stats.json
        """
        return PathUtils.get_logs_dir() / "stats.json"
    
    @staticmethod
    def get_session_file_path(session_id: Optional[str] = None) -> Path:
        """
        Get the session state file path.
        
        Args:
            session_id: Session identifier (default: timestamp)
            
        Returns:
            Path to session JSON file
        """
        if session_id is None:
            session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        filename = f"session_{session_id}.json"
        return PathUtils.get_sessions_dir() / filename


# Convenience functions
def get_project_root() -> Path:
    """Get project root directory."""
    return PathUtils.get_project_root()


def get_logs_dir() -> Path:
    """Get logs directory."""
    return PathUtils.get_logs_dir()


def get_data_dir() -> Path:
    """Get data directory."""
    return PathUtils.get_data_dir()


def get_calibration_dir() -> Path:
    """Get calibration directory."""
    return PathUtils.get_calibration_dir()


def get_screenshots_dir() -> Path:
    """Get screenshots directory."""
    return PathUtils.get_screenshots_dir()


def get_sessions_dir() -> Path:
    """Get sessions directory."""
    return PathUtils.get_sessions_dir()


def get_log_file_path(date: Optional[datetime] = None) -> Path:
    """Get log file path."""
    return PathUtils.get_log_file_path(date)


def get_stats_file_path() -> Path:
    """Get statistics file path."""
    return PathUtils.get_stats_file_path()


def get_session_file_path(session_id: Optional[str] = None) -> Path:
    """Get session file path."""
    return PathUtils.get_session_file_path(session_id)
