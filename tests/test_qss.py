#!/usr/bin/env python3

from PyQt5.QtWidgets import QWidget

from neosca.ns_consts import QSS_PATH
from neosca.ns_qss import Ns_QSS

from .base_tmpl import BaseTmpl


class TestQSS(BaseTmpl):
    def test_str_to_mapping(self):
        func = Ns_QSS.str_to_mapping

        # Every value be followed by a ";"
        mapping = {"font-size": "11pt;", "QTableView": {"color": "black;"}}
        self.assertNotEqual(func("font-size: 11pt QTableView {color: black;}"), mapping)
        # The following ";" should be attached to the value
        self.assertNotEqual(func("font-size: 11pt ; QTableView {color: black;}"), mapping)
        self.assertEqual(func("font-size: 11pt; QTableView {color: black;}"), mapping)
        # The following ";" should be separated from the subsequent token
        mapping = {"font-size": "11pt;", "max-width": "75px;"}
        self.assertNotEqual(func("font-size: 11pt;max-width: 75px;"), mapping)
        self.assertEqual(func("font-size: 11pt; max-width: 75px;"), mapping)

        mapping = {"font-size": "11pt;"}
        # The ":" following a property should be attached to the lhs property
        self.assertNotEqual(func("font-size : 11pt;"), mapping)
        # The ":" following a property should be separated from the rhs value
        self.assertNotEqual(func("font-size :11pt;"), mapping)
        self.assertEqual(func("font-size: 11pt;"), mapping)

        # Values can have whitespaces
        self.assertEqual(func("font-family: Noto Sans;"), {"font-family": "Noto Sans;"})
        self.assertEqual(func("font-family: 'Noto Sans';"), {"font-family": "'Noto Sans';"})

        # Selectors can have whitespaces
        self.assertEqual(
            func("QDialog QPushButton { color: black; }"), {"QDialog QPushButton": {"color": "black;"}}
        )
        self.assertEqual(
            func("QDialog > QPushButton { color: black; }"), {"QDialog > QPushButton": {"color": "black;"}}
        )
        # "{" and "}" can not be separated from others
        self.assertEqual(
            func("QDialog QPushButton{color: black;}"), {"QDialog QPushButton": {"color": "black;"}}
        )

        # Later value for the same property will override the previous one
        self.assertEqual(func("font-size: 12pt; font-size: 21pt;"), {"font-size": "21pt;"})

        # Test various selector types
        # https://doc.qt.io/qt-6/stylesheet-syntax.html#selector-types
        self.assertEqual(
            func("QTableView::item:selected { background-color: #C7C7C7;}"),
            {"QTableView::item:selected": {"background-color": "#C7C7C7;"}},
        )
        self.assertEqual(func("* {font-size: 11pt;}"), {"*": {"font-size": "11pt;"}})
        self.assertEqual(
            func("QPushButton[flat='false'] {font-size: 11pt;}"),
            {"QPushButton[flat='false']": {"font-size": "11pt;"}},
        )
        self.assertEqual(func(".QPushButton {font-size: 11pt;}"), {".QPushButton": {"font-size": "11pt;"}})
        self.assertEqual(
            func("*[class~='QPushButton'] {font-size: 11pt;}"),
            {"*[class~='QPushButton']": {"font-size": "11pt;"}},
        )
        self.assertEqual(
            func("QPushButton#okButton {font-size: 11pt;}"), {"QPushButton#okButton": {"font-size": "11pt;"}}
        )

    def test_mapping_to_str(self):
        to_string = Ns_QSS.mapping_to_str
        to_mapping = Ns_QSS.str_to_mapping

        self.assertEqual(to_string({"font-size": "11pt;"}), to_string(to_mapping("font-size: 11pt;")))
        self.assertEqual(to_string({"font-size": "11pt"}), to_string(to_mapping("font-size: 11pt;")))

        self.assertEqual(
            to_string({"font-size": "11pt", "QTableView": {"color": "red"}}),
            to_string(to_mapping("font-size: 11pt; QTableView {color: red;}")),
        )
        self.assertEqual(
            to_string({"font-size": "11pt;", "QTableView": {"color": "red;"}}),
            to_string(to_mapping("font-size: 11pt; QTableView {color: red;}")),
        )

    def test_get_value(self):
        qss_str = """QHeaderView::section:horizontal { background-color: #5C88C5; }
                     QHeaderView::section:vertical { background-color: #737373; }
                     QHeaderView::section { color: #FFFFFF; font-weight: bold; }"""
        self.assertEqual(
            Ns_QSS.get_value(qss_str, "QHeaderView::section:horizontal", "background-color"), "#5C88C5"
        )
        self.assertEqual(
            Ns_QSS.get_value(qss_str, "QHeaderView::section:vertical", "background-color"), "#737373"
        )
        self.assertEqual(Ns_QSS.get_value(qss_str, "QHeaderView::section", "color"), "#FFFFFF")

    def test_set_value(self):
        w = QWidget()
        qss = Ns_QSS.read_qss_file(QSS_PATH)
        w.setStyleSheet(qss)

        font_size = 20
        Ns_QSS.update(w, {"*": {"font-size": f"{font_size}pt;"}})
        self.assertEqual(Ns_QSS.get_value(w.styleSheet(), "*", "font-size"), f"{font_size}pt")
