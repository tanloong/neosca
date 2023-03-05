<div align="center"><h1>Changelog</h1></div>

## [0.0.36](https://github.com/tanloong/neosca/releases/tag/0.0.36) (5 March 2023)

### New Features

+ Add the option `--combine-subfiles`
+ Add the option `--expand-wildcards`
+ Add the option `--max-length`
+ Add the option `--newline-break`
+ Add the option `--select`

### Bugfixes

+ Fix raising PermissionError when installing dependencies on Windows
+ Fix missing subfiles when expanding wildcards
+ Fix the slightly inaccurate word counting due to changes in the output format of Stanford Parser
+ Fix raising an error if target_dir does not exist when installing dependencies
+ Fix unexpectedly adding blanklines at the end of each line within each matched subtree on Windows

### Dependency Changes

+ Add JPype1
