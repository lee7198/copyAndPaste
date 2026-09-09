"""Qt rendering and CRUD checks. Runs on Windows or QT_QPA_PLATFORM=offscreen."""

from pathlib import Path
import os
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
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
        manager.select_item(manager.data_list_ctrl.item(0))
        assert QApplication.clipboard().text() == original.strip()
        assert manager.input_panel.isVisible()
        manager.value_text.setText("수정한 값")
        manager.save()
        assert manager.data_manager.get_items()[0]["value"] == "수정한 값"
        # No count label or nested header panel. Caption touches the frame edge.
        assert manager.title_bar.y() <= 1
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
                    assert alpha == 255 if backdrop == "off" else 0 < alpha < 255, (
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
        manager.select_item(manager.data_list_ctrl.item(0))
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
