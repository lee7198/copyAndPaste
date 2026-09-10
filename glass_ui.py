"""Alpha-painted window and a caption attached directly to its top edge."""

from ctypes import wintypes

from PySide6.QtCore import Qt, QRectF, QSize, QEvent, Signal
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen, QRegion
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton


from icons import icon


class GlassFrame(QWidget):
    display_changed = Signal(bool)

    def __init__(self):
        super().__init__(
            None, Qt.Window | Qt.FramelessWindowHint | Qt.WindowMinMaxButtonsHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowTitle("Copy & Paste")
        self.dark = False
        self.background_opacity = 0.52
        self.setMinimumSize(260, 540)
        self.resize(260, 540)

    def event(self, event):
        result = super().event(event)
        if event.type() in (
            QEvent.DevicePixelRatioChange, QEvent.WinIdChange, QEvent.Show,
            QEvent.WindowStateChange, QEvent.Resize,
        ):
            self.display_changed.emit(event.type() != QEvent.Resize)
        return result

    def nativeEvent(self, event_type, message):
        if event_type == b"windows_generic_MSG":
            native = wintypes.MSG.from_address(int(message))
            if native.message == 0x031E:  # WM_DWMCOMPOSITIONCHANGED
                self.display_changed.emit(True)
        return super().nativeEvent(event_type, message)

    def update_window_mask(self):
        # Match the window region to the custom-painted surface.
        if self.isMaximized():
            self.clearMask()
        else:
            outline = QPainterPath()
            outline.addRoundedRect(QRectF(self.rect()), 16, 16)
            self.setMask(QRegion(outline.toFillPolygon().toPolygon()))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_window_mask()

    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() == QEvent.WindowStateChange:
            self.update_window_mask()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        color = QColor(35, 35, 35) if self.dark else QColor(235, 235, 235)
        color.setAlphaF(self.background_opacity)
        painter.setBrush(color)
        painter.setPen(QPen(QColor(255, 255, 255, 105), 1))
        painter.drawRoundedRect(
            QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5),
            0 if self.isMaximized() else 16,
            0 if self.isMaximized() else 16,
        )

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and not self.isMaximized():
            pos = event.position()
            edges = Qt.Edges()
            if pos.x() < 7:
                edges |= Qt.LeftEdge
            if pos.x() > self.width() - 7:
                edges |= Qt.RightEdge
            if pos.y() < 7:
                edges |= Qt.TopEdge
            if pos.y() > self.height() - 7:
                edges |= Qt.BottomEdge
            if edges and self.windowHandle():
                self.windowHandle().startSystemResize(edges)
                return
        super().mousePressEvent(event)


class TitleBar(QWidget):
    def __init__(self, frame, on_settings):
        super().__init__(frame)
        self.frame = frame
        self.setFixedHeight(48)
        row = QHBoxLayout(self)
        row.setContentsMargins(18, 0, 8, 0)
        row.setSpacing(2)
        title = QLabel("Copy & Paste")
        title.setAttribute(Qt.WA_TransparentForMouseEvents)
        title.setStyleSheet("font-size: 12px; font-weight: 600;")
        row.addWidget(title, 1)
        self.buttons = []
        for label, name, callback in (
            ("settings", "환경 설정", on_settings),
            ("minimize", "최소화", frame.showMinimized),
            ("maximize", "최대화 / 복원", self.toggle_maximize),
            ("close", "닫기", frame.close),
        ):
            button = QPushButton()
            button.setProperty("iconName", label)
            button.setIcon(icon(label))
            button.setIconSize(QSize(16, 16))
            button.setProperty("caption", True)
            button.setFixedSize(32, 30)
            button.setAccessibleName(name)
            button.setToolTip(name)
            if label == "maximize":
                self.maximize_button = button
            if name == "닫기":
                button.setObjectName("close")
            button.clicked.connect(callback)
            row.addWidget(button)
            self.buttons.append(button)
        frame.installEventFilter(self)
        self.update_maximize_button()

    def update_maximize_button(self):
        maximized = self.frame.isMaximized()
        name = "restore" if maximized else "maximize"
        text = "창 복원" if maximized else "최대화"
        self.maximize_button.setProperty("iconName", name)
        self.maximize_button.setIcon(icon(name, self.frame.dark))
        self.maximize_button.setToolTip(text)
        self.maximize_button.setAccessibleName(text)

    def eventFilter(self, watched, event):
        if watched is self.frame and event.type() == QEvent.WindowStateChange:
            self.update_maximize_button()
        return super().eventFilter(watched, event)

    def toggle_maximize(self):
        (
            self.frame.showNormal()
            if self.frame.isMaximized()
            else self.frame.showMaximized()
        )

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.frame.windowHandle():
            self.frame.windowHandle().startSystemMove()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.toggle_maximize()
