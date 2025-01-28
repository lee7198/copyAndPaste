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
        self.panel = wx.Panel(self.frame)
        
        self.init_controls()
        self.layout_controls()
        self.frame.Show()

    def init_controls(self):
        self.key_text 