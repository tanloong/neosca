#!/usr/bin/env python3

from PyQt5.QtCore import QSortFilterProxyModel, Qt
from typing_extensions import override

from ..ns_widgets.ns_standarditemmodel import NsStandardItemModel


class NsSortFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, main, source_model: NsStandardItemModel):
        super().__init__(main)
        self.main = main
        self.source_model = source_model
        self.setSourceModel(source_model)

        self.setDynamicSortFilter(False)

    # Override to sepcify the return type
    @override
    def sourceModel(self) -> NsStandardItemModel:
        return self.source_model

    # https://www.qtcentre.org/threads/22120-No-Sort-Vertical-Header?p=107720#post107720
    @override
    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole):
        if orientation != Qt.Orientation.Vertical or role != Qt.ItemDataRole.DisplayRole:
            return super().headerData(section, orientation, role)
        else:
            return section + 1
