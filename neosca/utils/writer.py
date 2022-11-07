import os
from os import path

from .structures import Structures


def write_match_output(structures: Structures, odir_match: str) -> None:
    """
    Save Tregex's match output

    :param structures: an instance of Structures
    :param dir_match_output: where to save the match output
    """
    bn_input = path.basename(structures.ifile)
    bn_input_noext = path.splitext(bn_input)[0]
    subdir_match_output = path.join(odir_match, bn_input_noext)
    if not path.isdir(subdir_match_output):
        # if not (exists and is a directory)
        os.makedirs(subdir_match_output)
    for structure in structures.to_search_for:
        bn_match_output = bn_input_noext + "-" + structure.name + ".matches"
        fn_match_output = path.join(subdir_match_output, bn_match_output)
        if structure.matches:
            with open(fn_match_output, "w", encoding="utf-8") as f:
                f.write(structure.matches)
    print(f"Match output was saved to {subdir_match_output}")


def write_freq_output(freq_output: str, ofile_freq: str) -> None:
    """
    :param freq_output: comma-separated frequency output
    :param fn_output: where to save the frequency output
    """
    with open(ofile_freq, "w", encoding="utf-8") as f:
        f.write(f"{Structures.fields}\n{freq_output}")
    print(f"Frequency output was saved to {ofile_freq}. Done.")
