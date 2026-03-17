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

    @staticmethod
    def get_theme_colors() -> Dict[str, wx.Colour]:
        """현재 테마에 맞는 색상 팔레트를 반환합니다."""
        is_dark = ThemeManager.is_dark_mode()

        if is_dark:
            return {
                # Material 3 dark inspired palette
                "primary": wx.Colour(178, 197, 255),
                "on_primary": wx.Colour(22, 46, 97),
                "secondary": wx.Colour(194, 197, 220),
                "background": wx.Colour(19, 19, 24),
                "surface": wx.Colour(30, 30, 36),
                "surface_variant": wx.Colour(45, 46, 56),
                "list_background": wx.Colour(30, 30, 36),
                "text": wx.Colour(230, 226, 236),
                "on_surface": wx.Colour(230, 226, 236),
                "on_surface_variant": wx.Colour(199, 198, 209),
                "input_background": wx.Colour(45, 46, 56),
                "border": wx.Colour(100, 101, 114),
                "outline": wx.Colour(123, 124, 137),
                "success": wx.Colour(117, 220, 126),
                "danger": wx.Colour(255, 180, 171),
            }
        else:
            return {
                # Material 3 light inspired palette
                "primary": wx.Colour(64, 95, 168),
                "on_primary": wx.Colour(255, 255, 255),
                "secondary": wx.Colour(86, 95, 127),
                "background": wx.Colour(248, 249, 255),
                "surface": wx.Colour(255, 255, 255),
                "surface_variant": wx.Colour(227, 226, 236),
                "list_background": wx.Colour(255, 255, 255),
                "text": wx.Colour(28, 27, 31),
                "on_surface": wx.Colour(28, 27, 31),
                "on_surface_variant": wx.Colour(72, 70, 79),
                "input_background": wx.Colour(243, 244, 251),
                "border": wx.Colour(203, 201, 212),
                "outline": wx.Colour(120, 118, 128),
                "success": wx.Colour(31, 123, 54),
                "danger": wx.Colour(186, 26, 26),
            }

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
