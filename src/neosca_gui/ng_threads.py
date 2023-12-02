#!/usr/bin/env python3

from typing import Generator, List, Optional

from PySide6.QtCore import QObject, QThread, Signal
from PySide6.QtGui import QStandardItem
from PySide6.QtWidgets import QMessageBox

from neosca_gui.neosca.lca.lca import LCA
from neosca_gui.neosca.neosca import NeoSCA
from neosca_gui.neosca.structure_counter import StructureCounter
from neosca_gui.ng_widgets.ng_tables import Ng_StandardItemModel


class Ng_Worker(QObject):
    worker_done = Signal()

    def __init__(self, *args, main, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.main = main

    def run(self) -> None:
        raise NotImplementedError()


class Ng_Worker_SCA_Generate_Table(Ng_Worker):
    counter_ready = Signal(StructureCounter, str, int)

    def __init__(self, *args, main, **kwargs) -> None:
        super().__init__(*args, main=main, **kwargs)

    def run(self) -> None:
        input_file_names: Generator[str, None, None] = self.main.yield_added_file_names()
        input_file_paths: Generator[str, None, None] = self.main.yield_added_file_paths()

        sca_kwargs = {
            "is_auto_save": False,
            "odir_matched": "",
            "selected_measures": None,
            "is_reserve_parsed": self.main.checkbox_cache_sca.isChecked(),
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
        for rowno, (file_name, file_path) in enumerate(zip(input_file_names, input_file_paths)):
            try:
                counter: Optional[StructureCounter] = sca_analyzer.parse_and_query_ifile(file_path)
                # TODO should concern --no-parse, --no-query, ... after adding all available options
            except:
                err_file_paths.append(file_path)
                rowno -= 1
                continue
            if counter is None:
                err_file_paths.append(file_path)
                rowno -= 1
                continue
            self.counter_ready.emit(counter, file_name, rowno)

        if err_file_paths:  # TODO: should show a table
            QMessageBox.information(
                None,
                "Error Processing Files",
                "These files are skipped:\n- {}".format("\n- ".join(err_file_paths)),
            )
        self.worker_done.emit()


class Ng_Worker_LCA_Generate_Table(Ng_Worker):
    def __init__(self, *args, main, **kwargs) -> None:
        super().__init__(*args, main=main, **kwargs)

    def run(self) -> None:
        input_file_names: Generator[str, None, None] = self.main.yield_added_file_names()
        input_file_paths: Generator[str, None, None] = self.main.yield_added_file_paths()

        lca_kwargs = {
            "wordlist": "bnc" if self.main.radiobutton_wordlist_BNC.isChecked() else "anc",
            "tagset": "ud" if self.main.radiobutton_tagset_ud.isChecked() else "ptb",
            "is_stdout": False,
            "is_cache": self.main.checkbox_cache_lca.isChecked(),
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
        model: Ng_StandardItemModel = self.main.model_lca
        has_trailing_rows: bool = True
        for rowno, (file_name, file_path) in enumerate(zip(input_file_names, input_file_paths)):
            try:
                values = lca_analyzer._analyze(file_path=file_path)
            except:
                err_file_paths.append(file_path)
                rowno -= 1
                continue
            if values is None:  # TODO: should pop up warning window
                err_file_paths.append(file_path)
                rowno -= 1
                continue
            if has_trailing_rows:
                has_trailing_rows = model.removeRows(rowno, model.rowCount() - rowno)
            # Drop file_path
            del values[0]
            model.set_row_num(rowno, values)
            model.setVerticalHeaderItem(rowno, QStandardItem(file_name))
            model.data_updated.emit()

        if err_file_paths:  # TODO: should show a table
            QMessageBox.information(
                None,
                "Error Processing Files",
                "These files are skipped:\n- {}".format("\n- ".join(err_file_paths)),
            )

        self.worker_done.emit()


class Ng_Thread(QThread):
    def __init__(self, worker: Ng_Worker):
        super().__init__()
        self.worker = worker
        # https://mayaposch.wordpress.com/2011/11/01/how-to-really-truly-use-qthreads-the-full-explanation/
        self.worker.moveToThread(self)

    def run(self):
        self.start()
        self.worker.run()

    # def cancel(self) -> None:
    #     self.terminate()
    #     self.wait()
