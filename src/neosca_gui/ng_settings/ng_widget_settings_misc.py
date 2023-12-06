#!/usr/bin/env python3


from PySide6.QtWidgets import QCheckBox, QGridLayout, QGroupBox, QSizePolicy, QSpacerItem

from neosca_gui.ng_settings.ng_settings import Ng_Settings
from neosca_gui.ng_settings.ng_widget_settings_abstract import Ng_Widget_Settings_Abstract


class Ng_Widget_Settings_Misc(Ng_Widget_Settings_Abstract):
    name: str = "Miscellaneous"

    def __init__(self, main=None):
        super().__init__(main)
        self.setup_cache()
        self.checkbox_dont_confirm_on_exit = QCheckBox("Don't confirm on exit")

        self.gridlayout.addWidget(self.groupbox_cache, 0, 0)
        self.gridlayout.addWidget(self.checkbox_dont_confirm_on_exit, 1, 0)
        self.gridlayout.addItem(QSpacerItem(0, 0, vData=QSizePolicy.Policy.Expanding))

    def setup_cache(self) -> None:
        self.checkbox_cache_for_future_runs = QCheckBox("Cache for future runs")
        self.checkbox_use_past_cache = QCheckBox("Use past cache if available")

        gridlayout_cache = QGridLayout()
        gridlayout_cache.addWidget(self.checkbox_cache_for_future_runs, 0, 0)
        gridlayout_cache.addWidget(self.checkbox_use_past_cache, 1, 0)
        self.groupbox_cache = QGroupBox("Cache")
        self.groupbox_cache.setLayout(gridlayout_cache)

    def load_settings(self) -> None:
        self.checkbox_dont_confirm_on_exit.setChecked(
            Ng_Settings.value(f"{self.name}/dont-confirm-on-exit", type=bool)
        )
        self.load_settings_cache()

    def load_settings_cache(self) -> None:
        self.checkbox_cache_for_future_runs.setChecked(
            Ng_Settings.value(f"{self.name}/cache-for-future-runs", type=bool)
        )
        self.checkbox_use_past_cache.setChecked(Ng_Settings.value(f"{self.name}/use-past-cache", type=bool))

    def verify_settings(self) -> bool:
        return True

    def apply_settings(self) -> None:
        Ng_Settings.setValue(
            f"{self.name}/dont-confirm-on-exit", self.checkbox_dont_confirm_on_exit.isChecked()
        )
        Ng_Settings.setValue(
            f"{self.name}/cache-for-future-runs", self.checkbox_cache_for_future_runs.isChecked()
        )
        Ng_Settings.setValue(f"{self.name}/use-past-cache", self.checkbox_use_past_cache.isChecked())
