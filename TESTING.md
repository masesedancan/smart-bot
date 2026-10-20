# Testing Guide

## Quick Test Commands

### 1. Environment Test
```bash
# Verify Python version and dependencies
python --version  # Should be 3.9+
pip list | grep -E "(pyautogui|numpy|pynput)"
```

### 2. Configuration Test
```bash
# Load config without errors
python -c "from src.config.config_loader import load_config; print('✓ Config loaded')"
```

### 3. Module Import Test
```bash
# Test all core imports
python -c "
from src.core.orchestrator import Orchestrator
from src.core.state_machine import StateMachine
from src.behavior.timing_engine import TimingEngine
from src.interaction.cursor_controller import CursorController
print('✓ All modules import successfully')
"
```

### 4. Logging Test
```bash
# Test logging system
python -c "
from src.monitoring.logger_config import setup_logging
logger = setup_logging('INFO')
logger.info('Test log message')
print('✓ Logging works')
"
```

### 5. Timing Engine Test
```bash
# Test random timing generation
python -c "
from src.behavior.timing_engine import TimingEngine, TimingConfig
engine = TimingEngine(TimingConfig())
print(f'Watch duration: {engine.get_watch_duration():.2f}s')
print(f'Cooldown: {engine.get_cooldown_duration():.2f}s')
print('✓ Timing engine works')
"
```

### 6. Statistics Test
```bash
# Test stats tracking
python -c "
from src.monitoring.stats_tracker import StatsTracker
tracker = StatsTracker()
tracker.start_cycle()
tracker.end_cycle(success=True, watch_duration=120.0)
print('✓ Statistics tracking works')
"
```

## Full Integration Tests

### Test 1: Dry Run Single Cycle
```bash
# Complete test without actual clicks
python main.py --dry-run --single-cycle --debug

# Expected output:
# - No errors
# - State transitions logged
# - [DRY RUN] messages for clicks
# - Cycle completion message
```

### Test 2: Configuration Validation
```bash
# Test with invalid config
python main.py --dry-run --config nonexistent.yaml

# Expected: Error message about missing file
```

### Test 3: Kill Switch Test
```bash
# Start bot and press Ctrl+Shift+Q
python main.py --dry-run

# Expected: Graceful shutdown message
```

### Test 4: Resource Monitoring
```bash
# Monitor system resources during execution
python -c "
from src.monitoring.performance_monitor import PerformanceMonitor
monitor = PerformanceMonitor()
usage = monitor.get_resource_usage()
print(f'CPU: {usage.cpu_percent}%')
print(f'Memory: {usage.memory_percent}%')
"
```

## Manual Testing Checklist

### Before First Run
- [ ] `.env` file exists (run `calibrate.py`)
- [ ] Recorder app is running
- [ ] Browser window is open
- [ ] Virtual environment activated
- [ ] All dependencies installed

### During Dry Run
- [ ] Cursor moves smoothly
- [ ] No Python errors
- [ ] Logs show state transitions
- [ ] [DRY RUN] messages appear for clicks
- [ ] Stats.json file created

### During Real Run
- [ ] START button gets clicked
- [ ] Window switches to browser
- [ ] Waits for ~2 minutes
- [ ] Micro-actions occur (check logs)
- [ ] Switches back to recorder
- [ ] STOP button gets clicked
- [ ] Cycle completes successfully

### After Multiple Cycles
- [ ] Timing values vary (check logs)
- [ ] No identical delays repeated
- [ ] Bio-break occurs after 6-9 cycles
- [ ] Statistics accurately tracked
- [ ] No memory leaks (check `htop`)

## Troubleshooting Tests

### If cursor doesn't move:
```bash
# Test PyAutoGUI
python -c "import pyautogui; pyautogui.moveTo(100, 100, duration=1)"
```

### If window switching fails:
```bash
# Test pygetwindow
python -c "
import pygetwindow as gw
windows = gw.getAllWindows()
for w in windows:
    print(w.title)
"
```

### If keyboard events fail:
```bash
# Test pynput
python -c "
from pynput import keyboard
def on_press(key):
    print(f'Key pressed: {key}')
    return False
listener = keyboard.Listener(on_press=on_press)
listener.start()
listener.join()
"
# Press any key to test
```

## Performance Benchmarks

### Expected Performance
```bash
# Run performance test
python -c "
import time
from src.interaction.cursor_controller import CursorController

controller = CursorController({'speed_multiplier': 1.0, 'bezier_control_points': 3, 'movement_fps': 60, 'jitter_amplitude': 1.5, 'jitter_frequency': 0.1})

start = time.time()
controller.move_to(500, 500)
elapsed = time.time() - start

print(f'Movement time: {elapsed:.2f}s')
print(f'Should be: 0.5-2.0s depending on distance')
"
```

### Expected Cycle Time
- Minimum: ~125 seconds (2 min watch + overhead)
- Average: ~135 seconds
- Maximum: ~150 seconds (with longer watch time)

## Automated Test Suite (Future)

### Unit Tests Structure
```
tests/
├── unit/
│   ├── test_timing_engine.py
│   ├── test_cursor_controller.py
│   ├── test_state_machine.py
│   └── test_config_loader.py
├── integration/
│   ├── test_full_cycle.py
│   └── test_window_switching.py
└── behavioral/
    ├── test_timing_distribution.py
    └── test_randomness.py
```

### Run Tests (when implemented)
```bash
# All tests
pytest tests/

# Unit tests only
pytest tests/unit/

# With coverage
pytest --cov=src --cov-report=html
```

## Success Criteria

### The system passes all tests when:
1. ✅ All modules import without errors
2. ✅ Configuration loads and validates correctly
3. ✅ Dry run completes without exceptions
4. ✅ Cursor moves naturally (Bezier curves visible)
5. ✅ Timing values show variance (no repetition)
6. ✅ Statistics file generated correctly
7. ✅ Kill switch stops execution immediately
8. ✅ Resource usage stays below thresholds
9. ✅ No memory leaks after 10+ cycles
10. ✅ Logs are clean and informative
