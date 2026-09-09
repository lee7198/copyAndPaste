"""Small neutral palette; all widget surfaces remain alpha composited."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication


def is_dark(theme):
    return theme == "dark" or (
        theme == "system"
        and QApplication.styleHints().colorScheme() == Qt.ColorScheme.Dark
    )


def stylesheet(dark):
    text = "#f7f5f0" if dark else "#272c29"
    muted = "#c7c9c4" if dark else "#626860"
    fill = "255,255,255" if dark else "255,255,252"
    return f"""
    QWidget {{ color: {text}; font-family: 'Segoe UI', 'Malgun Gothic'; font-size: 13px; }}
    QLabel {{ background: transparent; }}
    QLabel[muted="true"] {{ color: {muted}; font-size: 11px; }}
    QPushButton {{ background: rgba({fill},28); border: 1px solid rgba({fill},65);
        border-radius: 12px; padding: 9px 12px; }}
    QPushButton:hover {{ background: rgba({fill},70); }}
    QPushButton:pressed {{ background: rgba({fill},100); }}
    QPushButton:focus {{ border: 1px solid {muted}; }}
    QPushButton:disabled {{ color: {muted}; background: transparent; }}
    QPushButton[caption="true"] {{ border: none; background: transparent;
        border-radius: 7px; padding: 0; font-size: 16px; }}
    QPushButton[caption="true"]:hover {{ background: rgba({fill},65); }}
    QPushButton#close:hover {{ background: #bb5049; color: white; }}
    QPushButton#primary {{ background: {text}; color: {'#262b28' if dark else '#fff'};
        border: none; font-weight: 600; }}
    QPushButton#delete {{ color: {'#ffc0b8' if dark else '#a23d32'}; }}
    QListWidget {{ background: transparent; border: none; outline: none; }}
    QListWidget::item {{ background: rgba({fill},32); border: 1px solid rgba({fill},65);
        border-radius: 14px; margin-bottom: 8px; padding: 12px; }}
    QListWidget::item:hover {{ background: rgba({fill},64); }}
    QListWidget::item:selected {{ background: rgba({fill},88); }}
    QLineEdit {{ background: rgba({fill},42); border: 1px solid rgba({fill},85);
        border-radius: 10px; padding: 10px; selection-background-color: #758879; }}
    QLineEdit:focus {{ border-color: {muted}; }}
    QComboBox {{ background: rgba({fill},45); border: 1px solid rgba({fill},85);
        border-radius: 10px; padding: 10px; }}
    QComboBox QAbstractItemView {{ background: {'#333833' if dark else '#f0f0e9'}; }}
    QSlider::groove:horizontal {{ height: 4px; background: rgba({fill},90); border-radius: 2px; }}
    QSlider::handle:horizontal {{ width: 16px; margin: -6px 0; background: {text}; border-radius: 8px; }}
    QScrollBar:vertical {{ background: transparent; width: 5px; margin: 0; }}
    QScrollBar::handle:vertical {{ background: rgba({fill},110); border-radius: 2px; min-height: 28px; }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
    """
