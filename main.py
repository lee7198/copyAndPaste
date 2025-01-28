import wx
from data_manager import DataManager
from ui_manager import UIManager

class CopyAndPasteApp(wx.App):
    def OnInit(self):
        self.data_manager = DataManager('./data.json')
        self.ui_manager = UIManager(self, self.data_manager)
        return True

if __name__ == "__main__":
    app = CopyAndPasteApp()
    app.MainLoop()