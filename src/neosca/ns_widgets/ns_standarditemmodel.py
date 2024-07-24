#!/usr/bin/env python3

from collections.abc import Generator, Iterable, Sequence
from typing import Any, Literal

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QMessageBox

from neosca.ns_widgets.ns_widgets import Ns_MessageBox_Question


class Ns_StandardItemModel(QStandardItemModel):
    data_cleared = pyqtSignal()
    rows_added = pyqtSignal()
    data_exported = pyqtSignal()
    item_left_shifted = pyqtSignal(tuple)
    item_right_shifted = pyqtSignal(tuple)

    def __init__(
        self,
        main,
        hor_labels: Sequence[str] | None = None,
        ver_labels: Sequence[str] | None = None,
        orientation: Literal["hor", "ver"] = "hor",
        show_empty_row: bool = True,
        **kwargs,
    ) -> None:
        super().__init__(main, **kwargs)
        self.main = main
        if hor_labels is not None:
            self.setColumnCount(len(hor_labels))
            self.setHorizontalHeaderLabels(hor_labels)
        if ver_labels is not None:
            self.setRowCount(len(ver_labels))
            self.setVerticalHeaderLabels(ver_labels)

        self.orientation = orientation
        if show_empty_row:
            if orientation == "hor":
                self.setRowCount(1)
            elif orientation == "ver":
                self.setColumnCount(1)
            else:
                assert False, f"Invalid orientation: {orientation}"
        self.show_empty_row = show_empty_row

        self.has_been_exported: bool = False
        self.rows_added.connect(lambda: self.set_has_been_exported(False))
        self.data_exported.connect(lambda: self.set_has_been_exported(True))
        self.item_left_shifted.connect(lambda args: self.set_item_left_shifted(*args))
        self.item_right_shifted.connect(lambda args: self.set_item_right_shifted(*args))

    def set_item_left_shifted(self, rowno: int, colno: int, value: QStandardItem | str):
        if isinstance(value, QStandardItem):
            item = value
        elif isinstance(value, str):
            item = QStandardItem()
            # https://stackoverflow.com/a/20469423/20732031
            item.setData(value, Qt.ItemDataRole.DisplayRole)
        else:
            assert False, f"Invalid value type: {type(value)}"
        item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.setItem(rowno, colno, item)

    def set_row_left_shifted(self, rowno: int, values: Iterable[QStandardItem | str], start: int = 0) -> None:
        for colno, value in enumerate(values, start=start):
            self.set_item_left_shifted(rowno, colno, value)

    def set_item_right_shifted(self, rowno: int, colno: int, value: QStandardItem | str | int | float):
        if isinstance(value, QStandardItem):
            item = value
        elif isinstance(value, (str, int, float)):
            item = QStandardItem()
            # https://stackoverflow.com/a/20469423/20732031
            item.setData(value, Qt.ItemDataRole.DisplayRole)
        else:
            assert False, f"Invalid value type: {type(value)}"
        item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.setItem(rowno, colno, item)

    def set_row_right_shifted(
        self, rowno: int, values: Iterable[QStandardItem | str | int | float], start: int = 0
    ) -> None:
        for colno, value in enumerate(values, start=start):
            self.set_item_right_shifted(rowno, colno, value)

    def set_has_been_exported(self, exported: bool) -> None:
        self.has_been_exported = exported

    def _clear_data(self) -> None:
        if self.orientation == "hor":
            self.removeRows(0, self.rowCount())
            if self.show_empty_row:
                self.setRowCount(1)
        elif self.orientation == "ver":
            self.setColumnCount(0)
            if self.show_empty_row:
                self.setColumnCount(1)
        self.data_cleared.emit()

    def clear_data(self, confirm=False) -> None:
        """
        Clear data, reserve headers
        """
        if not confirm or self.has_been_exported:
            return self._clear_data()
        else:
            messagebox = Ns_MessageBox_Question(
                self.main,
                "Clear Table",
                "The table has not been exported yet and all the data will be lost. Continue?",
            )
            if messagebox.exec() == QMessageBox.StandardButton.Yes:
                self._clear_data()

    def is_row_empty(self, rowno: int) -> bool:
        for colno in range(self.columnCount()):
            item = self.item(rowno, colno)
            if item is not None and item.text() != "":
                return False
        return True

    def is_empty(self) -> bool:
        return all(self.is_row_empty(rowno) for rowno in range(self.rowCount()))

    def has_user_data(self) -> bool:
        for rowno in range(self.rowCount()):
            for colno in range(self.columnCount()):
                if self.item(rowno, colno).data(Qt.ItemDataRole.UserRole):
                    return True
        return False

    def remove_empty_rows(self) -> None:
        for rowno in reversed(range(self.rowCount())):
            if self.is_row_empty(rowno):
                self.removeRow(rowno)

    # Type hint for generator: https://docs.python.org/3.12/library/typing.html#typing.Generator
    def yield_column(
        self, colno: int, role: Qt.ItemDataRole = Qt.ItemDataRole.DisplayRole
    ) -> Generator[Any, None, None]:
        items = (self.item(rowno, colno) for rowno in range(self.rowCount()))
        return (item.data(role) for item in items if item is not None)

    def yield_checked_item_data(self, colno: int, role: Qt.ItemDataRole) -> Generator[Any, None, None]:
        for rowno in range(self.rowCount()):
            item = self.item(rowno, colno)
            if item is None:
                continue
            if item.checkState() == Qt.CheckState.Checked:
                yield item.data(role)

    # https://stackoverflow.com/questions/75038194/qt6-how-to-disable-selection-for-empty-cells-in-qtableview
    # def flags(self, index) -> Qt.ItemFlag:
    #     if index.data() is None:
    #         return Qt.ItemFlag.NoItemFlags
    #     return super().flags(index)
