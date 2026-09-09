"""
UI 관리 기능을 담당하는 모듈입니다.
메인 윈도우와 사용자 인터페이스를 관리합니다.
"""

# mypy: ignore-errors
# pylint: skip-file
# pyright: reportOptionalMemberAccess=false, reportArgumentType=false, reportCallIssue=false, reportAttributeAccessIssue=false
import wx
from typing import Optional
from constants import (
    KEY_COLUMN_RATIO,
    INPUT_FIELD_WIDTH,
    DEFAULT_FONT_SIZE,
    LABEL_FONT_SIZE_OFFSET,
    STATUS_DISPLAY_TIME,
)
from theme_manager import ThemeManager
from data_manager import DataManager


from appearance import AppearanceSettings
from glass_ui import GlassButton, GlassFrame, GlassPanel, TitleBar
from windows_effects import apply_backdrop


class UIManager:
    """사용자 인터페이스 관리 클래스"""

    def __init__(
        self, app: wx.App, data_manager: DataManager, font_size: int = DEFAULT_FONT_SIZE
    ):
        self.app = app
        self.data_manager = data_manager
        self.appearance = AppearanceSettings()
        ThemeManager.preference = self.appearance.values["theme"]
        ThemeManager.panel_density = self.appearance.values["panel_density"]
        # 저장된 값이 과도하게 크면 UI가 깨지므로 기본값을 상한으로 사용
        self.font_size = min(self.data_manager.get_font_size(), DEFAULT_FONT_SIZE)
        self.selected_index: Optional[int] = None
        self.is_edit_mode = False

        # UI 컴포넌트들
        self.frame: Optional[wx.Frame] = None
        self.main_panel: Optional[wx.Panel] = None
        self.input_panel: Optional[wx.Panel] = None
        self.key_text: Optional[wx.TextCtrl] = None
        self.value_text: Optional[wx.TextCtrl] = None
        self.add_button: Optional[wx.Button] = None
        self.new_button: Optional[wx.Button] = None
        self.save_button: Optional[wx.Button] = None
        self.delete_button: Optional[wx.Button] = None
        self.data_list_ctrl: Optional[wx.ListCtrl] = None
        self.status_label: Optional[wx.StaticText] = None
        self.font: Optional[wx.Font] = None
        self.status_clear_timer = None

        self.init_ui()
        self.setup_event_handlers()

    def init_ui(self) -> None:
        """UI 초기화"""
        self._create_main_frame()
        self._create_panels()
        self._init_controls()
        self._layout_controls()
        self._apply_theme()
        self.frame.Show()
        self._apply_backdrop()

    def _create_main_frame(self) -> None:
        """메인 프레임 생성"""
        self.frame = GlassFrame()
        self.frame.SetSize(self.frame.FromDIP((380, 620)))
        self.frame.SetMinSize(self.frame.FromDIP((360, 500)))
        self.app.SetTopWindow(self.frame)
        self.frame.Centre()

    def _create_panels(self) -> None:
        """패널들 생성"""
        self.main_panel = wx.Panel(self.frame)
        self.title_bar = TitleBar(self.main_panel, self.frame, self.on_settings)
        self.list_panel = GlassPanel(self.main_panel)
        self.library_title = wx.StaticText(self.list_panel, label="저장한 텍스트")
        self.library_hint = wx.StaticText(
            self.list_panel, label="항목을 선택하면 바로 복사됩니다."
        )
        self.library_title.SetFont(
            wx.Font(14, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        )
        self.main_panel.SetBackgroundColour(ThemeManager.get_background_color())

        self.status_label = wx.StaticText(self.main_panel, label="")
        self.status_label.SetMinSize(self.frame.FromDIP((-1, 22)))

        self.input_panel = GlassPanel(self.main_panel)
        self.input_panel.SetBackgroundColour(ThemeManager.get_background_color())
        self.input_panel.Hide()

    def _init_controls(self) -> None:
        """컨트롤들 초기화"""
        self._init_text_controls()
        self._init_buttons()
        self._init_list_control()
        self._init_font()
        self.refresh_listctrl()

    def _init_text_controls(self) -> None:
        """텍스트 컨트롤 초기화"""
        colors = ThemeManager.get_theme_colors()

        self.key_text = wx.TextCtrl(
            self.input_panel,
            size=(INPUT_FIELD_WIDTH, -1),
            style=wx.TE_PROCESS_ENTER | wx.BORDER_THEME,
        )
        self.value_text = wx.TextCtrl(
            self.input_panel,
            size=(INPUT_FIELD_WIDTH, -1),
            style=wx.TE_PROCESS_ENTER | wx.BORDER_THEME,
        )

        # 색상 설정
        for text_ctrl in [self.key_text, self.value_text]:
            text_ctrl.SetBackgroundColour(colors["input_background"])
            text_ctrl.SetForegroundColour(colors["text"])

        # 이벤트 바인딩
        self.key_text.Bind(wx.EVT_TEXT_ENTER, lambda e: self.value_text.SetFocus())
        self.value_text.Bind(wx.EVT_TEXT_ENTER, self.on_save)

    def _init_buttons(self) -> None:
        """버튼들 초기화"""
        BUTTON_HEIGHT = self.frame.FromDIP(38)
        self.add_button = GlassButton(
            self.main_panel,
            label="추가",
            style=wx.BORDER_NONE,
            size=(-1, BUTTON_HEIGHT),
        )
        self.add_button.SetMinSize((-1, BUTTON_HEIGHT))
        self.add_button.SetMaxSize((-1, BUTTON_HEIGHT))
        self.new_button = GlassButton(
            self.input_panel, label="새 항목", style=wx.BORDER_NONE
        )
        self.save_button = GlassButton(
            self.input_panel, label="저장", style=wx.BORDER_NONE
        )
        self.delete_button = GlassButton(
            self.input_panel, label="삭제", style=wx.BORDER_NONE
        )

        # 버튼들 높이 맞추기
        for btn in [self.new_button, self.save_button, self.delete_button]:
            btn.SetMinSize((-1, BUTTON_HEIGHT))
            btn.SetMaxSize((-1, BUTTON_HEIGHT))
            btn.SetSize(-1, BUTTON_HEIGHT)

    def _init_list_control(self) -> None:
        """리스트 컨트롤 초기화"""
        self.data_list_ctrl = wx.ListCtrl(
            self.list_panel,
            style=wx.LC_REPORT | wx.BORDER_NONE | wx.LC_SINGLE_SEL,
        )

        # 컬럼 설정 (초기값, 이후 동적으로 조정)
        self.data_list_ctrl.InsertColumn(0, "이름", width=100)
        self.data_list_ctrl.InsertColumn(1, "내용", width=100)

        colors = ThemeManager.get_theme_colors()
        self.data_list_ctrl.SetBackgroundColour(colors["list_background"])
        self.data_list_ctrl.SetForegroundColour(colors["text"])

        # 이벤트 바인딩
        self.data_list_ctrl.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_listctrl_click)
        self.data_list_ctrl.Bind(wx.EVT_SIZE, self.on_listctrl_resize)

    def _init_font(self) -> None:
        """폰트 초기화"""
        self.font = wx.Font(
            self.font_size,
            wx.FONTFAMILY_DEFAULT,
            wx.FONTSTYLE_NORMAL,
            wx.FONTWEIGHT_NORMAL,
            faceName="Malgun Gothic",
        )

        # 폰트 적용
        self.data_list_ctrl.SetFont(self.font)
        self.key_text.SetFont(self.font)
        self.value_text.SetFont(self.font)

        # 폰트 기준으로 입력 필드 높이를 계산해 글자 잘림 방지
        input_height = max(
            self.frame.FromDIP(34),
            self.font.GetPixelSize().GetHeight() + self.frame.FromDIP(14),
        )
        for text_ctrl in [self.key_text, self.value_text]:
            text_ctrl.SetMinSize(wx.Size(-1, input_height))
            text_ctrl.SetSize(wx.Size(-1, input_height))

    def _layout_controls(self) -> None:
        """컨트롤 레이아웃 설정"""
        margin = self.frame.FromDIP(12)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.title_bar, 0, wx.EXPAND | wx.ALL, margin)
        list_sizer = wx.BoxSizer(wx.VERTICAL)
        list_sizer.Add(self.library_title, 0, wx.ALL, margin)
        list_sizer.Add(self.library_hint, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, margin)
        list_sizer.Add(
            self.data_list_ctrl, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, margin
        )
        self.list_panel.SetSizer(list_sizer)
        main_sizer.Add(self.list_panel, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, margin)
        main_sizer.Add(self.status_label, 0, wx.EXPAND | wx.ALL, margin)
        main_sizer.Add(self.input_panel, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, margin)
        main_sizer.Add(self.add_button, 0, wx.EXPAND | wx.ALL, margin)
        self.main_panel.SetSizer(main_sizer)
        frame_sizer = wx.BoxSizer(wx.VERTICAL)
        frame_sizer.Add(self.main_panel, 1, wx.EXPAND)
        self.frame.SetSizer(frame_sizer)
        self._layout_input_panel()

    def _layout_input_panel(self) -> None:
        """입력 패널 레이아웃 설정"""
        button_gap = self.frame.FromDIP(6)
        field_inner_gap = self.frame.FromDIP(6)
        section_gap = self.frame.FromDIP(8)

        # 라벨 생성
        key_label = wx.StaticText(self.input_panel, label="이름")
        value_label = wx.StaticText(self.input_panel, label="내용")

        # 라벨 폰트 설정
        label_font = wx.Font(
            self.font_size + LABEL_FONT_SIZE_OFFSET,
            wx.FONTFAMILY_DEFAULT,
            wx.FONTSTYLE_NORMAL,
            wx.FONTWEIGHT_NORMAL,
        )
        key_label.SetFont(label_font)
        value_label.SetFont(label_font)

        # 라벨 스타일 설정
        for label in [key_label, value_label]:
            label.SetMinSize(self.frame.FromDIP((43, -1)))

        # 입력 박스 레이아웃
        input_sizer = wx.BoxSizer(wx.VERTICAL)

        # KEY 입력 박스
        input_box_key = wx.BoxSizer(wx.HORIZONTAL)
        input_box_key.Add(
            key_label,
            0,
            wx.ALIGN_CENTER_VERTICAL,
            0,
        )
        input_box_key.AddSpacer(field_inner_gap)
        input_box_key.Add(
            self.key_text,
            1,
            wx.EXPAND,
            0,
        )

        # VALUE 입력 박스
        input_box_value = wx.BoxSizer(wx.HORIZONTAL)
        input_box_value.Add(
            value_label,
            0,
            wx.ALIGN_CENTER_VERTICAL,
            0,
        )
        input_box_value.AddSpacer(field_inner_gap)
        input_box_value.Add(
            self.value_text,
            1,
            wx.EXPAND,
            0,
        )

        # 버튼 레이아웃
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.Add(self.new_button, 1, wx.EXPAND)
        button_sizer.AddSpacer(button_gap)
        button_sizer.Add(self.save_button, 1, wx.EXPAND)
        button_sizer.AddSpacer(button_gap)
        button_sizer.Add(self.delete_button, 1, wx.EXPAND)

        # 전체 레이아웃 조합
        input_sizer.Add(input_box_key, 0, wx.EXPAND)
        input_sizer.Add(input_box_value, 0, wx.EXPAND | wx.TOP, section_gap)
        input_sizer.Add(button_sizer, 0, wx.EXPAND | wx.TOP, section_gap)
        wrapper = wx.BoxSizer(wx.VERTICAL)
        wrapper.Add(input_sizer, 1, wx.EXPAND | wx.ALL, self.frame.FromDIP(12))
        self.input_panel.SetSizer(wrapper)

    def _apply_theme(self) -> None:
        """테마 적용"""
        colors = ThemeManager.get_theme_colors()

        self.frame.SetBackgroundColour(colors["background"])
        self.main_panel.SetBackgroundColour(colors["background"])
        self.input_panel.SetBackgroundColour(colors["surface"])
        self.list_panel.SetBackgroundColour(colors["surface"])
        self.title_bar.apply_theme(colors)
        for panel in (self.input_panel, self.list_panel):
            for child in panel.GetChildren():
                if isinstance(child, wx.StaticText):
                    child.SetBackgroundColour(colors["surface"])
                    child.SetForegroundColour(colors["on_surface_variant"])
        self.library_title.SetForegroundColour(colors["text"])

        # 기본 폰트 및 리스트 스타일
        self.data_list_ctrl.SetBackgroundColour(colors["surface"])
        self.data_list_ctrl.SetForegroundColour(colors["on_surface"])
        self.data_list_ctrl.SetFont(self.font)
        self.key_text.SetFont(self.font)
        self.value_text.SetFont(self.font)
        self.status_label.SetFont(self.font)
        self.status_label.SetForegroundColour(colors["on_surface_variant"])

        # 입력 필드 스타일
        for text_ctrl in [self.key_text, self.value_text]:
            text_ctrl.SetBackgroundColour(colors["input_background"])
            text_ctrl.SetForegroundColour(colors["on_surface"])

        # 일반 버튼들 (추가/새로/저장)
        for btn in [self.add_button, self.save_button]:
            btn.SetBackgroundColour(colors["primary"])
            btn.SetForegroundColour(colors["on_primary"])
            try:
                btn.SetFont(self.font.Bold())
            except Exception:
                pass

        self.new_button.SetBackgroundColour(colors["surface_variant"])
        self.new_button.SetForegroundColour(colors["text"])
        self.delete_button.SetBackgroundColour(colors["surface_variant"])
        self.delete_button.SetForegroundColour(colors["danger"])
        try:
            self.delete_button.SetFont(self.font.Bold())
        except Exception:
            pass

    def setup_event_handlers(self) -> None:
        """이벤트 핸들러 설정"""
        self.add_button.Bind(wx.EVT_BUTTON, self.on_add_button_click)
        self.new_button.Bind(wx.EVT_BUTTON, self.on_new_button_click)
        self.save_button.Bind(wx.EVT_BUTTON, self.on_save)
        self.delete_button.Bind(wx.EVT_BUTTON, self.on_delete)
        self.frame.Bind(wx.EVT_SIZE, self.on_frame_resize)
        self.frame.Bind(wx.EVT_MAXIMIZE, self.on_frame_maximize)
        self.frame.Bind(wx.EVT_CLOSE, self.on_close)
        self.frame.Bind(wx.EVT_SYS_COLOUR_CHANGED, self.on_system_theme)
        self.frame.Bind(wx.EVT_ACTIVATE, self.on_activate)

    def on_frame_resize(self, event) -> None:
        event.Skip()

    def on_frame_maximize(self, event) -> None:
        event.Skip()

    def on_listctrl_resize(self, event):
        """리스트 컨트롤 크기 변경 시 컬럼 너비를 동적으로 조정"""
        total_width = self.data_list_ctrl.GetClientSize().GetWidth()
        key_width = int(total_width * KEY_COLUMN_RATIO)
        value_width = total_width - key_width
        self.data_list_ctrl.SetColumnWidth(0, key_width)
        self.data_list_ctrl.SetColumnWidth(1, value_width)
        event.Skip()

    def refresh_listctrl(self) -> None:
        """리스트 컨트롤 새로고침 (가로 스크롤 없이, VALUE는 ... 처리)"""
        self.data_list_ctrl.DeleteAllItems()
        self.data_manager.refresh_data()

        # 컬럼 너비 측정 (항상 최신 크기로)
        total_width = self.data_list_ctrl.GetClientSize().GetWidth()
        key_width = int(total_width * KEY_COLUMN_RATIO)
        value_col_width = total_width - key_width
        self.data_list_ctrl.SetColumnWidth(0, key_width)
        self.data_list_ctrl.SetColumnWidth(1, value_col_width)
        dc = wx.ClientDC(self.data_list_ctrl)
        dc.SetFont(self.data_list_ctrl.GetFont())

        items = self.data_manager.get_items()
        self.library_title.SetLabel(f"저장한 텍스트 · {len(items)}")
        self.library_hint.SetLabel(
            "항목을 선택하면 바로 복사됩니다."
            if items
            else "아래 추가 버튼으로 첫 텍스트를 저장하세요."
        )
        for item in items:
            idx = self.data_list_ctrl.InsertItem(
                self.data_list_ctrl.GetItemCount(), item["key"]
            )
            value = item["value"]
            # 텍스트 픽셀 길이 측정
            text_width, _ = dc.GetTextExtent(value)
            if text_width > value_col_width - 10:
                # ...을 붙여서 잘라내기
                ellipsis = "..."
                max_width = value_col_width - dc.GetTextExtent(ellipsis)[0] - 10
                short_value = ""
                for ch in value:
                    w, _ = dc.GetTextExtent(short_value + ch)
                    if w > max_width:
                        break
                    short_value += ch
                value = short_value + ellipsis
            self.data_list_ctrl.SetItem(idx, 1, value)

        # 가로 스크롤바가 나오지 않도록 스타일을 강제
        self.data_list_ctrl.SetScrollbar(wx.HORIZONTAL, 0, 0, 0, True)

    def on_add_button_click(self, event) -> None:
        """Add 버튼 클릭 이벤트"""
        if self.input_panel.IsShown():
            self.input_panel.Hide()
            self.add_button.SetLabel("추가")
            self.selected_index = None
            self.is_edit_mode = False
        else:
            self.input_panel.Show()
            self.add_button.SetLabel("닫기")
            self.key_text.SetFocus()
        self.main_panel.Layout()

    def on_new_button_click(self, event) -> None:
        """New 버튼 클릭 시 입력창을 비우고 새 항목 추가 모드로 전환"""
        self.key_text.SetValue("")
        self.value_text.SetValue("")
        self.selected_index = None
        self.is_edit_mode = False
        self.key_text.SetFocus()

    def on_save(self, event) -> None:
        """Save 버튼 클릭 이벤트"""
        key = self.key_text.GetValue().strip()
        value = self.value_text.GetValue().strip()

        if key or value:  # 둘 중 하나라도 값이 있으면 저장
            success = False

            if self.is_edit_mode and self.selected_index is not None:
                # 수정 모드
                success = self.data_manager.update_item(self.selected_index, key, value)
            else:
                # 추가 모드
                success = self.data_manager.add_item(key, value)

            if success:
                self.key_text.Clear()
                self.value_text.Clear()
                self.selected_index = None
                self.is_edit_mode = False
                self.refresh_listctrl()
                self.key_text.SetFocus()
                self.show_copy_status("저장을 완료했습니다.", "success")
            else:
                self.show_copy_status("저장에 실패했습니다.", "error")

    def on_listctrl_click(self, event) -> None:
        """리스트 항목 클릭 이벤트"""
        self.selected_index = event.GetIndex()
        self.show_input_fields()

        # 클립보드에는 리스트 표시값(...)이 아닌 원본 값을 복사
        selected_item = self._get_selected_item()
        if selected_item is None:
            self.show_copy_status("선택한 항목을 찾을 수 없습니다.", "error")
            return
        value = selected_item["value"]

        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(wx.TextDataObject(value))
            wx.TheClipboard.Close()
            self.show_copy_status("클립보드에 복사했습니다.", "success")
        else:
            wx.MessageBox(
                "클립보드에 접근할 수 없습니다.", "오류", wx.OK | wx.ICON_ERROR
            )

    def on_delete(self, event) -> None:
        """Delete 버튼 클릭 이벤트"""
        selected_index = self.data_list_ctrl.GetFirstSelected()
        if selected_index != -1:
            if self.data_manager.delete_data(selected_index):
                self.refresh_listctrl()
                if self.selected_index == selected_index:
                    self.selected_index = None
                    self.is_edit_mode = False
                self.show_copy_status("항목을 삭제했습니다.", "success")
            else:
                self.show_copy_status("삭제에 실패했습니다.", "error")

    def show_input_fields(self) -> None:
        """입력 필드 표시"""
        self.input_panel.Show()
        self.add_button.SetLabel("닫기")
        self.main_panel.Layout()
        self.key_text.Show()
        self.value_text.Show()
        self.save_button.Show()

        # 선택된 항목이 있으면 입력창에 값 채우기
        selected_item = self._get_selected_item()
        if selected_item is not None:
            self.key_text.SetValue(selected_item["key"])
            self.value_text.SetValue(selected_item["value"])
            self.is_edit_mode = True
        else:
            self.key_text.SetValue("")
            self.value_text.SetValue("")
            self.is_edit_mode = False

        self.key_text.SetFocus()

    def _get_selected_item(self) -> Optional[dict]:
        """현재 선택 인덱스의 원본 항목 반환"""
        if self.selected_index is None:
            return None
        items = self.data_manager.get_items()
        if 0 <= self.selected_index < len(items):
            return items[self.selected_index]
        return None

    def show_copy_status(self, message: str, status_kind: str = "info") -> None:
        """복사 상태 메시지 표시"""
        colors = ThemeManager.get_theme_colors()
        self.status_label.SetLabel(f"  {message}")
        if status_kind == "success":
            self.status_label.SetForegroundColour(colors["success"])
        elif status_kind == "error":
            self.status_label.SetForegroundColour(colors["danger"])
        else:
            self.status_label.SetForegroundColour(colors["primary"])
        self.main_panel.Layout()

        if self.status_clear_timer is not None:
            try:
                self.status_clear_timer.Stop()
            except Exception:
                pass
        self.status_clear_timer = wx.CallLater(
            STATUS_DISPLAY_TIME, self._clear_status_message
        )

    def _clear_status_message(self) -> None:
        colors = ThemeManager.get_theme_colors()
        self.status_label.SetLabel("")
        self.status_label.SetForegroundColour(colors["on_surface_variant"])
        self.main_panel.Layout()

    def _apply_backdrop(self):
        dark = ThemeManager.preference == "dark" or (
            ThemeManager.preference == "system" and ThemeManager.is_dark_mode()
        )
        self.backdrop_active = apply_backdrop(
            self.frame.GetHandle(), self.appearance.values["backdrop"], dark
        )
        # Zero RGB GDI background exposes DWM in the gutters between panels.
        color = (
            wx.BLACK if self.backdrop_active else ThemeManager.get_background_color()
        )
        self.frame.SetBackgroundColour(color)
        self.main_panel.SetBackgroundColour(color)
        self.status_label.SetBackgroundColour(ThemeManager.get_background_color())
        self.main_panel.Refresh()

    def on_activate(self, event):
        self._apply_backdrop()
        event.Skip()

    def on_system_theme(self, event):
        self._apply_theme()
        self._apply_backdrop()
        event.Skip()

    def on_close(self, event):
        if self.status_clear_timer:
            self.status_clear_timer.Stop()
        event.Skip()

    def on_settings(self, event):
        from settings_dialog import SettingsDialog

        dialog = SettingsDialog(
            self.frame, self.appearance.values, self.backdrop_active
        )
        try:
            if dialog.ShowModal() == wx.ID_OK:
                try:
                    self.appearance.save(dialog.values())
                except OSError as error:
                    wx.MessageBox(
                        f"설정을 저장할 수 없습니다.\n{error}",
                        "환경 설정",
                        wx.OK | wx.ICON_ERROR,
                    )
                    return
                ThemeManager.preference = self.appearance.values["theme"]
                ThemeManager.panel_density = self.appearance.values["panel_density"]
                self._apply_theme()
                self._apply_backdrop()
                self.frame.Refresh()
                self.show_copy_status("환경 설정을 저장했습니다.", "success")
        finally:
            dialog.Destroy()
