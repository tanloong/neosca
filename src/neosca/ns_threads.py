#!/usr/bin/env python3

from collections.abc import Generator

from PyQt5.QtCore import QObject, Qt, QThread, pyqtSignal
from PyQt5.QtGui import QStandardItem

from neosca.ns_lca.ns_lca import Ns_LCA
from neosca.ns_lca.ns_lca_counter import Ns_LCA_Counter
from neosca.ns_sca.ns_sca import Ns_SCA
from neosca.ns_sca.ns_sca_counter import Ns_SCA_Counter
from neosca.ns_settings.ns_settings import Ns_Settings
from neosca.ns_widgets.ns_tables import Ns_StandardItemModel


class Ns_Worker(QObject):
    finished = pyqtSignal()

    def __init__(self, *args, main, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.main = main

    def run(self) -> None:
        raise NotImplementedError()


class Ns_Worker_SCA_Generate_Table(Ns_Worker):
    def __init__(self, *args, main, **kwargs) -> None:
        super().__init__(*args, main=main, **kwargs)

    def run(self) -> None:
        file_names: Generator[str, None, None] = self.main.model_file.yield_file_names()
        file_paths: Generator[str | list[str], None, None] = self.main.model_file.yield_file_paths()

        init_kwargs = {
            "selected_measures": None,
            "is_cache": Ns_Settings.value("Miscellaneous/cache", type=bool),
            "is_use_cache": Ns_Settings.value("Miscellaneous/use-cache", type=bool),
            "is_skip_parsing": False,
            "is_stdout": False,
            "is_save_values": False,
            "is_save_matches": False,
            "config": None,
        }

        sca_instance = Ns_SCA(**init_kwargs)
        model: Ns_StandardItemModel = self.main.model_sca
        has_trailing_rows: bool = True
        for rowno, (file_name, file_path) in enumerate(zip(file_names, file_paths, strict=False)):
            # TODO: add handling of --no-parse, --no-query, ...
            counter: Ns_SCA_Counter = sca_instance.run_on_file_or_subfiles(file_path)

            if has_trailing_rows:
                has_trailing_rows = model.removeRows(rowno, model.rowCount() - rowno)

            model.item_left_shifted.emit((rowno, 0, file_name))
            for colno in range(1, model.columnCount()):
                sname = model.horizontalHeaderItem(colno).text()
                assert (value := counter.get_value(sname)) is not None

                item = QStandardItem()
                # https://stackoverflow.com/a/20469423/20732031
                item.setData(value, Qt.ItemDataRole.DisplayRole)
                if matches := counter.get_matches(sname):
                    item.setData(matches, Qt.ItemDataRole.UserRole)
                model.item_right_shifted.emit((rowno, colno, item))
        model.rows_added.emit()

        self.finished.emit()


class Ns_Worker_LCA_Generate_Table(Ns_Worker):
    def __init__(self, *args, main, **kwargs) -> None:
        super().__init__(*args, main=main, **kwargs)

    def run(self) -> None:
        file_names: Generator[str, None, None] = self.main.model_file.yield_file_names()
        file_paths: Generator[str, None, None] = self.main.model_file.yield_file_paths()

        init_kwargs = {
            "wordlist": Ns_Settings.value("Lexical Complexity Analyzer/wordlist"),
            "tagset": Ns_Settings.value("Lexical Complexity Analyzer/tagset"),
            "is_cache": Ns_Settings.value("Miscellaneous/cache", type=bool),
            "is_use_cache": Ns_Settings.value("Miscellaneous/use-cache", type=bool),
            "is_stdout": False,
            "is_save_values": False,
            "is_save_matches": False,
        }
        lca_instance = Ns_LCA(**init_kwargs)
        model: Ns_StandardItemModel = self.main.model_lca
        has_trailing_rows: bool = True
        for rowno, (file_name, file_path) in enumerate(zip(file_names, file_paths, strict=False)):
            counter: Ns_LCA_Counter = lca_instance.run_on_file_or_subfiles(file_path)

            if has_trailing_rows:
                has_trailing_rows = model.removeRows(rowno, model.rowCount() - rowno)

            # model.set_item_left_shifted(rowno, 0, file_name)
            model.item_left_shifted.emit((rowno, 0, file_name))
            for colno in range(1, model.columnCount()):
                item_name = model.horizontalHeaderItem(colno).text()
                value = counter.get_value(item_name)

                item = QStandardItem()
                item.setData(value, Qt.ItemDataRole.DisplayRole)
                if matches := counter.get_matches(item_name):
                    item.setData(matches, Qt.ItemDataRole.UserRole)
                model.item_right_shifted.emit((rowno, colno, item))
        model.rows_added.emit()

        self.finished.emit()


class Ns_Thread(QThread):
    err_occurs = pyqtSignal(Exception)

    def __init__(self, worker: Ns_Worker):
        super().__init__()
        self.worker = worker
        # https://mayaposch.wordpress.com/2011/11/01/how-to-really-truly-use-qthreads-the-full-explanation/
        self.worker.moveToThread(self)

        worker.finished.connect(worker.deleteLater)
        worker.destroyed.connect(self.quit)
        self.finished.connect(self.deleteLater)

    def run(self):
        try:
            self.worker.run()
        except BaseException as ex:
            self.err_occurs.emit(ex)

    # def cancel(self) -> None:
    #     self.terminate()
    #     self.wait()
