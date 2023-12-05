#!/usr/bin/env python3

import glob
import os
import os.path as os_path
import re
import subprocess
import sys
from typing import Generator, List, Set

from PySide6.QtCore import QModelIndex, Qt
from PySide6.QtGui import QAction, QCursor, QStandardItem
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QCheckBox,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QMainWindow,
    QMenu,
    QPushButton,
    QRadioButton,
    QSizePolicy,
    QSpacerItem,
    QSplitter,
    QTableView,
    QTabWidget,
    QWidget,
)

from neosca_gui import QSS_PATH
from neosca_gui.ng_sca.structure_counter import StructureCounter
from neosca_gui.ng_about import __title__, __version__
from neosca_gui.ng_io import SCAIO
from neosca_gui.ng_lca.lca import LCA
from neosca_gui.ng_platform_info import IS_MAC
from neosca_gui.ng_qss import Ng_QSS
from neosca_gui.ng_settings.ng_dialog_settings import Ng_Dialog_Settings
from neosca_gui.ng_settings.ng_settings import Ng_Settings
from neosca_gui.ng_settings.ng_settings_default import available_import_types
from neosca_gui.ng_threads import Ng_Thread, Ng_Worker_LCA_Generate_Table, Ng_Worker_SCA_Generate_Table
from neosca_gui.ng_widgets.ng_dialogs import (
    Ng_Dialog_Processing_With_Elapsed_Time,
    Ng_Dialog_Table,
    Ng_Dialog_TextEdit_Citing,
)
from neosca_gui.ng_widgets.ng_tables import Ng_Delegate_SCA, Ng_StandardItemModel, Ng_TableView
from neosca_gui.ng_widgets.ng_widgets import Ng_ScrollArea


class Ng_Main(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle(f"{__title__} {__version__}")
        qss = Ng_QSS.read_qss_file(QSS_PATH)
        qss += f"""\n* {{
         font-family: {Ng_Settings.value('Appearance/font-family')};
         font-size: {Ng_Settings.value('Appearance/font-size')}pt;
         }}"""
        self.setStyleSheet(qss)
        self.setup_menu()
        self.setup_worker()
        self.setup_main_window()
        self.resize_splitters()
        self.fix_macos_layout(self)

    # https://github.com/BLKSerene/Wordless/blob/fa743bcc2a366ec7a625edc4ed6cfc355b7cd22e/wordless/wl_main.py#L266
    def fix_macos_layout(self, parent):
        if not IS_MAC:
            return

        for widget in parent.children():
            if widget.children():
                self.fix_macos_layout(widget)
            else:
                if isinstance(widget, QWidget) and not isinstance(widget, QPushButton):
                    widget.setAttribute(Qt.WidgetAttribute.WA_LayoutUsesWidgetRect)

    def setup_menu(self):
        # File
        self.menu_file = QMenu("File", self.menuBar())
        action_open_file = QAction("Open File...", self.menu_file)
        action_open_file.setShortcut("CTRL+O")
        action_open_file.triggered.connect(self.menubar_file_open_file)
        action_open_folder = QAction("Open Folder...", self.menu_file)
        action_open_folder.setShortcut("CTRL+F")
        action_open_folder.triggered.connect(self.menubar_file_open_folder)
        action_restart = QAction("Restart", self.menu_file)  # TODO remove this before releasing
        action_restart.triggered.connect(self.menubar_file_restart)  # TODO remove this before releasing
        action_restart.setShortcut("CTRL+R")  # TODO remove this before releasing
        action_quit = QAction("Exit", self.menu_file)
        action_quit.setShortcut("CTRL+Q")
        action_quit.triggered.connect(self.close)
        self.menu_file.addAction(action_open_file)
        self.menu_file.addAction(action_open_folder)
        self.menu_file.addSeparator()
        self.menu_file.addAction(action_restart)
        self.menu_file.addAction(action_quit)
        # Edit
        self.menu_edit = QMenu("Edit", self.menuBar())
        action_preferences = QAction("Preferences", self.menu_edit)
        # TODO: remove this before releasing
        action_preferences.setShortcut("CTRL+,")
        action_preferences.triggered.connect(self.menubar_edit_preferences)
        action_increase_font_size = QAction("Increase Font Size", self.menu_edit)
        action_increase_font_size.setShortcut("CTRL+=")
        action_increase_font_size.triggered.connect(self.menubar_edit_increase_font_size)
        action_decrease_font_size = QAction("Decrease Font Size", self.menu_edit)
        action_decrease_font_size.setShortcut("CTRL+-")
        action_decrease_font_size.triggered.connect(self.menubar_edit_decrease_font_size)
        action_reset_layout = QAction("Reset Layouts", self.menu_edit)
        action_reset_layout.triggered.connect(lambda: self.resize_splitters(is_reset=True))
        self.menu_edit.addAction(action_preferences)
        self.menu_edit.addAction(action_increase_font_size)
        self.menu_edit.addAction(action_decrease_font_size)
        self.menu_edit.addAction(action_reset_layout)
        # Help
        self.menu_help = QMenu("Help", self.menuBar())
        action_citing = QAction("Citing", self.menu_help)
        action_citing.triggered.connect(self.menubar_help_citing)
        self.menu_help.addAction(action_citing)

        self.menuBar().addMenu(self.menu_file)
        self.menuBar().addMenu(self.menu_edit)
        self.menuBar().addMenu(self.menu_help)

    # Override
    def close(self) -> None:
        if any(
            (not model.is_empty() and not model.has_been_exported)
            for model in (
                self.model_sca,
                self.model_lca,
            )
        ):
            messagebox = Ng_MessageBox_Confirm(
                self, "Exit NeoSCA", "<b>All unsaved data will be lost.</b> Continue?", QMessageBox.Icon.Warning
            )
            if not messagebox.exec():
                return

        Ng_Settings.setValue(self.splitter_workarea_sca.objectName(), self.splitter_workarea_sca.saveState())
        Ng_Settings.setValue(self.splitter_workarea_lca.objectName(), self.splitter_workarea_lca.saveState())
        Ng_Settings.setValue(
            self.splitter_central_widget.objectName(), self.splitter_central_widget.saveState()
        )
        Ng_Settings.sync()

        super().close()

    def menubar_edit_preferences(self) -> None:
        attr = "dialog_settings"
        if hasattr(self, attr):
            getattr(self, attr).exec()
        else:
            dialog_settings = Ng_Dialog_Settings(self)
            setattr(self, attr, dialog_settings)
            dialog_settings.exec()

    def menubar_edit_increase_font_size(self) -> None:
        key = "Appearance/font-size"
        point_size = Ng_Settings.value(key, type=int) + 1
        if point_size < Ng_Settings.value("Appearance/font-size-max", type=int):
            Ng_QSS.set_value(self, {"*": {"font-size": f"{point_size}pt"}})
            Ng_Settings.setValue(key, point_size)

    def menubar_edit_decrease_font_size(self) -> None:
        key = "Appearance/font-size"
        point_size = Ng_Settings.value(key, type=int) - 1
        if point_size > Ng_Settings.value("Appearance/font-size-min", type=int):
            Ng_QSS.set_value(self, {"*": {"font-size": f"{point_size}pt"}})
            Ng_Settings.setValue(key, point_size)

    # TODO: def menubar_edit_reset_font_size(self) -> None:

    def menubar_help_citing(self) -> None:
        dialog_citing = Ng_Dialog_TextEdit_Citing(self)
        dialog_citing.exec()

    def setup_tab_sca(self):
        self.button_generate_table_sca = QPushButton("Generate table")
        self.button_generate_table_sca.setShortcut("CTRL+G")
        self.button_export_table_sca = QPushButton("Export table...")
        self.button_export_table_sca.setEnabled(False)
        # self.button_export_selected_cells = QPushButton("Export selected cells...")
        # self.button_export_selected_cells.setEnabled(False)
        self.button_export_matches_sca = QPushButton("Export matches...")
        self.button_export_matches_sca.setEnabled(False)
        self.button_clear_table_sca = QPushButton("Clear table")
        self.button_clear_table_sca.setEnabled(False)

        # TODO comment this out before releasing
        self.button_custom_func = QPushButton("Custom func")
        # TODO comment this out before releasing
        self.button_custom_func.clicked.connect(self.custom_func)

        self.model_sca = Ng_StandardItemModel(main=self)
        self.model_sca.setColumnCount(len(StructureCounter.DEFAULT_MEASURES))
        self.model_sca.setHorizontalHeaderLabels(StructureCounter.DEFAULT_MEASURES)
        self.model_sca.clear_data()
        self.tableview_sca = Ng_TableView(main=self, model=self.model_sca)
        self.tableview_sca.setItemDelegate(Ng_Delegate_SCA(None, self.styleSheet()))

        # Bind
        self.button_generate_table_sca.clicked.connect(self.ng_thread_sca_generate_table.start)
        self.button_export_table_sca.clicked.connect(
            lambda: self.tableview_sca.export_table("neosca_sca_results.xlsx")
        )
        self.button_export_matches_sca.clicked.connect(self.tableview_sca.export_matches)
        self.button_clear_table_sca.clicked.connect(lambda: self.model_sca.clear_data(confirm=True))
        self.model_sca.data_cleared.connect(
            lambda: self.button_generate_table_sca.setEnabled(True) if not self.model_file.is_empty() else None
        )
        self.model_sca.data_cleared.connect(lambda: self.button_export_table_sca.setEnabled(False))
        self.model_sca.data_cleared.connect(lambda: self.button_export_matches_sca.setEnabled(False))
        self.model_sca.data_cleared.connect(lambda: self.button_clear_table_sca.setEnabled(False))
        self.model_sca.data_updated.connect(lambda: self.button_export_table_sca.setEnabled(True))
        self.model_sca.data_updated.connect(lambda: self.button_export_matches_sca.setEnabled(True))
        self.model_sca.data_updated.connect(lambda: self.button_clear_table_sca.setEnabled(True))
        self.model_sca.data_updated.connect(lambda: self.button_generate_table_sca.setEnabled(False))

        # Setting area
        self.checkbox_cache_sca = QCheckBox("Cache")
        self.checkbox_cache_sca.setChecked(True)

        widget_settings_sca = QWidget()
        layout_settings_sca = QGridLayout()
        widget_settings_sca.setLayout(layout_settings_sca)
        layout_settings_sca.addWidget(self.checkbox_cache_sca, 0, 0)
        layout_settings_sca.addItem(QSpacerItem(0, 0, vData=QSizePolicy.Policy.Expanding))
        layout_settings_sca.setContentsMargins(6, 0, 6, 0)

        self.scrollarea_settings_sca = Ng_ScrollArea()
        self.scrollarea_settings_sca.setWidget(widget_settings_sca)

        self.widget_previewarea_sca = QWidget()
        self.layout_previewarea_sca = QGridLayout()
        self.widget_previewarea_sca.setLayout(self.layout_previewarea_sca)
        for btn_no, btn in enumerate(
            (
                self.button_generate_table_sca,
                self.button_export_table_sca,
                self.button_export_matches_sca,
                self.button_clear_table_sca,
                self.button_custom_func,
            ),
            start=1,
        ):
            self.layout_previewarea_sca.addWidget(btn, 1, btn_no - 1)
        self.layout_previewarea_sca.addWidget(self.tableview_sca, 0, 0, 1, btn_no)
        self.layout_previewarea_sca.addWidget(self.scrollarea_settings_sca, 0, btn_no, 2, 1)
        self.layout_previewarea_sca.setContentsMargins(0, 0, 0, 0)

        self.splitter_workarea_sca = QSplitter(Qt.Orientation.Horizontal)
        self.splitter_workarea_sca.addWidget(self.widget_previewarea_sca)
        self.splitter_workarea_sca.addWidget(self.scrollarea_settings_sca)
        self.splitter_workarea_sca.setStretchFactor(0, 1)
        self.splitter_workarea_sca.setContentsMargins(6, 4, 6, 4)
        self.splitter_workarea_sca.setObjectName("splitter-sca")

    def custom_func(self):
        breakpoint()

    def setup_tab_lca(self):
        self.button_generate_table_lca = QPushButton("Generate table")
        self.button_generate_table_lca.setShortcut("CTRL+G")
        self.button_export_table_lca = QPushButton("Export table...")
        self.button_export_table_lca.setEnabled(False)
        # self.button_export_selected_cells = QPushButton("Export selected cells...")
        # self.button_export_selected_cells.setEnabled(False)
        self.button_clear_table_lca = QPushButton("Clear table")
        self.button_clear_table_lca.setEnabled(False)

        self.model_lca = Ng_StandardItemModel(main=self)
        self.model_lca.setColumnCount(len(LCA.FIELDNAMES) - 1)
        self.model_lca.setHorizontalHeaderLabels(LCA.FIELDNAMES[1:])
        self.model_lca.clear_data()
        self.tableview_lca = Ng_TableView(main=self, model=self.model_lca)
        # TODO: tableview_sca use custom delegate to only enable
        # clickable items, in which case a dialog will pop up to show matches.
        # Here when tableview_lca also use custom delegate, remember to
        # remove this line.
        self.tableview_lca.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        # Bind
        self.button_generate_table_lca.clicked.connect(self.ng_thread_lca_generate_table.start)
        self.button_export_table_lca.clicked.connect(
            lambda: self.tableview_lca.export_table("neosca_lca_results.xlsx")
        )
        self.button_clear_table_lca.clicked.connect(lambda: self.model_lca.clear_data(confirm=True))
        self.model_lca.data_cleared.connect(
            lambda: self.button_generate_table_lca.setEnabled(True) if not self.model_file.is_empty() else None
        )
        self.model_lca.data_cleared.connect(lambda: self.button_export_table_lca.setEnabled(False))
        self.model_lca.data_cleared.connect(lambda: self.button_clear_table_lca.setEnabled(False))
        self.model_lca.data_updated.connect(lambda: self.button_export_table_lca.setEnabled(True))
        self.model_lca.data_updated.connect(lambda: self.button_clear_table_lca.setEnabled(True))
        self.model_lca.data_updated.connect(lambda: self.button_generate_table_lca.setEnabled(False))

        # Setting area
        self.radiobutton_wordlist_BNC = QRadioButton("British National Corpus (BNC) wordlist")
        self.radiobutton_wordlist_BNC.setChecked(True)
        self.radiobutton_wordlist_ANC = QRadioButton("American National Corpus (ANC) wordlist")
        groupbox_wordlist = QGroupBox("Wordlist")
        layout_wordlist = QGridLayout()
        groupbox_wordlist.setLayout(layout_wordlist)
        layout_wordlist.addWidget(self.radiobutton_wordlist_BNC, 0, 0)
        layout_wordlist.addWidget(self.radiobutton_wordlist_ANC, 1, 0)
        self.radiobutton_tagset_ud = QRadioButton("Universal POS Tagset")
        self.radiobutton_tagset_ud.setChecked(True)
        self.radiobutton_tagset_ptb = QRadioButton("Penn Treebank POS Tagset")
        groupbox_tagset = QGroupBox("Tagset")
        layout_tagset = QGridLayout()
        groupbox_tagset.setLayout(layout_tagset)
        layout_tagset.addWidget(self.radiobutton_tagset_ud, 0, 0)
        layout_tagset.addWidget(self.radiobutton_tagset_ptb, 1, 0)
        self.checkbox_cache_lca = QCheckBox("Cache")
        self.checkbox_cache_lca.setChecked(True)

        widget_settings_lca = QWidget()
        layout_settings_lca = QGridLayout()
        widget_settings_lca.setLayout(layout_settings_lca)
        layout_settings_lca.addWidget(groupbox_wordlist, 0, 0)
        layout_settings_lca.addWidget(groupbox_tagset, 1, 0)
        layout_settings_lca.addWidget(self.checkbox_cache_lca, 2, 0)
        layout_settings_lca.addItem(QSpacerItem(0, 0, vData=QSizePolicy.Policy.Expanding))
        layout_settings_lca.setContentsMargins(6, 0, 6, 0)

        self.scrollarea_settings_lca = Ng_ScrollArea()
        self.scrollarea_settings_lca.setWidget(widget_settings_lca)

        self.widget_previewarea_lca = QWidget()
        self.layout_previewarea_lca = QGridLayout()
        self.widget_previewarea_lca.setLayout(self.layout_previewarea_lca)
        for btn_no, btn in enumerate(
            (
                self.button_generate_table_lca,
                self.button_export_table_lca,
                self.button_clear_table_lca,
            ),
            start=1,
        ):
            self.layout_previewarea_lca.addWidget(btn, 1, btn_no - 1)
        self.layout_previewarea_lca.addWidget(self.tableview_lca, 0, 0, 1, btn_no)
        self.layout_previewarea_lca.setContentsMargins(0, 0, 0, 0)

        self.splitter_workarea_lca = QSplitter(Qt.Orientation.Horizontal)
        self.splitter_workarea_lca.addWidget(self.widget_previewarea_lca)
        self.splitter_workarea_lca.addWidget(self.scrollarea_settings_lca)
        self.splitter_workarea_lca.setStretchFactor(0, 1)
        self.splitter_workarea_lca.setContentsMargins(6, 4, 6, 4)
        self.splitter_workarea_lca.setObjectName("splitter-lca")

    def resize_splitters(self, is_reset: bool = False) -> None:
        for splitter in (
            self.splitter_workarea_sca,
            self.splitter_workarea_lca,
            self.splitter_central_widget,
        ):
            key = splitter.objectName()
            if not is_reset and Ng_Settings.contains(key):
                splitter.restoreState(Ng_Settings.value(key))
            else:
                if splitter.orientation() == Qt.Orientation.Vertical:
                    total_size = splitter.size().height()
                else:
                    total_size = splitter.size().width()
                section_size = Ng_Settings.value(f"default-{key}", type=int)
                splitter.setSizes((total_size - section_size, section_size))

    def enable_button_generate_table(self, enabled: bool) -> None:
        self.button_generate_table_sca.setEnabled(enabled)
        self.button_generate_table_lca.setEnabled(enabled)

    def setup_tableview_file(self) -> None:
        self.model_file = Ng_StandardItemModel(main=self)
        self.model_file.setHorizontalHeaderLabels(("Name", "Path"))
        self.model_file.data_cleared.connect(lambda: self.enable_button_generate_table(False))
        self.model_file.data_updated.connect(lambda: self.enable_button_generate_table(True))
        self.model_file.clear_data()
        self.tableview_file = Ng_TableView(main=self, model=self.model_file, has_vertical_header=False)
        self.tableview_file.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tableview_file.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.tableview_file.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tableview_file.setCornerButtonEnabled(True)
        # https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QWidget.html#PySide6.QtWidgets.PySide6.QtWidgets.QWidget.customContextMenuRequested
        self.menu_tableview_file = QMenu(self)
        self.action_tableview_file_remove = QAction("Remove", self.menu_tableview_file)
        self.action_tableview_file_remove.triggered.connect(self.remove_file_paths)
        self.menu_tableview_file.addAction(self.action_tableview_file_remove)
        self.tableview_file.customContextMenuRequested.connect(self.show_menu_for_tableview_file)

    def setup_main_window(self):
        self.setup_tab_sca()
        self.setup_tab_lca()
        self.setup_tableview_file()

        self.tabwidget = QTabWidget()
        self.tabwidget.addTab(self.splitter_workarea_sca, "Syntactic Complexity Analyzer")
        self.tabwidget.addTab(self.splitter_workarea_lca, "Lexical Complexity Analyzer")
        self.splitter_central_widget = QSplitter(Qt.Orientation.Vertical)
        self.splitter_central_widget.setChildrenCollapsible(False)
        self.splitter_central_widget.addWidget(self.tabwidget)
        self.splitter_central_widget.addWidget(self.tableview_file)
        self.splitter_central_widget.setStretchFactor(0, 1)
        self.splitter_central_widget.setObjectName("splitter-file")
        self.setCentralWidget(self.splitter_central_widget)

    def sca_add_data(self, counter: StructureCounter, file_name: str, rowno: int) -> None:
        # Remove trailing rows
        self.model_sca.removeRows(rowno, self.model_sca.rowCount() - rowno)
        for colno in range(self.model_sca.columnCount()):
            sname = self.model_sca.horizontalHeaderItem(colno).text()

            value = counter.get_value(sname)
            value_str: str = str(value) if value is not None else ""
            item = QStandardItem(value_str)
            self.model_sca.set_item_num(rowno, colno, item)

            if matches := counter.get_matches(sname):
                item.setData(matches, Qt.ItemDataRole.UserRole)

        self.model_sca.setVerticalHeaderItem(rowno, QStandardItem(file_name))
        self.model_sca.data_updated.emit()

    def setup_worker(self) -> None:
        self.dialog_processing = Ng_Dialog_Processing_With_Elapsed_Time(self)

        self.ng_worker_sca_generate_table = Ng_Worker_SCA_Generate_Table(main=self)
        self.ng_worker_sca_generate_table.counter_ready.connect(self.sca_add_data)
        self.ng_thread_sca_generate_table = Ng_Thread(self.ng_worker_sca_generate_table)
        self.ng_thread_sca_generate_table.started.connect(self.dialog_processing.exec)
        self.ng_thread_sca_generate_table.finished.connect(self.dialog_processing.accept)

        self.ng_worker_lca_generate_table = Ng_Worker_LCA_Generate_Table(main=self)
        self.ng_thread_lca_generate_table = Ng_Thread(self.ng_worker_lca_generate_table)
        self.ng_thread_lca_generate_table.started.connect(self.dialog_processing.exec)
        self.ng_thread_lca_generate_table.finished.connect(self.dialog_processing.accept)

    def show_menu_for_tableview_file(self) -> None:
        if not self.tableview_file.selectionModel().selectedRows():
            self.action_tableview_file_remove.setEnabled(False)
        else:
            self.action_tableview_file_remove.setEnabled(True)
        self.menu_tableview_file.exec(QCursor.pos())

    def remove_file_paths(self) -> None:
        # https://stackoverflow.com/questions/5927499/how-to-get-selected-rows-in-qtableview
        indexes: List[QModelIndex] = self.tableview_file.selectionModel().selectedRows()
        # Remove rows from bottom to top, or otherwise lower row indexes will
        # change as upper rows are removed
        rownos = sorted((index.row() for index in indexes), reverse=True)
        for rowno in rownos:
            self.model_file.takeRow(rowno)
        if self.model_file.rowCount() == 0:
            self.model_file.clear_data()

    def remove_model_rows(self, model: Ng_StandardItemModel, *rownos: int) -> None:
        if not rownos:
            # https://doc.qt.io/qtforpython-6/PySide6/QtGui/QStandardItemModel.html#PySide6.QtGui.PySide6.QtGui.QStandardItemModel.setRowCount
            model.setRowCount(0)
        else:
            for rowno in rownos:
                model.takeRow(rowno)

    # Type hint for generator: https://docs.python.org/3.12/library/typing.html#typing.Generator
    def yield_model_column(self, model: Ng_StandardItemModel, colno: int) -> Generator[str, None, None]:
        items = (model.item(rowno, colno) for rowno in range(model.rowCount()))
        return (item.text() for item in items if item is not None)

    def yield_added_file_names(self) -> Generator[str, None, None]:
        colno_path = 0
        return self.yield_model_column(self.model_file, colno_path)

    def yield_added_file_paths(self) -> Generator[str, None, None]:
        colno_path = 1
        return self.yield_model_column(self.model_file, colno_path)

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
            self.model_file.remove_single_empty_row()
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
                rowno = self.model_file.rowCount()
                self.model_file.set_row_str(rowno, (file_name, file_path))
                self.model_file.data_updated.emit()

        if file_paths_dup or file_paths_unsupported or file_paths_empty:
            model_err_files = Ng_StandardItemModel(main=self)
            model_err_files.setHorizontalHeaderLabels(("Error Type", "File Path"))
            for reason, file_paths in (
                ("Duplicate file", file_paths_dup),
                ("Unsupported file type", file_paths_unsupported),
                ("Empty file", file_paths_empty),
            ):
                for file_path in file_paths:
                    model_err_files.appendRow((QStandardItem(reason), QStandardItem(file_path)))
            tableview_err_files = Ng_TableView(main=self, model=model_err_files, has_vertical_header=False)

            dialog = Ng_Dialog_Table(
                self,
                title="Error Adding Files",
                text="Failed to add the following files.",
                width=300,
                height=200,
                resizable=True,
                tableview=tableview_err_files,
                export_filename="neosca_error_files.xlsx",
            )
            dialog.exec()

    def menubar_file_open_folder(self):
        # TODO remove default directory before releasing
        folder_path = QFileDialog.getExistingDirectory(
            caption="Open Folder", dir=Ng_Settings.value("Import/default-path")
        )
        if not folder_path:
            return

        file_paths_to_add = []
        for extension in SCAIO.SUPPORTED_EXTENSIONS:
            file_paths_to_add.extend(glob.glob(os_path.join(folder_path, f"*.{extension}")))
        self.add_file_paths(file_paths_to_add)

    def menubar_file_open_file(self):
        file_paths_to_add, _ = QFileDialog.getOpenFileNames(
            parent=None,
            caption="Open Files",
            # TODO: remove this before releasing
            dir="/home/tan/docx/corpus/YuHua-parallel-corpus-zh-en/02aligned/standalone/",
            filter=";;".join(available_import_types),
            selectedFilter=Ng_Settings.value("Import/default-type"),
        )
        if not file_paths_to_add:
            return
        self.add_file_paths(file_paths_to_add)

    def menubar_file_restart(self):
        self.close()
        command = [sys.executable, "-m", "neosca_gui"]
        subprocess.call(command, env=os.environ.copy(), close_fds=False)


def main():
    ui_scaling = Ng_Settings.value("Appearance/interface-scaling")
    # https://github.com/BLKSerene/Wordless/blob/main/wordless/wl_main.py#L1238
    os.environ["QT_SCALE_FACTOR"] = re.sub(r"([0-9]{2})%$", r".\1", ui_scaling)
    ng_app = QApplication(sys.argv)
    ng_window = Ng_Main()
    ng_window.showMaximized()
    sys.exit(ng_app.exec())
