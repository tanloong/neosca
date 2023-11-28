#!/usr/bin/env python3

from PySide6.QtCore import QObject


# https://github.com/jazzycamel/PyQt5Singleton/issues/1#issuecomment-1429485569
class QSingleton(type(QObject)):
    """
    Usage:
        class Foo(QObject, metaclass=QSingleton):
            ...
    """

    def __init__(self, name, bases, dict):
        super().__init__(name, bases, dict)
        self.instance = None

    def __call__(self, *args, **kwargs):
        if self.instance is None:
            self.instance = super().__call__(*args, **kwargs)
        return self.instance
