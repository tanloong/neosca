import json
import logging
import os
import shutil
import subprocess
from .base_tmpl import BaseTmpl
from typing import Union, Optional


text = """
This is a test.
"""


class CmdlineTmpl(BaseTmpl):
    def build_ifile(self, text, name="sample.txt"):
        with open(name, "w") as f:
            f.write(text)

    def cleanup(
        self,
        output_file: Union[str, list, None] = "result.csv",
        ifile_name="sample.txt",
    ):
        if os.path.exists(ifile_name):
            os.remove(ifile_name)
        if output_file:
            if type(output_file) is list:
                for f in output_file:
                    if os.path.exists(f):
                        if os.path.isdir(f):
                            shutil.rmtree(f)
                        elif os.path.isfile(f):
                            os.remove(f)
            elif type(output_file) is str:
                if os.path.exists(output_file):
                    if os.path.isdir(output_file):
                        shutil.rmtree(output_file)
                    elif os.path.isfile(output_file):
                        os.remove(output_file)
            else:
                raise Exception("Unexpected output file argument")

    def template(
        self,
        cmd,
        expected_output_file: Union[str, list, None] = "result.csv",
        success=True,
        text: Optional[str] = text,
        ifile_name="sample.txt",
        expected_stdout=None,
        expected_stderr=None,
        cleanup=True,
        check_func=None,
    ):
        if text:
            self.build_ifile(text, ifile_name)
        timeout = 60000
        try:
            result = subprocess.run(cmd, capture_output=True, timeout=timeout)
        except subprocess.TimeoutExpired as e:
            logging.error(f"stdout: {e.stdout}")
            logging.error(f"stderr: {e.stderr}")
            raise e
        if not (success ^ (result.returncode != 0)):
            logging.error(f"stdout: {result.stdout.decode('utf-8')}")
            logging.error(f"stderr: {result.stderr.decode('utf-8')}")
        self.assertTrue(success ^ (result.returncode != 0))
        if success:
            if expected_output_file:
                if type(expected_output_file) is list:
                    for f in expected_output_file:
                        self.assertFileExists(f)
                elif type(expected_output_file) is str:
                    self.assertFileExists(expected_output_file)

            if expected_stdout is not None:
                self.assertRegex(result.stdout.decode("utf-8"), expected_stdout)

            if expected_stderr is not None:
                self.assertRegex(result.stderr.decode("utf-8"), expected_stderr)

            if check_func:
                assert (
                    type(expected_output_file) is str
                    and expected_output_file.split(".")[-1] == "csv"
                )
                with open(expected_output_file) as f:
                    data = json.load(f)
                    check_func(data)

        if cleanup:
            self.cleanup(output_file=expected_output_file, ifile_name=ifile_name)
        return result
