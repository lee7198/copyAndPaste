import wx

class UIManager:
    def __init__(self, app, data_manager):
        self.app = app
        self.data_manager = data_manager
        self.init_ui()
        self.setup_event_handlers()

    def init_ui(self):
        fix_width = 220
        self.frame = wx.Frame(None, title="copyAndPaste")
        self.frame.SetSize(fix_width, 500)
        self.frame.SetMinSize((fix_width, -1))  # 최소 너비를 200픽셀로 설정
        self.frame.SetPosition(wx.Point(50, 150))  # 창을 좌측 상단에 위치시킴
        self.main_panel = wx.Panel(self.frame)  # 메인 패널
        
        # 입력 필드를 위한 패널 (z-index 효과를 위해 별도 패널 사용)
        self.input_panel = wx.Panel(self.main_panel)
        self.input_panel.Hide()  # 초기에 숨김
        
        self.init_controls()
        self.layout_controls()
        self.frame.Show()

        # 키 이벤트 바인딩
        # self.frame.Bind(wx.EVT_KEY_DOWN, self.on_key_down)

    def init_controls(self):
        fix_width = 100
        # 입력 필드 초기화
        self.title_text = wx.TextCtrl(self.input_panel, size=(fix_width, -1), style=wx.TE_PROCESS_ENTER)
        self.value_text = wx.TextCtrl(self.input_panel, size=(fix_width, -1), style=wx.TE_PROCESS_ENTER)
        
        # 버튼 초기화
        self.add_button = wx.Button(self.main_panel, label="Add")
        self.save_button = wx.Button(self.input_panel, label="Save")
        
        # 리스트 박스 초기화
        self.data_list_ctrl = wx.ListBox(self.main_panel)
        
        # 초기 상태 설정
        self.refresh_listbox()

    def layout_controls(self):
        # 메인 패널 레이아웃
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 메인 패널에 컨트롤 추가
        main_sizer.Add(self.data_list_ctrl, 1, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(self.input_panel, 0, wx.EXPAND)  # 입력 패널 추가
        main_sizer.Add(self.add_button, 0, wx.ALL | wx.EXPAND, 5)
        self.main_panel.SetSizer(main_sizer)
        
        # 입력 패널 레이아웃
        input_sizer = wx.BoxSizer(wx.VERTICAL)
        input_box = wx.BoxSizer(wx.HORIZONTAL)
        input_box.Add(self.title_text, 0, wx.ALL | wx.EXPAND, 5)
        input_box.Add(self.value_text, 0, wx.ALL | wx.EXPAND, 5)
        input_sizer.Add(input_box, 0, wx.EXPAND)
        input_sizer.Add(self.save_button, 0, wx.ALL | wx.EXPAND, 5)
        self.input_panel.SetSizer(input_sizer)
        

    def hide_input_fields(self):
        self.title_text.Hide()
        self.value_text.Hide()
        self.save_button.Hide()

    def show_input_fields(self):
        self.title_text.Show()
        self.value_text.Show()
        self.save_button.Show()
        self.title_text.SetFocus()

    def init_listbox(self):
        self.data_list_ctrl = wx.ListBox(self.main_panel)
        self.refresh_listbox()  # 데이터를 로드하고 표시

    def refresh_listbox(self):
        self.data_list_ctrl.Clear()  # 기존 항목 지우기
        self.data_manager.refresh_data()
        for item in self.data_manager.get_items():
            value = item["title"] + " : " + item["value"]
            self.data_list_ctrl.Append(f"{value}")  # 새로운 항목 추가

    def setup_event_handlers(self):
        # 이벤트 핸들러 설정
        self.add_button.Bind(wx.EVT_BUTTON, self.on_add_button_click)
        self.save_button.Bind(wx.EVT_BUTTON, self.on_save)

    def on_add_button_click(self, event):
        if self.input_panel.IsShown():  # 입력 패널이 보이는 상태라면
            self.input_panel.Hide()  # 입력 패널 숨기기
            self.add_button.SetLabel("Add")  # 버튼 텍스트 변경
        else:  # 입력 패널이 숨겨진 상태라면
            self.input_panel.Show()  # 입력 패널 보이기
            self.add_button.SetLabel("Cancel")  # 버튼 텍스트 변경
            self.title_text.SetFocus()  # key 입력란에 포커스 설정
        self.main_panel.Layout()  # 레이아웃 갱신

    # save 핸들러
    def on_save(self, event):
        self.data_manager.add_item(
            self.title_text.GetValue(), 
            self.value_text.GetValue()
        )
        
        self.title_text.Clear()  # key 텍스트 박스 초기화
        self.value_text.Clear()  # value 텍스트 박스 초기화
        self.title_text.SetFocus()  # key 텍스트 박스에 포커스 설정
        
        # refresh data
        self.refresh_listbox()
        pass

    # def on_key_down(self, event):
    #     # Ctrl+W (Windows/Linux) 또는 Cmd+W (macOS) 감지
    #     if event.GetKeyCode() == ord('W') and (event.ControlDown() or event.CmdDown()):
    #         self.frame.Close(force=True)  # 프로그램 종료
    #     event.Skip()  # 다른 이벤트 핸들러도 처리할 수 있도록 이벤트 전파 