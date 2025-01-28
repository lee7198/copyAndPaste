import wx


class ToDoApp(wx.App):
    def OnInit(self):
        frame = wx.Frame(None, title="copyAndPaste")
        panel = wx.Panel(frame)

        # 할 일 목록을 저장할 리스트
        self.todo_list = []

        # 할 일 추가 텍스트 박스
        self.todo_text = wx.TextCtrl(panel, size=(200, -1))

        # 할 일 추가 버튼
        add_button = wx.Button(panel, label="Add")
        add_button.Bind(wx.EVT_BUTTON, self.onAdd)

        # 할 일 목록을 보여줄 리스트 컨트롤
        self.todo_list_ctrl = wx.ListBox(panel)

        # 레이아웃 설정
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.todo_text, 0, wx.ALL, 5)
        sizer.Add(add_button, 0, wx.ALL, 5)
        sizer.Add(self.todo_list_ctrl, 1, wx.EXPAND | wx.ALL, 5)
        panel.SetSizer(sizer)

        frame.Show()
        return True

    def onAdd(self, event):
        todo_item = self.todo_text.GetValue()
        self.todo_list.append(todo_item)
        self.todo_list_ctrl.Append(todo_item)
        self.todo_text.Clear()

if __name__ == "__main__":
    app = ToDoApp()
    app.MainLoop()