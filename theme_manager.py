"""Neutral palette with opaque controls over a translucent window."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication


def is_dark(theme):
    return theme == "dark" or (
        theme == "system"
        and QApplication.styleHints().colorScheme() == Qt.ColorScheme.Dark
    )


def stylesheet(dark):
    text = "#f5f5f5" if dark else "#292929"
    muted = "#c7c7c7" if dark else "#646464"
    fill = "255,255,255"
    control = "#404040" if dark else "#f4f4f4"
    hover = "#505050" if dark else "#ffffff"
    pressed = "#343434" if dark else "#dedede"
    return f"""
    QWidget {{ color: {text}; font-family: 'Malgun Gothic', 'Segoe UI'; font-size: 13px; }}
    QLabel {{ background: transparent; }}
    QLabel[muted="true"] {{ color: {muted}; font-size: 11px; }}
    QPushButton {{ background: {control}; border: 1px solid rgba({fill},65);
        border-radius: 12px; padding: 9px 12px; }}
    QPushButton:hover {{ background: {hover}; }}
    QPushButton:pressed {{ background: {pressed}; }}
    QPushButton:focus {{ border: 1px solid {muted}; }}
    QPushButton:disabled {{ color: {muted}; background: {control}; }}
    QPushButton[caption="true"] {{ border: none; background: transparent;
        border-radius: 7px; padding: 0; font-size: 16px; }}
    QPushButton[caption="true"]:hover {{ background: rgba({fill},65); }}
    QPushButton#close:hover {{ background: #bb5049; color: white; }}
    QPushButton#primary {{ background: {text}; color: {'#292929' if dark else '#fff'};
        border: none; font-weight: 600; }}
    QPushButton#delete {{ color: {'#ffc0b8' if dark else '#a23d32'}; }}
    QListWidget {{ background: transparent; border: none; outline: none; }}
    QLabel#itemTitle {{ color: {'#ffffff' if dark else '#171717'};
        font-size: 15px; font-weight: 700; }}
    QLabel#itemValue {{ color: {muted}; font-size: 13px; font-weight: 400; }}
    QListWidget::item {{ background: rgba({fill},99); border: 1px solid rgba({fill},65);
        border-radius: 14px; margin-bottom: 8px; padding: 0; }}
    QPushButton#itemMenu {{ background: transparent; border: 1px solid transparent;
        padding: 0; font-size: 20px; }}
    QPushButton#itemMenu:hover {{ background: rgba({fill},70); }}
    QPushButton#itemMenu:pressed {{ background: rgba({fill},100); }}
    QPushButton#itemMenu:focus {{ border: 1px solid {muted}; }}
    QListWidget::item:hover {{ background: rgba({fill},64); }}
    QListWidget::item:selected {{ background: rgba({fill},88); }}
    QLineEdit {{ background: {control}; border: 1px solid rgba({fill},85);
        border-radius: 10px; padding: 10px; selection-background-color: #808080; }}
    QLineEdit:focus {{ border-color: {muted}; }}
    QComboBox {{ background: {control}; border: 1px solid rgba({fill},85);
        border-radius: 10px; padding: 10px; }}
    QComboBox QAbstractItemView {{ background: {'#363636' if dark else '#efefef'}; }}
    QSlider::groove:horizontal {{ height: 4px; background: rgba({fill},90); border-radius: 2px; }}
    QSlider::handle:horizontal {{ width: 16px; margin: -6px 0; background: {text}; border-radius: 8px; }}
    QScrollBar:vertical {{ background: transparent; width: 5px; margin: 0; }}
    QScrollBar::handle:vertical {{ background: rgba({fill},110); border-radius: 2px; min-height: 28px; }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
    """
