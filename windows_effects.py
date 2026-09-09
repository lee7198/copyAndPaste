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
            0x01202020 if dark else 0x01F0EFEB,
            0,
        )
        data = CompositionData(19, ctypes.addressof(policy), ctypes.sizeof(policy))
        return bool(apply(handle, ctypes.byref(data))) and policy.state != 0
    except (OSError, AttributeError):
        return False
