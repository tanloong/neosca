#!/usr/bin/env python3

import operator

from neosca.ns_exceptions import StructureNotFoundError
from neosca.ns_sca.ns_sca_counter import Ns_SCA_Counter, Ns_SCA_Structure

from .base_tmpl import BaseTmpl


class TestStructure(BaseTmpl):
    def test_init(self):
        self.assertRaises(ValueError, Ns_SCA_Structure, **{"name": "S", "description": "sentence"})
        self.assertRaises(
            ValueError,
            Ns_SCA_Structure,
            **{
                "name": "S",
                "description": "sentence",
                "tregex_pattern": "non-None",
                "value_source": "non-None",
            },
        )

    def test_numeric_op(self):
        s1 = Ns_SCA_Structure("W")
        s2 = Ns_SCA_Structure("W")

        s1.value = 20
        s2.value = 10

        self.assertEqual(s1 + s2, 30)
        self.assertEqual(s1 + 10, 30)
        self.assertEqual(20 + s2, 30)
        self.assertRaises(NotImplementedError, operator.add, "20", s2)

        self.assertEqual(s1 - s2, 10)
        self.assertEqual(s1 - 10, 10)
        self.assertEqual(20 - s2, 10)
        self.assertRaises(NotImplementedError, operator.sub, "20", s2)

        self.assertEqual(s1 * s2, 200)
        self.assertEqual(s1 * 10, 200)
        self.assertEqual(20 * s2, 200)
        self.assertRaises(NotImplementedError, operator.mul, "20", s2)

        self.assertEqual(s1 / s2, 2)
        self.assertEqual(s1 / 10, 2)
        self.assertEqual(20 / s2, 2)
        self.assertRaises(NotImplementedError, operator.truediv, "20", s2)

        self.assertEqual(s1 / 0, 0)


class TestStructureCounter(BaseTmpl):
    def test_init(self):
        kwargs_duplicated_defs = {"user_structure_defs": [{"name": "A"}, {"name": "A"}]}
        self.assertRaises(ValueError, Ns_SCA_Counter, **kwargs_duplicated_defs)

        kwargs_undefined_measures = {"selected_measures": ["an_undefined_measure"]}
        self.assertRaises(ValueError, Ns_SCA_Counter, **kwargs_undefined_measures)

        kwargs_with_user_defs_without_selected_measures = {
            "ifile": "",
            "user_structure_defs": [
                {"name": "A", "tregex_pattern": "A !< __"},
                {"name": "B", "tregex_pattern": "B !< __"},
            ],
        }
        counter = Ns_SCA_Counter(**kwargs_with_user_defs_without_selected_measures)
        self.assertEqual(counter.selected_measures, Ns_SCA_Counter.DEFAULT_MEASURES + ["A", "B"])

        kwargs_with_user_defs_with_selected_measures = {
            "selected_measures": ["VP", "A", "B"],
            "user_structure_defs": [
                {"name": "A", "tregex_pattern": "A !< __"},
                {"name": "B", "tregex_pattern": "B !< __"},
            ],
        }
        counter = Ns_SCA_Counter(**kwargs_with_user_defs_with_selected_measures)
        self.assertEqual(
            counter.selected_measures,
            kwargs_with_user_defs_with_selected_measures["selected_measures"],
        )

    def test_undefined_measure(self):
        Ns_SCA_Counter.check_undefined_measure(Ns_SCA_Counter.DEFAULT_MEASURES, None)
        Ns_SCA_Counter.check_undefined_measure(["VP", "CT/T"], {"A"})
        self.assertRaises(ValueError, Ns_SCA_Counter.check_undefined_measure, ["VP", "CT/T", "NULL"], None)
        Ns_SCA_Counter.check_undefined_measure(["VP", "CT/T", "A"], {"A"})

    def test_check_duplicated_def(self):
        user_structure_defs = [{"name": "A"}, {"name": "A"}]
        self.assertRaises(ValueError, Ns_SCA_Counter.check_user_structure_def, user_structure_defs)

        user_structure_defs = [{"name": ""}]
        self.assertRaises(ValueError, Ns_SCA_Counter.check_user_structure_def, user_structure_defs)

        user_structure_defs = [{"": "A"}]
        self.assertRaises(ValueError, Ns_SCA_Counter.check_user_structure_def, user_structure_defs)

        user_structure_defs = [{"name": "A"}, {"name": "B"}]
        user_defined_snames = Ns_SCA_Counter.check_user_structure_def(user_structure_defs)
        self.assertEqual(user_defined_snames, {"A", "B"})

    def test_get_structure(self):
        counter = Ns_SCA_Counter()
        for sname in Ns_SCA_Counter.DEFAULT_MEASURES:
            counter.get_structure(sname)
        self.assertRaises(StructureNotFoundError, counter.get_structure, "NULL")

    def test_get_all_values(self):
        counter = Ns_SCA_Counter()
        value_dict = counter.get_all_values()
        self.assertTrue("Filename", value_dict.keys() - set(counter.selected_measures))

        selected_measures = ["A", "B", "C"]
        user_structure_defs = [
            {"name": "A", "tregex_pattern": "A !< __"},
            {"name": "B", "tregex_pattern": "B !< __"},
            {"name": "C", "tregex_pattern": "C !< __"},
        ]
        counter = Ns_SCA_Counter(selected_measures=selected_measures, user_structure_defs=user_structure_defs)
        self.assertTrue("Filename", value_dict.keys() - set(counter.selected_measures))

    def test_set_matches(self):
        counter = Ns_SCA_Counter()
        self.assertRaises(ValueError, counter.set_matches, "NULL", ["(A a)", "(A (B b))"])
        self.assertRaises(ValueError, counter.set_matches, "W", ("(A a)", "(A (B b))"))

        self.assertEqual(counter.get_matches("W"), [])
        matches = ["counter", "set", "matches"]
        counter.set_matches("W", matches)
        self.assertEqual(counter.get_matches("W"), matches)

    def test_get_matches(self):
        counter = Ns_SCA_Counter()
        self.assertRaises(StructureNotFoundError, counter.get_matches, "NULL")

    def test_get_value(self):
        counter = Ns_SCA_Counter()
        self.assertRaises(StructureNotFoundError, counter.get_value, "NULL")

        self.assertIsNone(counter.get_value("T"))
        counter.set_value("T", 300)
        self.assertEqual(counter.get_value("T"), 300)

    def test_set_value(self):
        counter = Ns_SCA_Counter()
        self.assertRaises(ValueError, counter.set_value, "NULL", 97)
        self.assertRaises(ValueError, counter.set_value, "C", "97")

        counter.set_value("C", 97)
        self.assertEqual(counter.get_value("C"), 97)

        counter.set_value("C", 51.2)
        self.assertEqual(counter.get_value("C"), 51.2)

    def test_add(self):
        selected_measures1 = ["VP", "T", "DC/C"]
        selected_measures2 = ["CP", "VP/T", "CN/C"]
        counter1 = Ns_SCA_Counter(selected_measures=selected_measures1)
        counter2 = Ns_SCA_Counter(selected_measures=selected_measures2)

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
        self.assertEqual({"Filepath"}, value_dict.keys() - set(expected_selected_measures3))

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
