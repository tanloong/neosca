#!/usr/bin/env python3

from typing import Any, List

from PySide6.QtCore import QSettings

from neosca_gui.ng_about import __name__


class Ng_Settings:
    # Although QSettings can auto synchronize changes across all instances,
    #  we use this class to keep a single instance in the whole application.
    # Don't have to instanciate this class, just use its classmethods.

    # Use IniFormat to avoid Windows system registry limitations on subkey lengths
    # https://doc.qt.io/qtforpython-6/PySide6/QtCore/QSettings.html#platform-limitations
    QSettings.setDefaultFormat(QSettings.Format.IniFormat)
    # Orgnization name, application name
    settings = QSettings(__name__.lower(), __name__.lower())

    @classmethod
    def allKeys(cls) -> List[str]:
        return cls.settings.allKeys()

    @classmethod
    def beginGroup(cls, prefix: str) -> None:
        return cls.settings.beginGroup(prefix)

    @classmethod
    def endGroup(cls) -> None:
        return cls.settings.endGroup()

    @classmethod
    def fileName(cls) -> str:
        return cls.settings.fileName()

    @classmethod
    def value(cls, key: str, defaultValue: Any = None) -> Any:
        return cls.settings.value(key, defaultValue)

    @classmethod
    def setValue(cls, key: str, value: Any) -> None:
        cls.settings.setValue(key, value)

    @classmethod
    def remove(cls, key: str) -> None:
        cls.settings.remove(key)

    @classmethod
    def sync(cls) -> None:
        cls.settings.sync()

    @classmethod
    def contains(cls, key: str) -> bool:
        return cls.settings.contains(key)
