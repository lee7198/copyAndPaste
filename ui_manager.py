import wx

class UIManager:
    def __init__(self, app, data_manager):
        self.app = app
        self.data_manager = data_manager
        self.init_ui()
        self.setup_event_handlers()

    def init_ui(self):
        fix_width = 220
        self.frame = wx.Frame(None, title="복붙")
        self.frame.SetSize(fix_width, 500)
        self.frame.SetMinSize((fix_width, 450))  
        self.frame.SetMaxSize((fix_width, -1))
        self.frame.SetPosition(wx.Point(50, 150))
        self.main_panel = wx.Panel(self.frame)
        
        self.input_panel = wx.Panel(self.main_panel)
        self.input_panel.Hide()
        
        self.init_controls()
        self.layout_controls()
        self.frame.Show()

        # 키 이벤트 바인딩
        # self.frame.Bind(wx.EVT_KEY_DOWN, self.on_key_down)

    def init_controls(self):
        fix_width = 100
        # 입력 필드 초기화
        self.key_text = wx.TextCtrl(self.input_panel, size=(fix_width, -1))
        self.value_text = wx.TextCtrl(self.input_panel, size=(fix_width, -1), style=wx.TE_PROCESS_ENTER)
        
        self.key_text.Bind(wx.EVT_TEXT_ENTER, self.value_text.SetFocus())
        self.value_text.Bind(wx.EVT_TEXT_ENTER, self.on_save)
        
        # 버튼 초기화
        self.add_button = wx.Button(self.main_panel, label="Add")
        self.save_button = wx.Button(self.input_panel, label="Save")
        self.delete_button = wx.Button(self.input_panel, label="Delete")
        
        # 리스트 박스 초기화
        self.data_list_ctrl = wx.ListBox(self.main_panel)
        
        # 초기 상태 설정
        self.refresh_listbox()
        
        # 리스트박스 click event binding
        self.data_list_ctrl.Bind(wx.EVT_LISTBOX, self.on_listbox_click)

    def layout_controls(self):
        # 메인 패널 레이아웃
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 메인 패널에 컨트롤 추가
        main_sizer.Add(self.data_list_ctrl, 1, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(self.input_panel, 0, wx.EXPAND)  # 입력 패널 추가
        main_sizer.Add(self.add_button, 0, wx.ALL | wx.EXPAND, 5)
        self.main_panel.SetSizer(main_sizer)
        
        # Labels
        key_label = wx.StaticText(self.input_panel, label='KEY')
        value_label = wx.StaticText(self.input_panel, label='VALUE')
        small_font = wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        key_label.SetFont(small_font)
        key_label.SetMinSize((30, -1))
        key_label.SetWindowStyle(wx.ALIGN_CENTER_VERTICAL)
        value_label.SetFont(small_font)
        value_label.SetMinSize((30, -1))
        value_label.SetWindowStyle(wx.ALIGN_CENTER_VERTICAL)
        
        input_sizer = wx.BoxSizer(wx.VERTICAL)
        
        input_box_key = wx.BoxSizer(wx.HORIZONTAL)
        input_box_value = wx.BoxSizer(wx.HORIZONTAL)
        
        input_box_key.Add(key_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        input_box_key.Add(self.key_text, 1, wx.ALL | wx.EXPAND, 5)
        
        input_box_value.Add(value_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        input_box_value.Add(self.value_text, 1, wx.ALL | wx.EXPAND, 5)
        
        # save & delete sizer
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.Add(self.save_button, 1, wx.ALL | wx.EXPAND, 5)
        button_sizer.Add(self.delete_button, 1, wx.ALL | wx.EXPAND, 5)
        
        input_sizer.Add(input_box_key, 1, wx.EXPAND)
        input_sizer.Add(input_box_value, 0, wx.EXPAND)
        input_sizer.Add(button_sizer, 0, wx.EXPAND)
        self.input_panel.SetSizer(input_sizer)
        

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
        self.data_list_ctrl = wx.ListBox(self.main_panel)
        self.refresh_listbox()

    def refresh_listbox(self):
        self.data_list_ctrl.Clear()
        self.data_manager.refresh_data()
        for item in self.data_manager.get_items():
            value = item["key"] + " : " + item["value"]
            self.data_list_ctrl.Append(f"{value}") 

    def setup_event_handlers(self):
        # 이벤트 핸들러 설정
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

    # save 핸들러
    def on_save(self, event):
        key = self.key_text.GetValue()
        value = self.value_text.GetValue()
        
        if(key != '' or value != '') :
            self.data_manager.add_item(key, value)
            
            self.key_text.Clear()
            self.value_text.Clear()
            self.key_text.SetFocus()
            
            # refresh data
            self.refresh_listbox()
            pass
        
    def on_tab_next(self) :
        self.value_text.SetFocus()
            
    def on_listbox_click(self, event):
        selected_index = self.data_list_ctrl.GetSelection()
        if selected_index != wx.NOT_FOUND:
            selected_item = self.data_list_ctrl.GetString(selected_index)
            value = selected_item.split(" : ")[-1]
            
            if wx.TheClipboard.Open():
                wx.TheClipboard.SetData(wx.TextDataObject(value))
                wx.TheClipboard.Close()
            else:
                wx.MessageBox("클립보드에 접근할 수 없습니다.", "오류", wx.OK | wx.ICON_ERROR)
    
    def on_delete(self, event):
        selected_index = self.data_list_ctrl.GetSelection()
        if selected_index != wx.NOT_FOUND:
            self.data_manager.delete_data(selected_index)
            self.refresh_listbox()
            
    # def on_key_down(self, event):
    #     # Ctrl+W (Windows/Linux) 또는 Cmd+W (macOS) 감지
    #     if event.GetKeyCode() == ord('W') and (event.ControlDown() or event.CmdDown()):
    #         self.frame.Close(force=True)  # 프로그램 종료
    #     event.Skip()  # 다른 이벤트 핸들러도 처리할 수 있도록 이벤트 전파 