"""Alpha-painted window and a caption attached directly to its top edge."""

from PySide6.QtCore import Qt, QRectF, QSize
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton


from icons import icon


class GlassFrame(QWidget):
    def __init__(self):
        super().__init__(
            None, Qt.Window | Qt.FramelessWindowHint | Qt.WindowMinMaxButtonsHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowTitle("Copy & Paste")
        self.dark = False
        self.background_opacity = 0.52
        self.setMinimumSize(340, 540)
        self.resize(380, 620)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        color = QColor(32, 38, 34) if self.dark else QColor(235, 236, 228)
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
            if name == "닫기":
                button.setObjectName("close")
            button.clicked.connect(callback)
            row.addWidget(button)
            self.buttons.append(button)

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
