"""
Emergency kill switch for graceful shutdown.
"""

import logging
import threading
import pyautogui
from typing import Optional

try:
    from pynput import keyboard
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False
    logging.warning("pynput not available, keyboard kill switch disabled")

logger = logging.getLogger(__name__)


class KillSwitch:
    """Emergency stop mechanism with multiple trigger methods."""
    
    def __init__(self, config: dict):
        """
        Initialize kill switch.
        
        Args:
            config: Configuration dictionary with safety settings
        """
        self.config = config
        self.safety_config = config.get('safety', {})
        self.triggered = False
        self.listener: Optional[keyboard.Listener] = None
        self._lock = threading.Lock()
        
        # Keys currently pressed
        self.current_keys = set()
        
        # Parse keyboard killswitch combination
        killswitch_str = self.safety_config.get('keyboard_killswitch', 'ctrl+shift+q')
        self.killswitch_keys = self._parse_key_combination(killswitch_str)
        
    def _parse_key_combination(self, combo: str) -> set:
        """
        Parse key combination string into set of keys.
        
        Args:
            combo: Key combination string (e.g., "ctrl+shift+q")
            
        Returns:
            Set of key names
        """
        keys = combo.lower().split('+')
        parsed = set()
        
        for key in keys:
            key = key.strip()
            # Map common names
            if key == 'ctrl':
                parsed.add('ctrl_l')
                parsed.add('ctrl_r')
            elif key == 'shift':
                parsed.add('shift_l')
                parsed.add('shift_r')
            elif key == 'alt':
                parsed.add('alt_l')
                parsed.add('alt_r')
            else:
                parsed.add(key)
        
        return parsed
    
    def start(self):
        """Start the kill switch listener."""
        if not PYNPUT_AVAILABLE:
            logger.warning("Kill switch disabled (pynput not available)")
            return
        
        try:
            self.listener = keyboard.Listener(
                on_press=self._on_key_press,
                on_release=self._on_key_release
            )
            self.listener.start()
            logger.info(f"Kill switch active: {self.safety_config.get('keyboard_killswitch', 'ctrl+shift+q')}")
            
        except Exception as e:
            logger.error(f"Failed to start kill switch listener: {e}")
    
    def stop(self):
        """Stop the kill switch listener."""
        if self.listener:
            self.listener.stop()
            logger.info("Kill switch listener stopped")
    
    def _on_key_press(self, key):
        """Handle key press event."""
        try:
            # Get key name
            key_name = self._get_key_name(key)
            
            # Add to current keys
            with self._lock:
                self.current_keys.add(key_name)
                
                # Check if killswitch combination is pressed
                if self._is_killswitch_pressed():
                    logger.warning("KILL SWITCH TRIGGERED!")
                    self.trigger()
                    
        except Exception as e:
            logger.debug(f"Error in key press handler: {e}")
    
    def _on_key_release(self, key):
        """Handle key release event."""
        try:
            # Get key name
            key_name = self._get_key_name(key)
            
            # Remove from current keys
            with self._lock:
                self.current_keys.discard(key_name)
                
        except Exception as e:
            logger.debug(f"Error in key release handler: {e}")
    
    def _get_key_name(self, key) -> str:
        """Get normalized key name."""
        if hasattr(key, 'char') and key.char:
            return key.char.lower()
        elif hasattr(key, 'name'):
            return key.name.lower()
        else:
            return str(key).lower()
    
    def _is_killswitch_pressed(self) -> bool:
        """Check if killswitch combination is currently pressed."""
        # Check if any variant of the required keys are pressed
        for required_key in self.killswitch_keys:
            if required_key not in self.current_keys:
                # Check for variants (left/right modifiers)
                if required_key.endswith('_l') or required_key.endswith('_r'):
                    base_key = required_key[:-2]
                    has_variant = any(k.startswith(base_key) for k in self.current_keys)
                    if not has_variant:
                        return False
                else:
                    return False
        
        return len(self.killswitch_keys) > 0
    
    def trigger(self):
        """Trigger the kill switch."""
        with self._lock:
            if not self.triggered:
                self.triggered = True
                logger.critical("EMERGENCY STOP ACTIVATED")
    
    def is_triggered(self) -> bool:
        """Check if kill switch has been triggered."""
        with self._lock:
            return self.triggered
    
    def check_mouse_corner(self) -> bool:
        """
        Check if mouse is in top-left corner (panic position).
        
        Returns:
            True if in corner for panic duration
        """
        if not self.safety_config.get('mouse_corner_killswitch', True):
            return False
        
        try:
            x, y = pyautogui.position()
            
            # Check if in top-left corner (within 10 pixels)
            if x <= 10 and y <= 10:
                logger.warning("Mouse in panic corner!")
                return True
                
        except Exception:
            pass
        
        return False
    
    def reset(self):
        """Reset the kill switch (for testing)."""
        with self._lock:
            self.triggered = False
            self.current_keys.clear()


def create_kill_switch(config: dict) -> KillSwitch:
    """
    Create a kill switch instance.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Configured KillSwitch instance
    """
    return KillSwitch(config)
