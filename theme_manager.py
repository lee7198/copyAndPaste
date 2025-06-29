"""
테마 관리 기능을 담당하는 모듈입니다.
시스템 테마 감지 및 색상 관리를 처리합니다.
"""

import wx
from typing import Dict, Tuple
import subprocess
import sys


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
                "primary": wx.Colour(33, 150, 243),  # Material Blue 500
                "background": wx.Colour(30, 30, 30),  # 어두운 배경
                "list_background": wx.Colour(45, 45, 45),  # 어두운 리스트 배경
                "text": wx.Colour(255, 255, 255),  # 흰색 텍스트
                "input_background": wx.Colour(50, 50, 50),  # 어두운 입력 필드
                "border": wx.Colour(70, 70, 70),  # 어두운 테두리
            }
        else:
            return {
                "primary": wx.Colour(33, 150, 243),  # Material Blue 500
                "background": wx.Colour(250, 250, 250),  # 밝은 배경
                "list_background": wx.Colour(245, 245, 245),  # 밝은 리스트 배경
                "text": wx.Colour(0, 0, 0),  # 검은색 텍스트
                "input_background": wx.Colour(255, 255, 255),  # 흰색 입력 필드
                "border": wx.Colour(200, 200, 200),  # 밝은 테두리
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
