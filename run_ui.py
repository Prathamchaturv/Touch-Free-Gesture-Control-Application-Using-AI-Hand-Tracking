"""
run_ui.py — MMGI Premium Dashboard entry point

Usage
-----

  # Run with built-in fake-data simulator (no camera required):
  python run_ui.py --simulate

  # Run connected to the real MMGI camera pipeline:
  python run_ui.py

"""

import sys
import argparse
from pathlib import Path

# Ensure project root is importable
sys.path.insert(0, str(Path(__file__).resolve().parent))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore    import Qt
from PyQt6.QtGui     import QFont


def main() -> None:
    parser = argparse.ArgumentParser(
        description="MMGI Premium PyQt6 Dashboard"
    )
    parser.add_argument(
        "--simulate", "-s",
        action="store_true",
        default=False,
        help="Use built-in fake-data simulator instead of real camera.",
    )
    args = parser.parse_args()

    app = QApplication(sys.argv)
    app.setApplicationName("MMGI Dashboard")
    app.setOrganizationName("MMGI")

    # High-DPI
    app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)

    # Default font
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    from ui.main_window  import MainWindow
    from ui.state_manager import StateManager

    state  = StateManager()
    window = MainWindow(state=state, simulate=args.simulate)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
