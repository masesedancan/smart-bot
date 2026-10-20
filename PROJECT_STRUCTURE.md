# Bot Project - Complete Folder Structure

```
Bot/
├── .env.example                      # Environment variables template
├── .env                             # Actual environment (gitignored)
├── .gitignore                       # Git ignore rules
├── README.md                        # User-facing documentation
├── overview.md                      # Technical specification (this doc reference)
├── requirements.txt                 # Python dependencies
├── setup.py                         # Package installation script
├── config.yaml                      # Behavior configuration
│
├── main.py                          # Application entry point
├── calibrate.py                     # Interactive calibration tool
│
├── src/                            # Source code directory
│   ├── __init__.py
│   │
│   ├── core/                       # Core application logic
│   │   ├── __init__.py
│   │   ├── orchestrator.py         # Main loop controller
│   │   ├── state_machine.py        # State management
│   │   └── session_manager.py      # Cycle tracking, bio-breaks
│   │
│   ├── interaction/                # System interaction layer
│   │   ├── __init__.py
│   │   ├── cursor_controller.py    # Bezier movement, overshoot
│   │   ├── click_handler.py        # Human-like clicking
│   │   ├── window_controller.py    # Window detection & switching
│   │   └── keyboard_controller.py  # Keystroke simulation
│   │
│   ├── behavior/                   # Human emulation layer
│   │   ├── __init__.py
│   │   ├── timing_engine.py        # Stochastic delays
│   │   ├── human_behaviors.py      # Micro-distractions
│   │   ├── fatigue_simulator.py    # Performance degradation
│   │   └── randomness_utils.py     # Distribution helpers
│   │
│   ├── config/                     # Configuration management
│   │   ├── __init__.py
│   │   ├── config_loader.py        # YAML + .env parser
│   │   ├── validator.py            # Config validation
│   │   └── defaults.py             # Default values
│   │
│   ├── monitoring/                 # Logging & stats
│   │   ├── __init__.py
│   │   ├── logger_config.py        # Logging setup
│   │   ├── stats_tracker.py        # Metrics collection
│   │   └── performance_monitor.py  # System resource tracking
│   │
│   ├── safety/                     # Safety mechanisms
│   │   ├── __init__.py
│   │   ├── kill_switch.py          # Emergency stop handlers
│   │   ├── error_recovery.py       # Retry & fallback logic
│   │   └── resource_guard.py       # CPU/memory safeguards
│   │
│   └── utils/                      # Utility functions
│       ├── __init__.py
│       ├── screen_utils.py         # Screen resolution, scaling
│       ├── path_utils.py           # File path helpers
│       └── validation_utils.py     # Input validation
│
├── tests/                          # Test suite
│   ├── __init__.py
│   ├── conftest.py                 # Pytest configuration
│   │
│   ├── unit/                       # Unit tests
│   │   ├── __init__.py
│   │   ├── test_timing_engine.py
│   │   ├── test_cursor_controller.py
│   │   ├── test_state_machine.py
│   │   └── test_config_loader.py
│   │
│   ├── integration/                # Integration tests
│   │   ├── __init__.py
│   │   ├── test_window_detection.py
│   │   ├── test_full_cycle.py
│   │   └── test_error_recovery.py
│   │
│   ├── behavioral/                 # Behavioral validation
│   │   ├── __init__.py
│   │   ├── test_randomness.py      # Statistical tests
│   │   └── test_human_likeness.py  # Pattern detection
│   │
│   └── fixtures/                   # Test data
│       ├── mock_config.yaml
│       └── sample_screenshots/
│
├── logs/                           # Log files (gitignored)
│   ├── bot_YYYYMMDD.log
│   └── stats.json
│
├── docs/                           # Additional documentation
│   ├── INSTALLATION.md
│   ├── CALIBRATION.md
│   ├── TROUBLESHOOTING.md
│   ├── API_REFERENCE.md
│   └── CONTRIBUTING.md
│
├── scripts/                        # Utility scripts
│   ├── analyze_logs.py             # Log analysis tool
│   ├── visualize_stats.py          # Stats visualization
│   └── generate_report.py          # Session report generator
│
└── data/                          # Runtime data (gitignored)
    ├── calibration/               # Saved button positions
    │   └── profiles/
    │       └── default.json
    ├── screenshots/               # Template images
    │   ├── start_button.png
    │   └── stop_button.png
    └── sessions/                  # Session state persistence
        └── session_YYYYMMDD_HHMMSS.json
```

## Key Files Description

### Root Level

| File | Purpose |
|------|---------|
| `main.py` | CLI entry point, argument parsing, execution start |
| `calibrate.py` | Interactive tool to set up button positions |
| `requirements.txt` | All Python package dependencies |
| `config.yaml` | Tunable behavior parameters (timing, probabilities) |
| `.env` | Environment-specific settings (window titles, coordinates) |

### Core Modules

| Module | Responsibility |
|--------|---------------|
| `orchestrator.py` | Coordinates entire loop execution |
| `state_machine.py` | Manages state transitions (IDLE → RECORDING → WATCHING, etc.) |
| `session_manager.py` | Tracks cycles, determines bio-break scheduling |

### Interaction Modules

| Module | Responsibility |
|--------|---------------|
| `cursor_controller.py` | Bezier curves, overshoot, jitter, natural movement |
| `click_handler.py` | Press/release timing, hover, post-click pause |
| `window_controller.py` | Find windows, Alt+Tab, focus verification |

### Behavior Modules

| Module | Responsibility |
|--------|---------------|
| `timing_engine.py` | Gaussian distributions for all delays |
| `human_behaviors.py` | Micro-scrolls, cursor drift, idle pauses |
| `fatigue_simulator.py` | Gradual performance degradation over time |

### Configuration Modules

| Module | Responsibility |
|--------|---------------|
| `config_loader.py` | Load and merge YAML + .env files |
| `validator.py` | Validate config values (ranges, types) |
| `defaults.py` | Fallback values if config missing |

### Monitoring Modules

| Module | Responsibility |
|--------|---------------|
| `logger_config.py` | Set up file/console logging with rotation |
| `stats_tracker.py` | Collect metrics (cycle times, distances, errors) |
| `performance_monitor.py` | Track CPU/RAM usage, trigger safeguards |

### Safety Modules

| Module | Responsibility |
|--------|---------------|
| `kill_switch.py` | Keyboard listener (Ctrl+Shift+Q), mouse corner detection |
| `error_recovery.py` | Retry logic, exponential backoff, fallback strategies |
| `resource_guard.py` | Pause execution if system resources critical |

---

## Module Dependencies Graph

```
main.py
  └─→ orchestrator.py
       ├─→ state_machine.py
       ├─→ session_manager.py
       │    └─→ timing_engine.py
       ├─→ cursor_controller.py
       │    ├─→ human_behaviors.py
       │    └─→ randomness_utils.py
       ├─→ click_handler.py
       │    └─→ timing_engine.py
       ├─→ window_controller.py
       ├─→ logger_config.py
       ├─→ stats_tracker.py
       ├─→ kill_switch.py
       └─→ error_recovery.py
```

---

## Data Flow

```
[User] → calibrate.py → data/calibration/profiles/default.json
                      → data/screenshots/*.png

[User] → main.py → config_loader.py → config.yaml + .env
                → orchestrator.py
                   ├─→ [State Transitions]
                   ├─→ [Cursor Movements] → PyAutoGUI
                   ├─→ [Window Switches] → pygetwindow
                   └─→ [Logging] → logs/bot_YYYYMMDD.log
                                → logs/stats.json
```

---

## Endpoint Summary (No HTTP APIs - This is Desktop Automation)

This application does **not** expose HTTP/REST endpoints. It's a desktop automation tool that interacts with:

1. **PyAutoGUI API**: Mouse movement, clicks, keyboard
2. **pygetwindow API**: Window enumeration, focus
3. **HumanCursor API**: Natural cursor path generation
4. **OS APIs**: Window management (Alt+Tab, focus)

### Internal "Endpoints" (Module Public Functions)

#### cursor_controller.py
- `move_to(x, y, overshoot=True)` → Move cursor naturally
- `get_current_position()` → Return (x, y)
- `apply_jitter()` → Add micro-tremor

#### click_handler.py
- `click_at(x, y, button='left')` → Perform human-like click
- `hover(x, y, duration=None)` → Hover before action
- `double_click_accident()` → Simulate mistake

#### window_controller.py
- `find_window(title)` → Return window object or None
- `switch_to_window(window)` → Activate window
- `alt_tab()` → Simulate Alt+Tab keypress

#### timing_engine.py
- `get_delay(base, std)` → Return Gaussian-distributed delay
- `chunked_wait(duration, check_interval)` → Long wait with checks

#### session_manager.py
- `increment_cycle()` → Track completed cycle
- `should_take_bio_break()` → Return True/False
- `execute_bio_break()` → Pause for 4-12 minutes

#### state_machine.py
- `transition_to(new_state)` → Change state with validation
- `get_current_state()` → Return current state enum
- `can_transition(from_state, to_state)` → Validate transition

---

## Configuration Schema

### config.yaml
```yaml
timing:
  watch_duration_mean: 120
  watch_duration_std: 8
  cooldown_mean: 3
  cooldown_std: 1
  click_duration_mean: 0.1
  click_duration_std: 0.03
  hover_duration_mean: 0.4
  hover_duration_std: 0.15

behavior:
  overshoot_probability: 0.20
  overshoot_distance_min: 3
  overshoot_distance_max: 8
  micro_distraction_probability: 0.25
  micro_distraction_interval: 30
  bio_break_after_cycles_min: 6
  bio_break_after_cycles_max: 9
  bio_break_duration_min: 240
  bio_break_duration_max: 720

cursor:
  speed_multiplier: 1.0
  bezier_control_points: 3
  jitter_amplitude: 1.5
  jitter_frequency: 0.1

fatigue:
  enabled: true
  start_after_minutes: 30
  max_performance_degradation: 0.15
  gradual_onset: true

safety:
  max_runtime_hours: 4
  cpu_threshold_percent: 90
  memory_threshold_percent: 90
  auto_stop_on_threshold: true

logging:
  level: INFO
  console_output: true
  file_output: true
  rotate_daily: true
  keep_logs_days: 7
```

### .env
```env
# Window Identifiers
RECORDER_APP_TITLE=OBS Studio
BROWSER_WINDOW_TITLE=YouTube - Mozilla Firefox

# Button Coordinates (from calibration)
START_BUTTON_X=100
START_BUTTON_Y=200
STOP_BUTTON_X=150
STOP_BUTTON_Y=200

# Optional: Advanced settings
SCREEN_WIDTH=1920
SCREEN_HEIGHT=1080
DPI_SCALE=1.0
```

---

## Build & Deployment Commands

```bash
# Development Setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run Calibration
python calibrate.py

# Dry Run (no actual clicks)
python main.py --dry-run

# Production Run
python main.py

# Debug Mode
python main.py --debug --visual-debug

# Single Cycle Test
python main.py --single-cycle

# With Custom Config
python main.py --config custom_config.yaml

# Run Tests
pytest tests/
pytest tests/unit/
pytest tests/behavioral/ -v

# Generate Coverage Report
pytest --cov=src --cov-report=html

# Analyze Logs
python scripts/analyze_logs.py logs/bot_20261019.log

# Visualize Statistics
python scripts/visualize_stats.py logs/stats.json
```

---

This structure provides complete separation of concerns, testability, and scalability for production deployment.
