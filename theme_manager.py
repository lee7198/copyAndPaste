"""
테마 관리 기능을 담당하는 모듈입니다.
시스템 테마 감지 및 색상 관리를 처리합니다.
"""

# mypy: ignore-errors
# pylint: disable=broad-exception-caught,no-member
import wx  # type: ignore[import-untyped]
from typing import Dict
import subprocess


class ThemeManager:
    """시스템 테마를 감지하고 적절한 색상을 제공하는 클래스"""

    @staticmethod
    def is_dark_mode() -> bool:
        """시스템이 다크모드인지 확인합니다."""
        if wx.Platform == "__WXMAC__":
            return ThemeManager._detect_macos_dark_mode()
        elif wx.Platform == "__WXMSW__":
            return ThemeManager._detect_windows_dark_mode()
        else:
            return False

    @staticmethod
    def _detect_macos_dark_mode() -> bool:
        """macOS에서 다크모드 감지"""
        try:
            result = subprocess.run(
                ["defaults", "read", "-g", "AppleInterfaceStyle"],
                capture_output=True,
                text=True,
                check=False,
            )
            return result.stdout.strip() == "Dark"
        except Exception:
            return False

    @staticmethod
    def _detect_windows_dark_mode() -> bool:
        """Windows에서 다크모드 감지"""
        try:
            import winreg

            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
            )
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            winreg.CloseKey(key)
            return value == 0
        except Exception:
            return False

    preference = "system"
    panel_density = 80

    @staticmethod
    def get_theme_colors() -> Dict[str, wx.Colour]:
        """Warm neutral glass palette with opaque, readable text surfaces."""
        dark = ThemeManager.preference == "dark" or (
            ThemeManager.preference == "system" and ThemeManager.is_dark_mode()
        )
        values = {
            "primary": "E6DFD3" if dark else "484C46",
            "on_primary": "292B29" if dark else "FFFFFF",
            "background": "252725" if dark else "D9D7D0",
            "surface": "3D403C" if dark else "F0EEE8",
            "surface_variant": "50534D" if dark else "E1DFD7",
            "text": "F4F1E9" if dark else "292D28",
            "on_surface_variant": "C9CDC3" if dark else "60665D",
            "input_background": "333631" if dark else "FAF9F5",
            "border": "6A6E65" if dark else "FFFFFF",
            "success": "B1DBB9" if dark else "326743",
            "danger": "EFB7AE" if dark else "A44339",
        }
        colors = {key: wx.Colour("#" + value) for key, value in values.items()}
        # Density changes panel tint; Windows owns the actual blur radius.
        ratio = ThemeManager.panel_density / 100
        bg, surface = colors["background"], colors["surface"]
        colors["surface"] = wx.Colour(
            *[
                round(a * ratio + b * (1 - ratio))
                for a, b in zip(surface.Get()[:3], bg.Get()[:3])
            ]
        )
        colors["on_surface"] = colors["text"]
        colors["list_background"] = colors["surface"]
        colors["secondary"] = colors["on_surface_variant"]
        colors["outline"] = colors["border"]
        return colors

    @staticmethod
    def get_primary_color() -> wx.Colour:
        """주요 색상을 반환합니다."""
        return ThemeManager.get_theme_colors()["primary"]

    @staticmethod
    def get_background_color() -> wx.Colour:
        """배경 색상을 반환합니다."""
        return ThemeManager.get_theme_colors()["background"]

    @staticmethod
    def get_list_background_color() -> wx.Colour:
        """리스트 배경 색상을 반환합니다."""
        return ThemeManager.get_theme_colors()["list_background"]

    @staticmethod
    def get_status_color(kind: str) -> wx.Colour:
        """상태 메시지 종류에 맞는 강조 색상을 반환합니다."""
        colors = ThemeManager.get_theme_colors()
        if kind == "success":
            return colors["success"]
        if kind == "error":
            return colors["danger"]
        return colors["primary"]
