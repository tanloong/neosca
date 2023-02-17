from collections import OrderedDict
from typing import Sequence, Union


class Structure:
    def __init__(self, name: str, desc: str, pat="", matches="") -> None:
        """
        :param name: name of the structure
        :param desc: description of the structure
        :param pat: Tregex pattern
        :param matches: matched subtrees by Tregex
        """
        self.name = name
        self.desc = desc
        self.pat = pat
        self.matches = matches
        self.freq: Union[float, int] = 0


class Structures:
    def __init__(self, ifile) -> None:
        self.ifile = ifile
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

        self.VP = Structure("VP", "verb phrases")
        self.C = Structure("C", "clauses")
        self.T = Structure("T", "T-units")
        self.CN = Structure("CN", "complex nominals")

        self.MLS = Structure("MLS", "mean length of sentence")
        self.MLT = Structure("MLT", "mean length of T-unit")
        self.MLC = Structure("MLC", "mean length of clause")
        self.C_S = Structure("C_S", "clauses per sentence")
        self.VP_T = Structure("VP_T", "verb phrases per T-unit")
        self.C_T = Structure("C_T", "clauses per T-unit")
        self.DC_C = Structure("DC_C", "dependent clauses per clause")
        self.DC_T = Structure("DC_T", "dependent clauses per T-unit")
        self.T_S = Structure("T_S", "T-units per sentence")
        self.CT_T = Structure("CT_T", "complex T-unit ratio")
        self.CP_T = Structure("CP_T", "coordinate phrases per T-unit")
        self.CP_C = Structure("CP_C", "coordinate phrases per clause")
        self.CN_T = Structure("CN_T", "complex nominals per T-unit")
        self.CN_C = Structure("CN_C", "complex nominals per clause")

        # a list of tregex patterns for various structures
        self.to_query: Sequence[Structure] = (
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
        self.to_report: Sequence[Structure] = (
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

        self.fields = "Filename,W," + ",".join(
            (structure.name for structure in self.to_report)
        ).replace("_", "/")

    def update_freqs(self) -> None:
        """
        Update frequencies of complex nominals, clauses, verb phrases, and T-units
        """
        self.CN.freq = self.CN1.freq + self.CN2.freq + self.CN3.freq
        self.C.freq = self.C1.freq + self.C2.freq
        self.VP.freq = self.VP1.freq + self.VP2.freq
        self.T.freq = self.T1.freq + self.T2.freq

    def _div(self, x, y) -> Union[float, int]:
        return round(x / y, 4) if y else 0

    def compute_14_indicies(self) -> None:
        """
        Compute the 14 syntactic complexity indices
        """
        self.MLS.freq = self._div(self.W.freq, self.S.freq)
        self.MLT.freq = self._div(self.W.freq, self.T.freq)
        self.MLC.freq = self._div(self.W.freq, self.C1.freq)
        self.C_S.freq = self._div(self.C1.freq, self.S.freq)
        self.VP_T.freq = self._div(self.VP1.freq, self.T.freq)
        self.C_T.freq = self._div(self.C1.freq, self.T.freq)
        self.DC_C.freq = self._div(self.DC.freq, self.C1.freq)
        self.DC_T.freq = self._div(self.DC.freq, self.T.freq)
        self.T_S.freq = self._div(self.T.freq, self.S.freq)
        self.CT_T.freq = self._div(self.CT.freq, self.T.freq)
        self.CP_T.freq = self._div(self.CP.freq, self.T.freq)
        self.CP_C.freq = self._div(self.CP.freq, self.C1.freq)
        self.CN_T.freq = self._div(self.CN.freq, self.T.freq)
        self.CN_C.freq = self._div(self.CN.freq, self.C1.freq)

    def get_freqs(self) -> dict:
        freq_dict = OrderedDict({"Filename": self.ifile, "W": self.W.freq})
        for structure in self.to_report:
            freq_dict[structure.name] = structure.freq
        return freq_dict

    def __add__(self, other: "Structures") -> "Structures":
        new_ifile = self.ifile + "+" + other.ifile if self.ifile is not None else other.ifile
        new = Structures(new_ifile)
        new.W.freq = self.W.freq + other.W.freq
        for structure in self.to_query:
            exec(
                f"new.{structure.name}.freq = self.{structure.name}.freq +"
                f" other.{structure.name}.freq"
            )
        return new
