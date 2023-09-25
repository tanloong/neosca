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

簡體中文 |
[繁體中文](https://github.com/tanloong/neosca/blob/master/README_zh_tw.md) |
[English](https://github.com/tanloong/neosca#readme)

NeoSCA 是 [Xiaofei Lu](http://personal.psu.edu/xxl13/index.html) 的 [L2 Syntactic Complexity Analyzer (L2SCA)](http://personal.psu.edu/xxl13/downloads/l2sca.html) 的復刻版，添加了對 Windows 的支持和更多的命令行選項，作者譚龍。NeoSCA 對英文語料統計以下內容：

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
7. 複雜 T 單位
8. 並列短語
9. 複雜名詞性短語

</details>

<details>

<summary>
14 種句法複雜度指標的值
</summary>

1. 平均句子長度
2. 平均 T 單位長度
3. 平均子句長度
4. 每個句子中子句的數量
5. 每個 T 單位中的動詞短語數量
6. 每個 T 單位中的子句數量
7. 從屬子句比率，即每個子句中的從屬子句數量
8. 每個 T 單位中的從屬子句數量 
9. 並列句比率，即每個句子中的 T 單位數量
10. 複雜 T 單位比率，即每個 T 單位中的複雜 T 單位數量
11. 每個 T 單位中的並列短語數量
12. 每個子句中的並列短語數量
13. 每個 T 單位中的複雜名詞性短語數量
14. 每個子句中的複雜名詞性短語數量

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
* [類似軟體](#類似軟體)
* [許可證](#許可證)
* [聯繫](#聯繫)

<!-- vim-markdown-toc -->

## Highlights

* 跨平臺：支持 **Windows**、macOS 和 Linux 系統。
* 靈活的命令行選項
* 支持 txt/docx/odt 格式的輸入文件
* 統計自定義句法結構

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

在終端中輸入 `nsca` 加空格，後面跟輸入文件的路徑。

```sh
nsca ./samples/sample1.txt
nsca ./samples/sample1.docx
```

docx/odt 文件需要事先刪除表格、圖表、圖片等不相關元素，頁眉頁腳會自動忽略，不必刪除 (若有)。

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

這可以讓包括空格在內的整個路徑被識別為單個輸入文件，否則 「./samples/sample」 和 「1.txt」 會被認為是兩個文件，因為這兩個文件都不存在，所以程序會運行失敗。

</details>

#### 多個輸入文件

在 `nsca` 的右邊指定輸入文件夾。

```
nsca samples/              # 分析 samples/ 文件夾下所有的 txt 和 docx 文件
nsca samples/ --ftype txt  # 只分析 txt 文件
nsca samples/ --ftype docx # 只分析 docx 文件
```

或者以空格為間隔列出輸入文件：

```sh
cd ./samples/
nsca sample1.txt sample2.txt
```

或者使用 [通配符](https://www.gnu.org/savannah-checkouts/gnu/clisp/impnotes/wildcard.html#wildcard-syntax)：

```sh
cd ./samples/
nsca sample*.txt                                           # 指定所有文件名以 「sample」 開頭並且以 「.txt」 結尾的文件
nsca sample[1-9].txt sample10.txt                          # sample1.txt -- sample10.txt
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

#### 配置文件

你可以使用配置文件來自定義需要統計/計算的句法結構。

neosca 的默認配置文件名為 `nsca.json`，neosca 會嘗試在當前工作目錄查找 `nsca.json`。你可以使用命令 `nsca --config <your_config_file>` 指定自己的配置文件。配置文件應為 JSON 格式，並以 `.json` 擴展名命名。

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

上面是 neosca 內置的句法結構定義的一部分。定義應遵循鍵值對的格式，其中鍵和值都應放在半角引號中。

neosca 提供了兩種定義句法結構的方法：使用 `tregex_pattern` 或 `value_source`。`tregex_pattern` 是基於 Tregex 語法的定義。通過 `tregex_pattern` 定義的句法結構，會運行 Stanford Tregex 來統計頻次。關於 Tregex pattern 要怎麼寫，請查看：

+ Xiaofei 的 [*Computational Methods for Corpus Annotation and Analysis*](http://www.springer.com/education+%26+language/linguistics/book/978-94-017-8644-7?otherVersion=978-94-017-8645-4) 的第六章
+ 一位 Galen Andrew 的 [PPT](https://nlp.stanford.edu/software/tregex/The_Wonderful_World_of_Tregex.ppt)
+ [TregexPattern 文檔](http://nlp.stanford.edu/nlp/javadoc/javanlp/edu/stanford/nlp/trees/tregex/TregexPattern.html)

`value_source` 表示該句法結構通過對其他結構的值做算術運算來間接統計。`value_source` 可以包含其他結構的 `name`、整數、小數、`+`、`-`、`*`、`/`、半角括號 `(` 和 `)`。`value_source` 的分詞用的是 Python 的標準庫 tokenize，這個庫是專門針對 Python 原始碼的，如果一個句法結構需要在其他結構的 `value_source` 裡被引用，確保它的 `name` 符合 Python 變量的命名規則 (由字母、數字、下劃線組成，不能以數字開頭；字母指 Unicode 字符集中 Letter 分類的字符，比如英文字母、漢字等)，否則會識別錯誤。

`value_source` 的定義可以嵌套，依賴結構自身也可以通過 `value_source` 來定義並依賴於其他結構，形成類似樹的關係。但位於葉子節點的句法結構必須通過 `tregex_pattern` 來定義，避免定義循環。

定義一個句法結構時只能使用 `tregex_pattern` 或 `value_source` 的其中一種，不能兩個同時使用。`name` 的值可以在 `--select` 選項中使用。`description` 可以不寫。

#### 選取部分指標

NeoSCA 默認計算所有指標的值，使用 `--select` 可以只計算選定指標的值。要查看所有的可選指標可以用 `nsca --list`。

```sh
nsca --select VP T DC/C -- sample1.txt
```

注意需要使用 `--` 將選定指標與輸入文件名區分開。`--` 右邊的所有參數都將被視為輸入文件名，請確保將輸入文件名之外的參數寫在 `--` 的左邊。

#### 合併子文件

使用 `-c`/`--combine-subfiles` 選項可以累加子文件中 9 種句法結構的頻次並計算原文件的 14 種句法複雜度指標的值。你可以使用多個 `-c` 來分別合併不同的子文件列表。命令中同時含有輸入子文件名和輸入文件名時需要使用 `--` 把二者區分開。

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

#### 將成分句法樹作為輸入

NeoSCA 默認接受原始文本作為輸入，對文本進行短語結構分析並生成句法樹，然後統計句法樹中的目標句法結構。使用 `--no-parse` 可以讓程序跳過短語結構分析的步驟，直接將輸入文件作為句法樹開始統計的步驟。使用此選項時，`is_skip_querying` 和 `reserve_parsed` 會自動設置為 False。

```sh
nsca samples/sample1.parsed --no-parse
```

#### 列出內置指標

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

#### Tregex 接口

使用 `nsca-tregex` 可以在命令行下運行 Tregex，該命令和 Tregex package 中的 `tregex.sh` 功能類似，但額外支持 Windows。

#### 詞法複雜度分析

使用 `nsca-lca` 命令可以分析輸入文本的詞法複雜度，功能與 [LCA (Lexical Complexity Analyzer)](https://sites.psu.edu/xxl13/lca/) 相同，指標如下：

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
nsca-lca sample.txt # 單篇分析
nsca-lca samples/   # 批量分析
```

## 引用

如果你在發表的成果中使用了 NeoSCA，請按如下信息進行引用。

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

同時，你也需要引用 Xiaofei 介紹 L2SCA 的文章：

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

如果你使用了詞法複雜度的功能，請引用 Xiaofei 關於 LCA 的文章。

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

## 相關軟體

+ [L2SCA](https://sites.psu.edu/xxl13/l2sca/) 原版，使用的是 Python，作者 [Xiaofei Lu](https://sites.psu.edu/xxl13)
+ [L2SCA online](https://aihaiyang.com/software/l2sca/)，作者 [Haiyang Ai](https://aihaiyang.com/)
+ [TAASSC](https://www.linguisticanalysistools.org/taassc.html)，使用的是 Python，作者 [Kristopher Kyle]( https://kristopherkyle.github.io/professional-webpage/)
+ [L2SCA R 語言版](https://pennstateoffice365-my.sharepoint.com/personal/xxl13_psu_edu/_layouts/15/onedrive.aspx?id=%2Fpersonal%2Fxxl13%5Fpsu%5Fedu%2FDocuments%2Fother%2Dwork%2Fwebpage%2Fdownloads%2FL2SCA%5FR%2Ezip&parent=%2Fpersonal%2Fxxl13%5Fpsu%5Fedu%2FDocuments%2Fother%2Dwork%2Fwebpage%2Fdownloads&ga=1)，作者 [Thomas Gaillat](https://perso.univ-rennes2.fr/thomas.gaillat)、Anas Knefati 和 Antoine Lafontaine
+ [FSCA](https://github.com/nvandeweerd/fsca) (法語句法複雜度分析器)，使用的是 R 語言，作者 [Nate Vandeweerd](https://github.com/nvandeweerd)

## 許可證

根據 [GNU 通用公共許可證第 2 版](https://github.com/tanloong/neosca/blob/master/LICENSE.txt) 或更高版本的條款分發。

## 聯繫

你可以通過以下方式發送錯誤報告、功能請求或任何問題：

+ [GitHub Issues](https://github.com/tanloong/neosca/issues)
+ tanloong@foxmail.com
