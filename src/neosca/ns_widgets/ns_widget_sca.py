#!/usr/bin/env python3

from PyQt5.QtWidgets import QGridLayout, QMainWindow, QWidget

from ..ns_sca.ns_sca_counter import Ns_SCA_Counter
from ..ns_threads import Ns_Worker_SCA_Generate_Table, create_thread
from ..ns_utils import ns_find_main
from .ns_buttons import Ns_PushButton
from .ns_delegates import Ns_StyledItemDelegate_Matches
from .ns_sortfilterproxymodel import Ns_SortFilterProxyModel
from .ns_standarditemmodel import Ns_StandardItemModel
from .ns_tableview import Ns_TableView


class Ns_Widget_SCA(QWidget):
    def __init__(self, parent=None, *, with_button_pdb: bool = False):
        super().__init__(parent)

        self.button_generate_table_sca = Ns_PushButton("Generate table", False)
        self.button_export_table_sca = Ns_PushButton("Export table...", False)
        self.button_export_matches_sca = Ns_PushButton("Export matches...", False)
        self.button_clear_table_sca = Ns_PushButton("Clear table", False)

        self.model_sca = Ns_StandardItemModel(self, hor_labels=("File", *Ns_SCA_Counter.DEFAULT_MEASURES))
        proxy_model_sca = Ns_SortFilterProxyModel(self, self.model_sca)
        tableview_sca = Ns_TableView(self, model=proxy_model_sca)
        tableview_sca.setItemDelegate(Ns_StyledItemDelegate_Matches(self))

        # Bind
        self.button_generate_table_sca.clicked.connect(self.on_generate_table_sca)
        self.button_export_table_sca.clicked.connect(
            lambda: tableview_sca.export_table("neosca_sca_results.xlsx")
        )
        self.button_export_matches_sca.clicked.connect(
            lambda: tableview_sca.export_matches("neosca_sca_matches.xlsx")
        )
        self.button_clear_table_sca.clicked.connect(lambda: self.model_sca.clear_data(confirm=True))
        self.model_sca.data_cleared.connect(self.on_model_sca_data_cleared)
        self.model_sca.rows_added.connect(self.on_model_sca_row_added)

        layout_sca = QGridLayout()
        self.setLayout(layout_sca)

        btn_no = 0
        for btn_no, btn in enumerate(
            (
                self.button_generate_table_sca,
                self.button_export_table_sca,
                self.button_export_matches_sca,
                self.button_clear_table_sca,
            ),
        ):
            layout_sca.addWidget(btn, 1, btn_no)
        if with_button_pdb:
            button_pdb = Ns_PushButton("Run Pdb")
            button_pdb.clicked.connect(self.run_pdb)
            btn_no += 1
            layout_sca.addWidget(button_pdb, 1, btn_no)
        layout_sca.addWidget(tableview_sca, 0, 0, 1, btn_no + 1)

        layout_sca.setContentsMargins(0, 0, 0, 0)

    def on_model_sca_data_cleared(self) -> None:
        self.button_export_table_sca.setEnabled(False)
        self.button_export_matches_sca.setEnabled(False)
        self.button_clear_table_sca.setEnabled(False)

    def on_model_sca_row_added(self) -> None:
        if not self.model_sca.is_empty():
            self.button_export_table_sca.setEnabled(True)
        if self.model_sca.has_user_data():
            self.button_export_matches_sca.setEnabled(True)
        self.button_clear_table_sca.setEnabled(True)

    def run_pdb(self):
        # import gc
        # import time
        #
        # from .ns_sca.ns_sca_counter import Structure, StructureCounter
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

    def on_generate_table_sca(self) -> None:
        main: QMainWindow = ns_find_main(self)
        worker = Ns_Worker_SCA_Generate_Table(main=main, model=self.model_sca)
        self.thread_generate_table_sca = create_thread(main, worker)
        self.thread_generate_table_sca.start()
