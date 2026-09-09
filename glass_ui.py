"""Reusable frosted panels, keyboard accessible buttons and custom caption."""

import wx
from wx.lib.buttons import GenButton
from theme_manager import ThemeManager


class GlassButton(GenButton):
    def __init__(self, parent, label, **kwargs):
        kwargs.pop("style", None)
        super().__init__(parent, label=label, style=wx.BORDER_NONE, **kwargs)
        self.SetBezelWidth(1)
        self.SetMinSize(self.FromDIP((44, 36)))
        self.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        self.SetName(label)

    def GetBackgroundBrush(self, dc):
        return wx.Brush(self.GetParent().GetBackgroundColour())

    def DrawBezel(self, dc, x1, y1, x2, y2):
        color = self.GetBackgroundColour()
        if not self.up:
            color = color.ChangeLightness(90)
        dc.SetBrush(wx.Brush(color))
        dc.SetPen(wx.Pen(ThemeManager.get_theme_colors()["border"]))
        dc.DrawRoundedRectangle(x1, y1, x2 - x1, y2 - y1, self.FromDIP(12))


class GlassPanel(wx.Panel):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.Bind(wx.EVT_PAINT, self._paint)
        self.Bind(wx.EVT_SIZE, self._size)

    def _size(self, event):
        self.Refresh()
        event.Skip()

    def _paint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        dc.SetBackground(wx.Brush(self.GetParent().GetBackgroundColour()))
        dc.Clear()
        gc = wx.GraphicsContext.Create(dc)
        if gc:
            colors = ThemeManager.get_theme_colors()
            gc.SetBrush(wx.Brush(self.GetBackgroundColour()))
            gc.SetPen(wx.Pen(colors["border"]))
            width, height = self.GetClientSize()
            gc.DrawRoundedRectangle(
                1, 1, max(0, width - 2), max(0, height - 2), self.FromDIP(18)
            )


class GlassFrame(wx.Frame):
    def __init__(self):
        style = wx.DEFAULT_FRAME_STYLE & ~wx.CAPTION
        super().__init__(None, title="Copy & Paste", style=style)


class TitleBar(GlassPanel):
    def __init__(self, parent, frame, on_settings):
        super().__init__(parent)
        self.frame = frame
        self.drag_origin = None
        row = wx.BoxSizer(wx.HORIZONTAL)
        self.title = wx.StaticText(self, label="Copy & Paste")
        self.title.SetFont(
            wx.Font(11, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        )
        row.Add(self.title, 1, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, self.FromDIP(14))
        self.buttons = []
        for label, name, callback in (
            ("⚙", "환경 설정", on_settings),
            ("−", "최소화", lambda e: frame.Iconize()),
            ("□", "최대화 / 복원", self.toggle_maximize),
            ("×", "닫기", lambda e: frame.Close()),
        ):
            button = GlassButton(self, label=label, size=self.FromDIP((36, 32)))
            button.SetMinSize(self.FromDIP((36, 32)))
            button.SetToolTip(name)
            button.SetName(name)
            button.Bind(wx.EVT_BUTTON, callback)
            row.Add(button, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, self.FromDIP(4))
            self.buttons.append(button)
        self.SetSizer(row)
        self.SetMinSize(self.FromDIP((-1, 52)))
        for target in (self, self.title):
            target.Bind(wx.EVT_LEFT_DOWN, self.start_drag)
            target.Bind(wx.EVT_LEFT_DCLICK, self.toggle_maximize)
            target.Bind(wx.EVT_MOTION, self.drag)
            target.Bind(wx.EVT_LEFT_UP, self.end_drag)
            target.Bind(wx.EVT_MOUSE_CAPTURE_LOST, self.capture_lost)

    def toggle_maximize(self, event):
        self.frame.Maximize(not self.frame.IsMaximized())
        self.buttons[2].SetLabel("❐" if self.frame.IsMaximized() else "□")

    def start_drag(self, event):
        if not self.frame.IsMaximized():
            self.drag_origin = wx.GetMousePosition() - self.frame.GetPosition()
            event.GetEventObject().CaptureMouse()

    def drag(self, event):
        if self.drag_origin is not None and event.Dragging() and event.LeftIsDown():
            self.frame.Move(wx.GetMousePosition() - self.drag_origin)

    def end_drag(self, event):
        target = event.GetEventObject()
        if target.HasCapture():
            target.ReleaseMouse()
        self.drag_origin = None

    def capture_lost(self, event):
        self.drag_origin = None

    def apply_theme(self, colors):
        self.SetBackgroundColour(colors["surface"])
        self.title.SetBackgroundColour(colors["surface"])
        self.title.SetForegroundColour(colors["text"])
        for button in self.buttons:
            button.SetBackgroundColour(colors["surface"])
            button.SetForegroundColour(colors["text"])
        self.Refresh()
