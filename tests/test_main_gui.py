#!/usr/bin/env python3

import os.path as os_path
from itertools import product
from unittest.mock import Mock, patch

from neosca import ns_main_gui
from neosca.ns_about import __title__
from neosca.ns_io import Ns_IO
from PyQt5.QtWidgets import QFileDialog

from .base_tmpl import BaseTmpl, temp_files


class TestMain(BaseTmpl):
    @classmethod
    def setUpClass(cls):
        cls.gui = ns_main_gui.Ns_Main_Gui()

    def test_tabbar(self):
        self.assertEqual(self.gui.tabwidget.count(), 2)

    def test_tray(self):
        self.gui.setVisible(True)

        # Initial tray actions: Minimize to Tray, Separator, Quit
        tray_actions = self.gui.menu_tray.actions()
        self.assertEqual(tray_actions[0].text(), "Minimize to Tray")
        self.assertEqual(tray_actions[-1].text(), "Quit")

        # Attach mock
        hide_orig, bring_to_front_orig = self.gui.hide, ns_main_gui.bring_to_front

        self.gui.hide = Mock()
        ns_main_gui.bring_to_front = Mock()

        self.gui.action_toggle.trigger()
        self.gui.hide.assert_called_once()

        self.gui.setVisible(False)
        self.gui.menu_tray.aboutToShow.emit()
        self.assertEqual(tray_actions[0].text(), f"Show {__title__}")
        self.assertEqual(tray_actions[-1].text(), "Quit")

        self.gui.action_toggle.trigger()
        ns_main_gui.bring_to_front.assert_called_once()

        # Detach mock
        self.gui.hide, ns_main_gui.bring_to_front = hide_orig, bring_to_front_orig

    def test_previewarea_sca(self):
        ...
        # test how many buttons

    def test_previewarea_lca(self):
        # test how many buttons
        ...

    def test_menu_file_open_folder(self):
        affixes: tuple[tuple[str, str], ...] = tuple(
            product(("", *Ns_IO.HIDDEN_PREFIXES), map(lambda s: f".{s}", Ns_IO.SUPPORTED_EXTENSIONS))
        )
        with (
            temp_files(affixes) as temp_dir,
            patch.object(QFileDialog, "getExistingDirectory", return_value=temp_dir.name) as _,
            patch.object(self.gui.table_file, "add_file_paths", return_value=None) as mock_add_file_paths,
        ):
            self.gui.menu_files_open_folder()
            file_paths = mock_add_file_paths.call_args.args[0]
        # Test hidden files are excluded
        self.assertTrue(all(not os_path.basename(p).startswith(Ns_IO.HIDDEN_PREFIXES) for p in file_paths))
        self.assertTrue(file_paths)
