import gc
import io
import logging
import os.path as os_path
import sys
import time
from unittest import TestCase

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
text = "There was no possibility of taking a walk that day."
tree = """(ROOT
  (S
    (NP (EX There))
    (VP (VBD was)
      (NP
        (NP (DT no) (NN possibility))
        (PP (IN of)
          (S
            (VP (VBG taking)
              (NP (DT a) (NN walk))
              (NP (DT that) (NN day)))))))
    (. .)))
"""


class BaseTmpl(TestCase):
    def setUp(self):
        logging.info("=" * 60)
        logging.info(f"{self.id()} start")
        self.stdout = io.StringIO()
        self.stdout_orig, sys.stdout = sys.stdout, self.stdout

        self.test_dir = os_path.dirname(os_path.abspath(__file__))
        self.samples_dir = os_path.join(self.test_dir, "data", "samples")
        self.project_dir = os_path.dirname(self.test_dir)

    def tearDown(self):
        sys.stdout = self.stdout_orig
        logging.info(f"{self.id()} finish")
        gc.collect()

    def assertFileExists(self, path, timeout=None, msg=None):
        err_msg = f"file {path} does not exist!"
        if msg is not None:
            err_msg = f"file {path} does not exist! {msg}"
        if timeout is None:
            if not os_path.exists(path):
                raise AssertionError(err_msg)
        else:
            start = time.time()
            while True:
                if os_path.exists(path):
                    return
                elif time.time() - start > timeout:
                    raise AssertionError(err_msg)
                else:
                    time.sleep(0.5)

    def assertFileNotExist(self, path):
        if os_path.exists(path):
            raise AssertionError(f"file {path} does exist!")

    def assertTrueTimeout(self, func, timeout):
        start = time.time()
        while True:
            try:
                func()
                break
            except AssertionError as e:
                if time.time() - start > timeout:
                    raise e
