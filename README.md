# NeoSCA

[![build](https://github.com/tanloong/neosca/workflows/build/badge.svg)](https://github.com/tanloong/neosca/actions?query=workflow%3Abuild)
[![lint](https://github.com/tanloong/neosca/workflows/lint/badge.svg)](https://github.com/tanloong/neosca/actions?query=workflow%3ALint)
[![codecov](https://img.shields.io/codecov/c/github/tanloong/neosca)](https://codecov.io/gh/tanloong/neosca)
[![codacy](https://app.codacy.com/project/badge/Grade/6d49b7a0f3ac44b79d6fc6b87b303034)](https://www.codacy.com/gh/tanloong/neosca/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=tanloong/neosca&amp;utm_campaign=Badge_Grade)
[![pypi](https://img.shields.io/pypi/v/neosca)](https://pypi.org/project/neosca)
[![commit](https://img.shields.io/github/last-commit/tanloong/neosca)](https://github.com/tanloong/neosca/commits/master)
![support-version](https://img.shields.io/pypi/pyversions/neosca)
![platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgray)
[![downloads](https://img.shields.io/pypi/dm/neosca)](#install)
[![license](https://img.shields.io/github/license/tanloong/neosca)](https://github.com/tanloong/neosca/blob/master/LICENSE.txt)

![](img/testing-on-Windows.gif)

NeoSCA is a rewrite of
[L2 Syntactic Complexity Analyzer](http://personal.psu.edu/xxl13/downloads/l2sca.html) (L2SCA),
developed by
[Xiaofei Lu](http://personal.psu.edu/xxl13/index.html),
with added support for Windows and an improved command-line interface for easier usage.
The same as L2SCA, NeoSCA takes written English language samples in plain text format as input, and computes:

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

* [Highlights](#highlights)
* [Install](#install)
* [Basic Usage](#basic-usage)
* [Advanced Usage](#advanced-usage)
* [Citing](#citing)
* [License](#license)

<!-- vim-markdown-toc -->

## <a name="highlights"></a> Highlights <small><sup>[Top ▲](#contents)</sup></small>

* Works on Windows/macOS/Linux
* Reserves intermediate results, i.e., parsed trees of Stanford Parser and matched subtrees of Stanford Tregex
* An improved command-line interface

## <a name="install"></a> Install <small><sup>[Top ▲](#contents)</sup></small>

### Install NeoSCA <small><sup>[Top ▲](#contents)</sup></small>

To install NeoSCA, you need to have [Python](https://www.python.org/) 3.7 or later installed on your system. You can check if you already have Python installed by running the following command in your terminal:

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

### Install Dependents <small><sup>[Top ▲](#contents)</sup></small>

NeoSCA depends on
[Java](https://www.java.com/en/download/manual.jsp),
[Stanford Parser](https://nlp.stanford.edu/software/lex-parser.shtml),
and
[Stanford Tregex](https://nlp.stanford.edu/software/tregex.html).
After you have NeoSCA installed, you can use `nsca --check-depends` to install them.

## <a name="basic-usage"></a> Basic Usage <small><sup>[Top ▲](#contents)</sup></small>

To use NeoSCA, run the `nsca` command in your terminal, followed by the options and arguments you want to use.

### Single Input <small><sup>[Top ▲](#contents)</sup></small>

To analyze a single text file, use the command `nsca` followed by the file path. 

```sh
nsca ./samples/sample1.txt
# frequency output: ./result.csv
```

A `result.csv` file will be generated in the current directory. You can specify a different output filename using `-o`.

```sh
nsca ./samples/sample1.txt -o sample1.csv
# frequency output: ./sample1.csv
```

<details>

<summary>
When analyzing a text file with a filename that includes spaces, it is important to enclose the file path in double quotes. Assume you have a <code>sample 1.txt</code> to analyze:
</summary>

```sh
nsca "./samples/sample 1.txt"
```

This ensures that the entire filename including the spaces, is interpreted as a single argument. Without the double quotes, the command would interpret "sample" and "1.txt" as two separate arguments and the analysis would fail.

</details>

### Multiple Input <small><sup>[Top ▲](#contents)</sup></small>

To analyze multiple text files at once, simply list them after the `nsca` command.

```sh
nsca ./samples/sample1.txt ./samples/sample2.txt
```

You can also use [wildcards](https://www.gnu.org/savannah-checkouts/gnu/clisp/impnotes/wildcard.html#wildcard-syntax) to select multiple files at once.

```sh
nsca ./samples/sample*.txt 
nsca ./samples/sample[1-100].txt
```

## <a name="advanced-usage"></a> Advanced Usage <small><sup>[Top ▲](#contents)</sup></small>

### Output Frequencies in Json Format <small><sup>[Top ▲](#contents)</sup></small>

You can generate a json file by:

```sh
nsca ./samples/sample1.txt --output-format json
# frequency output: ./result.json
```

Or

```sh
nsca ./samples/sample1.txt -o sample1.json
# frequency output: ./sample1.json
```

### Pass Text Through the Command Line <small><sup>[Top ▲](#contents)</sup></small>

If you want to analyze text that is passed directly through the command line, you can use `--text` followed by the text.

```sh
nsca --text 'The quick brown fox jumps over the lazy dog.'
# frequency output: ./result.csv
```

### Reserve Intermediate Results <small><sup>[Top ▲](#contents)</sup></small>

<details>

<summary>
To reserve the parsed trees, use <code>-p</code> or <code>--reserve-parsed</code>. To reserve matched subtrees, use <code>-m</code> or <code>--reserve-matched</code>.
</summary>

```sh
nsca samples/sample1.txt -p
# frequency output: ./result.csv
# parsed trees: ./samples/sample1.parsed
nsca samples/sample1.txt -m
# frequency output: ./result.csv
# matched subtrees: ./result_matches/
nsca samples/sample1.txt -p -m
# frequency output: ./result.csv
# parsed trees: ./samples/sample1.parsed
# matched subtrees: ./result_matches/
```

</details>

### Just Parse Texts and Exit <small><sup>[Top ▲](#contents)</sup></small>

If you only want to save the parsed trees and exit, you can use `--no-query`. This can be useful if you want to use the parsed trees for other purposes.

```sh
nsca samples/sample1.txt --no-query
# parsed trees: samples/sample1.parsed
nsca --text 'This is a test.' --no-query
# parsed trees: ./cmdline_text.parsed
```

### List Output Fields <small><sup>[Top ▲](#contents)</sup></small>

If you are not sure what the output fields represent, you can use `--list` to print a list of all the available output fields.

<details>

<summary>
<code>nsca --list</code>
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

### Print the Help Message <small><sup>[Top ▲](#contents)</sup></small>

If you call the `nsca` command without any arguments or options, it will return a help message.

## <a name="citing"></a> Citing <small><sup>[Top ▲](#contents)</sup></small>

If you use NeoSCA in your research, please cite as follows.

<details>

<summary>
BibTeX:
</summary>

```BibTeX
@misc{tan2022neosca,
title        = {NeoSCA: A Rewrite of L2 Syntactic Complexity Analyzer, version 0.0.35},
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

<pre>Tan, L. (2022). <i>NeoSCA: A Rewrite of L2 Syntactic Complexity Analyzer</i> (version 0.0.35) [Software]. Github. https://github.com/tanloong/neosca</pre>

</details>

<details>

<summary>
MLA (9th edition):
</summary>

<pre>Tan, Long. <i>NeoSCA: A Rewrite of L2 Syntactic Complexity Analyzer</i>. version 0.0.35, GitHub, 2022, https://github.com/tanloong/neosca.</pre>

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

NeoSCA is licensed under the [GNU General Public License version 2](https://github.com/tanloong/neosca/blob/master/LICENSE.txt) or later.
