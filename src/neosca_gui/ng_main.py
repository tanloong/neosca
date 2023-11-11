#!/usr/bin/env python3

import glob
import os
import os.path as os_path
import re
import subprocess
import sys
from typing import Dict, Generator, List, Literal, Optional, Set, Tuple

from PySide6.QtCore import QModelIndex, QObject, Qt, QThread, Signal
from PySide6.QtGui import (
    QAction,
    QCursor,
    QPalette,
    QStandardItem,
    QStandardItemModel,
)
from PySide6.QtWidgets import (
    QAbstractItemView,
    QAbstractScrollArea,
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHeaderView,
    QLabel,
    QMainWindow,
    QMenu,
    QMenuBar,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSplitter,
    QTableView,
    QTabWidget,
    QTextEdit,
    QWidget,
)

from .neosca.lca.lca import LCA
from .neosca.neosca import NeoSCA
from .neosca.scaio import SCAIO
from .neosca.structure_counter import StructureCounter


class Ng_Model(QStandardItemModel):
    data_cleared = Signal()
    data_updated = Signal()
    data_exported = Signal()

    def __init__(self, *args, orientation: Literal["hor", "ver"] = "hor", **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.orientation = orientation

        self.has_been_exported: bool = False
        self.data_exported.connect(lambda: self.set_has_been_exported(True))
        self.data_updated.connect(lambda: self.set_has_been_exported(False))

    def set_has_been_exported(self, exported: bool) -> None:
        self.has_been_exported = exported

    def clear_data(self) -> None:
        # https://stackoverflow.com/questions/75038194/qt6-how-to-disable-selection-for-empty-cells-in-qtableview
        if self.orientation == "hor":
            self.setRowCount(0)
            self.setRowCount(1)
        elif self.orientation == "ver":
            self.setColumnCount(0)
            self.setColumnCount(1)
        self.data_cleared.emit()


class Ng_Worker(QObject):
    worker_done = Signal()

    def __init__(self, main, dialog) -> None:
        super().__init__()
        self.main = main
        self.dialog = dialog

    # TODO
    # def cancel(self) -> None:
    #     self.terminate()
    #     self.wait() # TODO ?
    #     <<>>

    def run(self) -> None:
        raise NotImplementedError()


class Ng_Worker_SCA_Generate_Table(Ng_Worker):
    def __init__(self, main, dialog) -> None:
        super().__init__(main, dialog)

    def run(self) -> None:
        input_file_names: Generator[str, None, None] = self.main.yield_added_file_names()
        input_file_paths: Generator[str, None, None] = self.main.yield_added_file_paths()

        sca_kwargs = {
            "is_auto_save": False,
            "odir_matched": "",
            "selected_measures": None,
            "is_reserve_parsed": self.main.checkbox_reserve_parsed_trees.isChecked(),
            "is_reserve_matched": self.main.checkbox_reserve_matched_subtrees.isChecked(),
            "is_skip_querying": False,
            "is_skip_parsing": False,
            "config": None,
        }

        attrname = "sca_analyzer"
        try:
            sca_analyzer = getattr(self.main, attrname)
        except AttributeError:
            sca_analyzer = NeoSCA(**sca_kwargs)
            setattr(self.main, attrname, sca_analyzer)
        else:
            sca_analyzer.update_options(sca_kwargs)

        err_file_paths: List[str] = []
        model: Ng_Model = self.main.model_sca
        has_trailing_rows: bool = True
        for rowno, (file_name, file_path) in enumerate(zip(input_file_names, input_file_paths)):
            try:
                counter: Optional[StructureCounter] = sca_analyzer.parse_and_query_ifile(file_path)
                # TODO should concern --no-parse, --no-query, ... after adding all available options
            except:
                err_file_paths.append(file_path)
                continue
            if counter is None:
                err_file_paths.append(file_path)
                continue
            sname_value_map: Dict[str, str] = counter.get_all_values()
            _, *items = (QStandardItem(value) for value in sname_value_map.values())
            if has_trailing_rows:
                has_trailing_rows = model.removeRows(rowno, model.rowCount() - rowno)
            model.insertRow(rowno, items)
            model.setVerticalHeaderItem(rowno, QStandardItem(file_name))
        model.data_updated.emit()

        if err_file_paths:  # TODO: should show a table
            QMessageBox.information(
                self.main,
                "Error Processing Files",
                "These files are skipped:\n- {}".format("\n- ".join(err_file_paths)),
            )
        self.worker_done.emit()


class Ng_Worker_LCA_Generate_Table(Ng_Worker):
    def __init__(self, main, dialog) -> None:
        super().__init__(main, dialog)

    def run(self) -> None:
        input_file_names: Generator[str, None, None] = self.main.yield_added_file_names()
        input_file_paths: Generator[str, None, None] = self.main.yield_added_file_paths()

        lca_kwargs = {
            "wordlist": "bnc" if self.main.radiobutton_wordlist_BNC.isChecked() else "anc",
            "tagset": "ud" if self.main.radiobutton_tagset_ud.isChecked() else "ptb",
            "is_stdout": False,
        }
        attrname = "lca_analyzer"
        try:
            lca_analyzer = getattr(self.main, attrname)
        except AttributeError:
            lca_analyzer = LCA(**lca_kwargs)
            setattr(self.main, attrname, lca_analyzer)
        else:
            lca_analyzer.update_options(lca_kwargs)

        err_file_paths: List[str] = []
        model: Ng_Model = self.main.mode_lca
        has_trailing_rows: bool = True
        for rowno, (file_name, file_path) in enumerate(zip(input_file_names, input_file_paths)):
            try:
                values = lca_analyzer._analyze(file_path=file_path)
            except:
                err_file_paths.append(file_path)
                continue
            if values is None:  # TODO: should pop up warning window
                err_file_paths.append(file_path)
                continue
            _, *items = (QStandardItem(value) for value in values)
            if has_trailing_rows:
                has_trailing_rows = model.removeRows(rowno, model.rowCount() - rowno)
            model.insertRow(rowno, items)
            model.setVerticalHeaderItem(rowno, QStandardItem(file_name))
        model.data_updated.emit()

        if err_file_paths:  # TODO: should show a table
            QMessageBox.information(
                self.main,
                "Error Processing Files",
                "These files are skipped:\n- {}".format("\n- ".join(err_file_paths)),
            )

        self.worker_done.emit()


class Ng_Thread(QThread):
    def __init__(self, worker):
        super().__init__()
        self.worker = worker
        # https://mayaposch.wordpress.com/2011/11/01/how-to-really-truly-use-qthreads-the-full-explanation/
        self.worker.moveToThread(self)

        self.started.connect(self.worker.dialog.open)
        self.finished.connect(self.worker.dialog.accept)

    def run(self):
        self.start()
        self.worker.run()


class Ng_Dialog(QDialog):
    def __init__(self, *args, main, title: str = "", size: Tuple[int, int] = (300, 200), **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.main = main
        self.setWindowTitle(title)
        self.resize(*size)
        # ┌———————————┐
        # │           │
        # │  content  │
        # │           │
        # │———————————│
        # │  buttons  │
        # └———————————┘
        self.content_layout = QGridLayout()
        self.button_layout = QGridLayout()

        self.grid_layout = QGridLayout()
        self.grid_layout.addLayout(self.content_layout, 0, 0)
        self.grid_layout.addLayout(self.button_layout, 1, 0)
        self.setLayout(self.grid_layout)

        # self.setSizeGripEnabled(True)

    def addWidget(self, *args, **kwargs) -> None:
        self.content_layout.addWidget(*args, **kwargs)

    def addButton(self, *args, **kwargs) -> None:
        self.button_layout.addWidget(*args, **kwargs)


class Ng_Dialog_Table(Ng_Dialog):
    def __init__(
        self,
        *args,
        text: str,
        tableview: QTableView,
        model_has_horizontal_header: bool = True,
        model_has_vertical_header: bool = True,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.model = tableview.model()
        self.model_has_horizontal_header = model_has_horizontal_header
        self.model_has_vertical_header = model_has_vertical_header

        self.content_layout.addWidget(QLabel(text), 0, 0)
        self.content_layout.addWidget(tableview, 1, 0)

        self.button_ok = QPushButton("OK")
        self.button_ok.clicked.connect(self.accept)
        self.button_export_table = QPushButton("Export table...")
        self.button_export_table.clicked.connect(
            lambda: self.main.export_table(
                self.model,
                has_horizontal_header=self.model_has_horizontal_header,
                has_vertical_header=self.model_has_vertical_header,
            )
        )
        self.button_layout.addWidget(self.button_export_table, 0, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        self.button_layout.addWidget(self.button_ok, 0, 1, alignment=Qt.AlignmentFlag.AlignRight)


class Ng_Main(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setup_env()

        self.setWindowTitle("NeoSCA-GUI")
        self.setup_menu()
        self.setup_worker()
        self.setup_main_window()

    def setup_menu(self):
        # File
        menu_file = QMenu("File")
        action_open_file = QAction("Open File...", menu_file)
        action_open_file.setShortcut("CTRL+O")
        action_open_file.triggered.connect(self.browse_file)
        action_open_folder = QAction("Open Folder...", menu_file)
        action_open_folder.setShortcut("CTRL+F")
        action_open_folder.triggered.connect(self.browse_folder)
        action_restart = QAction("Restart", menu_file)  # TODO remove this before releasing
        action_restart.triggered.connect(self.restart)  # TODO remove this before releasing
        action_restart.setShortcut("CTRL+R")  # TODO remove this before releasing
        action_quit = QAction("Quit", menu_file)
        action_quit.setShortcut("CTRL+Q")
        action_quit.triggered.connect(self.close)
        menu_file.addAction(action_open_file)
        menu_file.addAction(action_open_folder)
        menu_file.addAction(action_restart)
        menu_file.addAction(action_quit)
        # Help
        menu_help = QMenu("Help")
        action_citing = QAction("Citing", menu_help)
        action_citing.triggered.connect(self.show_help_citing)
        menu_help.addAction(action_citing)

        self.menuBar().addMenu(menu_file)
        self.menuBar().addMenu(menu_help)

    def show_help_citing(self) -> None:
        import json

        with open(os_path.join(self.here, "citing.json")) as f:
            style_citation_mapping = json.load(f)
        label_citing = QLabel("If you use NeoSCA-GUI in your research, please kindly cite as follows.")
        label_citing.setWordWrap(True)
        textedit_citing = QTextEdit()
        textedit_citing.setReadOnly(True)
        textedit_citing.setText(next(iter(style_citation_mapping.values())))
        label_choose_citation_style = QLabel("Choose citation style: ")
        combobox_choose_citation_style = QComboBox()
        combobox_choose_citation_style.addItems(tuple(style_citation_mapping.keys()))
        combobox_choose_citation_style.currentTextChanged.connect(
            lambda key: textedit_citing.setText(style_citation_mapping[key])
        )

        dialog_citing = Ng_Dialog(self, main=self, title="Citing")
        dialog_citing.addWidget(label_citing, 0, 0, 1, 2)
        dialog_citing.addWidget(label_choose_citation_style, 1, 0)
        dialog_citing.addWidget(combobox_choose_citation_style, 1, 1)
        dialog_citing.addWidget(textedit_citing, 2, 0, 1, 2)

        button_copy = QPushButton("Copy")
        button_copy.clicked.connect(textedit_citing.selectAll)
        button_copy.clicked.connect(textedit_citing.copy)
        button_close = QPushButton("Close")
        button_close.clicked.connect(dialog_citing.reject)

        dialog_citing.addButton(button_copy, 0, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        dialog_citing.addButton(button_close, 0, 1, alignment=Qt.AlignmentFlag.AlignRight)
        dialog_citing.open()

    def setup_tab_sca(self):
        self.button_generate_table_sca = QPushButton("Generate table")
        self.button_generate_table_sca.clicked.connect(self.ng_thread_sca_generate_table.start)
        self.button_generate_table_sca.setShortcut("CTRL+G")
        self.button_export_table_sca = QPushButton("Export all cells...")
        self.button_export_table_sca.setEnabled(False)
        self.button_export_table_sca.clicked.connect(lambda: self.export_table(self.model_sca))
        # self.button_export_selected_cells = QPushButton("Export selected cells...")
        # self.button_export_selected_cells.setEnabled(False)
        self.button_clear_table_sca = QPushButton("Clear table")
        self.button_clear_table_sca.setEnabled(False)
        self.button_clear_table_sca.clicked.connect(lambda: self.ask_clear_model(self.model_sca, "hor"))

        # TODO comment this out before releasing
        self.button_custom_func = QPushButton("Custom func")
        # TODO comment this out before releasing
        self.button_custom_func.clicked.connect(self.custom_func)

        # frame_setting_sca.setStyleSheet("background-color: pink;")
        self.checkbox_reserve_parsed_trees = QCheckBox(
            "Reserve parsed trees",
        )

        self.model_sca = Ng_Model()
        self.model_sca.setColumnCount(len(StructureCounter.DEFAULT_MEASURES))
        self.model_sca.setHorizontalHeaderLabels(StructureCounter.DEFAULT_MEASURES)
        self.model_sca.data_cleared.connect(lambda: self.button_generate_table_sca.setEnabled(True))
        self.model_sca.data_cleared.connect(lambda: self.button_export_table_sca.setEnabled(False))
        self.model_sca.data_cleared.connect(lambda: self.button_clear_table_sca.setEnabled(False))
        self.model_sca.data_updated.connect(lambda: self.button_export_table_sca.setEnabled(True))
        self.model_sca.data_updated.connect(lambda: self.button_clear_table_sca.setEnabled(True))
        self.model_sca.data_updated.connect(lambda: self.button_generate_table_sca.setEnabled(False))
        self.model_sca.data_updated.connect(lambda: self.resize_horizontal_header(self.tableview_preview_sca))
        self.model_sca.clear_data()
        self.tableview_preview_sca = QTableView()
        self.tableview_preview_sca.setModel(self.model_sca)
        # self.table_preview_sca.setStyleSheet("background-color: #C7C7C7;")
        self.tableview_preview_sca.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tableview_preview_sca.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )
        self.tableview_preview_sca.horizontalHeader().setHighlightSections(False)
        self.tableview_preview_sca.verticalHeader().setHighlightSections(False)
        # self.tableview_preview_sca.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.tableview_preview_sca.setSelectionBehavior(QTableView.SelectRows)

        self.checkbox_reserve_parsed_trees.setChecked(True)
        self.checkbox_reserve_matched_subtrees = QCheckBox("Reserve matched subtrees")
        self.checkbox_reserve_matched_subtrees.setChecked(True)
        widget_settings_sca = QWidget()
        widget_settings_sca.setLayout(QGridLayout())
        widget_settings_sca.layout().addWidget(self.checkbox_reserve_parsed_trees, 0, 0)
        widget_settings_sca.layout().addWidget(self.checkbox_reserve_matched_subtrees, 1, 0)

        scrollarea_settings_sca = QScrollArea()
        scrollarea_settings_sca.setLayout(QGridLayout())
        scrollarea_settings_sca.setWidgetResizable(True)
        scrollarea_settings_sca.setFixedWidth(200)
        scrollarea_settings_sca.setBackgroundRole(QPalette.Light)
        scrollarea_settings_sca.setWidget(widget_settings_sca)

        self.tab_sca = QWidget()
        self.tab_sca.setLayout(QGridLayout())
        for btn_no, btn in enumerate(
            (
                self.button_generate_table_sca,
                self.button_export_table_sca,
                self.button_clear_table_sca,
                self.button_custom_func,
            ),
            start=1,
        ):
            self.tab_sca.layout().addWidget(btn, 1, btn_no - 1)
        self.tab_sca.layout().addWidget(self.tableview_preview_sca, 0, 0, 1, btn_no)
        self.tab_sca.layout().addWidget(scrollarea_settings_sca, 0, btn_no, 2, 1)
        self.tab_sca.layout().setContentsMargins(6, 4, 6, 4)

    def custom_func(self):
        breakpoint()

    def setup_tab_lca(self):
        self.button_generate_table_lca = QPushButton("Generate table")
        self.button_generate_table_lca.clicked.connect(self.ng_thread_lca_generate_table.start)
        self.button_generate_table_lca.setShortcut("CTRL+G")
        self.button_export_table_lca = QPushButton("Export all cells...")
        self.button_export_table_lca.setEnabled(False)
        self.button_export_table_lca.clicked.connect(lambda: self.export_table(self.model_lca))
        # self.button_export_selected_cells = QPushButton("Export selected cells...")
        # self.button_export_selected_cells.setEnabled(False)
        self.button_clear_table_lca = QPushButton("Clear table")
        self.button_clear_table_lca.setEnabled(False)
        self.button_clear_table_lca.clicked.connect(lambda: self.ask_clear_model(self.model_lca, "hor"))

        self.model_lca = Ng_Model()
        self.model_lca.setColumnCount(len(LCA.FIELDNAMES) - 1)
        self.model_lca.setHorizontalHeaderLabels(LCA.FIELDNAMES[1:])
        self.model_lca.data_cleared.connect(lambda: self.button_generate_table_lca.setEnabled(True))
        self.model_lca.data_cleared.connect(lambda: self.button_export_table_lca.setEnabled(False))
        self.model_lca.data_cleared.connect(lambda: self.button_clear_table_lca.setEnabled(False))
        self.model_lca.data_updated.connect(lambda: self.button_export_table_lca.setEnabled(True))
        self.model_lca.data_updated.connect(lambda: self.button_clear_table_lca.setEnabled(True))
        self.model_lca.data_updated.connect(lambda: self.button_generate_table_lca.setEnabled(False))
        self.model_lca.data_updated.connect(lambda: self.resize_horizontal_header(self.tableview_preview_lca))
        self.model_lca.clear_data()
        self.tableview_preview_lca = QTableView()
        self.tableview_preview_lca.setModel(self.model_lca)
        self.tableview_preview_lca.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tableview_preview_lca.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )
        self.tableview_preview_lca.horizontalHeader().setHighlightSections(False)
        self.tableview_preview_lca.verticalHeader().setHighlightSections(False)
        # self.tableview_preview_lca.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.tableview_preview_lca.setSelectionBehavior(QTableView.SelectRows)

        self.radiobutton_wordlist_BNC = QRadioButton("British National Corpus (BNC) wordlist")
        self.radiobutton_wordlist_BNC.setChecked(True)
        self.radiobutton_wordlist_ANC = QRadioButton("American National Corpus (ANC) wordlist")
        groupbox_wordlist = QGroupBox("Wordlist")
        groupbox_wordlist.setLayout(QGridLayout())
        groupbox_wordlist.layout().addWidget(self.radiobutton_wordlist_BNC, 0, 0)
        groupbox_wordlist.layout().addWidget(self.radiobutton_wordlist_ANC, 1, 0)
        self.radiobutton_tagset_ud = QRadioButton("Universal POS Tagset")
        self.radiobutton_tagset_ud.setChecked(True)
        self.radiobutton_tagset_ptb = QRadioButton("Penn Treebank POS Tagset")
        groupbox_tagset = QGroupBox("Tagset")
        groupbox_tagset.setLayout(QGridLayout())
        groupbox_tagset.layout().addWidget(self.radiobutton_tagset_ud, 0, 0)
        groupbox_tagset.layout().addWidget(self.radiobutton_tagset_ptb, 1, 0)

        widget_settings_lca = QWidget()
        widget_settings_lca.setLayout(QGridLayout())
        widget_settings_lca.layout().addWidget(groupbox_wordlist, 0, 0)
        widget_settings_lca.layout().addWidget(groupbox_tagset, 1, 0)

        scrollarea_settings_lca = QScrollArea()
        scrollarea_settings_lca.setFixedWidth(200)
        scrollarea_settings_lca.setWidgetResizable(True)
        scrollarea_settings_lca.setBackgroundRole(QPalette.Light)
        scrollarea_settings_lca.setWidget(widget_settings_lca)

        self.tab_lca = QWidget()
        self.tab_lca.setLayout(QGridLayout())

        for btn_no, btn in enumerate(
            (
                self.button_generate_table_lca,
                self.button_export_table_lca,
                self.button_clear_table_lca,
            ),
            start=1,
        ):
            self.tab_lca.layout().addWidget(btn, 1, btn_no - 1)
        self.tab_lca.layout().addWidget(self.tableview_preview_lca, 0, 0, 1, btn_no)
        self.tab_lca.layout().addWidget(scrollarea_settings_lca, 0, btn_no, 2, 1)
        self.tab_lca.layout().setContentsMargins(6, 4, 6, 4)

    def enable_button_generate_table(self, enabled: bool) -> None:
        self.button_generate_table_sca.setEnabled(enabled)
        self.button_generate_table_lca.setEnabled(enabled)

    def resize_horizontal_header(self, tableview: QTableView) -> None:
        tableview.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

    def setup_tableview_file(self) -> None:
        self.model_file = Ng_Model()
        self.model_file.setHorizontalHeaderLabels(("Name", "Path"))
        self.model_file.data_cleared.connect(lambda: self.enable_button_generate_table(False))
        self.model_file.data_updated.connect(lambda: self.enable_button_generate_table(True))
        self.model_file.data_updated.connect(lambda: self.resize_horizontal_header(self.tableview_file))
        self.model_file.clear_data()
        self.tableview_file = QTableView()
        self.tableview_file.setModel(self.model_file)
        self.tableview_file.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tableview_file.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.tableview_file.horizontalHeader().setHighlightSections(False)
        self.tableview_file.verticalHeader().setHighlightSections(False)
        # self.tableview_file.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.tableview_file.setSelectionBehavior(QTableView.SelectRows)
        self.tableview_file.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        # https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QWidget.html#PySide6.QtWidgets.PySide6.QtWidgets.QWidget.customContextMenuRequested
        self.tableview_file.customContextMenuRequested.connect(self.show_menu_for_tableview_file)

    def setup_main_window(self):
        self.setup_tab_sca()
        self.setup_tab_lca()
        self.setup_tableview_file()

        self.tabwidget = QTabWidget()
        self.tabwidget.addTab(self.tab_sca, "Syntactic Complexity Analyzer")
        self.tabwidget.addTab(self.tab_lca, "Lexical Complexity Analyzer")
        self.splitter_central_widget = QSplitter(Qt.Orientation.Vertical)
        self.splitter_central_widget.setChildrenCollapsible(False)
        self.splitter_central_widget.addWidget(self.tabwidget)
        self.splitter_central_widget.setStretchFactor(0, 2)
        self.splitter_central_widget.addWidget(self.tableview_file)
        self.splitter_central_widget.setStretchFactor(1, 1)
        self.setCentralWidget(self.splitter_central_widget)

    def setup_worker(self) -> None:
        self.processing_dialog = QDialog(self)
        self.processing_dialog.setWindowTitle("Please waite.")
        self.processing_dialog.resize(300, 200)
        self.label_wait = QLabel(
            "NeoSCA is running. It may take a few minutes to finish the job. Please wait.",
            self.processing_dialog,
        )
        self.label_wait.setWordWrap(True)

        self.ng_worker_sca_generate_table = Ng_Worker_SCA_Generate_Table(self, self.processing_dialog)
        self.ng_thread_sca_generate_table = Ng_Thread(self.ng_worker_sca_generate_table)

        self.ng_worker_lca_generate_table = Ng_Worker_LCA_Generate_Table(self, self.processing_dialog)
        self.ng_thread_lca_generate_table = Ng_Thread(self.ng_worker_lca_generate_table)

    def ask_clear_model(self, model: Ng_Model, orientation: Literal["hor", "ver"] = "hor") -> None:
        if model.has_been_exported:
            model.clear_data()
        else:
            messagebox = QMessageBox()
            messagebox.setWindowTitle("Clear Table")
            messagebox.setText(
                "All the data that has not been exported will be lost. Are you sure to clear it?"
            )
            messagebox.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

            messagebox.accepted.connect(model.clear_data)
            messagebox.exec()

    def setup_env(self) -> None:
        self.desktop = os_path.normpath(os_path.expanduser("~/Desktop"))
        self.here = os_path.dirname(os_path.abspath(__file__))
        ng_home = os_path.dirname(self.here)
        libs_dir = os_path.join(ng_home, "libs")
        # TODO: remove these
        self.java_home = os_path.join(libs_dir, "jdk8u372")
        self.stanford_parser_home = os_path.join(libs_dir, "stanford-parser-full-2020-11-17")
        self.stanford_tregex_home = os_path.join(libs_dir, "stanford-tregex-2020-11-17")
        os.environ["JAVA_HOME"] = self.java_home
        os.environ["STANFORD_PARSER_HOME"] = self.stanford_parser_home
        os.environ["STANFORD_TREGEX_HOME"] = self.stanford_tregex_home
        self.env = os.environ.copy()

    def get_qss_attr(self, qss: str, selector: str, attrname: str) -> Optional[str]:
        """
        >>> qss = "QHeaderView::section:horizontal { background-color: #5C88C5; }"
        >>> get_qss_attr(qss, "QHeaderView::section:horizontal", "background-color")
        5C88C5
        """
        # Notice that only the 1st selector will be matched here
        matched_selector = re.search(selector, qss)
        if matched_selector is None:
            return None
        matched_value = re.search(rf"[^}}]+{attrname}:\s*([^;]+);", qss[matched_selector.end() :])
        if matched_value is None:
            return None
        return matched_value.group(1)

    def export_table(
        self,
        model: Ng_Model,
        has_horizontal_header: bool = True,
        has_vertical_header: bool = True,
    ) -> None:
        file_path, file_type = QFileDialog.getSaveFileName(
            parent=None,
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
                from openpyxl.styles import Alignment, Font, PatternFill
                from openpyxl.utils import get_column_letter

                workbook = openpyxl.Workbook()
                worksheet = workbook.active
                worksheet_cell = worksheet.cell

                rowno_cell_offset = 2 if has_horizontal_header else 1
                colno_cell_offset = 2 if has_vertical_header else 1

                horizontal_left_alignment = Alignment(horizontal="left")
                horizontal_center_alignment = Alignment(horizontal="center")
                horizontal_right_alignment = Alignment(horizontal="right")

                # 1. Horizontal header text
                if has_horizontal_header:
                    for colno_cell, colno_item in enumerate(range(col_count)):
                        cell = worksheet_cell(1, colno_cell_offset + colno_cell)
                        cell.value = model.horizontalHeaderItem(colno_item).text()
                        cell.alignment = horizontal_center_alignment
                # 2. Vertical header text
                if has_vertical_header:
                    for rowno_cell, rowno_item in enumerate(range(row_count)):
                        cell = worksheet_cell(rowno_cell_offset + rowno_cell, 1)
                        cell.value = model.verticalHeaderItem(rowno_item).text()
                        cell.alignment = horizontal_left_alignment

                # 3. Both header background and font
                # 3.0.1 Get header background
                horizon_bacolor: Optional[str] = self.get_qss_attr(
                    self.styleSheet(), "QHeaderView::section:horizontal", "background-color"
                )
                vertical_bacolor: Optional[str] = self.get_qss_attr(
                    self.styleSheet(), "QHeaderView::section:vertical", "background-color"
                )
                # 3.0.2 Get header font, currently only consider color and boldness
                #  https://www.codespeedy.com/change-font-color-of-excel-cells-using-openpyxl-in-python/
                #  https://doc.qt.io/qt-6/stylesheet-reference.html#font-weight
                font_color = self.get_qss_attr(self.styleSheet(), "QHeaderView::section", "color")
                font_color = font_color.lstrip("#") if font_color is not None else "000"
                font_weight = self.get_qss_attr(self.styleSheet(), "QHeaderView::section", "font-weight")
                is_bold = (font_weight == "bold") if font_weight is not None else False
                # 3.1 Horizontal header background and font
                if has_horizontal_header:
                    # 3.1.1 Horizontal header background
                    #  TODO: Currently all tabs share the same style sheet and the
                    #   single QSS file is loaded from MainWindow, thus here the
                    #   style sheet is accessed from self. In the future different
                    #   tabs might load their own QSS files, and the style sheet
                    #   should be accessed from the QTabWidget. This is also the
                    #   case for all other "self.styleSheet()" expressions, when
                    #   making this change, remember to edit all of them.
                    if horizon_bacolor is not None:
                        horizon_bacolor = horizon_bacolor.lstrip("#")
                        for colno_cell in range(col_count):
                            cell = worksheet_cell(1, colno_cell_offset + colno_cell)
                            cell.fill = PatternFill(fill_type="solid", fgColor=horizon_bacolor)
                    # 3.1.2 Horizontal header font
                    for colno_cell in range(col_count):
                        cell = worksheet_cell(1, colno_cell_offset + colno_cell)
                        cell.font = Font(color=font_color, bold=is_bold)
                # 3.2 Vertical header background and font
                if has_vertical_header:
                    # 3.2.1 Vertial header background
                    if vertical_bacolor is not None:
                        vertical_bacolor = vertical_bacolor.lstrip("#")
                        for rowno_cell in range(row_count):
                            cell = worksheet_cell(rowno_cell_offset + rowno_cell, 1)
                            cell.fill = PatternFill(fill_type="solid", fgColor=vertical_bacolor)
                    # 3.2.2 Vertical header font
                    for rowno_cell in range(row_count):
                        cell = worksheet_cell(rowno_cell_offset + rowno_cell, 1)
                        cell.font = Font(color=font_color, bold=is_bold)

                # 4. Cells
                for rowno_cell, rowno in enumerate(range(row_count)):
                    for colno_cell, colno_item in enumerate(range(col_count)):
                        cell = worksheet_cell(rowno_cell_offset + rowno_cell, colno_cell_offset + colno_cell)
                        item_value = model.item(rowno, colno_item).text()
                        try:
                            item_value = float(item_value)
                        except ValueError:
                            cell.alignment = horizontal_left_alignment
                        else:
                            cell.alignment = horizontal_right_alignment
                        cell.value = item_value
                # 5. Column width
                #  https://stackoverflow.com/questions/13197574/openpyxl-adjust-column-width-size
                #  https://stackoverflow.com/questions/60182474/auto-size-column-width
                for colno, col_cells in enumerate(worksheet.columns, start=1):
                    # https://openpyxl.readthedocs.io/en/stable/api/openpyxl.worksheet.worksheet.html#openpyxl.worksheet.worksheet.Worksheet.columns
                    valid_values = filter(lambda v: v is not None, (cell.value for cell in col_cells))
                    width = max(map(len, map(str, valid_values)))
                    worksheet.column_dimensions[get_column_letter(colno)].width = width * 1.23
                # 6. Freeze panes
                # https://stackoverflow.com/questions/73837417/freeze-panes-first-two-rows-and-column-with-openpyxl
                # Using "2" in both cases means to always freeze the 1st column
                if has_horizontal_header:
                    worksheet.freeze_panes = "B2"
                else:
                    worksheet.freeze_panes = "A2"
                workbook.save(file_path)
            elif ".csv" in file_type or ".tsv" in file_type:
                import csv

                dialect = csv.excel if ".csv" in file_type else csv.excel_tab
                with open(os_path.normpath(file_path), "w", newline="", encoding="utf-8") as fh:
                    csv_writer = csv.writer(fh, dialect=dialect, lineterminator="\n")
                    # Horizontal header
                    hor_header: List[str] = [""]
                    hor_header.extend(model.horizontalHeaderItem(colno).text() for colno in range(col_count))
                    csv_writer.writerow(hor_header)
                    # Vertical header + cells
                    for rowno in range(row_count):
                        row: List[str] = [model.verticalHeaderItem(rowno).text()]
                        row.extend(model.item(rowno, colno).text() for colno in range(col_count))
                        csv_writer.writerow(row)
            QMessageBox.information(
                self, "Success", f"The table has been successfully exported to {file_path}."
            )
        except PermissionError:
            QMessageBox.critical(
                self,
                "Error Exporting Cells",
                f"PermissionError: failed to export the table to {file_path}.",
            )
        else:
            model.data_exported.emit()

    def show_menu_for_tableview_file(self) -> None:
        action_remove_file = QAction("Remove")
        action_remove_file.triggered.connect(self.remove_file_paths)
        menu = QMenu()
        menu.addAction(action_remove_file)
        menu.exec(QCursor.pos())

    def remove_file_paths(self) -> None:
        # https://stackoverflow.com/questions/5927499/how-to-get-selected-rows-in-qtableview
        indexes: List[QModelIndex] = self.tableview_file.selectionModel().selectedRows()
        # Remove rows from bottom to top, or otherwise the lower row indexes
        #  will change as upper rows are removed
        rownos = sorted((index.row() for index in indexes), reverse=True)
        for rowno in rownos:
            self.model_file.takeRow(rowno)
        if self.model_file.rowCount() == 0:
            self.model_file.data_cleared.emit()

    def remove_model_rows(self, model: Ng_Model, *rownos: int) -> None:
        if not rownos:
            # https://doc.qt.io/qtforpython-6/PySide6/QtGui/QStandardItemModel.html#PySide6.QtGui.PySide6.QtGui.QStandardItemModel.setRowCount
            model.setRowCount(0)
        else:
            for rowno in rownos:
                model.takeRow(rowno)

    def remove_model_single_empty_row(self, model: Ng_Model) -> None:
        if model.rowCount() == 1 and model.item(0, 0) is None:
            model.setRowCount(0)

    # Type hint for generator: https://docs.python.org/3.12/library/typing.html#typing.Generator
    def yield_model_column(self, model: Ng_Model, colno: int) -> Generator[str, None, None]:
        items = (model.item(rowno, colno) for rowno in range(model.rowCount()))
        return (item.text() for item in items if item is not None)

    def yield_added_file_names(self) -> Generator[str, None, None]:
        colno_path = 0
        return self.yield_model_column(self.model_file, colno_path)

    def yield_added_file_paths(self) -> Generator[str, None, None]:
        colno_path = 1
        return self.yield_model_column(self.model_file, colno_path)

    def set_model_items_from_row_start(self, model: Ng_Model, rowno: int, *items: str) -> None:
        for colno, item in enumerate(items):
            model.setItem(rowno, colno, QStandardItem(item))

    def add_file_paths(self, file_paths_to_add: List[str]) -> None:
        unique_file_paths_to_add: Set[str] = set(file_paths_to_add)
        already_added_file_paths: Set[str] = set(self.yield_added_file_paths())
        file_paths_dup: Set[str] = unique_file_paths_to_add & already_added_file_paths
        file_paths_unsupported: Set[str] = set(
            filter(lambda p: SCAIO.suffix(p) not in SCAIO.SUPPORTED_EXTENSIONS, file_paths_to_add)
        )
        file_paths_empty: Set[str] = set(filter(lambda p: not os_path.getsize(p), unique_file_paths_to_add))
        file_paths_ok: Set[str] = (
            unique_file_paths_to_add
            - already_added_file_paths
            - file_paths_dup
            - file_paths_unsupported
            - file_paths_empty
        )
        if file_paths_ok:
            self.remove_model_single_empty_row(self.model_file)
            colno_name = 0
            already_added_file_names = list(
                self.yield_model_column(self.model_file, colno_name)
            )  # Here the already_added_file_names will have no duplicates
            for file_path in file_paths_ok:
                file_name = os_path.splitext(os_path.basename(file_path))[0]
                if file_name in already_added_file_names:
                    occurrence = 2
                    while f"{file_name} ({occurrence})" in already_added_file_names:
                        occurrence += 1
                    file_name = f"{file_name} ({occurrence})"
                already_added_file_names.append(file_name)
                self.set_model_items_from_row_start(
                    self.model_file, self.model_file.rowCount(), file_name, file_path
                )

            self.model_file.data_updated.emit()

        if file_paths_dup or file_paths_unsupported or file_paths_empty:
            model_err_files = Ng_Model()
            model_err_files.setHorizontalHeaderLabels(("Error Type", "File Path"))
            for reason, file_paths in (
                ("Duplicate file", file_paths_dup),
                ("Unsupported file type", file_paths_unsupported),
                ("Empty file", file_paths_empty),
            ):
                for file_path in file_paths:
                    model_err_files.insertRow(
                        model_err_files.rowCount(),
                        (QStandardItem(reason), QStandardItem(file_path)),
                    )
            tableview_err_files = QTableView()
            tableview_err_files.setModel(model_err_files)
            tableview_err_files.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

            dialog = Ng_Dialog_Table(
                self,
                main=self,
                title="Error Adding Files",
                text="Failed to add the following files.",
                size=(300, 200),
                tableview=tableview_err_files,
                model_has_horizontal_header=True,
                model_has_vertical_header=False,
            )
            dialog.open()

    def browse_folder(self):
        # TODO: Currently only include files of supported types, should include
        #  all files, and popup error for unsupported files
        folder_dialog = QFileDialog()
        # TODO remove default directory before releasing
        folder_path = folder_dialog.getExistingDirectory(
            caption="Open Folder",
            dir='directory="/home/tan/docx/corpus/YuHua-parallel-corpus-zh-en/02aligned/standalone/',
        )
        if not folder_path:
            return

        file_paths_to_add = []
        for extension in SCAIO.SUPPORTED_EXTENSIONS:
            file_paths_to_add.extend(glob.glob(os_path.join(folder_path, f"*.{extension}")))
        self.add_file_paths(file_paths_to_add)

    def browse_file(self):
        file_dialog = QFileDialog()
        file_paths_to_add, _ = file_dialog.getOpenFileNames(
            parent=None,
            caption="Open Files",
            dir="/home/tan/docx/corpus/YuHua-parallel-corpus-zh-en/02aligned/standalone/",
            # TODO remove this before releasing
            filter="Text files (*.txt);;Docx files (*.docx);;Odt files (*.odt);;All files (*.*)",
        )
        if not file_paths_to_add:
            return
        self.add_file_paths(file_paths_to_add)

    def restart(self):
        self.close()
        command = [sys.executable, "-m", "neosca_gui"]
        subprocess.call(command, env=os.environ.copy(), close_fds=False)


class Ng_QSS_Loader:
    def __init__(self):
        pass

    @staticmethod
    def read_qss_file(qss_file_path):
        with open(qss_file_path, encoding="utf-8") as file:
            return file.read()


if __name__ == "__main__":
    ng_app = QApplication(sys.argv)
    ng_window = Ng_Main()
    ng_window.setStyleSheet(Ng_QSS_Loader.read_qss_file(os_path.join(ng_window.here, "ng_style.qss")))
    ng_window.showMaximized()
    sys.exit(ng_app.exec())
