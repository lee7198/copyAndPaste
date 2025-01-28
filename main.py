import wx
import json
import os


class CopyAndPaste(wx.App):
    def OnInit(self):
        self.frame = wx.Frame(None, title="copyAndPaste")
        self.frame.SetSize(200, 500)
        self.panel = wx.Panel(self.frame)

        self.json_file = 'data.json'
        self.data_list = self.load_data()

        # key 입력란
        self.key_text = wx.TextCtrl(self.panel, size=(200, -1), style=wx.TE_PROCESS_ENTER)
        self.key_text.Hide()  # 초기에 숨김
        self.key_text.Bind(wx.EVT_TEXT_ENTER, self.onAdd)  # 엔터키 이벤트 바인딩

        # value 입력란
        self.value_text = wx.TextCtrl(self.panel, size=(200, -1), style=wx.TE_PROCESS_ENTER)
        self.value_text.Hide()  # 초기에 숨김
        self.value_text.Bind(wx.EVT_TEXT_ENTER, self.onAdd)  # 엔터키 이벤트 바인딩

        # 데이터 추가 버튼
        self.add_button = wx.Button(self.panel, label="Add")
        self.add_button.Bind(wx.EVT_BUTTON, self.onAddButtonClick)

        # 저장 버튼
        self.save_button = wx.Button(self.panel, label="Save")
        self.save_button.Hide()  # 초기에 숨김
        self.save_button.Bind(wx.EVT_BUTTON, self.onSaveButtonClick)

        # 할 일 목록을 보여줄 리스트 컨트롤
        self.data_list_ctrl = wx.ListBox(self.panel)

        # 저장된 할 일 목록 표시
        for key, value in self.data_list.items():
            self.data_list_ctrl.Append(f"{key}: {value}")

        # 프레임이 닫힐 때 데이터 저장
        self.frame.Bind(wx.EVT_CLOSE, self.onClose)

        # 레이아웃 설정
        self.layoutInit()
        self.frame.Show()
        
        return True
      
    def layoutInit(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.key_text, 0, wx.ALL, 5)
        sizer.Add(self.value_text, 0, wx.ALL, 5)
        sizer.Add(self.save_button, 0, wx.ALL, 5)
        sizer.Add(self.add_button, 0, wx.ALL, 5)
        sizer.Add(self.data_list_ctrl, 1, wx.EXPAND | wx.ALL, 5)
        self.panel.SetSizer(sizer)

    def load_data(self):
        if os.path.exists(self.json_file):
            try:
                with open(self.json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):  # 기존 데이터가 리스트인 경우 딕셔너리로 변환
                        return {str(i): item for i, item in enumerate(data)}
                    return data
            except:
                return {}  # 빈 딕셔너리로 초기화
        return {}  # 빈 딕셔너리로 초기화

    def save_data_list(self):
        with open(self.json_file, 'w', encoding='utf-8') as f:
            json.dump(self.data_list, f, ensure_ascii=False, indent=2)

    def onAddButtonClick(self, event):
        if self.key_text.IsShown():  # 입력란이 보이는 상태라면
            self.key_text.Hide()  # 입력란 숨기기
            self.value_text.Hide()  # 입력란 숨기기
            self.save_button.Hide()  # 저장 버튼 숨기기
            self.add_button.SetLabel("Add")  # 버튼 텍스트 변경
        else:  # 입력란이 숨겨진 상태라면
            self.key_text.Show()  # 입력란 보이기
            self.value_text.Show()  # 입력란 보이기
            self.save_button.Show()  # 저장 버튼 보이기
            self.add_button.SetLabel("Cancel")  # 버튼 텍스트 변경
            self.key_text.SetFocus()  # key 입력란에 포커스 설정
        self.panel.Layout()  # 레이아웃 갱신

    def onAdd(self, event):
        key = self.key_text.GetValue().strip()
        value = self.value_text.GetValue().strip()
        if key and value:  # key와 value가 모두 입력된 경우에만 추가
            self.data_list[key] = value  # 딕셔너리에 추가
            self.data_list_ctrl.Append(f"{key}: {value}")  # 리스트 박스에 표시
            self.key_text.Clear()
            self.value_text.Clear()
            self.key_text.Hide()  # 입력 완료 후 다시 숨기기
            self.value_text.Hide()  # 입력 완료 후 다시 숨기기
            self.add_button.SetLabel("Add")  # 버튼 텍스트 원래대로 변경
            self.panel.Layout()  # 레이아웃 갱신
            self.save_data_list()

    def onSaveButtonClick(self, event):
        self.save_data_list()
        wx.MessageBox("데이터가 저장되었습니다.", "저장 완료", wx.OK | wx.ICON_INFORMATION)

    def onClose(self, event):
        self.save_data_list()
        event.Skip()

if __name__ == "__main__":
    app = CopyAndPaste()
    app.MainLoop()