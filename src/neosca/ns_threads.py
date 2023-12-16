#!/usr/bin/env python3

from typing import Generator, List, Optional

from PySide6.QtCore import QObject, QThread, Signal
from PySide6.QtGui import QStandardItem
from PySide6.QtWidgets import QMessageBox

from neosca.ns_lca.lca import LCA
from neosca.ns_sca.neosca import NeoSCA
from neosca.ns_sca.structure_counter import StructureCounter
from neosca.ns_settings.ns_settings import Ns_Settings
from neosca.ns_widgets.ns_tables import Ns_StandardItemModel


class Ns_Worker(QObject):
    worker_done = Signal()

    def __init__(self, *args, main, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.main = main

    def run(self) -> None:
        raise NotImplementedError()


class Ns_Worker_SCA_Generate_Table(Ns_Worker):
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
            "is_reserve_parsed": Ns_Settings.value("Miscellaneous/cache-for-future-runs", type=bool),
            "is_use_past_parsed": Ns_Settings.value("Miscellaneous/use-past-cache", type=bool),
            "is_skip_querying": False,
            "is_skip_parsing": False,
            "config": None,
        }

        attrname = "sca_instance"
        try:
            sca_instance = getattr(self.main, attrname)
        except AttributeError:
            sca_instance = NeoSCA(**sca_kwargs)
            setattr(self.main, attrname, sca_instance)
        else:
            sca_instance.update_options(sca_kwargs)

        for rowno, (file_name, file_path) in enumerate(zip(input_file_names, input_file_paths)):
            try:
                counter: Optional[StructureCounter] = sca_instance.parse_and_query_ifile(file_path)
                # TODO should concern --no-parse, --no-query, ... after adding all available options
            except Exception as ex:
                raise ex
            else:
                assert counter is not None, "SCA StructureCounter is None"

            self.counter_ready.emit(counter, file_name, rowno)
        self.worker_done.emit()


class Ns_Worker_LCA_Generate_Table(Ns_Worker):
    def __init__(self, *args, main, **kwargs) -> None:
        super().__init__(*args, main=main, **kwargs)

    def run(self) -> None:
        input_file_names: Generator[str, None, None] = self.main.yield_added_file_names()
        input_file_paths: Generator[str, None, None] = self.main.yield_added_file_paths()

        lca_kwargs = {
            "wordlist": Ns_Settings.value("Lexical Complexity Analyzer/wordlist"),
            "tagset": Ns_Settings.value("Lexical Complexity Analyzer/tagset"),
            "is_stdout": False,
            "is_cache_for_future_runs": Ns_Settings.value("Miscellaneous/cache-for-future-runs", type=bool),
            "is_use_past_cache": Ns_Settings.value("Miscellaneous/use-past-cache", type=bool),
        }
        attrname = "lca_instance"
        try:
            lca_instance = getattr(self.main, attrname)
        except AttributeError:
            lca_instance = LCA(**lca_kwargs)
            setattr(self.main, attrname, lca_instance)
        else:
            lca_instance.update_options(lca_kwargs)

        model: Ns_StandardItemModel = self.main.model_lca
        has_trailing_rows: bool = True
        for rowno, (file_name, file_path) in enumerate(zip(input_file_names, input_file_paths)):
            try:
                values = lca_instance._analyze(file_path=file_path)
            except Exception as ex:
                raise ex
            else:
                assert values is not None, "LCA result is None"

            if has_trailing_rows:
                has_trailing_rows = model.removeRows(rowno, model.rowCount() - rowno)
            # Drop file_path
            del values[0]
            model.set_row_num(rowno, values)
            model.setVerticalHeaderItem(rowno, QStandardItem(file_name))
            model.data_updated.emit()

        self.worker_done.emit()


class Ns_Thread(QThread):
    err_occurs = Signal(Exception)

    def __init__(self, worker: Ns_Worker):
        super().__init__()
        self.worker = worker
        # https://mayaposch.wordpress.com/2011/11/01/how-to-really-truly-use-qthreads-the-full-explanation/
        self.worker.moveToThread(self)

    def run(self):
        self.start()
        try:
            self.worker.run()
        except Exception as ex:
            self.err_occurs.emit(ex)

    # def cancel(self) -> None:
    #     self.terminate()
    #     self.wait()