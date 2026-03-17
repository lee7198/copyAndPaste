"""
UI 컴포넌트들을 정의하는 모듈입니다.
재사용 가능한 UI 요소들을 포함합니다.
"""

# mypy: ignore-errors
# pylint: skip-file
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
    """Material 스타일 상태 토스트 프레임"""

    def __init__(
        self,
        parent: wx.Frame,
        message: str,
        font_size: int = 15,
        status_kind: str = "info",
    ):
        from constants import STATUS_FRAME_WIDTH, STATUS_FRAME_HEIGHT

        super().__init__(
            parent,
            title="",
            size=wx.Size(STATUS_FRAME_WIDTH, STATUS_FRAME_HEIGHT),
            style=wx.FRAME_NO_TASKBAR | wx.STAY_ON_TOP | wx.BORDER_NONE,
        )
        self.SetTransparent(245)
        self.SetBackgroundStyle(wx.BG_STYLE_SYSTEM)
        self.parent = parent
        self.message = message
        self.font_size = font_size
        self.status_kind = status_kind
        self._init_ui()
        self._position_frame()

    def _init_ui(self):
        from constants import STATUS_PANEL_RADIUS

        colors = ThemeManager.get_theme_colors()
        accent = ThemeManager.get_status_color(self.status_kind)

        panel = wx.Panel(self)
        panel.SetBackgroundColour(colors["surface"])
        root_sizer = wx.BoxSizer(wx.HORIZONTAL)

        accent_bar = RoundedPanel(panel, radius=STATUS_PANEL_RADIUS)
        accent_bar.SetBackgroundColour(accent)
        accent_bar.SetMinSize(wx.Size(8, -1))

        text_wrapper = wx.BoxSizer(wx.VERTICAL)
        status_text = wx.StaticText(panel, label=self.message, style=wx.ALIGN_LEFT)
        status_font = wx.Font(
            self.font_size,
            wx.FONTFAMILY_SWISS,
            wx.FONTSTYLE_NORMAL,
            wx.FONTWEIGHT_MEDIUM,
            faceName="Malgun Gothic",
        )
        status_text.SetFont(status_font)
        status_text.SetForegroundColour(colors["on_surface"])
        text_wrapper.AddStretchSpacer(1)
        text_wrapper.Add(status_text, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 14)
        text_wrapper.AddStretchSpacer(1)

        root_sizer.Add(accent_bar, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 6)
        root_sizer.Add(text_wrapper, 1, wx.EXPAND)
        panel.SetSizer(root_sizer)

        frame_sizer = wx.BoxSizer(wx.VERTICAL)
        frame_sizer.Add(panel, 1, wx.EXPAND | wx.ALL, 0)
        self.SetSizer(frame_sizer)
        self.panel = panel

    def _position_frame(self):
        from constants import STATUS_FRAME_WIDTH, STATUS_OFFSET_Y

        frame_pos = self.parent.GetPosition()
        frame_size = self.parent.GetSize()
        x = frame_pos[0] + (frame_size[0] - self.GetSize()[0]) // 2
        y = frame_pos[1] + STATUS_OFFSET_Y
        self.SetPosition(wx.Point(x, y))

    def show_temporarily(self, duration: int = 2000):
        """일정 시간 동안 표시 후 자동으로 닫기 (안전하게 처리)"""
        self.Show()

        def safe_close():
            try:
                if self and not self.IsBeingDeleted():
                    self.Close()
            except Exception:
                pass

        wx.CallLater(duration, safe_close)
