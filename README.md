<div align="center">
 <h1> NeoSCA </h1>
 <p>
  <a>
   <img alt="support-version" src="https://img.shields.io/badge/python-3.7%20%7C%203.8%20%7C%203.9%20%7C%203.10%20%7C%203.11-blue" />
  </a>
  <a href="https://pypi.org/project/neosca">
   <img alt="pypi" src="https://img.shields.io/badge/pypi-v0.0.32-orange" />
  </a>
 <a href="https://codecov.io/gh/tanloong/neosca">
   <img src="https://codecov.io/gh/tanloong/neosca/branch/master/graph/badge.svg?token=M2MX1BSAEI"/>
 </a>
  <a>
   <img alt="platform" src="https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgray" />
  </a>
  <a href="https://github.com/tanloong/neosca/blob/master/LICENSE.txt">
   <img alt="license" src="https://img.shields.io/badge/license-GPL%20v2%2B-green"/>
  </a>
  <h4>
   Another syntactic complexity analyzer of written English language samples.
  </h4>
 </p>
</div>

![](img/testing-on-Windows.gif)

NeoSCA is a rewrite of
[Xiaofei Lu](http://personal.psu.edu/xxl13/index.html)'s 
[L2 Syntactic Complexity Analyzer](http://personal.psu.edu/xxl13/downloads/l2sca.html),
supporting Windows, macOS, and Linux.
The same as L2SCA,
NeoSCA takes written English language
samples in plain text format as input, and computes:

<details>

<summary>
the frequency of 9 structures in the text:
</summary>

1. words (W)
2. sentences (S)
3. verb phrases (VP)
4. clauses (C)
5. T-units (T)
6. dependent clauses (DC)
7. complex T-units (CT)
8. coordinate phrases (CP)
9. complex nominals (CN), and

</details>

<details>

<summary>
14 syntactic complexity indices of the text:
</summary>

1. mean length of sentence (MLS)
2. mean length of T-unit (MLT)
3. mean length of clause (MLC)
4. clauses per sentence (C/S)
5. verb phrases per T-unit (VP/T)
6. clauses per T-unit (C/T)
7. dependent clauses per clause (DC/C)
8. dependent clauses per T-unit (DC/T)
9. T-units per sentence (T/S)
10. complex T-unit ratio (CT/T)
11. coordinate phrases per T-unit (CP/T)
12. coordinate phrases per clause (CP/C)
13. complex nominals per T-unit (CN/T)
14. complex nominals per clause (CP/C)

</details>

## Contents

<!-- vim-markdown-toc GFM -->

* [NeoSCA vs. L2SCA](#neosca-vs-l2sca)
* [Installation](#installation)
* [Usage](#usage)
* [Citing](#citing)
* [License](#license)

<!-- vim-markdown-toc -->

## <a name="neosca-vs-l2sca"></a> NeoSCA vs. L2SCA <small><sup>[Top ▲](#contents)</sup></small>

| L2SCA | NeoSCA |
|-|-|
| runs on macOS and Linux | runs on **Windows**, macOS, and Linux |
| single and multiple input are handled respectively by two commands | one command, `nsca`, for both cases, making your life easier |
| runs only under its own home directory | runs under any directory |
| outputs only frequencies of the "9+14" syntactic structures | add options to reserve intermediate results, such as the results of parsing the text with Stanford Parser and matching patterns with Stanford Tregex |

## <a name="installation"></a> Installation <small><sup>[Top ▲](#contents)</sup></small>

1. Install NeoSCA

To install NeoSCA, you need to have [Python](https://www.python.org/) 3.7 or later installed on your system. You can check if you have Python installed by running the following command in your terminal:

```sh
python --version
```

If Python is not installed, you can download and install it from [Python website](https://www.python.org/downloads/). Once you have Python installed, you can install NeoSCA using `pip`:

```sh
pip install neosca
```

If you are in China and having trouble with slow download speeds or network issues, you can use the Tsinghua University PyPI mirror to install NeoSCA:

```sh
pip install neosca -i https://pypi.tuna.tsinghua.edu.cn/simple
```

2. Install [Java](https://www.java.com/en/download) 8 or later

3. Download and unzip latest versions of
[Stanford Parser](https://nlp.stanford.edu/software/lex-parser.shtml#Download) and 
[Stanford Tregex](https://nlp.stanford.edu/software/tregex.html#Download)

<details>

<summary>
4. Set environment variables
</summary>

+ Windows:

In the Environment Variables window (press `Windows`+`s`, type *env*, and press `Enter`):

```sh
STANFORD_PARSER_HOME=\path\to\stanford-parser-full-2020-11-17
STANFORD_TREGEX_HOME=\path\to\stanford-tregex-2020-11-17
```

+ Linux/macOS:

```sh
export STANFORD_PARSER_HOME=/path/to/stanford-parser-full-2020-11-17
export STANFORD_TREGEX_HOME=/path/to/stanford-tregex-2020-11-17
```

</details>

## <a name="usage"></a> Usage <small><sup>[Top ▲](#contents)</sup></small>

To use NeoSCA, run the `nsca` command in your terminal, followed by the options and arguments you want to use.

1. To analyze a single text file, use the command `nsca` followed by the file path. The default output will be saved as `result.csv` in the current directory. To specify a different output file name, use the option `-o` followed by the desired file name. For example:

```sh
nsca ./samples/sample1.txt 
# frequency output: ./result.csv
nsca ./samples/sample1.txt -o sample1.csv 
# frequency output: ./sample1.csv
```

2. When analyzing a text file with a file name that includes spaces, it is important to enclose the file path in double quotes. This ensures that the entire file name, including the spaces, is interpreted as a single argument. Here is an example of how to use the command for a file named `sample 1.txt`:

```sh
nsca "./samples/sample 1.txt"
```

Without the double quotes, the command would interpret "sample" and "1.txt" as two separate arguments and the analysis would fail.

3. To analyze multiple text files at once, simply list them after the `nsca` command. You can also use [wildcards](https://www.gnu.org/savannah-checkouts/gnu/clisp/impnotes/wildcard.html#wildcard-syntax) to select multiple files at once. For example:

```sh
nsca ./samples/sample1.txt ./samples/sample2.txt
nsca ./samples/sample*.txt 
nsca ./samples/sample[1-100].txt
```

4. If you want to analyze text that is passed directly through the command line, you can use the `--text` option followed by the text. For example:

```sh
nsca --text 'The quick brown fox jumps over the lazy dog.'
# frequency output: ./result.csv
```

5. If you want to reserve the parsed trees and matched subtrees generated by Stanford Parser and Stanford Tregex, you can use the options `-p` or `--reserve-parsed` and `-m` or `--reserve-matched`. For example:

```sh
nsca samples/sample1.txt -p -m
# frequency output: ./result.csv
# parsed trees: ./samples/sample1.parsed
# matched subtrees: ./result_matches/
```

6. If you are not sure what the output fields represent, you can use the `--list` option to print a list of all the available output fields:

```sh
nsca --list
```

<details>

<summary>
This will print a list of all the output fields that can be produced by NeoSCA.
</summary>

```sh
W: words
S: sentences
VP: verb phrases
C: clauses
T: T-units
DC: dependent clauses
CT: complex T-units
CP: coordinate phrases
CN: complex nominals
MLS: mean length of sentence
MLT: mean length of T-unit
MLC: mean length of clause
C/S: clauses per sentence
VP/T: verb phrases per T-unit
C/T: clauses per T-unit
DC/C: dependent clauses per clause
DC/T: dependent clauses per T-unit
T/S: T-units per sentence
CT/T: complex T-unit ratio
CP/T: coordinate phrases per T-unit
CP/C: coordinate phrases per clause
CN/T: complex nominals per T-unit
CN/C: complex nominals per clause
```

</details>

7. If you only want to save the parsed trees and exit, you can use the `--no-query` option. This can be useful if you want to use the parsed trees for other purposes. Here is an example of how to use the option:

```sh
nsca samples/sample1.txt --no-query
# parsed trees: samples/sample1.parsed
nsca --text 'This is a test.' --no-query
# parsed trees: ./cmdline_text.parsed
```

8. If you call the `nsca` command without any arguments or options, it will return a help message.

## <a name="citing"></a> Citing <small><sup>[Top ▲](#contents)</sup></small>

If you use NeoSCA in your research, please cite as follows.

<details>

<summary>
BibTeX:
</summary>

```BibTeX
@misc{tan2022neosca,
title        = {NeoSCA: A Rewrite of L2 Syntactic Complexity Analyzer, version 0.0.32},
author       = {Long Tan},
howpublished = {\url{https://github.com/tanloong/neosca}},
year         = {2022}
}
```

</details>

<details>

<summary>
APA (7th edition):
</summary>

<pre>Tan, L. (2022). <i>NeoSCA: A Rewrite of L2 Syntactic Complexity Analyzer</i> (version 0.0.32) [Software]. Github. https://github.com/tanloong/neosca</pre>

</details>

<details>

<summary>
MLA (9th edition):
</summary>

<pre>Tan, Long. <i>NeoSCA: A Rewrite of L2 Syntactic Complexity Analyzer</i>. version 0.0.32, GitHub, 2022, https://github.com/tanloong/neosca.</pre>

</details>

Also, you need to cite Xiaofei's article describing L2SCA.

<details>

<summary>
BibTeX:
</summary>

```BibTeX
@article{lu2010automatic,
title     = {Automatic analysis of syntactic complexity in second language writing},
author    = {Xiaofei Lu},
journal   = {International journal of corpus linguistics},
volume    = {15},
number    = {4},
pages     = {474--496},
year      = {2010},
publisher = {John Benjamins Publishing Company},
doi       = {10.1075/ijcl.15.4.02lu},
}
```

</details>

<details>

<summary>
APA (7th edition):
</summary>

<pre>Lu, X. (2010). Automatic analysis of syntactic complexity in second language writing. <i>International Journal of Corpus Linguistics</i>, 15(4), 474-496.</pre>

</details>

<details>

<summary>
MLA (9th edition):
</summary>

<pre>Lu, Xiaofei. "Automatic Analysis of Syntactic Complexity in Second Language Writing." <i>International Journal of Corpus Linguistics</i>, vol. 15, no. 4, John Benjamins Publishing Company, 2010, pp. 474-96.</pre>

</details>

## <a name="license"></a> License <small><sup>[Top ▲](#contents)</sup></small>

NeoSCA is licensed under the GNU General Public License version 2 or later.
