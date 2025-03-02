#!/usr/bin/env python3

from PyQt5.QtWidgets import QGridLayout, QMainWindow, QWidget

from ..ns_lca.ns_lca_counter import NsLCACounter
from ..ns_threads import NsWorkerLCAGenerateTable, create_thread
from ..ns_utils import ns_find_main
from .ns_buttons import NsPushButton
from .ns_delegates import NsStyledItemDelegateMatches
from .ns_sortfilterproxymodel import NsSortFilterProxyModel
from .ns_standarditemmodel import NsStandardItemModel
from .ns_tableview import NsTableview


class NsWidgetLCA(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.button_generate_table_lca = NsPushButton("Generate table", False)
        self.button_export_table_lca = NsPushButton("Export table...", False)
        self.button_export_matches_lca = NsPushButton("Export matches...", False)
        self.button_clear_table_lca = NsPushButton("Clear table", False)

        self.model_lca = NsStandardItemModel(self, hor_labels=("File", *NsLCACounter.DEFAULT_MEASURES))
        proxy_model_lca = NsSortFilterProxyModel(self, self.model_lca)
        tableview_lca = NsTableview(self, model=proxy_model_lca)
        tableview_lca.setItemDelegate(NsStyledItemDelegateMatches(self))

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
        worker = NsWorkerLCAGenerateTable(main=main, model=self.model_lca)
        self.thread_generate_table_lca = create_thread(main, worker)
        self.thread_generate_table_lca.start()
