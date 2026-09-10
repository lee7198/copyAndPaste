import ctypes
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
from windows_effects import Accent, CompositionData, Margins, apply_backdrop, apply_native_shadow


class BackdropTests(unittest.TestCase):
    def test_acrylic_failure_tries_blur_then_disables_effect(self):
        for blur_works in (True, False):
            states = []

            def apply(handle, pointer):
                data = ctypes.cast(pointer, ctypes.POINTER(CompositionData)).contents
                state = ctypes.cast(data.data, ctypes.POINTER(Accent)).contents.state
                states.append(state)
                return int(state == 3 and blur_works)

            native = SimpleNamespace(SetWindowCompositionAttribute=Mock(side_effect=apply))
            with patch("windows_effects.sys.platform", "win32"), patch(
                "windows_effects.sys.getwindowsversion",
                return_value=SimpleNamespace(build=22621), create=True,
            ), patch("windows_effects.ctypes.WinDLL", return_value=native, create=True):
                self.assertEqual(apply_backdrop(123, "acrylic"), blur_works)
            self.assertEqual(states, [4, 3] if blur_works else [4, 3, 0])

    def test_native_shadow_policy_and_failure(self):
        def apply(handle, attribute, pointer, size):
            self.assertEqual(handle, 123)
            self.assertEqual(attribute, 2)
            self.assertEqual(size, ctypes.sizeof(ctypes.c_int))
            self.assertEqual(ctypes.cast(pointer, ctypes.POINTER(ctypes.c_int)).contents.value, 2)
            return 0

        def extend(handle, pointer):
            self.assertEqual(handle, 123)
            margins = ctypes.cast(pointer, ctypes.POINTER(Margins)).contents
            self.assertEqual((margins.left, margins.right, margins.top, margins.bottom), (1, 1, 1, 1))
            return 0

        native = SimpleNamespace(
            DwmSetWindowAttribute=Mock(side_effect=apply),
            DwmExtendFrameIntoClientArea=Mock(side_effect=extend),
        )
        with patch("windows_effects.sys.platform", "win32"), patch(
            "windows_effects.ctypes.WinDLL", return_value=native, create=True
        ):
            self.assertTrue(apply_native_shadow(123))
            native.DwmSetWindowAttribute.side_effect = OSError
            self.assertFalse(apply_native_shadow(123))

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
