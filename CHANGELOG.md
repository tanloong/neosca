<div align="center"><h1>Changelog</h1></div>

## [0.0.46](https://github.com/tanloong/neosca/releases/tag/0.0.45) (14 August 2023)

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
