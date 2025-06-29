import wx
from data_manager import DataManager
from ui_manager import UIManager

FONT_SIZE = 9  # 폰트 사이즈를 변수로 관리


class CopyAndPasteApp(wx.App):
    def OnInit(self):
        self.data_manager = DataManager("./data.json")
        self.ui_manager = UIManager(self, self.data_manager, font_size=FONT_SIZE)
        return True


if __name__ == "__main__":
    app = CopyAndPasteApp()
    app.MainLoop()
