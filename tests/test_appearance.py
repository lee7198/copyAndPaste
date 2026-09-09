import json
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from appearance import AppearanceSettings, DEFAULTS, normalize
from data_manager import DataManager
from windows_effects import apply_backdrop


class AppearanceTests(unittest.TestCase):
    def test_invalid_values_and_bounds(self):
        self.assertEqual(normalize(None), DEFAULTS)
        self.assertEqual(normalize({"theme": [], "panel_density": True}), DEFAULTS)
        self.assertEqual(normalize({"panel_density": -50})["panel_density"], 50)
        self.assertEqual(normalize({"panel_density": 500})["panel_density"], 100)

    def test_settings_round_trip_does_not_touch_clipboard_data(self):
        with tempfile.TemporaryDirectory() as directory:
            data_path = Path(directory) / "data.json"
            data_path.write_text(
                json.dumps(
                    {"font_size": 15, "list": [{"key": "안녕", "value": "원문"}]}
                )
            )
            original = data_path.read_bytes()
            settings = AppearanceSettings(Path(directory) / "settings.json")
            settings.save({"theme": "dark", "backdrop": "off", "panel_density": 60})
            self.assertEqual(AppearanceSettings(settings.path).values, settings.values)
            self.assertEqual(data_path.read_bytes(), original)
            manager = DataManager(str(data_path))
            self.assertTrue(manager.add_item("긴 글", "x" * 1000))
            self.assertTrue(manager.update_item(0, "수정", "한글\n두 번째 줄"))
            self.assertTrue(manager.delete_data(1))
            manager.refresh_data()
            self.assertEqual(
                manager.get_items(), [{"key": "수정", "value": "한글\n두 번째 줄"}]
            )

    def test_corrupt_file_and_failed_write(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "appearance.json"
            path.write_text("{broken")
            settings = AppearanceSettings(path)
            self.assertEqual(settings.values, DEFAULTS)
            settings.save(DEFAULTS)
            original = path.read_bytes()
            with patch("appearance.os.replace", side_effect=OSError("read only")):
                with self.assertRaises(OSError):
                    settings.save({"theme": "dark"})
            self.assertEqual(path.read_bytes(), original)
            self.assertEqual(settings.values, DEFAULTS)
            self.assertEqual(list(Path(directory).iterdir()), [path])

    def test_korean_data_and_errors_with_cp1252_console(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "한글.json"
            path.write_text('{"list": [], "font_size": 15}', encoding="utf-8")
            output = io.BytesIO()
            with io.TextIOWrapper(
                output, encoding="cp1252", errors="strict"
            ) as console:
                with patch("data_manager.sys.stdout", console):
                    manager = DataManager(str(path))
                    self.assertTrue(manager.add_item("이름", "한글 원문"))
                    manager.refresh_data()
                    self.assertEqual(
                        manager.get_items(), [{"key": "이름", "value": "한글 원문"}]
                    )
                    self.assertFalse(manager.delete_data(999))
                    with patch("builtins.open", side_effect=OSError("저장 실패")):
                        self.assertFalse(manager.save_data())
                console.flush()
                self.assertTrue(output.getvalue())
            self.assertIn("한글 원문", path.read_text(encoding="utf-8"))

    def test_save_with_missing_or_closed_console(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "data.json"
            path.write_text('{"list": [], "font_size": 15}', encoding="utf-8")
            closed = io.StringIO()
            closed.close()
            for console in (None, closed):
                with self.subTest(console=console):
                    with patch("data_manager.sys.stdout", console):
                        manager = DataManager(str(path))
                        self.assertTrue(manager.save_data())
                        with patch("builtins.open", side_effect=OSError("저장 실패")):
                            self.assertFalse(manager.save_data())

    def test_old_mica_settings_migrate_to_blur_with_real_opacity(self):
        values = normalize({"theme": "dark", "backdrop": "mica", "panel_density": 80})
        self.assertEqual(values["backdrop"], "blur")
        self.assertEqual(values["window_opacity"], 52)
        self.assertEqual(normalize({"window_opacity": 1})["window_opacity"], 20)
        self.assertEqual(normalize({"window_opacity": 100})["window_opacity"], 90)

    def test_unsupported_platform_does_not_load_windows_dll(self):
        with patch("windows_effects.sys.platform", "linux"):
            self.assertFalse(apply_backdrop(0, "acrylic"))


if __name__ == "__main__":
    unittest.main()
