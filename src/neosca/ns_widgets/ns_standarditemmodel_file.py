#!/usr/bin/env python3

from collections.abc import Generator
from typing import Any

from PyQt5.QtCore import QModelIndex, Qt

from ..ns_widgets.ns_standarditemmodel import Ns_StandardItemModel


class Ns_StandardItemModel_File(Ns_StandardItemModel):
    def __init__(self, main) -> None:
        super().__init__(main, hor_labels=("Name", "Path"), show_empty_row=True)
        self.data_cleared.connect(lambda: self.main.enable_button_generate_table(False))
        self.rows_added.connect(lambda: self.main.enable_button_generate_table(True))

    def user_or_display_data(self, index_or_rowno: QModelIndex | int, colno: int | None = None) -> Any:
        if isinstance(index_or_rowno, QModelIndex):
            user_data = index_or_rowno.data(Qt.ItemDataRole.UserRole)
            return user_data if user_data else index_or_rowno.data(Qt.ItemDataRole.DisplayRole)
        elif colno is not None:
            return self.user_or_display_data(self.index(index_or_rowno, colno))
        else:
            assert False, f"Invalid index_or_rowno type: {type(index_or_rowno)}"

    def _yield_flat_file_column(self, colno: int) -> Generator[str, None, None]:
        for rowno in range(self.rowCount()):
            data = self.user_or_display_data(rowno, colno)
            if isinstance(data, str):
                yield data
            elif isinstance(data, list):
                yield from data

    def yield_flat_file_names(self) -> Generator[str, None, None]:
        """
        For simple row, yield file name displayed (str); for combined row, yield each combined subfile name (str)
        """
        return self._yield_flat_file_column(0)

    def yield_flat_file_paths(self) -> Generator[str, None, None]:
        """
        For simple row, yield file path displayed (str); for combined row, yield each combined subfile path (str)
        """
        return self._yield_flat_file_column(1)

    def _yield_file_column(self, colno) -> Generator[str | list[str], None, None]:
        for rowno in range(self.rowCount()):
            data = self.user_or_display_data(rowno, colno)
            if isinstance(data, (str, list)):
                yield data

    def yield_file_names(self) -> Generator[str, None, None]:
        """
        For either simple or combined row, yield file name displayed (str)
        """
        return self.yield_column(0)

    def yield_file_paths(self) -> Generator[str | list[str], None, None]:
        """
        For simple row, yield file path displayed (str); for combined row, yield the list of subfile paths (list[str])
        """
        return self._yield_file_column(1)
