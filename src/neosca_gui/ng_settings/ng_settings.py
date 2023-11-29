#!/usr/bin/env python3

from typing import Any, List

from PySide6.QtCore import QSettings

from neosca_gui import SETTING_PATH
from neosca_gui.ng_settings.ng_settings_default import settings_default


class Ng_Settings:
    # Although QSettings can auto synchronize changes across all instances,
    #  we use this class to keep a single instance in the whole application.
    # Don't have to instanciate this class, just use its classmethods.

    # Use IniFormat to avoid Windows system registry limitations on subkey lengths
    # https://doc.qt.io/qtforpython-6/PySide6/QtCore/QSettings.html#platform-limitations
    settings = QSettings(str(SETTING_PATH), QSettings.Format.IniFormat)
    for k, v in settings_default.items():
        if not settings.contains(k):
            settings.setValue(k, v)

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
