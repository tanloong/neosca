#!/usr/bin/env python3

from os import PathLike
import os.path as os_path
import re
from typing import Any, Dict, Optional, Union

from PySide6.QtWidgets import QWidget

QSSMapping = Dict[str, Union[str, Dict[str, str]]]


class Ng_QSS:
    def __init__(self):
        pass

    @staticmethod
    def read_qss_file(qss_file_path: Union[str, PathLike], default: Any = ""):
        if os_path.isfile(qss_file_path) and os_path.getsize(qss_file_path) > 0:
            with open(qss_file_path, encoding="utf-8") as file:
                return file.read()
        else:
            return default

    @staticmethod
    def get_value(qss: str, selector: str, attrname: str) -> Optional[str]:
        """
        >>> qss = "QHeaderView::section:horizontal { background-color: #5C88C5; }"
        >>> get_value(qss, "QHeaderView::section:horizontal", "background-color")
        #5C88C5
        """
        # Notice that only the 1st selector will be matched here
        matched_selector = re.search(selector, qss)
        if matched_selector is None:
            return None
        matched_value = re.search(rf"[^}}]+{attrname}:\s*([^;]+);", qss[matched_selector.end() :])
        if matched_value is None:
            return None
        return matched_value.group(1)

    @classmethod
    def mapping_to_str(cls, mapping: QSSMapping) -> str:
        qss_str = ""
        for selector, declaration in mapping.items():
            if isinstance(declaration, str):
                # str_to_mapping requires every value ends with ";"
                if not declaration.endswith(";"):
                    declaration = f"{declaration};"
                qss_str += f"{selector}: {declaration}\n"
            else:
                qss_str += f"{selector} {{\n"  # }}
                for property, value in declaration.items():
                    # str_to_mapping requires every value ends with ";"
                    if not value.endswith(";"):
                        value = f"{value};"
                    qss_str += f"{property}: {value}\n"
                qss_str += "}\n"
        return qss_str

    @classmethod
    def str_to_mapping(cls, qss_str: str) -> QSSMapping:
        """
        This func requires that in the qss_str
            (1) Every value ends with ";"
                e.g., "font-size: 11pt" ✗
                e.g., "font-size: 11pt;" ✓
            (2) The trailing ";" be attached to the value and separated
                from the subsequent token
                e.g., "font-size: 11pt ;" ✗
                e.g., "font-size: 11pt;" ✓
                e.g., "font-size: 11pt;max-width: 75px;" ✗
                e.g., "font-size: 11pt; max-width: 75px;" ✓
            (3) The trailing ":" of a property be attached to the lhs property and
                separated from the rhs value
                e.g., "font-size :11pt;" ✗
                e.g., "font-size : 11pt;" ✗
                e.g., "font-size: 11pt;" ✓
        This func allows that in the qss_str
            (1) Values have whitespaces
                e.g., "font-family: Noto Sans;" ✓
            (2) Selectors have whitespaces
                e.g., "QDialog QPushButton { color: black; }" ✓
                e.g., "QDialog > QPushButton { color: black; }" ✓
            (3) "{" and "}" are not separated from others
                e.g., "QDialog QPushButton{color: black;}" ✓
        Later value for the same property will override the previous one
        The returned dict will always has a trailing ";" across its values
        """
        selector_declaration_mapping = {}
        cur_selector = None
        cur_property = None
        qss_str = qss_str.replace("{", " { ").replace("}", " } ")
        token_gen = iter(qss_str.split())
        while (token := next(token_gen, None)) is not None:
            if token == "{":  # }
                pass
            elif token == "}":
                cur_selector = None
            elif token.endswith(":"):
                cur_property = token.rstrip(":")
            elif cur_property is not None:
                if cur_selector is None:
                    value_prev = selector_declaration_mapping.get(cur_property, "")
                    value = f"{value_prev} {token}" if not value_prev.endswith(";") else token
                    selector_declaration_mapping[cur_property] = value.lstrip()
                else:
                    if cur_selector not in selector_declaration_mapping:
                        selector_declaration_mapping[cur_selector] = {}
                    value_prev = selector_declaration_mapping[cur_selector].get(cur_property, "")
                    value = f"{value_prev} {token}" if not value_prev.endswith(";") else token
                    selector_declaration_mapping[cur_selector][cur_property] = value.lstrip()
                if token.endswith(";"):
                    cur_property = None
            else:
                cur_selector = f"{cur_selector} {token}" if cur_selector is not None else token
        return selector_declaration_mapping

    @classmethod
    def set_value(cls, widget: QWidget, selector: str, property: str, value: str) -> None:
        qss_str = widget.styleSheet()
        selector_declaration_mapping: QSSMapping = cls.str_to_mapping(qss_str)
        property_value_mapping = selector_declaration_mapping.get(selector, {})
        if isinstance(property_value_mapping, str):
            raise ValueError(f"{selector} is not a valid selector")
        property_value_mapping[property] = value
        selector_declaration_mapping[selector] = property_value_mapping

        widget.setStyleSheet(cls.mapping_to_str(selector_declaration_mapping))
