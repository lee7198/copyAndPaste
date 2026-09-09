"""Appearance editor. Cancel leaves saved preferences untouched."""

import wx
from appearance import DEFAULTS
from theme_manager import ThemeManager


class SettingsDialog(wx.Dialog):
    THEMES = ("system", "light", "dark")
    BACKDROPS = ("off", "mica", "acrylic")

    def __init__(self, parent, values, backdrop_active):
        super().__init__(parent, title="환경 설정", style=wx.DEFAULT_DIALOG_STYLE)
        colors = ThemeManager.get_theme_colors()
        self.SetBackgroundColour(colors["surface"])
        self.SetForegroundColour(colors["text"])
        root = wx.BoxSizer(wx.VERTICAL)
        title = wx.StaticText(self, label="나에게 맞는 유리 스타일")
        title.SetFont(title.GetFont().Larger().Bold())
        root.Add(title, 0, wx.ALL, self.FromDIP(20))
        self.theme = wx.Choice(self, choices=["시스템 설정 따르기", "라이트", "다크"])
        self.backdrop = wx.Choice(
            self, choices=["끄기 · 불투명", "은은하게 · Mica", "흐리게 · Acrylic"]
        )
        self.density = wx.Slider(
            self,
            value=80,
            minValue=50,
            maxValue=100,
            style=wx.SL_HORIZONTAL | wx.SL_LABELS,
        )
        for label, control in (
            ("테마", self.theme),
            ("배경 블러", self.backdrop),
            ("패널 색상 농도", self.density),
        ):
            root.Add(
                wx.StaticText(self, label=label),
                0,
                wx.LEFT | wx.RIGHT | wx.TOP,
                self.FromDIP(20),
            )
            root.Add(
                control, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, self.FromDIP(20)
            )
        note = wx.StaticText(
            self,
            label=(
                "배경 블러는 Windows 11 22H2 이상에서 지원됩니다.\n"
                "블러 반경은 Windows가 결정하며, 패널 농도는\n"
                "카드의 색상을 조절합니다. 글자는 흐려지지 않습니다.\n"
                "절전·접근성 설정에 따라 효과가 제한될 수 있습니다."
            ),
        )
        root.Add(note, 0, wx.ALL, self.FromDIP(20))
        if not backdrop_active and values["backdrop"] != "off":
            root.Add(
                wx.StaticText(
                    self, label="현재 환경에서는 불투명 스타일을 사용 중입니다."
                ),
                0,
                wx.LEFT | wx.RIGHT | wx.BOTTOM,
                self.FromDIP(20),
            )
        reset = wx.Button(self, label="기본값 복원")
        reset.Bind(wx.EVT_BUTTON, lambda e: self.load(DEFAULTS))
        root.Add(reset, 0, wx.LEFT | wx.BOTTOM, self.FromDIP(20))
        root.Add(
            self.CreateButtonSizer(wx.OK | wx.CANCEL),
            0,
            wx.EXPAND | wx.ALL,
            self.FromDIP(20),
        )
        self.SetSizerAndFit(root)
        self.CentreOnParent()
        self.load(values)

    def load(self, values):
        self.theme.SetSelection(self.THEMES.index(values["theme"]))
        self.backdrop.SetSelection(self.BACKDROPS.index(values["backdrop"]))
        self.density.SetValue(values["panel_density"])

    def values(self):
        return {
            "theme": self.THEMES[self.theme.GetSelection()],
            "backdrop": self.BACKDROPS[self.backdrop.GetSelection()],
            "panel_density": self.density.GetValue(),
        }
