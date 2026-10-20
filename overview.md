# Screen Recorder Automation Bot - Complete Technical Overview

## 1. Executive Summary

A sophisticated Python-based automation system that orchestrates screen recording sessions with YouTube/browser activity. The system employs advanced human behavior emulation techniques to create natural, organic interaction patterns that are indistinguishable from genuine human activity.

**Core Mission**: Automate the cycle of starting screen recording, switching to browser content for ~2 minutes, then stopping the recording—while maintaining complete behavioral authenticity.

---

## 2. Technical Architecture

### 2.1 Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Runtime** | Python 3.9+ | Core execution environment |
| **GUI Automation** | PyAutoGUI | System-level window control & clicks |
| **Cursor Physics** | HumanCursor (SystemCursor) | Natural Bezier-based mouse movement |
| **Randomization** | random, numpy | Gaussian/stochastic timing variance |
| **Timing** | time, datetime | Precise delay management |
| **Window Management** | pygetwindow | Cross-platform window detection |
| **Logging** | logging | Activity tracking & debugging |
| **Configuration** | python-dotenv, yaml | Environment & behavior configs |

### 2.2 System Architecture Layers

```
┌─────────────────────────────────────────────────────────┐
│              Application Layer                          │
│  (Main Orchestrator, Session Manager, Loop Controller)  │
└─────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────────┐
│           Behavior Emulation Layer                      │
│  (Human Patterns, Fatigue Simulation, Micro-Actions)    │
└─────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────────┐
│          Interaction Layer                              │
│  (Cursor Controller, Click Handler, Window Manager)     │
└─────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────────┐
│            System Layer                                 │
│  (PyAutoGUI, HumanCursor, OS Window APIs)              │
└─────────────────────────────────────────────────────────┘
```

---

## 3. Core Features & Components

### 3.1 Natural Cursor Movement Engine

**Module**: `cursor_controller.py`

**Features**:
- **Bezier Curve Pathfinding**: Multi-control-point curves for organic trajectories
- **Dynamic Speed Profiling**: Accelerates from rest, cruises, decelerates to target
- **Overshoot Correction**: 15-25% probability of overshooting by 3-8 pixels, then correcting
- **Micro-Jitter**: Sub-pixel tremor simulation (±1-2px during hover)
- **Fatigue Indicators**: Gradually slower/less precise movements after 30+ minutes

**Technical Implementation**:
```python
- Calculate cubic Bezier path with 2-4 control points
- Sample path at 60-120 FPS for smooth rendering
- Apply easing functions (ease-in-out cubic)
- Add Perlin noise for natural deviation
- Implement overshoot with exponential decay correction
```

### 3.2 Stochastic Timing System

**Module**: `timing_engine.py`

**Features**:
- **Gaussian Distribution**: All delays use normal distribution (μ, σ)
- **Configurable Ranges**: Base values with ±10-15% variance
- **Anti-Pattern Detection**: Never repeats same timing twice consecutively
- **Chunked Delays**: Long waits split into multiple micro-checks

**Timing Profiles**:
| Action | Base Duration | Variance | Distribution |
|--------|--------------|----------|--------------|
| Click Registration | 0.3s | ±0.1s | Gaussian |
| Window Switch Wait | 1.5s | ±0.4s | Gaussian |
| Watch Duration | 120s | ±8s | Gaussian |
| Post-Click Pause | 0.5s | ±0.2s | Gaussian |
| Cooldown Period | 3.0s | ±1.0s | Gaussian |

### 3.3 Micro-Distraction System

**Module**: `human_behaviors.py`

**Features**:
- **Probability-Based Triggers**: 20-30% chance per evaluation window
- **Action Variety**: 5+ different micro-actions
- **Context Awareness**: Different behaviors for different phases

**Micro-Actions Catalog**:
1. **Idle Scroll** (35% probability): Small mouse wheel movement (1-3 ticks)
2. **Cursor Drift** (25%): Slow 10-30px movement in random direction
3. **Tab Focus Shift** (15%): Fake Alt+Tab (no actual switch)
4. **Micro-Pause** (15%): Complete stillness for 0.8-2.0 seconds
5. **Hand Readjustment** (10%): Slight cursor repositioning (5-15px)

**Evaluation Windows**: Every 25-35 seconds during watch phase

### 3.4 Session Fatigue & Bio-Breaks

**Module**: `session_manager.py`

**Features**:
- **Cycle Tracking**: Monitors completed loops
- **Fatigue Accumulation**: Performance degrades subtly over time
- **Scheduled Breaks**: Long pauses after 6-9 cycles

**Break System**:
```
Cycle Count: 1-5   → No break
Cycle Count: 6-9   → Trigger bio-break (probability increases)
Break Duration: 4-12 minutes (Gaussian: μ=8min, σ=2min)
Break Activities: 
  - Complete mouse/keyboard silence
  - OR minimal idle movements (5% chance per minute)
```

**Fatigue Indicators**:
- Slightly longer response times (+5-15%)
- Increased overshoot probability
- More frequent micro-pauses
- Occasional "missed" click (cursor moves away before clicking, then returns)

### 3.5 Window Management System

**Module**: `window_controller.py`

**Features**:
- **Robust Window Detection**: Finds recorder app by title/class
- **Fallback Mechanisms**: Multiple strategies for window switching
- **Position Validation**: Ensures windows are not minimized/hidden
- **Multi-Monitor Support**: Handles different screen configurations

**Window Switch Strategies**:
1. **Primary**: Alt+Tab with natural keystroke timing (50ms hold)
2. **Fallback 1**: Direct window activation via pygetwindow
3. **Fallback 2**: Click on taskbar icon position (if known)

### 3.6 Click Handler with Human Physics

**Module**: `click_handler.py`

**Features**:
- **Pre-Click Hover**: 200-600ms hover before click
- **Click Duration Variance**: Mouse down for 80-150ms
- **Post-Click Stillness**: 100-300ms motionless after release
- **Double-Click Accidents**: 2-3% chance of unintended double-click (immediately corrected)

**Click Sequence**:
```
1. Move cursor to target (Bezier path)
2. Optional overshoot correction
3. Hover for random duration
4. Press mouse button (random duration)
5. Release mouse button
6. Stay still momentarily
7. Move away naturally (not instantly)
```

---

## 4. Application Flow & State Machine

### 4.1 Main Loop State Diagram

```
     ┌─────────────┐
     │  IDLE/START │
     └──────┬──────┘
            │
            ▼
     ┌─────────────────┐
     │ LOCATE_RECORDER │ ───────► [Error: Retry 3x]
     └──────┬──────────┘
            │
            ▼
     ┌──────────────────┐
     │ MOVE_TO_START_BTN│
     └──────┬───────────┘
            │
            ▼
     ┌──────────────┐
     │ CLICK_START  │
     └──────┬───────┘
            │
            ▼
     ┌────────────────┐
     │ SWITCH_BROWSER │
     └──────┬─────────┘
            │
            ▼
     ┌────────────────────────┐
     │ WATCH_WITH_DISTRACTIONS│ (120s ± variance)
     │  ├─ Micro-action checks │
     │  └─ Chunked 10s intervals│
     └──────┬─────────────────┘
            │
            ▼
     ┌─────────────────┐
     │ SWITCH_RECORDER │
     └──────┬──────────┘
            │
            ▼
     ┌──────────────────┐
     │ MOVE_TO_STOP_BTN │
     └──────┬───────────┘
            │
            ▼
     ┌──────────────┐
     │ CLICK_STOP   │
     └──────┬───────┘
            │
            ▼
     ┌──────────────┐
     │ COOLDOWN     │ (3s ± variance)
     └──────┬───────┘
            │
            ▼
     ┌─────────────────┐
     │ CHECK_BIO_BREAK │ ───Yes──► [Break 4-12min]
     └──────┬──────────┘              │
            │ No                       │
            └──────────────────────────┘
            │
            └──────► [Loop back to LOCATE_RECORDER]
```

### 4.2 Error Recovery & Resilience

**Features**:
- **Window Not Found**: Retry 3x with exponential backoff (2s, 4s, 8s)
- **Button Position Lost**: Re-calibration mode (user prompt or saved fallback)
- **Unexpected Window State**: Graceful degradation to manual override
- **System Interruption**: Graceful shutdown, save state, resume capability

---

## 5. Configuration System

### 5.1 Configuration Files

**`.env`** - Sensitive/user-specific settings:
```env
RECORDER_APP_TITLE=OBS Studio
BROWSER_WINDOW_TITLE=YouTube - Mozilla Firefox
START_BUTTON_X=100
START_BUTTON_Y=200
STOP_BUTTON_X=150
STOP_BUTTON_Y=200
```

**`config.yaml`** - Behavior parameters:
```yaml
timing:
  watch_duration_mean: 120  # seconds
  watch_duration_std: 8
  cooldown_mean: 3
  cooldown_std: 1
  
behavior:
  overshoot_probability: 0.20
  micro_distraction_probability: 0.25
  bio_break_after_cycles: [6, 9]  # random between
  bio_break_duration: [240, 720]  # 4-12 minutes in seconds
  
cursor:
  speed_multiplier: 1.0  # 0.5 = slow, 2.0 = fast
  bezier_control_points: 3
  jitter_amplitude: 1.5  # pixels
  
fatigue:
  enabled: true
  start_after_minutes: 30
  max_performance_degradation: 0.15  # 15% slower
```

### 5.2 Calibration Module

**Module**: `calibrator.py`

**Features**:
- **Interactive Setup**: Guided button position recording
- **Screenshot Capture**: Saves button images for template matching
- **Multi-Profile Support**: Different recorder apps/layouts
- **Validation**: Test run before saving configuration

**Calibration Process**:
```
1. Launch calibration mode
2. User positions cursor on START button → Press 'S' to save
3. User positions cursor on STOP button → Press 'P' to save
4. System captures screenshots (optional template matching)
5. System performs test run (dry run without clicking)
6. Save to .env file
```

---

## 6. Logging & Monitoring

### 6.1 Logging System

**Module**: `logger_config.py`

**Log Levels**:
- **DEBUG**: Cursor coordinates, timing values, state transitions
- **INFO**: Cycle completions, window switches, break events
- **WARNING**: Retry attempts, fallback activations
- **ERROR**: Critical failures, recovery attempts

**Log Outputs**:
- **Console**: INFO and above (colorized)
- **File**: `logs/bot_YYYYMMDD.log` (DEBUG and above, rotated daily)
- **Statistics**: `logs/stats.json` (cycle metrics, success rates)

### 6.2 Statistics Tracking

**Metrics Collected**:
```json
{
  "session_id": "uuid",
  "start_time": "ISO timestamp",
  "cycles_completed": 42,
  "cycles_failed": 1,
  "total_watch_time": 5040,  // seconds
  "bio_breaks_taken": 5,
  "average_cycle_duration": 126.3,
  "cursor_movement_stats": {
    "total_distance_pixels": 384720,
    "average_speed": 425.3,
    "overshoot_events": 8
  },
  "errors": []
}
```

---

## 7. Safety & Kill Switch Mechanisms

### 7.1 Emergency Stop Features

**Implementation**:
1. **Keyboard Kill Switch**: Press `Ctrl+Shift+Q` anytime to gracefully stop
2. **Mouse Corner Panic**: Move mouse to top-left corner (0,0) for 2 seconds
3. **Scheduled Auto-Stop**: Max runtime limit (default: 4 hours)
4. **CPU/Memory Safeguards**: Auto-pause if system resources exceed 90%

### 7.2 Dry Run Mode

**Module**: `dry_run.py`

**Features**:
- Executes entire loop WITHOUT actual clicks
- Shows visual overlay of where clicks would occur
- Logs all timing values and decisions
- Validates configuration before production run

**Usage**: `python main.py --dry-run`

---

## 8. Advanced Features (Phase 2+)

### 8.1 Machine Learning Enhancements

**Future Modules**:
- **Pattern Learning**: Analyze user's real mouse data, train custom behavior model
- **Anomaly Detection**: Self-monitor for robotic patterns, auto-adjust
- **Adaptive Timing**: Learn optimal watch durations based on content type

### 8.2 Multi-Session Orchestration

**Features**:
- Run multiple independent bot instances (different profiles)
- Distributed timing (no synchronized behavior across instances)
- Shared resource locking (only one instance controls mouse at a time)

### 8.3 Visual Recognition Fallback

**Module**: `visual_matcher.py`

**Features**:
- Template matching for button detection (OpenCV)
- OCR for text-based button finding (Tesseract)
- Color-based region detection
- Fallback when coordinate-based approach fails

---

## 9. Testing & Quality Assurance

### 9.1 Test Suite Components

**Unit Tests** (`tests/unit/`):
- Timing distribution validation
- Bezier curve generation correctness
- Configuration parsing
- State machine transitions

**Integration Tests** (`tests/integration/`):
- Window detection across OS
- Cursor movement accuracy
- Full cycle execution (mocked clicks)
- Error recovery scenarios

**Behavioral Tests** (`tests/behavioral/`):
- Statistical analysis of generated timings (chi-squared test)
- Cursor path randomness validation
- Anti-pattern detection (no repetition)

### 9.2 Quality Metrics

**Acceptance Criteria**:
- ✅ No identical timing sequences in 100 cycles
- ✅ Cursor movement passes human-likeness score >0.85
- ✅ Zero crashes in 8-hour continuous run
- ✅ Successful recovery from 95%+ of errors
- ✅ Bio-breaks occur within expected frequency range

---

## 10. Deployment & Production Readiness

### 10.1 Prerequisites

**System Requirements**:
- Python 3.9 or higher
- Operating System: Windows 10+, macOS 11+, or Linux (X11/Wayland)
- RAM: Minimum 256MB available
- Screen Resolution: 1280x720 or higher
- Recording Software: OBS, ScreenFlow, or similar

**Permission Requirements**:
- Accessibility permissions (macOS)
- Input monitoring permissions (macOS)
- Administrator rights (Windows, for PyAutoGUI)

### 10.2 Installation Steps

```bash
# 1. Clone/download project
cd /path/to/project

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run calibration
python calibrate.py

# 5. Test with dry run
python main.py --dry-run

# 6. Start production run
python main.py
```

### 10.3 Production Checklist

- [ ] Calibration completed and validated
- [ ] Config files reviewed and customized
- [ ] Dry run executed successfully (3+ cycles)
- [ ] Kill switch tested and understood
- [ ] Log rotation configured
- [ ] System resources monitored (baseline check)
- [ ] Backup/recovery strategy defined
- [ ] User understands ethical/legal implications

---

## 11. Ethical Considerations & Disclaimers

### 11.1 Intended Use Cases

**Legitimate Applications**:
- **Quality Assurance Testing**: Automated testing of screen recording software
- **Performance Benchmarking**: Measuring system resource usage during recording
- **Workflow Optimization**: Researching optimal recording session patterns
- **Educational Purposes**: Learning automation and human behavior modeling

### 11.2 Prohibited Use Cases

**NOT for**:
- Artificially inflating view counts or metrics
- Circumventing time-tracking or monitoring systems
- Generating fraudulent activity logs
- Any activity that violates terms of service of platforms

### 11.3 Legal Compliance

Users are responsible for:
- Compliance with local laws regarding automation
- Respecting software terms of service
- Ensuring use does not violate workplace policies
- Understanding applicable fraud/deception statutes

**Developer Liability**: This software is provided "as-is" for educational and research purposes.

---

## 12. Project Roadmap

### Phase 1: Core Foundation (Current)
- ✅ Basic loop architecture
- ✅ Bezier cursor movement
- ✅ Stochastic timing
- ✅ Configuration system

### Phase 2: Human Behavior (In Progress)
- 🔄 Micro-distractions
- 🔄 Fatigue simulation
- 🔄 Bio-breaks
- 🔄 Overshoot correction

### Phase 3: Robustness
- ⏳ Visual recognition fallback
- ⏳ Multi-monitor support
- ⏳ Advanced error recovery
- ⏳ Session persistence

### Phase 4: Intelligence
- ⏳ ML-based behavior learning
- ⏳ Adaptive timing optimization
- ⏳ Self-monitoring anomaly detection
- ⏳ Multi-instance orchestration

---

## 13. Technical Debt & Known Limitations

### Current Limitations

1. **Platform Dependency**: HumanCursor may have OS-specific quirks
2. **Fixed Button Positions**: Requires recalibration if UI layout changes
3. **Single-Monitor Optimization**: Multi-monitor support is basic
4. **No Visual Verification**: Assumes buttons remain visible/clickable
5. **Language Locked**: Currently English-only for window titles

### Future Improvements

- Dynamic button detection (computer vision)
- Cross-language window title matching
- Headless/background operation mode
- Cloud-based configuration sync
- Web dashboard for remote monitoring

---

## 14. Support & Maintenance

### Troubleshooting Resources

**Common Issues**:
1. **"Window not found"** → Check recorder app title in `.env`
2. **Cursor not moving** → Verify accessibility permissions
3. **Clicks not registering** → Increase `click_duration` in config
4. **Timing feels robotic** → Increase `std` values in timing config

### Debugging Mode

```bash
# Enable verbose logging
python main.py --debug

# Enable visual overlay (shows cursor targets)
python main.py --visual-debug

# Run single cycle only
python main.py --single-cycle
```

### Version History

- **v0.1.0** - Initial architecture and basic loop
- **v0.2.0** - Bezier cursor + stochastic timing
- **v0.3.0** - Micro-distractions + bio-breaks (current)
- **v1.0.0** - Production-ready with full test coverage (target)

---

## 15. Conclusion

This system represents a sophisticated blend of automation engineering and behavioral psychology. By implementing multiple layers of randomization, natural movement physics, and human fatigue patterns, it creates an interaction profile that is statistically indistinguishable from genuine human activity.

**Key Success Factors**:
1. **No Fixed Patterns**: Every execution is unique
2. **Behavioral Depth**: Multiple simultaneous humanization layers
3. **Graceful Degradation**: Robust error handling
4. **Configurability**: Adaptable to different use cases
5. **Observability**: Comprehensive logging and monitoring

**Final Notes**:
- This is a **research and educational tool** demonstrating advanced automation techniques
- Users bear full responsibility for ethical and legal use
- The system prioritizes quality over speed (natural > fast)
- Continuous improvement through statistical validation and testing

---

**Document Version**: 1.0  
**Last Updated**: 2026-10-19  
**Author**: Senior Software Engineering Team  
**Status**: Technical Specification - Ready for Implementation
