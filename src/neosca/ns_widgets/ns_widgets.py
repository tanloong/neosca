#!/usr/bin/env python3

from typing import Optional

from PySide6.QtCore import (
    QDir,
    Signal,
)
from PySide6.QtGui import (
    QFocusEvent,
    QPalette,
    Qt,
)
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QCompleter,
    QFileDialog,
    QFileSystemModel,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QTextEdit,
    QWidget,
)

from neosca.ns_singleton import QSingleton


# https://github.com/BLKSerene/Wordless/blob/fa743bcc2a366ec7a625edc4ed6cfc355b7cd22e/wordless/wl_widgets/wl_layouts.py#L108
class Ns_ScrollArea(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setBackgroundRole(QPalette.ColorRole.Light)


class Ns_FileSystemModel(QFileSystemModel, metaclass=QSingleton):
    def __init__(self, parent=None):
        super().__init__(parent)
        # > Do not add file watchers to the paths. This reduces overhead when using the
        # > model for simple tasks like line edit completion.
        self.setOption(QFileSystemModel.Option.DontWatchForChanges)
        self.has_set_root = False

    def start_querying(self):
        # > QFileSystemModel will not fetch any files or directories until
        # > setRootPath() is called.
        if not self.has_set_root:
            self.setRootPath(QDir.homePath())
            self.has_set_root = True


class Ns_LineEdit(QLineEdit):
    """This class emits the custom "focused" signal and is specifically used
    in Ns_LineEdit_Path to tell Ns_FileSystemModel to start querying. The
    querying should only start at the first emit and all subsequent emits are
    ignored. We prefer the custom "focused" signal over the built-in
    "textEdited" because it has much less frequent emits."""

    focused = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

    # Override
    def focusInEvent(self, e: QFocusEvent):
        super().focusInEvent(e)
        self.focused.emit()


class Ns_LineEdit_Path(QWidget):
    # https://stackoverflow.com/a/20796318/20732031
    def __init__(self, parent=None):
        super().__init__(parent)

        filesystem_model = Ns_FileSystemModel()
        completer_lineedit_files = QCompleter()
        completer_lineedit_files.setModel(filesystem_model)
        completer_lineedit_files.setCompletionMode(QCompleter.CompletionMode.InlineCompletion)
        completer_lineedit_files.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.lineedit = Ns_LineEdit()
        self.lineedit.focused.connect(filesystem_model.start_querying)
        self.lineedit.setCompleter(completer_lineedit_files)
        self.lineedit.setClearButtonEnabled(True)
        button_browse = QPushButton("Browse")

        # Bind
        button_browse.clicked.connect(self.browse_path)

        hlayout = QHBoxLayout()
        hlayout.setContentsMargins(0, 0, 0, 0)
        hlayout.addWidget(self.lineedit)
        hlayout.addWidget(button_browse)
        self.setLayout(hlayout)

    def text(self) -> str:
        return self.lineedit.text()

    def setText(self, text: str) -> None:
        self.lineedit.setText(text)

    def browse_path(self):
        folder_path = QFileDialog.getExistingDirectory(self, caption="Choose Path")
        if not folder_path:
            return
        self.lineedit.setText(folder_path)

    # Override
    def setFocus(self) -> None:
        self.lineedit.setFocus()

    def selectAll(self) -> None:
        self.lineedit.selectAll()


class Ns_Combobox_Editable(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        # https://stackoverflow.com/questions/45393507/pyqt4-avoid-adding-the-items-to-the-qcombobox
        self.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.setEditable(True)


class Ns_MessageBox_Question(QMessageBox):
    def __init__(
        self,
        parent=None,
        title: str = "",
        text: str = "",
        icon: QMessageBox.Icon = QMessageBox.Icon.Question,
        checkbox: Optional[QCheckBox] = None,
    ):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setText(text)
        self.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        self.setIcon(icon)
        if checkbox is not None:
            self.setCheckBox(checkbox)

    # Override
    def exec(self) -> bool:
        ret = super().exec()
        return ret == QMessageBox.StandardButton.Yes.value


class Ns_TextEdit_ReadOnly(QTextEdit):
    def __init__(self, *, text: str = "", parent=None):
        super().__init__(text, parent)
        self.setReadOnly(True)
