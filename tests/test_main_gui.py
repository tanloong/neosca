#!/usr/bin/env python3

from unittest.mock import Mock

from neosca.ns_about import __title__
from neosca.ns_main_gui import Ns_Main_Gui

from .base_tmpl import BaseTmpl


class TestMain(BaseTmpl):
    @classmethod
    def setUpClass(cls):
        cls.gui = Ns_Main_Gui()

    def test_tabbar(self):
        self.assertEqual(self.gui.tabwidget.count(), 2)

    def test_tray(self):
        self.gui.setVisible(True)

        # Initial tray actions: Minimize to Tray, Separator, Quit
        tray_actions = self.gui.menu_tray.actions()
        self.assertEqual(tray_actions[0].text(), "Minimize to Tray")
        self.assertEqual(tray_actions[-1].text(), "Quit")

        # Attach mock
        self.hide_orig, self.bring_to_front_orig = self.gui.hide, self.gui.bring_to_front
        self.gui.hide = Mock()
        self.gui.bring_to_front = Mock()

        self.gui.action_toggle.trigger()
        self.gui.hide.assert_called_once()

        self.gui.setVisible(False)
        self.gui.menu_tray.aboutToShow.emit()
        self.assertEqual(tray_actions[0].text(), f"Show {__title__}")
        self.assertEqual(tray_actions[-1].text(), "Quit")

        self.gui.action_toggle.trigger()
        self.gui.bring_to_front.assert_called_once()

        # Detach mock
        self.gui.hide, self.gui.bring_to_front = self.hide_orig, self.bring_to_front_orig

    def test_previewarea_sca(self):
        ...
        # test how many buttons

    def test_previewarea_lca(self):
        # test how many buttons
        ...
