from collections import OrderedDict
from typing import Optional, Sequence, Set, Union


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
        self.W = Structure("W", "words")
        self.S = Structure("S", "sentences", "ROOT")
        self.VP1 = Structure("VP1", "regular verb phrases", "VP > S|SINV|SQ")
        self.VP2 = Structure(
            "VP2",
            "verb phrases in inverted yes/no questions or in wh-questions",
            "MD|VBZ|VBP|VBD > (SQ !< VP)",
        )
        self.C1 = Structure(
            "C1",
            "regular clauses",
            "S|SINV|SQ "
            "[> ROOT <, (VP <# VB) | <# MD|VBZ|VBP|VBD | < "
            "(VP [<# MD|VBP|VBZ|VBD | < CC < (VP <# MD|VBP|VBZ|VBD)])]",
        )
        self.C2 = Structure(
            "C2",
            "fragment clauses",
            "FRAG > ROOT !<< "
            "(S|SINV|SQ [> ROOT <, (VP <# VB) | <# MD|VBZ|VBP|VBD | < "
            "(VP [<# MD|VBP|VBZ|VBD | < CC < "
            "(VP <# MD|VBP|VBZ|VBD)])])",
        )
        self.T1 = Structure(
            "T1",
            "regular T-units",
            "S|SBARQ|SINV|SQ > ROOT | [$-- S|SBARQ|SINV|SQ !>> SBAR|VP]",
        )
        self.T2 = Structure(
            "T2",
            "fragment T-units",
            "FRAG > ROOT !<< (S|SBARQ|SINV|SQ > ROOT | [$-- S|SBARQ|SINV|SQ !>> SBAR|VP])",
        )
        self.CN1 = Structure(
            "CN1",
            "complex nominals, type 1",
            "NP !> NP [<< JJ|POS|PP|S|VBG | << (NP $++ NP !$+ CC)]",
        )
        self.CN2 = Structure(
            "CN2",
            "complex nominals, type 2",
            "SBAR [<# WHNP | <# (IN < That|that|For|for) | <, S] & [$+ VP | > VP]",
        )
        self.CN3 = Structure("CN3", "complex nominals, type 3", "S < (VP <# VBG|TO) $+ VP")
        self.DC = Structure(
            "DC",
            "dependent clauses",
            "SBAR < "
            "(S|SINV|SQ "
            "[> ROOT <, (VP <# VB) | <# MD|VBZ|VBP|VBD | < "
            "(VP [<# MD|VBP|VBZ|VBD | < CC < (VP <# MD|VBP|VBZ|VBD)])])",
        )
        self.CT = Structure(
            "CT",
            "complex T-units",
            "S|SBARQ|SINV|SQ [> ROOT | [$-- S|SBARQ|SINV|SQ !>> SBAR|VP]] << "
            "(SBAR < (S|SINV|SQ "
            "[> ROOT <, (VP <# VB) | <# MD|VBZ|VBP|VBD | < "
            "(VP [<# MD|VBP|VBZ|VBD | < CC < "
            "(VP <# MD|VBP|VBZ|VBD)])]))",
        )
        self.CP = Structure("CP", "coordinate phrases", "ADJP|ADVP|NP|VP < CC")

        self.VP = Structure("VP", "verb phrases", requirements=["VP1", "VP2"])
        self.C = Structure("C", "clauses", requirements=["C1", "C2"])
        self.T = Structure("T", "T-units", requirements=["T1", "T2"])
        self.CN = Structure("CN", "complex nominals", requirements=["CN1", "CN2", "CN3"])

        self.MLS = Structure("MLS", "mean length of sentence", requirements=["W", "S"])
        self.MLT = Structure("MLT", "mean length of T-unit", requirements=["W", "T1", "T2"])
        self.MLC = Structure("MLC", "mean length of clause", requirements=["W", "C1"])
        self.C_S = Structure("C_S", "clauses per sentence", requirements=["C1", "S"])
        self.VP_T = Structure(
            "VP_T", "verb phrases per T-unit", requirements=["VP1", "T1", "T2"]
        )
        self.C_T = Structure("C_T", "clauses per T-unit", requirements=["C1", "T1", "T2"])
        self.DC_C = Structure("DC_C", "dependent clauses per clause", requirements=["DC", "C1"])
        self.DC_T = Structure(
            "DC_T", "dependent clauses per T-unit", requirements=["DC", "T1", "T2"]
        )
        self.T_S = Structure("T_S", "T-units per sentence", requirements=["T1", "T2", "S"])
        self.CT_T = Structure("CT_T", "complex T-unit ratio", requirements=["CT", "T1", "T2"])
        self.CP_T = Structure(
            "CP_T", "coordinate phrases per T-unit", requirements=["CP", "T1", "T2"]
        )
        self.CP_C = Structure("CP_C", "coordinate phrases per clause", requirements=["CP", "C1"])
        self.CN_T = Structure(
            "CN_T", "complex nominals per T-unit", requirements=["CN1", "CN2", "CN3", "T1", "T2"]
        )
        self.CN_C = Structure(
            "CN_C", "complex nominals per clause", requirements=["CN1", "CN2", "CN3", "C1"]
        )

        self.structures_to_query: Sequence[Structure] = (
            self.W,
            self.S,
            self.VP1,
            self.VP2,
            self.C1,
            self.C2,
            self.T1,
            self.T2,
            self.CN1,
            self.CN2,
            self.CN3,
            self.DC,
            self.CT,
            self.CP,
        )
        self.structures_to_report: Sequence[Structure] = (
            self.W,
            self.S,
            self.VP,
            self.C,
            self.T,
            self.DC,
            self.CT,
            self.CP,
            self.CN,
            self.MLS,
            self.MLT,
            self.MLC,
            self.C_S,
            self.VP_T,
            self.C_T,
            self.DC_C,
            self.DC_T,
            self.T_S,
            self.CT_T,
            self.CP_T,
            self.CP_C,
            self.CN_T,
            self.CN_C,
        )

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
