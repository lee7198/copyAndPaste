"""Theme-aware SVG icons. Replace the files in assets/icons to customize."""

from pathlib import Path
import sys
from PySide6.QtCore import Qt, QByteArray
from PySide6.QtGui import QIcon, QPixmap, QPainter
from PySide6.QtSvg import QSvgRenderer


def icon(name, dark=False):
    root = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
    svg = (root / "assets" / "icons" / f"{name}.svg").read_text(encoding="utf-8")
    svg = svg.replace("currentColor", "#f7f5f0" if dark else "#272c29")
    renderer = QSvgRenderer(QByteArray(svg.encode()))
    pixmap = QPixmap(40, 40)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    pixmap.setDevicePixelRatio(2)
    return QIcon(pixmap)
