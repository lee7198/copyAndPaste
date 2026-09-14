"""Glass surfaces and controls using the design.md theme palette."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication


def is_dark(theme):
    return theme == "dark" or (
        theme == "system"
        and QApplication.styleHints().colorScheme() == Qt.ColorScheme.Dark
    )


def stylesheet(dark):
    text = "#FFFFFF" if dark else "#111111"
    muted = "rgba(255,255,255,153)" if dark else "rgba(0,0,0,140)"
    fill = "255,255,255" if dark else "0,0,0"
    surface = "rgba(255,255,255,18)" if dark else "rgba(255,255,255,191)"
    border = f"rgba({fill},{51 if dark else 15})"
    focus = f"rgba({fill},{89 if dark else 64})"
    control = f"rgba({fill},{80 if dark else 20})"
    hover = f"rgba({fill},{31 if dark else 20})"
    pressed = f"rgba({fill},{46 if dark else 31})"
    return f"""
    QWidget {{ color: {text}; font-family: 'Noto Sans KR', 'Segoe UI'; font-size: 12px; }}
    QLabel {{ background: transparent; font-weight: 800; }}
    QFrame[card="true"] {{ background: {surface}; border: 1px solid {border};
        border-radius: 12px; }}
    QLabel[muted="true"] {{ color: {muted}; font-size: 11px; }}
    QPushButton {{ background: {control}; border: 1px solid transparent;
        border-radius: 12px; min-height: 16px; padding: 6px 8px; }}
    QPushButton:hover {{ background: {hover}; }}
    QPushButton:pressed {{ background: {pressed}; }}
    QPushButton:focus {{ border: 1px solid {focus}; }}
    QPushButton:disabled {{ color: {muted}; background: {control}; }}
    QPushButton[caption="true"] {{ border: none; background: transparent;
        border-radius: 6px; min-height: 0; padding: 0; font-size: 16px; }}
    QPushButton[caption="true"]:hover {{ background: rgba({fill},65); }}
    QPushButton#close:hover {{ background: #DF301C; color: white; }}
    QPushButton#primary {{ background: {text}; color: {'#000000' if dark else '#FFFFFF'};
        border: 1px solid transparent; font-weight: 600; }}
    QPushButton#primary:hover {{ background: {'#dedede' if dark else '#333333'}; }}
    QPushButton#primary:pressed {{ background: {'#c7c7c7' if dark else '#000000'}; }}
    QPushButton#primary:focus {{ border-color: {focus}; }}
    QPushButton#delete {{ background: #E45742; }}
    QPushButton#delete:hover {{ background: #EF6854; }}
    QPushButton#delete:pressed {{ background: #C84432; }}
    QPushButton#delete:focus {{ border-color: #FFB4A8; }}
    QPushButton#toggle {{ background: {'#F5F5F5' if dark else '#222222'};
        color: {'#111111' if dark else '#FFFFFF'}; }}
    QPushButton#toggle:hover {{ background: {'#E2E2E2' if dark else '#383838'}; }}
    QPushButton#toggle:pressed {{ background: {'#C7C7C7' if dark else '#111111'}; }}
    QPushButton#toggle:focus {{ border-color: {'#777777' if dark else '#8A8A8A'}; }}
    QListWidget {{ background: transparent; border: none; outline: none; }}
    QLabel#itemTitle {{ color: {'#ffffff' if dark else '#171717'};
        font-size: 12px; font-weight: 600; }}
    QLabel#itemValue {{ color: {muted}; font-size: 11px; font-weight: 400; }}
    QListWidget::item {{ background: {surface}; border: 1px solid {border};
        border-radius: 8px; margin-bottom: 4px; padding: 0; }}
    QPushButton#itemMenu {{ background: transparent; border: 1px solid transparent;
        border-radius: 6px; min-height: 0; padding: 0; font-size: 16px; }}
    QPushButton#itemMenu:hover {{ background: rgba({fill},70); }}
    QPushButton#itemMenu:pressed {{ background: rgba({fill},100); }}
    QPushButton#itemMenu:focus {{ border: 1px solid {focus}; }}
    QListWidget::item:hover {{ background: {surface}; border-color: {focus}; }}
    QListWidget::item:selected {{ background: {surface}; border: 2px solid {focus}; }}
    QLineEdit {{ background: {control}; border: 1px solid transparent;
        border-radius: 10px; padding: 6px 10px; selection-background-color: #808080; }}
    QLineEdit:focus {{ border-color: {focus}; }}
    QRadioButton {{ background: {control}; border: 1px solid transparent;
        border-radius: 4px; min-height: 16px; padding: 6px; spacing: 0; }}
    QRadioButton:hover {{ background: {hover}; }}
    QRadioButton:checked {{ background: {text}; color: {'#000000' if dark else '#FFFFFF'}; }}
    QRadioButton:focus {{ border: 1px dashed {focus}; }}
    QRadioButton::indicator {{ width: 0; height: 0; border: none; }}
    QSlider::groove:horizontal {{ height: 4px; background: rgba({fill},90); border-radius: 2px; }}
    QSlider::handle:horizontal {{ width: 16px; margin: -6px 0; background: {text}; border-radius: 8px; }}
    QScrollBar:vertical {{ background: transparent; width: 5px; margin: 0; }}
    QScrollBar::handle:vertical {{ background: rgba({fill},110); border-radius: 2px; min-height: 28px; }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
    """
