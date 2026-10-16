# Validation record

## Bootstrap on 2026-10-15

Authoring host: Windows; Python 3.12. WSL reports that it is not installed, Docker is unavailable on PATH, and the selected scanners are not available on PATH. Scanner binaries were not installed. The controlled Linux image and its executable paths remain unverified.

Documentation review covers all seven packages under SAST schema v0.1. See [source review](source-review.md) for source/task mapping and [reuse](reuse.md) for copied helper identities.

Checks executed against the authored bootstrap file set before placement:

| Check | Actual outcome |
|---|---|
| `python -B scripts/check_repository.py` | Passed: 7 skills, 25 Markdown files, 50 local links, no errors. |
| Checker with Git Bash selected using `--bash` | Passed: all 24 Bash blocks parsed with `bash -n`; no documented commands executed. Bash startup required leaving the Windows sandbox. |
| `python -B -m unittest discover -s tests -v` | Passed: all 19 tests, including isolated copies of every skill and real help-capture success/failure/timeout subprocess cases. These subprocesses used Python fixtures, not scanners. |
| Bundled skill-creator `quick_validate.py` | All 7 packages passed frontmatter/scaffold validation using a temporary PyYAML 6.0.3 authoring dependency. That dependency is not part of the repository. |
| Semgrep starter asset parsing | YAML parsed and Python fixture parsed with `ast.parse`; Semgrep rule compilation/matching was not executed. |
| Catalogue and first-read structure | All 7 accepted skills appear in README; every complete entrypoint and its task/resource routes fit within the first 150 lines. Full entrypoints and conditional tasks were reviewed. |
| Reused file identity | All 6 unmodified copies match the SHA-256 values in the reuse record. |
| `git diff --check` with new files exposed using intent-to-add | Passed for the bootstrap files. |

Temporary-directory access initially prevented dependency setup in the sandbox's default temp area. Redirecting task-local TEMP/TMP into ignored `work/` resolved that issue. Helper tests used the same task-local approach. Optional raw bootstrap logs live under ignored `runs/` and are not a dependency of portable skills.

No scanner workflow, Semgrep rule test, target-code execution, or independent worker evaluation is claimed. No test established bug-finding rates, cross-language completeness, or behavior on the controlled Linux image. The [evaluation cases](../evaluation/README.md) describe the remaining on-image work. Missing runtime access did not prevent acceptance of source-reviewed documentation.

## Selective catalogue and Board evidence output, 2026-10-16

Added optional schema-version-1 `catalog.json` covering all seven physical packages, with reviewed task/language/artifact facets and no asserted host requirements or readiness. Reviewed all seven complete entrypoints under SAST schema v0.1 while changing their common output-directory task: `BOARD_EVIDENCE_DIR` takes precedence when supplied, with standalone `TMPDIR`/`/tmp` fallback, unique per-tool output directories, and failure instead of silently redirecting unavailable Board evidence. Conditional scanner procedures were preserved. This is not a new scanner source intake or an installed-version review.

Windows checks: 33 repository/helper/catalogue/directory tests completed successfully (32 passed, one real symlink-containment test skipped because this account lacks symlink creation privileges). Catalogues and isolated copies of every skill passed. The repository checker passed with 7 skills/catalogue entries, 26 Markdown files, 57 local links and 26 Bash blocks parsed by Git Bash; zero errors. The two directory tests execute only the documented setup prefix, ending before any scanner/version invocation: all seven examples create a report beneath a Board path containing spaces or the selected standalone temporary path, and all seven fail without fallback when the Board path is an ordinary file. No scanner or target application executed.

The first directory-fixture attempt exposed Git Bash rewriting inherited `TMPDIR` during Windows startup, which made the fixture's expected path wrong. The test now sets the requested temporary path inside its Bash child before exercising the unchanged Linux snippet; the full suite then passed. This is explicitly Windows Git Bash evidence, not validation of the controlled Linux host. `git diff --check` passed. No live Pi/Board worker outcome or efficiency claim follows. See [catalogue semantics](catalog.md) and [evaluation cases](../evaluation/README.md).

### Debian-derived Linux CI, 2026-10-16

[Board CI run 38877409000](https://github.com/strikeboxlabs/board/actions/runs/38877409000) passed on Ubuntu 24.04 with Python 3.12 and locked Board dependencies. The SAST snapshot tested was `f3d5ff2dd1e20709bf78af30a0ff906c1056fc32`; Board was `812fecfceabf0a42ca61d419c23bcf7e17662dbe`. All 33 SAST tests passed with zero skips, including symlink containment, independent package copies and the directory-only Bash fixtures. All seven examples preserved Board evidence-directory precedence, standalone fallback and failure without fallback for an unusable Board path. The repository checker accepted all seven skills and parsed 26 documented Bash blocks for syntax with zero errors.

The directory fixtures execute only setup commands before the scanner invocation. No scanner workflow, Semgrep rule matching, target application or external credential validation ran. The same CI run passed 313 Board tests, including actual Pi 1.3 loading a harmless selected skill through an owned loopback dummy provider and resuming its session. That establishes integration mechanics; it does not establish scanner availability, useful security findings, real-model skill effectiveness or an efficiency gain. Scanner execution and outcome studies remain separate work.
