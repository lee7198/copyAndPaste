import ctypes
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
from windows_effects import Accent, CompositionData, apply_backdrop


class BackdropTests(unittest.TestCase):
    def test_native_effect_modes_and_pointer_safe_payload(self):
        states = []

        def apply(handle, pointer):
            data = ctypes.cast(pointer, ctypes.POINTER(CompositionData)).contents
            self.assertEqual(data.attribute, 19)
            self.assertEqual(data.size, ctypes.sizeof(Accent))
            states.append(ctypes.cast(data.data, ctypes.POINTER(Accent)).contents.state)
            return 1

        native = SimpleNamespace(SetWindowCompositionAttribute=Mock(side_effect=apply))
        with patch("windows_effects.sys.platform", "win32"), patch(
            "windows_effects.sys.getwindowsversion",
            return_value=SimpleNamespace(build=22621),
            create=True,
        ), patch("windows_effects.ctypes.WinDLL", return_value=native, create=True):
            self.assertTrue(apply_backdrop(123, "acrylic"))
            self.assertTrue(apply_backdrop(123, "blur"))
            self.assertFalse(apply_backdrop(123, "off"))
        self.assertEqual(states, [4, 3, 0])

    def test_missing_api_falls_back_without_hiding_content(self):
        with patch("windows_effects.sys.platform", "win32"), patch(
            "windows_effects.sys.getwindowsversion",
            return_value=SimpleNamespace(build=22621),
            create=True,
        ), patch("windows_effects.ctypes.WinDLL", side_effect=OSError, create=True):
            self.assertFalse(apply_backdrop(123, "acrylic"))
