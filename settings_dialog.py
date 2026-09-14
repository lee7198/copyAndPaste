"""In-window settings page; only Save changes persistent preferences."""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QButtonGroup,
    QRadioButton,
    QSizePolicy,
)
from appearance import DEFAULTS
from glass_ui import GlassCard


class SettingsPanel(QWidget):
    saved = Signal(dict)
    cancelled = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 6, 4, 0)
        layout.setSpacing(8)
        heading = QLabel("환경 설정")
        heading.setStyleSheet("font-size: 16px; font-weight: 600;")
        layout.addWidget(heading)
        self.theme = QButtonGroup(self)
        for label, control, options in (
            (QLabel("테마"), self.theme, ("시스템", "라이트", "다크")),
        ):
            card = GlassCard()
            group = QVBoxLayout(card)
            group.setContentsMargins(8, 8, 8, 8)
            group.setSpacing(6)
            group.addWidget(label)
            if options:
                choices = QHBoxLayout()
                choices.setSpacing(6)
                for index, text in enumerate(options):
                    button = QRadioButton(text)
                    button.setAccessibleName(f"{label.text()} · {text}")
                    button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                    control.addButton(button, index)
                    choices.addWidget(button, 1)
                label.setBuddy(control.button(0))
                group.addLayout(choices)
            else:
                label.setBuddy(control)
                group.addWidget(control)
            layout.addWidget(card)
        self.hint = QLabel()
        self.hint.setWordWrap(True)
        self.hint.setProperty("muted", True)
        layout.addWidget(self.hint)
        layout.addStretch()
        reset = QPushButton("기본값 복원")
        reset.clicked.connect(lambda: self.load(DEFAULTS))
        layout.addWidget(reset)
        row = QHBoxLayout()
        row.setSpacing(6)
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
        self.theme.button(("system", "light", "dark").index(values["theme"])).setChecked(True)

    def values(self):
        return dict(
            self.original,
            theme=("system", "light", "dark")[self.theme.checkedId()],
            backdrop="off",
        )
