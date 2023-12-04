#!/usr/bin/env python3


from PySide6.QtWidgets import QListWidget, QPushButton, QStackedWidget

from neosca_gui.ng_settings.ng_settings import Ng_Settings
from neosca_gui.ng_settings.ng_widget_settings_abstract import Ng_Widget_Settings_Abstract
from neosca_gui.ng_settings.ng_widget_settings_appearance import Ng_Widget_Settings_Appearance
from neosca_gui.ng_settings.ng_widget_settings_export import Ng_Widget_Settings_Export
from neosca_gui.ng_settings.ng_widget_settings_import import Ng_Widget_Settings_Import
from neosca_gui.ng_widgets.ng_dialogs import Ng_Dialog
from neosca_gui.ng_widgets.ng_widgets import Ng_MessageBox_Confirm, Ng_ScrollArea


class Ng_Dialog_Settings(Ng_Dialog):
    def __init__(self, main):
        super().__init__(main, title="Preferences", width=768, height=576, resizable=True)

        self.sections = (
            Ng_Widget_Settings_Appearance(main),
            Ng_Widget_Settings_Import(main),
            Ng_Widget_Settings_Export(main),
        )
        self.listwidget_settings = QListWidget()
        self.stackedwidget_settings = QStackedWidget()
        self.scrollarea_settings = Ng_ScrollArea()
        self.scrollarea_settings.setWidget(self.stackedwidget_settings)
        self.button_reset = QPushButton("Reset all settings")
        self.button_save = QPushButton("Save")
        self.button_apply = QPushButton("Apply")
        self.button_cancel = QPushButton("Cancel")

        for section in self.sections:
            self.listwidget_settings.addItem(section.name)
            self.stackedwidget_settings.addWidget(section)
        self.listwidget_settings.setFixedWidth(self.listwidget_settings.sizeHintForColumn(0) + 60)
        self.current_section_rowno = 0
        self.listwidget_settings.item(self.current_section_rowno).setSelected(True)

        # Bind
        self.listwidget_settings.selectionModel().selectionChanged.connect(self.on_selection_changed)
        self.button_reset.clicked.connect(self.reset_settings)
        self.button_save.clicked.connect(self.apply_settings_and_close)
        self.button_apply.clicked.connect(self.apply_settings)
        self.button_cancel.clicked.connect(self.reject)

        self.addWidget(self.listwidget_settings, 0, 0)
        self.addWidget(self.scrollarea_settings, 0, 1)
        self.addButtons(self.button_reset, alignment=Ng_Dialog.ButtonAlignmentFlag.AlignLeft)
        self.addButtons(
            self.button_save,
            self.button_apply,
            self.button_cancel,
            alignment=Ng_Dialog.ButtonAlignmentFlag.AlignRight,
        )

    # https://github.com/BLKSerene/Wordless/blob/fa743bcc2a366ec7a625edc4ed6cfc355b7cd22e/wordless/wl_settings/wl_settings.py#L234
    def on_selection_changed(self, selected, deselected) -> None:
        if not self.listwidget_settings.selectionModel().selectedIndexes():
            return

        current_widget: Ng_Widget_Settings_Abstract = self.stackedwidget_settings.currentWidget()
        if current_widget.verify_settings():
            selected_rowno = self.listwidget_settings.selectionModel().currentIndex().row()
            self.stackedwidget_settings.setCurrentIndex(selected_rowno)
            self.current_section_rowno = selected_rowno
        else:
            self.listwidget_settings.selectionModel().blockSignals(True)
            self.listwidget_settings.clearSelection()
            self.listwidget_settings.setCurrentRow(self.current_section_rowno)
            self.listwidget_settings.selectionModel().blockSignals(False)

    def load_settings(self) -> None:
        for section in self.sections:
            section.load_settings()

    def apply_settings(self) -> bool:
        for section in self.sections:
            if not section.verify_settings():
                return False
        else:
            for section in self.sections:
                section.apply_settings()
            return True

    def apply_settings_and_close(self) -> None:
        if self.apply_settings():
            Ng_Settings.sync()
            self.accept()

    def reset_settings(self) -> None:
        messagebox = Ng_MessageBox_Confirm(
            self, "Reset All Settings", "Settings across <b>all pages</b> will be reset. Continue?"
        )
        if messagebox.exec():
            Ng_Settings.reset()
            self.load_settings()

    # Override
    def exec(self) -> None:
        self.load_settings()
        # Avoid triggering "on_current_section_changed" at startup, which
        # should happen after being edited by users
        self.listwidget_settings.blockSignals(True)
        self.listwidget_settings.setCurrentRow(self.current_section_rowno)
        self.listwidget_settings.blockSignals(False)
        super().exec()
