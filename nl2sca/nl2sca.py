"""CAUTION: DON'T manually modify parsedFile"""

"""
Name: L2SCA 4.2.0-0.1
Desc: A rewrite of Professor Xiaofei Lu's project, with some extended features.
      See README-L2SCA-fork.txt for details.
Author: TAN Long
Email: tanloong@foxmail.com
Date: 17 Aug 2022
"""

from .utils.arg_processer import ArgProcessor
from .utils.analyzer import Analyzer
from .utils.writer import write_match_output
from .utils.writer import write_freq_output


def main():
    args = ArgProcessor().process_args()
    analyzer = Analyzer(args.dir_parser, args.dir_tregex)

    structures_list = list(
        analyzer.perform_analysis(args.fn_inputs, args.is_reserve_parsed)
    )  # list of instances of Structures, each for one corresponding input file

    freq_output = ""
    for structures in structures_list:
        freq_output += structures.get_freqs() + "\n"
    write_freq_output(freq_output, args.fn_freq_output)

    if args.is_reserve_match:
        for structures in structures_list:
            write_match_output(structures, args.dir_match_output)


if __name__ == "__main__":
    main()
