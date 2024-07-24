#!/usr/bin/env python3

import os.path as os_path
from collections.abc import Generator
from pathlib import Path

from PyQt5.QtCore import QItemSelection, QItemSelectionModel, QModelIndex, Qt
from PyQt5.QtGui import QCursor, QDragEnterEvent, QDropEvent, QStandardItem
from PyQt5.QtWidgets import QAbstractItemView, QMenu, QTableView

from neosca.ns_io import Ns_IO
from neosca.ns_settings.ns_settings import Ns_Settings
from neosca.ns_widgets.ns_delegates import Ns_StyledItemDelegate_File
from neosca.ns_widgets.ns_dialogs import Ns_Dialog_Table, Ns_Dialog_Table_Subfiles
from neosca.ns_widgets.ns_standarditemmodel import Ns_StandardItemModel
from neosca.ns_widgets.ns_standarditemmodel_file import Ns_StandardItemModel_File
from neosca.ns_widgets.ns_tableview import Ns_TableView


class Ns_Table_File(Ns_TableView):
    def __init__(self, main):
        self._model = Ns_StandardItemModel_File(main)
        super().__init__(main, self._model, disable_on_empty=False)

        self.setItemDelegate(Ns_StyledItemDelegate_File(self))
        self.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.setCornerButtonEnabled(True)

        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.DropOnly)

        # https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QWidget.html#PySide6.QtWidgets.PySide6.QtWidgets.QWidget.customContextMenuRequested
        self.menu = QMenu(self)
        self.action_combine = self.menu.addAction("Combine")
        self.action_combine.triggered.connect(self.combine_file_paths)
        self.action_split = self.menu.addAction("Split")
        self.action_split.triggered.connect(self.split_file_paths)
        self.action_show_subfiles = self.menu.addAction("Show Subfiles...")
        self.action_show_subfiles.triggered.connect(self.show_subfiles)
        self.menu.addSeparator()
        self.action_remove = self.menu.addAction("Remove")
        self.action_remove.triggered.connect(self.remove_file_paths)
        self.menu.aboutToShow.connect(self.on_about_to_show)
        self.customContextMenuRequested.connect(self.show_menu)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragMoveEvent(event)

    def dropEvent(self, event: QDropEvent) -> None:
        if not event.mimeData().hasUrls():
            super().dropEvent(event)
            return

        file_paths = []
        is_recursive = Ns_Settings.value("Import/include-files-in-subfolders", type=bool)
        for url in event.mimeData().urls():
            if not (path := url.toLocalFile()):
                continue

            if os_path.isdir(path):
                file_paths.extend(Ns_IO.find_files(path, is_recursive))
            elif os_path.isfile(path):
                file_paths.append(path)

        self.add_file_paths(file_paths)
        event.acceptProposedAction()

    def on_about_to_show(self) -> None:
        if self._model.is_empty():
            self.menu.setEnabled(False)
            return
        else:
            self.menu.setEnabled(True)

        indexes: list[QModelIndex] = self.selectionModel().selectedRows()
        len_selected_rows = len(indexes)
        match len_selected_rows:
            case 0:
                self.menu.setEnabled(False)
            case 1:
                self.action_combine.setEnabled(False)
                self.action_remove.setEnabled(True)
                is_combined = bool(indexes[0].data(Qt.ItemDataRole.UserRole))
                self.action_split.setEnabled(is_combined)
                self.action_show_subfiles.setEnabled(is_combined)
            case _:
                self.action_combine.setEnabled(True)
                self.action_remove.setEnabled(True)
                self.action_split.setEnabled(False)
                self.action_show_subfiles.setEnabled(False)

    def show_menu(self) -> None:
        self.menu.exec(QCursor.pos())

    def combine_file_paths(self) -> None:
        name_indexes: list[QModelIndex] = self.selectionModel().selectedRows(column=0)
        path_indexes: list[QModelIndex] = self.selectionModel().selectedRows(column=1)
        rowno_name_path_triples: list[tuple[int, str | list[str], str | list[str]]] = sorted(
            zip(
                (index.row() for index in name_indexes),
                map(self._model.user_or_display_data, name_indexes),
                map(self._model.user_or_display_data, path_indexes),
                strict=False,
            ),
            key=lambda tri: tri[0],
        )
        (rowno_retained, names_retained, paths_retained), *triples = rowno_name_path_triples
        # name and path are both either str or list[str], does not check here
        # and this should be manually guaranteed
        if isinstance(names_retained, str):
            names_retained = [names_retained]
        if isinstance(paths_retained, str):
            paths_retained = [paths_retained]
        # Remove rows from bottom up, or otherwise lower row indexes will
        # change as upper rows are removed
        for rowno, name, path in reversed(triples):
            if isinstance(name, str):
                names_retained.append(name)
            elif isinstance(name, list):
                names_retained.extend(name)
            else:
                assert False, f"Invalid name type: {type(name)}"
            if isinstance(path, str):
                paths_retained.append(path)
            elif isinstance(path, list):
                paths_retained.extend(path)
            else:
                assert False, f"Invalid path type: {type(path)}"
            self.source_model.takeRow(rowno)

        first_name, *_, last_name = names_retained
        if len(names_retained) == 2:
            name_display = f"{first_name},{last_name}"
        else:
            name_display = f"{first_name},...,{last_name}"
        common_path = os_path.commonpath(paths_retained)
        first_path, *_, last_path = paths_retained
        first_path = first_path.removeprefix(common_path).lstrip(os_path.sep)
        last_path = last_path.removeprefix(common_path).lstrip(os_path.sep)
        if len(paths_retained) == 2:
            path_display = f"{common_path}{os_path.sep}{{{first_path},{last_path}}}"
        else:
            path_display = f"{common_path}{os_path.sep}{{{first_path},...,{last_path}}}"

        self.source_model.set_item_left_shifted(rowno_retained, 0, name_display)
        self.source_model.set_item_left_shifted(rowno_retained, 1, path_display)

        self.source_model.item(rowno_retained, 0).setData(names_retained, Qt.ItemDataRole.UserRole)
        self.source_model.item(rowno_retained, 1).setData(paths_retained, Qt.ItemDataRole.UserRole)

        self.edit(self.source_model.index(rowno_retained, 0))
        self.main.statusBar().showMessage(f"Marked {len(names_retained)} files for combination")

    def split_file_paths(self) -> None:
        name_index: QModelIndex = self.selectionModel().selectedRows(column=0)[0]
        path_index: QModelIndex = self.selectionModel().selectedRows(column=1)[0]
        top_rowno = name_index.row()

        names_retained = name_index.data(Qt.ItemDataRole.UserRole)
        paths_retained = path_index.data(Qt.ItemDataRole.UserRole)

        self.source_model.setData(name_index, names_retained[0])
        self.source_model.setData(path_index, paths_retained[0])
        self.selectRow(top_rowno)

        self.source_model.insertRows(top_rowno + 1, len(names_retained) - 1)

        bot_rowno = 0
        for bot_rowno, row in enumerate(
            zip(names_retained[1:], paths_retained[1:], strict=False), start=top_rowno + 1
        ):
            self.source_model.set_row_left_shifted(bot_rowno, row)
            self.selectRow(bot_rowno)

        # Select rows split off
        # https://forum.pythonguis.com/t/programmatically-select-multiple-rows-in-qtableview/510
        selection = QItemSelection()
        selection.select(self.source_model.index(top_rowno, 0), self.source_model.index(bot_rowno, 1))
        mode = QItemSelectionModel.SelectionFlag.Select | QItemSelectionModel.SelectionFlag.Rows
        self.selectionModel().select(selection, mode)

        # Clear subfile list
        self.source_model.setData(name_index, None, Qt.ItemDataRole.UserRole)
        self.source_model.setData(path_index, None, Qt.ItemDataRole.UserRole)

        self.main.statusBar().showMessage(f"Demarked {len(names_retained)} files from combination")

    def show_subfiles(self) -> None:
        name_index: QModelIndex = self.selectionModel().selectedRows(column=0)[0]
        path_index: QModelIndex = self.selectionModel().selectedRows(column=1)[0]

        Ns_Dialog_Table_Subfiles(self, name_index, path_index).open()

    def remove_file_paths(self) -> None:
        # https://stackoverflow.com/questions/5927499/how-to-get-selected-rows-in-qtableview
        indexes: list[QModelIndex] = self.selectionModel().selectedRows()
        # Need to count num before takeRow
        num = sum(
            map(
                lambda index: 1
                if isinstance((data := self._model.user_or_display_data(index)), str)
                else len(data),
                indexes,
            )
        )
        # Remove rows from bottom up, or otherwise lower row indexes will
        # change as upper rows are removed
        rownos = sorted((index.row() for index in indexes), reverse=True)
        for rowno in rownos:
            self.source_model.takeRow(rowno)
        if self.source_model.rowCount() == 0:
            self.source_model.clear_data()

        noun = "file" if num == 1 else "files"
        self.main.statusBar().showMessage(f"Removed {num} {noun}")

    def add_file_paths(self, file_paths_to_add: list[str]) -> None:
        if len(file_paths_to_add) == 0:
            self.main.statusBar().showMessage("No files found")
            return

        unique_file_paths_to_add: set[str] = set(file_paths_to_add)
        already_added_file_paths: set[str] = set(self._model.yield_flat_file_paths())
        file_paths_dup: set[str] = unique_file_paths_to_add & already_added_file_paths
        file_paths_unsupported: set[str] = set(filter(Ns_IO.not_supports, unique_file_paths_to_add))
        file_paths_empty: set[str] = set(filter(lambda p: not os_path.getsize(p), unique_file_paths_to_add))
        file_paths_ok: set[str] = (
            unique_file_paths_to_add
            - already_added_file_paths
            - file_paths_dup
            - file_paths_unsupported
            - file_paths_empty
        )
        if file_paths_ok:
            self._model.remove_empty_rows()
            already_added_file_stems = list(self._model.yield_flat_file_names())
            for file_path in sorted(file_paths_ok):
                file_stem = Path(file_path).stem
                file_stem = Ns_IO.ensure_unique_filestem(file_stem, already_added_file_stems)
                already_added_file_stems.append(file_stem)
                rowno = self._model.rowCount()
                self._model.set_row_left_shifted(rowno, (file_stem, file_path))
            self._model.rows_added.emit()

            num = len(file_paths_ok)
            noun = "file" if num == 1 else "files"
            self.main.statusBar().showMessage(f"Added {num} {noun}")

        if file_paths_dup or file_paths_unsupported or file_paths_empty:
            model_err_files = Ns_StandardItemModel(
                self, hor_labels=("Error Type", "File Path"), show_empty_row=False
            )
            for reason, file_paths in (
                ("Duplicate file", file_paths_dup),
                ("Unsupported file type", file_paths_unsupported),
                ("Empty file", file_paths_empty),
            ):
                for file_path in sorted(file_paths):
                    model_err_files.appendRow((QStandardItem(reason), QStandardItem(file_path)))
            tableview_err_files = Ns_TableView(self, model=model_err_files)

            dialog = Ns_Dialog_Table(
                self,
                title="Error Adding Files",
                text="Failed to add the following files.",
                width=580,
                height=260,
                tableview=tableview_err_files,
                export_filename="neosca_error_files.xlsx",
            )
            dialog.open()

    def yield_file_names(self) -> Generator[str, None, None]:
        return self._model.yield_file_names()

    def yield_file_paths(self) -> Generator[str | list[str], None, None]:
        return self._model.yield_file_paths()
