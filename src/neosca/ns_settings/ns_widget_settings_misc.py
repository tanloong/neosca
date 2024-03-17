#!/usr/bin/env python3

from PyQt5.QtWidgets import QCheckBox, QGridLayout, QGroupBox

from neosca.ns_settings.ns_settings import Ns_Settings
from neosca.ns_settings.ns_widget_settings_abstract import Ns_Widget_Settings_Abstract


class Ns_Widget_Settings_Misc(Ns_Widget_Settings_Abstract):
    name: str = "Miscellaneous"

    def __init__(self, main=None):
        super().__init__(main)
        self.setup_cache()
        self.setup_warning()

        self.gridlayout.addWidget(self.groupbox_cache, 0, 0)
        self.gridlayout.addWidget(self.groupbox_warning, 1, 0)
        self.gridlayout.setRowStretch(self.gridlayout.rowCount(), 1)

    def setup_cache(self) -> None:
        self.checkbox_cache = QCheckBox("Cache uncached files for faster future runs")
        self.checkbox_use_cache = QCheckBox("Use cache if available")

        gridlayout_cache = QGridLayout()
        gridlayout_cache.addWidget(self.checkbox_cache, 0, 0)
        gridlayout_cache.addWidget(self.checkbox_use_cache, 1, 0)
        self.groupbox_cache = QGroupBox("Cache")
        self.groupbox_cache.setLayout(gridlayout_cache)

    def setup_warning(self) -> None:
        self.checkbox_dont_warn_on_exit = QCheckBox("Don't warn on exit")
        self.checkbox_dont_warn_on_cache_deletion = QCheckBox("Don't warn on cache deletion")

        gridlayout_warning = QGridLayout()
        gridlayout_warning.addWidget(self.checkbox_dont_warn_on_exit, 0, 0)
        gridlayout_warning.addWidget(self.checkbox_dont_warn_on_cache_deletion, 1, 0)
        self.groupbox_warning = QGroupBox("Warning")
        self.groupbox_warning.setLayout(gridlayout_warning)

    def load_settings(self) -> None:
        self.load_settings_cache()
        self.load_settings_warning()

    def load_settings_cache(self) -> None:
        self.checkbox_cache.setChecked(Ns_Settings.value(f"{self.name}/cache", type=bool))
        self.checkbox_use_cache.setChecked(Ns_Settings.value(f"{self.name}/use-cache", type=bool))

    def load_settings_warning(self) -> None:
        self.checkbox_dont_warn_on_exit.setChecked(
            Ns_Settings.value(f"{self.name}/dont-warn-on-exit", type=bool)
        )
        self.checkbox_dont_warn_on_cache_deletion.setChecked(
            Ns_Settings.value(f"{self.name}/dont-warn-on-cache-deletion", type=bool)
        )

    def verify_settings(self) -> bool:
        return True

    def apply_settings(self) -> None:
        self.apply_settings_cache()
        self.apply_settings_warning()

    def apply_settings_cache(self) -> None:
        Ns_Settings.setValue(f"{self.name}/cache", self.checkbox_cache.isChecked())
        Ns_Settings.setValue(f"{self.name}/use-cache", self.checkbox_use_cache.isChecked())

    def apply_settings_warning(self) -> None:
        Ns_Settings.setValue(f"{self.name}/dont-warn-on-exit", self.checkbox_dont_warn_on_exit.isChecked())
        Ns_Settings.setValue(
            f"{self.name}/dont-warn-on-cache-deletion",
            self.checkbox_dont_warn_on_cache_deletion.isChecked(),
        )
