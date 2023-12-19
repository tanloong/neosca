#!/usr/bin/env python3

from typing import Dict, Tuple

from PySide6.QtCore import QModelIndex, QPersistentModelIndex, QPoint
from PySide6.QtGui import QBrush, QColor, QPainter, Qt
from PySide6.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem

from neosca.ns_qss import Ns_QSS
from neosca.ns_settings.ns_settings import Ns_Settings
from neosca.ns_widgets import ns_dialogs


class Ns_Delegate_SCA(QStyledItemDelegate):
    def __init__(self, parent=None, qss: str = ""):
        super().__init__(parent)
        if (
            triangle_rgb := Ns_QSS.get_value(qss, "QHeaderView::section:vertical", "background-color")
        ) is not None:
            self.triangle_rgb = triangle_rgb
        else:
            self.triangle_rgb = "#000000"

        self.pos_dialog_mappings: Dict[Tuple[int, int], ns_dialogs.Ns_Dialog_TextEdit_SCA_Matched_Subtrees] = {}

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

    # Override
    def createEditor(self, parent, option, index):
        if not index.data(Qt.ItemDataRole.UserRole):
            return None
        pos = (index.row(), index.column())
        if pos in self.pos_dialog_mappings:
            self.pos_dialog_mappings[pos].bring_to_front()
        else:
            dialog = ns_dialogs.Ns_Dialog_TextEdit_SCA_Matched_Subtrees(parent, index=index)
            self.pos_dialog_mappings[pos] = dialog
            dialog.finished.connect(lambda: self.pos_dialog_mappings.pop(pos))
            dialog.show()

