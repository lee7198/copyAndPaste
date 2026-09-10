"""Display updates must preserve editing and avoid repeated native effect calls."""

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from PySide6.QtCore import QEvent, QPoint
from PySide6.QtGui import QFontInfo
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QLabel
from appearance import AppearanceSettings
from data_manager import DataManager
from ui_manager import UIManager


class DisplayTests(unittest.TestCase):
    def test_effect_recovery_font_and_screen_changes(self):
        app = QApplication.instance() or QApplication([])
        with tempfile.TemporaryDirectory() as directory, patch(
            "ui_manager.apply_backdrop", return_value=True
        ) as backdrop, patch("ui_manager.apply_native_shadow", return_value=True):
            root = Path(directory)
            data = root / "data.json"
            data.write_text('{"list": [{"key": "Title", "value": "Value"}]}')
            manager = UIManager(app, DataManager(str(data)), AppearanceSettings(root / "prefs.json"))
            try:
                QTest.qWait(150)
                manager.edit_item(manager.data_list_ctrl.item(0))
                manager.value_text.setText("Unsaved edit")
                QTest.qWait(150)
                previous = backdrop.call_count
                manager.frame.resize(400, 650)
                QTest.qWait(150)
                self.assertEqual(backdrop.call_count, previous)
                for screen in app.screens() * 2:
                    manager.frame.move(screen.availableGeometry().topLeft() + QPoint(40, 40))
                    QTest.qWait(150)
                    self.assertEqual(manager.value_text.text(), "Unsaved edit")
                    row = manager.data_list_ctrl.itemWidget(manager.data_list_ctrl.item(0))
                    for label in row.findChildren(QLabel):
                        self.assertGreaterEqual(label.height(), label.sizeHint().height())
                    self.assertEqual(QFontInfo(row.findChild(QLabel).font()).family(), "Malgun Gothic")
                backdrop.return_value = False
                app.sendEvent(manager.frame, QEvent(QEvent.DevicePixelRatioChange))
                QTest.qWait(150)
                self.assertEqual(manager.frame.background_opacity, 1.0)
                backdrop.return_value = True
                app.sendEvent(manager.frame, QEvent(QEvent.DevicePixelRatioChange))
                QTest.qWait(150)
                self.assertEqual(manager.frame.background_opacity, 0.52)
            finally:
                manager.frame.close()
                app.processEvents()
