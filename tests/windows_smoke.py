"""Qt rendering and CRUD checks. Runs on Windows or QT_QPA_PLATFORM=offscreen."""

from pathlib import Path
import os
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from PySide6.QtCore import Qt, QEvent, QPoint
from PySide6.QtTest import QTest
from unittest.mock import patch
from windows_effects import apply_native_shadow
from PySide6.QtWidgets import QApplication, QLabel, QPushButton
from appearance import AppearanceSettings
from data_manager import DataManager
from ui_manager import UIManager

app = QApplication([])
with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    data_path = root / "data.json"
    data_path.write_text('{"list": [], "font_size": 15}', encoding="utf-8")
    prefs = AppearanceSettings(root / "appearance.json")
    manager = UIManager(app, DataManager(str(data_path)), prefs)
    try:
        app.processEvents()
        manager.toggle_editor()
        manager.key_text.setText("한글 항목")
        original = "복사 원문 " * 80
        manager.value_text.setText(original)
        manager.save()
        assert manager.data_manager.get_item_count() == 1
        manager.toggle_editor()
        manager.select_item(manager.data_list_ctrl.item(0))
        assert QApplication.clipboard().text() == original.strip()
        assert manager.input_panel.isHidden()
        row = manager.data_list_ctrl.item(0)
        menu_button = manager.data_list_ctrl.itemWidget(row).findChild(QPushButton)
        manager.frame.resize(340, 540)
        app.processEvents()
        row_widget = manager.data_list_ctrl.itemWidget(row)
        label = row_widget.findChild(QLabel)
        assert label.height() >= label.sizeHint().height()
        assert label.width() > 0
        assert row_widget.rect().contains(menu_button.geometry())
        assert menu_button.visibleRegion().boundingRect() == menu_button.rect()
        assert menu_button.text() == "⋯"
        menu_button.click()
        assert manager.input_panel.isVisible()
        manager.value_text.setText("저장 전 편집 내용")
        with patch("ui_manager.apply_native_shadow", wraps=apply_native_shadow) as shadow:
            for screen in app.screens() * 2:
                manager.frame.move(screen.availableGeometry().topLeft() + QPoint(40, 40))
                QTest.qWait(200)
                assert manager.frame.screen() == screen
                assert manager.value_text.text() == "저장 전 편집 내용"
                assert manager.selected_index == 0
                assert manager.data_list_ctrl.item(0) is row
                for label in row_widget.findChildren(QLabel):
                    assert label.height() >= label.sizeHint().height()
                    assert label.width() > 0
                assert row_widget.rect().contains(menu_button.geometry())
                assert menu_button.visibleRegion().boundingRect() == menu_button.rect()
            # A same-screen DPI change must also refresh, without a resize.
            previous = shadow.call_count
            app.sendEvent(manager.frame, QEvent(QEvent.DevicePixelRatioChange))
            QTest.qWait(200)
            assert shadow.call_count > previous
            previous = shadow.call_count
            QTest.qWait(200)
            assert shadow.call_count == previous, "Display refresh loop"
        manager.value_text.setText("수정한 값")
        manager.save()
        assert manager.data_manager.get_items()[0]["value"] == "수정한 값"
        # No count label or nested header panel. Caption touches the frame edge.
        assert manager.title_bar.y() <= 1
        assert not manager.frame.mask().contains(manager.frame.rect().topLeft())
        assert manager.frame.mask().contains(manager.frame.rect().center())
        manager.frame.showMaximized()
        app.processEvents()
        assert manager.frame.mask().isEmpty()
        assert manager.title_bar.maximize_button.property("iconName") == "restore"
        manager.apply_appearance()
        assert manager.title_bar.maximize_button.property("iconName") == "restore"
        manager.frame.showNormal()
        app.processEvents()
        assert not manager.frame.mask().isEmpty()
        manager.frame.showMinimized()
        app.processEvents()
        manager.frame.showNormal()
        app.processEvents()
        assert manager.title_bar.maximize_button.property("iconName") == "maximize"
        for theme in ("light", "dark"):
            for backdrop in ("off", "blur", "acrylic"):
                prefs.save(dict(prefs.values, theme=theme, backdrop=backdrop))
                manager.apply_appearance()
                for width, height in ((340, 540), (600, 800)):
                    manager.frame.resize(width, height)
                    app.processEvents()
                    assert manager.data_list_ctrl.height() >= 120
                    assert manager.title_bar.isVisible()
                    assert (
                        manager.delete_button.geometry().right()
                        <= manager.input_panel.width()
                    )
                    rendered = manager.frame.grab().toImage()
                    # Sample empty list surface: alpha is genuinely transparent,
                    # while text/icons still contribute distinct pixel colors.
                    point = manager.data_list_ctrl.mapTo(
                        manager.frame, manager.data_list_ctrl.rect().center()
                    )
                    alpha = rendered.pixelColor(point).alpha()
                    assert alpha == 255 if not manager.backdrop_active else 0 < alpha < 255, (
                        backdrop,
                        alpha,
                    )
                    header = rendered.copy(0, 0, width, 48)
                    colors = {
                        header.pixel(x, y)
                        for x in range(15, 140)
                        for y in range(10, 38)
                    }
                    assert len(colors) > 10, "Title text did not render"
        manager.toggle_settings()
        assert manager.pages.currentIndex() == 1
        manager.settings.opacity.setValue(30)
        manager.settings.cancelled.emit()
        assert prefs.values["window_opacity"] == 52
        manager.toggle_settings()
        manager.settings.opacity.setValue(35)
        manager.save_settings(manager.settings.values())
        assert AppearanceSettings(prefs.path).values["window_opacity"] == 35
        row = manager.data_list_ctrl.item(0)
        manager.data_list_ctrl.itemWidget(row).findChild(QPushButton).click()
        manager.delete()
        assert manager.data_manager.get_item_count() == 0
        if os.environ.get("UI_SCREENSHOT_DIR"):
            out = Path(os.environ["UI_SCREENSHOT_DIR"])
            out.mkdir(parents=True, exist_ok=True)
            manager.frame.grab().save(str(out / "empty.png"))
        print("Qt alpha rendering / clipboard / CRUD / settings smoke passed")
    finally:
        manager.frame.close()
        app.processEvents()
