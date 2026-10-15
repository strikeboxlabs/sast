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
