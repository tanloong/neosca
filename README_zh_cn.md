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

NeoSCA 是 [Xiaofei Lu](http://personal.psu.edu/xxl13/index.html) 的 [L2 Syntactic Complexity Analyzer (L2SCA)](http://personal.psu.edu/xxl13/downloads/l2sca.html) 的重写版本，添加了对 Windows 的支持和更多的命令行选项。与 L2SCA 一样，NeoSCA 对 txt 格式的英文语料统计以下内容：

<details>

<summary>
9 种句法结构的频次
</summary>

1. 单词
2. 句子
3. 动词短语
4. 子句
5. T 单位
6. 从属子句
7. 复杂 T 单位
8. 并列短语
9. 复杂名词性短语

</details>

<details>

<summary>
14 种句法复杂度指标的值
</summary>

1. 平均句子长度
2. 平均 T 单位长度
3. 平均子句长度
4. 每个句子中子句的数量
5. 每个 T 单位中的动词短语数量
6. 每个 T 单位中的子句数量
7. 从属子句比率，即每个子句中的从属子句数量
8. 每个 T 单位中的从属子句数量 
9. 并列句比率，即每个句子中的 T 单位数量
10. 复杂 T 单位比率，即每个 T 单位中的复杂 T 单位数量
11. 每个 T 单位中的并列短语数量
12. 每个子句中的并列短语数量
13. 每个 T 单位中的复杂名词性短语数量
14. 每个子句中的复杂名词性短语数量

</details>

<a name="readme-top"></a>

## 目录

<!-- vim-markdown-toc GFM -->

* [Highlights](#highlights)
* [安装](#安装)
* [使用](#使用)
    * [基本使用](#基本使用)
    * [进阶使用](#进阶使用)
    * [其他](#其他)
* [引用](#引用)
* [类似软件](#类似软件)
* [许可证](#许可证)
* [联系](#联系)

<!-- vim-markdown-toc -->

## Highlights

* 支持 **Windows**、macOS 和 Linux 系统。
* 提供灵活的命令行选项

## 安装

### 安装 NeoSCA

要安装 NeoSCA，你需要在电脑上安装 Python 3.7 或更高版本。你可以在终端中运行以下命令来检查是否已安装 Python：

```sh
python --version
```

如果未安装 Python，则可以从 [Python 官网](https://www.python.org/downloads/) 下载并安装。安装了 Python 后，可以使用 pip 安装 NeoSCA：

```sh
pip install neosca
```

国内用户可以从镜像网站下载：

```sh
pip install neosca -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 安装依赖

运行 NeoSCA 需要 [Java](https://www.java.com/en/download/manual.jsp) 8 或更高版本、[Stanford Parser](https://nlp.stanford.edu/software/lex-parser.shtml) 和 [Stanford Tregex](https://nlp.stanford.edu/software/tregex.html)。NeoSCA 提供了安装这些依赖的选项：

```sh
nsca --check-depends
```

运行上面这条命令，NeoSCA 会将依赖的压缩包下载并解压到 `%AppData%` (Windows；`C:\\Users\\<username>\\AppData\\Roaming`) 或者 `~/.local/share` (macOS 和 Linux)，然后设置 3 个环境变量 `JAVA_HOME`、`STANFORD_PARSER_HOME` 和 `STANFORD_TREGEX_HOME`。**如果你之前已经下载过某个/某些依赖，需要手动设置对应的环境变量。**

## 使用

NeoSCA 是通过命令行来使用的。在终端中输入 `nsca --help` 加回车可以查看它的帮助信息。

### 基本使用

#### 单个输入文件

在终端中输入 `nsca` 右边加输入文件的路径。

```sh
nsca ./samples/sample1.txt
# 输出文件: ./result.csv
```

输出文件会保存在当前路径下，默认文件名是 `result.csv`，使用 `-o/--output-file` 可以自定义输出文件名。

```sh
nsca ./samples/sample1.txt -o sample1.csv
# 输出文件: ./sample1.csv
```

<details>

<summary>
如果输入文件的路径包含空格，需要将它用单引号或双引号包裹。比如分析 <code>sample 1.txt</code> 应该用：
</summary>

```sh
nsca "./samples/sample 1.txt"
```

这可以让包括空格在内的整个路径被识别为单个输入文件，否则 “./samples/sample” 和 “1.txt” 会被认为是两个文件，因为这两个文件都不存在，所以程序会运行失败。

</details>

#### 多个输入文件

以空格为间隔，在 `nsca` 的右边列出输入文件：

```sh
cd ./samples/
nsca sample1.txt sample2.txt
```

或者使用 [通配符](https://www.gnu.org/savannah-checkouts/gnu/clisp/impnotes/wildcard.html#wildcard-syntax)：

```sh
cd ./samples/
nsca sample*.txt # 指定所有文件名以 “sample” 开头并且以 “.txt” 结尾的文件
nsca sample[1-9].txt sample10.txt # sample1.txt -- sample10.txt
nsca sample10[1-9].txt sample1[1-9][0-9].txt sample200.txt # sample101.txt -- sample200.txt
```

### 进阶使用

#### 展开通配符

如果你要检验输入的通配符是否匹配且只匹配到想要分析的文件，可以使用 `--expand-wildcards` 来显示通配符的展开结果。注意这只会显示存在的文件，如果展开范围里的某个文件并不存在，那么它不会显示在展开结果里。

```sh
nsca sample10[1-9].txt sample1[1-9][0-9].txt sample200.txt --expand-wildcards
```

#### 将换行符作为句子边界

NeoSCA 所调用的 Stanford Parser 在分句时，默认不会把换行符当作句子边界。要实现这个效果可以用：

```sh
nsca sample1.txt --newline-break always
```

`--newline-break` 有 3 个可选值：`never` (默认)、`always` 和 `two`。

+ `never` 表示在分句时忽略换行符，只使用非空白字符来确定句子边界，适用于存在句内换行的文本。
+ `always` 表示将换行符作为句子边界，但两个换行符之间仍可以有多个句子。
+ `two` 表示将连续的两个 (或更多) 换行符作为句子边界，适用于存在句内换行、段落之间以空行间隔的文本。

#### 只计算一部分指标

NeoSCA 默认计算所有指标的值，使用 `--select` 可以只计算选定指标的值。要查看所有的可选指标可以用 `nsca --list`。

```sh
nsca --select VP T DC_C -- sample1.txt
```

注意需要使用 `--` 将选定指标与输入文件名区分开。`--` 右边的所有参数都将被视为输入文件名，请确保在 `--` 的左边指定除了输入文件名之外的参数。

#### 合并子文件

使用 `-c`/`--combine-subfiles` 选项可以累加子文件中 9 种句法结构的频次并计算原文件的 14 种句法复杂度指标的值。你可以使用多个 `-c` 来分别合并不同的子文件列表。命令中同时含有输入子文件名和输入文件名时需要使用 `--` 把二者区分开。

```sh
nsca -c sample1-sub1.txt sample1-sub2.txt
nsca -c sample1-sub*.txt
nsca -c sample1-sub*.txt -c sample2-sub*.txt
nsca -c sample1-sub*.txt -c sample2-sub*.txt -- sample[3-9].txt
```

#### 跳过长句子

使用 `--max-length` 选项来只分析不超过 (≤) 特定长度的句子。

```sh
nsca sample1.txt --max-length 100
```

当没有指定 `--max-length` 时，NeoSCA 会分析所有句子，但可能会导致[内存超出限制](https://nlp.stanford.edu/software/parser-faq.html#k)。

#### 保存中间结果

<details>

<summary>
NeoSCA 默认只保存各指标的计算结果，如果要保存对输入文件进行短语结构分析得到的句法树，请使用 <code>-p</code> 或 <code>--reserve-parsed</code>。如果要保存查找句法树时得到的符合对应句法结构的子树，请使用 <code>-m</code> 或 <code>--reserve-matched</code>。
</summary>

```sh
nsca samples/sample1.txt -p
# 频次结果: ./result.csv
# 句法树:     ./samples/sample1.parsed
nsca samples/sample1.txt -m
# 频次结果: ./result.csv
# 查找到的子树: ./result_matches/
nsca samples/sample1.txt -p -m
# 频次结果: ./result.csv
# 句法树:     ./samples/sample1.parsed
# 查找到的子树: ./result_matches/
```

</details>

### 其他

#### 从命令行传入文本

要直接从命令行传入文本可以使用 `--text`。

```sh
nsca --text 'The quick brown fox jumps over the lazy dog.'
# 输出结果: ./result.csv
```

#### 输出 Json 文件

要输出 Json 格式的文件可以通过以下方式：

```sh
nsca ./samples/sample1.txt --output-format json
# 输出结果: ./result.json
nsca ./samples/sample1.txt -o sample1.json
# 输出结果: ./sample1.json
```

#### 只做句法分析

如果你不需要各指标的计算结果，只需要得到短语结构句法树用于其他用途，可以使用 `--no-query`，NeoSCA 会只对输入文件做短语结构分析并保存得到的句法树，跳过后续查找句法树的环节。

```sh
nsca samples/sample1.txt --no-query
# 句法树: samples/sample1.parsed
nsca --text 'This is a test.' --no-query
# 句法树: ./cmdline_text.parsed
```

#### 列出 9 种句法结构和 14 个句法复杂度指标

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

## 引用

如果你在发表的成果中使用了 NeoSCA，请按如下信息进行引用。

<details>

<summary>
BibTeX
</summary>

```BibTeX
@misc{tan2022neosca,
title        = {NeoSCA: A Rewrite of L2 Syntactic Complexity Analyzer, version 0.0.37},
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

<pre>Tan, L. (2022). <i>NeoSCA</i> (version 0.0.37) [Computer software]. Github. https://github.com/tanloong/neosca</pre>

</details>

<details>

<summary>
MLA (9th edition)
</summary>

<pre>Tan, Long. <i>NeoSCA</i>. version 0.0.37, GitHub, 2022, https://github.com/tanloong/neosca.</pre>

</details>

同时，你也需要引用 Xiaofei 介绍 L2SCA 的文章：

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

## 类似软件

+ [L2SCA](https://sites.psu.edu/xxl13/l2sca/) 原版，使用的是 Python，作者 [Xiaofei Lu](https://sites.psu.edu/xxl13)
+ [L2SCA online](https://aihaiyang.com/software/l2sca/)，作者 [Haiyang Ai](https://aihaiyang.com/)
+ [L2SCA included in TAASSC](https://www.linguisticanalysistools.org/taassc.html)，使用的是 Python，作者 [Kristopher Kyle]( https://kristopherkyle.github.io/professional-webpage/)
+ [L2SCA R 语言版](https://pennstateoffice365-my.sharepoint.com/personal/xxl13_psu_edu/_layouts/15/onedrive.aspx?id=%2Fpersonal%2Fxxl13%5Fpsu%5Fedu%2FDocuments%2Fother%2Dwork%2Fwebpage%2Fdownloads%2FL2SCA%5FR%2Ezip&parent=%2Fpersonal%2Fxxl13%5Fpsu%5Fedu%2FDocuments%2Fother%2Dwork%2Fwebpage%2Fdownloads&ga=1)，作者 [Thomas Gaillat](https://perso.univ-rennes2.fr/thomas.gaillat)、Anas Knefati 和 Antoine Lafontaine
+ [FSCA](https://github.com/nvandeweerd/fsca) (法语句法复杂度分析器)，使用的是 R 语言，作者 [Nate Vandeweerd](https://github.com/nvandeweerd)

## FAQ

### NeoSCA 有词数限制吗？

NeoSCA 没有词数限制，但也不是无论多大的文件都能处理，决定它能处理多大文件的是运行它需要的内存。 我试了试用 NeoSCA v0.0.37 分析 The Great Gatsby (原始文件：https://www.gutenberg.org/cache/epub/64317/pg64317.txt)，把原始文件简单处理之后用 NeoSCA 分析的时候有 4 万 8 千词 (https://controlc.com/d3072aa6)，可以正常出结果 (https://controlc.com/7e289eb6)。

NeoSCA 使用 Stanford Parser 分析输入文本，再使用 Tregex 在分析结果中查找句法结构。Tregex 需要的内存比较少，决定 NeoSCA 需要多少内存的主要是 Stanford Parser。Stanford Parser 所需要的内存既与要分析的单个句子的长度有关，也与要分析的文件的总长度有关。

1. Stanford Parser 分析一个 100 词的句子需要 350M 内存 (https://nlp.stanford.edu/software/parser-faq.html#k)，NeoSCA 设置的最大内存限制是 3G。 如果一个句子太太太长，比如多个分句用分号连接成一个句子，就会报错 (OutOfMemoryError)。

对这种情况，即使这个句子所在的输入文件很小，NeoSCA 也处理不了。解决办法是找到这种句子，用句号/问号/叹号把它们拆分成多个句子。如果你下载的 NeoSCA 的版本是 0.0.36+，也可以使用 --max-length 来跳过长句子 (https://gitee.com/tanloong/neosca#skip-long-sentences)。 比如 nsca --max-length 100 sample.txt 的意思是只分析长度小于等于 100 的句子，长度大于 100 的句子不会被 Stanford Parser 分析，所以它们的 9 个句法结构的频次和 14 个句法复杂度指标的值也不会体现在输出结果里。

2.1 如果输入文件里没有太太太长的句子，NeoSCA v0.0.35- 会把正在分析的那个文件里的整个文本一次性发送给 Stanford Parser，需要的内存取决于那个文件的大小。

NeoSCA v0.0.36+ 添加了 --newline-break 选项 (https://gitee.com/tanloong/neosca#treat-newlines-as-sentence-breaks)，这个选项有 3 个可选值：never (默认)、always、two。如果 --newline-break 被设置为 never (默认就是 never)，NeoSCA 在分析一个文件时会把里面的整个文本一次性发送给 Stanford Parser，需要的内存也取决于整个文件的大小。

对这种情况，如果出现 OutOfMemoryError，只能把输入文件拆分成多个子文件再分析，但这么做就只能得到子文件的 14 个指标的值，而且不能把子文件的这些值简单地加起来求平均来当作原文件的值，因为没有考虑每个子文件的权重，要得到原文件的值只能在 Excel 里把各子文件的 9 种句法结构的频次分别加起来，然后手动计算 14 个指标的值。NeoSCA v0.0.36+ 添加了 --combine-subfiles 选项 (https://gitee.com/tanloong/neosca#combine-subfiles)，可以自动进行这个手动计算的过程。

2.2 如果 --newline-break 被设置为 always，NeoSCA 会先把文本以单个换行符为间隔切分成很多段落，然后一段一段地发送给 Stanford Parser，需要的内存取决于正在被分析的那个段落的大小；当--newline-break 被设置为 two 时，NeoSCA 会先把文本以空行作为间隔切分成很多段落，然后一段一段地发送给 Stanford Parser，需要的内存取决于正在被分析的那个段落的大小。

对这种情况，应该不会有 OutOfMemoryError 的问题 (我感觉)，因为这两种段落都不会太长(吧)。如果还是出现了 OutOfMemoryError，可能实际上是上面第1点里的问题，或者段落确实太长了。解决办法见上面第1点和第2.1点。

## 许可证

根据 [GNU通用公共许可证第2版](https://github.com/tanloong/neosca/blob/master/LICENSE.txt) 或更高版本的条款分发。

## 联系

你可以通过以下方式发送错误报告、功能请求或任何问题：

+ [GitHub Issues](https://github.com/tanloong/neosca/issues)
+ tanloong@foxmail.com