from collections import namedtuple
import email.message
import glob
import lzma
import os
from os import path
import re
import shutil
from subprocess import run
from sys import maxsize, platform
import tarfile
import tempfile
from typing import Optional
from urllib import request
import zipfile

from .util import SCAProcedureResult

_Path = namedtuple("_Path", "dir base name ext")


class Implementation:
    OPENJ9 = "openj9"
    HOTSPOT = "hotspot"


class java_installer:
    def __init__(self):
        self._IS_WINDOWS = os.name == "nt"
        self._IS_DARWIN = platform == "darwin"
        self._UNPACK200 = "unpack200.exe" if self._IS_WINDOWS else "unpack200"
        self._UNPACK200_ARGS = '-r -v -l ""' if self._IS_WINDOWS else ""
        self._USER_DIR = path.expanduser("~")
        self._JDK_DIR = path.join(self._USER_DIR, ".jdk")

        self.OS = "windows" if self._IS_WINDOWS else "mac" if self._IS_DARWIN else platform
        self.ARCH = "x64" if maxsize > 2**32 else "x32"

        self._TAR = ".tar"
        self._TAR_GZ = ".tar.gz"
        self._ZIP = ".zip"
        self._SEVEN_ZIP = ".7z"

    def normalize_version(self, version: str) -> SCAProcedureResult:
        if re.search(r"^\d+$", version):
            return True, version
        else:
            match = re.search(r"^\d+\.(\d+)$", version)
            if match:
                return True, match.group(1)
            else:
                return False, f"Error: Unexpected version format: {version}."

    def get_download_url(
        self,
        version: str,
        operating_system: Optional[str] = None,
        arch: Optional[str] = None,
        impl: str = Implementation.HOTSPOT,
    ) -> str:
        if operating_system is None:
            operating_system = self.OS
        if arch is None:
            arch = self.ARCH
        url_template = (
            "https://api.adoptopenjdk.net/v3/binary/latest/{}/ga/{}/{}/jdk/{}/normal/adoptopenjdk"
        )
        return url_template.format(version, operating_system, arch, impl)

    def _get_normalized_archive_ext(self, file: str) -> SCAProcedureResult:
        if file.endswith(self._TAR):
            return True, self._TAR
        elif file.endswith(self._TAR_GZ):
            return True, self._TAR_GZ
        elif file.endswith(self._ZIP):
            return True, self._ZIP
        elif file.endswith(self._SEVEN_ZIP):
            return True, self._SEVEN_ZIP
        else:
            return False, f"Error: {file} has unexpected extension."

    def _extract_files(
        self, file: str, file_ending: str, destination_folder: str
    ) -> SCAProcedureResult:
        if not path.isfile(file):
            return False, f"Error: {file} is not a regular file."

        start_listing = set(os.listdir(destination_folder))

        if file_ending == self._TAR:
            with tarfile.open(file, "r:") as tar:
                tar.extractall(path=destination_folder)
        elif file_ending == self._TAR_GZ:
            with tarfile.open(file, "r:gz") as tar:
                tar.extractall(path=destination_folder)
        elif file_ending == self._ZIP:
            with zipfile.ZipFile(file, "r") as z:
                z.extractall(path=destination_folder)
        elif file_ending == self._SEVEN_ZIP:
            with lzma.open(file, "rb") as z:
                with open(destination_folder, "wb") as destination:
                    shutil.copyfileobj(z, destination)

        end_listing = set(os.listdir(destination_folder))
        jdk_directory = next(iter(end_listing.difference(start_listing)))

        return True, path.join(destination_folder, jdk_directory)

    def _path_parse(self, file_path: str) -> _Path:
        dirname = path.dirname(file_path)
        base = path.basename(file_path)
        name, ext = path.splitext(base)
        return _Path(dir=dirname, base=base, name=name, ext=ext)

    def _unpack_jars(self, fs_path: str, java_bin_path: str) -> SCAProcedureResult:
        if path.isdir(fs_path):
            for f in os.listdir(fs_path):
                current_path = path.join(fs_path, f)
                self._unpack_jars(current_path, java_bin_path)
            return True, None
        elif path.isfile(fs_path):
            file_name, file_ext = path.splitext(fs_path)
            if file_ext.endswith("pack"):
                p = self._path_parse(fs_path)
                name = path.join(p.dir, p.name)
                tool_path = path.join(java_bin_path, self._UNPACK200)
                run([tool_path, self._UNPACK200_ARGS, f"{name}.pack", f"{name}.jar"])
            return True, None
        else:
            return False, f"Error: {fs_path} is neither a directory not a file."

    def _decompress_archive(
        self, repo_root: str, file_ending: str, destination_folder: str
    ) -> SCAProcedureResult:
        if not path.isdir(destination_folder):
            os.mkdir(destination_folder)

        jdk_file = path.normpath(repo_root)

        if path.isfile(jdk_file):
            sucess, err_msg = self._extract_files(jdk_file, file_ending, destination_folder)
            if not sucess:
                return sucess, err_msg
            else:
                jdk_directory = err_msg
            jdk_bin = path.join(jdk_directory, "bin")  # type:ignore
            sucess, err_msg = self._unpack_jars(jdk_directory, jdk_bin)  # type:ignore
            if not sucess:
                return sucess, err_msg

            return True, jdk_directory
        elif path.isdir(jdk_file):
            return True, jdk_file
        else:
            return False, f"Error: {jdk_file} is neither a directory not a file."

    def _download(self, download_url) -> SCAProcedureResult:
        req = request.Request(download_url, headers={"User-Agent": "Mozilla/5.0"})

        jdk_file = None
        with request.urlopen(req) as open_request:
            info = open_request.info()
            if "Content-Disposition" in info:
                m = email.message.Message()
                m["content-type"] = info["Content-Disposition"]
                if m.get_param("filename") is not None:
                    jdk_file = m.get_param("filename")
                    if not isinstance(jdk_file, str):
                        return (
                            False,
                            f"Error: failed to parse response from {download_url}.",
                        )
                    jdk_file = path.join(tempfile.gettempdir(), jdk_file)
                    with open(jdk_file, "wb") as out_file:
                        shutil.copyfileobj(open_request, out_file)
        if jdk_file is None:
            return False, f"Error: connection to {download_url} failed."
        else:
            return True, jdk_file

    def ask_install(self) -> SCAProcedureResult:
        is_install_java = input(
            "Java not detected. Do you want to let NeoSCA install Java for you? (y/n) "
        )
        if is_install_java.lower() == "n":
            return (
                False,
                "You will have to install Java manually.\n\nTo install it, visit"
                " https://www.java.com/en/download.\n2. After installing, make sure you can"
                " access it in the cmd window by typing in `java -version`.",
            )
        elif is_install_java.lower() != "y":
            return (
                False,
                f"Unexpected input: {is_install_java}. You will have to install Java"
                " manually.\n\nTo install it, visit https://www.java.com/en/download.\n2."
                " After installing, make sure you can access it in the cmd window by typing"
                " in `java -version`.",
            )
        else:
            return True, None

    def install(
        self,
        version: str,
        operating_system: Optional[str] = None,
        arch: Optional[str] = None,
        impl: str = Implementation.HOTSPOT,
        path: Optional[str] = None,
    ) -> SCAProcedureResult:
        if operating_system is None:
            operating_system = self.OS
        if arch is None:
            arch = self.ARCH
        sucess, err_msg = self.normalize_version(version)
        if not sucess:
            return sucess, err_msg
        else:
            version = err_msg  # type:ignore
        url = self.get_download_url(version, operating_system, arch, impl)

        if not path:
            path = self._JDK_DIR
        match = glob.glob(f"{path}{os.sep}jdk-{version}*{os.sep}bin")
        if match:
            return True, match[0]

        sucess, err_msg = self.ask_install()
        if not sucess:
            return sucess, err_msg
        print(
            f"Installing Java {version} to {path}. It can take a few minutes, depending on"
            " your network connection."
        )

        jdk_file = None
        try:
            print(f"Downloading Java archive from {url}...")
            sucess, err_msg = self._download(url)
            if not sucess:
                return sucess, err_msg
            jdk_file = err_msg
            sucess, err_msg = self._get_normalized_archive_ext(jdk_file)  # type:ignore
            if not sucess:
                return sucess, err_msg
            jdk_ext = err_msg
            print(f"Decompressing Java archive...")
            sucess, err_msg = self._decompress_archive(jdk_file, jdk_ext, path)  # type:ignore
            if not sucess:
                return sucess, err_msg
            jdk_dir = err_msg

            return True, f"{jdk_dir}{os.sep}bin"
        finally:
            if jdk_file:
                os.remove(jdk_file)
