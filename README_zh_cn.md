<div align="center">
 <h1> NeoSCA </h1>
 <p>
  <a>
   <img alt="support-version" src="https://img.shields.io/badge/python-3.7%20%7C%203.8%20%7C%203.9%20%7C%203.10%20%7C%203.11-blue" />
  </a>
 <a href="https://codecov.io/gh/tanloong/neosca">
   <img src="https://codecov.io/gh/tanloong/neosca/branch/master/graph/badge.svg?token=M2MX1BSAEI"/>
 </a>
  <a href="https://pypi.org/project/neosca">
   <img alt="pypi" src="https://img.shields.io/badge/版本-v0.0.32-orange" />
  </a>
  <a>
   <img alt="platform" src="https://img.shields.io/badge/系统-Windows%20%7C%20macOS%20%7C%20Linux-lightgray" />
  </a>
  <a href="https://github.com/tanloong/neosca/blob/master/LICENSE.txt">
   <img alt="license" src="https://img.shields.io/badge/许可-GPL%20v2%2B-green"/>
  </a>
  <h4>
   Another syntactic complexity analyzer of written English language samples.
  </h4>
 </p>
</div>

![](img/testing-on-Windows.mp4)

NeoSCA 是 [L2 Syntactic Complexity Analyzer (L2SCA)](http://personal.psu.edu/xxl13/downloads/l2sca.html) 的从写版本，支持 Windows、macOS 和 Linux 系统。

与 L2SCA 一样，NeoSCA 能够对纯文本格式的英文语料统计和计算以下内容：

<details>

<summary>
9 种结构：
</summary>

1. 词数
2. 句子数量
3. 动词短语数量
4. 子句数量
5. T 单位数量
6. 从属子句数量
7. 复杂 T 单位数量
8. 并列短语数量
9. 复杂名词性短语数量，以及

</details>

<details>

<summary>
14 种句法复杂度指标:
</summary>

1. 平均句子长度
2. 平均 T 单位长度
3. 平均子句长度
4. 每个句子中子句的数量
5. 每个 T 单位中的动词短语数量
6. 每个 T 单位中的子句数量
7. 从属子句比率（即每个子句中的从属子句数量）
8. 每个 T 单位中的从属子句数量 
9. 并列句比率（即每个句子中的 T 单位数量）
10. 复杂 T 单位比率（即每个 T 单位中的复杂 T 单位数量）
11. 每个 T 单位中的并列短语数量
12. 每个子句中的并列短语数量
13. 每个 T 单位中的复杂名词性短语数量
14. 每个子句中的复杂名词性短语数量

</details>

## Contents

<!-- vim-markdown-toc GFM -->

* [NeoSCA vs. L2SCA](#neosca-vs-l2sca)
* [安装](#installation)
* [使用](#usage)
* [引用](#citing)
* [许可](#license)

<!-- vim-markdown-toc -->

## <a name="neosca-vs-l2sca"></a> NeoSCA vs. L2SCA <small><sup>[Top ▲](#contents)</sup></small>

| L2SCA | NeoSCA |
|-|-|
| 支持 macOS 和 Linux | 支持 **Windows**、macOS 和 Linux |
| 使用 2 个命令分别处理单文件和多文件输入 | 统一使用 `nsca` 处理 |
| 运行在 L2SCA 主目录下 | 运行在任何工作目录下 |
| 输出“9+14”种句法结构的频次 | 添加了保存中间结果的选项，包括 Stanford Parser 输出的句法树和 Tregex 输出的匹配子树 (matched subtrees) |

## <a name="installation"></a> 安装 <small><sup>[Top ▲](#contents)</sup></small>

1. 安装 NeoSCA

首先安装 [Python](https://www.python.org/) 3.7 或更高版本。在终端中使用以下命令查看You can check if you have Python installed by running the following command in your terminal:
