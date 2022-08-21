NeoL2SCA
==========

NeoL2SCA is a rewrite of [Xiaofei Lu](http://personal.psu.edu/xxl13/index.html)'s [L2 Syntactic Complexity Analyzer](http://personal.psu.edu/xxl13/downloads/l2sca.html), with extended functionalities.

## Comparison

| L2SCA | L2SCA-fork |
|-|-|
| runs on MacOS and Linux | runs on **Windows**, MacOS, and Linux |
| single input and multiple input are handled respectively by two commands | one command for both cases, making your life easier |
| runs only under its own home directory | runs under any directory |
| outputs only final results, i.e. frequencies of the "9+14" linguistic structures | add options to reserve intermediate results, i.e. Stanford Parser's parsing results, Tregex's querying results, and corresponding $\mathrm{\small \LaTeX}$ documents to visualize the two |

## Usage

1. Single input:
```
python l2sca-analyzer.py ./samples/sample1.txt ./samples/output.csv
```

2. Multiple input:
```
python l2sca-analyzer.py ./samples/sample1.txt ./samples/sample2.txt ./samples/output.csv
```

3. Wildcard characters are also supported:
```
python l2sca-analyzer.py ./samples/*.txt ./samples/output.csv
```

4. Use 
`--reserve-parsed`/`-rp`, `--reserve-match`/`-rm`
to reserve parsing results of Stanford Parser and match result of Tregex, respectively:

```
python l2sca-analyzer.py ./samples/sample1.txt ./samples/output.csv -rm -rp
```

## Installation

1. Install nl2sca
```
pip install nl2sca
```

2. Install [Java](https://www.java.com/en/download) 8 or later

3. Download [Stanford Parser](https://nlp.stanford.edu/software/lex-parser.shtml#Download) and [Stanford Tregex](https://nlp.stanford.edu/software/tregex.html#Download)

4. Set `STANFORD_PARSER_HOME` and `STANFORD_TREGEX_HOME`

+ Windows:

In the Environment Variables window:

```
STANFORD_PARSER_HOME=/path/to/stanford-parser-full-2022-11-17/*:
STANFORD_TREGEX_HOME=/path/to/stanford-tregex-2020-11-17/*:
```

The Environment Variables windows can be opened through 
pressing `Windows` and typing in `path`.

+ Linux/MacOS:

```
export STANFORD_PARSER_HOME=/path/to/stanford-parser-full-2020-11-17/*:
export STANFORD_TREGEX_HOME=/path/to/stanford-tregex-2020-11-17/*:
```

## License
The same as L2SCA, NeoL2SCA is licensed under the GNU General Public License, version 2 or later.
