from collections import OrderedDict
from copy import deepcopy
import json
import logging
import os.path as os_path
from typing import Dict, List, Optional, Set, Union

from .scaexceptions import StructureNotFoundError


class Structure:
    def __init__(
        self,
        name: str,
        *,
        tregex_pattern: Optional[str] = None,
        dependency_pattern: Optional[str] = None,
        value_source: Optional[str] = None,
        description: Optional[str] = None,
    ) -> None:
        """
        :param name: name of the structure
        :param tregex_pattern: Tregex pattern
        :param dependency_pattern: spaCy dependency pattern
        :param value_source: how to compute the value basing on values of other structures, e.g. "VP1 + VP2". One and only one of pattern and value_source should be given.
        :param description: description of the structure
        """
        self.name = name
        self.description = description

        # no need to check "W" because it uses regex
        if name != "W":
            count_non_none = sum(
                1
                for attr in (tregex_pattern, dependency_pattern, value_source)
                if attr is not None
            )
            if count_non_none != 1:
                raise ValueError(
                    "Exactly one of (tregex_pattern, dependency_pattern, value_source) should be"
                    " provided AND non-empty."
                )

        self.tregex_pattern = tregex_pattern
        self.dependency_pattern = dependency_pattern
        self.value_source = value_source

        self.value: Optional[Union[float, int]] = None
        self.matches: Optional[list] = None

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"name: {self.name}"
            + f"\ndescription: {self.description}"
            + f"\ntregex_pattern: {self.tregex_pattern}"
            + f"\nvalue_source: {self.value_source}"
            + f"\nmatches: {self.matches}"
            + f"\nfrequency: {self.value}"
        )

    def __add__(self, other) -> Union[int, float]:
        assert self.value is not None
        if isinstance(other, (float, int)):
            return self.value + other

        assert other.value is not None
        return self.value + other.value

    def __radd__(self, other) -> Union[int, float]:
        assert self.value is not None
        if isinstance(other, (float, int)):
            return other + self.value
        raise NotImplementedError()

    def __sub__(self, other) -> Union[int, float]:
        assert self.value is not None
        if isinstance(other, (float, int)):
            return self.value - other

        assert other.value is not None
        return self.value - other.value

    def __rsub__(self, other) -> Union[int, float]:
        assert self.value is not None
        if isinstance(other, (float, int)):
            return other - self.value
        raise NotImplementedError()

    def __mul__(self, other) -> Union[int, float]:
        assert self.value is not None
        if isinstance(other, (float, int)):
            return self.value * other

        assert other.value is not None
        return self.value * other.value

    def __rmul__(self, other) -> Union[int, float]:
        assert self.value is not None
        if isinstance(other, (float, int)):
            return other * self.value
        raise NotImplementedError()

    def __truediv__(self, other) -> float:
        assert self.value is not None
        if isinstance(other, (float, int)):
            return self.value / other if other else 0

        assert other.value is not None
        return self.value / other.value if other.value else 0

    def __rtruediv__(self, other) -> float:
        assert self.value is not None
        if isinstance(other, (float, int)):
            return other / self.value if self.value else 0
        raise NotImplementedError()


class StructureCounter:
    data_file = os_path.join(os_path.dirname(__file__), "data", "structure_data.json")
    with open(data_file, "r", encoding="utf-8") as f:
        BUILTIN_DATA = json.load(f)

    BUILTIN_STRUCTURE_DEFS: Dict[str, Structure] = {}
    for kwargs in BUILTIN_DATA["structures"]:
        BUILTIN_STRUCTURE_DEFS[kwargs["name"]] = Structure(**kwargs)

    DEFAULT_MEASURES: List[str] = [
        "W",
        "S",
        "VP",
        "C",
        "T",
        "DC",
        "CT",
        "CP",
        "CN",
        "MLS",
        "MLT",
        "MLC",
        "C/S",
        "VP/T",
        "C/T",
        "DC/C",
        "DC/T",
        "T/S",
        "CT/T",
        "CP/T",
        "CP/C",
        "CN/T",
        "CN/C",
    ]

    def __init__(
        self,
        ifile="",
        *,
        selected_measures: Optional[List[str]] = None,
        user_structure_defs: Optional[List[Dict[str, str]]] = None,
    ) -> None:
        self.ifile = ifile

        user_sname_structure_map: Dict[str, Structure] = {}
        user_snames: Optional[Set[str]] = None

        if user_structure_defs is not None:
            user_snames = StructureCounter.check_user_structure_def(user_structure_defs)
            logging.debug(f"[StructureCounter] user_snames: {user_snames}")

            for kwargs in user_structure_defs:
                user_sname_structure_map[kwargs["name"]] = Structure(**kwargs)

        self.sname_structure_map: Dict[str, Structure] = deepcopy(
            StructureCounter.BUILTIN_STRUCTURE_DEFS
        )
        self.sname_structure_map.update(user_sname_structure_map)

        default_measures = StructureCounter.DEFAULT_MEASURES + [
            sname
            for sname in user_sname_structure_map.keys()
            if sname not in StructureCounter.DEFAULT_MEASURES
        ]

        if selected_measures is not None:
            StructureCounter.check_undefined_measure(selected_measures, user_snames)
        self.selected_measures: List[str] = (
            selected_measures if selected_measures is not None else default_measures
        )
        logging.debug(f"[StructureCounter] selected_measures: {self.selected_measures}")

    @classmethod
    def check_user_structure_def(cls, user_structure_defs: List[Dict[str, str]]) -> Set[str]:
        """
        check duplicated definition, e.g., [{"name": "A", "tregex_pattern":"a"}, {"name": "A", "tregex_pattern":"a"}]
        check empty definition, e.g., [{"name": "A", "tregex_pattern":""}]
        """
        user_defined_snames = set()
        for definition in user_structure_defs:
            for k, v in definition.items():
                if len(v) == 0:
                    raise ValueError(f"Error! {k} is left empty.")
                if len(k) == 0:
                    raise ValueError(f"Error! {v} is assigned to empty attribute.")

            sname = definition["name"]
            if sname in user_defined_snames:
                raise ValueError(f'Duplicated structure definition "{sname}".')

            user_defined_snames.add(sname)
        logging.debug(f"[StructureCounter] user_defined_snames: {user_defined_snames}")
        return user_defined_snames

    @classmethod
    def check_undefined_measure(
        cls, selected_measures: List[str], user_defined_snames: Optional[Set[str]]
    ) -> None:
        # check undefined selected_measure
        if user_defined_snames is not None:
            all_measures = StructureCounter.BUILTIN_STRUCTURE_DEFS.keys() | user_defined_snames
        else:
            all_measures = set(StructureCounter.BUILTIN_STRUCTURE_DEFS.keys())
        logging.debug(f"[StructureCounter] all_measures: {all_measures}")

        for m in selected_measures:
            if m not in all_measures:
                raise ValueError(f"{m} has not been defined.")

    def get_structure(self, structure_name: str) -> Structure:
        try:
            structure = self.sname_structure_map[structure_name]
        except KeyError:
            raise StructureNotFoundError(f"{structure_name} not found.")
        else:
            return structure

    def set_matches(self, structure_name: str, matches: list) -> None:
        if structure_name not in self.sname_structure_map:
            raise StructureNotFoundError(f"{structure_name} not found")
        elif not isinstance(matches, list):
            raise ValueError("matches should be a list object")
        else:
            self.sname_structure_map[structure_name].matches = matches

    def get_matches(self, sname: str) -> Optional[list]:
        s = self.get_structure(sname)
        return s.matches

    def set_value(self, sname: str, value: Union[int, float]) -> None:
        if sname not in self.sname_structure_map:
            raise ValueError(f"{sname} not counted")
        elif not isinstance(value, (float, int)):
            raise ValueError(f"value should be either a float or an integer, got {value}")
        else:
            self.sname_structure_map[sname].value = value

    def get_value(self, sname: str, precision: int = 4) -> Optional[Union[float, int]]:
        value = self.get_structure(sname).value
        return round(value, precision) if value is not None else value

    def get_all_values(self, precision: int = 4) -> dict:
        # TODO should store Filename in an extra metadata layer
        # https://articles.zsxq.com/id_wnw0w98lzgsq.html
        freq_dict = OrderedDict({"Filename": self.ifile})
        for sname in self.selected_measures:
            freq_dict[sname] = str(self.get_value(sname, precision))
        return freq_dict

    def __add__(self, other: "StructureCounter") -> "StructureCounter":
        logging.debug("[StructureCounter] Adding counters...")
        new_ifile = self.ifile + "+" + other.ifile if self.ifile else other.ifile
        new_selected_measures = list(
            dict.fromkeys(self.selected_measures + other.selected_measures)
        )
        new = StructureCounter(new_ifile, selected_measures=new_selected_measures)
        snames_defined_by_value_source: List[str] = []
        for sname, structure in new.sname_structure_map.items():
            # structures defined by value_source should be re-calculated after
            # adding up structures defined by tregex_pattern
            if structure.value_source is not None:
                logging.debug(
                    f"[StructureCounter] Skip {sname} which is defined by value_source."
                )
                snames_defined_by_value_source.append(sname)
                continue

            this_value = self.get_value(sname)
            that_value = other.get_value(sname)
            value = (this_value or 0) + (that_value or 0)
            new.set_value(sname, value)
            logging.debug(
                f"[StructureCounter] Added {sname}: {this_value} + {that_value} = {value}"
            )
        return new
