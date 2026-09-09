"""Run on a Windows desktop: python tests/windows_smoke.py.

Uses temporary clipboard data/settings; closes its test frame automatically.
Desktop Acrylic appearance still requires a Windows 11 visual review.
"""

from pathlib import Path
import sys
import tempfile
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import wx
from appearance import AppearanceSettings
from data_manager import DataManager
from ui_manager import UIManager
from settings_dialog import SettingsDialog
from theme_manager import ThemeManager

app = wx.App(False)
with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    prefs = AppearanceSettings(root / "appearance.json")
    with patch("ui_manager.AppearanceSettings", return_value=prefs):
        manager = UIManager(app, DataManager(str(root / "data.json")))
    try:
        app.Yield()
        manager.on_add_button_click(None)
        manager.key_text.SetValue("한글 항목")
        original = "복사 원문 " * 80
        manager.value_text.SetValue(original)
        manager.on_save(None)
        assert manager.data_manager.get_item_count() == 1
        event = wx.ListEvent(wx.EVT_LIST_ITEM_SELECTED.typeId)
        event.SetIndex(0)
        manager.on_listctrl_click(event)
        assert manager.value_text.GetValue() == original.strip()
        assert manager.input_panel.IsShown()
        if not wx.TheClipboard.Open():
            raise AssertionError("Cannot open test clipboard")
        try:
            copied = wx.TextDataObject()
            assert wx.TheClipboard.GetData(copied)
            assert copied.GetText() == original.strip()
        finally:
            wx.TheClipboard.Close()
        manager.value_text.SetValue("수정한 값")
        manager.on_save(None)
        assert manager.data_manager.get_item_count() == 1
        for theme in ("light", "dark"):
            for backdrop in ("off", "mica", "acrylic", "off"):
                prefs.save({"theme": theme, "backdrop": backdrop, "panel_density": 70})
                ThemeManager.preference = theme
                manager._apply_theme()
                manager._apply_backdrop()
                for size in ((360, 500), (600, 800)):
                    manager.frame.SetSize(manager.frame.FromDIP(size))
                    app.Yield()
                    assert manager.main_panel.IsShownOnScreen()
                    assert manager.main_panel.GetBackgroundColour() != wx.BLACK
                    border = manager.frame.FromDIP(12)
                    rect = manager.main_panel.GetRect()
                    client = manager.frame.GetClientSize()
                    assert rect.x >= border and rect.y >= border
                    assert rect.GetRight() < client.width - border
                    assert rect.GetBottom() < client.height - border
                    list_height = manager.data_list_ctrl.GetSize().height
                    minimum_height = manager.frame.FromDIP(120)
                    assert list_height >= minimum_height, (
                        f"list={list_height}, required={minimum_height}, "
                        f"requested={size}, client={client}, "
                        f"minimum_client={manager.minimum_client_size}"
                    )
                    assert client.height >= manager.minimum_client_size.height
                    assert manager.input_panel.IsShownOnScreen()
                    assert (
                        manager.input_panel.GetRect().GetBottom()
                        < manager.main_panel.GetClientSize().height
                    )
                    for button in manager.title_bar.buttons:
                        assert button.IsShownOnScreen()
                        assert (
                            button.GetRect().GetRight()
                            <= manager.title_bar.GetClientSize().width
                        )
        dialog = SettingsDialog(manager.frame, prefs.values, False)
        assert dialog.values() == prefs.values
        dialog.Destroy()
        manager.data_list_ctrl.Select(0)
        manager.on_delete(None)
        assert manager.data_manager.get_item_count() == 0
        print("Windows UI / clipboard / CRUD / settings smoke passed")
    finally:
        if manager.status_clear_timer:
            manager.status_clear_timer.Stop()
        manager.frame.Destroy()
        app.Yield()
