#!/usr/bin/env python3

from PyQt5.QtWidgets import QGridLayout, QGroupBox, QRadioButton

from neosca.ns_settings.ns_settings import Ns_Settings
from neosca.ns_settings.ns_widget_settings_abstract import Ns_Widget_Settings_Abstract


class Ns_Widget_Settings_LCA(Ns_Widget_Settings_Abstract):
    name: str = "Lexical Complexity Analyzer"

    def __init__(self, main):
        super().__init__(main)
        self.setup_wordlist()
        self.setup_tagset()

        self.gridlayout.addWidget(self.groupbox_wordlist, 0, 0)
        self.gridlayout.addWidget(self.groupbox_tagset, 1, 0)
        self.gridlayout.setRowStretch(self.gridlayout.rowCount(), 1)

    def setup_wordlist(self) -> None:
        self.radiobutton_wordlist_bnc = QRadioButton("British National Corpus (BNC) wordlist")
        self.radiobutton_wordlist_anc = QRadioButton("American National Corpus (ANC) wordlist")

        layout_wordlist = QGridLayout()
        layout_wordlist.addWidget(self.radiobutton_wordlist_bnc, 0, 0)
        layout_wordlist.addWidget(self.radiobutton_wordlist_anc, 1, 0)

        self.groupbox_wordlist = QGroupBox("Wordlist")
        self.groupbox_wordlist.setLayout(layout_wordlist)

    def setup_tagset(self) -> None:
        self.radiobutton_tagset_ud = QRadioButton("Universal POS Tagset")
        self.radiobutton_tagset_ptb = QRadioButton("Penn Treebank POS Tagset")

        layout_tagset = QGridLayout()
        layout_tagset.addWidget(self.radiobutton_tagset_ud, 0, 0)
        layout_tagset.addWidget(self.radiobutton_tagset_ptb, 1, 0)

        self.groupbox_tagset = QGroupBox("Tagset")
        self.groupbox_tagset.setLayout(layout_tagset)

    def load_settings(self) -> None:
        self.load_settings_wordlist()
        self.load_settings_tagset()

    def load_settings_wordlist(self) -> None:
        key = f"{self.name}/wordlist"
        value = Ns_Settings.value(key)
        if value == "bnc":
            self.radiobutton_wordlist_bnc.setChecked(True)
            self.radiobutton_wordlist_anc.setChecked(False)
        elif value == "anc":
            self.radiobutton_wordlist_bnc.setChecked(False)
            self.radiobutton_wordlist_anc.setChecked(True)
        else:
            assert False, f"Invalid wordlist setting: {value}"

    def load_settings_tagset(self) -> None:
        key = f"{self.name}/tagset"
        value = Ns_Settings.value(key)
        if value == "ud":
            self.radiobutton_tagset_ud.setChecked(True)
            self.radiobutton_tagset_ptb.setChecked(False)
        elif value == "ptb":
            self.radiobutton_tagset_ud.setChecked(False)
            self.radiobutton_tagset_ptb.setChecked(True)
        else:
            assert False, f"Invalid tagset setting: {value}"

    def verify_settings(self) -> bool:
        return self.verify_settings_wordlist() and self.verify_settings_tagset()

    def verify_settings_wordlist(self) -> bool:
        return True

    def verify_settings_tagset(self) -> bool:
        return True

    def apply_settings(self) -> None:
        self.apply_settings_wordlist()
        self.apply_settings_tagset()

    def apply_settings_wordlist(self) -> None:
        key = f"{self.name}/wordlist"
        if self.radiobutton_wordlist_bnc.isChecked():
            Ns_Settings.setValue(key, "bnc")
        elif self.radiobutton_wordlist_anc.isChecked():
            Ns_Settings.setValue(key, "anc")
        else:
            assert False, "Invalid wordlist setting"

    def apply_settings_tagset(self) -> None:
        key = f"{self.name}/tagset"
        if self.radiobutton_tagset_ud.isChecked():
            Ns_Settings.setValue(key, "ud")
        elif self.radiobutton_tagset_ptb.isChecked():
            Ns_Settings.setValue(key, "ptb")
        else:
            assert False, "Invalid tagset setting"
