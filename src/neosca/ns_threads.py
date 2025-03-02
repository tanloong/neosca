#!/usr/bin/env python3

from collections.abc import Generator

from PyQt5.QtCore import QObject, Qt, QThread, pyqtSignal
from PyQt5.QtGui import QStandardItem
from PyQt5.QtWidgets import QMainWindow

from .ns_lca.ns_lca import NsLCA
from .ns_lca.ns_lca_counter import NsLCACounter
from .ns_sca.ns_sca import NsSCA
from .ns_sca.ns_sca_counter import NsSCACounter
from .ns_settings.ns_settings import NsSettings
from .ns_widgets.ns_dialogs import NsDialogProcessingWithElapsedTime, NsDialogTextEditErr
from .ns_widgets.ns_standarditemmodel import NsStandardItemModel


class NsWorker(QObject):
    finished = pyqtSignal()

    def __init__(self, *args, main, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.main = main

    def run(self) -> None:
        raise NotImplementedError()


class NsWorkerSCAGenerateTable(NsWorker):
    def __init__(self, *args, main, model: NsStandardItemModel, **kwargs) -> None:
        super().__init__(*args, main=main, **kwargs)
        self.model = model

    def run(self) -> None:
        file_names: Generator[str, None, None] = self.main.table_file.yield_file_names()
        file_paths: Generator[str | list[str], None, None] = self.main.table_file.yield_file_paths()

        init_kwargs = {
            "selected_measures": None,
            "is_cache": NsSettings.value("Miscellaneous/cache", type=bool),
            "is_use_cache": NsSettings.value("Miscellaneous/use-cache", type=bool),
            "is_skip_parsing": False,
            "is_stdout": False,
            "is_save_values": False,
            "is_save_matches": False,
            "config": None,
        }

        sca_instance = NsSCA(**init_kwargs)
        has_trailing_rows: bool = True
        for rowno, (file_name, file_path) in enumerate(zip(file_names, file_paths, strict=False)):
            # TODO: add handling of --no-parse, --no-query, ...
            counter: NsSCACounter = sca_instance.run_on_file_or_subfiles(file_path)

            if has_trailing_rows:
                has_trailing_rows = self.model.removeRows(rowno, self.model.rowCount() - rowno)

            self.model.item_left_shifted.emit((rowno, 0, file_name))
            for colno in range(1, self.model.columnCount()):
                sname = self.model.horizontalHeaderItem(colno).text()
                value = counter.get_value(sname)
                assert value is not None

                item = QStandardItem()
                # https://stackoverflow.com/a/20469423/20732031
                item.setData(value, Qt.ItemDataRole.DisplayRole)
                if matches := counter.get_matches(sname):
                    item.setData(matches, Qt.ItemDataRole.UserRole)
                self.model.item_right_shifted.emit((rowno, colno, item))
        self.model.rows_added.emit()

        self.finished.emit()


class NsWorkerLCAGenerateTable(NsWorker):
    def __init__(self, *args, main, model: NsStandardItemModel, **kwargs) -> None:
        super().__init__(*args, main=main, **kwargs)
        self.model = model

    def run(self) -> None:
        file_names: Generator[str, None, None] = self.main.table_file.yield_file_names()
        file_paths: Generator[str, None, None] = self.main.table_file.yield_file_paths()

        init_kwargs = {
            "wordlist": NsSettings.value("Lexical Complexity Analyzer/wordlist"),
            "tagset": NsSettings.value("Lexical Complexity Analyzer/tagset"),
            "is_cache": NsSettings.value("Miscellaneous/cache", type=bool),
            "is_use_cache": NsSettings.value("Miscellaneous/use-cache", type=bool),
            "is_stdout": False,
            "is_save_values": False,
            "is_save_matches": False,
        }
        lca_instance = NsLCA(**init_kwargs)
        has_trailing_rows: bool = True
        for rowno, (file_name, file_path) in enumerate(zip(file_names, file_paths, strict=False)):
            counter: NsLCACounter = lca_instance.run_on_file_or_subfiles(file_path)

            if has_trailing_rows:
                has_trailing_rows = self.model.removeRows(rowno, self.model.rowCount() - rowno)

            # self.model.set_item_left_shifted(rowno, 0, file_name)
            self.model.item_left_shifted.emit((rowno, 0, file_name))
            for colno in range(1, self.model.columnCount()):
                item_name = self.model.horizontalHeaderItem(colno).text()
                value = counter.get_value(item_name)

                item = QStandardItem()
                item.setData(value, Qt.ItemDataRole.DisplayRole)
                if matches := counter.get_matches(item_name):
                    item.setData(matches, Qt.ItemDataRole.UserRole)
                self.model.item_right_shifted.emit((rowno, colno, item))
        self.model.rows_added.emit()

        self.finished.emit()


class NsThread(QThread):
    err_occurs = pyqtSignal(Exception)

    def __init__(self, worker: NsWorker):
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


def create_thread(main: QMainWindow, worker: NsWorker) -> NsThread:
    dialog = NsDialogProcessingWithElapsedTime(main)

    thread = NsThread(worker)
    thread.started.connect(dialog.open)
    thread.finished.connect(dialog.accept)
    thread.err_occurs.connect(lambda ex: NsDialogTextEditErr(main, ex=ex).open())

    return thread
