#!/usr/bin/env python3

import glob
import json
import logging
import lzma
import os
import os.path as os_path
import pickle
import sys
import zipfile
from collections.abc import Generator, Iterable, Sequence
from os import PathLike
from pathlib import Path
from typing import Any
from xml.etree.ElementTree import XML, fromstring

from charset_normalizer import detect

from neosca.ns_consts import CACHE_DIR, CACHE_INFO_PATH
from neosca.ns_utils import Ns_Procedure_Result


class Ns_IO_Meta(type):
    def __new__(cls, name, bases, dict_):
        dict_["SUPPORTED_EXTENSIONS"] = tuple(
            attr.removeprefix("read_") for attr in dict_ if attr.startswith("read_")
        )
        return super().__new__(cls, name, bases, dict_)


class Ns_IO(metaclass=Ns_IO_Meta):
    # Type checker does not detect definition in Ns_IO_Meta, so declare here to
    # silence the "access unknown member warning"
    SUPPORTED_EXTENSIONS: tuple[str, ...] = tuple()
    HIDDEN_PREFIXES: tuple[str, ...] = (".", "~$")

    DOCX_NAMESPACE = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    DOCX_PARA = DOCX_NAMESPACE + "p"
    DOCX_TEXT = DOCX_NAMESPACE + "t"

    ODT_NAMESPACE = ".//{urn:oasis:names:tc:opendocument:xmlns:text:1.0}"
    ODT_PARA = ODT_NAMESPACE + "p"

    previous_encoding: str = "utf-8"

    @classmethod
    def read_txt(cls, path: str, is_guess_encoding: bool = True) -> str:
        if not is_guess_encoding:
            with open(path, encoding="utf-8") as f:
                return f.read()

        try:
            logging.info(f"Attempting to read {path} with {cls.previous_encoding} encoding...")
            with open(path, encoding=cls.previous_encoding) as f:
                content = f.read()
        except UnicodeDecodeError:
            logging.info(f"Attempt failed. Guessing the encoding of {path}...")
            with open(path, "rb") as f:
                bytes_ = f.read()

            encoding = detect(bytes_)["encoding"]
            assert isinstance(encoding, str), f"Got invalid encoding for {path}: {encoding}"

            logging.info(f"Decoding the byte string with {encoding} encoding...")
            content = bytes_.decode(encoding=encoding)
            cls.previous_encoding = encoding

        return content

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
    def suffix(cls, file_path: str | PathLike, *, strip_dot: bool = False) -> str:
        """
        >>> suffix('my/library/setup.py')
        .py
        >>> suffix('my/library.tar.gz')
        .gz
        >>> suffix('my/library.tar.gz', strip_dot=True)
        gz
        >>> suffix('my/library')
        ''
        """
        extension = os_path.splitext(file_path)[-1]
        if strip_dot:
            extension = extension.lstrip(".")
        return extension

    @classmethod
    def supports(cls, file_path: str | PathLike) -> bool:
        # Can instead use hasattr(f"read_{extension}").
        # The SUPPORTED_EXTENSIONS is required by ns_main_cli:74 to list
        #  supported extensions to users.
        return cls.suffix(file_path, strip_dot=True) in cls.SUPPORTED_EXTENSIONS

    @classmethod
    def not_supports(cls, file_path: str | PathLike) -> bool:
        return not cls.supports(file_path)

    @classmethod
    def load_file(cls, file_path: str) -> str:
        extension = cls.suffix(file_path, strip_dot=True)
        if extension not in cls.SUPPORTED_EXTENSIONS:
            raise ValueError(f"{file_path} is of unsupported filetype. Skipping.")

        return getattr(cls, f"read_{extension}")(file_path)

    @classmethod
    def is_writable(cls, filename: str) -> Ns_Procedure_Result:
        """Check whether files are opened by other processes such as WPS"""
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
    def _check_file_extension(cls, file_path: str | PathLike, valid_extensions: str | tuple[str, ...]):
        if not os_path.isfile(file_path):
            raise FileNotFoundError(f"File {file_path} does not exist")
        if not str(file_path).endswith(valid_extensions):
            raise ValueError(f"{file_path} does not have a valid extension")

    @classmethod
    def load_pickle_lzma(cls, file_path: str | PathLike) -> Any:
        cls._check_file_extension(file_path, (".pickle.lzma", ".pkl.lzma"))

        with open(file_path, "rb") as f:
            data_pickle_lzma = f.read()

        data_pickle = lzma.decompress(data_pickle_lzma)
        return pickle.loads(data_pickle)

    @classmethod
    def load_pickle(cls, file_path: str | PathLike) -> Any:
        cls._check_file_extension(file_path, (".pickle", ".pkl"))

        with open(file_path, "rb") as f:
            data_pickle = f.read()
        return pickle.loads(data_pickle)

    @classmethod
    def load_lzma(cls, file_path: str | PathLike) -> bytes:
        cls._check_file_extension(file_path, ".lzma")

        with open(file_path, "rb") as f:
            data_lzma = f.read()
        return lzma.decompress(data_lzma)

    @classmethod
    def load_json(cls, file_path: str | PathLike) -> Any:
        cls._check_file_extension(file_path, ".json")

        with open(file_path, "rb") as f:
            return json.load(f)

    @classmethod
    def dump_json(cls, data: Any, path: str | PathLike) -> None:
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except FileNotFoundError:
            Path(path).parent.mkdir(parents=True)
            cls.dump_json(data, path)

    @classmethod
    def dump_bytes(cls, data: bytes, path: str | PathLike) -> None:
        try:
            with open(path, "wb") as f:
                f.write(data)
        except FileNotFoundError:
            Path(path).parent.mkdir(parents=True)
            cls.dump_bytes(data, path)

    @classmethod
    def get_verified_ifile_list(cls, ifile_list: Iterable[str]) -> list[str]:
        verified_ifile_list = []
        for path in ifile_list:
            # File path
            if os_path.isfile(path):
                if cls.not_supports(path):
                    logging.warning(f"{path} is of unsupported filetype. Skipping.")
                    continue
                logging.debug(f"Adding {path} to input file list")
                verified_ifile_list.append(path)
            # Dir path
            elif os_path.isdir(path):
                verified_ifile_list.extend(
                    os_path.join(path, file_name)
                    for file_name in next(os.walk(path))[2]
                    if cls.supports(file_name)
                )
            # Glob pattern
            elif glob.glob(path):
                verified_ifile_list.extend(glob.glob(path))
            else:
                logging.critical(f"No such file as\n\n{path}")
                sys.exit(1)
        verified_ifile_list = [
            path for path in verified_ifile_list if not os_path.basename(path).startswith(cls.HIDDEN_PREFIXES)
        ]
        return verified_ifile_list

    @classmethod
    def get_verified_subfiles_list(cls, subfiles_list: list[list[str]]) -> list[list[str]]:
        verified_subfiles_list = []
        for subfiles in subfiles_list:
            verified_subfiles: list[str] = cls.get_verified_ifile_list(subfiles)
            if len(verified_subfiles) == 1:
                logging.critical(
                    f"Only 1 subfile provided: ({verified_subfiles.pop()}). There should be 2"
                    " or more subfiles to combine."
                )
                sys.exit(1)
            verified_subfiles_list.append(verified_subfiles)
        return verified_subfiles_list

    @classmethod
    def ensure_unique_filestem(cls, stem: str, existing_stems: Sequence[str]) -> str:
        if stem in existing_stems:
            occurrence = 2
            while f"{stem} ({occurrence})" in existing_stems:
                occurrence += 1
            stem = f"{stem} ({occurrence})"
        return stem


class Ns_Cache:
    CACHE_EXTENSION = ".pickle.lzma"
    # fpath_cname: { "/absolute/path/to/foo.txt": "foo.pickle.lzma", ... }
    fpath_cname: dict[str, str] = (
        Ns_IO.load_json(CACHE_INFO_PATH)
        if CACHE_INFO_PATH.exists() and os_path.getsize(CACHE_INFO_PATH) > 0
        else {}
    )
    info_changed: bool = False

    @classmethod
    def get_cache_path(cls, file_path: str) -> tuple[str, bool]:
        """
        return (cache_path, available: whether the cache is usable)
        """
        if not os_path.isfile(file_path):
            raise FileNotFoundError(f"{file_path} is not an existing file")
        cache_name = cls.fpath_cname.get(file_path, None)
        if file_path not in cls.fpath_cname:
            cache_name = cls.register_cache_name(file_path)
            cache_path = cls._name2path(cache_name)
            return cache_path, False

        cache_name = cls.fpath_cname[file_path]
        cache_path = cls._name2path(cache_name)
        if not os_path.exists(cache_path):
            return cache_path, False
        outdated = os_path.getmtime(cache_path) <= os_path.getmtime(file_path)
        if outdated:
            return cache_path, False
        empty = os_path.getsize(cache_path) == 0
        if empty:
            return cache_path, False

        logging.info(f"Found cache: {cache_path} exists, and is non-empty and newer than {file_path}.")
        return cache_path, True

    @classmethod
    def _size_fmt(cls, filesize: int | float, suffix: str = "B") -> str:
        # https://github.com/gaogaotiantian/viztracer/blob/3ecd46aa0e70df7dd78f720a2660d6da211c4a51/src/viztracer/util.py#L12
        for unit in ("", "Ki", "Mi", "Gi"):
            if abs(filesize) < 1024.0:
                return f"{filesize:3.1f} {unit}{suffix}"
            filesize /= 1024.0
        return f"{filesize:.1f} {'Ti'}{suffix}"

    @classmethod
    def yield_cname_cpath_csize_fpath(cls) -> Generator[tuple[str, str, str, str], None, None]:
        for file_path, cache_name in Ns_Cache.fpath_cname.items():
            cache_path = Ns_Cache._name2path(cache_name)
            if not os_path.exists(cache_path):
                continue
            cache_size = cls._size_fmt(os_path.getsize(cache_path))
            yield cache_name, cache_path, cache_size, file_path

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
        return str(CACHE_DIR / name)

    @classmethod
    def _path2name(cls, path: str) -> str:
        """
        >>> _path2name("/path/to/cache_dir/foo.pickle.lzma")
        foo.pickle.lzma
        """
        return os_path.basename(path)

    @classmethod
    def register_cache_name(cls, file_path: str) -> str:
        logging.debug(f"Registering cache path for {file_path}...")
        cache_stem = Path(file_path).stem
        cache_stem = Ns_IO.ensure_unique_filestem(
            cache_stem, tuple(map(cls._name2stem, cls.fpath_cname.values()))
        )
        cache_name = cls._stem2name(cache_stem)
        cls.fpath_cname[file_path] = cache_name
        if not cls.info_changed:
            cls.info_changed = True
        return cache_name

    @classmethod
    def delete_cache_entries(cls, deleted_cache_paths: Iterable[str]) -> None:
        logging.debug(f"Deleting cache entries from {CACHE_INFO_PATH}...")
        deleted_cache_names = tuple(map(cls._path2name, deleted_cache_paths))
        cls.fpath_cname = {k: v for k, v in cls.fpath_cname.items() if v not in deleted_cache_names}
        if not cls.info_changed:
            cls.info_changed = True

    @classmethod
    def save_cache_info(cls) -> None:
        if cls.info_changed:
            logging.debug(f"Saving cache information to {CACHE_INFO_PATH}...")
            Ns_IO.dump_json(cls.fpath_cname, CACHE_INFO_PATH)
        else:
            logging.debug("No new cache information to save.")
