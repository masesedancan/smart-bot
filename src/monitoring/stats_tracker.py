"""
Statistics tracking and metrics collection.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict

from src.utils.path_utils import get_stats_file_path


@dataclass
class CycleStats:
    """Statistics for a single cycle."""
    cycle_number: int
    start_time: str
    end_time: str
    duration: float
    watch_duration: float
    success: bool
    error_message: Optional[str] = None
    cursor_distance: float = 0.0
    clicks_performed: int = 0


@dataclass
class SessionStats:
    """Statistics for entire session."""
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    start_time: str = field(default_factory=lambda: datetime.now().isoformat())
    end_time: Optional[str] = None
    cycles_completed: int = 0
    cycles_failed: int = 0
    total_watch_time: float = 0.0
    bio_breaks_taken: int = 0
    average_cycle_duration: float = 0.0
    cursor_movement_stats: Dict[str, float] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    cycles: List[Dict[str, Any]] = field(default_factory=list)


class StatsTracker:
    """Tracks and persists session statistics."""
    
    def __init__(self):
        """Initialize statistics tracker."""
        self.session_stats = SessionStats()
        self.current_cycle_start: Optional[datetime] = None
        self.current_cycle_number: int = 0
        self.total_cursor_distance: float = 0.0
        self.total_clicks: int = 0
    
    def start_cycle(self):
        """Mark the start of a new cycle."""
        self.current_cycle_number += 1
        self.current_cycle_start = datetime.now()
    
    def end_cycle(self, success: bool, watch_duration: float, 
                  error_message: Optional[str] = None):
        """
        Mark the end of a cycle and record statistics.
        
        Args:
            success: Whether cycle completed successfully
            watch_duration: Duration of watch phase in seconds
            error_message: Error message if failed
        """
        if self.current_cycle_start is None:
            return
        
        end_time = datetime.now()
        duration = (end_time - self.current_cycle_start).total_seconds()
        
        cycle_stats = CycleStats(
            cycle_number=self.current_cycle_number,
            start_time=self.current_cycle_start.isoformat(),
            end_time=end_time.isoformat(),
            duration=duration,
            watch_duration=watch_duration,
            success=success,
            error_message=error_message,
            cursor_distance=0.0,  # Will be updated by cursor controller
            clicks_performed=0
        )
        
        # Update session stats
        if success:
            self.session_stats.cycles_completed += 1
            self.session_stats.total_watch_time += watch_duration
        else:
            self.session_stats.cycles_failed += 1
            if error_message:
                self.session_stats.errors.append(
                    f"Cycle {self.current_cycle_number}: {error_message}"
                )
        
        # Add cycle to history
        self.session_stats.cycles.append(asdict(cycle_stats))
        
        # Update averages
        total_cycles = self.session_stats.cycles_completed + self.session_stats.cycles_failed
        if total_cycles > 0:
            total_duration = sum(c['duration'] for c in self.session_stats.cycles)
            self.session_stats.average_cycle_duration = total_duration / total_cycles
        
        self.current_cycle_start = None
    
    def record_bio_break(self):
        """Record that a bio-break was taken."""
        self.session_stats.bio_breaks_taken += 1
    
    def record_cursor_movement(self, distance: float):
        """
        Record cursor movement distance.
        
        Args:
            distance: Distance moved in pixels
        """
        self.total_cursor_distance += distance
        
        # Update cursor movement stats
        self.session_stats.cursor_movement_stats['total_distance_pixels'] = \
            self.total_cursor_distance
        
        if self.session_stats.cycles_completed > 0:
            self.session_stats.cursor_movement_stats['average_distance_per_cycle'] = \
                self.total_cursor_distance / self.session_stats.cycles_completed
    
    def record_click(self):
        """Record that a click was performed."""
        self.total_clicks += 1
    
    def finalize(self):
        """Finalize session statistics."""
        self.session_stats.end_time = datetime.now().isoformat()
        
        # Calculate final cursor stats
        if self.total_cursor_distance > 0:
            self.session_stats.cursor_movement_stats['total_distance_pixels'] = \
                self.total_cursor_distance
            self.session_stats.cursor_movement_stats['total_clicks'] = self.total_clicks
    
    def save(self, file_path: Optional[Path] = None):
        """
        Save statistics to JSON file.
        
        Args:
            file_path: Path to save file (default: logs/stats.json)
        """
        if file_path is None:
            file_path = get_stats_file_path()
        
        # Ensure directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save to file
        with open(file_path, 'w') as f:
            json.dump(asdict(self.session_stats), f, indent=2)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert statistics to dictionary.
        
        Returns:
            Statistics as dictionary
        """
        return asdict(self.session_stats)
    
    def get_summary(self) -> str:
        """
        Get a human-readable summary of statistics.
        
        Returns:
            Formatted summary string
        """
        stats = self.session_stats
        
        summary_lines = [
            "=" * 60,
            "SESSION STATISTICS",
            "=" * 60,
            f"Session ID:       {stats.session_id}",
            f"Duration:         {self._format_duration()}",
            f"Cycles Completed: {stats.cycles_completed}",
            f"Cycles Failed:    {stats.cycles_failed}",
            f"Total Watch Time: {stats.total_watch_time / 60:.1f} minutes",
            f"Bio-Breaks:       {stats.bio_breaks_taken}",
            f"Avg Cycle Time:   {stats.average_cycle_duration:.1f} seconds",
        ]
        
        if stats.cursor_movement_stats:
            summary_lines.extend([
                "",
                "Cursor Movement:",
                f"  Total Distance: {stats.cursor_movement_stats.get('total_distance_pixels', 0):.0f} pixels",
                f"  Total Clicks:   {stats.cursor_movement_stats.get('total_clicks', 0)}",
            ])
        
        if stats.errors:
            summary_lines.extend([
                "",
                f"Errors ({len(stats.errors)}):",
            ])
            for error in stats.errors[:5]:  # Show first 5 errors
                summary_lines.append(f"  - {error}")
            if len(stats.errors) > 5:
                summary_lines.append(f"  ... and {len(stats.errors) - 5} more")
        
        summary_lines.append("=" * 60)
        
        return "\n".join(summary_lines)
    
    def _format_duration(self) -> str:
        """Format session duration as human-readable string."""
        if self.session_stats.end_time is None:
            return "In progress"
        
        start = datetime.fromisoformat(self.session_stats.start_time)
        end = datetime.fromisoformat(self.session_stats.end_time)
        duration = (end - start).total_seconds()
        
        hours = int(duration // 3600)
        minutes = int((duration % 3600) // 60)
        seconds = int(duration % 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
