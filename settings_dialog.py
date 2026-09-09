"""In-window settings page; only Save changes persistent preferences."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QSlider,
)
from appearance import DEFAULTS


class SettingsPanel(QWidget):
    saved = Signal(dict)
    cancelled = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 12, 8, 0)
        layout.setSpacing(18)
        heading = QLabel("환경 설정")
        heading.setStyleSheet("font-size: 18px; font-weight: 600;")
        layout.addWidget(heading)
        self.theme = QComboBox()
        self.theme.addItems(["시스템 설정", "라이트", "다크"])
        self.backdrop = QComboBox()
        self.backdrop.addItems(["끄기", "부드러운 블러", "아크릴 블러"])
        self.opacity = QSlider(Qt.Horizontal)
        self.opacity.setRange(20, 90)
        self.opacity.setAccessibleName("배경 불투명도")
        self.opacity_label = QLabel()
        self.opacity.valueChanged.connect(
            lambda v: self.opacity_label.setText(f"배경 불투명도 · {v}%")
        )
        for label, control in (
            (QLabel("테마"), self.theme),
            (QLabel("배경 효과"), self.backdrop),
            (self.opacity_label, self.opacity),
        ):
            group = QVBoxLayout()
            group.setSpacing(8)
            group.addWidget(label)
            group.addWidget(control)
            layout.addLayout(group)
        self.hint = QLabel("낮출수록 배경이 비칩니다. 글자는 선명하게 유지됩니다.")
        self.hint.setWordWrap(True)
        self.hint.setProperty("muted", True)
        layout.addWidget(self.hint)
        layout.addStretch()
        reset = QPushButton("기본값 복원")
        reset.clicked.connect(lambda: self.load(DEFAULTS))
        layout.addWidget(reset)
        row = QHBoxLayout()
        cancel = QPushButton("취소")
        save = QPushButton("저장")
        save.setObjectName("primary")
        cancel.clicked.connect(self.cancelled)
        save.clicked.connect(lambda: self.saved.emit(self.values()))
        row.addWidget(cancel)
        row.addWidget(save)
        layout.addLayout(row)

    def load(self, values):
        self.original = values.copy()
        self.theme.setCurrentIndex(("system", "light", "dark").index(values["theme"]))
        self.backdrop.setCurrentIndex(
            ("off", "blur", "acrylic").index(values["backdrop"])
        )
        self.opacity.setValue(values["window_opacity"])
        self.opacity_label.setText(f"배경 불투명도 · {self.opacity.value()}%")

    def values(self):
        return dict(
            self.original,
            theme=("system", "light", "dark")[self.theme.currentIndex()],
            backdrop=("off", "blur", "acrylic")[self.backdrop.currentIndex()],
            window_opacity=self.opacity.value(),
        )
