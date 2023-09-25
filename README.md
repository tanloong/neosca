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

<!-- ![](img/testing-on-Windows.gif) -->

[简体中文](https://github.com/tanloong/neosca/blob/master/README_zh_cn.md)|
[繁體中文](https://github.com/tanloong/neosca/blob/master/README_zh_tw.md)|
English

NeoSCA is a fork of [Xiaofei Lu](http://personal.psu.edu/xxl13/index.html)'s [L2 Syntactic Complexity Analyzer](http://personal.psu.edu/xxl13/downloads/l2sca.html) (L2SCA), with added support for Windows and an improved command-line interface for easier usage. NeoSCA is written by Tan, Long (谭龙)。It accepts written English texts and computes the following measures:

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

* Cross-platform compatibility: Windows, macOS, and Linux
* Flexible command-line options to serve various needs
* Supports reading txt/docx/odt files
* Custom syntactic structure search/calculation

## Install

### Install NeoSCA

To install NeoSCA, you need to have [Python](https://www.python.org/) 3.7 or later installed on your system. You can check if you already have Python installed by running the following command in your terminal:

```sh
python --version
```

If Python is not installed, you can download and install it from [Python website](https://www.python.org/downloads/). Once you have Python installed, you can install `neosca` using `pip`:

```sh
pip install neosca
```

If you are in China and having trouble with slow download speeds or network issues, you can use the Tsinghua University PyPI mirror to install `neosca`:

```sh
pip install neosca -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Install dependencies

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

NeoSCA is a command-line tool. You can see the help message by running `nsca --help` in your terminal.

### Basic usage

#### Single input

To analyze a single file, use the command `nsca` followed by the file path.

```sh
nsca ./samples/sample1.txt
nsca ./samples/sample1.docx
```

Tables, figures, images, and other unrelated elements (except for headers and footers, which will be automatically ignored) should be manually removed before docx/odt files are analyzed.

After running the above command, a `result.csv` file will be generated in the current directory. You can specify a different output filename using `-o/--output-file`.

```sh
nsca ./samples/sample1.txt -o sample1.csv
# frequency output: ./sample1.csv
```

<details>

<summary>
When analyzing a file whose name includes spaces, it is important to enclose the file path in single or double quotes. Assume you have a <code>sample 1.txt</code> to analyze:
</summary>

```sh
nsca "./samples/sample 1.txt"
```

This ensures that the entire filename including the spaces, is interpreted as a single argument. Without the double quotes, the command would interpret "./samples/sample" and "1.txt" as two separate arguments and the analysis would fail.

</details>

#### Multiple input

Specify the input directory after `nsca`.

```
nsca samples/              # analyze every txt/docx file under the "samples/" directory
nsca samples/ --ftype txt  # analyze only txt files under "samples/"
nsca samples/ --ftype docx # analyze only docx files under "samples/"
```

Or simply list each file:

```sh
cd ./samples/
nsca sample1.txt sample2.txt
```

You can also use [wildcards](https://www.gnu.org/savannah-checkouts/gnu/clisp/impnotes/wildcard.html#wildcard-syntax) to select multiple files at once.

```sh
cd ./samples/
nsca sample*.txt                                           # every file whose name starts with "sample" and ends with ".txt"
nsca sample[1-9].txt sample10.txt                          # sample1.txt -- sample10.txt
nsca sample10[1-9].txt sample1[1-9][0-9].txt sample200.txt # sample101.txt -- sample200.txt
```

### Advanced usage

#### Expand wildcards

Use `--expand-wildcards` to print all files that match your wildcard pattern. This can help you ensure that your pattern matches all desired files and excludes any unwanted ones. Note that files that do not exist on the computer will not be included in the output, even if they match the specified pattern.

```sh
nsca sample10[1-9].txt sample1[1-9][0-9].txt sample200.txt --expand-wildcards
```

#### Treat newlines as sentence breaks

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

#### Configuration file

You can use a configuration file to define custom syntactic structures to search or calculate.

The default configuration filename for neosca is `nsca.json`, neosca will try to find `nsca.json` in current working directory. Alternatively, you can provide your own configuration file with `nsca --config <your_config_file>`. The configuration file should be in JSON format and named with `.json` extension.

```json
{
    "structures": [
        {
            "name": "VP1",
            "description": "regular verb phrases",
            "tregex_pattern": "VP > S|SINV|SQ"
        },
        {
            "name": "VP2",
            "description": "verb phrases in inverted yes/no questions or in wh-questions",
            "tregex_pattern": "MD|VBZ|VBP|VBD > (SQ !< VP)"
        },
        {
            "name": "VP",
            "description": "verb phrases",
            "value_source": "VP1 + VP2"
        }
    ]
}
```

Above is a part of neosca's built-in structure definitions. Each definition follows a key-value pair format, where both the key and value should be enclosed in quotation marks.

There are two approaches to define a structure: using `tregex_pattern` or `value_source`. `tregex_pattern` represents the formal definition in Tregex syntax. Structures defined through `tregex_pattern` will be searched and counted by running Stanford Tregex against input text. For instructions about how to write a Tregex pattern, see:

+ Chapter 6 of Xiaofei's book [*Computational Methods for Corpus Annotation and Analysis*](http://www.springer.com/education+%26+language/linguistics/book/978-94-017-8644-7?otherVersion=978-94-017-8645-4)
+ [Powerpoint tutorial](https://nlp.stanford.edu/software/tregex/The_Wonderful_World_of_Tregex.ppt) for Tregex by Galen Andrew
+ [The TregexPattern javadoc page](http://nlp.stanford.edu/nlp/javadoc/javanlp/edu/stanford/nlp/trees/tregex/TregexPattern.html)

`value_source` specifies an arithmetic operation on values of other structures to calculate the value of the structure being defined. `value_source` can include names of other structures, integers, decimals, `+`, `-`, `*`, `/`, `(` and `)`. `value_source` are tokenized using Python's standard library `tokenize`, which is specifically designed for Python source code. The name of a structure that is refered to in a `value_source` should adhere to the naming convention of Python variables (composed of *letters*, *numbers*, and *underscores*, cannot start with a *number*; *letters* refer to those characters defined in the Unicode character database as "Letter", such as English letters and Chinese characters), or otherwise the name will not be correctly recognized.

The `value_source` definition can be nested, which means that dependant structures in turn can also be defined through `value_source` and rely on others, forming a tree-like relationship. But the terminal structures must be defined by `tregex_pattern` to avoid circular definition.

Structures can be defined using either `tregex_pattern` or `value_source`, but not both simultaneously. The `name` attribute will be used for `--select` option. The `description` attribute is optional, you can omit it for convenience.

#### Select a subset of measures

NeoSCA by default outputs values of all of the available measures. You can use `--select` to only analyze measures that you are interested in. To see a full list of available measures, use `nsca --list`.

```sh
nsca --select VP T DC/C -- sample1.txt
```

To avoid the program taking input filenames as a selected measure and raising an error, use `--` to separate them from the measures. All arguments after `--` will be considered input filenames. Make sure to specify arguments except for input filenames at the left side of `--`.

#### Combine subfiles

Use `-c`/`--combine-subfiles` to add up frequencies of the 9 syntactic structures of subfiles and compute values of the 14 syntactic complexity indices for the imaginary parent file. You can use this option multiple times to combine different lists of subfiles respectively. The `--` should be used to separate input filenames from input subfile-names.

```sh
nsca -c sample1-sub1.txt sample1-sub2.txt
nsca -c sample1-sub*.txt
nsca -c sample1-sub*.txt -c sample2-sub*.txt
nsca -c sample1-sub*.txt -c sample2-sub*.txt -- sample[3-9].txt
```

#### Skip long sentences

Use `--max-length` to only analyze sentences with lengths shorter than or equal to 100, for example.

```sh
nsca sample1.txt --max-length 100
```

When the `--max-length` is not specified, the program will try to analyze sentences of any lengths, but may [run out of memory](https://nlp.stanford.edu/software/parser-faq.html#k) trying to do so.

#### Reserve intermediate results

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

#### Pass text through the command line

If you want to analyze text that is passed directly through the command line, you can use `--text` followed by the text.

```sh
nsca --text 'The quick brown fox jumps over the lazy dog.'
# frequency output: ./result.csv
```

#### JSON output

You can generate a JSON file by:

```sh
nsca ./samples/sample1.txt --output-format json
# frequency output: ./result.json
nsca ./samples/sample1.txt -o sample1.json
# frequency output: ./sample1.json
```

#### Just parse text and exit

If you only want to save the parsed trees and exit, you can use `--no-query`. This can be useful if you want to use the parsed trees for other purposes. When `--no-query` is specified, the `--reserve-parsed` will be automatically set.

```sh
nsca samples/sample1.txt --no-query
# parsed trees: samples/sample1.parsed
nsca --text 'This is a test.' --no-query
# parsed trees: ./cmdline_text.parsed
```

#### Parse trees as input

By default, the program expects raw text as input that will be parsed before querying. If you already have parsed input files, use `--no-parse` to indicate that the program should skip the parsing step and proceed directly to querying. When this flag is set, the is_skip_querying and reserve_parsed are automatically set as False.

```sh
nsca samples/sample1.parsed --no-parse
```

#### List built-in measures

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

#### Tregex interface

NeoSCA has a Tregex command line interface `nsca-tregex`, which behaves similar as `tregex.sh` from Tregex package, with additional support for Windows.

#### Lexical complexity analysis

NeoSCA provides an `nsca-lca` command to do the lexical complexity analysis mirroring the functionality of [LCA (Lexical Complexity Analyzer)](https://sites.psu.edu/xxl13/lca/). Below are the available measures:

<!-- {{{ LCA measures -->
<details>
<summary>
Measures of Lexical Density and Sophistication
</summary>

|Measure|Formula|
|-|-|
|Lexical Density|![Formula](/img/ld.svg "the ratio of the number of lexical words to the number of words")|
|Lexical Sophistication-I|![Formula](/img/ls1.svg "the ratio of the number of sophisticated lexical words to the total number of lexical words")|
|Lexical Sophistication-II|![Formula](/img/ls2.svg "the ratio of the number of sophisticated word types to the total number of word types")|
|Verb Sophistication-I|![Formula](/img/vs1.svg "the ratio of the number of sophisticated verb types to the total number of verbs")|
|Corrected Verb Sophistication-I|![Formula](/img/cvs1.svg "the ratio of the number of sophisticated verb types to the square root of two times the number of verbs")|
|Verb Sophistication-II|![Formula](/img/vs2.svg "the ratio of the number of sophisticated verb types squared to the number of verbs")|

</details>

<details>
<summary>
Measures of Lexical Variation
</summary>

|Measure|Formula|
|-|-|
|Number of Different Words|![Formula](/img/ndw.svg "the number of word types")|
|Number of Different Words (first 50 words)|![Formula](/img/ndw-50.svg "no hover text for this formula")|
|Number of Different Words (expected random 50)|![Formula](/img/ndw-er50.svg "no hover text for this formula")|
|Number of Different Words (expected sequence 50)|![Formula](/img/ndw-es50.svg "no hover text for this formula")|
|Type-Token Ratio|![Formula](/img/ttr.svg "the ratio of the number of word types to the number of words")|
|Mean Segmental Type-Token Ratio (50)|![Formula](/img/msttr-50.svg "divide a sample into successive 50-word segments, discard the remaining text with fewer words than 50, and then calculate the average TTR of all segments")|
|Corrected Type-Token Ratio|![Formula](/img/cttr.svg "the ratio of the number of word types to the square root of two times the total number of words")|
|Root Type-Token Ratio|![Formula](/img/rttr.svg "the ratio of the number of word types to the square root of the number of words")|
|Bilogarithmic Type-Token Ratio|![Formula](/img/logttr.svg "no hover text for this formula")|
|Uber Index|![Formula](/img/uber.svg "no hover text for this formula")|
|Lexical Word Variation|![Formula](/img/lv.svg "the ratio of the number of lexical word types to the total number of lexical words")|
|Verb Variation-I|![Formula](/img/vv1.svg "the ratio of the number of verb types to the total number of verbs")|
|Squared Verb Variation-I|![Formula](/img/svv1.svg "the ratio of the number of verb types squared to the number of verbs")|
|Corrected Verb Variation-I|![Formula](/img/cvv1.svg "the ratio of the number of verb types to the square root of two times the total number of verbs")|
|Verb Variation-II|![Formula](/img/vv2.svg "the ratio of the number of verb types to the number of lexical words")|
|Noun Variation|![Formula](/img/nv.svg "the ratio of the number of noun types to the number of lexical words")|
|Adjective Variation|![Formula](/img/adjv.svg "the ratio of the number of adjective types to the number of lexical words")|
|Adverb Variation|![Formula](/img/advv.svg "the ratio of the number of adverb types to the number of lexical words")|
|Modifier Variation|![Formula](/img/modv.svg "the ratio of the number of modifier (both adjective and adverb) types to the number of lexical words")|

</details>
<!-- }}} -->

```sh
nsca-lca sample.txt # single input file
nsca-lca samples/   # multiple input files
```

## Citing

If you use NeoSCA in your research, please cite as follows.

<details>

<summary>
BibTeX
</summary>

```BibTeX
@misc{tan2022neosca,
title        = {NeoSCA: A Fork of L2 Syntactic Complexity Analyzer, version 0.0.53},
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

<pre>Tan, L. (2022). <i>NeoSCA</i> (version 0.0.53) [Computer software]. Github. https://github.com/tanloong/neosca</pre>

</details>

<details>

<summary>
MLA (9th edition)
</summary>

<pre>Tan, Long. <i>NeoSCA</i>. version 0.0.53, GitHub, 2022, https://github.com/tanloong/neosca.</pre>

</details>

Also, you need to cite Xiaofei's article describing L2SCA.

<details>

<summary>
BibTeX
</summary>

```BibTeX
@article{xiaofei2010automatic,
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

If you use the lexical complexity analyzing feature, please cite Xiaofei's article about LCA.

<details>

<summary>
BibTeX
</summary>

```BibTeX
@article{xiaofei2012relationship,
author  = {Xiaofei Lu},
title   = {The Relationship of Lexical Richness to the Quality of ESL Learners' Oral Narratives},
journal = {The Modern Language Journal},
volume  = {96},
number  = {2},
pages   = {190-208},
doi     = {https://doi.org/10.1111/j.1540-4781.2011.01232\_1.x},
year    = {2012}
}
```

</details>

<details>

<summary>
APA (7th edition)
</summary>

<pre>Lu, X. (2012). The relationship of lexical richness to the quality of ESL learners' oral narratives. <i>The Modern Language Journal, 96</i>(2), 190-208.</pre>

</details>

<details>

<summary>
MLA (9th edition)
</summary>

<pre>Lu, Xiaofei. "The Relationship of Lexical Richness to the Quality of ESL Learners' Oral Narratives." <i>The Modern Language Journal</i>, vol. 96, no. 2, Wiley-Blackwell, 2012, pp. 190-208.</pre>

</details>


## Related efforts

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
