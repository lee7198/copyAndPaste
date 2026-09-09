"""DWM contract checks without requiring a Windows desktop."""

import ctypes
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from windows_effects import Margins, apply_backdrop


class BackdropTests(unittest.TestCase):
    def test_glass_is_confined_to_dpi_scaled_border_and_can_be_disabled(self):
        margins = []

        def extend(handle, pointer):
            value = ctypes.cast(pointer, ctypes.POINTER(Margins)).contents
            margins.append((value.left, value.right, value.top, value.bottom))
            return 0

        dwm = SimpleNamespace(
            DwmSetWindowAttribute=Mock(return_value=0),
            DwmExtendFrameIntoClientArea=Mock(side_effect=extend),
        )
        with (
            patch("windows_effects.sys.platform", "win32"),
            patch(
                "windows_effects.sys.getwindowsversion",
                return_value=SimpleNamespace(build=22621),
                create=True,
            ),
            patch("windows_effects.ctypes.WinDLL", return_value=dwm, create=True),
        ):
            self.assertTrue(apply_backdrop(123, "acrylic", border_width=18))
            self.assertTrue(apply_backdrop(123, "mica", border_width=24))
            self.assertFalse(apply_backdrop(123, "off", border_width=24))
        self.assertEqual(margins, [(18, 18, 18, 18), (24, 24, 24, 24), (0, 0, 0, 0)])

    def test_failed_extension_resets_glass_before_opaque_fallback(self):
        margins = []

        def extend(handle, pointer):
            value = ctypes.cast(pointer, ctypes.POINTER(Margins)).contents
            margins.append((value.left, value.right, value.top, value.bottom))
            return -1 if len(margins) == 1 else 0

        dwm = SimpleNamespace(
            DwmSetWindowAttribute=Mock(return_value=0),
            DwmExtendFrameIntoClientArea=Mock(side_effect=extend),
        )
        with (
            patch("windows_effects.sys.platform", "win32"),
            patch(
                "windows_effects.sys.getwindowsversion",
                return_value=SimpleNamespace(build=22621),
                create=True,
            ),
            patch("windows_effects.ctypes.WinDLL", return_value=dwm, create=True),
        ):
            self.assertFalse(apply_backdrop(123, "acrylic", border_width=12))
        self.assertEqual(margins, [(12, 12, 12, 12), (0, 0, 0, 0)])
