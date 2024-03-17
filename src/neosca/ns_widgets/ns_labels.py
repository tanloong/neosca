#!/usr/bin/env python3

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel


class Ns_Label_WordWrapped(QLabel):
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setWordWrap(True)


# https://github.com/BLKSerene/Wordless/blob/1c319ce54be60aa948c89d6d3cdd327cccfc7c15/wordless/wl_widgets/wl_labels.py#L47
class Ns_Label_Html(QLabel):
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setTextFormat(Qt.TextFormat.RichText)
        self.setOpenExternalLinks(True)


class Ns_Label_Html_VTop(Ns_Label_Html):
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setAlignment(Qt.AlignmentFlag.AlignTop)


class Ns_Label_Html_VBottom(Ns_Label_Html):
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setAlignment(Qt.AlignmentFlag.AlignBottom)


# https://github.com/BLKSerene/Wordless/blob/1c319ce54be60aa948c89d6d3cdd327cccfc7c15/wordless/wl_widgets/wl_labels.py#L54
class Ns_Label_Html_Centered(Ns_Label_Html):
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)


class Ns_Label_Html_WordWrapped(Ns_Label_Html):
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setWordWrap(True)
