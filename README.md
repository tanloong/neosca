# NeoSCA

[![build](https://github.com/tanloong/neosca/workflows/build/badge.svg)](https://github.com/tanloong/neosca/actions?query=workflow%3Abuild)
[![lint](https://github.com/tanloong/neosca/workflows/lint/badge.svg)](https://github.com/tanloong/neosca/actions?query=workflow%3ALint)
[![codecov](https://img.shields.io/codecov/c/github/tanloong/neosca)](https://codecov.io/gh/tanloong/neosca)
[![codacy](https://app.codacy.com/project/badge/Grade/6d49b7a0f3ac44b79d6fc6b87b303034)](https://www.codacy.com/gh/tanloong/neosca/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=tanloong/neosca&amp;utm_campaign=Badge_Grade)
[![commit](https://img.shields.io/github/last-commit/tanloong/neosca)](https://github.com/tanloong/neosca/commits/master)
![platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgray)
![downloads](https://img.shields.io/github/downloads/tanloong/neosca/total?label=Downloads)
[![license](https://img.shields.io/github/license/tanloong/neosca)](https://github.com/tanloong/neosca/blob/master/LICENSE)

NeoSCA is a fork of [Xiaofei Lu](http://personal.psu.edu/xxl13/index.html)'s [L2 Syntactic Complexity Analyzer](http://personal.psu.edu/xxl13/downloads/l2sca.html) (L2SCA) and [Lexical Complexity Analyzer](https://sites.psu.edu/xxl13/lca/) (LCA). Starting from version 0.1.0, NeoSCA has a graphical interface and no longer requires Java installation, it has translated a portion of the Tregex code into Python and favors Stanza over Stanford Parser.

<!-- ### Download from source -->
<!---->
<!-- ```sh -->
<!-- git clone https://github.com/tanloong/neosca -->
<!-- cd neosca -->
<!-- pip3 install . -->
<!-- python -m neosca gui -->
<!-- ``` -->

## Basic Usage

### GUI

Download and run the packaged application

|Release|Remarks|
|-|-|
|[Latest Release for Windows](https://github.com/tanloong/neosca/releases/download/0.1.4/NeoSCA-0.1.4-windows.zip)|1. Extract all files<br>2. Double-click **NeoSCA/NeoSCA.exe** to run|
|[Latest Release for macOS](https://github.com/tanloong/neosca/releases/download/0.1.4/NeoSCA-0.1.4-macos.zip)|1. Extract all files<br>2. Search and open **Terminal** in Launchpad, then type `xattr -rc ` (note the trailing whitespace), drag the whole **NeoSCA** directory to the **Terminal**, and press `Enter` <br>3. Double-click **NeoSCA.app** to run|
|[Latest Release for Arch Linux](https://github.com/tanloong/neosca/releases/download/0.1.4/NeoSCA-0.1.4-archlinux.tar.gz)|1. Extract all files<br>2. Double-click **NeoSCA/NeoSCA** to run<br>|
|[Past Releases](https://github.com/tanloong/neosca/releases)|Not recommended|
|[Baidu Netdisk](https://pan.baidu.com/s/1okMY3Dw20jQJtQfS6KtlYw?pwd=nsca)|For users with unstable connections to GitHub|


### Command Line

Install NeoSCA from the source code

```
pip install git+https://github.com/tanloong/neosca
```

Run SCA or LCA by

```
python -m neosca sca filepath.txt
python -m neosca sca --text 'This is a test.'
python -m neosca lca filepath.txt
python -m neosca lca --text 'This is a test.'
```

To see other command line options please use

```
python -m neosca --help
python -m neosca sca --help
python -m neosca lca --help
```

## Citing

If you use NeoSCA in your research, please cite as follows.

<details>

<summary>
BibTeX
</summary>

```BibTeX
@misc{long2024neosca,
title        = {NeoSCA: A Fork of L2 Syntactic Complexity Analyzer, version 0.1.4},
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

<pre>Tan, L. (2024). <i>NeoSCA</i> (version 0.1.4) [Computer software]. GitHub. https://github.com/tanloong/neosca</pre>

</details>

<details>

<summary>
MLA (9th edition)
</summary>

<pre>Tan, Long. <i>NeoSCA</i>. version 0.1.4, GitHub, 2024, https://github.com/tanloong/neosca.</pre>

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

## Contact

You can send bug reports, feature requests, or any questions via:

+ [GitHub Issues](https://github.com/tanloong/neosca/issues)
+ tanloong@foxmail.com
