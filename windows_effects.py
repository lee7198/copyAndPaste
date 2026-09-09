"""Documented Windows 11 22H2 DWM backdrops; no whole-window opacity.

The blur radius is controlled by Windows. Unsupported systems use opaque panels.
https://learn.microsoft.com/windows/win32/api/dwmapi/ne-dwmapi-dwm_systembackdrop_type
"""

import ctypes
from ctypes import wintypes
import sys


class Margins(ctypes.Structure):
    _fields_ = [(name, ctypes.c_int) for name in ("left", "right", "top", "bottom")]


def apply_backdrop(handle, mode, dark=False, border_width=12):
    if sys.platform != "win32" or sys.getwindowsversion().build < 22621:
        return False
    try:
        dwm = ctypes.WinDLL("dwmapi")
        set_attribute = dwm.DwmSetWindowAttribute
        set_attribute.argtypes = [
            wintypes.HWND,
            wintypes.DWORD,
            ctypes.c_void_p,
            wintypes.DWORD,
        ]
        set_attribute.restype = ctypes.c_long
        extend = dwm.DwmExtendFrameIntoClientArea
        extend.argtypes = [wintypes.HWND, ctypes.POINTER(Margins)]
        extend.restype = ctypes.c_long

        def attribute(number, value):
            value = ctypes.c_int(value)
            return (
                set_attribute(handle, number, ctypes.byref(value), ctypes.sizeof(value))
                >= 0
            )

        attribute(20, int(dark))  # DWMWA_USE_IMMERSIVE_DARK_MODE
        attribute(33, 2)  # DWMWA_WINDOW_CORNER_PREFERENCE: round
        material = {"off": 1, "mica": 2, "acrylic": 3}.get(mode, 1)
        enabled = attribute(38, material) and material != 1
        # Never extend glass across wx/GDI child controls: their paint output
        # does not provide the alpha channel required for full-client glass.
        margin = max(0, int(border_width)) if enabled else 0
        if extend(handle, ctypes.byref(Margins(margin, margin, margin, margin))) < 0:
            attribute(38, 1)
            extend(handle, ctypes.byref(Margins(0, 0, 0, 0)))
            return False
        return enabled
    except (OSError, AttributeError):
        return False
