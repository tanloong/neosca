#!/usr/bin/env python3

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel


class NsLabelWordWrapped(QLabel):
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setWordWrap(True)


# https://github.com/BLKSerene/Wordless/blob/1c319ce54be60aa948c89d6d3cdd327cccfc7c15/wordless/wl_widgets/wl_labels.py#L47
class NsLabelHtml(QLabel):
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setTextFormat(Qt.TextFormat.RichText)
        self.setOpenExternalLinks(True)


class NsLabelHTMLVTop(NsLabelHtml):
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setAlignment(Qt.AlignmentFlag.AlignTop)


class NsLabelHTMLVBottom(NsLabelHtml):
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setAlignment(Qt.AlignmentFlag.AlignBottom)


# https://github.com/BLKSerene/Wordless/blob/1c319ce54be60aa948c89d6d3cdd327cccfc7c15/wordless/wl_widgets/wl_labels.py#L54
class NsLabelHtmlCentered(NsLabelHtml):
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)


class NsLabelHTMLWordWrapped(NsLabelHtml):
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setWordWrap(True)
