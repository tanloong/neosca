from collections import OrderedDict
from typing import Dict, List, Optional, Set, Union

from .structure_data import data


class Structure:
    def __init__(
        self,
        name: str,
        desc: str,
        pattern: str = "",
        matches: Optional[list] = None,
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
        if matches is None:
            self.matches = []
        else:  # pragma: no cover
            self.matches = matches
        if requirements is None:
            self.requirements = []
        else:
            self.requirements = requirements
        self.freq: Union[float, int] = 0

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"name: {self.name} ({self.desc})\nrequirements: {self.requirements}\npattern:"
            f" {self.pattern}\nmatches: {self.matches}\nfrequency: {self.freq}"
        )

    def __truediv__(self, other) -> Union[float, int]:
        return round(self.freq / other.freq, 4) if other.freq else 0


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
                "C_S",
                "VP_T",
                "C_T",
                "DC_C",
                "DC_T",
                "T_S",
                "CT_T",
                "CP_T",
                "CP_C",
                "CN_T",
                "CN_C",
            )
        ]

        self.parse_selected_measures()
        self.fields = "Filename," + ",".join(
            (structure.name for structure in self.structures_to_report)
        ).replace("_", "/")

    def parse_selected_measures(self):
        if len(self.selected_measures) > 0:
            self.structures_to_report = [
                structure
                for structure in self.structures_to_report
                if structure.name in self.selected_measures
            ]
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
        self.VP.freq = self.VP1.freq + self.VP2.freq
        self.C.freq = self.C1.freq + self.C2.freq
        self.T.freq = self.T1.freq + self.T2.freq
        self.CN.freq = self.CN1.freq + self.CN2.freq + self.CN3.freq

    def compute_14_indicies(self) -> None:
        """
        Compute the 14 syntactic complexity indices
        """
        self.MLS.freq = self.W / self.S
        self.MLT.freq = self.W / self.T
        self.MLC.freq = self.W / self.C1
        self.C_S.freq = self.C1 / self.S
        self.VP_T.freq = self.VP1 / self.T
        self.C_T.freq = self.C1 / self.T
        self.DC_C.freq = self.DC / self.C1
        self.DC_T.freq = self.DC / self.T
        self.T_S.freq = self.T / self.S
        self.CT_T.freq = self.CT / self.T
        self.CP_T.freq = self.CP / self.T
        self.CP_C.freq = self.CP / self.C1
        self.CN_T.freq = self.CN / self.T
        self.CN_C.freq = self.CN / self.C1

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
        for structure in new.structures_to_query:
            exec("new.{0}.freq = self.{0}.freq + other.{0}.freq".format(structure.name))
        return new
