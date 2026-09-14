"""Interaction animations settle and restart without losing feedback."""

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from PySide6.QtCore import QPoint, qInstallMessageHandler
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from appearance import AppearanceSettings
from data_manager import DataManager
from ui_manager import UIManager


class InteractionTests(unittest.TestCase):
    def test_copy_restart_and_panel_open(self):
        app = QApplication.instance() or QApplication([])
        with tempfile.TemporaryDirectory() as directory, patch(
            "ui_manager.apply_backdrop", return_value=False
        ), patch("ui_manager.apply_native_shadow", return_value=False):
            root = Path(directory)
            data = root / "data.json"
            data.write_text('{"list": [{"key": "Title", "value": "Value"}]}')
            manager = UIManager(app, DataManager(str(data)), AppearanceSettings(root / "prefs.json"))
            messages = []
            previous_handler = qInstallMessageHandler(lambda kind, context, message: messages.append(message))
            try:
                row = manager.data_list_ctrl.item(0)
                manager.select_item(row)
                self.assertEqual(app.clipboard().text(), "Value")
                self.assertTrue(manager.status_label.text().startswith("✓"))
                manager.timer.stop()
                manager.status_fade.start()
                manager.status_fade.setCurrentTime(175)
                self.assertAlmostEqual(manager.status_opacity.opacity(), 0.5)
                manager.select_item(row)
                self.assertEqual(manager.status_opacity.opacity(), 1.0)
                manager.timer.stop()
                manager.status_fade.start()
                manager.status_fade.setCurrentTime(350)
                self.assertEqual(manager.status_label.text(), "")
                manager.edit_item(row)
                manager.toggle_editor()
                manager.toggle_editor()
                QTest.qWait(250)
                self.assertTrue(manager.input_panel.isVisible())
                self.assertEqual(manager.input_panel.maximumHeight(), 16777215)
                manager.toggle_settings()
                manager.settings_pop.setCurrentTime(90)
                self.assertGreater(manager.settings.y(), 0)
                manager.frame.grab()
                manager.toggle_settings()
                manager.toggle_settings()
                QTest.qWait(250)
                self.assertEqual(manager.pages.currentIndex(), 1)
                self.assertEqual(manager.settings.pos(), QPoint(0, 0))
                manager.frame.grab()
                self.assertFalse([message for message in messages if
                                  "QPainter" in message or "QWidgetEffectSource" in message])
            finally:
                manager.frame.close()
                app.processEvents()
                qInstallMessageHandler(previous_handler)
