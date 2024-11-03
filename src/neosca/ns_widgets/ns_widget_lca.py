#!/usr/bin/env python3

from PyQt5.QtWidgets import QGridLayout, QMainWindow, QWidget

from ..ns_lca.ns_lca_counter import Ns_LCA_Counter
from ..ns_threads import Ns_Worker_LCA_Generate_Table, create_thread
from ..ns_utils import ns_find_main
from .ns_buttons import Ns_PushButton
from .ns_delegates import Ns_StyledItemDelegate_Matches
from .ns_sortfilterproxymodel import Ns_SortFilterProxyModel
from .ns_standarditemmodel import Ns_StandardItemModel
from .ns_tableview import Ns_TableView


class Ns_Widget_LCA(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.button_generate_table_lca = Ns_PushButton("Generate table", False)
        self.button_export_table_lca = Ns_PushButton("Export table...", False)
        self.button_export_matches_lca = Ns_PushButton("Export matches...", False)
        self.button_clear_table_lca = Ns_PushButton("Clear table", False)

        self.model_lca = Ns_StandardItemModel(self, hor_labels=("File", *Ns_LCA_Counter.DEFAULT_MEASURES))
        proxy_model_lca = Ns_SortFilterProxyModel(self, self.model_lca)
        tableview_lca = Ns_TableView(self, model=proxy_model_lca)
        tableview_lca.setItemDelegate(Ns_StyledItemDelegate_Matches(self))

        # Bind
        self.button_generate_table_lca.clicked.connect(self.on_generate_table_lca)
        self.button_export_table_lca.clicked.connect(
            lambda: tableview_lca.export_table("neosca_lca_results.xlsx")
        )
        self.button_export_matches_lca.clicked.connect(
            lambda: tableview_lca.export_matches("neosca_lca_matches.xlsx")
        )
        self.button_clear_table_lca.clicked.connect(lambda: self.model_lca.clear_data(confirm=True))
        self.model_lca.data_cleared.connect(self.on_model_lca_data_cleared)
        self.model_lca.rows_added.connect(self.on_model_lca_row_added)

        layout_lca = QGridLayout()
        self.setLayout(layout_lca)

        btn_no = 0
        for btn_no, btn in enumerate(
            (
                self.button_generate_table_lca,
                self.button_export_table_lca,
                self.button_export_matches_lca,
                self.button_clear_table_lca,
            ),
        ):
            layout_lca.addWidget(btn, 1, btn_no)
        layout_lca.addWidget(tableview_lca, 0, 0, 1, btn_no + 1)

        layout_lca.setContentsMargins(0, 0, 0, 0)

    def on_model_lca_data_cleared(self) -> None:
        self.button_export_table_lca.setEnabled(False)
        self.button_export_matches_lca.setEnabled(False)
        self.button_clear_table_lca.setEnabled(False)

    def on_model_lca_row_added(self) -> None:
        if not self.model_lca.is_empty():
            self.button_export_table_lca.setEnabled(True)
        if self.model_lca.has_user_data():
            self.button_export_matches_lca.setEnabled(True)
        self.button_clear_table_lca.setEnabled(True)

    def on_generate_table_lca(self) -> None:
        main: QMainWindow = ns_find_main(self)
        worker = Ns_Worker_LCA_Generate_Table(main=main, model=self.model_lca)
        self.thread_generate_table_lca = create_thread(main, worker)
        self.thread_generate_table_lca.start()
