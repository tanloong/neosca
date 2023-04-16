<div align="center"><h1>Changelog</h1></div>

## [0.0.39](https://github.com/tanloong/neosca/releases/tag/0.0.39) (8 April 2023)

### Bug Fixes

+ Fix raising IndexError when running only on subfiles
+ Fix wrong column alignment in the csv output if filenames contain commas

## [0.0.38](https://github.com/tanloong/neosca/releases/tag/0.0.38) (25 March 2023)

### New Features

+ Add `--pretokenized`
+ Add `--quiet`

### Bug Fixes

+ Fix not rasing error for typos in arguments when `--text` is specified
+ Fix zero frequency for some measures with `--select` (#12)

## [0.0.37](https://github.com/tanloong/neosca/releases/tag/0.0.37) (10 March 2023)

### Bug Fixes

+ Fix not being able to start JVM if Java is installed but JAVA_HOME is not set.

## [0.0.36](https://github.com/tanloong/neosca/releases/tag/0.0.36) (5 March 2023)

### New Features

+ Add `--combine-subfiles`
+ Add `--expand-wildcards`
+ Add `--max-length`
+ Add `--newline-break`
+ Add `--select`

### Bug Fixes

+ Fix raising PermissionError when installing dependencies on Windows
+ Fix missing subfiles when expanding wildcards
+ Fix the slightly inaccurate word counting due to changes in the output format of Stanford Parser
+ Fix raising an error if target_dir does not exist when installing dependencies
+ Fix unexpectedly adding blanklines at the end of each line within each matched subtree on Windows

### Dependency Changes

+ Add JPype1
