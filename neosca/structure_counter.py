from collections import OrderedDict
import json
import os.path as os_path
from typing import Dict, Optional, Set, Union
from copy import deepcopy


class Structure:
    def __init__(
        self,
        name: str,
        desc: str,
        *,
        tregex_pattern: Optional[str] = None,
        value_source: Optional[str] = None,
    ) -> None:
        """
        :param name: name of the structure
        :param desc: description of the structure
        :param pattern: Tregex pattern
        :param value_source: how to compute the value basing on values of other structures, e.g. "VP1 + VP2". One and only one of pattern and value_source should be given.
        """
        self.name = name
        self.desc = desc

        # no need to check "W" because it uses regex
        if name != "W":
            is_exclussive = (tregex_pattern is None) ^ (value_source is None)
            if not is_exclussive:
                raise ValueError("Exactly one of pattern and value_source must be provided")

        self.tregex_pattern = tregex_pattern
        self.value_source = value_source

        self.value: Optional[Union[float, int]] = None
        self.matches: Optional[list] = None

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"name: {self.name}\ndescription: {self.desc}\npattern:"
            f" {self.tregex_pattern}\nmatches: {self.matches}\nfrequency: {self.value}"
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
        else:
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
        else:
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
        else:
            raise NotImplementedError()

    def __truediv__(self, other) -> float:
        assert self.value is not None
        if isinstance(other, (float, int)):
            return round(self.value / other, 4) if other else 0

        assert other.value is not None
        return round(self.value / other.value, 4) if other.value else 0

    def __rtruediv__(self, other) -> float:
        assert self.value is not None
        if isinstance(other, (float, int)):
            return round(other / self.value, 4) if other else 0
        else:
            raise NotImplementedError()


class StructureCounter:
    data_file = os_path.join(os_path.dirname(__file__), "data", "structure_data.json")
    with open(data_file, "r", encoding="utf-8") as f:
        builtin_data = json.load(f)

    builtin_structures: Dict[str, Structure] = {}
    for kwargs in builtin_data:
        builtin_structures[kwargs["name"]] = Structure(**kwargs)

    builtin_selected_measures = [
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

    def __init__(self, ifile="", selected_measures: Optional[Set[str]] = None) -> None:
        self.ifile = ifile
        if selected_measures is not None:
            # accepted from users as a set to avoid duplicates, now convert to list to ensure order
            self.selected_measures = list(selected_measures)
        else:
            self.selected_measures = self.builtin_selected_measures

        self.fields = "Filename," + ",".join(self.selected_measures)
        self.structures = deepcopy(self.builtin_structures)

    def get_structure(self, structure_name: str) -> Structure:
        try:
            structure = self.structures[structure_name]
        except KeyError:
            raise KeyError(f"{structure_name} not found.")
        else:
            return structure

    def set_matches(self, structure_name: str, matches: list) -> None:
        if structure_name not in self.structures:
            raise ValueError(f"{structure_name} not found")
        elif not isinstance(matches, list):
            raise ValueError("matches should be a list object")
        else:
            self.structures[structure_name].matches = matches

    def get_matches(self, s_name: str) -> Optional[list]:
        s = self.get_structure(s_name)
        return s.matches

    def set_value(self, s_name: str, value: Union[int, float]) -> None:
        if s_name not in self.structures:
            raise ValueError(f"{s_name} not counted")
        elif not isinstance(value, (float, int)):
            raise ValueError(f"value should be either a float or an integer, got {value}")
        else:
            self.structures[s_name].value = value

    def get_value(self, s_name: str) -> Optional[Union[float, int]]:
        s = self.get_structure(s_name)
        return s.value

    def get_all_values(self) -> dict:
        # TODO should store Filename in an extra metadata layer
        # https://articles.zsxq.com/id_wnw0w98lzgsq.html
        freq_dict = OrderedDict({"Filename": self.ifile})
        for s_name in self.selected_measures:
            freq_dict[s_name] = str(self.get_value(s_name))
        return freq_dict

    def __add__(self, other: "StructureCounter") -> "StructureCounter":
        new_ifile = self.ifile + "+" + other.ifile if self.ifile else other.ifile
        new_selected_measures = set(self.selected_measures + other.selected_measures)
        new = StructureCounter(new_ifile, selected_measures=new_selected_measures)
        for s_name in new.structures:
            this_value = self.get_value(s_name)
            that_value = other.get_value(s_name)
            if not (this_value is None and that_value is None):
                value = (this_value or 0) + (that_value or 0)
                new.set_value(s_name, value)  # type: ignore
        return new
