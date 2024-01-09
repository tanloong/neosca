#!/usr/bin/env python3

try:
    from xml.etree.ElementTree import XML, fromstring
except ImportError:
    from xml.etree.ElementTree import XML, fromstring
import glob
import json
import logging
import lzma
import os.path as os_path
import pickle
import sys
import zipfile
from os import PathLike
from pathlib import Path
from typing import Any, ByteString, Dict, Iterable, Optional, Sequence, Set, Tuple, Union

from charset_normalizer import detect

from neosca.ns_platform_info import IS_WINDOWS
from neosca.ns_util import Ns_Procedure_Result


class Ns_IO:
    SUPPORTED_EXTENSIONS = ("txt", "docx", "odt")

    DOCX_NAMESPACE = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    DOCX_PARA = DOCX_NAMESPACE + "p"
    DOCX_TEXT = DOCX_NAMESPACE + "t"

    ODT_NAMESPACE = ".//{urn:oasis:names:tc:opendocument:xmlns:text:1.0}"
    ODT_PARA = ODT_NAMESPACE + "p"

    previous_encoding: str = "utf-8"

    @classmethod
    def read_docx(cls, path: str) -> str:
        """
        Take the path of a docx file as argument, return the text in unicode.
        This approach does not extract text from headers and footers.

        https://etienned.github.io/posts/extract-text-from-word-docx-simply/
        """
        with zipfile.ZipFile(path) as zip_file:
            xml_content = zip_file.read("word/document.xml")
        tree = XML(xml_content)

        paragraphs = []
        for paragraph in tree.iter(cls.DOCX_PARA):
            text = "".join(node.text for node in paragraph.iter(cls.DOCX_TEXT) if node.text)
            paragraphs.append(text)
        return "\n".join(paragraphs)

    @classmethod
    def read_odt(cls, path: str) -> str:
        with zipfile.ZipFile(path) as zip_file:
            xml_content = zip_file.read("content.xml")
        root = fromstring(xml_content)
        paragraphs = root.findall(cls.ODT_PARA)
        return "\n".join("".join(node.itertext()) for node in paragraphs)

    @classmethod
    def _read_txt(cls, path: str, mode: str, encoding: Optional[str] = None) -> Union[str, ByteString]:
        try:
            with open(path, mode=mode, encoding=encoding) as f:
                content = f.read()
        # input file existence has already been checked in main.py, here check
        # it again in case users delete input files during runtime
        except FileNotFoundError:
            logging.critical(f"{path} does not exist.")
            sys.exit(1)
        else:
            return content

    @classmethod
    def read_txt(cls, path: str, is_guess_encoding: bool = True) -> Optional[str]:
        if not is_guess_encoding:
            return cls._read_txt(path, "r", "utf-8")  # type:ignore

        try:
            logging.info(f"Attempting to read {path} with {cls.previous_encoding} encoding...")
            content = cls._read_txt(path, "r", cls.previous_encoding)  # type:ignore
        except UnicodeDecodeError:
            logging.info(f"Attempt failed. Reading {path} in binary mode...")
            bytes_ = cls._read_txt(path, "rb")
            logging.info("Guessing the encoding of the byte string...")
            encoding = detect(bytes_)["encoding"]  # type:ignore

            if encoding is None:
                logging.warning(f"{path} is of unsupported file type. Skipped.")
                return None

            cls.previous_encoding = encoding  # type:ignore
            logging.info(f"Decoding the byte string with {encoding} encoding...")
            content = bytes_.decode(encoding=encoding)  # type:ignore

        return content  # type:ignore

    @classmethod
    def suffix(cls, file_path: Union[str, PathLike], strip_dot: bool = False) -> str:
        """
        >>> suffix('my/library/setup.py')
        .py
        >>> suffix('my/library.tar.gz')
        .gz
        >>> suffix('my/library')
        ''
        """
        extension = os_path.splitext(file_path)[-1]
        if strip_dot:
            extension = extension.lstrip(".")
        return extension

    @classmethod
    def read_file(cls, path: str) -> Optional[str]:
        extension = cls.suffix(path, strip_dot=True)
        if extension not in cls.SUPPORTED_EXTENSIONS:
            logging.warning(f"[Ns_IO] {path} is of unsupported filetype. Skipping.")
            return None

        return getattr(cls, f"read_{extension}")(path)

    @classmethod
    def is_writable(cls, filename: str) -> Ns_Procedure_Result:
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

    @classmethod
    def load_pickle_lzma(cls, file_path: Union[str, PathLike]) -> Any:
        if not os_path.isfile(file_path):
            raise FileNotFoundError(f"{file_path} is not an existing file")
        if not str(file_path).endswith((".pickle.lzma", ".pkl.lzma")):
            raise ValueError(
                f"{file_path} does not look like a pickle lzma file as it has neither .pkl.lzma nor .pickle.lzma extension"
            )

        with open(file_path, "rb") as f:
            data_pickle_lzma = f.read()

        data_pickle = lzma.decompress(data_pickle_lzma)
        return pickle.loads(data_pickle)

    @classmethod
    def load_pickle(cls, file_path: Union[str, PathLike]) -> Any:
        if not os_path.isfile(file_path):
            raise FileNotFoundError(f"{file_path} is not an existing file")
        if not str(file_path).endswith((".pkl", ".pickle")):
            raise ValueError(
                f"{file_path} does not look like a pickle file as it has neither .pkl nor .pickle extension"
            )

        with open(file_path, "rb") as f:
            data_pickle = f.read()
        return pickle.loads(data_pickle)

    @classmethod
    def load_lzma(cls, file_path: Union[str, PathLike]) -> bytes:
        if not os_path.isfile(file_path):
            raise FileNotFoundError(f"{file_path} is not an existing file")
        if not str(file_path).endswith(".lzma"):
            raise ValueError(f"{file_path} does not look like a json file because it has no .lzma extension")

        with open(file_path, "rb") as f:
            data_lzma = f.read()
        return lzma.decompress(data_lzma)

    @classmethod
    def load_json(cls, file_path: Union[str, PathLike]) -> Any:
        if not os_path.isfile(file_path):
            raise FileNotFoundError(f"{file_path} is not an existing file")
        if not str(file_path).endswith(".json"):
            raise ValueError(f"{file_path} does not look like a json file because it has no .json extension")

        with open(file_path, "rb") as f:
            return json.load(f)

    @classmethod
    def dump_json(cls, data: Any, json_path: Union[str, PathLike]) -> None:
        with open(json_path, "w") as f:
            json.dump(data, f, ensure_ascii=False)

    @classmethod
    def get_verified_ifile_list(cls, ifile_list: Iterable[str]) -> Set[str]:
        verified_ifile_list = []
        for path in ifile_list:
            if os_path.isfile(path):
                extension = cls.suffix(path)
                if extension not in cls.SUPPORTED_EXTENSIONS:
                    logging.warning(f"[Ns_IO] {path} is of unsupported filetype. Skipping.")
                    continue
                logging.debug(f"[Ns_IO] Adding {path} to input file list")
                verified_ifile_list.append(path)
            elif os_path.isdir(path):
                verified_ifile_list.extend(
                    path
                    for path in glob.glob(f"{path}{os_path.sep}*")
                    if os_path.isfile(path) and cls.suffix(path) in cls.SUPPORTED_EXTENSIONS
                )
            elif glob.glob(path):
                verified_ifile_list.extend(glob.glob(path))
            else:
                logging.critical(f"No such file as\n\n{path}")
                sys.exit(1)
        if IS_WINDOWS:
            verified_ifile_list = [
                path
                for path in verified_ifile_list
                if not (path.endswith(".docx") and os_path.basename(path).startswith("~"))
            ]
        return set(verified_ifile_list)

    @classmethod
    def ensure_unique_filestem(cls, stem: str, existing_stems: Iterable[str]) -> str:
        if stem in existing_stems:
            occurrence = 2
            while f"{stem} ({occurrence})" in existing_stems:
                occurrence += 1
            stem = f"{stem} ({occurrence})"
        return stem


class Ns_Cache:
    from neosca import CACHE_DIR, CACHE_INFO_PATH

    CACHE_EXTENSION = ".pickle.lzma"
    # { "<file_path1>": "<cache_name1>", ... }
    fpath_cname: Dict[str, str] = (
        {} if not os_path.exists(CACHE_INFO_PATH) else Ns_IO.load_json(CACHE_INFO_PATH)
    )

    @classmethod
    def get_cache_path(cls, file_path: str) -> Tuple[str, bool]:
        if not os_path.isfile(file_path):
            raise FileNotFoundError(f"{file_path} is not an existing file")
        if file_path not in cls.fpath_cname:
            cache_path = cls.register_cache_path(file_path)
            return cache_path, False

        cache_path = cls._name2path(cls.fpath_cname[file_path])
        not_exist = not os_path.exists(cache_path)
        outdated = os_path.getmtime(cache_path) <= os_path.getmtime(file_path)
        empty = os_path.getsize(cache_path) == 0
        if not_exist or outdated or empty:
            return cache_path, False

        logging.info(f"Found cache: {cache_path} exists, and is non-empty and newer than {file_path}.")
        return cache_path, True

    @classmethod
    def _stem2name(cls, stem: str) -> str:
        """
        >>> _stem2name("foo")
        foo.pickle.lzma
        """
        return f"{stem}{cls.CACHE_EXTENSION}"

    @classmethod
    def _name2stem(cls, name: str) -> str:
        """
        >>> _name2stem("foo.pickle.lzma")
        foo
        """
        return name.removesuffix(cls.CACHE_EXTENSION)

    @classmethod
    def _name2path(cls, name: str) -> str:
        """
        >>> _name2path("foo.pickle.lzma")
        /path/to/cache_dir/foo.pickle.lzma
        """
        return str(cls.CACHE_DIR / name)

    @classmethod
    def register_cache_path(cls, file_path: str) -> str:
        logging.info(f"Registering cache path for {file_path}...")
        cache_stem = Path(file_path).stem
        cache_stem = Ns_IO.ensure_unique_filestem(cache_stem, map(cls._name2stem, cls.fpath_cname.keys()))
        cache_name = cls._stem2name(cache_stem)
        cls.fpath_cname[file_path] = cache_name
        return cls._name2path(cache_name)

    @classmethod
    def dump_cache_info(cls) -> None:
        logging.info(f"Dumping cache information to {cls.CACHE_INFO_PATH}...")
        Ns_IO.dump_json(cls.fpath_cname, cls.CACHE_INFO_PATH)
