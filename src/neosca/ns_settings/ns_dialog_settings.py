#!/usr/bin/env python3

from PyQt5.QtWidgets import QDialogButtonBox, QListWidget, QMessageBox, QStackedWidget

from ..ns_settings.ns_settings import NsSettings
from ..ns_settings.ns_widget_settings_abstract import NsWidgetSettingsAbstract
from ..ns_settings.ns_widget_settings_appearance import NsWidgetSettingsAppearance
from ..ns_settings.ns_widget_settings_export import NsWidgetSettingsExport
from ..ns_settings.ns_widget_settings_import import NsWidgetSettingsImport
from ..ns_settings.ns_widget_settings_lca import NsWidgetSettingsLCA
from ..ns_settings.ns_widget_settings_misc import NsWidgetSettingsMisc
from ..ns_widgets.ns_dialogs import NsDialog
from ..ns_widgets.ns_widgets import NsMessageboxQuestion, NsScrollArea


class NsDialogSettings(NsDialog):
    def __init__(self, main):
        super().__init__(main, title="Settings", width=1024, height=768, resizable=True)

        self.sections = (
            NsWidgetSettingsAppearance(main),
            NsWidgetSettingsImport(main),
            NsWidgetSettingsExport(main),
            NsWidgetSettingsLCA(main),
            NsWidgetSettingsMisc(main),
        )
        self.listwidget_settings = QListWidget()
        self.stackedwidget_settings = QStackedWidget()
        self.scrollarea_settings = NsScrollArea()
        self.scrollarea_settings.setWidget(self.stackedwidget_settings)

        buttonbox = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Reset
            | QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
            | QDialogButtonBox.StandardButton.Apply
        )
        self.button_reset = buttonbox.button(QDialogButtonBox.StandardButton.Reset)
        self.button_ok = buttonbox.button(QDialogButtonBox.StandardButton.Ok)
        self.button_cancel = buttonbox.button(QDialogButtonBox.StandardButton.Cancel)
        self.button_apply = buttonbox.button(QDialogButtonBox.StandardButton.Apply)
        # self.button_reset = QPushButton("Reset all settings")
        # self.button_ok = QPushButton("OK")
        # self.button_cancel = QPushButton("Cancel")
        # self.button_apply = QPushButton("Apply")

        for section in self.sections:
            self.listwidget_settings.addItem(section.name)
            self.stackedwidget_settings.addWidget(section)
        self.listwidget_settings.setFixedWidth(self.listwidget_settings.sizeHintForColumn(0) + 60)
        self.current_section_rowno = 0
        self.listwidget_settings.item(self.current_section_rowno).setSelected(True)

        # Bind
        self.listwidget_settings.selectionModel().selectionChanged.connect(self.on_selection_changed)
        self.button_reset.clicked.connect(self.reset_settings)

        self.button_ok.clicked.connect(self.apply_settings_and_close)
        self.button_cancel.clicked.connect(self.reject)
        self.button_apply.clicked.connect(self.apply_settings)

        self.addWidget(self.listwidget_settings, 0, 0)
        self.addWidget(self.scrollarea_settings, 0, 1)
        self.addButtons(self.button_reset, alignment=NsDialog.ButtonAlignmentFlag.AlignLeft)
        self.addButtons(
            self.button_ok,
            self.button_cancel,
            self.button_apply,
            alignment=NsDialog.ButtonAlignmentFlag.AlignRight,
        )

    # https://github.com/BLKSerene/Wordless/blob/fa743bcc2a366ec7a625edc4ed6cfc355b7cd22e/wordless/wl_settings/wl_settings.py#L234
    def on_selection_changed(self, selected, deselected) -> None:
        if not self.listwidget_settings.selectionModel().selectedIndexes():
            return

        current_widget: NsWidgetSettingsAbstract = self.stackedwidget_settings.currentWidget()  # type: ignore
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
            NsSettings.sync()
            self.accept()

    def reset_settings(self) -> None:
        messagebox = NsMessageboxQuestion(
            self, "Reset All Settings", "Settings across <b>all pages</b> will be reset. Continue?"
        )
        if messagebox.exec() == QMessageBox.StandardButton.Yes:
            NsSettings.reset()
            self.load_settings()

    # Override
    def exec(self) -> int:
        self.load_settings()
        # Avoid triggering "on_current_section_changed" at startup, which
        # should happen after being edited by users
        self.listwidget_settings.blockSignals(True)
        self.listwidget_settings.setCurrentRow(self.current_section_rowno)
        self.listwidget_settings.blockSignals(False)
        return super().exec()

    # Override
    def open(self) -> None:
        self.load_settings()
        self.listwidget_settings.blockSignals(True)
        self.listwidget_settings.setCurrentRow(self.current_section_rowno)
        self.listwidget_settings.blockSignals(False)
        return super().open()
