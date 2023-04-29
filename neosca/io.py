#!/usr/bin/env python3
# -*- coding=utf-8 -*-

try:
    from xml.etree.cElementTree import XML
except ImportError:
    from xml.etree.ElementTree import XML
import logging
import os
import sys
from typing import Optional
import zipfile

from charset_normalizer import detect

from .util import SCAProcedureResult

WORD_NAMESPACE = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
PARA = WORD_NAMESPACE + "p"
TEXT = WORD_NAMESPACE + "t"


class SCAIO:
    def __init__(self) -> None:
        self.previous_encoding = "utf-8"

    def read_docx(self, path) -> str:
        """
        Take the path of a docx file as argument, return the text in unicode.
        This approach does not extract text from tables, headers, and footers.

        https://etienned.github.io/posts/extract-text-from-word-docx-simply/
        """
        document = zipfile.ZipFile(path)
        xml_content = document.read("word/document.xml")
        document.close()
        tree = XML(xml_content)

        paragraphs = []
        for paragraph in tree.iter(PARA):
            text = "".join(node.text for node in paragraph.iter(TEXT) if node.text)
            paragraphs.append(text)
        return "\n".join(paragraphs)

    def read_txt(self, path: str, is_guess_encoding=True) -> str:
        if not is_guess_encoding:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        else:
            try:
                logging.info(
                    f"Attempting to read {path} with {self.previous_encoding} encoding..."
                )
                with open(path, "r", encoding=self.previous_encoding) as f:  # type:ignore
                    content = f.read()
            except ValueError:
                logging.info(f"Attempt failed. Reading {path} in binary mode...")
                with open(path, "rb") as f:
                    bytes_ = f.read()
                logging.info("Guessing the encoding of the byte string...")
                encoding = detect(bytes_)["encoding"]
                if encoding is not None:
                    logging.info(f"Decoding the byte string with {encoding} encoding...")
                    content = bytes_.decode(encoding=encoding)  # type:ignore
                    self.previous_encoding = encoding  # type:ignore
                else:
                    logging.critical(f"Cannot detect encoding for {path}.")
                    sys.exit(1)
        return content

    def read_file(self, path: str) -> str:
        _, ext = os.path.splitext(path)

        if ext == ".txt":
            return self.read_txt(path)
        elif ext == ".docx":
            return self.read_docx(path)
        else:
            raise ValueError("Unexpected file type. Only txt and docx files are supported.")


def try_write(filename: str, content: Optional[str]) -> SCAProcedureResult:
    if not os.path.exists(filename):
        return True, None
    try:
        with open(filename, "w", encoding="utf-8") as f:
            if content is not None:
                f.write(content)
            return True, None
    except PermissionError:
        return (
            False,
            (
                f"PermissionError: can not write to {filename}, because it is already"
                f" in use by another process.\n\n1. Ensure that {filename} is closed,"
                " or \n2. Specify another output filename through the `-o` option,"
                f" e.g. nsca input.txt -o {filename.replace('.csv', '-2.csv')}"
            ),
        )
