#!/usr/bin/env python3


from PySide6.QtWidgets import QListWidget, QPushButton, QStackedWidget

from neosca_gui.ng_settings.ng_settings_appearance import Ng_Widget_Settings_Appearance
from neosca_gui.ng_settings.ng_settings_export import Ng_Widget_Settings_Export
from neosca_gui.ng_settings.ng_settings_import import Ng_Widget_Settings_Import
from neosca_gui.ng_singleton import QSingleton
from neosca_gui.ng_widgets import Ng_Dialog, Ng_ScrollArea


class Ng_Dialog_Settings(Ng_Dialog, metaclass=QSingleton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, title="Settings", width=768, height=576, resizable=True, **kwargs)

        self.sections = (
            Ng_Widget_Settings_Appearance(),
            Ng_Widget_Settings_Import(),
            Ng_Widget_Settings_Export(),
        )
        self.listwidget_settings = QListWidget()
        self.stackedwidget_settings = QStackedWidget()
        self.scrollarea_settings = Ng_ScrollArea()
        self.scrollarea_settings.setWidget(self.stackedwidget_settings)
        self.button_save = QPushButton("Save")
        self.button_apply = QPushButton("Apply")
        self.button_cancel = QPushButton("Cancel")

        for section in self.sections:
            self.listwidget_settings.addItem(section.name)
            self.stackedwidget_settings.addWidget(section)
        self.listwidget_settings.setFixedWidth(self.listwidget_settings.sizeHintForColumn(0) + 60)
        self.listwidget_settings.item(0).setSelected(True)

        # Bind
        self.listwidget_settings.currentRowChanged.connect(self.stackedwidget_settings.setCurrentIndex)
        # Hide setting dialog, and the same instance, instead of a newly
        # created one, will show up next time because it is a singleton.
        self.button_cancel.clicked.connect(self.hide)

        self.addWidget(self.listwidget_settings, 0, 0)
        self.addWidget(self.scrollarea_settings, 0, 1)
        self.addButtons(
            self.button_save,
            self.button_apply,
            self.button_cancel,
            alignment=Ng_Dialog.ButtonAlignmentFlag.AlignRight,
        )
