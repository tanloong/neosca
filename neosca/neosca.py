import os
import re
import sys
from typing import Generator

from .parser import Parser
from .querier import Querier
from .structures import Structures


class NeoSCA:
    def __init__(
        self,
        dir_stanford_parser: str,
        dir_stanford_tregex: str,
        ifiles: list,
        reserve_parsed: bool,
    ):
        """
        :param dir_parser: directory to Stanford Parser
        :param dir_tregex: directory to Tregex
        :param ifiles: list of input files
        :param reserve_parsed: option to reserve Stanford Parser's
         parsing results
        """
        self.parser = Parser(dir_stanford_parser)
        self.querier = Querier(dir_stanford_tregex)
        self.ifiles = ifiles
        self.reserve_parsed = reserve_parsed
        self.skip_parsing = False

    def _analyze_text(self, ifile: str, fn_parsed: str) -> Structures:
        """
        Analyze a text file

        :param ifile: which file to analyze
        :return structures: an instance of Structures
        """
        if os.path.exists(fn_parsed) and os.path.getsize(fn_parsed) > 0:
            mt_input = os.path.getmtime(ifile)  # get the last modification time
            mt_parsed = os.path.getmtime(fn_parsed)
            if mt_input < mt_parsed:
                self.skip_parsing = True
                print(
                    f"\t[Parser] Parsing skipped: {fn_parsed} already exists,"
                    f" and is non-empty and newer than {ifile}."
                )
        if not self.skip_parsing:
            self.parser.parse(ifile, fn_parsed)

        structures = Structures(ifile)
        for structure in structures.to_query:
            structure.freq, structure.matches = self.querier.query(
                structure, fn_parsed
            )
        structures.update_freqs()

        with open(fn_parsed, "r", encoding="utf-8") as f:
            structures.W.freq = len(
                re.findall(r"\([A-Z]+\$? [^()]+\)", f.read())
            )

        structures.compute_SC_indicies()
        if not self.reserve_parsed and not self.skip_parsing:
            os.remove(fn_parsed)
        return structures

    def perform_analysis(self) -> Generator[Structures, None, None]:
        total = len(self.ifiles)
        for i, ifile in enumerate(self.ifiles):
            print(f'[NeoSCA] Processing "{ifile}" ({i+1}/{total})...')
            fn_parsed = os.path.splitext(ifile)[0] + ".parsed"
            try:
                structures = self._analyze_text(ifile, fn_parsed)
                yield structures
            except KeyboardInterrupt:
                if os.path.exists(fn_parsed) and not self.skip_parsing:
                    os.remove(fn_parsed)
                sys.exit(1)
