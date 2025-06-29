"""
UI 관리 기능을 담당하는 모듈입니다.
메인 윈도우와 사용자 인터페이스를 관리합니다.
"""

import wx
from typing import Optional
from constants import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    WINDOW_MIN_HEIGHT,
    WINDOW_MARGIN_X,
    WINDOW_MARGIN_Y,
    KEY_COLUMN_RATIO,
    VALUE_COLUMN_RATIO,
    INPUT_FIELD_WIDTH,
    DEFAULT_FONT_SIZE,
    LABEL_FONT_SIZE_OFFSET,
    PANEL_MARGIN,
    STATUS_DISPLAY_TIME,
    STATUS_FRAME_HEIGHT,
)
from theme_manager import ThemeManager
from ui_components import StatusFrame
from data_manager import DataManager


# 시스템 테마에 따른 동적 색상 설정
def get_theme_colors():
    """시스템 테마에 따라 색상을 반환"""
    # macOS에서 다크모드 감지
    if wx.Platform == "__WXMAC__":
        try:
            import subprocess

            result = subprocess.run(
                ["defaults", "read", "-g", "AppleInterfaceStyle"],
                capture_output=True,
                text=True,
            )
            is_dark = result.stdout.strip() == "Dark"
        except:
            is_dark = False
    # Windows에서 다크모드 감지
    elif wx.Platform == "__WXMSW__":
        try:
            import winreg

            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
            )
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            is_dark = value == 0
            winreg.CloseKey(key)
        except:
            is_dark = False
    else:
        is_dark = False

    if is_dark:
        # 다크모드 색상
        return {
            "primary": wx.Colour(33, 150, 243),  # Material Blue 500
            "background": wx.Colour(30, 30, 30),  # 어두운 배경
            "list_background": wx.Colour(45, 45, 45),  # 어두운 리스트 배경
            "text": wx.Colour(255, 255, 255),  # 흰색 텍스트
            "input_background": wx.Colour(50, 50, 50),  # 어두운 입력 필드
            "border": wx.Colour(70, 70, 70),  # 어두운 테두리
        }
    else:
        # 라이트모드 색상
        return {
            "primary": wx.Colour(33, 150, 243),  # Material Blue 500
            "background": wx.Colour(250, 250, 250),  # 밝은 배경
            "list_background": wx.Colour(245, 245, 245),  # 밝은 리스트 배경
            "text": wx.Colour(0, 0, 0),  # 검은색 텍스트
            "input_background": wx.Colour(255, 255, 255),  # 흰색 입력 필드
            "border": wx.Colour(200, 200, 200),  # 밝은 테두리
        }


# 기존 색상 상수 제거하고 함수로 대체
def get_primary_color():
    return get_theme_colors()["primary"]


def get_background_color():
    return get_theme_colors()["background"]


def get_list_background_color():
    return get_theme_colors()["list_background"]


class RoundedPanel(wx.Panel):
    def __init__(self, parent, radius=10, **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)
        self.radius = radius
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)

    def OnPaint(self, event):
        dc = wx.BufferedPaintDC(self)
        self.DrawRoundedRectangle(dc)

    def OnSize(self, event):
        self.Refresh()

    def DrawRoundedRectangle(self, dc):
        dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
        dc.Clear()

        width, height = self.GetSize()

        # 둥근 사각형 그리기
        dc.SetBrush(wx.Brush(self.GetBackgroundColour()))
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.DrawRoundedRectangle(0, 0, width, height, self.radius)


class UIManager:
    """사용자 인터페이스 관리 클래스"""

    def __init__(
        self, app: wx.App, data_manager: DataManager, font_size: int = DEFAULT_FONT_SIZE
    ):
        self.app = app
        self.data_manager = data_manager
        # 폰트 크기를 data_manager에서 읽어옴
        self.font_size = self.data_manager.get_font_size()
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
        self.font: Optional[wx.Font] = None
        self.status_frame = None

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

    def _create_main_frame(self) -> None:
        """메인 프레임 생성"""
        self.frame = wx.Frame(None, title="복붙")
        self.frame.SetSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.frame.SetMinSize((WINDOW_WIDTH, WINDOW_MIN_HEIGHT))
        self.frame.SetMaxSize((WINDOW_WIDTH, -1))

        # 화면 중앙에 위치
        screen_width, screen_height = wx.GetDisplaySize()
        x = screen_width - WINDOW_WIDTH - WINDOW_MARGIN_X
        y = screen_height - WINDOW_HEIGHT - WINDOW_MARGIN_Y
        self.frame.SetPosition(wx.Point(x, y))

    def _create_panels(self) -> None:
        """패널들 생성"""
        self.main_panel = wx.Panel(self.frame)
        self.main_panel.SetBackgroundColour(ThemeManager.get_background_color())

        self.input_panel = wx.Panel(self.main_panel)
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
            style=wx.TE_PROCESS_ENTER | wx.BORDER_SIMPLE,
        )
        self.value_text = wx.TextCtrl(
            self.input_panel,
            size=(INPUT_FIELD_WIDTH, -1),
            style=wx.TE_PROCESS_ENTER | wx.BORDER_SIMPLE,
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
        BUTTON_WIDTH = int(WINDOW_WIDTH / 3)
        BUTTON_HEIGHT = 30
        self.add_button = wx.Button(self.main_panel, label="Add", style=wx.BORDER_NONE)
        self.new_button = wx.Button(self.input_panel, label="New", style=wx.BORDER_NONE)
        self.save_button = wx.Button(
            self.input_panel, label="Save", style=wx.BORDER_NONE
        )
        self.delete_button = wx.Button(
            self.input_panel, label="Delete", style=wx.BORDER_NONE
        )

        # 버튼 크기를 강제로 고정
        for btn in [self.new_button, self.save_button, self.delete_button]:
            btn.SetSize(BUTTON_WIDTH, BUTTON_HEIGHT)
            btn.SetMinSize((BUTTON_WIDTH, BUTTON_HEIGHT))
            btn.SetMaxSize((BUTTON_WIDTH, BUTTON_HEIGHT))

    def _init_list_control(self) -> None:
        """리스트 컨트롤 초기화"""
        self.data_list_ctrl = wx.ListCtrl(
            self.main_panel,
            style=wx.LC_REPORT | wx.BORDER_NONE | wx.LC_SINGLE_SEL,
        )

        # 컬럼 설정 (초기값, 이후 동적으로 조정)
        self.data_list_ctrl.InsertColumn(0, "KEY", width=100)
        self.data_list_ctrl.InsertColumn(1, "VALUE", width=100)

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
        )

        # 폰트 적용
        self.data_list_ctrl.SetFont(self.font)
        self.key_text.SetFont(self.font)
        self.value_text.SetFont(self.font)

    def _layout_controls(self) -> None:
        """컨트롤 레이아웃 설정"""
        # 메인 레이아웃
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.data_list_ctrl, 1, wx.EXPAND | wx.ALL, PANEL_MARGIN)
        main_sizer.Add(self.input_panel, 0, wx.EXPAND)
        main_sizer.Add(self.add_button, 0, wx.ALL | wx.EXPAND, PANEL_MARGIN)
        self.main_panel.SetSizer(main_sizer)

        # 입력 패널 레이아웃
        self._layout_input_panel()

    def _layout_input_panel(self) -> None:
        """입력 패널 레이아웃 설정"""
        # 라벨 생성
        key_label = wx.StaticText(self.input_panel, label="KEY")
        value_label = wx.StaticText(self.input_panel, label="VALUE")

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
            label.SetMinSize((30, -1))
            label.SetWindowStyle(wx.ALIGN_CENTER_VERTICAL)

        # 입력 박스 레이아웃
        input_sizer = wx.BoxSizer(wx.VERTICAL)

        # KEY 입력 박스
        input_box_key = wx.BoxSizer(wx.HORIZONTAL)
        input_box_key.Add(key_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, PANEL_MARGIN)
        input_box_key.Add(self.key_text, 1, wx.ALL | wx.EXPAND, PANEL_MARGIN)

        # VALUE 입력 박스
        input_box_value = wx.BoxSizer(wx.HORIZONTAL)
        input_box_value.Add(
            value_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, PANEL_MARGIN
        )
        input_box_value.Add(self.value_text, 1, wx.ALL | wx.EXPAND, PANEL_MARGIN)

        # 버튼 레이아웃
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.Add(self.new_button, 1, wx.ALL | wx.EXPAND, PANEL_MARGIN)
        button_sizer.Add(self.save_button, 1, wx.ALL | wx.EXPAND, PANEL_MARGIN)
        button_sizer.Add(self.delete_button, 1, wx.ALL | wx.EXPAND, PANEL_MARGIN)

        # 전체 레이아웃 조합
        input_sizer.Add(input_box_key, 1, wx.EXPAND)
        input_sizer.Add(input_box_value, 0, wx.EXPAND)
        input_sizer.Add(button_sizer, 0, wx.EXPAND)
        self.input_panel.SetSizer(input_sizer)

        # 입력 패널 리사이즈 이벤트에 버튼 크기 재조정 핸들러 연결
        self.input_panel.Bind(wx.EVT_SIZE, self._resize_input_buttons)

    def _resize_input_buttons(self, event):
        total_width = self.input_panel.GetClientSize().GetWidth()
        button_width = int((total_width - 4 * PANEL_MARGIN) / 3)
        for btn in [self.new_button, self.save_button, self.delete_button]:
            btn.SetMinSize((button_width, 30))
            btn.SetMaxSize((button_width, 30))
            btn.SetSize(button_width, 30)
        self.input_panel.Layout()
        event.Skip()

    def _apply_theme(self) -> None:
        """테마 적용"""
        colors = ThemeManager.get_theme_colors()

        # 버튼 스타일 적용
        for btn in [
            self.add_button,
            self.new_button,
            self.save_button,
            self.delete_button,
        ]:
            btn.SetBackgroundColour(colors["primary"])
            btn.SetForegroundColour(wx.WHITE)
            try:
                btn.SetFont(self.font.Bold())
            except Exception:
                pass

        # 리스트 컨트롤 스타일 적용
        self.data_list_ctrl.SetBackgroundColour(colors["list_background"])
        self.data_list_ctrl.SetForegroundColour(colors["text"])

        # 프레임 및 패널 배경색 적용
        self.frame.SetBackgroundColour(colors["background"])
        self.main_panel.SetBackgroundColour(colors["background"])
        self.input_panel.SetBackgroundColour(colors["background"])

        # 입력 필드 색상 적용
        if hasattr(self, "key_text"):
            self.key_text.SetBackgroundColour(colors["input_background"])
            self.value_text.SetBackgroundColour(colors["input_background"])
            self.key_text.SetForegroundColour(colors["text"])
            self.value_text.SetForegroundColour(colors["text"])

    def setup_event_handlers(self) -> None:
        """이벤트 핸들러 설정"""
        self.add_button.Bind(wx.EVT_BUTTON, self.on_add_button_click)
        self.new_button.Bind(wx.EVT_BUTTON, self.on_new_button_click)
        self.save_button.Bind(wx.EVT_BUTTON, self.on_save)
        self.delete_button.Bind(wx.EVT_BUTTON, self.on_delete)

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

        for item in self.data_manager.get_items():
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
            self.add_button.SetLabel("Add")
            self.selected_index = None
            self.is_edit_mode = False
        else:
            self.input_panel.Show()
            self.add_button.SetLabel("Cancel")
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
            else:
                wx.MessageBox("저장에 실패했습니다.", "오류", wx.OK | wx.ICON_ERROR)

    def on_listctrl_click(self, event) -> None:
        """리스트 항목 클릭 이벤트"""
        self.selected_index = event.GetIndex()
        self.show_input_fields()

        # 클립보드에 복사
        key = self.data_list_ctrl.GetItemText(self.selected_index)
        value = self.data_list_ctrl.GetItem(self.selected_index, 1).GetText()

        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(wx.TextDataObject(value))
            wx.TheClipboard.Close()
            self.show_copy_status("복사 완료")
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
            else:
                wx.MessageBox("삭제에 실패했습니다.", "오류", wx.OK | wx.ICON_ERROR)

    def show_input_fields(self) -> None:
        """입력 필드 표시"""
        self.key_text.Show()
        self.value_text.Show()
        self.save_button.Show()

        # 선택된 항목이 있으면 입력창에 값 채우기
        if self.selected_index is not None:
            key = self.data_list_ctrl.GetItemText(self.selected_index)
            value = self.data_list_ctrl.GetItem(self.selected_index, 1).GetText()
            self.key_text.SetValue(key)
            self.value_text.SetValue(value)
            self.is_edit_mode = True
        else:
            self.key_text.SetValue("")
            self.value_text.SetValue("")
            self.is_edit_mode = False

        self.key_text.SetFocus()

    def show_copy_status(self, message: str) -> None:
        """복사 상태 메시지 표시"""
        if self.status_frame is not None:
            try:
                self.status_frame.Close()
            except Exception:
                pass
            self.status_frame = None
        self.status_frame = StatusFrame(self.frame, message, self.font_size)
        self.status_frame.show_temporarily(STATUS_DISPLAY_TIME)
