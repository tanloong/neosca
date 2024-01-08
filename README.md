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
[![license](https://img.shields.io/github/license/tanloong/neosca)](https://github.com/tanloong/neosca/blob/master/LICENSE)

[简体中文](https://github.com/tanloong/neosca/blob/master/README_zh_cn.md)|
[繁體中文](https://github.com/tanloong/neosca/blob/master/README_zh_tw.md)|
English

NeoSCA is a fork of [Xiaofei Lu](http://personal.psu.edu/xxl13/index.html)'s [L2 Syntactic Complexity Analyzer](http://personal.psu.edu/xxl13/downloads/l2sca.html) (L2SCA) and [Lexical Complexity Analyzer](https://sites.psu.edu/xxl13/lca/), with the cross-platform compatibility and a graphical interface.

## Download

### Get binary builds

1. [Github Releases]()
2. [Baidu Netdisk]()

### From PyPI

```
pip3 install neosca
python3 -m neosca --gui
```

### Run from source

```
git clone https://github.com/tanloong/neosca
cd neosca
pip3 install -r ./requirements.txt
cd src
python3 -m neosca --gui
```

### Building

```
git clone https://github.com/tanloong/neosca
cd neosca
pyinstaller ./utils/ns_packaging.spec
```

## Citing

If you use NeoSCA in your research, please cite as follows.

<details>

<summary>
BibTeX
</summary>

```BibTeX
@misc{tan2024neosca,
title        = {NeoSCA: A Fork of L2 Syntactic Complexity Analyzer, version 0.1.0},
author       = {Long Tan},
howpublished = {\url{https://github.com/tanloong/neosca}},
year         = {2024}
}
```

</details>

<details>

<summary>
APA (7th edition)
</summary>

<pre>Tan, L. (2024). <i>NeoSCA</i> (version 0.1.0) [Computer software]. Github. https://github.com/tanloong/neosca</pre>

</details>

<details>

<summary>
MLA (9th edition)
</summary>

<pre>Tan, Long. <i>NeoSCA</i>. version 0.1.0, GitHub, 2024, https://github.com/tanloong/neosca.</pre>

</details>

If you use the Syntactic Complexity Analyzer module of NeoSCA, please cite Xiaofei's article describing L2SCA as well.

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

<pre>Lu, X. (2010). Automatic analysis of syntactic complexity in second language writing. <i>International Journal of Corpus Linguistics, 15</i>(4), 474-496. https://doi.org/10.1075/ijcl.15.4.02lu</pre>

</details>

<details>

<summary>
MLA (9th edition)
</summary>

<pre>Lu, Xiaofei. "Automatic Analysis of Syntactic Complexity in Second Language Writing." <i>International Journal of Corpus Linguistics</i>, vol. 15, no. 4, John Benjamins Publishing Company, 2010, pp. 474-96, https://doi.org/10.1075/ijcl.15.4.02lu</pre>

</details>

If you use the Lexical Complexity Analyzer module of NeoSCA, please also cite Xiaofei's article about LCA.

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

## License

Distributed under the terms of the [GNU General Public License version 3](https://github.com/tanloong/neosca/blob/master/LICENSE) or later.

## Contact

You can send bug reports, feature requests, or any questions via:

+ [GitHub Issues](https://github.com/tanloong/neosca/issues)
+ tanloong@foxmail.com
