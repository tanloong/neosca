#!/usr/bin/env python3

from neosca_gui.ng_singleton import QSingleton

from tests.base_tmpl import BaseTmpl


class TestSingleton(BaseTmpl):
    def test_singleton(self):
        class C(metaclass=QSingleton):
            pass
        c1 = C()
        c2 = C()
        self.assertEqual(id(c1), id(c2))
