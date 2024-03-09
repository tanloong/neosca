from unittest import mock

from neosca.ns_main_cli import Ns_Main_Cli

from .base_tmpl import BaseTmpl
from .cmdline_tmpl import text as cmdline_text


class TestMain(BaseTmpl):
    ui = Ns_Main_Cli()

    @mock.patch("sys.version_info")
    def test_check_python(self, mock_version_info):
        mock_version_info.major, mock_version_info.minor = (3, 7)
        sucess, _ = self.ui.check_python()
        self.assertFalse(sucess)

    def test_show_version(self) -> None:
        self.assertTrue(self.ui.show_version())
