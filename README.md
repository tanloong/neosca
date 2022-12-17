<div align="center">
 <h1> NeoSCA </h1>
 <p>
  <a>
   <img alt="support-version" src="https://img.shields.io/badge/python-3.7%20%7C%203.8%20%7C%203.9%20%7C%203.10%20%7C%203.11-blue" />
  </a>
  <a href="https://pypi.org/project/neosca">
   <img alt="pypi" src="https://img.shields.io/badge/pypi-v0.0.30-orange" />
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

1. Install neosca

To install NeoSCA, you need to have [Python](https://www.python.org/) 3.7 or later installed on your system. You can check if you have Python installed by running the following command in your terminal:

```sh
python --version
```

If Python is not installed, you can download and install it from [Python website](https://www.python.org/downloads/). Once you have Python installed, you can install NeoSCA using `pip`:

```sh
pip install neosca
```

For users inside of China:

```sh
pip install neosca -i https://pypi.tuna.tsinghua.edu.cn/simple
```

2. Install [Java](https://www.java.com/en/download) 8 or later

3. Download and unzip latest versions of
[Stanford Parser](https://nlp.stanford.edu/software/lex-parser.shtml#Download) and 
[Stanford Tregex](https://nlp.stanford.edu/software/tregex.html#Download)

<details>

<summary>
4. Set environment variables `STANFORD_PARSER_HOME` and `STANFORD_TREGEX_HOME`
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

1. Single input:

```sh
nsca ./samples/sample1.txt 
# frequency output: ./result.csv
nsca ./samples/sample1.txt -o sample1.csv 
# frequency output: ./sample1.csv
```

2. Multiple input:

```sh
nsca ./samples/sample1.txt ./samples/sample2.txt
nsca ./samples/sample*.txt 
# wildcard characters are supported
nsca ./samples/sample[1-1000].txt
```

3. Use `--text` to pass text through command line.

```sh
nsca --text 'The quick brown fox jumps over the lazy dog.'
# frequency output: ./result.csv
```

4. Use `-p/--reserve-parsed` 
to reserve parsed trees of Stanford Parser.
Use `-m/--reserve-matched`
to reserve matched subtrees of Stanford Tregex.

```sh
nsca samples/sample1.txt -p -m
# frequency output: ./result.csv
# parsed trees: ./samples/sample1.parsed
# matched subtrees: ./result_matches/
```

<details>

<summary>
5. Use `--list` to print output fields.
</summary>

```sh
nsca --list
```

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

6. Use `--no-query` to just save parsed trees and exit.

```sh
nsca samples/sample1.txt --no-query
# parsed trees: samples/sample1.parsed
nsca --text 'This is a test.' --no-query
# parsed trees: ./cmdline_text.parsed
```

7. Calling `nsca` without any arguments returns the help message.

## <a name="citing"></a> Citing <small><sup>[Top ▲](#contents)</sup></small>

If you use NeoSCA in your research, please cite it using the following BibTeX entry:

```BibTeX
@misc{tan2022neosca,
author = {Tan, Long},
title = {NeoSCA (version 0.0.30)},
howpublished = {\url{https://github.com/tanloong/neosca}},
year = {2022}
}
```

Also, you need to cite Lu's article describing L2SCA:

```BibTeX
@article{lu2010automatic,
title={Automatic analysis of syntactic complexity in second language writing},
author={Lu, Xiaofei},
journal={International journal of corpus linguistics},
volume={15},
number={4},
pages={474--496},
year={2010},
publisher={John Benjamins}
}
```

## <a name="license"></a> License <small><sup>[Top ▲](#contents)</sup></small>

NeoSCA is licensed under the GNU General Public License version 2 or later.
