#!/usr/bin/env python3
"""
Loggy3 Recording-Cycle Bot  –  Windows edition
================================================
Automates the Loggy3 recording cycle using image recognition to find
buttons on screen. No hardcoded pixel coordinates needed.

Cycle (runs forever until stopped):
  1. Bring Loggy3 window to the front
  2. Find & click  [▷ Start]
  3. Wait for recording to begin (Stop button appears)
  4. Click the minimize [—] icon  →  Loggy3 goes to taskbar
  5. Switch to YouTube web-app
  6. Watch for ~130 seconds
  7. Restore Loggy3 from taskbar
  8. Find & click  [□ Stop]
  9. Short cooldown, then back to step 1

Stop any time:
  • Ctrl+Shift+Q  (keyboard kill-switch)
  • Move mouse to top-left corner of screen
  • Ctrl+C in the terminal

Quick start (Windows):
  1. Install Python 3.9+ from python.org
  2. Open a terminal in this folder:
       python -m venv venv
       venv\\Scripts\\activate
       pip install -r requirements.txt
  3. Open Loggy3 and YouTube, then:
       python loggy3_bot.py --dry-run --single-cycle
       python loggy3_bot.py
"""

import sys
import time
import signal
import logging
import argparse
import platform
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.config.config_loader import ConfigLoader
from src.monitoring.logger_config import setup_logging
from src.safety.kill_switch import KillSwitch, create_kill_switch
from src.behavior.timing_engine import create_timing_engine
from src.monitoring.stats_tracker import StatsTracker
from src.utils.visual_finder import VisualFinder

# ── Platform detection ────────────────────────────────────────────────────────
IS_WINDOWS = platform.system() == "Windows"
IS_LINUX   = platform.system() == "Linux"
IS_MAC     = platform.system() == "Darwin"

# ── Button image paths ────────────────────────────────────────────────────────
BUTTONS_DIR  = Path("data/buttons")
START_IMG    = BUTTONS_DIR / "start_button.png"
STOP_IMG     = BUTTONS_DIR / "stop_button.png"
MINIMIZE_IMG = BUTTONS_DIR / "minimize_button.png"


# ─────────────────────────────────────────────────────────────────────────────
# Cross-platform Window Manager
# ─────────────────────────────────────────────────────────────────────────────

class WindowManager:
    """
    Cross-platform window focus / minimize / restore.

    Windows  → pygetwindow
    Linux    → xdotool / wmctrl
    macOS    → osascript (AppleScript)
    """

    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)
        self._init_backend()

    def _init_backend(self):
        """Load the right backend for the current OS."""
        if IS_WINDOWS:
            try:
                import pygetwindow as gw
                self._gw = gw
                self.log.info("Window backend: pygetwindow (Windows)")
            except ImportError:
                self._gw = None
                self.log.error(
                    "pygetwindow not installed. Run:  pip install pygetwindow"
                )
        else:
            self._gw = None

    # ── helpers ───────────────────────────────────────────────────────────────

    def _find_win_windows(self, fragment: str):
        """Find a window on Windows by partial title (case-insensitive)."""
        if not self._gw:
            return None
        frag = fragment.lower()
        for title in self._gw.getAllTitles():
            if frag in title.lower():
                wins = self._gw.getWindowsWithTitle(title)
                if wins:
                    self.log.debug(f"Found window: '{title}'")
                    return wins[0]
        self.log.warning(f"Window not found: '{fragment}'")
        return None

    def _run(self, *args, timeout: int = 3) -> bool:
        """Run a subprocess command, return True on success."""
        import subprocess
        try:
            r = subprocess.run(list(args), capture_output=True,
                               text=True, timeout=timeout)
            return r.returncode == 0
        except Exception:
            return False

    def _xdotool_find(self, fragment: str) -> str | None:
        """Find window ID via xdotool on Linux."""
        import subprocess
        try:
            r = subprocess.run(
                ["xdotool", "search", "--name", fragment],
                capture_output=True, text=True, timeout=3
            )
            ids = r.stdout.strip().splitlines()
            return ids[0] if ids else None
        except Exception:
            return None

    # ── public API ────────────────────────────────────────────────────────────

    def focus(self, title_fragment: str) -> bool:
        """Bring a window to the front."""
        self.log.info(f"Focusing: '{title_fragment}'")

        # ── Windows ──────────────────────────────────────────────────────────
        if IS_WINDOWS:
            win = self._find_win_windows(title_fragment)
            if win:
                try:
                    if win.isMinimized:
                        win.restore()
                        time.sleep(0.4)
                    win.activate()
                    time.sleep(0.6)
                    return True
                except Exception as e:
                    self.log.warning(f"activate() failed: {e}, trying maximize")
                    try:
                        win.maximize()
                        time.sleep(0.6)
                        return True
                    except Exception:
                        pass
            return False

        # ── Linux ─────────────────────────────────────────────────────────────
        if IS_LINUX:
            import subprocess
            # wmctrl
            r = subprocess.run(["wmctrl", "-l", "-p"], capture_output=True,
                               text=True, timeout=3)
            frag = title_fragment.lower()
            for line in r.stdout.strip().splitlines():
                parts = line.split(None, 4)
                if len(parts) >= 5 and frag in parts[4].lower():
                    subprocess.run(["wmctrl", "-i", "-a", parts[0]],
                                   capture_output=True, timeout=3)
                    time.sleep(0.8)
                    return True
            # xdotool fallback
            wid = self._xdotool_find(title_fragment)
            if wid:
                self._run("xdotool", "windowactivate", "--sync", wid)
                time.sleep(0.8)
                return True
            self.log.error(f"Cannot focus '{title_fragment}'")
            return False

        # ── macOS ─────────────────────────────────────────────────────────────
        if IS_MAC:
            import subprocess
            script = f'tell application "{title_fragment}" to activate'
            r = subprocess.run(["osascript", "-e", script],
                               capture_output=True, text=True, timeout=5)
            time.sleep(0.8)
            return r.returncode == 0

        return False

    def minimize(self, title_fragment: str) -> bool:
        """Minimize a window to the taskbar."""
        self.log.info(f"Minimizing: '{title_fragment}'")

        if IS_WINDOWS:
            win = self._find_win_windows(title_fragment)
            if win:
                try:
                    win.minimize()
                    time.sleep(0.5)
                    return True
                except Exception as e:
                    self.log.warning(f"minimize() failed: {e}")
            return False

        if IS_LINUX:
            import subprocess
            r = subprocess.run(["wmctrl", "-l", "-p"], capture_output=True,
                               text=True, timeout=3)
            frag = title_fragment.lower()
            for line in r.stdout.strip().splitlines():
                parts = line.split(None, 4)
                if len(parts) >= 5 and frag in parts[4].lower():
                    subprocess.run(
                        ["wmctrl", "-i", "-r", parts[0], "-b", "add,hidden"],
                        capture_output=True, timeout=3
                    )
                    time.sleep(0.5)
                    return True
            wid = self._xdotool_find(title_fragment)
            if wid:
                self._run("xdotool", "windowminimize", wid)
                time.sleep(0.5)
                return True
            # last resort keyboard shortcut
            import pyautogui
            pyautogui.hotkey("alt", "F9")
            time.sleep(0.5)
            return True

        if IS_MAC:
            import subprocess
            script = (
                f'tell application "System Events" to set visible of '
                f'process "{title_fragment}" to false'
            )
            subprocess.run(["osascript", "-e", script],
                           capture_output=True, timeout=5)
            time.sleep(0.5)
            return True

        return False

    def restore(self, title_fragment: str) -> bool:
        """Un-minimize / restore a window from the taskbar."""
        self.log.info(f"Restoring: '{title_fragment}'")
        # restore is the same as focus — activating a minimized window restores it
        return self.focus(title_fragment)


# ─────────────────────────────────────────────────────────────────────────────
# Main Bot
# ─────────────────────────────────────────────────────────────────────────────

class Loggy3Bot:
    """
    Image-recognition Loggy3 cycle bot.
    Works on Windows, Linux, and macOS.
    """

    def __init__(self, config: dict, kill_switch: KillSwitch,
                 dry_run: bool = False,
                 single_cycle: bool = False,
                 max_cycles: int = None):

        self.config       = config
        self.ks           = kill_switch
        self.dry_run      = dry_run
        self.single_cycle = single_cycle
        self.max_cycles   = max_cycles
        self.log          = logging.getLogger(self.__class__.__name__)

        env = config["env"]
        self.recorder_title = env.get("recorder_app_title", "Loggy3")
        self.browser_title  = env.get("browser_window_title", "YouTube")

        self.timing  = create_timing_engine(config["timing"])
        self.stats   = StatsTracker()
        self.windows = WindowManager()

        # Primary finder: high confidence
        self.finder    = VisualFinder(confidence=0.8, retries=6,  retry_delay=0.5)
        # Fallback finder: lower confidence
        self.finder_lo = VisualFinder(confidence=0.65, retries=4, retry_delay=0.6)

        self.cycles_done = 0

    # ── public ───────────────────────────────────────────────────────────────

    def run(self):
        self.log.info("=" * 55)
        self.log.info("  Loggy3 Bot  –  cross-platform edition")
        self.log.info(f"  Platform : {platform.system()}")
        self.log.info(f"  Recorder : '{self.recorder_title}'")
        self.log.info(f"  Browser  : '{self.browser_title}'")
        self.log.info("  Stop     : Ctrl+Shift+Q  or  mouse → top-left corner")
        self.log.info("=" * 55)

        if self.dry_run:
            self.log.warning("⚠  DRY-RUN – no real clicks")

        # Validate button images
        missing = [str(p) for p in (START_IMG, STOP_IMG, MINIMIZE_IMG)
                   if not p.exists()]
        if missing:
            self.log.error("Missing button images:\n" +
                           "\n".join(f"  {p}" for p in missing))
            self.log.error("Run this to regenerate them:  python recrop_buttons.py")
            return

        while not self._stopped():
            self.log.info(
                f"─── Cycle #{self.cycles_done + 1} ────────────────────────"
            )
            ok = self._run_cycle()

            if not ok:
                self.log.error("Cycle failed – stopping bot")
                break

            self.cycles_done += 1

            if self.single_cycle:
                self.log.info("Single-cycle mode: done.")
                break
            if self.max_cycles and self.cycles_done >= self.max_cycles:
                self.log.info(f"Reached max cycles ({self.max_cycles}).")
                break

        self.stats.finalize()
        self.stats.save()
        self.log.info(f"Finished. Cycles completed: {self.cycles_done}")

    # ── cycle ─────────────────────────────────────────────────────────────────

    def _run_cycle(self) -> bool:
        self.stats.start_cycle()
        watched = 0.0
        try:
            if not self._focus_loggy3():   return False
            if not self._click_start():    return False
            self._wait_for_recording()
            if not self._minimize_loggy3(): return False
            if not self._focus_youtube():  return False
            watched = self._watch()
            if not self._restore_loggy3(): return False
            if not self._click_stop():     return False
            self._cooldown()

            self.stats.end_cycle(success=True, watch_duration=watched)
            self.log.info(f"✓ Cycle done  (watched {watched:.0f} s)")
            return True

        except Exception as exc:
            self.log.exception(f"Cycle error: {exc}")
            self.stats.end_cycle(success=False, watch_duration=watched,
                                 error_message=str(exc))
            return False

    # ── steps ─────────────────────────────────────────────────────────────────

    def _focus_loggy3(self) -> bool:
        self.log.info("Focusing Loggy3 …")
        ok = self.windows.focus(self.recorder_title)
        if not ok:
            self.log.error(
                f"Cannot find Loggy3 window ('{self.recorder_title}').\n"
                f"  → Make sure Loggy3 is open.\n"
                f"  → Check RECORDER_APP_TITLE in .env matches the window title."
            )
        return ok

    def _click_start(self) -> bool:
        self.log.info("Looking for Start button …")
        ok = self.finder.find_and_click(str(START_IMG), dry_run=self.dry_run)
        if not ok:
            ok = self.finder_lo.find_and_click(str(START_IMG), dry_run=self.dry_run)
        if not ok:
            self.log.error(
                "Start button not found.\n"
                "  → Is Loggy3 fully visible on screen?\n"
                "  → Run:  python recrop_buttons.py  to refresh button images."
            )
        return ok

    def _wait_for_recording(self):
        """Wait up to 5 s for the Stop button to confirm recording started."""
        self.log.info("Confirming recording started …")
        pos = self.finder.wait_for(str(STOP_IMG), timeout=5.0)
        if pos:
            self.log.info("Recording confirmed ✓")
        else:
            self.log.warning("Could not confirm recording – continuing anyway")

    def _minimize_loggy3(self) -> bool:
        self.log.info("Minimizing Loggy3 …")

        # Preferred: click the visible "—" icon
        pos = self.finder.find(str(MINIMIZE_IMG), confidence=0.75)
        if pos:
            x, y = pos
            if self.dry_run:
                self.log.info(f"[DRY RUN] Would click minimize at ({x}, {y})")
            else:
                import pyautogui
                pyautogui.moveTo(x, y, duration=0.25)
                time.sleep(0.1)
                pyautogui.click(x, y)
            time.sleep(0.6)
            return True

        # Fallback: window manager minimize
        self.log.warning("Minimize icon not found visually – using window manager")
        return self.windows.minimize(self.recorder_title)

    def _focus_youtube(self) -> bool:
        self.log.info("Switching to YouTube …")
        ok = self.windows.focus(self.browser_title)
        if not ok:
            self.log.error(
                f"Cannot find YouTube window ('{self.browser_title}').\n"
                f"  → Make sure YouTube is open.\n"
                f"  → Check BROWSER_WINDOW_TITLE in .env."
            )
        return ok

    def _watch(self) -> float:
        """Wait ~130 s while YouTube plays."""
        duration = self.timing.get_watch_duration()
        self.log.info(f"Watching for {duration:.0f} s …")

        interval = self.config["behavior"].get("micro_distraction_interval", 30)
        elapsed  = 0.0
        while elapsed < duration:
            if self._stopped():
                break
            chunk    = min(interval, duration - elapsed)
            time.sleep(chunk)
            elapsed += chunk
            remaining = duration - elapsed
            if remaining > 5:
                self.log.info(f"  … {remaining:.0f} s remaining")

        return elapsed

    def _restore_loggy3(self) -> bool:
        self.log.info("Restoring Loggy3 from taskbar …")
        ok = self.windows.restore(self.recorder_title)
        if not ok:
            self.log.error("Failed to restore Loggy3")
        time.sleep(0.5)
        return ok

    def _click_stop(self) -> bool:
        self.log.info("Looking for Stop button …")
        ok = self.finder.find_and_click(str(STOP_IMG), dry_run=self.dry_run)
        if not ok:
            ok = self.finder_lo.find_and_click(str(STOP_IMG), dry_run=self.dry_run)
        if not ok:
            self.log.error(
                "Stop button not found.\n"
                "  → Is Loggy3 visible and in recording state?"
            )
        return ok

    def _cooldown(self):
        loggy3_cfg = self.config.get("loggy3", {})
        settle  = loggy3_cfg.get("post_stop_settle", 3.0)
        total   = self.timing.get_cooldown_duration() + settle
        self.log.info(f"Cooldown {total:.1f} s …")
        elapsed = 0.0
        while elapsed < total:
            if self._stopped():
                return
            chunk    = min(2.0, total - elapsed)
            time.sleep(chunk)
            elapsed += chunk

    # ── helper ────────────────────────────────────────────────────────────────

    def _stopped(self) -> bool:
        if self.ks.is_triggered():
            self.log.warning("Kill-switch active – stopping")
            return True
        if self.ks.check_mouse_corner():
            self.ks.trigger()
            return True
        return False


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(description="Loggy3 Recording-Cycle Bot")
    p.add_argument("--config",       default="config.yaml")
    p.add_argument("--dry-run",      action="store_true",
                   help="Simulate without real clicks")
    p.add_argument("--debug",        action="store_true",
                   help="Verbose logging")
    p.add_argument("--single-cycle", action="store_true",
                   help="Run one cycle then exit")
    p.add_argument("--max-cycles",   type=int, default=None)
    return p.parse_args()


def main():
    args   = parse_args()
    logger = setup_logging(level="DEBUG" if args.debug else "INFO")
    logger.info(f"Loggy3 Bot starting … (Python {sys.version.split()[0]}, "
                f"{platform.system()})")

    try:
        config = ConfigLoader.load(
            config_path=args.config,
            dry_run=args.dry_run,
            single_cycle=args.single_cycle,
        )
    except (FileNotFoundError, ValueError) as exc:
        logger.error(f"Config error: {exc}")
        return 1

    env     = config["env"]
    missing = [k for k in ("recorder_app_title", "browser_window_title")
               if not env.get(k)]
    if missing:
        logger.error("Missing .env values: " +
                     ", ".join(m.upper() for m in missing))
        return 1

    ks = create_kill_switch(config)

    def _sig(signum, frame):
        print("\n[!] Interrupt – shutting down …")
        ks.trigger()

    signal.signal(signal.SIGINT,  _sig)
    signal.signal(signal.SIGTERM, _sig)
    ks.start()

    bot = Loggy3Bot(
        config=config,
        kill_switch=ks,
        dry_run=args.dry_run,
        single_cycle=args.single_cycle,
        max_cycles=args.max_cycles,
    )
    bot.run()
    ks.stop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
