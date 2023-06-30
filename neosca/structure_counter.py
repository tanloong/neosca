from collections import OrderedDict
from typing import Dict, List, Optional, Set, Union

from .structure_data import data


class Structure:
    def __init__(
        self,
        name: str,
        desc: str,
        pattern: str = "",
        *,
        requirements: Optional[list] = None,
    ) -> None:
        """
        :param name: name of the structure
        :param desc: description of the structure
        :param pattern: Tregex pattern
        :param matches: matched subtrees by Tregex
        :param requirements: a list of structure names that current instance of Structure requires. Note that the elements come from the initial StructureCounter.structures_to_query, thus CN_T requires ["CN1", "CN2", "CN3", "T1", "T2"] instead of ["CN", "T"]
        """
        self.name = name
        self.desc = desc
        self.pattern = pattern
        if requirements is None:
            self.requirements = []
        else:
            self.requirements = requirements
        self.freq: Union[float, int] = 0
        self.matches: list = []

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"name: {self.name} ({self.desc})\nrequirements: {self.requirements}\npattern:"
            f" {self.pattern}\nmatches: {self.matches}\nfrequency: {self.freq}"
        )

    def set_freq(self, freq: int):
        if not isinstance(freq, int) or freq < 0:
            raise ValueError("freq should be a non-negative integer")
        else:
            self.freq = freq

    def set_matches(self, matches: list):
        if not isinstance(matches, list):
            raise ValueError("matches should be a list object")
        else:
            self.matches = matches


class StructureCounter:
    def __init__(self, ifile="", selected_measures: Optional[Set[str]] = None) -> None:
        self.ifile = ifile
        if selected_measures is None:
            self.selected_measures = set()
        else:
            self.selected_measures = selected_measures

        self.structures: Dict[str, Structure] = {}
        for args, kwargs in data:
            self.structures[args[0]] = Structure(*args, **kwargs)

        self.structures_to_query: List[Structure] = [
            self.structures[key]
            for key in (
                "W",
                "S",
                "VP1",
                "VP2",
                "C1",
                "C2",
                "T1",
                "T2",
                "CN1",
                "CN2",
                "CN3",
                "DC",
                "CT",
                "CP",
            )
        ]

        self.structures_to_report: List[Structure] = [
            self.structures[key]
            for key in (
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
            )
        ]

        self.parse_selected_measures()
        self.fields = "Filename," + ",".join((s.name for s in self.structures_to_report))

    def parse_selected_measures(self):
        if len(self.selected_measures) > 0:
            self.structures_to_report = list(
                filter(lambda s: s.name in self.selected_measures, self.structures_to_report)
            )
            selected_measures_extended = self.selected_measures.copy()
            for structure in self.structures_to_report:
                for name in structure.requirements:
                    if name not in self.selected_measures:
                        selected_measures_extended.add(name)
            self.structures_to_query = [
                structure
                for structure in self.structures_to_query
                if structure.name in selected_measures_extended
            ]

    def update_freqs(self) -> None:
        """
        Update frequencies of complex nominals, clauses, verb phrases, and T-units
        """
        for s_name in ("VP", "C", "T", "CN"):
            self.structures[s_name].freq = sum(
                self.structures[requirement_name].freq
                for requirement_name in self.structures[s_name].requirements
            )

    def compute_14_indicies(self) -> None:
        """
        Compute the 14 syntactic complexity indices
        """
        for s_name, dividend, divisor in (
            ("MLS", "W", "S"),
            ("MLT", "W", "T"),
            ("MLC", "W", "C1"),
            ("C/S", "C1", "S"),
            ("VP/T", "VP1", "T"),
            ("C/T", "C1", "T"),
            ("DC/C", "DC", "C1"),
            ("DC/T", "DC", "T"),
            ("T/S", "T", "S"),
            ("CT/T", "CT", "T"),
            ("CP/T", "CP", "T"),
            ("CP/C", "CP", "C1"),
            ("CN/T", "CN", "T"),
            ("CN/C", "CN", "C1"),
        ):
            divident_freq, divisor_freq = (
                self.structures[dividend].freq,
                self.structures[divisor].freq,
            )
            self.structures[s_name].freq = (
                round(divident_freq / divisor_freq, 4) if divisor_freq else 0
            )

    def get_freqs(self) -> dict:
        self.update_freqs()
        self.compute_14_indicies()
        freq_dict = OrderedDict({"Filename": self.ifile})
        for structure in self.structures_to_report:
            freq_dict[structure.name] = str(structure.freq)
        return freq_dict

    def __add__(self, other: "StructureCounter") -> "StructureCounter":
        new_ifile = self.ifile + "+" + other.ifile if self.ifile else other.ifile
        selected_measures = self.selected_measures | other.selected_measures
        new = StructureCounter(new_ifile, selected_measures=selected_measures)
        for s in new.structures_to_query:
            new.structures[s.name].freq = (
                self.structures[s.name].freq + other.structures[s.name].freq
            )
        return new
