"""Desktop entry point. Existing data.json remains the source of clipboard items."""

import sys
from PySide6.QtWidgets import QApplication
from data_manager import DataManager
from ui_manager import UIManager
from constants import DEFAULT_DATA_FILE


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Copy & Paste")
    ui = UIManager(app, DataManager(DEFAULT_DATA_FILE))
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
