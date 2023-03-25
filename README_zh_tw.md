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
繁體中文 |
[English](https://github.com/tanloong/neosca#readme)

NeoSCA 是 [Xiaofei Lu](http://personal.psu.edu/xxl13/index.html) 的 [L2 Syntactic Complexity Analyzer (L2SCA)](http://personal.psu.edu/xxl13/downloads/l2sca.html) 的重寫版本，添加了對 Windows 的支持和更多的命令行選項。與 L2SCA 一樣，NeoSCA 對 txt 格式的英文語料統計以下內容：

<details>

<summary>
9 種句法結構的頻次
</summary>

1. 單詞
2. 句子
3. 動詞短語
4. 子句
5. T 單位
6. 從屬子句
7. 復雜 T 單位
8. 并列短語
9. 復雜名詞性短語

</details>

<details>

<summary>
14 種句法復雜度指標的值
</summary>

1. 平均句子長度
2. 平均 T 單位長度
3. 平均子句長度
4. 每個句子中子句的數量
5. 每個 T 單位中的動詞短語數量
6. 每個 T 單位中的子句數量
7. 從屬子句比率，即每個子句中的從屬子句數量
8. 每個 T 單位中的從屬子句數量 
9. 并列句比率，即每個句子中的 T 單位數量
10. 復雜 T 單位比率，即每個 T 單位中的復雜 T 單位數量
11. 每個 T 單位中的并列短語數量
12. 每個子句中的并列短語數量
13. 每個 T 單位中的復雜名詞性短語數量
14. 每個子句中的復雜名詞性短語數量

</details>

<a name="readme-top"></a>

## 目錄

<!-- vim-markdown-toc GFM -->

* [Highlights](#highlights)
* [安裝](#安裝)
* [使用](#使用)
    * [基本使用](#基本使用)
    * [進階使用](#進階使用)
    * [其他](#其他)
* [引用](#引用)
* [類似軟件](#類似軟件)
* [許可證](#許可證)
* [聯繫](#聯繫)

<!-- vim-markdown-toc -->

## Highlights

* 支持 **Windows**、macOS 和 Linux 系統。
* 提供靈活的命令行選項

## 安裝

### 安裝 NeoSCA

要安裝 NeoSCA，你需要在電腦上安裝 Python 3.7 或更高版本。你可以在終端中運行以下命令來檢查是否已安裝 Python：

```sh
python --version
```

如果未安裝 Python，則可以從 [Python 官網](https://www.python.org/downloads/) 下載並安裝。安裝了 Python 後，可以使用 pip 安裝 NeoSCA：

```sh
pip install neosca
```

國內用戶可以從鏡像網站下載：

```sh
pip install neosca -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 安裝依賴

運行 NeoSCA 需要 [Java](https://www.java.com/en/download/manual.jsp) 8 或更高版本、[Stanford Parser](https://nlp.stanford.edu/software/lex-parser.shtml) 和 [Stanford Tregex](https://nlp.stanford.edu/software/tregex.html)。NeoSCA 提供了安裝這些依賴的選項：

```sh
nsca --check-depends
```

運行上面這條命令，NeoSCA 會將依賴的壓縮包下載並解壓到 `%AppData%` (Windows；`C:\\Users\\<username>\\AppData\\Roaming`) 或者 `~/.local/share` (macOS 和 Linux)，然後設置 3 個環境變量 `JAVA_HOME`、`STANFORD_PARSER_HOME` 和 `STANFORD_TREGEX_HOME`。**如果你之前已經下載過某個/某些依賴，需要手動設置對應的環境變量。**

## 使用

NeoSCA 是通過命令行來使用的。在終端中輸入 `nsca --help` 加回車可以查看它的幫助信息。

### 基本使用

#### 單個輸入文件

在終端中輸入 `nsca` 右邊加輸入文件的路徑。

```sh
nsca ./samples/sample1.txt
# 輸出文件: ./result.csv
```

輸出文件會保存在當前路徑下，默認文件名是 `result.csv`，使用 `-o/--output-file` 可以自定義輸出文件名。

```sh
nsca ./samples/sample1.txt -o sample1.csv
# 輸出文件: ./sample1.csv
```

<details>

<summary>
如果輸入文件的路徑包含空格，需要將它用單引號或雙引號包裹。比如分析 <code>sample 1.txt</code> 應該用：
</summary>

```sh
nsca "./samples/sample 1.txt"
```

這可以讓包括空格在內的整個路徑被識別為單個輸入文件，否則 “./samples/sample” 和 “1.txt” 會被認為是兩個文件，因為這兩個文件都不存在，所以程序會運行失敗。

</details>

#### 多個輸入文件

以空格為間隔，在 `nsca` 的右邊列出輸入文件：

```sh
cd ./samples/
nsca sample1.txt sample2.txt
```

或者使用 [通配符](https://www.gnu.org/savannah-checkouts/gnu/clisp/impnotes/wildcard.html#wildcard-syntax)：

```sh
cd ./samples/
nsca sample*.txt # 指定所有文件名以 “sample” 開頭並且以 “.txt” 結尾的文件
nsca sample[1-9].txt sample10.txt # sample1.txt -- sample10.txt
nsca sample10[1-9].txt sample1[1-9][0-9].txt sample200.txt # sample101.txt -- sample200.txt
```

### 進階使用

#### 展開通配符

如果你要檢驗輸入的通配符是否匹配且只匹配到想要分析的文件，可以使用 `--expand-wildcards` 來顯示通配符的展開結果。注意這只會顯示存在的文件，如果展開範圍裡的某個文件並不存在，那麼它不會顯示在展開結果裡。

```sh
nsca sample10[1-9].txt sample1[1-9][0-9].txt sample200.txt --expand-wildcards
```

#### 將換行符作為句子邊界

NeoSCA 所調用的 Stanford Parser 在分句時，默認不會把換行符當作句子邊界。要實現這個效果可以用：

```sh
nsca sample1.txt --newline-break always
```

`--newline-break` 有 3 個可選值：`never` (默認)、`always` 和 `two`。

+ `never` 表示在分句時忽略換行符，只使用非空白字符來確定句子邊界，適用於存在句內換行的文本。
+ `always` 表示將換行符作為句子邊界，但兩個換行符之間仍可以有多個句子。
+ `two` 表示將連續的兩個 (或更多) 換行符作為句子邊界，適用於存在句內換行、段落之間以空行間隔的文本。

#### 只計算一部分指標

NeoSCA 默認計算所有指標的值，使用 `--select` 可以只計算選定指標的值。要查看所有的可選指標可以用 `nsca --list`。

```sh
nsca --select VP T DC_C -- sample1.txt
```

注意需要使用 `--` 將選定指標與輸入文件名區分開。`--` 右邊的所有參數都將被視為輸入文件名，請確保在 `--` 的左邊指定除了輸入文件名之外的參數。

#### 合併子文件

使用 `-c`/`--combine-subfiles` 選項可以累加子文件中 9 種句法結構的頻次並計算原文件的 14 種句法復雜度指標的值。你可以使用多個 `-c` 來分別合併不同的子文件列表。命令中同時含有輸入子文件名和輸入文件名時需要使用 `--` 把二者區分開。

```sh
nsca -c sample1-sub1.txt sample1-sub2.txt
nsca -c sample1-sub*.txt
nsca -c sample1-sub*.txt -c sample2-sub*.txt
nsca -c sample1-sub*.txt -c sample2-sub*.txt -- sample[3-9].txt
```

#### 跳過長句子

使用 `--max-length` 選項來只分析不超過 (≤) 特定長度的句子。

```sh
nsca sample1.txt --max-length 100
```

當沒有指定 `--max-length` 時，NeoSCA 會分析所有句子，但可能會導致[內存超出限制](https://nlp.stanford.edu/software/parser-faq.html#k)。

#### 保存中間結果

<details>

<summary>
NeoSCA 默認只保存各指標的計算結果，如果要保存對輸入文件進行短語結構分析得到的句法樹，請使用 <code>-p</code> 或 <code>--reserve-parsed</code>。如果要保存查找句法樹時得到的符合對應句法結構的子樹，請使用 <code>-m</code> 或 <code>--reserve-matched</code>。
</summary>

```sh
nsca samples/sample1.txt -p
# 頻次結果: ./result.csv
# 句法樹:     ./samples/sample1.parsed
nsca samples/sample1.txt -m
# 頻次結果: ./result.csv
# 查找到的子樹: ./result_matches/
nsca samples/sample1.txt -p -m
# 頻次結果: ./result.csv
# 句法樹:     ./samples/sample1.parsed
# 查找到的子樹: ./result_matches/
```

</details>

### 其他

#### 從命令行傳入文本

要直接從命令行傳入文本可以使用 `--text`。

```sh
nsca --text 'The quick brown fox jumps over the lazy dog.'
# 輸出結果: ./result.csv
```

#### 輸出 JSON 文件

要輸出 JSON 格式的文件可以通過以下方式：

```sh
nsca ./samples/sample1.txt --output-format json
# 輸出結果: ./result.json
nsca ./samples/sample1.txt -o sample1.json
# 輸出結果: ./sample1.json
```

#### 只做句法分析

如果你不需要各指標的計算結果，只需要得到短語結構句法樹用於其他用途，可以使用 `--no-query`，NeoSCA 會只對輸入文件做短語結構分析並保存得到的句法樹，跳過後續查找句法樹的環節。

```sh
nsca samples/sample1.txt --no-query
# 句法樹: samples/sample1.parsed
nsca --text 'This is a test.' --no-query
# 句法樹: ./cmdline_text.parsed
```

#### 列出 9 種句法結構和 14 個句法復雜度指標

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

如果你在發表的成果中使用了 NeoSCA，請按如下信息進行引用。

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

同時，你也需要引用 Xiaofei 介紹 L2SCA 的文章：

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

## 類似軟件

+ [L2SCA](https://sites.psu.edu/xxl13/l2sca/) 原版，使用的是 Python，作者 [Xiaofei Lu](https://sites.psu.edu/xxl13)
+ [L2SCA online](https://aihaiyang.com/software/l2sca/)，作者 [Haiyang Ai](https://aihaiyang.com/)
+ [TAASSC](https://www.linguisticanalysistools.org/taassc.html)，使用的是 Python，作者 [Kristopher Kyle]( https://kristopherkyle.github.io/professional-webpage/)
+ [L2SCA R 語言版](https://pennstateoffice365-my.sharepoint.com/personal/xxl13_psu_edu/_layouts/15/onedrive.aspx?id=%2Fpersonal%2Fxxl13%5Fpsu%5Fedu%2FDocuments%2Fother%2Dwork%2Fwebpage%2Fdownloads%2FL2SCA%5FR%2Ezip&parent=%2Fpersonal%2Fxxl13%5Fpsu%5Fedu%2FDocuments%2Fother%2Dwork%2Fwebpage%2Fdownloads&ga=1)，作者 [Thomas Gaillat](https://perso.univ-rennes2.fr/thomas.gaillat)、Anas Knefati 和 Antoine Lafontaine
+ [FSCA](https://github.com/nvandeweerd/fsca) (法語句法復雜度分析器)，使用的是 R 語言，作者 [Nate Vandeweerd](https://github.com/nvandeweerd)

## 許可證

根據 [GNU 通用公共許可證第 2 版](https://github.com/tanloong/neosca/blob/master/LICENSE.txt) 或更高版本的條款分發。

## 聯繫

你可以通過以下方式發送錯誤報告、功能請求或任何問題：

+ [GitHub Issues](https://github.com/tanloong/neosca/issues)
+ tanloong@foxmail.com
