"""
State machine for managing bot execution states.
"""

import logging
from enum import Enum, auto
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class BotState(Enum):
    """Bot execution states."""
    IDLE = auto()
    LOCATING_RECORDER = auto()
    MOVING_TO_START = auto()
    CLICKING_START = auto()
    SWITCHING_TO_BROWSER = auto()
    WATCHING = auto()
    SWITCHING_TO_RECORDER = auto()
    MOVING_TO_STOP = auto()
    CLICKING_STOP = auto()
    COOLDOWN = auto()
    BIO_BREAK = auto()
    ERROR = auto()
    STOPPED = auto()


class StateMachine:
    """Manages bot state transitions and context."""
    
    # Valid state transitions
    VALID_TRANSITIONS = {
        BotState.IDLE: [BotState.LOCATING_RECORDER, BotState.STOPPED],
        BotState.LOCATING_RECORDER: [
            BotState.MOVING_TO_START,
            BotState.ERROR,
            BotState.STOPPED
        ],
        BotState.MOVING_TO_START: [
            BotState.CLICKING_START,
            BotState.ERROR,
            BotState.STOPPED
        ],
        BotState.CLICKING_START: [
            BotState.SWITCHING_TO_BROWSER,
            BotState.ERROR,
            BotState.STOPPED
        ],
        BotState.SWITCHING_TO_BROWSER: [
            BotState.WATCHING,
            BotState.ERROR,
            BotState.STOPPED
        ],
        BotState.WATCHING: [
            BotState.SWITCHING_TO_RECORDER,
            BotState.ERROR,
            BotState.STOPPED
        ],
        BotState.SWITCHING_TO_RECORDER: [
            BotState.MOVING_TO_STOP,
            BotState.ERROR,
            BotState.STOPPED
        ],
        BotState.MOVING_TO_STOP: [
            BotState.CLICKING_STOP,
            BotState.ERROR,
            BotState.STOPPED
        ],
        BotState.CLICKING_STOP: [
            BotState.COOLDOWN,
            BotState.ERROR,
            BotState.STOPPED
        ],
        BotState.COOLDOWN: [
            BotState.BIO_BREAK,
            BotState.LOCATING_RECORDER,
            BotState.STOPPED
        ],
        BotState.BIO_BREAK: [
            BotState.LOCATING_RECORDER,
            BotState.STOPPED
        ],
        BotState.ERROR: [
            BotState.LOCATING_RECORDER,  # Retry
            BotState.STOPPED
        ],
        BotState.STOPPED: []  # Terminal state
    }
    
    def __init__(self):
        """Initialize state machine."""
        self.current_state = BotState.IDLE
        self.previous_state: Optional[BotState] = None
        self.state_context: Dict[str, Any] = {}
        self.state_entry_time: Optional[datetime] = None
        self.transition_count = 0
    
    def transition_to(self, new_state: BotState, context: Optional[Dict[str, Any]] = None):
        """
        Transition to a new state.
        
        Args:
            new_state: Target state
            context: Optional context data for the state
            
        Raises:
            ValueError: If transition is invalid
        """
        # Validate transition
        if new_state not in self.VALID_TRANSITIONS.get(self.current_state, []):
            raise ValueError(
                f"Invalid transition: {self.current_state.name} -> {new_state.name}"
            )
        
        # Log transition
        logger.info(f"State transition: {self.current_state.name} → {new_state.name}")
        
        # Update state
        self.previous_state = self.current_state
        self.current_state = new_state
        self.state_entry_time = datetime.now()
        self.transition_count += 1
        
        # Update context
        if context:
            self.state_context.update(context)
    
    def can_transition_to(self, new_state: BotState) -> bool:
        """
        Check if transition to new state is valid.
        
        Args:
            new_state: Target state
            
        Returns:
            True if transition is valid
        """
        return new_state in self.VALID_TRANSITIONS.get(self.current_state, [])
    
    def get_state(self) -> BotState:
        """Get current state."""
        return self.current_state
    
    def is_in_state(self, state: BotState) -> bool:
        """Check if in specific state."""
        return self.current_state == state
    
    def is_terminal(self) -> bool:
        """Check if in terminal state."""
        return self.current_state == BotState.STOPPED
    
    def is_error(self) -> bool:
        """Check if in error state."""
        return self.current_state == BotState.ERROR
    
    def get_context(self, key: str, default: Any = None) -> Any:
        """Get value from state context."""
        return self.state_context.get(key, default)
    
    def set_context(self, key: str, value: Any):
        """Set value in state context."""
        self.state_context[key] = value
    
    def clear_context(self):
        """Clear state context."""
        self.state_context.clear()
    
    def get_time_in_state(self) -> float:
        """
        Get time spent in current state.
        
        Returns:
            Time in seconds, or 0 if not set
        """
        if self.state_entry_time:
            return (datetime.now() - self.state_entry_time).total_seconds()
        return 0.0
    
    def get_state_summary(self) -> str:
        """
        Get a summary of current state.
        
        Returns:
            Formatted state summary
        """
        time_in_state = self.get_time_in_state()
        return (
            f"State: {self.current_state.name} "
            f"(for {time_in_state:.1f}s, "
            f"{self.transition_count} transitions total)"
        )


def create_state_machine() -> StateMachine:
    """
    Create a new state machine instance.
    
    Returns:
        Initialized StateMachine
    """
    return StateMachine()
