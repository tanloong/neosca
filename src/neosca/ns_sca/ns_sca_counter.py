#!/usr/bin/env python3

import io
import logging
import os
import os.path as os_path
import re
import shutil
import sys
import tokenize
from collections import OrderedDict
from copy import deepcopy

from neosca import DATA_DIR
from neosca.ns_about import __title__
from neosca.ns_exceptions import CircularDefinitionError, InvalidSourceError, StructureNotFoundError
from neosca.ns_io import Ns_IO
from neosca.ns_sca import l2sca
from neosca.ns_tregex.tree import Tree
from neosca.ns_utils import safe_div


class Ns_SCA_Structure:
    def __init__(
        self,
        name: str,
        *,
        tregex_pattern: str | None = None,
        value_source: str | None = None,
        description: str | None = None,
    ) -> None:
        """
        :param name: name of the structure
        :param tregex_pattern: Tregex pattern
        :param value_source: how to compute the value basing on values of other structures, e.g. "VP1 + VP2".
        :param description: description of the structure
        """
        self.name = name
        self.description = description

        # no need to check "W" because it uses regex
        if name != "W":
            count_non_none = sum(1 for attr in (tregex_pattern, value_source) if attr is not None)
            if count_non_none != 1:
                raise ValueError(
                    "Exactly one of (tregex_pattern, value_source) should be provided AND non-empty."
                )

        self.tregex_pattern = tregex_pattern
        self.value_source = value_source

        self.value: float | int | None = None
        self.matches: list[str] = []

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

    def is_terminal(self) -> bool:
        # Note that we currently have only two definition types, value_source
        # and tregex_pattern. When new types are added, not having value source
        # may do NOT necessarily mean a terminal node.
        return not self.has_value_source()

    def __repr__(self) -> str:  # pragma: no cover
        return f"name: {self.name}\ndescription: {self.description}\n{self.definition()}\nvalue: {self.value}"

    def __add__(self, other) -> int | float:
        assert self.value is not None
        if isinstance(other, (float, int)):
            return self.value + other

        assert other.value is not None
        return self.value + other.value

    def __radd__(self, other) -> int | float:
        assert self.value is not None
        if isinstance(other, (float, int)):
            return other + self.value
        raise NotImplementedError

    def __sub__(self, other) -> int | float:
        assert self.value is not None
        if isinstance(other, (float, int)):
            return self.value - other

        assert other.value is not None
        return self.value - other.value

    def __rsub__(self, other) -> int | float:
        assert self.value is not None
        if isinstance(other, (float, int)):
            return other - self.value
        raise NotImplementedError

    def __mul__(self, other) -> int | float:
        assert self.value is not None
        if isinstance(other, (float, int)):
            return self.value * other

        assert other.value is not None
        return self.value * other.value

    def __rmul__(self, other) -> int | float:
        assert self.value is not None
        if isinstance(other, (float, int)):
            return other * self.value
        raise NotImplementedError

    def __truediv__(self, other) -> float:
        assert self.value is not None
        if isinstance(other, (float, int)):
            return safe_div(self.value, other)

        assert other.value is not None
        return safe_div(self.value, other.value)

    def __rtruediv__(self, other) -> float:
        assert self.value is not None
        if isinstance(other, (float, int)):
            return safe_div(other, self.value)
        raise NotImplementedError


class Ns_SCA_Counter:
    BUILTIN_DATA = Ns_IO.load_json(DATA_DIR / "l2sca_structures.json")
    BUILTIN_STRUCTURE_DEFS: dict[str, Ns_SCA_Structure] = {}
    for kwargs in BUILTIN_DATA["structures"]:
        BUILTIN_STRUCTURE_DEFS[kwargs["name"]] = Ns_SCA_Structure(**kwargs)

    DEFAULT_MEASURES: list[str] = [
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
        selected_measures: list[str] | None = None,
        user_structure_defs: list[dict[str, str]] | None = None,
    ) -> None:
        self.ifile = ifile

        user_sname_structure_map: dict[str, Ns_SCA_Structure] = {}
        user_snames: set[str] | None = None

        if user_structure_defs is not None:
            user_snames = Ns_SCA_Counter.check_user_structure_def(user_structure_defs)
            logging.debug(f"User definded snames: {user_snames}")

            for kwargs in user_structure_defs:
                user_sname_structure_map[kwargs["name"]] = Ns_SCA_Structure(**kwargs)

        self.sname_structure_map: dict[str, Ns_SCA_Structure] = deepcopy(Ns_SCA_Counter.BUILTIN_STRUCTURE_DEFS)
        self.sname_structure_map.update(user_sname_structure_map)

        default_measures = Ns_SCA_Counter.DEFAULT_MEASURES + [
            sname for sname in user_sname_structure_map if sname not in Ns_SCA_Counter.DEFAULT_MEASURES
        ]

        if selected_measures is not None:
            Ns_SCA_Counter.check_undefined_measure(selected_measures, user_snames)
        self.selected_measures: list[str] = (
            selected_measures if selected_measures is not None else default_measures
        )
        logging.debug(f"Selected measures: {self.selected_measures}")

    @classmethod
    def check_user_structure_def(cls, user_structure_defs: list[dict[str, str]]) -> set[str]:
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
        logging.debug(f"User defined snames: {user_defined_snames}")
        return user_defined_snames

    @classmethod
    def check_undefined_measure(
        cls, selected_measures: list[str], user_defined_snames: set[str] | None
    ) -> None:
        # check undefined selected_measure
        if user_defined_snames is not None:
            all_measures = Ns_SCA_Counter.BUILTIN_STRUCTURE_DEFS.keys() | user_defined_snames
        else:
            all_measures = set(Ns_SCA_Counter.BUILTIN_STRUCTURE_DEFS.keys())
        logging.debug(f"All measures: {all_measures}")

        for m in selected_measures:
            if m not in all_measures:
                raise ValueError(f"{m} has not been defined.")

    def get_structure(self, structure_name: str) -> Ns_SCA_Structure:
        try:
            structure = self.sname_structure_map[structure_name]
        except KeyError:
            raise StructureNotFoundError(f"{structure_name} not found.") from KeyError
        else:
            return structure

    def _check_matches(self, structure_name: str, matches: list[str]) -> None:
        if structure_name not in self.sname_structure_map:
            raise StructureNotFoundError(f"{structure_name} not found")
        elif not isinstance(matches, list):
            raise ValueError("matches should be a list object")

    def set_matches(self, structure_name: str, matches: list[str]) -> None:
        self._check_matches(structure_name, matches)
        self.sname_structure_map[structure_name].matches = matches

    def extend_matches(self, structure_name: str, matches: list[str]) -> None:
        self._check_matches(structure_name, matches)
        self.sname_structure_map[structure_name].matches.extend(matches)

    def get_matches(self, sname: str) -> list[str]:
        return self.get_structure(sname).matches

    def set_value(self, sname: str, value: int | float) -> None:
        if sname not in self.sname_structure_map:
            raise ValueError(f"{sname} not counted")
        elif not isinstance(value, (float, int)):
            raise ValueError(f"value should be either a float or an integer, got {value}")
        else:
            self.sname_structure_map[sname].value = value

    def get_value(self, sname: str, precision: int = 4) -> float | int | None:
        value = self.get_structure(sname).value
        return round(value, precision) if value is not None else value

    def get_all_values(self, precision: int = 4) -> dict:
        # TODO should store Filename in an extra metadata layer
        ret = OrderedDict({"Filepath": self.ifile})
        for sname in self.selected_measures:
            ret[sname] = str(self.get_value(sname, precision))
        return ret

    def sname_has_value_source(self, sname: str) -> bool:
        return self.get_structure(sname).has_value_source()

    def sname_has_tregex_pattern(self, sname: str) -> bool:
        return self.get_structure(sname).has_tregex_pattern()

    def sname_is_terminal(self, sname: str) -> bool:
        return self.get_structure(sname).is_terminal()

    def check_circular_def(self, descendant_sname: str, ancestor_snames: list[str]) -> None:
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
    def search_sname(cls, sname: str, forest: str) -> list[str]:
        if sname not in cls.SNAME_SEARCHER_MAPPING:
            raise ValueError(f"{sname} is not yet supported in {__title__}.")

        matches = []
        last_node = None
        for tree in Tree.fromstring(forest):
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
        forest: str,
        ancestor_snames: list[str],
    ) -> tuple[float | int, list[str]]:
        tokens = []
        matches: list[str] = []
        is_addition_only: bool = True
        for t in tokenize.generate_tokens(io.StringIO(value_source).readline):
            token_type, token_string, *_ = t
            if token_type == tokenize.NAME:
                ancestor_snames.append(sname)
                self.check_circular_def(token_string, ancestor_snames)
                self.determine_value(token_string, forest, ancestor_snames)
                if self.sname_is_terminal(token_string):
                    # No circular definition problem for terminal node.
                    ancestor_snames.clear()
                get_structure_code = f"self.get_structure('{token_string}')"
                if is_addition_only:
                    matches.extend(self.get_matches(token_string))
                tokens.append((token_type, get_structure_code))
            elif token_type == tokenize.NUMBER or token_string in ("(", ")"):
                tokens.append((token_type, token_string))
            elif token_string in ("+", "-", "*", "/"):
                tokens.append((token_type, token_string))
                if token_string != "+":
                    matches.clear()
                    is_addition_only = False
            # Limit value_source as only NAMEs and numberic operators to assure security for `eval`
            elif token_string != "":
                raise InvalidSourceError(f'Unexpected token: "{token_string}"')
        # Append "+ 0" to force tokens evaluated as number if value_source contains just name of another Structure
        tokens.extend(((tokenize.PLUS, "+"), (tokenize.NUMBER, "0")))
        return eval(tokenize.untokenize(tokens)), matches

    def determine_value_from_tregex_pattern(self, sname: str, forest: str):
        structure = self.get_structure(sname)
        tregex_pattern = structure.tregex_pattern
        assert tregex_pattern is not None

        logging.info(
            f" Searching for {sname}"
            + (f" ({structure.description})..." if structure.description is not None else "...")
        )
        logging.debug(f" Searching for {tregex_pattern}")
        matched_subtrees = self.search_sname(sname, forest)
        self.set_value(sname, len(matched_subtrees))
        self.set_matches(sname, matched_subtrees)

    def determine_value_from_value_source(self, sname: str, forest: str, ancestor_snames: list[str]) -> None:
        structure = self.get_structure(sname)
        value_source = structure.value_source
        assert value_source is not None, f"value_source for {sname} is None."

        logging.info(
            f" Calculating {sname} "
            + (f"({structure.description}) " if structure.description is not None else "")
            + f"= {value_source}..."
        )
        value, matches = self.exec_value_source(value_source, sname, forest, ancestor_snames)
        self.set_value(sname, value)
        self.set_matches(sname, matches)

    def determine_value(
        self,
        sname: str,
        forest: str,
        ancestor_snames: list[str] | None = None,
    ) -> None:
        value = self.get_value(sname)
        if value is not None:
            logging.debug(f"[Tregex] {sname} has already been set as {value}, skipping...")
            return

        if sname == "W":
            logging.info(' Searching for "words"')
            value = len(re.findall(r"\([A-Z]+\$? [^()—–-]+\)", forest))
            self.set_value(sname, value)
            return

        if self.sname_has_tregex_pattern(sname):
            self.determine_value_from_tregex_pattern(sname, forest)
        else:
            if ancestor_snames is None:
                ancestor_snames = []
            self.determine_value_from_value_source(sname, forest, ancestor_snames)

    def determine_all_values(self, forest: str = "") -> None:
        for sname in self.selected_measures:
            self.determine_value(sname, forest)

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
            # Only accept alphanumeric chars, underscore, and hypen
            escaped_sname = re.sub(r"[^\w-]", "", sname.replace("/", "-per-"))
            matches_id = bn_input_noext + "-" + escaped_sname
            if not is_stdout:
                extension = ".txt"
                fn_match_output = os_path.join(subodir_matched, matches_id + extension)
                with open(fn_match_output, "w", encoding="utf-8") as f:
                    f.write(f"{meta_data}\n\n{res}\n")
            else:
                sys.stdout.write(f"{matches_id}\n{meta_data}\n\n{res}\n")

    def __add__(self, other: "Ns_SCA_Counter") -> "Ns_SCA_Counter":
        logging.debug("Combining counters...")
        new_ifile = self.ifile + "+" + other.ifile if self.ifile else other.ifile
        new_selected_measures = list(dict.fromkeys(self.selected_measures + other.selected_measures))
        new = Ns_SCA_Counter(new_ifile, selected_measures=new_selected_measures)
        for sname, structure in new.sname_structure_map.items():
            # Structures defined by value_source should be re-calculated after
            # adding up structures defined by tregex_pattern
            if structure.value_source is not None:
                logging.debug(f"Skip combining {sname} as it is defined by value_source.")
                continue

            this_value = self.get_value(sname) or 0
            that_value = other.get_value(sname) or 0
            value = this_value + that_value
            new.set_value(sname, value)
            logging.debug(f"Combined {sname}: {this_value} + {that_value} = {value}")

            matches: list[str] = self.get_matches(sname) + other.get_matches(sname)
            new.set_matches(sname, matches)

        # Re-calc measures defined by value_source
        new.determine_all_values()

        return new
