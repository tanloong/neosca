<div align="center"><h1>Changelog</h1></div>

## [0.1.3](https://github.com/tanloong/neosca/releases/tag/0.1.3) (25 June 2024)

### Bug fixes

+ Fix including '.DS_Store' and '._*' on macOS and '~$*' on Windows when opening a folder
+ Fix extra empty cell in the first column of CSV output
+ Fix throwing error for files containing only punctuation marks
+ Fix [performance issue](https://github.com/tanloong/neosca/issues/41) with file opening
+ Fix cache_info.json not saving when quitting via the upper right X button
+ Fix decode error when loading cache_info.json on startup
+ Fix memory leak on thread management

### Improvements

+ Changes of QStandardItemModel is now strictly managed within the main thread [for stability and reliability](https://forum.qt.io/topic/32732/multi-threading-with-model-view-framework/4?_=1720380212407)
+ Add "Minimize to Tray" action to the "Files" menu
+ The main window can now be toggled by single clicking the system tray icon

### Dependency Changes

+ Update Stanza to 1.8.2
+ Update OpenPyXl to 3.1.5
+ Update PyInstaller to 6.9.0
+ Update PyQt to 5.15.11

## [0.1.2](https://github.com/tanloong/neosca/releases/tag/0.1.2) (24 March 2024)

### Bug fixes

+ Fix crash on exporting table

## [0.1.1](https://github.com/tanloong/neosca/releases/tag/0.1.1) (17 March 2024)

### Improvements

+ Able to query long sentences

Now query constituency trees non-recursively to prevent reaching the maximum recursion depth limit (default 1000 in Python). If any, trees for sentences that have hundreds of words can be queried normally.

+ Support macOS 10

Migrate from PySide6 to PyQt5 for earlier macOS version support. The testing macOS 10 complains that "Qt requires macOS 11.0.0 or later" when importing PySide6/PyQt6. Fallback to Qt5.

## [0.1.0](https://github.com/tanloong/neosca/releases/tag/0.1.0) (13 March 2024)

### Breaking Changes

+ Rename `--reserve-matched` to `--save-matches`
+ Rename `--reserve-parsed` to `--cache`

### Dependency Changes

+ Remove [JPype1](https://github.com/jpype-project/jpype)
+ Remove [Stanford Parser](https://nlp.stanford.edu/software/lex-parser.html)
+ Remove [Tregex](https://nlp.stanford.edu/software/tregex.html)
+ Remove [spaCy](https://github.com/explosion/spaCy)
+ Add [Stanza](https://github.com/stanfordnlp/stanza)

### New Features

+ Add GUI (`nsca gui`). NeoSCA borrows tons of code and design ideas to its GUI component from [Wordless](https://github.com/BLKSerene/Wordless).

### Deprecated Features

+ `--no-querying`
+ `--expand`
+ `--max-length`
+ `--config`

### Bug fixes

+ Fix including Windows temporary files (`~$\*`) as input files

### License change

Change the license from GPLv2-or-later to GPLv3. According to the [license compatibility matrix](https://www.gnu.org/licenses/gpl-faq.html#AllCompatibility), the combination of code under GPLv2-or-later, which is the current license, and code under LGPLv3, which is the license of the recently added dependency PySide6, should be licensed under GPLv3.

## [0.0.55](https://github.com/tanloong/neosca/releases/tag/0.0.55) (2 October 2023)

### Bug fixes

+ Fix exiting early when checking spaCy and model

## [0.0.54](https://github.com/tanloong/neosca/releases/tag/0.0.54) (2 October 2023)

### Dependency Changes

+ Update dependency on spaCy to 3.7.0

## [0.0.53](https://github.com/tanloong/neosca/releases/tag/0.0.53) (25 September 2023)

### Improvements

+ Add option to install spaCy from Chinese mirror site and en\_core\_web\_sm from sourceforge.net

## [0.0.52](https://github.com/tanloong/neosca/releases/tag/0.0.52) (1 September 2023)

### New features

+ Add support of PTB POS tagset for `nsca-lca`
+ Add `--text` option for `nsca-lca`

### Improvements

+ Add formulae in README for LCA measures

### Bug fixes

+ Fix not correctly using Chinese JDK mirror

## [0.0.51](https://github.com/tanloong/neosca/releases/tag/0.0.51) (23 August 2023)

### Bug fixes

+ Don't check empty key/value when initializing Structure

## [0.0.50](https://github.com/tanloong/neosca/releases/tag/0.0.50) (23 August 2023)

### Bug fixes

+ Fix `--reserve-matched` not working since 0.0.48

## [0.0.49](https://github.com/tanloong/neosca/releases/tag/0.0.49) (19 August 2023)

### Bug fixes

+ Fix missing filename in the output of nsca-lca

## [0.0.48](https://github.com/tanloong/neosca/releases/tag/0.0.48) (19 August 2023)

### New features

+ Add lexical complexity analyzing feature (`nsca-lca`)

## [0.0.47](https://github.com/tanloong/neosca/releases/tag/0.0.47) (18 August 2023)

### Bug fixes

+ Re-calculate values of structures defined by value_source after '+' operation
+ Check empty key/value when loading custom config file

## [0.0.46](https://github.com/tanloong/neosca/releases/tag/0.0.46) (14 August 2023)

### Bug fixes

+ Fix division by zero error introduced in 0.0.44

### Improvements

+ Update docs for custom structure definition
+ Add release.yml for workflow

## [0.0.45](https://github.com/tanloong/neosca/releases/tag/0.0.45) (14 August 2023)

### New features

+ Add Tregex command line interface

### Bug fixes

+ Include structure_data.json in dist

## [0.0.44](https://github.com/tanloong/neosca/releases/tag/0.0.44) (14 August 2023)

### New features

+ Add nsca.json config file feature (--config)

### Improvements

+ Skip unsupported file types instead of immediately exit
+ Try to parse a file if its extension is not among the extensions_to_exclude

### Bug fixes

+ Fix precision issue of values on combined files caused by Python's floating-point inaccuracy
+ Fix Tregex matching for "ROOT" nodes

## [0.0.43](https://github.com/tanloong/neosca/releases/tag/0.0.43) (7 July 2023)

### Breaking changes

+ Should now use slashes (e.g., C/S) instead of underscores (e.g., C_S) for `--select`

### New features

+ Add `--no-parse`
+ Add support for reading .odt files

### Bug fixes

+ Fix urlopen error on macOS
+ Store Java dependencies at root direcotry if Windows username contains non-latin characters

## [0.0.42](https://github.com/tanloong/neosca/releases/tag/0.0.42) (29 April 2023)

### Bug fixes

+ Update dependents in setup.py

## [0.0.41](https://github.com/tanloong/neosca/releases/tag/0.0.41) (29 April 2023)

### Improvements

+ Try reusing previously detected encoding for txt files before detecting again

## [0.0.40](https://github.com/tanloong/neosca/releases/tag/0.0.42) (29 April 2023)

### New features

+ Add support for input directories, allowing users to process batches of files more easily.
+ Add support for reading docx files, in addition to the previously-supported txt files.
+ Add the ability to guess the encoding of txt files, making it easier to read files with unknown or non-utf8 encodings.

### Bug fixes

+ Fix subsequent files cannot be processed if parsed results for preceding files are present (#20)
+ Fix incorrect column alignment in the csv output if filenames contain commas

## [0.0.39](https://github.com/tanloong/neosca/releases/tag/0.0.39) (8 April 2023)

### Bug fixes

+ Fix raising IndexError when running only on subfiles
+ Fix wrong column alignment in the csv output if filenames contain commas

## [0.0.38](https://github.com/tanloong/neosca/releases/tag/0.0.38) (25 March 2023)

### New features

+ Add `--pretokenized`
+ Add `--quiet`

### Bug fixes

+ Fix not rasing error for typos in arguments when `--text` is specified
+ Fix zero frequency for some measures with `--select` (#12)

## [0.0.37](https://github.com/tanloong/neosca/releases/tag/0.0.37) (10 March 2023)

### Bug fixes

+ Fix not being able to start JVM if Java is installed but JAVA_HOME is not set.

## [0.0.36](https://github.com/tanloong/neosca/releases/tag/0.0.36) (5 March 2023)

### New features

+ Add `--combine-subfiles`
+ Add `--expand-wildcards`
+ Add `--max-length`
+ Add `--newline-break`
+ Add `--select`

### Bug fixes

+ Fix raising PermissionError when installing dependencies on Windows
+ Fix missing subfiles when expanding wildcards
+ Fix the slightly inaccurate word counting due to changes in the output format of Stanford Parser
+ Fix raising an error if target_dir does not exist when installing dependencies
+ Fix unexpectedly adding blanklines at the end of each line within each matched subtree on Windows

### Dependency changes

+ Add JPype1
