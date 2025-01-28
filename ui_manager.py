import wx

class UIManager:
    def __init__(self, app, data_manager):
        self.app = app
        self.data_manager = data_manager
        self.init_ui()
        self.setup_event_handlers()

    def init_ui(self):
        self.frame = wx.Frame(None, title="copyAndPaste")
        self.frame.SetSize(200, 500)
        self.frame.SetPosition(wx.Point(0, 0))  # 창을 좌측 상단에 위치시킴
        self.panel = wx.Panel(self.frame)
        
        self.init_controls()
        self.layout_controls()
        self.frame.Show()

    def init_controls(self):
        # 입력 필드 초기화
        self.key_text = wx.TextCtrl(self.panel, size=(200, -1), style=wx.TE_PROCESS_ENTER)
        self.value_text = wx.TextCtrl(self.panel, size=(200, -1), style=wx.TE_PROCESS_ENTER)
        
        # 버튼 초기화
        self.add_button = wx.Button(self.panel, label="Add")
        self.save_button = wx.Button(self.panel, label="Save")
        
        # 리스트 박스 초기화
        self.data_list_ctrl = wx.ListBox(self.panel)
        
        # 초기 상태 설정
        self.hide_input_fields()  # 입력란과 Save 버튼 숨기기
        self.add_button.Show()  # Add 버튼은 항상 보이기
        self.refresh_listbox()

    def layout_controls(self):
        # 메인 수직 레이아웃
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 입력 필드와 리스트 박스를 위한 수직 레이아웃
        content_sizer = wx.BoxSizer(wx.VERTICAL)
        content_sizer.Add(self.key_text, 0, wx.ALL | wx.EXPAND, 5)
        content_sizer.Add(self.value_text, 0, wx.ALL | wx.EXPAND, 5)
        content_sizer.Add(self.data_list_ctrl, 1, wx.EXPAND | wx.ALL, 5)
        content_sizer.Add(self.save_button, 0, wx.ALL, 5)  # Save 버튼 추가
        
        # Add 버튼을 하단 우측에 배치하기 위한 수평 레이아웃
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.AddStretchSpacer()  # 왼쪽 공간을 채움
        button_sizer.Add(self.add_button, 0, wx.ALL, 5)  # Add 버튼 추가
        
        # 메인 레이아웃에 컨텐츠와 버튼 추가
        main_sizer.Add(content_sizer, 1, wx.EXPAND)
        main_sizer.Add(button_sizer, 0, wx.EXPAND | wx.BOTTOM, 5)
        
        self.panel.SetSizer(main_sizer)

    def hide_input_fields(self):
        self.key_text.Hide()
        self.value_text.Hide()
        self.save_button.Hide()

    def show_input_fields(self):
        self.key_text.Show()
        self.value_text.Show()
        self.save_button.Show()
        self.key_text.SetFocus()

    def init_listbox(self):
        self.data_list_ctrl = wx.ListBox(self.panel)
        self.refresh_listbox()  # 데이터를 로드하고 표시

    def refresh_listbox(self):
        self.data_list_ctrl.Clear()  # 기존 항목 지우기
        for key, value in self.data_manager.get_items():
            self.data_list_ctrl.Append(f"{key} {value}")  # 새로운 항목 추가

    def setup_event_handlers(self):
        # 이벤트 핸들러 설정
        self.add_button.Bind(wx.EVT_BUTTON, self.on_add)
        self.save_button.Bind(wx.EVT_BUTTON, self.on_save)

    def on_add(self, event):
        # 이벤트 핸들러 구현
        pass

    def on_save(self, event):
        # 이벤트 핸들러 구현
        pass 