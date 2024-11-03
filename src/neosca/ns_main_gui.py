#!/usr/bin/env python3

import os
import re
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCloseEvent, QIcon
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QFileDialog,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QSplitter,
    QSystemTrayIcon,
    QTabWidget,
    QWidget,
)

from .ns_about import __title__, __version__
from .ns_consts import ICON_PATH, QSS_PATH
from .ns_io import Ns_Cache, Ns_IO
from .ns_platform_info import IS_MAC
from .ns_qss import Ns_QSS
from .ns_settings.ns_dialog_settings import Ns_Dialog_Settings
from .ns_settings.ns_settings import Ns_Settings
from .ns_settings.ns_settings_default import DEFAULT_FONT_SIZE, available_import_types
from .ns_utils import bring_to_front, pt2px
from .ns_widgets.ns_dialogs import (
    Ns_Dialog_About,
    Ns_Dialog_Table_Acknowledgments,
    Ns_Dialog_Table_Cache,
    Ns_Dialog_TextEdit_Citing,
)
from .ns_widgets.ns_table_file import Ns_Table_File
from .ns_widgets.ns_widget_lca import Ns_Widget_LCA
from .ns_widgets.ns_widget_sca import Ns_Widget_SCA
from .ns_widgets.ns_widgets import Ns_MessageBox_Question


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
        self.setup_main_window()
        self.restore_splitters(use_default=False)
        self.setup_tray()
        self.fix_macos_layout(self)
        self.setup_statusbar()

    def setup_statusbar(self) -> None:
        height_pt = Ns_Settings.value("Appearance/font-size", type=int)
        height_px = int(pt2px(height_pt, offset=2))
        self.statusBar().setFixedHeight(height_px)

        self.statusBar().setVisible(Ns_Settings.value("show-statusbar", type=bool))
        self.statusBar().showMessage("Ready!")

    # https://github.com/zealdocs/zeal/blob/9630cc94c155d87295e51b41fbab2bd5798f8229/src/libs/ui/mainwindow.cpp#L421C3-L433C24
    def setup_tray(self) -> None:
        self.menu_tray = QMenu(self)

        self.action_toggle = self.menu_tray.addAction("Minimize to Tray")
        self.action_toggle.triggered.connect(self.toggle_window)
        self.menu_tray.aboutToShow.connect(
            lambda: self.action_toggle.setText("Minimize to Tray" if self.isVisible() else f"Show {__title__}")
        )
        self.menu_tray.addSeparator()

        self.action_quit = self.menu_tray.addAction("Quit")
        self.action_quit.triggered.connect(self.close)

        self.trayicon = QSystemTrayIcon(QIcon(str(ICON_PATH)), self)
        self.trayicon.setContextMenu(self.menu_tray)
        self.trayicon.setToolTip(__title__)
        self.trayicon.activated.connect(self.on_tray_activated)
        self.trayicon.show()

    def on_tray_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason != QSystemTrayIcon.ActivationReason.Trigger:
            return
        self.toggle_window()

    # https://github.com/zealdocs/zeal/blob/9630cc94c155d87295e51b41fbab2bd5798f8229/src/libs/ui/mainwindow.cpp#L529
    def toggle_window(self) -> None:
        if self.isVisible():
            self.hide()
        else:
            bring_to_front(self)

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
        # Files
        self.menu_file = self.menuBar().addMenu("&File")
        self.action_open_file = self.menu_file.addAction("&Open Files...")
        self.action_open_file.setShortcut("CTRL+O")
        self.action_open_file.triggered.connect(self.menu_files_open_file)
        self.action_open_folder = self.menu_file.addAction("Open &Folder...")
        self.action_open_folder.triggered.connect(self.menu_files_open_folder)
        self.menu_file.addSeparator()

        self.action_clear_cache = self.menu_file.addAction("&Clear Cache...")
        self.action_clear_cache.triggered.connect(self.menu_files_clear_cache)
        self.menu_file.addSeparator()

        self.action_minimize = self.menu_file.addAction("&Minimize to Tray")
        self.action_minimize.setShortcut("CTRL+M")
        self.action_minimize.triggered.connect(self.toggle_window)
        self.action_quit = self.menu_file.addAction("&Quit")
        self.action_quit.setShortcut("CTRL+Q")
        self.action_quit.triggered.connect(self.close)

        self.menu_file.aboutToShow.connect(self.menu_files_about_to_show)

        # Preferences
        self.menu_prefs = self.menuBar().addMenu("&Preferences")
        self.action_settings = self.menu_prefs.addAction("&Settings")
        self.action_settings.setShortcut("CTRL+,")
        self.action_settings.triggered.connect(self.menu_prefs_settings)

        self.menu_prefs.addSeparator()
        self.action_enlarge_font = self.menu_prefs.addAction("Enlarge Font")
        self.action_enlarge_font.setShortcut("CTRL+=")
        self.action_enlarge_font.triggered.connect(self.menu_prefs_enlarge_font)
        self.action_shrink_font = self.menu_prefs.addAction("Shrink Font")
        self.action_shrink_font.setShortcut("CTRL+-")
        self.action_shrink_font.triggered.connect(self.menu_prefs_shrink_font)
        self.action_default_font_size = self.menu_prefs.addAction("Default size")
        self.action_default_font_size.triggered.connect(self.menu_prefs_default_font_size)

        self.menu_prefs.addSeparator()
        self.action_reset_layout = self.menu_prefs.addAction("&Reset Layout")
        self.action_reset_layout.triggered.connect(self.menu_prefs_reset_layout)
        self.action_toggle_status_bar = self.menu_prefs.addAction("Show S&tatus Bar")
        self.action_toggle_status_bar.setCheckable(True)
        self.action_toggle_status_bar.setChecked(Ns_Settings.value("show-statusbar", type=bool))
        self.statusBar().setVisible(Ns_Settings.value("show-statusbar", type=bool))
        self.action_toggle_status_bar.triggered.connect(self.menu_prefs_toggle_status_bar)

        # Help
        self.menu_help = self.menuBar().addMenu("&Help")
        self.action_citing = self.menu_help.addAction("&Citing")
        self.action_citing.triggered.connect(self.menu_help_citing)
        self.action_acks = self.menu_help.addAction("&Acknowledgments")
        self.action_acks.triggered.connect(self.menu_help_acks)
        self.action_about = self.menu_help.addAction("A&bout")
        self.action_about.triggered.connect(self.menu_help_about)

    def menu_files_open_folder(self):
        folder_path = QFileDialog.getExistingDirectory(
            parent=self, caption="Open Folder", directory=Ns_Settings.value("Import/default-path")
        )
        if not folder_path:
            return

        is_recursive = Ns_Settings.value("Import/include-files-in-subfolders", type=bool)
        file_paths = Ns_IO.find_files(folder_path, is_recursive)
        self.table_file.add_file_paths(file_paths)

    def menu_files_open_file(self):
        file_paths, _ = QFileDialog.getOpenFileNames(
            parent=self,
            caption="Open Files",
            directory=Ns_Settings.value("Import/default-path"),
            filter=";;".join(available_import_types),
            initialFilter=Ns_Settings.value("Import/default-type"),
        )
        if not file_paths:
            return
        self.table_file.add_file_paths(file_paths)

    def menu_files_clear_cache(self):
        if any(Ns_Cache.yield_cname_cpath_csize_fpath()):
            Ns_Dialog_Table_Cache(self).open()
        else:
            QMessageBox.information(self, "No Caches", "There are no caches to clear.")

    def menu_files_about_to_show(self):
        if any(Ns_Cache.yield_cname_cpath_csize_fpath()):
            self.action_clear_cache.setEnabled(True)
        else:
            self.action_clear_cache.setEnabled(False)

    def menu_prefs_settings(self) -> None:
        Ns_Dialog_Settings(self).open()

    def menu_prefs_enlarge_font(self) -> None:
        key = "Appearance/font-size"
        point_size = Ns_Settings.value(key, type=int) + 1
        max_size = Ns_Settings.value("Appearance/font-size-max", type=int)
        if point_size <= max_size:
            Ns_QSS.update(self, {"*": {"font-size": f"{point_size}pt"}})
            Ns_Settings.setValue(key, point_size)
            self.statusBar().setFixedHeight(int(pt2px(point_size, offset=2)))
            self.statusBar().showMessage(f"Enlarged font to {point_size}pt")
        else:
            self.statusBar().showMessage(f"Reached maximum font size ({max_size}pt)")

    def menu_prefs_shrink_font(self) -> None:
        key = "Appearance/font-size"
        point_size = Ns_Settings.value(key, type=int) - 1
        min_size = Ns_Settings.value("Appearance/font-size-min", type=int)
        if point_size >= min_size:
            Ns_QSS.update(self, {"*": {"font-size": f"{point_size}pt"}})
            Ns_Settings.setValue(key, point_size)
            self.statusBar().setFixedHeight(int(pt2px(point_size, offset=2)))
            self.statusBar().showMessage(f"Shrunk font to {point_size}pt")
        else:
            self.statusBar().showMessage(f"Reached minimum font size ({min_size}pt)")

    def menu_prefs_default_font_size(self) -> None:
        key = "Appearance/font-size"
        curr_size = Ns_Settings.value(key, type=int)
        if curr_size != DEFAULT_FONT_SIZE:
            Ns_QSS.update(self, {"*": {"font-size": f"{DEFAULT_FONT_SIZE}pt"}})
            Ns_Settings.setValue(key, DEFAULT_FONT_SIZE)
            self.statusBar().setFixedHeight(int(pt2px(DEFAULT_FONT_SIZE, offset=2)))
            self.statusBar().showMessage(f"Reset font size to {DEFAULT_FONT_SIZE}pt")
        else:
            self.statusBar().showMessage(f"Already default font size ({DEFAULT_FONT_SIZE}pt)")

    def menu_prefs_toggle_status_bar(self, checked: bool) -> None:
        self.statusBar().setVisible(checked)
        Ns_Settings.setValue("show-statusbar", checked)

    def menu_help_citing(self) -> None:
        Ns_Dialog_TextEdit_Citing(self).open()

    def menu_help_acks(self) -> None:
        Ns_Dialog_Table_Acknowledgments(self).open()

    def menu_help_about(self) -> None:
        Ns_Dialog_About(self).open()

    def restore_splitters(self, use_default: bool) -> None:
        for splitter in (self.splitter_central_widget,):
            key = splitter.objectName()
            if not use_default and Ns_Settings.contains(key):
                splitter.restoreState(Ns_Settings.value(key))
            else:
                if splitter.orientation() == Qt.Orientation.Vertical:
                    total_size = splitter.size().height()
                else:
                    total_size = splitter.size().width()
                section_size = Ns_Settings.value(f"default-{key}", type=int)
                splitter.setSizes((total_size - section_size, section_size))

    def menu_prefs_reset_layout(self) -> None:
        self.restore_splitters(use_default=True)
        self.statusBar().showMessage("Layout reset")

    def enable_button_generate_table(self, enabled: bool) -> None:
        self.widget_sca.button_generate_table_sca.setEnabled(enabled)
        self.widget_lca.button_generate_table_lca.setEnabled(enabled)

    def setup_main_window(self):
        self.widget_sca = Ns_Widget_SCA(with_button_pdb=self.with_button_pdb)
        self.widget_lca = Ns_Widget_LCA()
        self.table_file = Ns_Table_File(self)

        self.tabwidget = QTabWidget()
        self.tabwidget.addTab(self.widget_sca, "Syntactic Complexity Analyzer")
        self.tabwidget.addTab(self.widget_lca, "Lexical Complexity Analyzer")
        self.splitter_central_widget: QSplitter = QSplitter(Qt.Orientation.Vertical)
        self.splitter_central_widget.setChildrenCollapsible(False)
        self.splitter_central_widget.addWidget(self.tabwidget)
        self.splitter_central_widget.addWidget(self.table_file)
        self.splitter_central_widget.setStretchFactor(0, 1)
        self.splitter_central_widget.setObjectName("splitter-file")
        self.setCentralWidget(self.splitter_central_widget)

    # Override
    def closeEvent(self, event: QCloseEvent) -> None:
        key = "Miscellaneous/dont-warn-on-exit"
        if not Ns_Settings.value(key, type=bool):
            checkbox_exit = QCheckBox("Don't warn on exit")
            checkbox_exit.stateChanged.connect(lambda: Ns_Settings.setValue(key, checkbox_exit.isChecked()))
            messagebox = Ns_MessageBox_Question(
                self,
                f"Quit {__title__}",
                "<b>All unsaved data will be lost.</b> Do you really want to exit?",
                QMessageBox.Icon.Warning,
                checkbox_exit,
            )
            if messagebox.exec() == QMessageBox.StandardButton.No:
                return event.ignore()

        for splitter in (self.splitter_central_widget,):
            Ns_Settings.setValue(splitter.objectName(), splitter.saveState())
        Ns_Settings.sync()
        Ns_Cache.save_cache_info()

        return super().closeEvent(event)


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
