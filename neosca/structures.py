import sys
from typing import Union, Sequence


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
    W = Structure("W", "words")
    S = Structure("S", "sentences", "ROOT")
    VP1 = Structure("VP1", "regular verb phrases", "VP > S|SINV|SQ")
    VP2 = Structure(
        "VP2",
        "verb phrases in inverted yes/no questions or in wh-questions",
        "MD|VBZ|VBP|VBD > (SQ !< VP)",
    )
    C1 = Structure(
        "C1",
        "regular clauses",
        "S|SINV|SQ "
        "[> ROOT <, (VP <# VB) | <# MD|VBZ|VBP|VBD | < "
        "(VP [<# MD|VBP|VBZ|VBD | < CC < (VP <# MD|VBP|VBZ|VBD)])]",
    )
    C2 = Structure(
        "C2",
        "fragment clauses",
        "FRAG > ROOT !<< "
        "(S|SINV|SQ [> ROOT <, (VP <# VB) | <# MD|VBZ|VBP|VBD | < "
        "(VP [<# MD|VBP|VBZ|VBD | < CC < "
        "(VP <# MD|VBP|VBZ|VBD)])])",
    )
    T1 = Structure(
        "T",
        "regular T-units",
        "S|SBARQ|SINV|SQ > ROOT | [$-- S|SBARQ|SINV|SQ !>> SBAR|VP]",
    )
    T2 = Structure(
        "T2",
        "fragment T-units",
        "FRAG > ROOT !<< (S|SBARQ|SINV|SQ > ROOT | [$-- S|SBARQ|SINV|SQ !>> SBAR|VP])",
    )
    CN1 = Structure(
        "CN1",
        "complex nominals, type 1",
        "NP !> NP [<< JJ|POS|PP|S|VBG | << (NP $++ NP !$+ CC)]",
    )
    CN2 = Structure(
        "CN2",
        "complex nominals, type 2",
        "SBAR [<# WHNP | <# (IN < That|that|For|for) | <, S] & [$+ VP | > VP]",
    )
    CN3 = Structure("CN3", "complex nominals, type 3", "S < (VP <# VBG|TO) $+ VP")
    DC = Structure(
        "DC",
        "dependent clauses",
        "SBAR < "
        "(S|SINV|SQ "
        "[> ROOT <, (VP <# VB) | <# MD|VBZ|VBP|VBD | < "
        "(VP [<# MD|VBP|VBZ|VBD | < CC < (VP <# MD|VBP|VBZ|VBD)])])",
    )
    CT = Structure(
        "CT",
        "complex T-units",
        "S|SBARQ|SINV|SQ [> ROOT | [$-- S|SBARQ|SINV|SQ !>> SBAR|VP]] << "
        "(SBAR < (S|SINV|SQ "
        "[> ROOT <, (VP <# VB) | <# MD|VBZ|VBP|VBD | < "
        "(VP [<# MD|VBP|VBZ|VBD | < CC < "
        "(VP <# MD|VBP|VBZ|VBD)])]))",
    )
    CP = Structure("CP", "coordinate phrases", "ADJP|ADVP|NP|VP < CC")

    VP = Structure("VP", "verb phrases")
    C = Structure("C", "clauses")
    T = Structure("T", "T-units")
    CN = Structure("CN", "complex nominals")

    MLS = Structure("MLS", "mean length of sentence")
    MLT = Structure("MLT", "mean length of T-unit")
    MLC = Structure("MLC", "mean length of clause")
    CpS = Structure("C/S", "clauses per sentence")
    VPpT = Structure("VP/T", "verb phrases per T-unit")
    CpT = Structure("C/T", "clauses per T-unit")
    DCpC = Structure("DC/C", "dependent clauses per clause")
    DCpT = Structure("DC/T", "dependent clauses per T-unit")
    TpS = Structure("T/S", "T-units per sentence")
    CTpT = Structure("CT/T", "complex T-unit ratio")
    CPpT = Structure("CP/T", "coordinate phrases per T-unit")
    CPpC = Structure("CP/C", "coordinate phrases per clause")
    CNpT = Structure("CN/T", "complex nominals per T-unit")
    CNpC = Structure("CN/C", "complex nominals per clause")

    # a list of tregex patterns for various structures
    to_query: Sequence[Structure] = (
        S,
        VP1,
        VP2,
        C1,
        C2,
        T1,
        T2,
        CN1,
        CN2,
        CN3,
        DC,
        CT,
        CP,
    )
    to_report: Sequence[Structure] = (
        S,
        VP,
        C,
        T,
        DC,
        CT,
        CP,
        CN,
        MLS,
        MLT,
        MLC,
        CpS,
        VPpT,
        CpT,
        DCpC,
        DCpT,
        TpS,
        CTpT,
        CPpT,
        CPpC,
        CNpT,
        CNpC,
    )

    if sys.platform == "win32":
        quotation_mark = '"'
    else:
        quotation_mark = "'"
    for structure in to_query:
        structure.pat = f"{quotation_mark}{structure.pat}{quotation_mark}"

    fields = "Filename,W," + ",".join((structure.name for structure in to_report))

    def __init__(self, ifile) -> None:
        self.ifile = ifile

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
        self.CpS.freq = self._div(self.C1.freq, self.S.freq)
        self.VPpT.freq = self._div(self.VP1.freq, self.T.freq)
        self.CpT.freq = self._div(self.C1.freq, self.T.freq)
        self.DCpC.freq = self._div(self.DC.freq, self.C1.freq)
        self.DCpT.freq = self._div(self.DC.freq, self.T.freq)
        self.TpS.freq = self._div(self.T.freq, self.S.freq)
        self.CTpT.freq = self._div(self.CT.freq, self.T.freq)
        self.CPpT.freq = self._div(self.CP.freq, self.T.freq)
        self.CPpC.freq = self._div(self.CP.freq, self.C1.freq)
        self.CNpT.freq = self._div(self.CN.freq, self.T.freq)
        self.CNpC.freq = self._div(self.CN.freq, self.C1.freq)

    def get_freqs(self) -> dict:
        freq_dict = {"Filename": self.ifile, "W": self.W.freq}
        for structure in self.to_report:
            freq_dict[structure.name] = structure.freq
        return freq_dict
