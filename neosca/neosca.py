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
        :param dir_stanford_parser: directory to Stanford Parser
        :param dir_stanford_tregex: directory to Tregex
        :param ifiles: list of input files
        :param reserve_parsed: option to reserve Stanford Parser's
         parsing results
        """
        self.parser = Parser(dir_stanford_parser)
        self.querier = Querier(dir_stanford_tregex)
        self.ifiles = ifiles
        self.reserve_parsed = reserve_parsed
        self.skip_parsing = False

    def _parse_text(self, ifile: str, fn_parsed: str) -> str:
        """
        Parse a single text file

        :param ifile: which file to parse
        :param fn_parsed: where to save trees
        :return trees: parsed trees by Stanford Parser
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
            trees = self.parser.parse(ifile, fn_parsed)
        else:
            with open(fn_parsed, "r", encoding="utf-8") as f:
                trees = f.read()

        if self.reserve_parsed:
            with open(fn_parsed, "w", encoding="utf-8") as f:
                f.write(trees)
        return trees

    def _query_against_trees(
        self, trees: str, structures: Structures
    ) -> Structures:
        """
        :param trees: parsed trees by Stanford Parser
        :param structures: an instance of Structures
        :return structures: an instance of Structures
        """
        for structure in structures.to_query:
            structure.freq, structure.matches = self.querier.query(
                structure, trees
            )

        structures.W.freq = len(re.findall(r"\([A-Z]+\$? [^()]+\)", trees))
        structures.update_freqs()
        structures.compute_14_indicies()
        return structures

    def parse_and_query(self) -> Generator[Structures, None, None]:
        total = len(self.ifiles)
        for i, ifile in enumerate(self.ifiles):
            print(f'[NeoSCA] Processing "{ifile}" ({i+1}/{total})...')
            fn_parsed = os.path.splitext(ifile)[0] + ".parsed"
            try:
                structures = Structures(ifile)
                trees = self._parse_text(ifile, fn_parsed)
                yield self._query_against_trees(trees, structures)
            except KeyboardInterrupt:
                if os.path.exists(fn_parsed) and not self.skip_parsing:
                    os.remove(fn_parsed)
                sys.exit(1)

    def parse_and_exit(self) -> None:
        total = len(self.ifiles)
        for i, ifile in enumerate(self.ifiles):
            print(f'[NeoSCA] Processing "{ifile}" ({i+1}/{total})...')
            fn_parsed = os.path.splitext(ifile)[0] + ".parsed"
            try:
                self._parse_text(ifile, fn_parsed)
            except KeyboardInterrupt:
                if os.path.exists(fn_parsed) and not self.skip_parsing:
                    os.remove(fn_parsed)
                sys.exit(1)
        print(
            "Done.\nParsed files were saved corresponding to input files, with"
            ' the same name but a ".parsed" extension.'
        )
