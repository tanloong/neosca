from .base_tmpl import BaseTmpl
from unittest import mock
from neosca.main import SCAUI

cmdline_text = "This is a test."


class TestMain(BaseTmpl):
    ui = SCAUI()

    @mock.patch("sys.version_info")
    def test_check_python(self, mock_version_info):
        mock_version_info.major, mock_version_info.minor = (3, 6)
        sucess, _ = self.ui.check_python()
        self.assertFalse(sucess)

    def test_show_version(self) -> None:
        self.assertTrue(self.ui.show_version())

    def test_list_fields(self):
        self.assertTrue(self.ui.list_fields())
