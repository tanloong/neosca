import os
import re
import sys
from typing import Tuple, Generator

from .parser import Parser
from .querier import Querier
from .structures import Structures


class NeoSCA:
    def __init__(
        self,
        dir_stanford_parser: str,
        dir_stanford_tregex: str,
        reserve_parsed: bool,
        verbose: bool = True,
    ) -> None:
        self.parser = Parser(dir_stanford_parser, verbose=verbose)
        self.querier = Querier(dir_stanford_tregex)

        self.reserve_parsed = reserve_parsed
        self.skip_parsing = False

    def _parse_ifile(self, ifile: str, ofile_parsed: str) -> str:
        """Parse a single text file"""
        if os.path.exists(ofile_parsed) and os.path.getsize(ofile_parsed) > 0:
            mt_input = os.path.getmtime(ifile)  # get the last modification time
            mt_parsed = os.path.getmtime(ofile_parsed)
            if mt_input < mt_parsed:
                self.skip_parsing = True
                print(
                    f"\t[Parser] Parsing skipped: {ofile_parsed} already"
                    f" exists, and is non-empty and newer than {ifile}."
                )
        if not self.skip_parsing:
            with open(ifile, "r", encoding="utf-8") as f:
                text = f.read()
            trees = self.parser.parse(text, ofile_parsed)
        else:
            with open(ofile_parsed, "r", encoding="utf-8") as f:
                trees = f.read()

        if self.reserve_parsed:
            with open(ofile_parsed, "w", encoding="utf-8") as f:
                f.write(trees)
        return trees

    def _query_against_trees(self, trees: str, structures: Structures) -> Structures:
        for structure in structures.to_query:
            structure.freq, structure.matches = self.querier.query(structure, trees)

        structures.W.freq = len(re.findall(r"\([A-Z]+\$? [^()]+\)", trees))
        structures.update_freqs()
        structures.compute_14_indicies()
        return structures

    def parse_text(self, text: str, ofile_parsed="cmdline_text.parsed") -> str:
        trees = self.parser.parse(text, ofile_parsed)
        if self.reserve_parsed:
            with open(ofile_parsed, "w", encoding="utf-8") as f:
                f.write(trees)
        return trees

    def parse_text_and_query(self, text: str) -> Structures:
        trees = self.parse_text(text)
        structures = Structures("cmdline_text")
        return self._query_against_trees(trees, structures)

    def parse_ifiles_and_query(self, ifiles) -> Generator[Structures, None, None]:
        total = len(ifiles)
        for i, ifile in enumerate(ifiles):
            print(f'[NeoSCA] Processing "{ifile}" ({i+1}/{total})...')
            ofile_parsed = os.path.splitext(ifile)[0] + ".parsed"
            try:
                structures = Structures(ifile)
                trees = self._parse_ifile(ifile, ofile_parsed)
                yield self._query_against_trees(trees, structures)
            except KeyboardInterrupt:
                if os.path.exists(ofile_parsed) and not self.skip_parsing:
                    os.remove(ofile_parsed)
                sys.exit(1)

    def parse_ifiles(self, ifiles) -> None:
        total = len(ifiles)
        for i, ifile in enumerate(ifiles):
            print(f'[NeoSCA] Processing "{ifile}" ({i+1}/{total})...')
            ofile_parsed = os.path.splitext(ifile)[0] + ".parsed"
            try:
                self._parse_ifile(ifile, ofile_parsed)
            except KeyboardInterrupt:
                if os.path.exists(ofile_parsed) and not self.skip_parsing:
                    os.remove(ofile_parsed)
                sys.exit(1)
