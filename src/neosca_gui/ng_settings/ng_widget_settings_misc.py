#!/usr/bin/env python3


from PySide6.QtWidgets import QCheckBox, QSizePolicy, QSpacerItem

from neosca_gui.ng_settings.ng_settings import Ng_Settings
from neosca_gui.ng_settings.ng_widget_settings_abstract import Ng_Widget_Settings_Abstract


class Ng_Widget_Settings_Misc(Ng_Widget_Settings_Abstract):
    name: str = "Miscellaneous"

    def __init__(self, main=None):
        super().__init__(main)
        self.checkbox_dont_confirm_on_exit = QCheckBox("Don't confirm on exit")

        self.gridlayout.addWidget(self.checkbox_dont_confirm_on_exit, 0, 0)
        self.gridlayout.addItem(QSpacerItem(0, 0, vData=QSizePolicy.Policy.Expanding))

    def load_settings(self) -> None:
        self.checkbox_dont_confirm_on_exit.setChecked(
            Ng_Settings.value(f"{self.name}/dont-confirm-on-exit", type=bool)
        )

    def verify_settings(self) -> bool:
        return True

    def apply_settings(self) -> None:
        Ng_Settings.setValue(f"{self.name}/dont-confirm-on-exit", self.checkbox_dont_confirm_on_exit.isChecked())
