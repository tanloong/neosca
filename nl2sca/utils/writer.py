import os
from os import path

from .structures import Structures
from .tree2tex import Tree2Tex


def write_match_output(structures: Structures, dir_match_output: str):
    """
    Save Tregex's match output

    :param structures: an instance of Structures
    :param dir_match_output: where to save the match output
    """
    bn_input = path.basename(structures.fn_input)
    bn_input_rstripped = path.splitext(bn_input)[0]
    # bn_input with the extension at the right side stripped
    subdir_match_output = path.join(dir_match_output, bn_input_rstripped)
    if not path.isdir(subdir_match_output):
        # if not exists and is a directory
        os.makedirs(subdir_match_output)
    for structure in structures.to_search_for:
        bn_match_output = bn_input_rstripped + "-" + structure.name + ".matches"
        bn_tex_output = bn_input_rstripped + "-" + structure.name + ".tex"
        fn_match_output = path.join(subdir_match_output, bn_match_output)
        fn_tex_output = path.join(subdir_match_output, bn_tex_output)
        if structure.matches:
            with open(fn_match_output, "w") as f:
                f.write(structure.matches)
            tex = Tree2Tex(structure.matches).to_latex()
            with open(fn_tex_output, "w") as f:
                f.write(tex)
    print(f"Match output was saved to {subdir_match_output}")


def write_freq_output(freq_output: str, fn_output: str):
    """
    :param freq_output: comma-separated frequency output
    :param fn_output: where to save the frequency output
    """
    with open(fn_output, "w") as f:
        f.write(f"{Structures.fields}\n{freq_output}")
    print(f"Frequency output was saved to {fn_output}. Done.")
