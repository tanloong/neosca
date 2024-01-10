#!/usr/bin/env python3

import glob
import os
import os.path as os_path
import re
import sys
from pathlib import Path
from typing import List, Set

from PySide6.QtCore import QModelIndex, Qt
from PySide6.QtGui import QAction, QCursor, QIcon, QStandardItem
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QCheckBox,
    QFileDialog,
    QGridLayout,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QSplitter,
    QSystemTrayIcon,
    QTableView,
    QTabWidget,
    QWidget,
)

from neosca import ICON_PATH, QSS_PATH
from neosca.ns_about import __title__, __version__
from neosca.ns_buttons import Ns_PushButton
from neosca.ns_io import Ns_Cache, Ns_IO
from neosca.ns_lca.ns_lca import Ns_LCA
from neosca.ns_platform_info import IS_MAC
from neosca.ns_qss import Ns_QSS
from neosca.ns_sca.structure_counter import StructureCounter
from neosca.ns_settings.ns_dialog_settings import Ns_Dialog_Settings
from neosca.ns_settings.ns_settings import Ns_Settings
from neosca.ns_settings.ns_settings_default import available_import_types
from neosca.ns_threads import Ns_Thread, Ns_Worker_LCA_Generate_Table, Ns_Worker_SCA_Generate_Table
from neosca.ns_widgets.ns_delegates import Ns_Delegate_SCA
from neosca.ns_widgets.ns_dialogs import (
    Ns_Dialog_About,
    Ns_Dialog_Processing_With_Elapsed_Time,
    Ns_Dialog_Table,
    Ns_Dialog_Table_Acknowledgments,
    Ns_Dialog_Table_Cache,
    Ns_Dialog_TextEdit_Citing,
    Ns_Dialog_TextEdit_Err,
)
from neosca.ns_widgets.ns_tables import Ns_SortFilterProxyModel, Ns_StandardItemModel, Ns_TableView
from neosca.ns_widgets.ns_widgets import Ns_MessageBox_Question


class Ns_Main_Gui(QMainWindow):
    def __init__(self, *args, with_button_pdb: bool = False, **kwargs):
        super().__init__(*args, **kwargs)
        self.with_button_pdb = with_button_pdb

        self.setWindowTitle(f"{__title__} {__version__}")
        self.setWindowIcon(QIcon(str(ICON_PATH)))
        qss = Ns_QSS.read_qss_file(QSS_PATH)
        qss += f"""\n* {{
         font-family: {Ns_Settings.value('Appearance/font-family')};
         font-size: {Ns_Settings.value('Appearance/font-size')}pt;
         }}"""
        self.setStyleSheet(qss)
        self.setup_menu()
        self.setup_worker()
        self.setup_main_window()
        self.resize_splitters()
        self.setup_tray()

        self.statusBar().setVisible(Ns_Settings.value("show-statusbar", type=bool))
        self.statusBar().showMessage("Ready!")
        self.statusBar().setFixedHeight(20)

        self.fix_macos_layout(self)

    # https://github.com/zealdocs/zeal/blob/9630cc94c155d87295e51b41fbab2bd5798f8229/src/libs/ui/mainwindow.cpp#L421C3-L433C24
    def setup_tray(self) -> None:
        menu_tray = QMenu(self)

        action_toggle = menu_tray.addAction("Minimize to Tray")
        action_toggle.triggered.connect(self.toggle_window)
        menu_tray.aboutToShow.connect(
            lambda: action_toggle.setText("Minimize to Tray" if self.isVisible() else f"Show {__title__}")
        )
        menu_tray.addSeparator()

        action_quit = menu_tray.addAction("Quit")
        action_quit.triggered.connect(self.close)

        self.trayicon = QSystemTrayIcon(QIcon(str(ICON_PATH)), self)
        self.trayicon.setContextMenu(menu_tray)
        self.trayicon.show()

    # https://github.com/zealdocs/zeal/blob/9630cc94c155d87295e51b41fbab2bd5798f8229/src/libs/ui/mainwindow.cpp#L447
    def bring_to_front(self) -> None:
        self.show()
        self.setWindowState(
            (self.windowState() & ~Qt.WindowState.WindowMinimized) | Qt.WindowState.WindowActive
        )
        self.raise_()
        self.activateWindow()

    # https://github.com/zealdocs/zeal/blob/9630cc94c155d87295e51b41fbab2bd5798f8229/src/libs/ui/mainwindow.cpp#L529
    def toggle_window(self) -> None:
        if self.isVisible():
            self.hide()
        else:
            self.bring_to_front()

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
        self.menu_file = self.menuBar().addMenu("&File")
        self.action_open_file = self.menu_file.addAction("&Open File...")
        self.action_open_file.setShortcut("CTRL+O")
        self.action_open_file.triggered.connect(self.menu_file_open_file)
        self.action_open_folder = self.menu_file.addAction("Open &Folder...")
        self.action_open_folder.triggered.connect(self.menu_file_open_folder)
        self.menu_file.addSeparator()

        self.action_clear_cache = self.menu_file.addAction("&Clear Cache...")
        self.action_clear_cache.triggered.connect(self.menu_file_clear_cache)
        self.menu_file.addSeparator()

        self.action_quit = self.menu_file.addAction("&Quit")
        self.action_quit.setShortcut("CTRL+Q")
        self.action_quit.triggered.connect(self.close)

        self.menu_file.aboutToShow.connect(self.menu_file_about_to_show)

        # Preferences
        self.menu_prefs = self.menuBar().addMenu("&Preferences")
        self.action_settings = self.menu_prefs.addAction("&Settings...")
        self.action_settings.setShortcut("CTRL+,")
        self.action_settings.triggered.connect(self.menu_prefs_settings)

        self.menu_prefs.addSeparator()
        self.action_enlarge_font = self.menu_prefs.addAction("Enlarge Font")
        self.action_enlarge_font.setShortcut("CTRL+=")
        self.action_enlarge_font.triggered.connect(self.menu_prefs_enlarge_font)
        self.action_shrink_font = self.menu_prefs.addAction("Shrink Font")
        self.action_shrink_font.setShortcut("CTRL+-")
        self.action_shrink_font.triggered.connect(self.menu_prefs_shrink_font)

        self.menu_prefs.addSeparator()
        self.action_reset_layout = self.menu_prefs.addAction("&Reset Layouts")
        self.action_reset_layout.triggered.connect(lambda: self.resize_splitters(reset=True))
        self.action_toggle_statusbar = self.menu_prefs.addAction("&Toggle Statusbar")
        self.action_toggle_statusbar.triggered.connect(self.menu_prefs_toggle_statusbar)

        # Help
        self.menu_help = self.menuBar().addMenu("&Help")
        self.action_citing = self.menu_help.addAction("&Citing")
        self.action_citing.triggered.connect(self.menu_help_citing)
        self.action_acks = self.menu_help.addAction("&Acknowledgments")
        self.action_acks.triggered.connect(self.menu_help_acks)
        self.action_about = self.menu_help.addAction("A&bout")
        self.action_about.triggered.connect(self.menu_help_about)

    def menu_file_open_folder(self):
        folder_path = QFileDialog.getExistingDirectory(
            caption="Open Folder", dir=Ns_Settings.value("Import/default-path")
        )
        if not folder_path:
            return

        file_paths_to_add = []
        for extension in Ns_IO.SUPPORTED_EXTENSIONS:
            file_paths_to_add.extend(glob.glob(os_path.join(folder_path, f"*.{extension}")))
        self.add_file_paths(file_paths_to_add)

    def menu_file_open_file(self):
        file_paths_to_add, _ = QFileDialog.getOpenFileNames(
            parent=self,
            caption="Open Files",
            dir=Ns_Settings.value("Import/default-path"),
            filter=";;".join(available_import_types),
            selectedFilter=Ns_Settings.value("Import/default-type"),
        )
        if not file_paths_to_add:
            return
        self.add_file_paths(file_paths_to_add)

    def menu_file_clear_cache(self):
        if any(Ns_Cache.yield_cname_cpath_csize_fpath()):
            Ns_Dialog_Table_Cache(self).open()
        else:
            QMessageBox.information(self, "No Caches", "There are no caches to clear.")

    def menu_file_about_to_show(self):
        if any(Ns_Cache.yield_cname_cpath_csize_fpath()):
            self.action_clear_cache.setEnabled(True)
        else:
            self.action_clear_cache.setEnabled(False)

    def menu_prefs_settings(self) -> None:
        attr = "dialog_settings"
        if hasattr(self, attr):
            getattr(self, attr).open()
        else:
            dialog_settings = Ns_Dialog_Settings(self)
            setattr(self, attr, dialog_settings)
            dialog_settings.open()

    def menu_prefs_enlarge_font(self) -> None:
        key = "Appearance/font-size"
        point_size = Ns_Settings.value(key, type=int) + 1
        if point_size < Ns_Settings.value("Appearance/font-size-max", type=int):
            Ns_QSS.update(self, {"*": {"font-size": f"{point_size}pt"}})
            Ns_Settings.setValue(key, point_size)

    def menu_prefs_shrink_font(self) -> None:
        key = "Appearance/font-size"
        point_size = Ns_Settings.value(key, type=int) - 1
        if point_size > Ns_Settings.value("Appearance/font-size-min", type=int):
            Ns_QSS.update(self, {"*": {"font-size": f"{point_size}pt"}})
            Ns_Settings.setValue(key, point_size)

    def menu_prefs_toggle_statusbar(self) -> None:
        self.statusBar().setVisible(not self.statusBar().isVisible())
        Ns_Settings.setValue("show-statusbar", self.statusBar().isVisible())

    def menu_help_citing(self) -> None:
        Ns_Dialog_TextEdit_Citing(self).open()

    def menu_help_acks(self) -> None:
        Ns_Dialog_Table_Acknowledgments(self).open()

    def menu_help_about(self) -> None:
        Ns_Dialog_About(self).open()

    def setup_tab_sca(self):
        self.button_generate_table_sca = Ns_PushButton("Generate table", False)
        self.button_export_table_sca = Ns_PushButton("Export table...", False)
        self.button_export_matches_sca = Ns_PushButton("Export matches...", False)
        self.button_clear_table_sca = Ns_PushButton("Clear table", False)

        self.button_pdb = QPushButton("Run Pdb")
        self.button_pdb.clicked.connect(self.run_pdb)

        self.model_sca = Ns_StandardItemModel(self, hor_labels=("File", *StructureCounter.DEFAULT_MEASURES))
        proxy_model_sca = Ns_SortFilterProxyModel(self, self.model_sca)
        self.tableview_sca = Ns_TableView(self, model=proxy_model_sca)
        self.tableview_sca.setItemDelegate(Ns_Delegate_SCA(None, self.styleSheet()))

        # Bind
        self.button_generate_table_sca.clicked.connect(self.ns_thread_sca_generate_table.start)
        self.button_export_table_sca.clicked.connect(
            lambda: self.tableview_sca.export_table("neosca_sca_results.xlsx")
        )
        self.button_export_matches_sca.clicked.connect(self.tableview_sca.export_matches)
        self.button_clear_table_sca.clicked.connect(lambda: self.model_sca.clear_data(confirm=True))
        self.model_sca.data_cleared.connect(self.on_model_sca_data_cleared)
        self.model_sca.row_added.connect(self.on_model_sca_row_added)

        self.widget_previewarea_sca = QWidget()
        self.layout_previewarea_sca = QGridLayout()
        self.widget_previewarea_sca.setLayout(self.layout_previewarea_sca)
        for btn_no, btn in enumerate(
            (
                self.button_generate_table_sca,
                self.button_export_table_sca,
                self.button_export_matches_sca,
                self.button_clear_table_sca,
            ),
            start=1,
        ):
            self.layout_previewarea_sca.addWidget(btn, 1, btn_no - 1)
        if self.with_button_pdb:
            self.layout_previewarea_sca.addWidget(btn, 1, btn_no - 1)
            btn_no += 1
        self.layout_previewarea_sca.addWidget(self.tableview_sca, 0, 0, 1, btn_no)
        self.layout_previewarea_sca.setContentsMargins(0, 0, 0, 0)

    def on_model_sca_data_cleared(self) -> None:
        if not self.model_file.is_empty():
            self.button_generate_table_sca.setEnabled(True)
        self.button_export_table_sca.setEnabled(False)
        self.button_export_matches_sca.setEnabled(False)
        self.button_clear_table_sca.setEnabled(False)

    def on_model_sca_row_added(self) -> None:
        if not self.model_sca.is_empty():
            self.button_export_table_sca.setEnabled(True)
        if self.model_sca.has_user_data():
            self.button_export_matches_sca.setEnabled(True)
        self.button_clear_table_sca.setEnabled(True)
        self.button_generate_table_sca.setEnabled(False)

    def run_pdb(self):
        # import gc
        # import time
        #
        # from neosca.ns_sca.structure_counter import Structure, StructureCounter
        # counters =[]
        # ss = []
        # for o in gc.get_objects():
        #     if isinstance(o, StructureCounter):
        #         counters.append(o)
        #     elif isinstance(o, Structure):
        #         ss.append(o)
        # gc.collect()
        # filename = "{}.txt".format(time.strftime("%H-%M-%S"))
        # with open(filename, "w") as f:
        #     f.write("\n".join(str(o) for o in gc.get_objects()))
        breakpoint()

    def setup_tab_lca(self):
        self.button_generate_table_lca = Ns_PushButton("Generate table", False)
        self.button_export_table_lca = Ns_PushButton("Export table...", False)
        self.button_clear_table_lca = Ns_PushButton("Clear table", False)

        self.model_lca = Ns_StandardItemModel(self, hor_labels=("File", *Ns_LCA.FIELDNAMES[1:]))
        proxy_model_lca = Ns_SortFilterProxyModel(self, self.model_lca)
        self.tableview_lca = Ns_TableView(self, model=proxy_model_lca)
        # TODO: tableview_sca use custom delegate to only enable clickable
        # items, in which case a dialog will pop up to show matches. Here when
        # tableview_lca also use custom delegate, remember to remove this line.
        # Remember that there is also setEditTriggers expression in
        # Ns_Dialog_Table_Cache.
        self.tableview_lca.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)

        # Bind
        self.button_generate_table_lca.clicked.connect(self.ns_thread_lca_generate_table.start)
        self.button_export_table_lca.clicked.connect(
            lambda: self.tableview_lca.export_table("neosca_lca_results.xlsx")
        )
        self.button_clear_table_lca.clicked.connect(lambda: self.model_lca.clear_data(confirm=True))
        self.model_lca.data_cleared.connect(self.on_model_lca_data_cleared)
        self.model_lca.row_added.connect(self.on_model_lca_row_added)

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

    def on_model_lca_data_cleared(self) -> None:
        if not self.model_file.is_empty():
            self.button_generate_table_lca.setEnabled(True)
        self.button_export_table_lca.setEnabled(False)
        self.button_clear_table_lca.setEnabled(False)

    def on_model_lca_row_added(self) -> None:
        self.button_export_table_lca.setEnabled(True)
        self.button_clear_table_lca.setEnabled(True)
        self.button_generate_table_lca.setEnabled(False)

    def resize_splitters(self, reset: bool = False) -> None:
        for splitter in (self.splitter_central_widget,):
            key = splitter.objectName()
            if not reset and Ns_Settings.contains(key):
                splitter.restoreState(Ns_Settings.value(key))
            else:
                if splitter.orientation() == Qt.Orientation.Vertical:
                    total_size = splitter.size().height()
                else:
                    total_size = splitter.size().width()
                section_size = Ns_Settings.value(f"default-{key}", type=int)
                splitter.setSizes((total_size - section_size, section_size))

    def enable_button_generate_table(self, enabled: bool) -> None:
        self.button_generate_table_sca.setEnabled(enabled)
        self.button_generate_table_lca.setEnabled(enabled)

    def setup_tableview_file(self) -> None:
        self.model_file = Ns_StandardItemModel(self, hor_labels=(("Name", "Path")))
        self.model_file.data_cleared.connect(lambda: self.enable_button_generate_table(False))
        self.model_file.row_added.connect(lambda: self.enable_button_generate_table(True))
        self.tableview_file = Ns_TableView(self, model=self.model_file)
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

        num = len(indexes)
        noun = "file" if num == 1 else "files"
        self.statusBar().showMessage(f"{num} {noun} has been removed.")

    def show_menu_for_tableview_file(self) -> None:
        if not self.tableview_file.selectionModel().selectedRows():
            self.action_tableview_file_remove.setEnabled(False)
        else:
            self.action_tableview_file_remove.setEnabled(True)
        self.menu_tableview_file.exec(QCursor.pos())

    def add_file_paths(self, file_paths_to_add: List[str]) -> None:
        unique_file_paths_to_add: Set[str] = set(file_paths_to_add)
        already_added_file_paths: Set[str] = set(self.model_file.yield_column(1))
        file_paths_dup: Set[str] = unique_file_paths_to_add & already_added_file_paths
        file_paths_unsupported: Set[str] = set(
            filter(lambda p: Ns_IO.suffix(p).lstrip(".") not in Ns_IO.SUPPORTED_EXTENSIONS, file_paths_to_add)
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
            self.model_file.remove_empty_rows()
            colno_name = 0
            # Has no duplicates
            already_added_file_stems = list(self.model_file.yield_column(colno_name))
            for file_path in file_paths_ok:
                file_stem = Path(file_path).stem
                file_stem = Ns_IO.ensure_unique_filestem(file_stem, already_added_file_stems)
                already_added_file_stems.append(file_stem)
                rowno = self.model_file.rowCount()
                self.model_file.set_row_left_shifted(rowno, (file_stem, file_path))
                self.model_file.row_added.emit()

            num = len(file_paths_ok)
            noun = "file" if num == 1 else "files"
            self.statusBar().showMessage(f"{num} {noun} has been added.")

        if file_paths_dup or file_paths_unsupported or file_paths_empty:
            model_err_files = Ns_StandardItemModel(
                self, hor_labels=("Error Type", "File Path"), show_empty_row=False
            )
            for reason, file_paths in (
                ("Duplicate file", file_paths_dup),
                ("Unsupported file type", file_paths_unsupported),
                ("Empty file", file_paths_empty),
            ):
                for file_path in file_paths:
                    model_err_files.appendRow((QStandardItem(reason), QStandardItem(file_path)))
            tableview_err_files = Ns_TableView(self, model=model_err_files)

            dialog = Ns_Dialog_Table(
                self,
                title="Error Adding Files",
                text="Failed to add the following files.",
                tableview=tableview_err_files,
                export_filename="neosca_error_files.xlsx",
            )
            dialog.open()

    def setup_main_window(self):
        self.setup_tab_sca()
        self.setup_tab_lca()
        self.setup_tableview_file()

        self.tabwidget = QTabWidget()
        self.tabwidget.addTab(self.widget_previewarea_sca, "Syntactic Complexity Analyzer")
        self.tabwidget.addTab(self.widget_previewarea_lca, "Lexical Complexity Analyzer")
        self.splitter_central_widget = QSplitter(Qt.Orientation.Vertical)
        self.splitter_central_widget.setChildrenCollapsible(False)
        self.splitter_central_widget.addWidget(self.tabwidget)
        self.splitter_central_widget.addWidget(self.tableview_file)
        self.splitter_central_widget.setStretchFactor(0, 1)
        self.splitter_central_widget.setObjectName("splitter-file")
        self.setCentralWidget(self.splitter_central_widget)

    def setup_worker(self) -> None:
        self.dialog_processing = Ns_Dialog_Processing_With_Elapsed_Time(self)

        self.ns_worker_sca_generate_table = Ns_Worker_SCA_Generate_Table(main=self)
        self.ns_thread_sca_generate_table = Ns_Thread(self.ns_worker_sca_generate_table)
        self.ns_thread_sca_generate_table.started.connect(self.dialog_processing.open)
        self.ns_thread_sca_generate_table.finished.connect(self.dialog_processing.accept)
        self.ns_thread_sca_generate_table.err_occurs.connect(
            lambda ex: Ns_Dialog_TextEdit_Err(self, ex=ex).open()
        )

        self.ns_worker_lca_generate_table = Ns_Worker_LCA_Generate_Table(main=self)
        self.ns_thread_lca_generate_table = Ns_Thread(self.ns_worker_lca_generate_table)
        self.ns_thread_lca_generate_table.started.connect(self.dialog_processing.open)
        self.ns_thread_lca_generate_table.finished.connect(self.dialog_processing.accept)
        self.ns_thread_lca_generate_table.err_occurs.connect(
            lambda ex: Ns_Dialog_TextEdit_Err(self, ex=ex).open()
        )

    # Override
    def close(self) -> bool:
        key = "Miscellaneous/dont-confirm-on-exit"
        if not Ns_Settings.value(key, type=bool) and any(
            (not model.is_empty() and not model.has_been_exported) for model in (self.model_sca, self.model_lca)
        ):
            checkbox_exit = QCheckBox("Don't confirm on exit")
            checkbox_exit.stateChanged.connect(lambda: Ns_Settings.setValue(key, checkbox_exit.isChecked()))
            messagebox = Ns_MessageBox_Question(
                self,
                f"Quit {__title__}",
                "<b>All unsaved data will be lost.</b> Do you really want to exit?",
                QMessageBox.Icon.Warning,
                checkbox_exit,
            )
            if not messagebox.exec():
                return False

        for splitter in (self.splitter_central_widget,):
            Ns_Settings.setValue(splitter.objectName(), splitter.saveState())
        Ns_Settings.sync()
        Ns_Cache.save_cache_info()

        return super().close()


def main_gui():
    ui_scaling = Ns_Settings.value("Appearance/scaling")
    # https://github.com/BLKSerene/Wordless/blob/main/wordless/wl_main.py#L1238
    os.environ["QT_SCALE_FACTOR"] = re.sub(r"([0-9]{2})%$", r".\1", ui_scaling)
    ns_app = QApplication(sys.argv)
    ns_window = Ns_Main_Gui(with_button_pdb=False)
    ns_window.showMaximized()
    sys.exit(ns_app.exec())


if __name__ == "__main__":
    main_gui()
