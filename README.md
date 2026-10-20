# Screen Recorder Automation Bot 🤖

A sophisticated Python automation system that orchestrates screen recording sessions with browser activity while maintaining **human-like interaction patterns** that are indistinguishable from genuine user behavior.

## 🎯 What Does It Do?

The bot automates this cycle:
1. **Start** your screen recording software
2. **Switch** to a browser window (e.g., YouTube)
3. **Watch** content for ~2 minutes with natural behavior
4. **Switch** back to the recorder
5. **Stop** the recording
6. **Repeat** with organic breaks

## ✨ Key Features

### 🖱️ Natural Cursor Movement
- **Bezier curves** instead of straight lines
- **Overshoot correction** (moves past target, then corrects)
- **Micro-jitter** simulation (sub-pixel tremors)
- **Variable speed** with acceleration/deceleration

### ⏱️ Stochastic Timing
- **Gaussian distributions** for all delays (no fixed timings)
- **2-minute watch time** with ±8 second natural variance
- **Chunked waits** with periodic micro-activity checks

### 🎭 Human Behaviors
- **Micro-distractions**: Random scrolls, cursor drifts, idle pauses
- **Fatigue simulation**: Gradually slower/less precise after 30+ minutes
- **Bio-breaks**: 4-12 minute pauses after 6-9 cycles (like grabbing water)
- **Session variance**: Every execution is statistically unique

### 🛡️ Safety Features
- **Emergency kill switch**: `Ctrl+Shift+Q` or mouse corner panic
- **Resource monitoring**: Auto-pause if CPU/RAM exceeds 90%
- **Graceful shutdown**: Never leaves system in inconsistent state
- **Dry-run mode**: Test without actual clicks

## 📋 Requirements

- **Python 3.9+**
- **Operating System**: Windows 10+, macOS 11+, or Linux (X11/Wayland)
- **Screen Recorder**: OBS, ScreenFlow, Camtasia, or similar
- **Browser**: Any modern browser (Chrome, Firefox, Safari, Edge)
- **Permissions**: 
  - Accessibility permissions (macOS)
  - Input monitoring (macOS)
  - Administrator rights (Windows - for PyAutoGUI)

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or download the project
cd Bot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Calibration

```bash
# Run interactive calibration tool
python calibrate.py
```

Follow the prompts to:
- Enter your recorder app window title
- Enter your browser window title  
- Position cursor on START button and press `S`
- Position cursor on STOP button and press `P`

This creates `.env` with your button coordinates.

### 3. Configuration (Optional)

Edit `config.yaml` to tune behavior:
- Timing variances
- Overshoot probability
- Micro-distraction frequency
- Bio-break scheduling
- Fatigue simulation

### 4. Test Run

```bash
# Dry run (no actual clicks - safe testing)
python main.py --dry-run

# Single cycle test
python main.py --single-cycle --dry-run
```

### 5. Production Run

```bash
# Start the bot
python main.py

# With debug logging
python main.py --debug

# Limit to 10 cycles
python main.py --max-cycles 10
```

## 📁 Project Structure

```
Bot/
├── main.py                  # Entry point
├── calibrate.py             # Setup tool
├── config.yaml              # Behavior configuration
├── .env                     # Environment variables (your setup)
├── requirements.txt         # Python dependencies
│
├── src/
│   ├── core/               # Main orchestration logic
│   ├── interaction/        # Cursor, clicks, windows
│   ├── behavior/           # Human emulation patterns
│   ├── config/             # Configuration management
│   ├── monitoring/         # Logging & statistics
│   ├── safety/             # Kill switches & safeguards
│   └── utils/              # Helper functions
│
├── tests/                  # Test suite
│   ├── unit/              # Unit tests
│   ├── integration/       # Integration tests
│   └── behavioral/        # Statistical validation
│
├── logs/                  # Runtime logs (auto-generated)
├── data/                  # Calibration data & screenshots
└── docs/                  # Additional documentation
```

## 🎮 Usage Examples

```bash
# Normal operation
python main.py

# Dry run (test mode - no clicks)
python main.py --dry-run

# Debug mode (verbose logging)
python main.py --debug

# Visual debugging (shows cursor targets)
python main.py --visual-debug

# Single cycle test
python main.py --single-cycle

# Disable bio-breaks
python main.py --no-bio-breaks

# Limit cycles
python main.py --max-cycles 20

# Custom config file
python main.py --config custom_config.yaml
```

## 🛑 Emergency Stop

**Three ways to stop the bot immediately:**

1. **Keyboard**: Press `Ctrl+Shift+Q` at any time
2. **Mouse**: Move cursor to top-left corner (0,0) and hold for 2 seconds
3. **Terminal**: Press `Ctrl+C` in the terminal

## 📊 Monitoring

### Logs

Logs are saved to `logs/bot_YYYYMMDD.log`:
- **INFO**: Cycle completions, window switches, bio-breaks
- **WARNING**: Retry attempts, fallback activations
- **ERROR**: Failures and recovery attempts
- **DEBUG**: Detailed cursor positions and timing values

### Statistics

Session statistics saved to `logs/stats.json`:
```json
{
  "cycles_completed": 42,
  "total_watch_time": 5040,
  "bio_breaks_taken": 5,
  "average_cycle_duration": 126.3,
  "cursor_movement_stats": {...}
}
```

## 🔧 Troubleshooting

### "Window not found"
→ Check recorder app title in `.env` matches exactly  
→ Ensure app is running and visible on screen

### "Cursor not moving"
→ Verify accessibility permissions (macOS)  
→ Run terminal as administrator (Windows)

### "Clicks not registering"
→ Increase `click_duration_mean` in `config.yaml`  
→ Re-run calibration to verify button positions

### "Behavior feels robotic"
→ Increase `std` (standard deviation) values in timing config  
→ Enable fatigue simulation  
→ Increase micro-distraction probability

## ⚙️ Configuration Deep Dive

### Key Config Parameters

**Timing** (`config.yaml`):
```yaml
timing:
  watch_duration_mean: 120    # 2 minutes avg
  watch_duration_std: 8       # ±8 sec variance
```

**Behavior**:
```yaml
behavior:
  overshoot_probability: 0.20        # 20% chance
  micro_distraction_probability: 0.25  # 25% chance
  bio_break_after_cycles_min: 6      # Break after 6-9 cycles
```

**Cursor**:
```yaml
cursor:
  speed_multiplier: 1.0      # 0.5=slow, 2.0=fast
  jitter_amplitude: 1.5      # pixels
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Unit tests only
pytest tests/unit/

# With coverage report
pytest --cov=src --cov-report=html

# Behavioral validation (statistical tests)
pytest tests/behavioral/ -v
```

## 📚 Documentation

- **[overview.md](overview.md)** - Complete technical specification
- **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** - Detailed folder structure
- **docs/INSTALLATION.md** - Detailed setup guide
- **docs/TROUBLESHOOTING.md** - Common issues and solutions
- **docs/API_REFERENCE.md** - Module API documentation

## ⚖️ Ethical Use & Disclaimer

### ✅ Intended For
- **Quality assurance testing** of screen recording software
- **Performance benchmarking** of recording sessions
- **Workflow research** and optimization studies
- **Educational purposes** in automation and behavioral modeling

### ❌ NOT For
- Artificially inflating view counts or metrics
- Circumventing time-tracking or monitoring systems
- Generating fraudulent activity logs
- Violating platform terms of service

### Legal Compliance

**You are responsible for:**
- Compliance with local laws regarding automation
- Respecting software terms of service
- Ensuring use does not violate workplace policies
- Understanding applicable fraud/deception statutes

**This software is provided "as-is" for educational and research purposes.**

## 🗺️ Roadmap

- [x] Core loop architecture
- [x] Bezier cursor movement
- [x] Stochastic timing engine
- [x] Configuration system
- [ ] Micro-distractions (in progress)
- [ ] Fatigue simulation (in progress)
- [ ] Visual recognition fallback
- [ ] ML-based behavior learning
- [ ] Multi-instance orchestration

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is provided for educational and research purposes.  
Users bear full responsibility for ethical and legal compliance.

## 📧 Support

For issues, questions, or feature requests:
- Open an issue on the repository
- Check docs/TROUBLESHOOTING.md
- Review logs/bot_*.log for errors

---

**Version**: 0.3.0  
**Status**: Development - Phase 2 (Human Behavior Implementation)  
**Last Updated**: October 2026

**Built with ❤️ by the Engineering Team**
