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
    """상태 메시지를 표시하는 프레임 (더 예쁘고 현대적으로 개선, 프레임 전체 둥글게 기능 제거)"""

    def __init__(self, parent: wx.Frame, message: str, font_size: int = 15):
        from constants import (
            STATUS_FRAME_WIDTH,
            STATUS_FRAME_HEIGHT,
            STATUS_PANEL_RADIUS,
        )

        super().__init__(
            parent,
            title="",
            size=(STATUS_FRAME_WIDTH + 40, STATUS_FRAME_HEIGHT),
            style=wx.FRAME_NO_TASKBAR | wx.STAY_ON_TOP | wx.BORDER_NONE,
        )
        self.SetTransparent(230)  # 반투명 효과 (0~255)
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.parent = parent
        self.message = message
        self.font_size = font_size
        self.radius = STATUS_PANEL_RADIUS + 10
        self._init_ui()
        self._position_frame()

    def _init_ui(self):
        panel = wx.Panel(self)
        panel.SetBackgroundColour(ThemeManager.get_primary_color())
        sizer = wx.BoxSizer(wx.VERTICAL)
        status_text = wx.StaticText(panel, label=self.message, style=wx.ALIGN_CENTER)
        status_font = wx.Font(
            self.font_size,
            wx.FONTFAMILY_SWISS,
            wx.FONTSTYLE_NORMAL,
            wx.FONTWEIGHT_BOLD,
        )
        status_text.SetFont(status_font)
        status_text.SetForegroundColour(wx.Colour(255, 255, 255))
        # 패딩과 중앙정렬 (패딩을 3으로 줄임)
        inner_sizer = wx.BoxSizer(wx.VERTICAL)
        inner_sizer.AddStretchSpacer(1)
        inner_sizer.Add(status_text, 0, wx.ALIGN_CENTER | wx.ALL, 3)
        inner_sizer.AddStretchSpacer(1)
        panel.SetSizer(inner_sizer)
        sizer.Add(panel, 1, wx.EXPAND | wx.ALL, 0)
        self.SetSizer(sizer)
        self.panel = panel

    def _position_frame(self):
        from constants import STATUS_FRAME_WIDTH, STATUS_OFFSET_Y

        frame_pos = self.parent.GetPosition()
        frame_size = self.parent.GetSize()
        x = frame_pos[0] + (frame_size[0] - self.GetSize()[0]) // 2
        y = frame_pos[1] + STATUS_OFFSET_Y
        self.SetPosition((x, y))

    def show_temporarily(self, duration: int = 2000):
        self.Show()
        wx.CallLater(duration, self.Close)
