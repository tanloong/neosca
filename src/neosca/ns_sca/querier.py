#!/usr/bin/env python3

import logging
import os
import os.path as os_path
import re
import shutil
import sys
from io import BytesIO
from tokenize import NAME, NUMBER, PLUS, tokenize, untokenize
from typing import TYPE_CHECKING, List, Optional, Tuple, Union

from neosca.ns_about import __title__
from neosca.ns_exceptions import CircularDefinitionError, InvalidSourceError
from neosca.ns_sca import l2sca
from neosca.ns_tregex.tree import Tree

if TYPE_CHECKING:
    from .structure_counter import StructureCounter


class Ns_Tregex:
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

    @classmethod
    def get_matches(cls, sname: str, trees: str) -> list:
        if sname not in cls.SNAME_SEARCHER_MAPPING:
            raise ValueError(f"{sname} is not yet supported in {__title__}.")

        matches = []
        last_node = None
        for tree in Tree.fromstring(trees):
            for node in cls.SNAME_SEARCHER_MAPPING[sname].searchNodeIterator(tree):
                if node is last_node:
                    # implement Tregex's -o option: https://github.com/stanfordnlp/CoreNLP/blob/efc66a9cf49fecba219dfaa4025315ad966285cc/src/edu/stanford/nlp/trees/tregex/TregexPattern.java#L885
                    continue
                last_node = node
                span_string = node.span_string()
                matches.append(span_string)
        return matches

    @classmethod
    def check_circular_def(
        cls, descendant_sname: str, ancestor_snames: List[str], counter: "StructureCounter"
    ) -> None:
        if descendant_sname in ancestor_snames:
            circular_definition = ", ".join(
                f"{upstream_sname} = {counter.get_structure(upstream_sname).value_source}"
                for upstream_sname in ancestor_snames
            )
            raise CircularDefinitionError(f"Circular definition: {circular_definition}")
        else:
            logging.debug(
                "[Tregex] Circular definition check passed: descendant"
                f" {descendant_sname} not in ancestors {ancestor_snames}"
            )

    @classmethod
    def exec_value_source(
        cls,
        value_source: str,
        counter: "StructureCounter",
        sname: str,
        trees: str,
        ancestor_snames: List[str],
    ) -> Tuple[Union[float, int], List[str]]:
        tokens = []
        g = tokenize(BytesIO(value_source.encode("utf-8")).readline)
        next(g)  # skip the "utf-8" token

        matches: List[str] = []
        is_addition_only: bool = True
        for toknum, tokval, *_ in g:
            if toknum == NAME:
                ancestor_snames.append(sname)
                cls.check_circular_def(tokval, ancestor_snames, counter)

                cls.set_value(counter, tokval, trees, ancestor_snames)
                if cls.has_tregex_pattern(counter, tokval):
                    ancestor_snames.clear()

                get_structure_code = f"counter.get_structure('{tokval}')"
                if is_addition_only:
                    try:  # noqa: SIM105
                        matches.extend(counter.get_matches(tokval))  # type: ignore
                    except TypeError:
                        pass
                tokens.append((toknum, get_structure_code))

            elif toknum == NUMBER or tokval in ("(", ")"):
                tokens.append((toknum, tokval))
            elif tokval in ("+", "-", "*", "/"):
                tokens.append((toknum, tokval))
                if tokval != "+":
                    matches.clear()
                    is_addition_only = False
            # constrain value_source as only NAMEs and numberic ops to assure security for `eval`
            elif tokval != "":
                raise InvalidSourceError(f'Unexpected token: "{tokval}"')

        # append "+ 0" to force tokens evaluated as num if value_source contains just name of another Structure
        tokens.extend(((PLUS, "+"), (NUMBER, "0")))
        return eval(untokenize(tokens)), matches

    @classmethod
    def has_tregex_pattern(cls, counter: "StructureCounter", sname: str) -> bool:
        return counter.get_structure(sname).tregex_pattern is not None

    @classmethod
    def set_value_from_pattern(cls, counter: "StructureCounter", sname: str, trees: str):
        structure = counter.get_structure(sname)
        tregex_pattern = structure.tregex_pattern
        assert tregex_pattern is not None

        logging.info(
            f" Searching for {sname}"
            + (f" ({structure.description})..." if structure.description is not None else "...")
        )
        logging.debug(f" Searching for {tregex_pattern}")
        matched_subtrees = cls.get_matches(sname, trees)
        counter.set_matches(sname, matched_subtrees)
        counter.set_value(sname, len(matched_subtrees))

    @classmethod
    def set_value_from_source(
        cls, counter: "StructureCounter", sname: str, trees: str, ancestor_snames: List[str]
    ) -> None:
        structure = counter.get_structure(sname)
        value_source = structure.value_source
        assert value_source is not None, f"value_source for {sname} is None."

        logging.info(
            f" Calculating {sname} "
            + (f"({structure.description}) " if structure.description is not None else "")
            + f"= {value_source}..."
        )
        value, matches = cls.exec_value_source(value_source, counter, sname, trees, ancestor_snames)
        counter.set_value(sname, value)
        counter.set_matches(sname, matches)

    @classmethod
    def set_value(
        cls,
        counter: "StructureCounter",
        sname: str,
        trees: str,
        ancestor_snames: Optional[List[str]] = None,
    ) -> None:
        value = counter.get_value(sname)
        if value is not None:
            logging.debug(f"[Tregex] {sname} has already been set as {value}, skipping...")
            return

        if sname == "W":
            logging.info(' Searching for "words"')
            value = len(re.findall(r"\([A-Z]+\$? [^()—–-]+\)", trees))
            counter.set_value(sname, value)
            return

        if cls.has_tregex_pattern(counter, sname):
            cls.set_value_from_pattern(counter, sname, trees)
        else:
            if ancestor_snames is None:
                ancestor_snames = []
            cls.set_value_from_source(counter, sname, trees, ancestor_snames)

    @classmethod
    def set_all_values(cls, counter: "StructureCounter", trees: str) -> None:
        for sname in counter.selected_measures:
            cls.set_value(counter, sname, trees)

    @classmethod
    def query(
        cls,
        counter: "StructureCounter",
        trees: str,
        is_reserve_matched: bool = False,
        odir_matched: str = "",
        is_stdout: bool = False,
    ) -> "StructureCounter":
        cls.set_all_values(counter, trees)

        if is_reserve_matched:  # pragma: no cover
            cls.write_match_output(counter, odir_matched, is_stdout)
        return counter

    @classmethod
    def write_match_output(
        cls, counter: "StructureCounter", odir_matched: str = "", is_stdout: bool = False
    ) -> None:  # pragma: no cover
        bn_input = os_path.basename(counter.ifile)
        bn_input_noext = os_path.splitext(bn_input)[0]
        subodir_matched = os_path.join(odir_matched, bn_input_noext).strip()
        if not is_stdout:
            shutil.rmtree(subodir_matched, ignore_errors=True)
            os.makedirs(subodir_matched)
        for sname, structure in counter.sname_structure_map.items():
            matches = structure.matches
            if matches is None or len(matches) == 0:
                continue

            meta_data = (
                f"# name: {structure.name}\n"
                + f"# description: {structure.description}\n"
                + f"# tregex_pattern: {structure.tregex_pattern}\n\n"
            )
            res = "\n".join(matches)
            # only accept alphanumeric chars, underscore, and hypen
            escaped_sname = re.sub(r"[^\w-]", "", sname.replace("/", "-per-"))
            matches_id = bn_input_noext + "-" + escaped_sname
            if not is_stdout:
                extension = ".txt"
                fn_match_output = os_path.join(subodir_matched, matches_id + extension)
                with open(fn_match_output, "w", encoding="utf-8") as f:
                    f.write(meta_data)
                    f.write(res)
            else:
                sys.stdout.write(matches_id + "\n")
                sys.stdout.write(meta_data)
                sys.stdout.write(res)
