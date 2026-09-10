"""Native blur for an alpha-composited Qt surface.

SetWindowCompositionAttribute is an optional Windows API (not a stable public
contract). Guard availability and fall back to ordinary alpha transparency.
No negative DWM margins and no opacity changes to text or child controls.
"""

import ctypes
from ctypes import wintypes
import sys


class Accent(ctypes.Structure):
    _fields_ = [
        ("state", ctypes.c_int),
        ("flags", ctypes.c_int),
        ("tint", wintypes.DWORD),
        ("animation", ctypes.c_int),
    ]


class CompositionData(ctypes.Structure):
    _fields_ = [
        ("attribute", ctypes.c_int),
        ("data", ctypes.c_void_p),
        ("size", ctypes.c_size_t),
    ]


class Margins(ctypes.Structure):
    _fields_ = [(name, ctypes.c_int) for name in ("left", "right", "top", "bottom")]


def apply_native_shadow(handle):
    """Request the system-managed frame shadow without drawing our own."""
    if sys.platform != "win32":
        return False
    try:
        dwm = ctypes.WinDLL("dwmapi")
        apply = dwm.DwmSetWindowAttribute
        apply.argtypes = [wintypes.HWND, wintypes.DWORD, ctypes.c_void_p, wintypes.DWORD]
        apply.restype = ctypes.c_long
        policy = ctypes.c_int(2)  # DWMNCRP_ENABLED
        if apply(handle, 2, ctypes.byref(policy), ctypes.sizeof(policy)) != 0:
            return False
        extend = dwm.DwmExtendFrameIntoClientArea
        extend.argtypes = [wintypes.HWND, ctypes.POINTER(Margins)]
        extend.restype = ctypes.c_long
        return extend(handle, ctypes.byref(Margins(1, 1, 1, 1))) == 0
    except (OSError, AttributeError):
        return False


def apply_backdrop(handle, mode, dark=False):
    if sys.platform != "win32" or sys.getwindowsversion().build < 17763:
        return False
    try:
        user = ctypes.WinDLL("user32")
        apply = user.SetWindowCompositionAttribute
        apply.argtypes = [wintypes.HWND, ctypes.POINTER(CompositionData)]
        apply.restype = wintypes.BOOL
        # Acrylic tint must have nonzero alpha. Actual tint/opacity is painted
        # by Qt so settings remain effective even without this optional API.
        policy = Accent(
            {"off": 0, "blur": 3, "acrylic": 4}.get(mode, 0),
            0,
            0x01202020 if dark else 0x01EFEFEF,
            0,
        )
        data = CompositionData(19, ctypes.addressof(policy), ctypes.sizeof(policy))
        if apply(handle, ctypes.byref(data)):
            return policy.state != 0
        if policy.state == 4:
            policy.state = 3  # Fall back to ordinary blur if acrylic is rejected.
            if apply(handle, ctypes.byref(data)):
                return True
        policy.state = 0
        apply(handle, ctypes.byref(data))
        return False
    except (OSError, AttributeError):
        return False
