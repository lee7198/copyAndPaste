import wx
import os

# 간단한 Material 색상 팔레트
PRIMARY_COLOR = wx.Colour(33, 150, 243)  # Material Blue 500
BACKGROUND_COLOR = wx.Colour(250, 250, 250)
LIST_BACKGROUND = wx.Colour(245, 245, 245)


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
    def __init__(self, app, data_manager, font_size=9):
        self.app = app
        self.data_manager = data_manager
        self.font_size = font_size
        self.selected_index = None  # 선택된 항목 인덱스 저장
        self.is_edit_mode = False  # 수정 모드 여부
        self.copy_status_timer = None  # 복사 상태 타이머
        self.set_theme()
        self.init_ui()
        self.setup_event_handlers()

    def set_theme(self):
        self.is_dark = wx.SystemSettings.GetAppearance().IsDark()

    def get_font(self, bold=False):
        weight = wx.FONTWEIGHT_BOLD if bold else wx.FONTWEIGHT_NORMAL
        return wx.Font(
            self.font_size, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, weight, False
        )

    def init_ui(self):
        fix_width = 220
        self.frame = wx.Frame(None, title="복붙")
        self.frame.SetSize(fix_width, 500)
        self.frame.SetMinSize((fix_width, 450))
        self.frame.SetMaxSize((fix_width, -1))

        screen_width, screen_height = wx.GetDisplaySize()
        window_width, window_height = self.frame.GetSize()

        x = screen_width - window_width - 50  # 50은 여백
        y = screen_height - window_height - 150  # 150은 여백

        self.frame.SetPosition(wx.Point(x, y))
        self.frame.SetBackgroundColour(BACKGROUND_COLOR)
        self.main_panel = wx.Panel(self.frame)
        self.main_panel.SetBackgroundColour(BACKGROUND_COLOR)
        self.input_panel = wx.Panel(self.main_panel)
        self.input_panel.SetBackgroundColour(BACKGROUND_COLOR)
        self.input_panel.Hide()
        self.init_controls()
        self.layout_controls()
        self.apply_theme()
        self.frame.Show()

    def init_controls(self):
        fix_width = 100
        # 입력 필드 초기화
        self.key_text = wx.TextCtrl(
            self.input_panel, size=(fix_width, -1), style=wx.BORDER_SIMPLE
        )
        self.value_text = wx.TextCtrl(
            self.input_panel,
            size=(fix_width, -1),
            style=wx.TE_PROCESS_ENTER | wx.BORDER_SIMPLE,
        )
        self.key_text.SetBackgroundColour(wx.WHITE)
        self.value_text.SetBackgroundColour(wx.WHITE)
        self.key_text.Bind(wx.EVT_TEXT_ENTER, self.value_text.SetFocus())
        self.value_text.Bind(wx.EVT_TEXT_ENTER, self.on_save)
        # 버튼 초기화
        self.add_button = wx.Button(self.main_panel, label="Add", style=wx.BORDER_NONE)
        self.save_button = wx.Button(
            self.input_panel, label="Save", style=wx.BORDER_NONE
        )
        self.delete_button = wx.Button(
            self.input_panel, label="Delete", style=wx.BORDER_NONE
        )

        # 리스트 컨트롤(Report 모드) 초기화
        self.data_list_ctrl = wx.ListCtrl(
            self.main_panel,
            style=wx.LC_REPORT | wx.BORDER_NONE | wx.LC_SINGLE_SEL,
        )
        self.data_list_ctrl.InsertColumn(0, "KEY", width=90)
        self.data_list_ctrl.InsertColumn(1, "VALUE", width=100)
        self.data_list_ctrl.SetBackgroundColour(LIST_BACKGROUND)
        # 시스템 기본 폰트 적용
        font = self.get_font()
        self.data_list_ctrl.SetFont(font)
        self.key_text.SetFont(font)
        self.value_text.SetFont(font)
        self.font = font  # 폰트를 인스턴스 변수로 저장
        # 초기 상태 설정
        self.refresh_listctrl()
        # 리스트 클릭 이벤트 바인딩
        self.data_list_ctrl.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_listctrl_click)

    def layout_controls(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        # 리스트와 입력창을 6:4 비율로 배치
        content_sizer = wx.BoxSizer(wx.VERTICAL)
        content_sizer.Add(self.data_list_ctrl, 6, wx.EXPAND | wx.ALL, 5)
        content_sizer.Add(self.input_panel, 4, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(content_sizer, 1, wx.EXPAND)
        main_sizer.Add(self.add_button, 0, wx.ALL | wx.EXPAND, 5)
        self.main_panel.SetSizer(main_sizer)
        # Labels
        key_label = wx.StaticText(self.input_panel, label="KEY")
        value_label = wx.StaticText(self.input_panel, label="VALUE")
        label_font = self.get_font(bold=True)
        try:
            key_label.SetFont(label_font)
            value_label.SetFont(label_font)
        except Exception:
            key_label.SetFont(label_font)
            value_label.SetFont(label_font)
        key_label.SetMinSize((30, -1))
        key_label.SetWindowStyle(wx.ALIGN_CENTER_VERTICAL)
        value_label.SetMinSize((30, -1))
        value_label.SetWindowStyle(wx.ALIGN_CENTER_VERTICAL)
        input_sizer = wx.BoxSizer(wx.VERTICAL)
        input_box_key = wx.BoxSizer(wx.HORIZONTAL)
        input_box_value = wx.BoxSizer(wx.HORIZONTAL)
        input_box_key.Add(key_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        input_box_key.Add(self.key_text, 1, wx.ALL | wx.EXPAND, 5)
        input_box_value.Add(value_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        input_box_value.Add(self.value_text, 1, wx.ALL | wx.EXPAND, 5)
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.Add(self.save_button, 1, wx.ALL | wx.EXPAND, 5)
        button_sizer.Add(self.delete_button, 1, wx.ALL | wx.EXPAND, 5)
        input_sizer.Add(input_box_key, 1, wx.EXPAND)
        input_sizer.Add(input_box_value, 0, wx.EXPAND)
        input_sizer.Add(button_sizer, 0, wx.EXPAND)
        self.input_panel.SetSizer(input_sizer)

    def apply_theme(self):
        """Material-like 색상과 스타일을 적용 (다크모드 지원)"""
        if self.is_dark:
            frame_bg = wx.Colour(30, 30, 30)
            panel_bg = wx.Colour(45, 45, 45)
            list_bg = wx.Colour(50, 50, 50)
            btn_bg = wx.Colour(60, 60, 60)
            btn_fg = wx.Colour(220, 220, 220)
        else:
            frame_bg = BACKGROUND_COLOR
            panel_bg = BACKGROUND_COLOR
            list_bg = LIST_BACKGROUND
            btn_bg = PRIMARY_COLOR
            btn_fg = wx.WHITE
        for btn in (self.add_button, self.save_button, self.delete_button):
            btn.SetBackgroundColour(btn_bg)
            btn.SetForegroundColour(btn_fg)
            try:
                btn.SetFont(self.font.Bold())
            except Exception:
                pass
        self.data_list_ctrl.SetBackgroundColour(list_bg)
        self.frame.SetBackgroundColour(frame_bg)
        self.main_panel.SetBackgroundColour(panel_bg)
        self.input_panel.SetBackgroundColour(panel_bg)

    def hide_input_fields(self):
        self.key_text.Hide()
        self.value_text.Hide()
        self.save_button.Hide()

    def show_input_fields(self):
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

    def refresh_listctrl(self):
        self.data_list_ctrl.DeleteAllItems()
        self.data_manager.refresh_data()
        for item in self.data_manager.get_items():
            idx = self.data_list_ctrl.InsertItem(
                self.data_list_ctrl.GetItemCount(), item["key"]
            )
            self.data_list_ctrl.SetItem(idx, 1, item["value"])

    def setup_event_handlers(self):
        self.add_button.Bind(wx.EVT_BUTTON, self.on_add_button_click)
        self.save_button.Bind(wx.EVT_BUTTON, self.on_save)
        self.delete_button.Bind(wx.EVT_BUTTON, self.on_delete)

    def on_add_button_click(self, event):
        if self.input_panel.IsShown():
            self.input_panel.Hide()
            self.add_button.SetLabel("Add")
        else:
            self.input_panel.Show()
            self.add_button.SetLabel("Cancel")
            self.key_text.SetFocus()
        self.main_panel.Layout()

    def on_save(self, event):
        key = self.key_text.GetValue()
        value = self.value_text.GetValue()
        if key != "" or value != "":
            if self.is_edit_mode and self.selected_index is not None:
                # 수정 모드: 기존 데이터 수정
                self.data_manager.update_item(self.selected_index, key, value)
            else:
                # 추가 모드: 새 데이터 추가
                self.data_manager.add_item(key, value)
            self.key_text.Clear()
            self.value_text.Clear()
            self.key_text.SetFocus()
            self.selected_index = None
            self.is_edit_mode = False
            self.refresh_listctrl()

    def on_tab_next(self):
        self.value_text.SetFocus()

    def on_listctrl_click(self, event):
        self.selected_index = event.GetIndex()
        self.show_input_fields()  # 항목 클릭 시 입력창 열기
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

    def on_delete(self, event):
        selected_index = self.data_list_ctrl.GetFirstSelected()
        if selected_index != -1:
            self.data_manager.delete_data(selected_index)
            self.refresh_listctrl()

    # def on_key_down(self, event):
    #     # Ctrl+W (Windows/Linux) 또는 Cmd+W (macOS) 감지
    #     if event.GetKeyCode() == ord('W') and (event.ControlDown() or event.CmdDown()):
    #         self.frame.Close(force=True)  # 프로그램 종료
    #     event.Skip()  # 다른 이벤트 핸들러도 처리할 수 있도록 이벤트 전파

    def show_copy_status(self, message):
        # 상태 창 생성 (프로그램 윈도우의 자식으로)
        frame_weight = 80
        status_frame = wx.Frame(
            self.frame,
            title="",
            size=(frame_weight, 30),
            style=wx.FRAME_NO_TASKBAR | wx.STAY_ON_TOP | wx.BORDER_NONE,
        )
        status_panel = RoundedPanel(status_frame, radius=8)  # 둥근 모서리 패널 사용
        status_text = wx.StaticText(status_panel, label=message)

        # 폰트 적용 (더 작고 예쁜 폰트)
        try:
            status_font = self.get_font(bold=True)
            status_text.SetFont(status_font)
        except:
            status_font = self.get_font(bold=True)
            status_text.SetFont(status_font)

        # 배경색과 텍스트 색상 설정
        status_panel.SetBackgroundColour(PRIMARY_COLOR)
        status_text.SetForegroundColour(wx.Colour(255, 255, 255))  # 흰색 텍스트

        # 레이아웃 - 패널을 프레임 전체에 맞춤
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(status_text, 1, wx.ALL | wx.ALIGN_CENTER, 5)
        status_panel.SetSizer(sizer)

        # 프로그램 윈도우 상단 중앙에 위치
        frame_pos = self.frame.GetPosition()
        frame_size = self.frame.GetSize()
        x = frame_pos[0] + (frame_size[0] - frame_weight) // 2
        y = frame_pos[1] + 40  # 상단에서 40px 아래
        status_frame.SetPosition((x, y))

        status_frame.Show()

        # 2초 후 자동으로 닫기
        wx.CallLater(2000, status_frame.Close)
