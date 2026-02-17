"""
MMGI - Main Entry Point (UI Mode)
Launch MMGI with professional desktop dashboard.

Author: MMGI Project
Date: February 2026
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from ui.dashboard import MMGIDashboard
from ui.core_wrapper import MMGICore


def main():
    """Main entry point for UI mode."""
    print("=" * 60)
    print("MMGI - Multi-Modal Gesture Intelligence")
    print("Professional Dashboard Mode")
    print("=" * 60)
    print("\nInitializing dashboard...")
    
    # Create dashboard
    dashboard = MMGIDashboard()
    
    # Get communication queues
    command_queue = dashboard.get_command_queue()
    status_queue = dashboard.get_status_queue()
    
    # Create and start MMGI core thread
    print("Starting MMGI core in background thread...")
    core = MMGICore(command_queue, status_queue)
    core.start()
    
    print("Dashboard ready!")
    print("\nControls:")
    print("  - Click 'START SYSTEM' to begin gesture detection")
    print("  - Select control mode (App/Media/System)")
    print("  - Use gestures to control your PC")
    print("  - Close window to exit")
    print("\n" + "=" * 60 + "\n")
    
    try:
        # Run dashboard (blocking)
        dashboard.run()
    except KeyboardInterrupt:
        print("\nKeyboard interrupt detected...")
    finally:
        # Stop core thread
        print("\nShutting down MMGI core...")
        core.stop()
        core.join(timeout=2)
        print("MMGI Dashboard closed.")


if __name__ == "__main__":
    main()
