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
from urllib.error import URLError
import zipfile

from .util import SCAProcedureResult

_IS_WINDOWS = os.name == "nt"
_IS_DARWIN = platform == "darwin"
_UNPACK200 = "unpack200.exe" if _IS_WINDOWS else "unpack200"
_UNPACK200_ARGS = '-r -v -l ""' if _IS_WINDOWS else ""
if _IS_WINDOWS and os.environ.get("ProgramFiles") is not None:
    _TARGET_DIR = os.environ.get("ProgramFiles")
else:
    _USER_DIR = path.expanduser("~")
    _TARGET_DIR = path.join(_USER_DIR, ".local", "share")

OS = "windows" if _IS_WINDOWS else "mac" if _IS_DARWIN else platform
ARCH = "x64" if maxsize > 2**32 else "x32"

_TAR = ".tar"
_TAR_GZ = ".tar.gz"
_ZIP = ".zip"
_SEVEN_ZIP = ".7z"

_Path = namedtuple("_Path", "dir base name ext")
JAVA = "Java"
_JAVA_VERSION = "18"
STANFORD_PARSER = "Stanford Parser"
STANFORD_TREGEX = "Stanford Tregex"

_URL_JAVA = "https://www.java.com/en/download"
_URL_STANFORD_PARSER = "https://downloads.cs.stanford.edu/nlp/software/stanford-parser-4.2.0.zip"
_URL_STANFORD_TREGEX = "https://downloads.cs.stanford.edu/nlp/software/stanford-tregex-4.2.0.zip"


class Implementation:
    OPENJ9 = "openj9"
    HOTSPOT = "hotspot"


class depends_installer:
    def normalize_version(self, version: str) -> SCAProcedureResult:
        if re.search(r"^\d+$", version):
            return True, version
        else:
            match = re.search(r"^\d+\.(\d+)$", version)
            if match:
                return True, match.group(1)
            else:
                return False, f"Error: Unexpected version format: {version}."

    def get_java_download_url(
        self,
        version: str,
        operating_system: Optional[str] = None,
        arch: Optional[str] = None,
        impl: str = Implementation.HOTSPOT,
    ) -> SCAProcedureResult:
        sucess, err_msg = self.normalize_version(version)
        if not sucess:
            return sucess, err_msg
        else:
            version = err_msg  # type:ignore
        url_template = "https://api.adoptopenjdk.net/v3/binary/latest/{}/ga/{}/{}/jdk/{}/normal/adoptopenjdk"
        return True, url_template.format(version, operating_system, arch, impl)

    def _get_normalized_archive_ext(self, file: str) -> SCAProcedureResult:
        if file.endswith(_TAR):
            return True, _TAR
        elif file.endswith(_TAR_GZ):
            return True, _TAR_GZ
        elif file.endswith(_ZIP):
            return True, _ZIP
        elif file.endswith(_SEVEN_ZIP):
            return True, _SEVEN_ZIP
        else:
            return False, f"Error: {file} has unexpected extension."

    def _extract_files(self, file: str, file_ending: str, destination_folder: str) -> SCAProcedureResult:
        if not path.isfile(file):
            return False, f"Error: {file} is not a regular file."

        start_listing = set(os.listdir(destination_folder))

        if file_ending == _TAR:
            with tarfile.open(file, "r:") as tar:
                tar.extractall(path=destination_folder)
        elif file_ending == _TAR_GZ:
            with tarfile.open(file, "r:gz") as tar:
                tar.extractall(path=destination_folder)
        elif file_ending == _ZIP:
            with zipfile.ZipFile(file, "r") as z:
                z.extractall(path=destination_folder)
        elif file_ending == _SEVEN_ZIP:
            with lzma.open(file, "rb") as z:
                with open(destination_folder, "wb") as destination:
                    shutil.copyfileobj(z, destination)

        end_listing = set(os.listdir(destination_folder))
        unzipped_directory = end_listing.difference(start_listing).pop()

        return True, path.join(destination_folder, unzipped_directory)

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
            file_ext = path.splitext(fs_path)[-1]
            if file_ext.endswith("pack"):
                p = self._path_parse(fs_path)
                name = path.join(p.dir, p.name)
                tool_path = path.join(java_bin_path, _UNPACK200)
                run([tool_path, _UNPACK200_ARGS, f"{name}.pack", f"{name}.jar"])
            return True, None
        else:
            return False, f"Error: {fs_path} is neither a directory not a file."

    def _decompress_archive(
        self, archive_path: str, file_ending: str, destination_folder: str
    ) -> SCAProcedureResult:
        if not path.isdir(destination_folder):
            os.mkdir(destination_folder)

        archive_path = path.normpath(archive_path)

        if path.isfile(archive_path):
            sucess, err_msg = self._extract_files(archive_path, file_ending, destination_folder)
            if not sucess:
                return sucess, err_msg
            else:
                unzipped_directory = err_msg
            return True, unzipped_directory
        elif path.isdir(archive_path):
            return True, archive_path
        else:
            return False, f"Error: {archive_path} is neither a directory not a file."

    def _get_java_filename(self, response) -> SCAProcedureResult:
        info = response.info()
        download_url = response.geturl()
        if "Content-Disposition" not in info:
            return (
                False,
                f"Parsing the response from {download_url} failed. \nReason:"
                ' "Content-Disposition" not in response.info().',
            )
        m = email.message.Message()
        m["content-type"] = info["Content-Disposition"]
        if m.get_param("filename") is None:
            return (
                False,
                f"Parsing the response from {download_url} failed.\nReason: can't detect the filename.",
            )
        filename = m.get_param("filename")
        if not isinstance(filename, str):
            return (
                False,
                f"Parsing the response from {download_url} failed.\nReason: the value of"
                ' the attribute "filename" is not a str.',
            )
        return True, filename

    def _download(self, download_url:str, name:str) -> SCAProcedureResult:
        req = request.Request(download_url, headers={"User-Agent": "Mozilla/5.0"})

        filename = None
        try:
            response = request.urlopen(req)
        except URLError as e:
            if hasattr(e, "reason"):
                return (False, f"Requesting to {download_url} failed.\nReason: {e.reason}")
            elif hasattr(e, "code"):
                return (False, f"Requesting to {download_url} failed.\nReason: {e.code}")
            else:
                return False, f"Requesting to {download_url} failed."
        else:
            if name == JAVA:
                success, err_msg = self._get_java_filename(response)
                if not success:
                    return success, err_msg
                else:
                    filename = err_msg  # e.g., jdk-18.0.2
            else:
                filename = path.basename(download_url)
                # e.g. stanford-tregex-4.2.0.zip, stanford-parser-4.2.0.zip
            filename = path.join(tempfile.gettempdir(), filename)  # type: ignore
            with open(filename, "wb") as out_file:
                shutil.copyfileobj(response, out_file)
            return True, filename

    def ask_install(self, name: str) -> SCAProcedureResult:
        is_install = input(
            f"It seems that {name} has not been installed on your device. Do you want to let"
            " NeoSCA install it for you?\nEnter [y]es or [n]o: "
        )
        while is_install not in ("y", "n", "Y", "N"):
            is_install = input(f"Unexpected input: {is_install}.\nEnter [y]es or [n]o: ")
        if is_install in ("n", "N"):
            prompt_dict = {
                JAVA: (
                    f"You will have to install {JAVA} manually.\n\n1. To install it, visit"
                    f" {_URL_JAVA}.\n2. After installing, make sure you can access it in the cmd"
                    " window by typing in `java -version`."
                ),
                STANFORD_PARSER: (
                    f"You will have to install {STANFORD_PARSER} manually.\n\n1. To install it,"
                    f" download and unzip the archive file at {_URL_STANFORD_PARSER}.\n2. Set an"
                    " environment variable STANFORD_PARSER_HOME to the path of the unzipped"
                    " directory."
                ),
                STANFORD_TREGEX: (
                    f"You will have to install {STANFORD_TREGEX} manually.\n\n1. To install it,"
                    f" download and unzip the archive file at {_URL_STANFORD_TREGEX}.\n2. Set an"
                    " environment variable STANFORD_PARSER_HOME to the path of the unzipped"
                    " directory."
                ),
            }
            return (False, prompt_dict[name])
        else:
            return True, None

    def install_java(
        self,
        version: str,
        operating_system: str,
        arch: str,
        impl: str,
        target_dir: str,
    ) -> SCAProcedureResult:
        match = glob.glob(f"{target_dir}{os.sep}jdk-{version}*{os.sep}bin")
        if match:
            return True, match[0]
        sucess, err_msg = self.ask_install(JAVA)
        if not sucess:
            return sucess, err_msg
        print(
            f'Installing {JAVA} {version} to "{target_dir}". It can take a few minutes, depending'
            " on your network connection."
        )
        sucess, err_msg = self.get_java_download_url(version, operating_system, arch, impl)
        if not sucess:
            return sucess, err_msg
        else:
            url = err_msg
        print(f"Downloading the {JAVA} archive from {url}...")
        sucess, err_msg = self._download(url, name=JAVA) # type:ignore
        if not sucess:
            return sucess, err_msg
        jdk_archive = err_msg
        sucess, err_msg = self._get_normalized_archive_ext(jdk_archive)  # type:ignore
        if not sucess:
            return sucess, err_msg
        jdk_ext = err_msg
        print(f"Decompressing {JAVA} archive...")
        sucess, err_msg = self._decompress_archive(jdk_archive, jdk_ext, target_dir)  # type:ignore
        if not sucess:
            return sucess, err_msg
        jdk_dir = err_msg
        jdk_bin = target_dir.join(jdk_dir, "bin")  # type:ignore
        sucess, err_msg = self._unpack_jars(jdk_dir, jdk_bin)  # type:ignore
        if not sucess:
            return sucess, err_msg
        if jdk_archive:
            os.remove(jdk_archive)
        return True, jdk_bin

    def install_stanford(self, name: str, url: str, target_dir: str) -> SCAProcedureResult:
        match = glob.glob(f"{target_dir}{os.sep}{name.lower().replace(' ', '-')}*")
        if match:
            return True, match[0]
        sucess, err_msg = self.ask_install(name)
        if not sucess:
            return sucess, err_msg
        print(
            f'Installing {name} to "{target_dir}". It can take a few minutes, depending'
            f" on your network connection.\nDownloading the {name} archive from {url}."
        )
        sucess, err_msg = self._download(url, name=name)
        if not sucess:
            return sucess, err_msg
        archive_file = err_msg
        sucess, err_msg = self._get_normalized_archive_ext(archive_file)  # type:ignore
        if not sucess:
            return sucess, err_msg
        archive_ext = err_msg
        print(f"Decompressing {name} archive...")
        sucess, err_msg = self._decompress_archive(archive_file, archive_ext, target_dir)  # type:ignore
        if not sucess:
            return sucess, err_msg
        unzipped_directory = err_msg
        if archive_file:
            os.remove(archive_file)
        return True, unzipped_directory

    def install(
        self,
        name: str,
        version: str = _JAVA_VERSION,
        operating_system: str = OS,
        arch: str = ARCH,
        impl: str = Implementation.HOTSPOT,
        target_dir: str = _TARGET_DIR,  # type: ignore
    ) -> SCAProcedureResult:
        if name == JAVA:
            return self.install_java(version, operating_system, arch, impl, target_dir)
        elif name == STANFORD_PARSER:
            return self.install_stanford(name, _URL_STANFORD_PARSER, target_dir)
        elif name == STANFORD_TREGEX:
            return self.install_stanford(name, _URL_STANFORD_TREGEX, target_dir)
        else:
            return False, f"Unexpected name: {name}."
