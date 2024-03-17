#!/usr/bin/env python3

from PyQt5.QtGui import QFontDatabase
from PyQt5.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QLabel,
    QMessageBox,
    QSpinBox,
)

from neosca.ns_qss import Ns_QSS
from neosca.ns_settings.ns_settings import Ns_Settings
from neosca.ns_settings.ns_widget_settings_abstract import Ns_Widget_Settings_Abstract
from neosca.ns_widgets.ns_widgets import Ns_Combobox_Font


class Ns_Widget_Settings_Appearance(Ns_Widget_Settings_Abstract):
    name: str = "Appearance"

    def __init__(self, main):
        super().__init__(main)
        self.setup_scaling()
        self.setup_font()
        self.setup_table()

        self.gridlayout.addLayout(self.formlayout_scaling, 0, 0)
        self.gridlayout.addWidget(self.groupbox_font, 1, 0)
        self.gridlayout.addWidget(self.groupbox_table, 2, 0)
        self.gridlayout.setRowStretch(self.gridlayout.rowCount(), 1)

    def setup_scaling(self) -> None:
        label_scaling = QLabel("Scaling (requires restart):")
        self.combobox_scaling = QComboBox()
        # https://github.com/BLKSerene/Wordless/blob/1c319ce54be60aa948c89d6d3cdd327cccfc7c15/wordless/wl_settings/wl_settings_general.py#L53
        self.combobox_scaling.addItems([f"{opt}%" for opt in range(100, 301, 25)])
        self.formlayout_scaling = QFormLayout()
        self.formlayout_scaling.addRow(label_scaling, self.combobox_scaling)

    def setup_font(self) -> None:
        self.database = QFontDatabase()
        self.combobox_family = Ns_Combobox_Font()
        self.spinbox_point_size = QSpinBox()
        self.spinbox_point_size.setSuffix(" pt")
        self.checkbox_italic = QCheckBox("Italic")
        self.checkbox_bold = QCheckBox("Bold")
        self.gridlayout_font_style = QGridLayout()
        self.gridlayout_font_style.addWidget(self.checkbox_italic, 0, 0)
        self.gridlayout_font_style.addWidget(self.checkbox_bold, 0, 1)

        # Bind
        self.combobox_family.currentTextChanged.connect(self.set_italic_bold_enabled)

        formlayout_font = QFormLayout()
        formlayout_font.addRow(QLabel("Font family:"), self.combobox_family)
        formlayout_font.addRow(QLabel("Font size:"), self.spinbox_point_size)
        formlayout_font.addRow(QLabel("Font style:"), self.gridlayout_font_style)
        self.groupbox_font = QGroupBox("Font")
        self.groupbox_font.setLayout(formlayout_font)

    def set_italic_bold_enabled(self, family: str) -> None:
        available_styles = self.database.styles(family)
        if "Italic" in available_styles:
            self.checkbox_italic.setEnabled(True)
        else:
            self.checkbox_italic.setChecked(False)
            self.checkbox_italic.setEnabled(False)
        if "Bold" in available_styles:
            self.checkbox_bold.setEnabled(True)
        else:
            self.checkbox_bold.setChecked(False)
            self.checkbox_bold.setEnabled(False)

    def setup_table(self) -> None:
        self.doublespinbox_triangle_height_ratio = QDoubleSpinBox()
        self.doublespinbox_triangle_height_ratio.setDecimals(2)
        self.doublespinbox_triangle_height_ratio.setSingleStep(0.01)
        self.doublespinbox_triangle_height_ratio.setRange(0.01, 1.0)

        formlayout_table = QFormLayout()
        formlayout_table.addRow(QLabel("Triangle height ratio:"), self.doublespinbox_triangle_height_ratio)

        self.groupbox_table = QGroupBox("Tables")
        self.groupbox_table.setLayout(formlayout_table)

    def load_settings(self) -> None:
        self.load_settings_scaling()
        self.load_settings_font()
        self.load_settings_tables()

    def load_settings_scaling(self) -> None:
        key = f"{self.name}/scaling"
        self.combobox_scaling.setCurrentText(Ns_Settings.value(key))

    def load_settings_font(self) -> None:
        family = Ns_Settings.value(f"{self.name}/font-family")
        self.combobox_family.setCurrentText(family)
        # If previously set font doesn't has italic or bold style, disable the according checkbox
        self.set_italic_bold_enabled(family)
        self.checkbox_italic.setChecked(Ns_Settings.value(f"{self.name}/font-italic", type=bool))
        self.checkbox_bold.setChecked(Ns_Settings.value(f"{self.name}/font-bold", type=bool))
        self.spinbox_point_size.setRange(
            Ns_Settings.value(f"{self.name}/font-size-min", type=int),
            Ns_Settings.value(f"{self.name}/font-size-max", type=int),
        )
        self.spinbox_point_size.setValue(Ns_Settings.value(f"{self.name}/font-size", type=int))

    def load_settings_tables(self) -> None:
        key = f"{self.name}/triangle-height-ratio"
        self.doublespinbox_triangle_height_ratio.setValue(Ns_Settings.value(key, type=float))

    def verify_settings(self) -> bool:
        return self.verify_settings_scaling() and self.verify_settings_font() and self.verify_settings_tables()

    def verify_settings_scaling(self) -> bool:
        return True

    def verify_settings_font(self) -> bool:
        return self.verify_settings_font_family()

    def verify_settings_font_family(self) -> bool:
        font_family = self.combobox_family.currentText()
        if not font_family.strip():
            self.combobox_family.lineEdit().setFocus()
            self.combobox_family.lineEdit().selectAll()
            QMessageBox(
                QMessageBox.Icon.Warning,
                "Empty Font Family",
                "Font family should not be left empty.",
                QMessageBox.StandardButton.Ok,
                self,
            ).open()
            return False
        if font_family not in self.database.families():
            self.combobox_family.lineEdit().setFocus()
            self.combobox_family.lineEdit().selectAll()
            QMessageBox(
                QMessageBox.Icon.Warning,
                "Font Family Not Found",
                f'The specified font family "{font_family}" could not be found. Please check and try again.',
                QMessageBox.StandardButton.Ok,
                self,
            ).open()
            return False
        return True

    def verify_settings_tables(self) -> bool:
        return True

    def apply_settings(self) -> None:
        self.apply_settings_scaling()
        self.apply_settings_font()
        self.apply_settings_table()

    def apply_settings_scaling(self) -> None:
        key = f"{self.name}/scaling"
        Ns_Settings.setValue(key, self.combobox_scaling.currentText())

    def apply_settings_font(self) -> None:
        key = f"{self.name}/font-family"
        family = self.combobox_family.currentText()
        Ns_Settings.setValue(key, family)

        key = f"{self.name}/font-size"
        size = self.spinbox_point_size.value()
        Ns_Settings.setValue(key, size)

        key = f"{self.name}/font-italic"
        is_italic = self.checkbox_italic.isChecked()
        Ns_Settings.setValue(key, is_italic)

        key = f"{self.name}/font-bold"
        is_bold = self.checkbox_bold.isChecked()
        Ns_Settings.setValue(key, is_bold)

        Ns_QSS.update(
            self.main,
            {
                "*": {
                    "font-family": family,
                    "font-size": f"{size}pt",
                    "font-style": "italic" if is_italic else "normal",
                    "font-weight": "bold" if is_bold else "normal",
                }
            },
        )

    def apply_settings_table(self) -> None:
        key = f"{self.name}/triangle-height-ratio"
        ratio = self.doublespinbox_triangle_height_ratio.value()
        Ns_Settings.setValue(key, ratio)
