#!/usr/bin/env python3

import logging
import os
import os.path as os_path
import re
import shutil
import sys
from collections import OrderedDict
from copy import deepcopy
from io import BytesIO
from tokenize import NAME, NUMBER, PLUS, tokenize, untokenize
from typing import Dict, List, Optional, Set, Tuple, Union

from neosca import DATA_DIR
from neosca.ns_about import __title__
from neosca.ns_exceptions import CircularDefinitionError, InvalidSourceError, StructureNotFoundError
from neosca.ns_io import Ns_IO
from neosca.ns_sca import l2sca
from neosca.ns_tregex.tree import Tree


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
                1 for attr in (tregex_pattern, dependency_pattern, value_source) if attr is not None
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
        self.matches: List[str] = []

    def definition(self) -> str:
        if self.tregex_pattern is not None:
            return f"tregex_pattern: {self.tregex_pattern}"
        elif self.value_source is not None:
            return f"value_source: {self.value_source}"
        else:
            raise ValueError("Either tregex_pattern or value_source should be provided, but not both")

    def has_value_source(self) -> bool:
        return self.value_source is not None

    def has_tregex_pattern(self) -> bool:
        return self.tregex_pattern is not None

    def __repr__(self) -> str:  # pragma: no cover
        return f"name: {self.name}\ndescription: {self.description}\n{self.definition()}\nvalue: {self.value}"

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
    BUILTIN_DATA = Ns_IO.load_json(DATA_DIR / "l2sca_structures.json")
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

    SNAME_SEARCHER_MAPPING = {
        "S": l2sca.S,
        "VP1": l2sca.VP1,
        "VP2": l2sca.VP2,
        "C1": l2sca.C1,
        "C2": l2sca.C2,
        "T1": l2sca.T1,
        "T2": l2sca.T2,
        "CN1": l2sca.CN1,
        "CN2": l2sca.CN2,
        "CN3": l2sca.CN3,
        "DC": l2sca.DC,
        "CT": l2sca.CT,
        "CP": l2sca.CP,
    }

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

        self.sname_structure_map: Dict[str, Structure] = deepcopy(StructureCounter.BUILTIN_STRUCTURE_DEFS)
        self.sname_structure_map.update(user_sname_structure_map)

        default_measures = StructureCounter.DEFAULT_MEASURES + [
            sname for sname in user_sname_structure_map if sname not in StructureCounter.DEFAULT_MEASURES
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
        check duplicated definition
            e.g., [{"name": "A", "tregex_pattern":"a"}, {"name": "A", "tregex_pattern":"a"}]
        check empty definition
            e.g., [{"name": "A", "tregex_pattern":""}]
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
            raise StructureNotFoundError(f"{structure_name} not found.") from KeyError
        else:
            return structure

    def set_matches(self, structure_name: str, matches: List[str]) -> None:
        if structure_name not in self.sname_structure_map:
            raise StructureNotFoundError(f"{structure_name} not found")
        elif not isinstance(matches, list):
            raise ValueError("matches should be a list object")
        else:
            self.sname_structure_map[structure_name].matches = matches

    def add_matches(self, structure_name: str, matches: List[str]) -> None:
        if structure_name not in self.sname_structure_map:
            raise StructureNotFoundError(f"{structure_name} not found")
        elif not isinstance(matches, list):
            raise ValueError("matches should be a list object")
        else:
            self.sname_structure_map[structure_name].matches.extend(matches)

    def get_matches(self, sname: str) -> List[str]:
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
        freq_dict = OrderedDict({"Filepath": self.ifile})
        for sname in self.selected_measures:
            freq_dict[sname] = str(self.get_value(sname, precision))
        return freq_dict

    def sname_has_value_source(self, sname: str) -> bool:
        return self.get_structure(sname).has_value_source()

    def sname_has_tregex_pattern(self, sname: str) -> bool:
        return self.get_structure(sname).has_tregex_pattern()

    def check_circular_def(self, descendant_sname: str, ancestor_snames: List[str]) -> None:
        if descendant_sname in ancestor_snames:
            circular_definition = ", ".join(
                f"{ancestor_sname} = {self.get_structure(ancestor_sname).value_source}"
                for ancestor_sname in ancestor_snames
            )
            raise CircularDefinitionError(f"Circular definition: {circular_definition}")
        else:
            logging.debug(
                "[Tregex] Circular definition check passed: descendant"
                f" {descendant_sname} not in ancestors {ancestor_snames}"
            )

    @classmethod
    def search_sname(cls, sname: str, trees: str) -> List[str]:
        if sname not in cls.SNAME_SEARCHER_MAPPING:
            raise ValueError(f"{sname} is not yet supported in {__title__}.")

        matches = []
        last_node = None
        for tree in Tree.fromstring(trees):
            for node in cls.SNAME_SEARCHER_MAPPING[sname].searchNodeIterator(tree):
                if node is last_node:
                    # Mimic Tregex's -o option
                    # https://github.com/stanfordnlp/CoreNLP/blob/efc66a9cf49fecba219dfaa4025315ad966285cc/src/edu/stanford/nlp/trees/tregex/TregexPattern.java#L885
                    continue
                last_node = node
                span_string = node.span_string()
                matches.append(span_string)
        return matches

    def exec_value_source(
        self,
        value_source: str,
        sname: str,
        trees: str,
        ancestor_snames: List[str],
    ) -> Tuple[Union[float, int], List[str]]:
        tokens = []
        g = tokenize(BytesIO(value_source.encode("utf-8")).readline)
        next(g)  # Skip the "utf-8" token

        matches: List[str] = []
        is_addition_only: bool = True
        for toknum, tokval, *_ in g:
            if toknum == NAME:
                ancestor_snames.append(sname)
                self.check_circular_def(tokval, ancestor_snames)

                self.determine_value(tokval, trees, ancestor_snames)
                if not self.sname_has_value_source(tokval):
                    # No circular def problem in terminal node.
                    # Note that we currently have only two definition types,
                    #  value_source and tregex_pattern. When new types are
                    #  added, not having value source may do NOT necessarily
                    #  mean a terminal node.
                    ancestor_snames.clear()

                get_structure_code = f"counter.get_structure('{tokval}')"
                if is_addition_only:
                    matches.extend(self.get_matches(tokval))
                tokens.append((toknum, get_structure_code))

            elif toknum == NUMBER or tokval in ("(", ")"):
                tokens.append((toknum, tokval))
            elif tokval in ("+", "-", "*", "/"):
                tokens.append((toknum, tokval))
                if tokval != "+":
                    matches.clear()
                    is_addition_only = False
            # Limit value_source as only NAMEs and numberic operators to assure security for `eval`
            elif tokval != "":
                raise InvalidSourceError(f'Unexpected token: "{tokval}"')

        # Append "+ 0" to force tokens evaluated as number if value_source contains just name of another Structure
        tokens.extend(((PLUS, "+"), (NUMBER, "0")))
        return eval(untokenize(tokens)), matches

    def determine_value_from_tregex_pattern(self, sname: str, trees: str):
        structure = self.get_structure(sname)
        tregex_pattern = structure.tregex_pattern
        assert tregex_pattern is not None

        logging.info(
            f" Searching for {sname}"
            + (f" ({structure.description})..." if structure.description is not None else "...")
        )
        logging.debug(f" Searching for {tregex_pattern}")
        matched_subtrees = self.search_sname(sname, trees)
        self.set_value(sname, len(matched_subtrees))
        self.set_matches(sname, matched_subtrees)

    def determine_value_from_value_source(self, sname: str, trees: str, ancestor_snames: List[str]) -> None:
        structure = self.get_structure(sname)
        value_source = structure.value_source
        assert value_source is not None, f"value_source for {sname} is None."

        logging.info(
            f" Calculating {sname} "
            + (f"({structure.description}) " if structure.description is not None else "")
            + f"= {value_source}..."
        )
        value, matches = self.exec_value_source(value_source, sname, trees, ancestor_snames)
        self.set_value(sname, value)
        self.set_matches(sname, matches)

    def determine_value(
        self,
        sname: str,
        trees: str,
        ancestor_snames: Optional[List[str]] = None,
    ) -> None:
        value = self.get_value(sname)
        if value is not None:
            logging.debug(f"[Tregex] {sname} has already been set as {value}, skipping...")
            return

        if sname == "W":
            logging.info(' Searching for "words"')
            value = len(re.findall(r"\([A-Z]+\$? [^()—–-]+\)", trees))
            self.set_value(sname, value)
            return

        if self.sname_has_tregex_pattern(sname):
            self.determine_value_from_tregex_pattern(sname, trees)
        else:
            if ancestor_snames is None:
                ancestor_snames = []
            self.determine_value_from_value_source(sname, trees, ancestor_snames)

    def determine_all_values(self, trees: str) -> None:
        for sname in self.selected_measures:
            self.determine_value(sname, trees)

    def dump_matches(self, odir_matched: str = "", is_stdout: bool = False) -> None:  # pragma: no cover
        bn_input = os_path.basename(self.ifile)
        bn_input_noext = os_path.splitext(bn_input)[0]
        subodir_matched = os_path.join(odir_matched, bn_input_noext).strip()
        if not is_stdout:
            shutil.rmtree(subodir_matched, ignore_errors=True)
            os.makedirs(subodir_matched)
        for sname, structure in self.sname_structure_map.items():
            matches = structure.matches
            if not matches:
                continue

            meta_data = str(structure)
            res = "\n".join(matches)
            # only accept alphanumeric chars, underscore, and hypen
            escaped_sname = re.sub(r"[^\w-]", "", sname.replace("/", "-per-"))
            matches_id = bn_input_noext + "-" + escaped_sname
            if not is_stdout:
                extension = ".txt"
                fn_match_output = os_path.join(subodir_matched, matches_id + extension)
                with open(fn_match_output, "w", encoding="utf-8") as f:
                    f.write(f"{meta_data}\n\n")
                    f.write(res)
            else:
                sys.stdout.write(f"{matches_id}\n")
                sys.stdout.write(f"{meta_data}\n\n")
                sys.stdout.write(res)

    def __add__(self, other: "StructureCounter") -> "StructureCounter":
        logging.debug("[StructureCounter] Combining counters...")
        new_ifile = self.ifile + "+" + other.ifile if self.ifile else other.ifile
        new_selected_measures = list(dict.fromkeys(self.selected_measures + other.selected_measures))
        new = StructureCounter(new_ifile, selected_measures=new_selected_measures)
        for sname, structure in new.sname_structure_map.items():
            # structures defined by value_source should be re-calculated after
            # adding up structures defined by tregex_pattern
            if structure.value_source is not None:
                logging.debug(f"[StructureCounter] Skip combining {sname} as it is defined by value_source.")
                continue

            this_value = self.get_value(sname) or 0
            that_value = other.get_value(sname) or 0
            value = this_value + that_value
            new.set_value(sname, value)
            logging.debug(f"[StructureCounter] Combined {sname}: {this_value} + {that_value} = {value}")

            matches: List[str] = self.get_matches(sname) + other.get_matches(sname)
            new.set_matches(sname, matches)

        return new
