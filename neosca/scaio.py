#!/usr/bin/env python3
# -*- coding=utf-8 -*-

try:
    from xml.etree.cElementTree import XML, fromstring
except ImportError:
    from xml.etree.ElementTree import XML, fromstring
import glob
import logging
import os.path as os_path
import sys
from typing import ByteString, Callable, Dict, List, Optional, Union
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
        self.ext_read_map: Dict[str, Callable] = {
            "txt": self.read_txt,
            "docx": self.read_docx,
            "odt": self.read_odt,
        }
        # .parsed files, along with other types of files, should be explicitly
        # checked and excluded, because they are text files and self.read_txt can
        # only exclude non-text files
        self.extensions_to_exclude: tuple = (
            "parsed",
            "prd",
            "csv",
            "tsv",
            "xml",
            "json",
            "md",
            "yml",
            "toml",
            "html",
            "htm",
            "svg",
            "cfg",
            "conf",
            "log",
            "png",
            "jpg",
            "gif",
            "ini",
            "rtf",
            "bat",
            "sh",
            "py",
            "r",
            "R",
            "h",
            "java",
            "cpp",
            "sql",
            "textile",
            "srt",
            "tex",
        )
        self.previous_encoding: str = "utf-8"

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
        # input file existence has already been checked in main.py, here check
        # it again in case users remove input files during runtime
        except FileNotFoundError:
            logging.critical(f"{path} does not exist.")
            sys.exit(1)
        else:
            return content

    def read_txt(self, path: str, is_guess_encoding: bool = True) -> Optional[str]:
        if not is_guess_encoding:
            return self._read_txt(path, "r", "utf-8")  # type:ignore

        try:
            logging.info(f"Attempting to read {path} with {self.previous_encoding} encoding...")
            content = self._read_txt(path, "r", self.previous_encoding)  # type:ignore
        except UnicodeDecodeError:
            logging.info(f"Attempt failed. Reading {path} in binary mode...")
            bytes_ = self._read_txt(path, "rb")
            logging.info("Guessing the encoding of the byte string...")
            encoding = detect(bytes_)["encoding"]  # type:ignore

            if encoding is None:
                logging.warning(f"{path} is of unsupported file type. Skipped.")
                return None

            self.previous_encoding = encoding  # type:ignore
            logging.info(f"Decoding the byte string with {encoding} encoding...")
            content = bytes_.decode(encoding=encoding)  # type:ignore

        return content  # type:ignore

    def _is_to_exclude(self, path: str) -> bool:
        *_, ext = path.split(".")
        if ext in self.extensions_to_exclude:
            return True
        return False

    def read_file(self, path: str) -> Optional[str]:
        if self._is_to_exclude(path):
            logging.warning(f"[SCAIO] {path} does not appear to be an input file. Skipping.")
            return None

        *_, ext = path.split(".")
        if ext not in self.ext_read_map:
            # assume files with other extensions as text files; if not so,
            # read_txt() will fail and log them and return None
            ext = "txt"
        return self.ext_read_map[ext](path)  # type:ignore

    @classmethod
    def is_writable(cls, filename: str) -> SCAProcedureResult:
        """check whether files are opened by such other processes as WPS"""
        if not os_path.exists(filename):
            return True, None
        try:
            with open(filename, "w", encoding="utf-8"):
                pass
        except PermissionError:
            return (
                False,
                (
                    f"PermissionError: can not write to {filename}, because it is already in use"
                    " by another process.\n\n1. Ensure that {filename} is closed, or \n2."
                    " Specify another output filename through the `-o` option, e.g. nsca"
                    f" input.txt -o {filename.replace('.csv', '-2.csv')}"
                ),
            )
        else:
            return True, None

    def load_pickle_lzma_file(self, filepath: str) -> dict:
        import lzma
        import pickle

        with open(filepath, "rb") as f:
            data_pickle_lzma = f.read()

        data_pickle = lzma.decompress(data_pickle_lzma)
        data = pickle.loads(data_pickle)

        return data

    def get_verified_ifile_list(self, ifile_list: List[str]) -> List[str]:
        verified_ifile_list = []
        for path in ifile_list:
            if os_path.isfile(path):
                if self._is_to_exclude(path):
                    logging.warning(
                        f"[SCAIO] {path} does not appear to be an input file. Skipping."
                    )
                    continue
                logging.debug(f"[SCAIO] Adding {path} to input file list")
                verified_ifile_list.append(path)
            elif os_path.isdir(path):
                verified_ifile_list.extend(
                    path
                    for path in glob.glob(f"{path}{os_path.sep}*")
                    if not self._is_to_exclude(path)
                )
            elif glob.glob(path):
                verified_ifile_list.extend(glob.glob(path))
            else:
                logging.critical(f"No such file as\n\n{path}")
                sys.exit(1)
        return verified_ifile_list
