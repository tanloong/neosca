# NeoSCA

[![build](https://github.com/tanloong/neosca/workflows/build/badge.svg)](https://github.com/tanloong/neosca/actions?query=workflow%3Abuild)
[![lint](https://github.com/tanloong/neosca/workflows/lint/badge.svg)](https://github.com/tanloong/neosca/actions?query=workflow%3ALint)
[![codecov](https://img.shields.io/codecov/c/github/tanloong/neosca)](https://codecov.io/gh/tanloong/neosca)
[![codacy](https://app.codacy.com/project/badge/Grade/6d49b7a0f3ac44b79d6fc6b87b303034)](https://www.codacy.com/gh/tanloong/neosca/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=tanloong/neosca&amp;utm_campaign=Badge_Grade)
[![pypi](https://img.shields.io/pypi/v/neosca)](https://pypi.org/project/neosca)
[![commit](https://img.shields.io/github/last-commit/tanloong/neosca)](https://github.com/tanloong/neosca/commits/master)
![support-version](https://img.shields.io/pypi/pyversions/neosca)
![platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgray)
[![downloads](https://static.pepy.tech/badge/neosca)](https://pepy.tech/project/neosca)
[![license](https://img.shields.io/github/license/tanloong/neosca)](https://github.com/tanloong/neosca/blob/master/LICENSE.txt)

![](img/testing-on-Windows.gif)

[简体中文](https://github.com/tanloong/neosca/blob/master/README_zh_cn.md) |
[繁體中文](https://github.com/tanloong/neosca/blob/master/README_zh_tw.md) |
English

NeoSCA is a rewrite of [L2 Syntactic Complexity Analyzer](http://personal.psu.edu/xxl13/downloads/l2sca.html) (L2SCA) which is developed by [Xiaofei Lu](http://personal.psu.edu/xxl13/index.html), with added support for Windows and an improved command-line interface for easier usage. The same as L2SCA, NeoSCA takes written English language samples in plain text format as input, and computes:

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

<a name="readme-top"></a>

## Contents

<!-- vim-markdown-toc GFM -->

* [Highlights](#highlights)
* [Install](#install)
* [Usage](#usage)
    * [Basic Usage](#basic-usage)
    * [Advanced Usage](#advanced-usage)
    * [Misc](#misc)
* [Citing](#citing)
* [Related Efforts](#related-efforts)
* [License](#license)
* [Contact](#contact)

<!-- vim-markdown-toc -->

## Highlights

* Works on **Windows**/macOS/Linux
* Flexible command-line options serving various needs

## Install

### Install NeoSCA

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

### Install Dependencies

NeoSCA depends on [Java](https://www.java.com/en/download/manual.jsp), [Stanford Parser](https://nlp.stanford.edu/software/lex-parser.shtml), and [Stanford Tregex](https://nlp.stanford.edu/software/tregex.html). NeoSCA provides an option to install all of them:

```sh
nsca --check-depends
```

Called with the `--check-depends`,
NeoSCA will download and unzip archive files of these three to
`%AppData%`
(for Windows users, usually `C:\\Users\\<username>\\AppData\\Roaming`) or
`~/.local/share`
(for macOS and Linux users),
and set the environment variable `JAVA_HOME`, `STANFORD_PARSER_HOME`, and `STANFORD_TREGEX_HOME`.
**If you have previously installed any of the three, you need to manually set the according environment variable.**

## Usage

NeoSCA is a CLI-based tool. You can see the help message by running `nsca --help` in your terminal.

### Basic Usage

#### Single Input

To analyze a single text file, use the command `nsca` followed by the file path.

```sh
nsca ./samples/sample1.txt
# frequency output: ./result.csv
```

A `result.csv` file will be generated in the current directory. You can specify a different output filename using `-o/--output-file`.

```sh
nsca ./samples/sample1.txt -o sample1.csv
# frequency output: ./sample1.csv
```

<details>

<summary>
When analyzing a text file with a filename that includes spaces, it is important to enclose the file path in single or double quotes. Assume you have a <code>sample 1.txt</code> to analyze:
</summary>

```sh
nsca "./samples/sample 1.txt"
```

This ensures that the entire filename including the spaces, is interpreted as a single argument. Without the double quotes, the command would interpret "./samples/sample" and "1.txt" as two separate arguments and the analysis would fail.

</details>

#### Multiple Input

To analyze multiple text files at once, simply list them after `nsca`.

```sh
cd ./samples/
nsca sample1.txt sample2.txt
```

You can also use [wildcards](https://www.gnu.org/savannah-checkouts/gnu/clisp/impnotes/wildcard.html#wildcard-syntax) to select multiple files at once.

```sh
cd ./samples/
nsca sample*.txt # every file whose name starts with "sample" and ends with ".txt"
nsca sample[1-9].txt sample10.txt # sample1.txt -- sample10.txt
nsca sample10[1-9].txt sample1[1-9][0-9].txt sample200.txt # sample101.txt -- sample200.txt
```

### Advanced Usage

#### Expand Wildcards

Use `--expand-wildcards` to print all files that match your wildcard pattern. This can help you ensure that your pattern matches all desired files and excludes any unwanted ones. Note that files that do not exist on the computer will not be included in the output, even if they match the specified pattern.

```sh
nsca sample10[1-9].txt sample1[1-9][0-9].txt sample200.txt --expand-wildcards
```

#### Treat Newlines as Sentence Breaks

Stanford Parser by default does not take newlines as sentence breaks during the sentence segmentation. To achieve this you can use:

```sh
nsca sample1.txt --newline-break always
```

The `--newline-break` has 3 legal values: `never` (default), `always`, and `two`.

+ `never` means to ignore newlines for the purpose of sentence splitting.
It is appropriate for continuous text with hard line breaks when just the non-whitespace characters should be used to determine sentence breaks.
+ `always` means to treat a newline as a sentence break, but there still may be
more than one sentences per line.
+ `two` means to take two or more consecutive newlines as a sentence break.
It is for text with hard line breaks and a blank line between paragraphs.

#### Select a Subset of Measures

NeoSCA by default outputs values of all of the available measures. You can use `--select` to only analyze measures that you are interested in. To see a full list of available measures, use `nsca --list`.

```sh
nsca --select VP T DC_C -- sample1.txt
```

To avoid the program taking input filenames as a selected measure and raising an error, use `--` to separate them from the measures. All arguments after `--` will be considered input filenames. Make sure to specify arguments except for input filenames at the left side of `--`.

#### Combine Subfiles

Use `-c`/`--combine-subfiles` to add up frequencies of the 9 syntactic structures of subfiles and compute values of the 14 syntactic complexity indices for the imaginary parent file. You can use this option multiple times to combine different lists of subfiles respectively. The `--` should be used to separate input filenames from input subfile-names.

```sh
nsca -c sample1-sub1.txt sample1-sub2.txt
nsca -c sample1-sub*.txt
nsca -c sample1-sub*.txt -c sample2-sub*.txt
nsca -c sample1-sub*.txt -c sample2-sub*.txt -- sample[3-9].txt
```

#### Skip Long Sentences

Use `--max-length` to only analyze sentences with lengths shorter than or equal to 100, for example.

```sh
nsca sample1.txt --max-length 100
```

When the `--max-length` is not specified, the program will try to analyze sentences of any lengths, but may [run out of memory](https://nlp.stanford.edu/software/parser-faq.html#k) trying to do so.

#### Reserve Intermediate Results

<details>

<summary>
NeoSCA by default only saves frequency output. To reserve the parsed trees, use <code>-p</code> or <code>--reserve-parsed</code>. To reserve matched subtrees, use <code>-m</code> or <code>--reserve-matched</code>.
</summary>

```sh
nsca samples/sample1.txt -p
# frequency output: ./result.csv
# parsed trees:     ./samples/sample1.parsed
nsca samples/sample1.txt -m
# frequency output: ./result.csv
# matched subtrees: ./result_matches/
nsca samples/sample1.txt -p -m
# frequency output: ./result.csv
# parsed trees:     ./samples/sample1.parsed
# matched subtrees: ./result_matches/
```

</details>

### Misc

#### Pass Text Through the Command Line

If you want to analyze text that is passed directly through the command line, you can use `--text` followed by the text.

```sh
nsca --text 'The quick brown fox jumps over the lazy dog.'
# frequency output: ./result.csv
```

#### JSON Output

You can generate a JSON file by:

```sh
nsca ./samples/sample1.txt --output-format json
# frequency output: ./result.json
nsca ./samples/sample1.txt -o sample1.json
# frequency output: ./sample1.json
```

#### Just Parse Text and Exit

If you only want to save the parsed trees and exit, you can use `--no-query`. This can be useful if you want to use the parsed trees for other purposes. When `--no-query` is specified, the `--reserve-parsed` will be automatically set.

```sh
nsca samples/sample1.txt --no-query
# parsed trees: samples/sample1.parsed
nsca --text 'This is a test.' --no-query
# parsed trees: ./cmdline_text.parsed
```

#### List Output Fields

Use `--list` to print a list of all the available output fields.

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

## Citing

If you use NeoSCA in your research, please cite as follows.

<details>

<summary>
BibTeX
</summary>

```BibTeX
@misc{tan2022neosca,
title        = {NeoSCA: A Rewrite of L2 Syntactic Complexity Analyzer, version 0.0.38},
author       = {Long Tan},
howpublished = {\url{https://github.com/tanloong/neosca}},
year         = {2022}
}
```

</details>

<details>

<summary>
APA (7th edition)
</summary>

<pre>Tan, L. (2022). <i>NeoSCA</i> (version 0.0.38) [Computer software]. Github. https://github.com/tanloong/neosca</pre>

</details>

<details>

<summary>
MLA (9th edition)
</summary>

<pre>Tan, Long. <i>NeoSCA</i>. version 0.0.38, GitHub, 2022, https://github.com/tanloong/neosca.</pre>

</details>

Also, you need to cite Xiaofei's article describing L2SCA.

<details>

<summary>
BibTeX
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
APA (7th edition)
</summary>

<pre>Lu, X. (2010). Automatic analysis of syntactic complexity in second language writing. <i>International Journal of Corpus Linguistics, 15</i>(4), 474-496.</pre>

</details>

<details>

<summary>
MLA (9th edition)
</summary>

<pre>Lu, Xiaofei. "Automatic Analysis of Syntactic Complexity in Second Language Writing." <i>International Journal of Corpus Linguistics</i>, vol. 15, no. 4, John Benjamins Publishing Company, 2010, pp. 474-96.</pre>

</details>

## Related Efforts

+ [L2SCA](https://sites.psu.edu/xxl13/l2sca/), the original implementation, written in Python, by [Xiaofei Lu](https://sites.psu.edu/xxl13)
+ [L2SCA online](https://aihaiyang.com/software/l2sca/), by [Haiyang Ai](https://aihaiyang.com/)
+ [TAASSC](https://www.linguisticanalysistools.org/taassc.html), written in Python, by [Kristopher Kyle]( https://kristopherkyle.github.io/professional-webpage/)
+ [L2SCA written in R](https://pennstateoffice365-my.sharepoint.com/personal/xxl13_psu_edu/_layouts/15/onedrive.aspx?id=%2Fpersonal%2Fxxl13%5Fpsu%5Fedu%2FDocuments%2Fother%2Dwork%2Fwebpage%2Fdownloads%2FL2SCA%5FR%2Ezip&parent=%2Fpersonal%2Fxxl13%5Fpsu%5Fedu%2FDocuments%2Fother%2Dwork%2Fwebpage%2Fdownloads&ga=1), by [Thomas Gaillat](https://perso.univ-rennes2.fr/thomas.gaillat), Anas Knefati, and Antoine Lafontaine
+ [FSCA](https://github.com/nvandeweerd/fsca) (French Syntactic Complexity Analyzer), written in R, by [Nate Vandeweerd](https://github.com/nvandeweerd)

## License

Distributed under the terms of the [GNU General Public License version 2](https://github.com/tanloong/neosca/blob/master/LICENSE.txt) or later.

## Contact

You can send bug reports, feature requests, or any questions via:

+ [GitHub Issues](https://github.com/tanloong/neosca/issues)
+ tanloong@foxmail.com
