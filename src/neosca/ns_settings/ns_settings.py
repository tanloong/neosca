#!/usr/bin/env python3

from typing import Any

from PyQt5.QtCore import QSettings

from neosca import SETTING_PATH
from neosca.ns_settings.ns_settings_default import settings_default


class Ns_Settings:
    # Although QSettings can auto synchronize changes across all instances,
    #  we use this class to keep a single object in the whole application.
    # Don't instanciate this class, just use its classmethods.

    # Use IniFormat to avoid Windows system registry limitations on subkey lengths
    # https://doc.qt.io/qtforpython-6/PySide6/QtCore/QSettings.html#platform-limitations
    settings = QSettings(str(SETTING_PATH), QSettings.Format.IniFormat)
    for k, v in settings_default.items():
        if not settings.contains(k):
            settings.setValue(k, v)

    @classmethod
    def reset(cls) -> None:
        for k, v in settings_default.items():
            cls.settings.setValue(k, v)

    @classmethod
    def allKeys(cls) -> list[str]:
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
    def value(cls, key: str, *args, **kwargs) -> Any:
        """
        e.g.
            called with defaultValue:
                >>> value("num", 100)
            called with type:
                >>> value("is_windows", type=bool)
                # Use the "type" arg to get values of types other than string
                # https://bugreports.qt.io/browse/PYSIDE-1466
        """
        return cls.settings.value(key, *args, **kwargs)

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
