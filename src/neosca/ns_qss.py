#!/usr/bin/env python3

import os.path as os_path
import re
from os import PathLike
from typing import Any, Dict, Optional, Union

from PyQt5.QtWidgets import QWidget

QSSMapping = Dict[str, Union[str, Dict[str, str]]]


class Ns_QSS:
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
    def get_value(qss: str, selector: str, property: str) -> Optional[str]:
        """Requires that every value ends with ";".
        >>> qss = "QHeaderView::section:horizontal { background-color: #5C88C5; }"
        >>> get_value(qss, "QHeaderView::section:horizontal", "background-color")
        #5C88C5
        """
        selector = re.escape(selector)
        property = re.escape(property)

        # Note that only value of the 1st matched selector returned
        matched_selector = re.search(rf"{selector}[ }}]", qss)
        if matched_selector is None:
            return None
        matched_value = re.search(rf"[^}}]+{property}:\s*([^;]+);", qss[matched_selector.end() :])
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
            (2) The trailing ";" be attached to the value and, if any,
                separated from the subsequent next property token
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
        # selector_declaration_mapping = {}
        sel_dec_mapping: QSSMapping = {}
        curr_selector = None
        curr_property = None
        qss_str = qss_str.replace("{", " { ").replace("}", " } ")
        token_gen = iter(qss_str.split())
        while (token := next(token_gen, None)) is not None:
            if token == "{":  # }
                pass
            elif token == "}":
                curr_selector = None
            elif token.endswith(":"):
                curr_property = token.rstrip(":")
            elif curr_property is not None:
                if curr_selector is None:
                    value_prev = sel_dec_mapping.get(curr_property, "")
                    value = f"{value_prev} {token}" if not value_prev.endswith(";") else token  # type: ignore
                    sel_dec_mapping[curr_property] = value.lstrip()
                else:
                    if curr_selector not in sel_dec_mapping:
                        sel_dec_mapping[curr_selector] = {}
                    value_prev = sel_dec_mapping[curr_selector].get(curr_property, "")  # type: ignore
                    value = f"{value_prev} {token}" if not value_prev.endswith(";") else token
                    sel_dec_mapping[curr_selector][curr_property] = value.lstrip()  # type: ignore
                if token.endswith(";"):
                    curr_property = None
            else:
                curr_selector = f"{curr_selector} {token}" if curr_selector is not None else token
        return sel_dec_mapping

    @classmethod
    def update(cls, widget: QWidget, new_qss_mapping: Dict[str, Dict[str, str]]) -> None:
        qss_str = widget.styleSheet()
        selector_declaration_mapping: QSSMapping = cls.str_to_mapping(qss_str)
        selector_declaration_mapping.update(new_qss_mapping)
        widget.setStyleSheet(cls.mapping_to_str(selector_declaration_mapping))
