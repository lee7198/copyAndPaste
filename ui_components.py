"""
UI 컴포넌트들을 정의하는 모듈입니다.
재사용 가능한 UI 요소들을 포함합니다.
"""

import wx
from typing import Optional
from constants import ROUNDED_PANEL_RADIUS, STATUS_PANEL_RADIUS
from theme_manager import ThemeManager


class RoundedPanel(wx.Panel):
    """둥근 모서리를 가진 패널 클래스"""

    def __init__(self, parent, radius: int = ROUNDED_PANEL_RADIUS, **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)
        self.radius = radius
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)

    def OnPaint(self, event):
        """페인트 이벤트 처리"""
        dc = wx.BufferedPaintDC(self)
        self.DrawRoundedRectangle(dc)

    def OnSize(self, event):
        """크기 변경 이벤트 처리"""
        self.Refresh()

    def DrawRoundedRectangle(self, dc):
        """둥근 사각형을 그립니다"""
        dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
        dc.Clear()

        width, height = self.GetSize()

        # 둥근 사각형 그리기
        dc.SetBrush(wx.Brush(self.GetBackgroundColour()))
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.DrawRoundedRectangle(0, 0, width, height, self.radius)


class StatusFrame(wx.Frame):
    """상태 메시지를 표시하는 프레임"""

    def __init__(self, parent: wx.Frame, message: str, font_size: int = 15):
        super().__init__(
            parent,
            title="",
            size=(80, 30),
            style=wx.FRAME_NO_TASKBAR | wx.STAY_ON_TOP | wx.BORDER_NONE,
        )

        self.parent = parent
        self.message = message
        self.font_size = font_size

        self._init_ui()
        self._position_frame()

    def _init_ui(self):
        """UI 초기화"""
        status_panel = RoundedPanel(self, radius=STATUS_PANEL_RADIUS)
        status_text = wx.StaticText(status_panel, label=self.message)

        # 시스템 폰트 사용
        status_font = wx.Font(
            self.font_size,
            wx.FONTFAMILY_DEFAULT,
            wx.FONTSTYLE_NORMAL,
            wx.FONTWEIGHT_BOLD,
        )
        status_text.SetFont(status_font)

        # 배경색과 텍스트 색상 설정
        status_panel.SetBackgroundColour(ThemeManager.get_primary_color())
        status_text.SetForegroundColour(wx.Colour(255, 255, 255))  # 흰색 텍스트

        # 레이아웃 - 패널을 프레임 전체에 맞춤
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(status_text, 1, wx.ALL | wx.ALIGN_CENTER, 5)
        status_panel.SetSizer(sizer)

    def _position_frame(self):
        """프레임 위치 설정"""
        from constants import STATUS_FRAME_WIDTH, STATUS_OFFSET_Y

        frame_pos = self.parent.GetPosition()
        frame_size = self.parent.GetSize()
        x = frame_pos[0] + (frame_size[0] - STATUS_FRAME_WIDTH) // 2
        y = frame_pos[1] + STATUS_OFFSET_Y
        self.SetPosition((x, y))

    def show_temporarily(self, duration: int = 2000):
        """일정 시간 동안 표시 후 자동으로 닫기"""
        self.Show()
        wx.CallLater(duration, self.Close)
