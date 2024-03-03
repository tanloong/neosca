#!/usr/bin/env python3

from typing import Dict, Tuple

from PySide6.QtCore import QModelIndex, QPersistentModelIndex, QPoint
from PySide6.QtGui import QBrush, QColor, QPainter, Qt
from PySide6.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem

from neosca.ns_settings.ns_settings import Ns_Settings
from neosca.ns_widgets import ns_dialogs


class Ns_StyledItemDelegate_Triangle(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.triangle_rgb = "#737373"

    def paint(
        self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex
    ):
        super().paint(painter, option, index)
        if index.data(Qt.ItemDataRole.UserRole):
            painter.save()
            painter.setBrush(QBrush(QColor.fromString(self.triangle_rgb)))
            triangle_leg_length = option.rect.height() * Ns_Settings.value(
                "Appearance/triangle-height-ratio", type=float
            )
            painter.drawPolygon(
                (
                    QPoint(option.rect.x() + triangle_leg_length, option.rect.y()),
                    QPoint(option.rect.x(), option.rect.y()),
                    QPoint(option.rect.x(), option.rect.y() + triangle_leg_length),
                )
            )
            painter.restore()


class Ns_StyledItemDelegate_Matches(Ns_StyledItemDelegate_Triangle):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.position_dialog_mappings: Dict[Tuple[int, int], ns_dialogs.Ns_Dialog_TextEdit_Matches] = {}

    # Override
    def createEditor(self, parent, option, index):  # type: ignore
        if not index.data(Qt.ItemDataRole.UserRole):
            return None
        position = (index.row(), index.column())
        if position in self.position_dialog_mappings:
            self.position_dialog_mappings[position].bring_to_front()
        else:
            dialog = ns_dialogs.Ns_Dialog_TextEdit_Matches(parent, index=index)
            self.position_dialog_mappings[position] = dialog
            dialog.finished.connect(lambda: self.position_dialog_mappings.pop(position))
            dialog.show()


class Ns_StyledItemDelegate_File(Ns_StyledItemDelegate_Triangle):
    def __init__(self, parent=None):
        super().__init__(parent)

    # Override
    def createEditor(self, parent, option, index):  # type: ignore
        if index.column() != 0:
            return None
        if not index.data(Qt.ItemDataRole.UserRole):
            return None

        return super().createEditor(parent, option, index)
