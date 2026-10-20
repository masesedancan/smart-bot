"""
Main orchestrator - coordinates all bot components and executes the main loop.
"""

import logging
import time
from typing import Optional
from dataclasses import dataclass

from src.core.state_machine import StateMachine, BotState, create_state_machine
from src.core.session_manager import SessionManager, create_session_manager
from src.behavior.timing_engine import TimingEngine, create_timing_engine
from src.behavior.human_behaviors import HumanBehaviors, create_human_behaviors
from src.interaction.cursor_controller import CursorController, create_cursor_controller
from src.interaction.click_handler import ClickHandler, create_click_handler
from src.interaction.window_controller import WindowController, create_window_controller
from src.monitoring.stats_tracker import StatsTracker
from src.monitoring.performance_monitor import PerformanceMonitor
from src.safety.kill_switch import KillSwitch
from src.safety.error_recovery import ErrorRecovery, create_error_recovery
from src.safety.resource_guard import ResourceGuard, create_resource_guard

logger = logging.getLogger(__name__)


@dataclass
class ExecutionResult:
    """Result of orchestrator execution."""
    success: bool
    cycles_completed: int
    error_message: Optional[str] = None


class Orchestrator:
    """Main orchestrator that coordinates all bot components."""
    
    def __init__(self, config: dict, kill_switch: KillSwitch, 
                 max_cycles: Optional[int] = None):
        """
        Initialize orchestrator.
        
        Args:
            config: Configuration dictionary
            kill_switch: Kill switch instance
            max_cycles: Maximum number of cycles (None = unlimited)
        """
        self.config = config
        self.kill_switch = kill_switch
        self.max_cycles = max_cycles
        
        # Initialize components
        logger.info("Initializing orchestrator components...")
        
        self.state_machine = create_state_machine()
        self.session_manager = create_session_manager(config['behavior'])
        self.timing_engine = create_timing_engine(config['timing'])
        self.human_behaviors = create_human_behaviors(config['behavior'])
        self.cursor_controller = create_cursor_controller(config['cursor'])
        self.click_handler = create_click_handler(
            self.timing_engine,
            dry_run=config['debug']['dry_run_mode']
        )
        self.window_controller = create_window_controller(self.timing_engine)
        self.stats_tracker = StatsTracker()
        self.performance_monitor = PerformanceMonitor(
            cpu_threshold=config['safety']['cpu_threshold_percent'],
            memory_threshold=config['safety']['memory_threshold_percent']
        )
        self.error_recovery = create_error_recovery(config['safety'])
        self.resource_guard = create_resource_guard(config['safety'])
        
        # Get configuration values
        self.env = config['env']
        self.recorder_title = self.env['recorder_app_title']
        self.browser_title = self.env['browser_window_title']
        self.start_button_x = self.env['start_button_x']
        self.start_button_y = self.env['start_button_y']
        self.stop_button_x = self.env['stop_button_x']
        self.stop_button_y = self.env['stop_button_y']
        # Minimize button coords (the "-" icon on Loggy3 top-right)
        self.minimize_button_x = self.env.get('minimize_button_x', 0)
        self.minimize_button_y = self.env.get('minimize_button_y', 0)
        
        # Runtime settings
        self.single_cycle = config['debug']['single_cycle_only']
        self.max_runtime_hours = config['safety']['max_runtime_hours']
        
        logger.info("Orchestrator initialized successfully")
    
    def run(self) -> ExecutionResult:
        """
        Run the main orchestration loop.
        
        Returns:
            ExecutionResult with success status and statistics
        """
        logger.info("Starting orchestrator main loop")
        
        try:
            # Main loop
            while not self._should_stop():
                # Execute one cycle
                success = self._execute_cycle()
                
                if not success:
                    logger.error("Cycle execution failed")
                    break
                
                # Increment cycle counter
                self.session_manager.increment_cycle()
                
                # Check if we should stop
                if self.single_cycle:
                    logger.info("Single-cycle mode: stopping after one cycle")
                    break
                
                if self.max_cycles and self.session_manager.cycles_completed >= self.max_cycles:
                    logger.info(f"Max cycles ({self.max_cycles}) reached")
                    break
                
                # Check for bio-break
                if self.session_manager.should_take_bio_break():
                    self._execute_bio_break()
            
            # Finalize and return
            return self._finalize()
            
        except KeyboardInterrupt:
            logger.warning("Interrupted by user")
            return self._finalize(error="User interrupted")
        
        except Exception as e:
            logger.exception(f"Unexpected error in orchestrator: {e}")
            return self._finalize(error=str(e))
    
    def _execute_cycle(self) -> bool:
        """
        Execute one complete cycle.
        
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Starting cycle #{self.session_manager.cycles_completed + 1}")
        self.stats_tracker.start_cycle()
        watch_duration = 0.0
        
        try:
            # 1. Locate recorder window
            if not self._locate_recorder():
                return False

            # 2. Move to START button and click
            if not self._click_start_button():
                return False

            # 3. Minimize Loggy3 (click the "-" icon or use window manager)
            if not self._minimize_recorder():
                return False

            # 4. Switch to YouTube / browser
            if not self._switch_to_browser():
                return False

            # 5. Watch with micro-distractions (~130 s)
            watch_duration = self._watch_phase()

            # 6. Restore Loggy3 from taskbar
            if not self._restore_recorder():
                return False

            # 7. Move to STOP button and click
            if not self._click_stop_button():
                return False

            # 8. Cooldown (let Loggy3 finish upload/processing)
            self._cooldown()
            
            # Record success
            self.stats_tracker.end_cycle(success=True, watch_duration=watch_duration)
            logger.info("Cycle completed successfully")
            
            return True
            
        except Exception as e:
            logger.error(f"Cycle failed: {e}")
            self.stats_tracker.end_cycle(success=False, watch_duration=watch_duration, error_message=str(e))
            return False
    
    def _locate_recorder(self) -> bool:
        """Locate and cache recorder window."""
        self.state_machine.transition_to(BotState.LOCATING_RECORDER)
        
        logger.info(f"Locating recorder window: {self.recorder_title}")
        
        # Check resources
        safe, msg = self.resource_guard.check_resources()
        if not safe:
            logger.error(msg)
            return False
        
        # Locate window
        self.window_controller.cache_windows(self.recorder_title, self.browser_title)
        
        return True
    
    def _click_start_button(self) -> bool:
        """Move to START button and click it."""
        # Move cursor
        self.state_machine.transition_to(BotState.MOVING_TO_START)
        logger.info(f"Moving to START button at ({self.start_button_x}, {self.start_button_y})")
        
        if not self.cursor_controller.move_to(
            self.start_button_x,
            self.start_button_y,
            overshoot=True,
            overshoot_probability=self.config['behavior']['overshoot_probability']
        ):
            logger.error("Failed to move to START button")
            return False
        
        # Click
        self.state_machine.transition_to(BotState.CLICKING_START)
        logger.info("Clicking START button")
        
        if not self.click_handler.click_at(self.start_button_x, self.start_button_y):
            logger.error("Failed to click START button")
            return False
        
        return True
    
    def _minimize_recorder(self) -> bool:
        """
        Minimize the Loggy3 recorder window after clicking Start.

        Prefers clicking the on-screen minimize ("-") button if coordinates
        are configured; falls back to the window manager minimize call.

        Returns:
            True if successful, False otherwise
        """
        self.state_machine.transition_to(BotState.SWITCHING_TO_BROWSER)
        logger.info("Minimizing Loggy3 recorder window")

        # If minimize button coordinates are known, click the "-" icon directly
        if self.minimize_button_x and self.minimize_button_y:
            logger.info(
                f"Clicking minimize icon at "
                f"({self.minimize_button_x}, {self.minimize_button_y})"
            )
            self.cursor_controller.move_to(
                self.minimize_button_x,
                self.minimize_button_y,
                overshoot=True,
                overshoot_probability=self.config['behavior']['overshoot_probability']
            )
            if not self.click_handler.click_at(
                self.minimize_button_x, self.minimize_button_y
            ):
                logger.warning(
                    "Click on minimize icon failed — falling back to "
                    "window manager minimize"
                )
                return self.window_controller.minimize_window(self.recorder_title)
            time.sleep(0.6)  # let the window animate down
            return True

        # No coordinates — use window manager directly
        return self.window_controller.minimize_window(self.recorder_title)

    def _restore_recorder(self) -> bool:
        """
        Restore (un-minimize) the Loggy3 window from the taskbar.

        Returns:
            True if successful, False otherwise
        """
        self.state_machine.transition_to(BotState.SWITCHING_TO_RECORDER)
        logger.info(f"Restoring Loggy3 from taskbar: {self.recorder_title}")

        if not self.window_controller.restore_window(self.recorder_title):
            logger.error("Failed to restore Loggy3 from taskbar")
            return False

        return True

    def _switch_to_browser(self) -> bool:
        """Switch to browser window."""
        self.state_machine.transition_to(BotState.SWITCHING_TO_BROWSER)
        logger.info(f"Switching to browser: {self.browser_title}")
        
        if not self.window_controller.switch_to_window(self.browser_title):
            logger.error("Failed to switch to browser")
            return False
        
        return True
    
    def _watch_phase(self) -> float:
        """Execute watching phase with micro-distractions."""
        self.state_machine.transition_to(BotState.WATCHING)
        
        # Get watch duration
        watch_duration = self.timing_engine.get_watch_duration()
        logger.info(f"Watching for {watch_duration:.1f} seconds...")
        
        # Chunked wait with micro-distraction checks
        distraction_interval = self.config['behavior']['micro_distraction_interval']
        elapsed = 0.0
        
        while elapsed < watch_duration:
            # Check kill switch
            if self._should_stop():
                return elapsed
            
            # Sleep for chunk
            chunk_duration = min(distraction_interval, watch_duration - elapsed)
            time.sleep(chunk_duration)
            elapsed += chunk_duration
            
            # Check for micro-distraction
            if elapsed < watch_duration and self.human_behaviors.should_perform_micro_distraction():
                self.human_behaviors.perform_random_micro_action()
        
        logger.info(f"Watch phase complete ({elapsed:.1f}s)")
        return elapsed
    
    def _switch_to_recorder(self) -> bool:
        """Switch back to recorder window."""
        self.state_machine.transition_to(BotState.SWITCHING_TO_RECORDER)
        logger.info(f"Switching back to recorder: {self.recorder_title}")
        
        if not self.window_controller.switch_to_window(self.recorder_title):
            logger.error("Failed to switch to recorder")
            return False
        
        return True
    
    def _click_stop_button(self) -> bool:
        """Move to STOP button and click it."""
        # Move cursor
        self.state_machine.transition_to(BotState.MOVING_TO_STOP)
        logger.info(f"Moving to STOP button at ({self.stop_button_x}, {self.stop_button_y})")
        
        if not self.cursor_controller.move_to(
            self.stop_button_x,
            self.stop_button_y,
            overshoot=True,
            overshoot_probability=self.config['behavior']['overshoot_probability']
        ):
            logger.error("Failed to move to STOP button")
            return False
        
        # Click
        self.state_machine.transition_to(BotState.CLICKING_STOP)
        logger.info("Clicking STOP button")
        
        if not self.click_handler.click_at(self.stop_button_x, self.stop_button_y):
            logger.error("Failed to click STOP button")
            return False
        
        return True
    
    def _cooldown(self):
        """Execute cooldown period."""
        self.state_machine.transition_to(BotState.COOLDOWN)
        
        cooldown_duration = self.timing_engine.get_cooldown_duration()
        logger.info(f"Cooldown for {cooldown_duration:.1f} seconds")
        time.sleep(cooldown_duration)
    
    def _execute_bio_break(self):
        """Execute a bio-break."""
        self.state_machine.transition_to(BotState.BIO_BREAK)
        
        break_duration = self.session_manager.get_bio_break_duration()
        logger.info(f"Taking bio-break for {break_duration / 60:.1f} minutes")
        
        # Chunked wait so we can check kill switch
        elapsed = 0.0
        while elapsed < break_duration:
            if self._should_stop():
                return
            
            chunk = min(10.0, break_duration - elapsed)
            time.sleep(chunk)
            elapsed += chunk
        
        self.session_manager.record_bio_break()
        self.stats_tracker.record_bio_break()
        logger.info("Bio-break complete")
    
    def _should_stop(self) -> bool:
        """Check if orchestrator should stop."""
        # Kill switch
        if self.kill_switch.is_triggered():
            logger.warning("Kill switch triggered")
            return True
        
        # Mouse corner panic
        if self.kill_switch.check_mouse_corner():
            self.kill_switch.trigger()
            return True
        
        # Max runtime
        if self.session_manager.should_stop_session(self.max_runtime_hours):
            return True
        
        return False
    
    def _finalize(self, error: Optional[str] = None) -> ExecutionResult:
        """
        Finalize execution and clean up.
        
        Args:
            error: Optional error message
            
        Returns:
            ExecutionResult
        """
        logger.info("Finalizing orchestrator...")
        
        # Finalize statistics
        self.stats_tracker.finalize()
        self.stats_tracker.save()
        
        # Log summary
        logger.info("\n" + self.stats_tracker.get_summary())
        
        # Stop kill switch
        self.kill_switch.stop()
        
        # Create result
        result = ExecutionResult(
            success=(error is None),
            cycles_completed=self.session_manager.cycles_completed,
            error_message=error
        )
        
        logger.info("Orchestrator shutdown complete")
        return result
