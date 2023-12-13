#!/usr/bin/env python3

import json
import re
from enum import Enum
from typing import TYPE_CHECKING, List, Union

from PySide6.QtCore import (
    QElapsedTimer,
    QModelIndex,
    QPersistentModelIndex,
    QTime,
    QTimer,
    Signal,
)
from PySide6.QtGui import (
    Qt,
    QTextBlockFormat,
    QTextCursor,
)
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QGridLayout,
    QLabel,
    QPushButton,
    QTextEdit,
)

from neosca_gui import CITING_PATH
from neosca_gui.ng_about import __title__

if TYPE_CHECKING:
    from neosca_gui.ng_widgets.ng_tables import Ng_TableView


class Ng_Dialog(QDialog):
    class ButtonAlignmentFlag(Enum):
        AlignLeft = 0
        AlignRight = 2

    def __init__(
        self, *args, title: str = "", width: int = 0, height: int = 0, resizable=False, **kwargs
    ) -> None:
        """
        ┌———————————┐
        │           │
        │  content  │
        │           │
        │———————————│
        │  buttons  │
        └———————————┘
        """
        super().__init__(*args, **kwargs)
        # https://github.com/BLKSerene/Wordless/blob/main/wordless/wl_dialogs/wl_dialogs.py#L28
        # [Copied code starts here]
        # Dialog size
        if resizable:
            if not width:
                width = self.size().width()

            if not height:
                height = self.size().height()

            self.resize(width, height)
        else:
            if width:
                self.setFixedWidth(width)

            if height:
                self.setFixedHeight(height)
            # Gives the window a thin dialog border on Windows. This style is
            # traditionally used for fixed-size dialogs.
            self.setWindowFlag(Qt.WindowType.MSWindowsFixedSizeDialogHint)
        # [Copied code ends here]
        self.setWindowTitle(title)

        self.layout_content = QGridLayout()
        self.layout_button = QGridLayout()
        self.layout_button.setColumnStretch(1, 1)

        self.grid_layout = QGridLayout()
        self.grid_layout.addLayout(self.layout_content, 0, 0)
        self.grid_layout.addLayout(self.layout_button, 1, 0)
        self.setLayout(self.grid_layout)

    def rowCount(self) -> int:
        return self.layout_content.rowCount()

    def columnCount(self) -> int:
        return self.layout_content.columnCount()

    def addWidget(self, *args, **kwargs) -> None:
        self.layout_content.addWidget(*args, **kwargs)

    def addButtons(self, *buttons, alignment: ButtonAlignmentFlag) -> None:
        layout = QGridLayout()
        for colno, button in enumerate(buttons):
            layout.addWidget(button, 0, colno)
        self.layout_button.addLayout(layout, 0, alignment.value)

    def setColumnStretch(self, column: int, strech: int) -> None:
        self.layout_content.setColumnStretch(column, strech)

    def setRowStretch(self, row: int, strech: int) -> None:
        self.layout_content.setRowStretch(row, strech)


class Ng_Dialog_Processing_With_Elapsed_Time(Ng_Dialog):
    started = Signal()
    # Use this to get the place holder, e.g. 0:00:00
    time_format_re = re.compile(r"[^:]")

    def __init__(
        self,
        *args,
        title: str = "Please Wait",
        width: int = 500,
        height: int = 0,
        time_format: str = "h:mm:ss",
        interval: int = 1000,
        **kwargs,
    ) -> None:
        super().__init__(*args, title=title, width=width, height=height, resizable=False, **kwargs)
        self.time_format = time_format
        self.interval = interval
        self.elapsedtimer = QElapsedTimer()
        self.timer = QTimer()

        # TODO: this label should be exposed
        self.label_status = QLabel("Processing...")
        self.text_time_elapsed_zero = f"Elapsed time: {self.time_format_re.sub('0', time_format)}"
        self.label_time_elapsed = QLabel(self.text_time_elapsed_zero)
        self.label_please_wait = QLabel(
            "Please be patient. The wait time can range from a few seconds to several minutes."
        )
        self.label_please_wait.setWordWrap(True)

        self.addWidget(self.label_status, 0, 0)
        self.addWidget(self.label_time_elapsed, 0, 1, alignment=Qt.AlignmentFlag.AlignRight)
        self.addWidget(self.label_please_wait, 1, 0, 1, 2)

        self.setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint)

        # Bind
        self.timer.timeout.connect(self.update_time_elapsed)
        self.started.connect(self.elapsedtimer.start)
        # If the timer is already running, it will be stopped and restarted.
        self.started.connect(lambda: self.timer.start(self.interval))
        # Either 'accepted' or 'rejected', although 'rejected' is disabled (see rejected below)
        self.finished.connect(self.reset_time_elapsed)
        self.finished.connect(self.timer.stop)

    def reset_time_elapsed(self) -> None:
        self.label_time_elapsed.setText(self.text_time_elapsed_zero)

    def update_time_elapsed(self) -> None:
        time_elapsed: int = self.elapsedtimer.elapsed()
        qtime: QTime = QTime.fromMSecsSinceStartOfDay(time_elapsed)
        self.label_time_elapsed.setText(f"Elapsed time: {qtime.toString(self.time_format)}")

    # Override
    def reject(self) -> None:
        pass

    # Override
    def show(self) -> None:
        self.started.emit()
        return super().show()

    # Override
    def open(self) -> None:
        self.started.emit()
        return super().open()

    # Override
    def exec(self) -> int:
        self.started.emit()
        return super().exec()


class Ng_Dialog_TextEdit(Ng_Dialog):
    def __init__(self, *args, title: str = "", text: str = "", **kwargs) -> None:
        super().__init__(*args, title=title, resizable=True, **kwargs)
        self.textedit = QTextEdit(text)
        self.textedit.setReadOnly(True)
        # https://stackoverflow.com/questions/74852753/indent-while-line-wrap-on-qtextedit-with-pyside6-pyqt6
        indentation: int = self.fontMetrics().horizontalAdvance("abcd")
        self.fmt_textedit = QTextBlockFormat()
        self.fmt_textedit.setLeftMargin(indentation)
        self.fmt_textedit.setTextIndent(-indentation)

        self.button_copy = QPushButton("Copy")
        self.button_copy.clicked.connect(self.copy)

        self.button_close = QPushButton("Close")
        self.button_close.clicked.connect(self.reject)

        self.addButtons(self.button_copy, alignment=Ng_Dialog.ButtonAlignmentFlag.AlignLeft)
        self.addButtons(self.button_close, alignment=Ng_Dialog.ButtonAlignmentFlag.AlignRight)

    def setText(self, text: str) -> None:
        self.textedit.setText(text)
        cursor = QTextCursor(self.textedit.document())
        cursor.select(QTextCursor.SelectionType.Document)
        cursor.mergeBlockFormat(self.fmt_textedit)

    def copy(self) -> None:
        self.textedit.selectAll()
        self.textedit.copy()

    # Override
    def show(self) -> None:
        # Add self.textedit lastly to allow users add custom widgets above
        self.addWidget(self.textedit, self.rowCount(), 0, 1, self.columnCount())
        return super().show()

    # Override
    def open(self) -> None:
        # Add self.textedit lastly to allow users add custom widgets above
        self.addWidget(self.textedit, self.rowCount(), 0, 1, self.columnCount())
        return super().open()

    # Override
    def exec(self) -> int:
        # Add self.textedit lastly to allow users add custom widgets above
        self.addWidget(self.textedit, self.rowCount(), 0, 1, self.columnCount())
        return super().exec()


class Ng_Dialog_TextEdit_SCA_Matched_Subtrees(Ng_Dialog_TextEdit):
    def __init__(self, *args, index: Union[QModelIndex, QPersistentModelIndex], **kwargs):
        super().__init__(*args, title="Matches", width=500, height=300, **kwargs)
        self.file_name = index.model().verticalHeaderItem(index.row()).text()
        self.sname = index.model().horizontalHeaderItem(index.column()).text()
        self.matched_subtrees: List[str] = index.data(Qt.ItemDataRole.UserRole)
        self.setText("\n".join(self.matched_subtrees))

        self.label_summary = QLabel(
            f'{len(self.matched_subtrees)} occurrences of "{self.sname}" in "{self.file_name}"'
        )
        self.label_summary.setWordWrap(True)
        self.addWidget(self.label_summary)


class Ng_Dialog_TextEdit_Citing(Ng_Dialog_TextEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, title="Citing", **kwargs)
        with open(CITING_PATH, encoding="utf-8") as f:
            self.style_citation_mapping = json.load(f)

        self.label_citing = QLabel(f"If you use {__title__} in your research, please kindly cite as follows.")
        self.label_citing.setWordWrap(True)
        self.setText(next(iter(self.style_citation_mapping.values())))
        self.label_choose_citation_style = QLabel("Choose citation style: ")
        self.combobox_choose_citation_style = QComboBox()
        self.combobox_choose_citation_style.addItems(tuple(self.style_citation_mapping.keys()))
        self.combobox_choose_citation_style.currentTextChanged.connect(
            lambda key: self.setText(self.style_citation_mapping[key])
        )

        self.addWidget(self.label_citing, 0, 0, 1, 2)
        self.addWidget(self.label_choose_citation_style, 1, 0)
        self.addWidget(self.combobox_choose_citation_style, 1, 1)
        self.setColumnStretch(1, 1)


class Ng_Dialog_Table(Ng_Dialog):
    def __init__(
        self,
        *args,
        text: str,
        tableview: "Ng_TableView",
        export_filename: str = "",
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.tableview: "Ng_TableView" = tableview
        self.layout_content.addWidget(QLabel(text), 0, 0)
        self.layout_content.addWidget(tableview, 1, 0)
        self.export_filename = export_filename

        self.button_ok = QPushButton("OK")
        self.button_ok.clicked.connect(self.accept)
        self.button_export_table = QPushButton("Export table...")
        self.button_export_table.clicked.connect(lambda: self.tableview.export_table(self.export_filename))
        self.addButtons(self.button_export_table, alignment=Ng_Dialog.ButtonAlignmentFlag.AlignLeft)
        self.addButtons(self.button_ok, alignment=Ng_Dialog.ButtonAlignmentFlag.AlignRight)
