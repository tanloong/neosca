#!/usr/bin/env python3
# -*- coding=utf-8 -*-

import operator

from neosca.scaexceptions import StructureNotFoundError
from neosca.structure_counter import Structure, StructureCounter

from .base_tmpl import BaseTmpl


class TestStructure(BaseTmpl):
    def test_init(self):
        self.assertRaises(ValueError, Structure, **{"name": "S", "description": "sentence"})
        self.assertRaises(
            ValueError,
            Structure,
            **{
                "name": "S",
                "description": "sentence",
                "tregex_pattern": "ROOT !> __",
                "value_source": "S1 + S2",
            }
        )

    def test_numeric_op(self):
        s1 = Structure("W")
        s2 = Structure("W")

        s1.value = 20
        s2.value = 10

        self.assertTrue(s1 + s2, 30)
        self.assertTrue(s1 + 10, 30)
        self.assertTrue(20 + s2, 30)
        self.assertRaises(NotImplementedError, operator.add, "20", s2)

        self.assertTrue(s1 - s2, 10)
        self.assertTrue(s1 - 10, 10)
        self.assertTrue(20 - s2, 10)
        self.assertRaises(NotImplementedError, operator.sub, "20", s2)

        self.assertTrue(s1 * s2, 200)
        self.assertTrue(s1 * 10, 200)
        self.assertTrue(20 * s2, 200)
        self.assertRaises(NotImplementedError, operator.mul, "20", s2)

        self.assertTrue(s1 / s2, 2)
        self.assertTrue(s1 / 10, 2)
        self.assertTrue(20 / s2, 2)
        self.assertRaises(NotImplementedError, operator.truediv, "20", s2)


class TestStructureCounter(BaseTmpl):
    def test_init(self):
        kwargs_duplicated_defs = {"user_structure_defs": [{"name": "A"}, {"name": "A"}]}
        self.assertRaises(ValueError, StructureCounter, **kwargs_duplicated_defs)

        kwargs_undefined_measures = {"selected_measures": ["an_undefined_measure"]}
        self.assertRaises(ValueError, StructureCounter, **kwargs_undefined_measures)

        kwargs_with_user_defs_without_selected_measures = {
            "ifile": "",
            "user_structure_defs": [
                {"name": "A", "tregex_pattern": "A !< __"},
                {"name": "B", "tregex_pattern": "B !< __"},
            ],
        }
        counter = StructureCounter(**kwargs_with_user_defs_without_selected_measures)
        self.assertEqual(
            counter.selected_measures, StructureCounter.DEFAULT_MEASURES + ["A", "B"]
        )

        kwargs_with_user_defs_with_selected_measures = {
            "selected_measures": ["VP", "A", "B"],
            "user_structure_defs": [
                {"name": "A", "tregex_pattern": "A !< __"},
                {"name": "B", "tregex_pattern": "B !< __"},
            ],
        }
        counter = StructureCounter(**kwargs_with_user_defs_with_selected_measures)
        self.assertEqual(
            counter.selected_measures,
            kwargs_with_user_defs_with_selected_measures["selected_measures"],
        )

    def test_undefined_measure(self):
        StructureCounter.check_undefined_measure(StructureCounter.DEFAULT_MEASURES, None)
        StructureCounter.check_undefined_measure(["VP", "CT/T"], {"A"})
        self.assertRaises(
            ValueError, StructureCounter.check_undefined_measure, ["VP", "CT/T", "NULL"], None
        )
        StructureCounter.check_undefined_measure(["VP", "CT/T", "A"], {"A"})

    def test_check_duplicated_def(self):
        user_structure_defs = [{"name": "A"}, {"name": "A"}]
        self.assertRaises(ValueError, StructureCounter.check_duplicated_def, user_structure_defs)

        user_structure_defs = [{"name": "A"}, {"name": "B"}]
        user_defined_snames = StructureCounter.check_duplicated_def(user_structure_defs)
        self.assertEqual(user_defined_snames, {"A", "B"})

    def test_get_structure(self):
        counter = StructureCounter()
        for sname in StructureCounter.DEFAULT_MEASURES:
            counter.get_structure(sname)
        self.assertRaises(StructureNotFoundError, counter.get_structure, "NULL")

    def test_get_all_values(self):
        counter = StructureCounter()
        value_dict = counter.get_all_values()
        self.assertTrue("Filename", value_dict.keys() - set(counter.selected_measures))

        selected_measures = ["A", "B", "C"]
        user_structure_defs = [
            {"name": "A", "tregex_pattern": "A !< __"},
            {"name": "B", "tregex_pattern": "B !< __"},
            {"name": "C", "tregex_pattern": "C !< __"},
        ]
        counter = StructureCounter(
            selected_measures=selected_measures, user_structure_defs=user_structure_defs
        )
        self.assertTrue("Filename", value_dict.keys() - set(counter.selected_measures))

    def test_set_matches(self):
        counter = StructureCounter()
        self.assertRaises(ValueError, counter.set_matches, "NULL", ["(A a)", "(A (B b))"])
        self.assertRaises(ValueError, counter.set_matches, "W", ("(A a)", "(A (B b))"))

        self.assertIsNone(counter.get_matches("W"))
        matches = ["counter", "set", "matches"]
        counter.set_matches("W", matches)
        self.assertEqual(counter.get_matches("W"), matches)

    def test_get_matches(self):
        counter = StructureCounter()
        self.assertRaises(StructureNotFoundError, counter.get_matches, "NULL")

    def test_get_value(self):
        counter = StructureCounter()
        self.assertRaises(StructureNotFoundError, counter.get_value, "NULL")

        self.assertIsNone(counter.get_value("T"))
        counter.set_value("T", 300)
        self.assertEqual(counter.get_value("T"), 300)

    def test_set_value(self):
        counter = StructureCounter()
        self.assertRaises(ValueError, counter.set_value, "NULL", 97)
        self.assertRaises(ValueError, counter.set_value, "C", "97")

        counter.set_value("C", 97)
        self.assertEqual(counter.get_value("C"), 97)

        counter.set_value("C", 51.2)
        self.assertEqual(counter.get_value("C"), 51.2)

    def test_add(self):
        selected_measures1 = ["VP", "T", "DC/C"]
        selected_measures2 = ["CP", "VP/T", "CN/C"]
        counter1 = StructureCounter(selected_measures=selected_measures1)
        counter2 = StructureCounter(selected_measures=selected_measures2)

        for s_name, value in (
            ("VP1", 5),
            ("VP2", 38),
            ("C1", 19),
            ("T1", 27),
            ("T2", 11),
            ("DC", 21),
        ):
            counter1.set_value(s_name, value)

        for s_name, value in (
            ("VP1", 4),
            ("C1", 3),
            ("T1", 41),
            ("T2", 8),
            ("CN1", 40),
            ("CN2", 16),
            ("CN3", 49),
            ("CP", 34),
        ):
            counter2.set_value(s_name, value)

        counter3 = counter1 + counter2
        expected_selected_measures3 = selected_measures1 + selected_measures2
        self.assertEqual(len(counter3.selected_measures), len(expected_selected_measures3))
        for m in expected_selected_measures3:
            self.assertIn(m, counter3.selected_measures)

        value_dict = counter3.get_all_values()
        self.assertEqual({"Filename"}, value_dict.keys() - set(expected_selected_measures3))

        for s_name, value in (
            ("VP1", 9),
            ("VP2", 38),
            ("C1", 22),
            ("T1", 68),
            ("T2", 19),
            ("DC", 21),
            ("CN1", 40),
            ("CN2", 16),
            ("CN3", 49),
            ("CP", 34),
        ):
            self.assertEqual(counter3.get_value(s_name), value)
