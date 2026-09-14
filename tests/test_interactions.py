"""Mouse interactions work without repaint-heavy effects."""

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from PySide6.QtCore import Qt, qInstallMessageHandler
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from appearance import AppearanceSettings
from data_manager import DataManager
from ui_manager import UIManager


class InteractionTests(unittest.TestCase):
    def test_row_click_and_panels(self):
        app = QApplication.instance() or QApplication([])
        with tempfile.TemporaryDirectory() as directory, patch(
            "ui_manager.apply_native_shadow", return_value=False
        ):
            root = Path(directory)
            data = root / "data.json"
            data.write_text(
                '{"list": [{"key": "Title", "value": "Value"}]}',
                encoding="utf-8",
            )
            manager = UIManager(
                app,
                DataManager(str(data)),
                AppearanceSettings(root / "prefs.json"),
            )
            messages = []
            previous_handler = qInstallMessageHandler(
                lambda kind, context, message: messages.append(message)
            )
            try:
                row = manager.data_list_ctrl.item(0)
                row_widget = manager.data_list_ctrl.itemWidget(row)
                QTest.mouseClick(row_widget, Qt.LeftButton)
                self.assertEqual(app.clipboard().text(), "Value")
                self.assertIs(manager.data_list_ctrl.currentItem(), row)

                manager.timer.start(1)
                QTest.qWait(10)
                self.assertEqual(manager.status_label.text(), "")

                manager.edit_item(row)
                manager.toggle_editor()
                manager.toggle_editor()
                self.assertTrue(manager.input_panel.isVisible())

                manager.toggle_settings()
                manager.frame.grab()
                manager.toggle_settings()
                manager.toggle_settings()
                self.assertEqual(manager.pages.currentIndex(), 1)
                manager.frame.grab()
                self.assertFalse(
                    [
                        message
                        for message in messages
                        if "QPainter" in message or "QWidgetEffectSource" in message
                    ]
                )
            finally:
                manager.frame.close()
                app.processEvents()
                qInstallMessageHandler(previous_handler)
