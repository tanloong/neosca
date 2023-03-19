from collections import namedtuple
import email.message
import glob
import logging
import lzma
import os
import re
import shutil
import subprocess
from sys import maxsize, platform
import tarfile
import tempfile
from typing import Optional, Union
from urllib.error import URLError
import urllib.parse
import urllib.request
import zipfile

from .util import SCAProcedureResult
from .util_platform_info import IS_DARWIN, IS_WINDOWS
from .util_platform_info import USER_SOFTWARE_DIR
from .util_print import same_line_print
from .util_print import get_yes_or_no

_UNPACK200 = "unpack200.exe" if IS_WINDOWS else "unpack200"
_UNPACK200_ARGS = '-r -v -l ""' if IS_WINDOWS else ""

OS = "windows" if IS_WINDOWS else "mac" if IS_DARWIN else platform
ARCH = "x64" if maxsize > 2**32 else "x32"

_TAR = ".tar"
_TAR_GZ = ".tar.gz"
_ZIP = ".zip"
_SEVEN_ZIP = ".7z"

_Path = namedtuple("_Path", "dir base name ext")
JAVA = "Java"
_JAVA_VERSION = "8"
STANFORD_PARSER = "Stanford Parser"
STANFORD_TREGEX = "Stanford Tregex"


class Implementation:
    OPENJ9 = "openj9"
    HOTSPOT = "hotspot"


class depends_installer:
    def __init__(self) -> None:
        self._URL_JAVA_TEMPLATE = (
            "https://api.adoptopenjdk.net/v3/binary/latest/"
            "{}/ga/{}/{}/jdk/{}/normal/adoptopenjdk"
        )
        self._URL_JAVA_TEMPLATE_CHINA = (
            "https://mirrors.tuna.tsinghua.edu.cn/Adoptium/{}/jdk/{}/{}/"
        )
        self._URL_STANFORD_PARSER = (
            "https://downloads.cs.stanford.edu/nlp/software/stanford-parser-4.2.0.zip"
        )
        self._URL_STANFORD_TREGEX = (
            "https://downloads.cs.stanford.edu/nlp/software/stanford-tregex-4.2.0.zip"
        )
        self.headers = {"User-Agent": "Mozilla/5.0"}

    def normalize_version(self, version: str) -> SCAProcedureResult:
        if re.search(r"^\d+$", version):
            return True, version
        match = re.search(r"^\d+\.(\d+)$", version)
        if match:
            return True, match.group(1)
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
        self.is_use_chinese_jdk_mirror = get_yes_or_no(
            "Do you want to download Java from a Chinese mirror site? If you are inside of"
            " China, you may want to use this for a faster network connection."
        )
        if self.is_use_chinese_jdk_mirror in ("n", "N"):
            return True, self._URL_JAVA_TEMPLATE.format(version, operating_system, arch, impl)
        else:
            index_url = self._URL_JAVA_TEMPLATE_CHINA.format(version, arch, operating_system)
            req = urllib.request.Request(index_url, headers=self.headers)
            response = urllib.request.urlopen(req)
            content = response.read().decode("utf-8")
            match = re.search(r'"([^"]+\.(?:zip|tar\.gz|tar|7z))"', content)
            if match:
                filename = match.group(1)
                return True, urllib.parse.urljoin(index_url, filename)
            else:
                return (
                    False,
                    "Failed to find any archive file (*.zip, *.tar.gz, *.tar, or *.7z) at"
                    f" {index_url}.",
                )

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

    def _extract_files(
        self, file: str, file_ending: str, destination_folder: str
    ) -> SCAProcedureResult:
        if not os.path.isfile(file):
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

        return True, os.path.join(destination_folder, unzipped_directory)

    def _path_parse(self, file_path: str) -> _Path:
        dirname = os.path.dirname(file_path)
        base = os.path.basename(file_path)
        name, ext = os.path.splitext(base)
        return _Path(dir=dirname, base=base, name=name, ext=ext)

    def _unpack_jars(self, fs_path: str, java_bin_path: str) -> SCAProcedureResult:
        if os.path.isdir(fs_path):
            for f in os.listdir(fs_path):
                current_path = os.path.join(fs_path, f)
                self._unpack_jars(current_path, java_bin_path)
            return True, None
        elif os.path.isfile(fs_path):
            file_ext = os.path.splitext(fs_path)[-1]
            if file_ext.endswith("pack"):
                p = self._path_parse(fs_path)
                name = os.path.join(p.dir, p.name)
                tool_path = os.path.join(java_bin_path, _UNPACK200)
                try:
                    subprocess.run(
                        [tool_path, _UNPACK200_ARGS, f"{name}.pack", f"{name}.jar"],
                        check=True,
                        capture_output=True,
                    )
                except (FileNotFoundError, subprocess.CalledProcessError) as e:
                    return False, str(e)
            return True, None
        else:
            return False, f"Error: {fs_path} is neither a directory not a file."

    def _decompress_archive(
        self, archive_path: str, file_extension: str, target_dir: str
    ) -> SCAProcedureResult:
        logging.info(f"Decompressing {archive_path} to {target_dir}...")
        if not os.path.isdir(target_dir):
            os.makedirs(target_dir)

        archive_path = os.path.normpath(archive_path)

        if os.path.isfile(archive_path):
            sucess, err_msg = self._extract_files(archive_path, file_extension, target_dir)
            if not sucess:
                return sucess, err_msg
            else:
                unzipped_directory = err_msg
            return True, unzipped_directory
        elif os.path.isdir(archive_path):
            return True, archive_path
        else:
            return False, f"Error: {archive_path} is neither a directory not a file."

    def _get_java_filename(self, download_url) -> SCAProcedureResult:
        if self.is_use_chinese_jdk_mirror:
            filename = urllib.parse.urlparse(download_url).path.rpartition("/")[-1]
        else:
            req = urllib.request.Request(download_url, headers=self.headers)
            response = urllib.request.urlopen(req)
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
                    f"Parsing the response from {download_url} failed.\nReason: can't detect"
                    " the filename.",
                )
            filename = m.get_param("filename")
            if not isinstance(filename, str):
                return (
                    False,
                    f"Parsing the response from {download_url} failed.\nReason: the value of"
                    ' the attribute "filename" is not a str.',
                )
        return True, filename

    def _format_bytes(self, size: Union[int, float], precesion: int = 2):
        power = 2**10  # 1024
        n = 0
        power_labels = {0: "", 1: "K", 2: "M", 3: "G", 4: "T"}
        while size > power:
            size /= power
            n += 1
        return round(size, precesion), f"{power_labels[n]}"

    def _callbackfunc(self, block_num: int, block_size: int, total_size):
        max_euqal_sign_num = 50  # print up to 50 hashes
        precesion = 2
        downloaded_size = block_num * block_size
        if downloaded_size >= total_size:
            downloaded_size = total_size
        percent = int(100 * downloaded_size / total_size)
        downloaded_size, downloaded_size_unit = self._format_bytes(downloaded_size, precesion)
        total_size, total_size_unit = self._format_bytes(total_size, precesion)
        equal_sign_num = int(percent / 100 * max_euqal_sign_num)
        s = (
            f"{percent:3}% [{'=' * equal_sign_num}>{' '*(max_euqal_sign_num-equal_sign_num-1)}]"
            f" {downloaded_size:6} {downloaded_size_unit}/{total_size} {total_size_unit}"
        )
        same_line_print(s, width=100)

    def _download(self, download_url: str, name: str) -> SCAProcedureResult:
        logging.info(f"Downloading {download_url}...")
        if name == JAVA:
            success, err_msg = self._get_java_filename(download_url)
            if not success:
                return success, err_msg
            else:
                filename = err_msg  # e.g., jdk-18.0.2
        else:
            filename = urllib.parse.urlparse(download_url).path.rpartition("/")[-1]
            # e.g. stanford-tregex-4.2.0.zip, stanford-parser-4.2.0.zip
        filename = os.path.join(tempfile.gettempdir(), filename)  # type: ignore
        try:
            opener = urllib.request.build_opener()
            opener.addheaders = list(self.headers.items())
            urllib.request.install_opener(opener)
            urllib.request.urlretrieve(download_url, filename, self._callbackfunc)
            same_line_print("", width=100)
        except URLError as e:
            if hasattr(e, "reason"):
                return (False, f"Requesting to {download_url} failed.\nReason: {e.reason}")
            elif hasattr(e, "code"):
                return (False, f"Requesting to {download_url} failed.\nReason: {e.code}")
            else:
                return False, f"Requesting to {download_url} failed."
        return True, filename

    def ask_install(self, name: str, is_assume_yes: bool = False) -> SCAProcedureResult:
        reason_dict = {
            JAVA: f"values of PATH does not include a {JAVA} bin folder",
            STANFORD_PARSER: (
                "the environment variable STANFORD_PARSER_HOME is not found or its value is not"
                " an existing directory"
            ),
            STANFORD_TREGEX: (
                "the environment variable STANFORD_TREGEX_HOME is not found or its value is not"
                " an existing directory"
            ),
        }
        if is_assume_yes:
            is_install = "y"
        else:
            is_install = get_yes_or_no(
                f"It seems that {name} has not been installed, because {reason_dict[name]}. Do"
                " you want to let NeoSCA install it for you?"
            )
        if is_install in ("n", "N"):
            manual_install_prompt_dict = {
                JAVA: (
                    f"You will have to install {JAVA} manually.\n\n1. To install it, visit"
                    " https://www.java.com/en/download/manual.jsp. Note that when mixing 64 bit"
                    " Python with 32 bit Java or vice versa the program will crash, so make"
                    " sure that you install a Java with the same bitness of your Python.\n2."
                    " Set an environment variable JAVA_HOME to the path of the unzipped"
                    " directory."
                ),
                STANFORD_PARSER: (
                    f"You will have to install {STANFORD_PARSER} manually.\n\n1. To install it,"
                    f" download and unzip the archive file at {self._URL_STANFORD_PARSER}.\n2."
                    " Set an environment variable STANFORD_PARSER_HOME to the path of the"
                    " unzipped directory."
                ),
                STANFORD_TREGEX: (
                    f"You will have to install {STANFORD_TREGEX} manually.\n\n1. To install it,"
                    f" download and unzip the archive file at {self._URL_STANFORD_TREGEX}.\n2."
                    " Set an environment variable STANFORD_PARSER_HOME to the path of the"
                    " unzipped directory."
                ),
            }
            return (False, manual_install_prompt_dict[name])
        else:
            return True, None

    def install_java(
        self,
        version: str,
        operating_system: str,
        arch: str,
        impl: str,
        target_dir: str,
        is_assume_yes: bool = False,
    ) -> SCAProcedureResult:
        match = glob.glob(f"{target_dir}{os.sep}j[dr][ke]{version}*")
        if match:
            return True, match[0]
        sucess, err_msg = self.ask_install(JAVA, is_assume_yes)
        if not sucess:
            return sucess, err_msg
        sucess, err_msg = self.get_java_download_url(version, operating_system, arch, impl)
        if not sucess:
            return sucess, err_msg
        else:
            url = err_msg
        sucess, err_msg = self._download(url, name=JAVA)  # type:ignore
        if not sucess:
            return sucess, err_msg
        jdk_archive = err_msg
        sucess, err_msg = self._get_normalized_archive_ext(jdk_archive)  # type:ignore
        if not sucess:
            return sucess, err_msg
        jdk_ext = err_msg
        sucess, err_msg = self._decompress_archive(
            jdk_archive, jdk_ext, target_dir  # type:ignore
        )
        if not sucess:
            return sucess, err_msg
        jdk_dir = err_msg
        jdk_bin = os.path.join(jdk_dir, "bin")  # type:ignore
        sucess, err_msg = self._unpack_jars(jdk_dir, jdk_bin)  # type:ignore
        if not sucess:
            return sucess, err_msg
        if jdk_archive:
            os.remove(jdk_archive)
        return True, jdk_dir

    def install_stanford(
        self, name: str, url: str, target_dir: str, is_assume_yes: bool = False
    ) -> SCAProcedureResult:
        match = glob.glob(f"{target_dir}{os.sep}{name.lower().replace(' ', '-')}*")
        if match:
            return True, match[0]
        sucess, err_msg = self.ask_install(name, is_assume_yes)
        if not sucess:
            return sucess, err_msg
        sucess, err_msg = self._download(url, name=name)
        if not sucess:
            return sucess, err_msg
        archive_file = err_msg
        sucess, err_msg = self._get_normalized_archive_ext(archive_file)  # type:ignore
        if not sucess:
            return sucess, err_msg
        archive_ext = err_msg
        sucess, err_msg = self._decompress_archive(
            archive_file, archive_ext, target_dir  # type:ignore
        )
        if not sucess:
            return sucess, err_msg
        unzipped_directory = err_msg
        if archive_file:
            os.remove(archive_file)
        return True, unzipped_directory

    def install(
        self,
        name: str,
        is_assume_yes: bool = False,
        version: str = _JAVA_VERSION,
        operating_system: str = OS,
        arch: str = ARCH,
        impl: str = Implementation.HOTSPOT,
        target_dir: str = USER_SOFTWARE_DIR,  # type: ignore
    ) -> SCAProcedureResult:
        if name == JAVA:
            return self.install_java(
                version, operating_system, arch, impl, target_dir, is_assume_yes
            )
        elif name == STANFORD_PARSER:
            return self.install_stanford(
                name, self._URL_STANFORD_PARSER, target_dir, is_assume_yes
            )
        elif name == STANFORD_TREGEX:
            return self.install_stanford(
                name, self._URL_STANFORD_TREGEX, target_dir, is_assume_yes
            )
        else:
            return False, f"Unexpected name: {name}."
