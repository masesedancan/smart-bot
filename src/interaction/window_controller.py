"""
Window controller for finding and switching between windows.
Linux-compatible implementation using wmctrl and xdotool.
"""

import logging
import time
import pyautogui
import subprocess
import platform
from typing import Optional, List

from src.behavior.timing_engine import TimingEngine

logger = logging.getLogger(__name__)

# Detect platform and available tools
IS_LINUX = platform.system() == 'Linux'
WMCTRL_AVAILABLE = False
XDOTOOL_AVAILABLE = False

if IS_LINUX:
    # Check for wmctrl
    try:
        subprocess.run(['wmctrl', '-h'], capture_output=True, timeout=1)
        WMCTRL_AVAILABLE = True
        logger.info("wmctrl is available")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        logger.warning("wmctrl not found. Install with: sudo apt-get install wmctrl")
    
    # Check for xdotool
    try:
        subprocess.run(['xdotool', '--version'], capture_output=True, timeout=1)
        XDOTOOL_AVAILABLE = True
        logger.info("xdotool is available")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        logger.warning("xdotool not found. Install with: sudo apt-get install xdotool")


class WindowController:
    """Controls window detection and switching (Linux-compatible)."""
    
    def __init__(self, timing_engine: TimingEngine):
        """
        Initialize window controller.
        
        Args:
            timing_engine: Timing engine for delays
        """
        self.timing_engine = timing_engine
        self.recorder_window = None
        self.browser_window = None
        
        if IS_LINUX and not (WMCTRL_AVAILABLE or XDOTOOL_AVAILABLE):
            logger.warning("Neither wmctrl nor xdotool available. Window management will be limited.")
    
    def _get_window_list_linux(self) -> List[dict]:
        """
        Get list of all windows on Linux using wmctrl.
        
        Returns:
            List of dicts with window info: {'id': str, 'desktop': str, 'title': str}
        """
        if not WMCTRL_AVAILABLE:
            return []
        
        try:
            result = subprocess.run(
                ['wmctrl', '-l'],
                capture_output=True,
                text=True,
                timeout=2
            )
            
            windows = []
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                
                parts = line.split(None, 3)
                if len(parts) >= 4:
                    windows.append({
                        'id': parts[0],
                        'desktop': parts[1],
                        'title': parts[3]
                    })
            
            return windows
            
        except Exception as e:
            logger.error(f"Error listing windows: {e}")
            return []
    
    def find_window(self, title: str) -> Optional[dict]:
        """
        Find a window by title.
        
        Args:
            title: Window title (can be partial match)
            
        Returns:
            Window dict or None if not found
        """
        if not IS_LINUX:
            logger.warning("Window finding only supported on Linux")
            return None
        
        try:
            windows = self._get_window_list_linux()
            
            # Find matching window
            for window in windows:
                if title.lower() in window['title'].lower():
                    logger.debug(f"Found window: {window['title']}")
                    return window
            
            logger.warning(f"Window not found with title containing: '{title}'")
            return None
            
        except Exception as e:
            logger.error(f"Error finding window: {e}")
            return None
    
    def switch_to_window(self, window_title: str) -> bool:
        """
        Switch to a window by title.
        
        Args:
            window_title: Title of window to switch to
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Try wmctrl activation
            if WMCTRL_AVAILABLE:
                window = self.find_window(window_title)
                if window:
                    try:
                        # Activate window using wmctrl
                        subprocess.run(
                            ['wmctrl', '-i', '-a', window['id']],
                            capture_output=True,
                            timeout=2
                        )
                        logger.info(f"Switched to window: {window_title}")
                        
                        # Wait for switch to complete
                        delay = self.timing_engine.get_window_switch_delay()
                        time.sleep(delay)
                        
                        return True
                    except Exception as e:
                        logger.warning(f"Failed to activate window with wmctrl: {e}")
            
            # Try xdotool activation
            if XDOTOOL_AVAILABLE:
                try:
                    # Search for window and activate
                    result = subprocess.run(
                        ['xdotool', 'search', '--name', window_title, 'windowactivate'],
                        capture_output=True,
                        text=True,
                        timeout=2
                    )
                    
                    if result.returncode == 0:
                        logger.info(f"Switched to window using xdotool: {window_title}")
                        
                        delay = self.timing_engine.get_window_switch_delay()
                        time.sleep(delay)
                        
                        return True
                except Exception as e:
                    logger.warning(f"Failed to activate window with xdotool: {e}")
            
            # Fallback: use Alt+Tab
            logger.info(f"Using Alt+Tab to switch to: {window_title}")
            return self._alt_tab()
            
        except Exception as e:
            logger.error(f"Failed to switch window: {e}")
            return False
    
    def _alt_tab(self) -> bool:
        """
        Simulate Alt+Tab key press.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Press Alt+Tab
            pyautogui.keyDown('alt')
            time.sleep(0.05)  # Brief hold
            pyautogui.press('tab')
            time.sleep(0.05)
            pyautogui.keyUp('alt')
            
            logger.debug("Alt+Tab pressed")
            
            # Wait for window switch
            delay = self.timing_engine.get_window_switch_delay()
            time.sleep(delay)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to press Alt+Tab: {e}")
            return False
    
    def is_window_visible(self, window_title: str) -> bool:
        """
        Check if a window is visible (not minimized).
        
        Args:
            window_title: Window title to check
            
        Returns:
            True if visible, False otherwise
        """
        if not IS_LINUX:
            return True  # Assume visible if we can't check
        
        try:
            window = self.find_window(window_title)
            if window:
                # On Linux, we assume if we found it, it exists
                # More sophisticated checking would require parsing window state
                return True
            return False
            
        except Exception as e:
            logger.warning(f"Error checking window visibility: {e}")
            return True  # Assume visible on error
    
    def get_active_window_title(self) -> Optional[str]:
        """
        Get the title of the currently active window.
        
        Returns:
            Active window title or None
        """
        if not IS_LINUX:
            return None
        
        try:
            if XDOTOOL_AVAILABLE:
                # Get active window ID
                result = subprocess.run(
                    ['xdotool', 'getactivewindow', 'getwindowname'],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                
                if result.returncode == 0:
                    return result.stdout.strip()
            
            elif WMCTRL_AVAILABLE:
                # Use wmctrl to get active window
                result = subprocess.run(
                    ['wmctrl', '-l'],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                
                # This is a simplification - wmctrl doesn't directly show active window
                # You'd need additional logic to determine which is active
                pass
            
            return None
            
        except Exception as e:
            logger.warning(f"Error getting active window: {e}")
            return None
    
    def minimize_window(self, window_title: str) -> bool:
        """
        Minimize a window by title.

        Tries wmctrl first, then xdotool, then falls back to
        clicking the minimize button via keyboard shortcut.

        Args:
            window_title: Title of window to minimize

        Returns:
            True if successful, False otherwise
        """
        try:
            if WMCTRL_AVAILABLE:
                window = self.find_window(window_title)
                if window:
                    # Use wmctrl to iconify (minimize) the window
                    result = subprocess.run(
                        ['wmctrl', '-i', '-r', window['id'], '-b', 'add,hidden'],
                        capture_output=True,
                        timeout=2
                    )
                    if result.returncode == 0:
                        logger.info(f"Minimized window via wmctrl: {window_title}")
                        time.sleep(0.5)
                        return True

            if XDOTOOL_AVAILABLE:
                window = self.find_window(window_title)
                if window:
                    result = subprocess.run(
                        ['xdotool', 'search', '--name', window_title,
                         'windowminimize'],
                        capture_output=True,
                        text=True,
                        timeout=2
                    )
                    if result.returncode == 0:
                        logger.info(f"Minimized window via xdotool: {window_title}")
                        time.sleep(0.5)
                        return True

            # Fallback: press the Super+H or Alt+F9 minimize shortcut
            logger.info("Using keyboard shortcut to minimize window")
            pyautogui.hotkey('alt', 'F9')
            time.sleep(0.5)
            return True

        except Exception as e:
            logger.error(f"Failed to minimize window '{window_title}': {e}")
            return False

    def restore_window(self, window_title: str) -> bool:
        """
        Restore (un-minimize) a window from the taskbar by title.

        On Linux this activates the window, which automatically
        un-minimizes it.

        Args:
            window_title: Title of window to restore

        Returns:
            True if successful, False otherwise
        """
        try:
            if WMCTRL_AVAILABLE:
                window = self.find_window(window_title)
                if window:
                    # Remove hidden flag then activate
                    subprocess.run(
                        ['wmctrl', '-i', '-r', window['id'],
                         '-b', 'remove,hidden'],
                        capture_output=True,
                        timeout=2
                    )
                    subprocess.run(
                        ['wmctrl', '-i', '-a', window['id']],
                        capture_output=True,
                        timeout=2
                    )
                    logger.info(f"Restored window via wmctrl: {window_title}")
                    delay = self.timing_engine.get_window_switch_delay()
                    time.sleep(delay)
                    return True

            if XDOTOOL_AVAILABLE:
                result = subprocess.run(
                    ['xdotool', 'search', '--name', window_title,
                     'windowactivate', '--sync'],
                    capture_output=True,
                    text=True,
                    timeout=3
                )
                if result.returncode == 0:
                    logger.info(f"Restored window via xdotool: {window_title}")
                    delay = self.timing_engine.get_window_switch_delay()
                    time.sleep(delay)
                    return True

            # Fallback: switch_to_window already handles Alt+Tab
            logger.info(f"Falling back to switch_to_window for restore: {window_title}")
            return self.switch_to_window(window_title)

        except Exception as e:
            logger.error(f"Failed to restore window '{window_title}': {e}")
            return False

    def cache_windows(self, recorder_title: str, browser_title: str):
        """
        Cache window references for faster access.
        
        Args:
            recorder_title: Recorder app window title
            browser_title: Browser window title
        """
        self.recorder_window = self.find_window(recorder_title)
        self.browser_window = self.find_window(browser_title)
        
        if self.recorder_window:
            logger.info(f"Cached recorder window: {self.recorder_window['title']}")
        else:
            logger.warning(f"Recorder window not found: {recorder_title}")
        
        if self.browser_window:
            logger.info(f"Cached browser window: {self.browser_window['title']}")
        else:
            logger.warning(f"Browser window not found: {browser_title}")


def create_window_controller(timing_engine: TimingEngine) -> WindowController:
    """
    Create a window controller.
    
    Args:
        timing_engine: Timing engine instance
        
    Returns:
        Configured WindowController instance
    """
    return WindowController(timing_engine)
