"""Qt presentation of the existing JSON clipboard data model."""

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QLineEdit,
    QPushButton,
    QLabel,
    QStackedWidget,
    QAbstractItemView,
    QSizeGrip,
    QSizePolicy,
)
from icons import icon
from appearance import AppearanceSettings
from glass_ui import GlassFrame, TitleBar
from settings_dialog import SettingsPanel
from theme_manager import is_dark, stylesheet
from windows_effects import apply_backdrop, apply_native_shadow


class UIManager:
    def __init__(self, app, data_manager, appearance=None):
        self.app = app
        self.data_manager = data_manager
        self.appearance = appearance or AppearanceSettings()
        self.selected_index = None
        self.frame = GlassFrame()
        self.effect_key = None
        self.title_bar = TitleBar(self.frame, self.toggle_settings)
        root = QVBoxLayout(self.frame)
        root.setContentsMargins(1, 1, 1, 7)
        root.setSpacing(0)
        root.addWidget(self.title_bar)
        self.pages = QStackedWidget()
        self.pages.setContentsMargins(0, 0, 0, 0)
        root.addWidget(self.pages, 1)
        self.main_panel = QWidget()
        content = QVBoxLayout(self.main_panel)
        content.setContentsMargins(16, 10, 16, 0)
        content.setSpacing(10)
        self.data_list_ctrl = QListWidget()
        self.data_list_ctrl.setAccessibleName("저장한 텍스트")
        self.data_list_ctrl.setMinimumHeight(120)
        self.data_list_ctrl.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.data_list_ctrl.setSelectionMode(QAbstractItemView.SingleSelection)
        self.data_list_ctrl.setTextElideMode(Qt.ElideRight)
        self.data_list_ctrl.viewport().setAutoFillBackground(False)
        self.empty_label = QLabel("자주 쓰는 텍스트를 추가하세요.")
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.setProperty("muted", True)
        content.addWidget(self.empty_label)
        content.addWidget(self.data_list_ctrl, 1)
        self.input_panel = QWidget()
        editor = QVBoxLayout(self.input_panel)
        editor.setContentsMargins(0, 0, 0, 0)
        editor.setSpacing(8)
        self.key_text = QLineEdit()
        self.key_text.setPlaceholderText("이름")
        self.key_text.setAccessibleName("이름")
        self.value_text = QLineEdit()
        self.value_text.setPlaceholderText("복사할 내용")
        self.value_text.setAccessibleName("복사할 내용")
        editor.addWidget(self.key_text)
        editor.addWidget(self.value_text)
        actions = QHBoxLayout()
        self.new_button = QPushButton("NEW")
        self.save_button = QPushButton("SAVE")
        self.save_button.setObjectName("primary")
        self.delete_button = QPushButton("DELETE")
        self.delete_button.setObjectName("delete")
        for button in (self.new_button, self.save_button, self.delete_button):
            actions.addWidget(button)
        editor.addLayout(actions)
        content.addWidget(self.input_panel)
        self.input_panel.hide()
        self.status_label = QLabel()
        self.status_label.setProperty("muted", True)
        self.status_label.setFixedHeight(18)
        content.addWidget(self.status_label)
        self.add_button = QPushButton("NEW")
        self.add_button.setMinimumHeight(40)
        content.addWidget(self.add_button)
        self.pages.addWidget(self.main_panel)
        self.settings = SettingsPanel()
        self.settings.setContentsMargins(16, 0, 16, 0)
        self.pages.addWidget(self.settings)
        bottom = QHBoxLayout()
        bottom.setContentsMargins(0, 0, 5, 0)
        bottom.addStretch()
        bottom.addWidget(QSizeGrip(self.frame))
        root.addLayout(bottom)
        self.timer = QTimer(self.frame)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.status_label.clear)
        self.add_button.clicked.connect(self.toggle_editor)
        self.new_button.clicked.connect(self.new_item)
        self.save_button.clicked.connect(self.save)
        self.delete_button.clicked.connect(self.delete)
        self.key_text.returnPressed.connect(self.value_text.setFocus)
        self.value_text.returnPressed.connect(self.save)
        self.data_list_ctrl.itemClicked.connect(self.select_item)
        self.data_list_ctrl.itemActivated.connect(self.select_item)
        self.settings.saved.connect(self.save_settings)
        self.settings.cancelled.connect(lambda: self.pages.setCurrentIndex(0))
        self.escape = QShortcut(QKeySequence("Escape"), self.frame)
        self.escape.activated.connect(lambda: self.pages.setCurrentIndex(0))
        self.display_timer = QTimer(self.frame)
        self.display_timer.setSingleShot(True)
        self.display_timer.setInterval(50)
        self.display_timer.timeout.connect(self.refresh_display)
        self.frame.display_changed.connect(self.schedule_display_refresh)
        self.apply_appearance()
        self.refresh_list()
        self.frame.show()
        self.frame.windowHandle().screenChanged.connect(
            lambda _: self.schedule_display_refresh(True)
        )
        self.apply_effect()
        app.styleHints().colorSchemeChanged.connect(lambda _: self.apply_appearance())

    def refresh_list(self):
        self.data_manager.refresh_data()
        self.data_list_ctrl.clear()
        for item in self.data_manager.get_items():
            row = QListWidgetItem()
            row.setToolTip(item["value"])
            self.data_list_ctrl.addItem(row)
            row_widget = QWidget(self.data_list_ctrl)
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(12, 6, 4, 6)
            text_layout = QVBoxLayout()
            text_layout.setSpacing(3)
            for name, text in (
                ("itemTitle", item["key"]),
                ("itemValue", item["value"].replace(chr(10), " ")),
            ):
                label = QLabel(text)
                label.setObjectName(name)
                label.setAttribute(Qt.WA_TransparentForMouseEvents)
                label.setTextFormat(Qt.PlainText)
                label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
                text_layout.addWidget(label)
            menu_button = QPushButton("⋯")
            menu_button.setAccessibleName(f"{item['key']} 항목 관리")
            menu_button.setToolTip("수정·삭제")
            menu_button.setFixedSize(34, 34)
            menu_button.setObjectName("itemMenu")
            menu_button.clicked.connect(lambda _, current=row: self.edit_item(current))
            row_layout.addLayout(text_layout, 1)
            row_layout.addWidget(menu_button)
            row_widget.ensurePolished()
            self.data_list_ctrl.setItemWidget(row, row_widget)
        self.update_row_sizes()
        self.empty_label.setVisible(self.data_list_ctrl.count() == 0)
        self.delete_button.setEnabled(self.selected_index is not None)

    def update_row_sizes(self):
        for index in range(self.data_list_ctrl.count()):
            row = self.data_list_ctrl.item(index)
            widget = self.data_list_ctrl.itemWidget(row)
            widget.layout().invalidate()
            row_size = widget.sizeHint()
            # Item borders (2px) and the bottom gap (8px) surround the widget.
            row_size.setHeight(row_size.height() + 10)
            row.setSizeHint(row_size)
        self.data_list_ctrl.doItemsLayout()

    def schedule_display_refresh(self, force=False):
        if force:
            self.effect_key = None
        self.display_timer.start()

    def refresh_display(self):
        if not self.frame.isVisible() or self.frame.isMinimized():
            return
        # Let Qt finish the screen/DPI transition before measuring or calling DWM.
        self.frame.layout().invalidate()
        self.frame.layout().activate()
        self.update_row_sizes()
        self.apply_effect()
        self.frame.update()
        self.data_list_ctrl.viewport().update()

    def toggle_editor(self):
        if self.input_panel.isHidden():
            self.new_item()
            self.input_panel.show()
            self.add_button.setText("DONE")
        else:
            self.input_panel.hide()
            self.add_button.setText("NEW")
            self.selected_index = None
        self.key_text.setFocus()

    def new_item(self):
        self.selected_index = None
        self.data_list_ctrl.clearSelection()
        self.key_text.clear()
        self.value_text.clear()
        self.delete_button.setEnabled(False)
        self.key_text.setFocus()

    def select_item(self, row):
        index = self.data_list_ctrl.row(row)
        items = self.data_manager.get_items()
        if not 0 <= index < len(items):
            return
        item = items[index]
        QApplication.clipboard().setText(item["value"])
        self.status("복사했습니다")

    def edit_item(self, row):
        index = self.data_list_ctrl.row(row)
        items = self.data_manager.get_items()
        if not 0 <= index < len(items):
            return
        self.selected_index = index
        item = items[index]
        self.data_list_ctrl.setCurrentItem(row)
        self.key_text.setText(item["key"])
        self.value_text.setText(item["value"])
        self.input_panel.show()
        self.add_button.setText("완료")
        self.delete_button.setEnabled(True)

    def save(self):
        key, value = self.key_text.text().strip(), self.value_text.text().strip()
        if not (key or value):
            return
        if self.selected_index is None:
            success = self.data_manager.add_item(key, value)
        else:
            success = self.data_manager.update_item(self.selected_index, key, value)
        if success:
            self.new_item()
            self.refresh_list()
        self.status("저장했습니다" if success else "저장할 수 없습니다")

    def delete(self):
        if self.selected_index is None:
            return
        success = self.data_manager.delete_data(self.selected_index)
        if success:
            self.new_item()
            self.refresh_list()
        self.status("삭제했습니다" if success else "삭제할 수 없습니다")

    def status(self, text):
        self.status_label.setText(text)
        self.timer.start(2000)

    def toggle_settings(self):
        if self.pages.currentIndex() == 1:
            self.pages.setCurrentIndex(0)
        else:
            self.settings.load(self.appearance.values)
            self.pages.setCurrentIndex(1)

    def save_settings(self, values):
        try:
            self.appearance.save(values)
        except OSError:
            self.settings.hint.setText(
                "설정을 저장할 수 없습니다. 저장 위치를 확인하세요."
            )
            return
        self.apply_appearance()
        self.pages.setCurrentIndex(0)
        self.status("설정을 저장했습니다")

    def apply_appearance(self):
        values = self.appearance.values
        self.frame.dark = is_dark(values["theme"])
        self.frame.background_opacity = (
            1.0 if values["backdrop"] == "off" else values["window_opacity"] / 100
        )
        self.frame.setStyleSheet(stylesheet(self.frame.dark))
        for button in self.title_bar.buttons:
            button.setIcon(icon(button.property("iconName"), self.frame.dark))
        self.add_button.setIcon(icon("plus", self.frame.dark))
        self.frame.update()
        if self.frame.isVisible():
            self.apply_effect()

    def apply_effect(self):
        values = self.appearance.values
        key = (int(self.frame.winId()), values["backdrop"], self.frame.dark,
               self.frame.devicePixelRatioF(), self.frame.screen().name(),
               self.frame.windowState())
        if key != self.effect_key:
            self.frame.update_window_mask()
            self.shadow_active = apply_native_shadow(int(self.frame.winId()))
            self.backdrop_active = apply_backdrop(
                int(self.frame.winId()), values["backdrop"], self.frame.dark
            )
            self.effect_key = key
        self.frame.background_opacity = (
            values["window_opacity"] / 100 if self.backdrop_active else 1.0
        )
        self.frame.update()
        self.settings.hint.setText(
            "낮출수록 배경이 비칩니다. 글자는 선명하게 유지됩니다."
            if self.backdrop_active
            else "불투명 배경을 사용 중입니다."
        )
