import os
from os import path
import sys

from typing import Dict, Iterator, Sequence, Union
from .structures import Structures


def write_match_output(structures: Structures, odir_match: str) -> None:
    """
    Save Tregex's match output

    :param structures: an instance of Structures
    :param dir_match_output: where to save the match output
    """
    bn_input = path.basename(structures.ifile)
    bn_input_noext = path.splitext(bn_input)[0]
    subdir_match_output = path.join(odir_match, bn_input_noext).strip()
    if not path.isdir(subdir_match_output):
        # if not (exists and is a directory)
        os.makedirs(subdir_match_output)
    for structure in structures.to_query:
        if structure.matches:
            bn_match_output = (
                bn_input_noext + "-" + structure.name.replace("/", "p") + ".matches"
            )
            fn_match_output = path.join(subdir_match_output, bn_match_output)
            with open(fn_match_output, "w", encoding="utf-8") as f:
                f.write(structure.matches)


def write_freq_output(
    multi_structures: Union[Iterator[Structures], Sequence[Structures]],
    ofile_freq,
    oformat_freq: str,
) -> None:
    if oformat_freq == "csv":
        freq_output = Structures.fields
        for structures in multi_structures:
            freq_dict = structures.get_freqs()
            freq_output += "\n" + ",".join(str(freq) for freq in freq_dict.values())
    elif oformat_freq == "json":
        import json

        combined_freq_dict: Dict[str, list[Dict]] = {"Files": []}
        for structures in multi_structures:
            freq_dict = structures.get_freqs()
            combined_freq_dict["Files"].append(freq_dict)
        freq_output = json.dumps(combined_freq_dict)
    else:
        print(f"Unexpected output format: {oformat_freq}")
        sys.exit(1)

    if ofile_freq is not sys.stdout:
        with open(ofile_freq, "w", encoding="utf-8") as f:
            f.write(freq_output)
    else:
        ofile_freq.write(freq_output)
