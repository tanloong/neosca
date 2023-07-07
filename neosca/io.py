#!/usr/bin/env python3
# -*- coding=utf-8 -*-

try:
    from xml.etree.cElementTree import XML, fromstring
except ImportError:
    from xml.etree.ElementTree import XML, fromstring
import logging
import os
import sys
from typing import ByteString, Optional, Union
import zipfile

from charset_normalizer import detect

from .util import SCAProcedureResult


class SCAIO:
    DOCX_NAMESPACE = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    DOCX_PARA = DOCX_NAMESPACE + "p"
    DOCX_TEXT = DOCX_NAMESPACE + "t"

    ODT_NAMESPACE = ".//{urn:oasis:names:tc:opendocument:xmlns:text:1.0}"
    ODT_PARA = ODT_NAMESPACE + "p"

    def __init__(self):
        self.ext_read_map = {
            ".txt": self.read_txt,
            ".docx": self.read_docx,
            ".odt": self.read_odt,
        }
        self.previous_encoding = "utf-8"

    def read_docx(self, path: str) -> str:
        """
        Take the path of a docx file as argument, return the text in unicode.
        This approach does not extract text from headers and footers.

        https://etienned.github.io/posts/extract-text-from-word-docx-simply/
        """
        with zipfile.ZipFile(path) as zip_file:
            xml_content = zip_file.read("word/document.xml")
        tree = XML(xml_content)

        paragraphs = []
        for paragraph in tree.iter(self.DOCX_PARA):
            text = "".join(node.text for node in paragraph.iter(self.DOCX_TEXT) if node.text)
            paragraphs.append(text)
        return "\n".join(paragraphs)

    def read_odt(self, path: str) -> str:
        with zipfile.ZipFile(path) as zip_file:
            xml_content = zip_file.read("content.xml")
        root = fromstring(xml_content)
        paragraphs = root.findall(self.ODT_PARA)
        return "\n".join("".join(node.itertext()) for node in paragraphs)

    def _read_txt(
        self, path: str, mode: str, encoding: Optional[str] = None
    ) -> Union[str, ByteString]:
        try:
            with open(path, mode=mode, encoding=encoding) as f:
                content = f.read()
        # input file existence has already been checked before running (main.py: verified_ifile_list),
        # here check it again in case users remove input files during runtime
        except FileNotFoundError:
            logging.critical(f"{path} does not exist.")
            sys.exit(1)
        else:
            return content

    def read_txt(self, path: str, is_guess_encoding=True) -> str:
        if not is_guess_encoding:
            content = self._read_txt(path, "r", "utf-8")
        else:
            try:
                logging.info(
                    f"Attempting to read {path} with {self.previous_encoding} encoding..."
                )
                content = self._read_txt(path, "r", self.previous_encoding)  # type:ignore
            except ValueError:
                logging.info(f"Attempt failed. Reading {path} in binary mode...")
                bytes_ = self._read_txt(path, "rb")
                logging.info("Guessing the encoding of the byte string...")
                encoding = detect(bytes_)["encoding"]  # type:ignore

                if encoding is not None:
                    logging.info(f"Decoding the byte string with {encoding} encoding...")
                    content = bytes_.decode(encoding=encoding)  # type:ignore
                    self.previous_encoding = encoding  # type:ignore
                else:
                    logging.critical(f"{path} is of unsupported file type.")
                    sys.exit(1)
        return content  # type:ignore

    def read_file(self, path: str) -> str:
        _, ext = os.path.splitext(path)
        if ext not in self.ext_read_map:
            ext = (  # assume files with other extensions as .txt files; throw an error from within read_txt() if not so
                ".txt"
            )
        return self.ext_read_map[ext](path)  # type:ignore

    @classmethod
    def try_write(cls, filename: str, content: Optional[str]) -> SCAProcedureResult:
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
