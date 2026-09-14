"""Display updates must preserve editing and avoid repeated native effect calls."""

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from PySide6.QtCore import QEvent, QPoint, Qt
from PySide6.QtGui import QFontInfo
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QLabel
from appearance import AppearanceSettings
from data_manager import DataManager
from ui_manager import UIManager
from settings_dialog import SettingsPanel
from appearance import DEFAULTS
from theme_manager import stylesheet


class DisplayTests(unittest.TestCase):
    def test_settings_radio_choices(self):
        app = QApplication.instance() or QApplication([])
        panel = SettingsPanel()
        panel.resize(306, 540)
        panel.setStyleSheet(stylesheet(False))
        panel.load(DEFAULTS)
        panel.show()
        app.processEvents()
        try:
            for group, key, values in (
                (panel.theme, "theme", ("system", "light", "dark")),
            ):
                for index, value in enumerate(values):
                    button = group.button(index)
                    button.setFocus()
                    QTest.keyClick(button, Qt.Key_Space)
                    self.assertEqual(panel.values()[key], value)
                    self.assertEqual(sum(b.isChecked() for b in group.buttons()), 1)
                    self.assertGreaterEqual(button.width(), button.minimumSizeHint().width())
                    self.assertEqual(button.visibleRegion().boundingRect(), button.rect())
            panel.load(DEFAULTS)
            self.assertEqual(panel.values(), DEFAULTS)
        finally:
            panel.close()

    def test_effect_recovery_font_and_screen_changes(self):
        app = QApplication.instance() or QApplication([])
        with tempfile.TemporaryDirectory() as directory, patch(
            "ui_manager.apply_native_shadow", return_value=True
        ) as shadow:
            root = Path(directory)
            data = root / "data.json"
            data.write_text('{"list": [{"key": "Title", "value": "Value"}]}')
            manager = UIManager(app, DataManager(str(data)), AppearanceSettings(root / "prefs.json"))
            try:
                QTest.qWait(150)
                manager.edit_item(manager.data_list_ctrl.item(0))
                manager.value_text.setText("Unsaved edit")
                QTest.qWait(150)
                previous = shadow.call_count
                manager.frame.resize(400, 650)
                QTest.qWait(150)
                self.assertEqual(shadow.call_count, previous)
                for screen in app.screens() * 2:
                    manager.frame.move(screen.availableGeometry().topLeft() + QPoint(40, 40))
                    QTest.qWait(150)
                    self.assertEqual(manager.value_text.text(), "Unsaved edit")
                    row = manager.data_list_ctrl.itemWidget(manager.data_list_ctrl.item(0))
                    for label in row.findChildren(QLabel):
                        self.assertGreaterEqual(label.height(), label.sizeHint().height())
                self.assertEqual(QFontInfo(row.findChild(QLabel).font()).family(), "Noto Sans KR")
                app.sendEvent(manager.frame, QEvent(QEvent.DevicePixelRatioChange))
                QTest.qWait(150)
                self.assertGreater(shadow.call_count, previous)
                self.assertFalse(manager.frame.testAttribute(Qt.WA_TranslucentBackground))
                self.assertFalse(manager.backdrop_active)
            finally:
                manager.frame.close()
                app.processEvents()
