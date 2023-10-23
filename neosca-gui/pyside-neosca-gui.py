#!/usr/bin/env python3
# -*- coding=utf-8 -*-

import os
import os.path as os_path
import re
import subprocess
import sys
from typing import Dict, List

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt
from neosca.neosca import NeoSCA
from neosca.structure_counter import StructureCounter
from neosca.lca.lca import LCA


class NeoSCA_GUI(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setup_menu()
        self.setup_main_window()
        self.setup_env()

    def setup_menu(self):
        menubar = QtWidgets.QMenuBar()
        # menubar.setStyleSheet("background-color: cyan;")
        menu_file = QtWidgets.QMenu("File")
        action_open_file = QtGui.QAction("Open File", menu_file)
        action_open_file.setShortcut(QtGui.QKeySequence(Qt.CTRL | Qt.Key_O))
        action_open_file.triggered.connect(self.browse_file)
        action_open_folder = QtGui.QAction("Open Folder", menu_file)
        action_restart = QtGui.QAction("Restart", menu_file)
        action_restart.triggered.connect(self.restart)
        action_restart.setShortcut(QtGui.QKeySequence(Qt.CTRL | Qt.Key_R))
        action_close = QtGui.QAction("Close", menu_file)
        action_close.setShortcut(QtGui.QKeySequence(Qt.CTRL | Qt.Key_Q))
        action_close.triggered.connect(self.close)
        menu_file.addAction(action_open_file)
        menu_file.addAction(action_open_folder)
        menu_file.addAction(action_restart)
        menu_file.addAction(action_close)
        menubar.addMenu(menu_file)
        self.setMenuBar(menubar)

    def setup_tab_sca(self):
        frame_preview_sca = QtWidgets.QFrame()
        # frame_preview.setStyleSheet("background-color: green;")
        self.model_sca = QtGui.QStandardItemModel()
        self.model_sca.setColumnCount(1 + len(StructureCounter.DEFAULT_MEASURES))
        self.model_sca.setHorizontalHeaderLabels(
            ["Filepath"] + StructureCounter.DEFAULT_MEASURES
        )
        self.model_sca.setRowCount(1)
        self.table_preview_sca = QtWidgets.QTableView()
        self.table_preview_sca.setModel(self.model_sca)
        self.table_preview_sca.setEditTriggers(
            QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers
        )
        layout_preview_button = QtWidgets.QHBoxLayout()
        self.button_generate_table_sca = QtWidgets.QPushButton("Generate table")
        self.button_generate_table_sca.setEnabled(False)
        self.button_generate_table_sca.clicked.connect(self.sca_generate_table)
        self.button_generate_table_sca.setShortcut(QtGui.QKeySequence(Qt.CTRL | Qt.Key_G))
        self.button_export_table_sca = QtWidgets.QPushButton("Export all cells...")
        self.button_export_table_sca.setEnabled(False)
        self.button_export_table_sca.clicked.connect(lambda :self.export_table(self.model_sca))
        # self.button_export_selected_cells = QtWidgets.QPushButton("Export selected cells...")
        # self.button_export_selected_cells.setEnabled(False)
        layout_preview_button.addWidget(self.button_generate_table_sca)
        layout_preview_button.addWidget(self.button_export_table_sca)
        # layout_preview_button.addWidget(self.button_export_selected_cells)
        layout_preview_sca = QtWidgets.QVBoxLayout()
        layout_preview_sca.addWidget(self.table_preview_sca)
        layout_preview_sca.addLayout(layout_preview_button)
        frame_preview_sca.setLayout(layout_preview_sca)

        frame_setting_sca = QtWidgets.QFrame()
        frame_setting_sca.setStyleSheet("background-color: white;")
        self.checkbox_reserve_parsed_trees = QtWidgets.QCheckBox(
            "Reserve parsed trees", frame_setting_sca
        )
        self.checkbox_reserve_parsed_trees.setChecked(True)
        self.checkbox_reserve_matched_subtrees = QtWidgets.QCheckBox(
            "Reserve matched subtrees", frame_setting_sca
        )
        self.checkbox_reserve_matched_subtrees.setChecked(True)
        layout_setting_sca = QtWidgets.QVBoxLayout()
        layout_setting_sca.addWidget(self.checkbox_reserve_parsed_trees)
        layout_setting_sca.addWidget(self.checkbox_reserve_matched_subtrees)
        frame_setting_sca.setLayout(layout_setting_sca)

        layout_tab_sca = QtWidgets.QHBoxLayout()
        layout_tab_sca.addWidget(frame_preview_sca)
        layout_tab_sca.addWidget(frame_setting_sca)

        self.tab_sca = QtWidgets.QWidget()
        self.tab_sca.setLayout(layout_tab_sca)

    def setup_tab_lca(self):
        frame_preview_lca = QtWidgets.QFrame()
        # frame_preview.setStyleSheet("background-color: green;")
        self.model_lca = QtGui.QStandardItemModel()
        self.model_lca.setColumnCount(len(LCA.FIELDNAMES))
        self.model_lca.setHorizontalHeaderLabels(LCA.FIELDNAMES)
        self.model_lca.setRowCount(1)
        self.table_preview_lca = QtWidgets.QTableView()
        self.table_preview_lca.setModel(self.model_lca)
        self.table_preview_lca.setEditTriggers(
            QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers
        )
        layout_preview_button = QtWidgets.QHBoxLayout()
        self.button_generate_table_lca = QtWidgets.QPushButton("Generate table")
        self.button_generate_table_lca.setEnabled(False)
        self.button_generate_table_lca.clicked.connect(self.lca_generate_table)
        self.button_generate_table_lca.setShortcut(QtGui.QKeySequence(Qt.CTRL | Qt.Key_G))
        self.button_export_table_lca = QtWidgets.QPushButton("Export all cells...")
        self.button_export_table_lca.setEnabled(False)
        self.button_export_table_lca.clicked.connect(lambda :self.export_table(self.model_lca))
        # self.button_export_selected_cells = QtWidgets.QPushButton("Export selected cells...")
        # self.button_export_selected_cells.setEnabled(False)
        layout_preview_button.addWidget(self.button_generate_table_lca)
        layout_preview_button.addWidget(self.button_export_table_lca)
        # layout_preview_button.addWidget(self.button_export_selected_cells)
        layout_preview_lca = QtWidgets.QVBoxLayout()
        layout_preview_lca.addWidget(self.table_preview_lca)
        layout_preview_lca.addLayout(layout_preview_button)
        frame_preview_lca.setLayout(layout_preview_lca)

        frame_setting_lca = QtWidgets.QFrame()
        frame_setting_lca.setStyleSheet("background-color: white;")
        self.radiobutton_wordlist_BNC = QtWidgets.QRadioButton(
            "British National Corpus (BNC) wordlist"
        )
        self.radiobutton_wordlist_BNC.setChecked(True)
        self.radiobutton_wordlist_ANC = QtWidgets.QRadioButton(
            "American National Corpus (ANC) wordlist"
        )
        layout_wordlist = QtWidgets.QVBoxLayout()
        layout_wordlist.addWidget(self.radiobutton_wordlist_BNC)
        layout_wordlist.addWidget(self.radiobutton_wordlist_ANC)
        self.groupbox_wordlist = QtWidgets.QGroupBox("Wordlist")
        self.groupbox_wordlist.setLayout(layout_wordlist)
        self.radiobutton_tagset_ud = QtWidgets.QRadioButton("Universal POS Tagset")
        self.radiobutton_tagset_ud.setChecked(True)
        self.radiobutton_tagset_ptb = QtWidgets.QRadioButton("Penn Treebank POS Tagset")
        layout_tagset = QtWidgets.QVBoxLayout()
        layout_tagset.addWidget(self.radiobutton_tagset_ud)
        layout_tagset.addWidget(self.radiobutton_tagset_ptb)
        self.groupbox_tagset = QtWidgets.QGroupBox("Tagset")
        self.groupbox_tagset.setLayout(layout_tagset)
        layout_setting_lca = QtWidgets.QVBoxLayout()
        layout_setting_lca.addWidget(self.groupbox_wordlist)
        layout_setting_lca.addWidget(self.groupbox_tagset)
        frame_setting_lca.setLayout(layout_setting_lca)

        layout_tab_lca = QtWidgets.QHBoxLayout()
        layout_tab_lca.addWidget(frame_preview_lca)
        layout_tab_lca.addWidget(frame_setting_lca)

        self.tab_lca = QtWidgets.QWidget()
        self.tab_lca.setLayout(layout_tab_lca)

    def setup_main_window(self):
        self.setup_tab_sca()
        self.setup_tab_lca()

        self.listwidget_file = QtWidgets.QListWidget()
        # self.listwidget_file.setStyleSheet("background-color: red;")
        self.listwidget_file.setMaximumHeight(150)
        self.listwidget_file.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.listwidget_file.customContextMenuRequested.connect(
            self.add_menu_for_listwidget_file
        )
        self.listwidget_file.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        tab_bar = QtWidgets.QTabWidget()
        tab_bar.addTab(self.tab_sca, "Syntactic Complexity Analyzer")
        tab_bar.addTab(self.tab_lca, "Lexical Complexity Analyzer")
        layout_main = QtWidgets.QVBoxLayout()
        layout_main.addWidget(tab_bar, stretch=3)
        layout_main.addWidget(self.listwidget_file, stretch=1)
        container = QtWidgets.QWidget()
        container.setLayout(layout_main)
        self.setCentralWidget(container)

    def setup_env(self) -> None:
        self.desktop = os_path.normpath(os_path.expanduser("~/Desktop"))
        neosca_gui_home = os_path.dirname(os_path.dirname(os_path.abspath(__file__)))
        libs_dir = os_path.join(neosca_gui_home, "libs")
        self.java_home = os_path.join(libs_dir, "jdk8u372")
        self.stanford_parser_home = os_path.join(libs_dir, "stanford-parser-full-2020-11-17")
        self.stanford_tregex_home = os_path.join(libs_dir, "stanford-tregex-2020-11-17")
        os.environ["JAVA_HOME"] = self.java_home
        os.environ["STANFORD_PARSER_HOME"] = self.stanford_parser_home
        os.environ["STANFORD_TREGEX_HOME"] = self.stanford_tregex_home
        self.env = os.environ.copy()

    def lca_generate_table(self) -> None:
        input_file_paths = [
            self.listwidget_file.item(i).text() for i in range(self.listwidget_file.count())
        ]
        if not input_file_paths:
            QtWidgets.QMessageBox.warning(
                self, "No input files", f"Please select files to process."
            )
            return

        self.button_generate_table_lca.setEnabled(False)
        lca_kwargs = {
            "wordlist": "bnc" if self.radiobutton_wordlist_BNC.isChecked() else "anc",
            "tagset": "ud" if self.radiobutton_tagset_ud.isChecked() else "ptb",
            "is_stdout": False,
        }
        attrname = "lca_analyzer"
        try:
            lca_analyzer = getattr(self, attrname)
        except AttributeError:
            lca_analyzer = LCA(**lca_kwargs)
            setattr(self, attrname, lca_analyzer)
        else:
            lca_analyzer.update_options(lca_kwargs)

        self.model_lca.setRowCount(0)
        for file_path in input_file_paths:
            values = lca_analyzer._analyze(file_path=file_path)
            if values is None:  # TODO: should pop up warning window
                continue
            items = [QtGui.QStandardItem(value) for value in values]
            self.model_lca.appendRow(items)
        if self.model_lca.rowCount() >= 1:
            self.button_export_table_lca.setEnabled(True)
        else:
            self.model_lca.setRowCount(1)

    def sca_generate_table(self) -> None:
        input_file_paths = [
            self.listwidget_file.item(i).text() for i in range(self.listwidget_file.count())
        ]
        if not input_file_paths:
            QtWidgets.QMessageBox.warning(
                self, "No input files", f"Please select files to process."
            )
            return

        self.button_generate_table_sca.setEnabled(False)
        # messagebox_processing = QtWidgets.QMessageBox(self)
        # messagebox_processing.setWindowTitle("Please waite.")
        # # dialog_processing.resize(300, 200)
        # messagebox_processing.setText("NeoSCA is running. It may take a few minutes to finish the job. Please wait.")
        # messagebox_processing.open()

        sca_kwargs = {
            "is_auto_save": False,
            "stanford_parser_home": self.stanford_parser_home,
            "stanford_tregex_home": self.stanford_tregex_home,
            "odir_matched": "",
            "newline_break": "never",
            "max_length": None,
            "selected_measures": None,
            "is_reserve_parsed": self.checkbox_reserve_parsed_trees.isChecked(),
            "is_reserve_matched": self.checkbox_reserve_matched_subtrees.isChecked(),
            "is_skip_querying": False,
            "is_skip_parsing": False,
            "is_pretokenized": False,
            "config": None,
        }

        attrname = "sca_analyzer"
        try:
            sca_analyzer = getattr(self, attrname)
        except AttributeError:
            sca_analyzer = NeoSCA(**sca_kwargs)
            setattr(self, attrname, sca_analyzer)
        else:
            sca_analyzer.update_options(sca_kwargs)

        sca_analyzer.run_on_ifiles(input_file_paths)
        sname_value_maps: List[Dict[str, str]] = [
            counter.get_all_values() for counter in sca_analyzer.counters
        ]
        self.model_sca.setRowCount(0)
        for i, map_ in enumerate(sname_value_maps):
            items = [QtGui.QStandardItem(value) for value in map_.values()]
            self.model_sca.appendRow(items)
        if self.model_sca.rowCount() >= 1:
            self.button_export_table_sca.setEnabled(True)
        else:
            self.model_sca.setRowCount(1)
        # don't have to enbale generate buttons here as they should only be
        # enabled when more input files are added
        # messagebox_processing.close()

    def export_table(self, model: QtGui.QStandardItemModel) -> None:
        file_path, file_type = QtWidgets.QFileDialog.getSaveFileName(
            parent=self,
            caption="Export Table",
            dir=self.desktop,
            filter="Excel Workbook (*.xlsx);;CSV File (*.csv);;TSV File (*.tsv)",
        )
        if not file_path:
            return

        col_count = model.columnCount()
        row_count = model.rowCount()
        try:
            if ".xlsx" in file_type:
                # https://github.com/BLKSerene/Wordless/blob/main/wordless/wl_widgets/wl_tables.py#L701C1-L716C54
                import openpyxl

                workbook = openpyxl.Workbook()
                worksheet = workbook.active
                # Header
                for colno_cell, colno_item in enumerate(range(col_count)):
                    cell = worksheet.cell(1, 1 + colno_cell)
                    cell.value = model.horizontalHeaderItem(colno_item).text()
                # Cells
                for rowno_cell, rowno in enumerate(range(row_count)):
                    for colno_cell, colno_item in enumerate(range(col_count)):
                        cell = worksheet.cell(2 + rowno_cell, 1 + colno_cell)
                        cell.value = model.item(rowno, colno_item).text()
                workbook.save(file_path)
            elif ".csv" in file_type or ".tsv" in file_type:
                import csv

                dialect = csv.excel if ".csv" in file_type else csv.excel_tab
                with open(os_path.normpath(file_path), "w", newline="", encoding="utf-8") as fh:
                    csv_writer = csv.writer(fh, dialect=dialect, lineterminator="\n")
                    csv_writer.writerow(
                        model.horizontalHeaderItem(colno).text() for colno in range(col_count)
                    )
                    for rowno in range(row_count):
                        csv_writer.writerow(
                            model.item(rowno, colno).text() for colno in range(col_count)
                        )
            QtWidgets.QMessageBox.information(
                self, "Success", f"The table has been successfully exported to {file_path}."
            )
        except PermissionError:
            QtWidgets.QMessageBox.critical(
                self, "Error", f"PermissionError: failed to export the table to {file_path}."
            )

    def browse_file(self):
        file_dialog = QtWidgets.QFileDialog(
            directory="/home/tan/docx/corpus/YuHua-parallel-corpus-zh-en/02aligned/standalone/"
        )
        file_paths_to_add, _ = file_dialog.getOpenFileNames(
            self, "Open Files", "", "Text Files (*.txt);;Docx Files (*.docx)"
        )
        if not file_paths_to_add:
            return

        unique_file_paths_to_add = set(file_paths_to_add)
        added_file_paths = set(
            self.listwidget_file.item(i).text() for i in range(self.listwidget_file.count())
        )
        file_paths_dup = unique_file_paths_to_add & added_file_paths
        file_paths_ok = [
            file_path
            for file_path in (unique_file_paths_to_add - added_file_paths)
            if os_path.getsize(file_path)
        ]
        if file_paths_ok:
            self.listwidget_file.addItems(file_paths_ok)
            # Enable "generate_table" button when new files are added
            self.button_generate_table_sca.setEnabled(True)
            self.button_generate_table_lca.setEnabled(True)

        if file_paths_dup:
            QtWidgets.QMessageBox.information(
                self,
                "Duplication",
                "These duplicated files are skipped:\n- {}".format("\n- ".join(file_paths_dup)),
            )

    def add_menu_for_listwidget_file(self, position):
        menu = QtWidgets.QMenu()
        remove_action = menu.addAction("Remove")
        action = menu.exec(self.listwidget_file.mapToGlobal(position))
        if action == remove_action:
            selected_items = self.listwidget_file.selectedItems()
            for item in selected_items:
                self.listwidget_file.takeItem(self.listwidget_file.row(item))
        if self.listwidget_file.count() <= 0:
            self.button_generate_table_sca.setEnabled(False)
            self.button_generate_table_lca.setEnabled(False)

    def restart(self):
        self.close()
        command = [sys.executable] + sys.argv
        subprocess.call(command, env=os.environ.copy(), close_fds=False)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    widget = NeoSCA_GUI()
    widget.show()
    sys.exit(app.exec())
