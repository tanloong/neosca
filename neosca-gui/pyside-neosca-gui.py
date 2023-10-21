#!/usr/bin/env python3
# -*- coding=utf-8 -*-

import os
import os.path as os_path
import subprocess
import sys
from typing import Dict, List

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt

from neosca.structure_counter import StructureCounter


class MyWidget(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setup_menu()
        self.setup_main_window()
        self.setup_env()

    def setup_menu(self):
        menubar = QtWidgets.QMenuBar()
        menubar.setStyleSheet("background-color: cyan;")
        menu_file = QtWidgets.QMenu("File")
        action_open_file = QtGui.QAction("Open File", menu_file)
        action_open_file.triggered.connect(self.browse_file)
        action_open_folder = QtGui.QAction("Open Folder", menu_file)
        action_restart = QtGui.QAction("Restart", menu_file)
        action_restart.triggered.connect(self.restart)
        action_restart.setShortcut(QtGui.QKeySequence(Qt.CTRL | Qt.Key_R))
        action_close = QtGui.QAction("Close", menu_file)
        action_close.triggered.connect(self.close)
        menu_file.addAction(action_open_file)
        menu_file.addAction(action_open_folder)
        menu_file.addAction(action_restart)
        menu_file.addAction(action_close)
        menubar.addMenu(menu_file)
        self.setMenuBar(menubar)

    def setup_main_window(self):
        frame_preview = QtWidgets.QFrame()
        frame_preview.setStyleSheet("background-color: green;")
        self.model = QtGui.QStandardItemModel()
        self.table_preview = QtWidgets.QTableView()
        self.table_preview.setModel(self.model)
        self.model.setColumnCount(len(StructureCounter.DEFAULT_MEASURES))
        self.model.setHorizontalHeaderLabels(StructureCounter.DEFAULT_MEASURES)
        self.model.setRowCount(1)
        layout_preview_button = QtWidgets.QHBoxLayout()
        self.button_generate_table = QtWidgets.QPushButton("Generate table")
        self.button_generate_table.clicked.connect(self.sca_generate_table)
        self.button_export_table = QtWidgets.QPushButton("Export all cells...")
        self.button_export_table.setEnabled(False)
        self.button_export_selected_cells = QtWidgets.QPushButton("Export selected cells...")
        self.button_export_selected_cells.setEnabled(False)
        layout_preview_button.addWidget(self.button_generate_table)
        layout_preview_button.addWidget(self.button_export_table)
        layout_preview_button.addWidget(self.button_export_selected_cells)
        layout_preview = QtWidgets.QVBoxLayout()
        layout_preview.addWidget(self.table_preview)
        layout_preview.addLayout(layout_preview_button)
        frame_preview.setLayout(layout_preview)

        frame_setting = QtWidgets.QFrame()
        frame_setting.setStyleSheet("background-color: pink;")
        self.checkbox_reserve_parsed_trees = QtWidgets.QCheckBox(
            "Reserve parsed trees", frame_setting
        )
        self.checkbox_reserve_parsed_trees.setChecked(True)
        self.checkbox_reserve_matched_subtrees = QtWidgets.QCheckBox(
            "Reserve matched subtrees", frame_setting
        )
        self.checkbox_reserve_matched_subtrees.setChecked(True)
        layout_setting = QtWidgets.QVBoxLayout()
        layout_setting.addWidget(self.checkbox_reserve_parsed_trees)
        layout_setting.addWidget(self.checkbox_reserve_matched_subtrees)
        frame_setting.setLayout(layout_setting)

        layout_upper = QtWidgets.QHBoxLayout()
        layout_upper.addWidget(frame_preview)
        layout_upper.addWidget(frame_setting)

        self.listwidget_file = QtWidgets.QListWidget()
        self.listwidget_file.setStyleSheet("background-color: red;")
        self.listwidget_file.setMaximumHeight(150)
        self.listwidget_file.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.listwidget_file.customContextMenuRequested.connect(self.showContextMenu)
        self.listwidget_file.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        layout_main = QtWidgets.QVBoxLayout()
        layout_main.addLayout(layout_upper, stretch=3)
        layout_main.addWidget(self.listwidget_file, stretch=1)
        container = QtWidgets.QWidget()
        container.setLayout(layout_main)
        self.setCentralWidget(container)

    def setup_env(self) -> None:
        neosca_gui_home = os_path.dirname(os_path.dirname(os_path.abspath(__file__)))
        libs_dir = os_path.join(neosca_gui_home, "libs")
        self.java_home = os_path.join(libs_dir, "jdk8u372")
        self.stanford_parser_home = os_path.join(libs_dir, "stanford-parser-full-2020-11-17")
        self.stanford_tregex_home = os_path.join(libs_dir, "stanford-tregex-2020-11-17")
        os.environ["JAVA_HOME"] = self.java_home
        os.environ["STANFORD_PARSER_HOME"] = self.stanford_parser_home
        os.environ["STANFORD_TREGEX_HOME"] = self.stanford_tregex_home
        self.env = os.environ.copy()

    def sca_generate_table(self) -> None:
        from neosca.neosca import NeoSCA

        input_file_items = self.listwidget_file.findItems(".*", QtCore.Qt.MatchFlag.MatchRegularExpression)
        if not input_file_items:
            QtWidgets.QMessageBox.warning(self, "Warning", f"{len(input_file_items)} Please select files to merge.")
            return

        input_files = [item.text() for item in input_file_items]
        self.button_generate_table.setEnabled(False)
        # ttk.Label(
        #     self.log_window,
        #     text="NeoSCA is running. It may take a few minutes to finish the job. Please wait.",
        # ).grid(column=0, row=0)

        sca_kwargs = {
            "is_auto_save": False,
            "ofile_freq": "",
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

        sca_analyzer.run_on_ifiles(input_files)
        sname_value_maps: List[Dict[str, str]] = [
            counter.get_all_values() for counter in sca_analyzer.counters
        ]
        self.model.setRowCount(0)
        for i, map_ in enumerate(sname_value_maps):
            items = [QtGui.QStandardItem(value) for value in map_.values()]
            self.model.insertRow(i, items)
        self.button_export_table.setEnabled(True)
        # don't have to enbale generate buttons here as they should only be
        # enabled when more input files are added

    def browse_file(self):
        file_dialog = QtWidgets.QFileDialog(
            directory="/home/tan/docx/corpus/YuHua-parallel-corpus-zh-en/02aligned/standalone/"
        )
        files, _ = file_dialog.getOpenFileNames(
            self, "Open Files", "", "Text Files (*.txt);;Docx Files (*.docx)"
        )
        if files:
            self.listwidget_file.clear()
            self.listwidget_file.addItems(files)

    def showContextMenu(self, position):
        menu = QtWidgets.QMenu()
        remove_action = menu.addAction("Remove")
        action = menu.exec_(self.listwidget_file.mapToGlobal(position))
        if action == remove_action:
            selected_items = self.listwidget_file.selectedItems()
            for item in selected_items:
                self.listwidget_file.takeItem(self.listwidget_file.row(item))

    def restart(self):
        self.close()
        command = [sys.executable] + sys.argv
        subprocess.call(command, env=os.environ.copy(), close_fds=False)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    widget = MyWidget()
    widget.show()
    sys.exit(app.exec())
