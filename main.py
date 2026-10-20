#!/usr/bin/env python3
"""
Screen Recorder Automation Bot - Main Entry Point

A sophisticated automation system that orchestrates screen recording sessions
with browser activity while maintaining human-like interaction patterns.

Usage:
    python main.py                    # Normal production run
    python main.py --dry-run          # Test without actual clicks
    python main.py --debug            # Verbose logging
    python main.py --single-cycle     # Run one cycle only
    python main.py --config custom.yaml  # Use custom config
"""

import sys
import argparse
import signal
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.orchestrator import Orchestrator
from src.config.config_loader import ConfigLoader
from src.monitoring.logger_config import setup_logging
from src.safety.kill_switch import KillSwitch, create_kill_switch
from src.utils.validation_utils import validate_environment


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Screen Recorder Automation Bot with Human Behavior Emulation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                         Run normally
  python main.py --dry-run               Test mode (no clicks)
  python main.py --debug                 Enable debug logging
  python main.py --single-cycle          Stop after one loop
  python main.py --config custom.yaml    Use custom configuration
  python main.py --visual-debug          Show visual overlays
        """
    )
    
    parser.add_argument(
        "--config",
        type=str,
        default="config.yaml",
        help="Path to configuration file (default: config.yaml)"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Execute without actual clicks (test mode)"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug-level logging"
    )
    
    parser.add_argument(
        "--visual-debug",
        action="store_true",
        help="Show visual overlays for cursor targets"
    )
    
    parser.add_argument(
        "--single-cycle",
        action="store_true",
        help="Execute only one cycle then exit"
    )
    
    parser.add_argument(
        "--no-bio-breaks",
        action="store_true",
        help="Disable bio-break scheduling"
    )
    
    parser.add_argument(
        "--max-cycles",
        type=int,
        help="Maximum number of cycles to execute"
    )
    
    return parser.parse_args()


def setup_signal_handlers(kill_switch):
    """Set up graceful shutdown on SIGINT/SIGTERM."""
    def signal_handler(signum, frame):
        print("\n[!] Received interrupt signal. Shutting down gracefully...")
        kill_switch.trigger()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


def main():
    """Main application entry point."""
    # Parse command-line arguments
    args = parse_arguments()
    
    # Setup logging
    log_level = "DEBUG" if args.debug else "INFO"
    logger = setup_logging(level=log_level)
    
    logger.info("=" * 60)
    logger.info("Screen Recorder Automation Bot - Starting")
    logger.info("=" * 60)
    
    try:
        # Load configuration
        logger.info(f"Loading configuration from: {args.config}")
        config = ConfigLoader.load(
            config_path=args.config,
            dry_run=args.dry_run,
            visual_debug=args.visual_debug,
            single_cycle=args.single_cycle,
            no_bio_breaks=args.no_bio_breaks
        )
        
        # Validate environment
        logger.info("Validating environment setup...")
        validation_errors = validate_environment(config)
        if validation_errors:
            logger.error("Environment validation failed:")
            for error in validation_errors:
                logger.error(f"  - {error}")
            return 1
        
        # Initialize kill switch
        logger.info("Initializing safety kill switch...")
        kill_switch = create_kill_switch(config)
        setup_signal_handlers(kill_switch)
        kill_switch.start()
        
        # Display runtime configuration
        if args.dry_run:
            logger.warning("⚠️  DRY RUN MODE - No actual clicks will be performed")
        if args.single_cycle:
            logger.info("Single-cycle mode: Will stop after one iteration")
        if args.max_cycles:
            logger.info(f"Max cycles limit: {args.max_cycles}")
        
        # Initialize orchestrator
        logger.info("Initializing orchestrator...")
        orchestrator = Orchestrator(
            config=config,
            kill_switch=kill_switch,
            max_cycles=args.max_cycles
        )
        
        # Run main loop
        logger.info("Starting main automation loop...")
        logger.info("-" * 60)
        result = orchestrator.run()
        
        # Shutdown
        logger.info("-" * 60)
        if result.success:
            logger.info(f"✓ Completed successfully: {result.cycles_completed} cycles")
            return 0
        else:
            logger.error(f"✗ Execution failed: {result.error_message}")
            return 1
    
    except KeyboardInterrupt:
        logger.warning("\n[!] Interrupted by user")
        return 130
    
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        return 1
    
    finally:
        logger.info("=" * 60)
        logger.info("Screen Recorder Automation Bot - Shutdown Complete")
        logger.info("=" * 60)


if __name__ == "__main__":
    sys.exit(main())
