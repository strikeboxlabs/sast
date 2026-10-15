# Validate on the controlled Linux image

These are evaluation cases, not executed results. Use disposable source you own, keep scan outputs in ignored `runs/`, and record tool versions, commands, expected/observed distinctions, and errors in [validation](../docs/validation.md). Scanner installation is separate.

| Package | Supported-result case | Incomplete-evidence or negative case |
|---|---|---|
| semgrep | Run the package's paired rule tests; scan their input and verify the two annotated shell-enabled calls are reported. | Confirm shell-disabled/list-argument calls are not reported by this starter rule. Introduce a malformed rule in a disposable copy and verify failure is reported as failure. |
| codeql | Extract a small supported-language project and run a named suite; inspect a known diagnostic and one path finding if the fixture supplies one. | Run against an incomplete or failed extraction and verify the worker does not call an empty result clean. Record source units actually extracted. |
| bandit | Scan a synthetic Python source with a documented plugin trigger and inspect the issue ID, severity, confidence, and location. | Supply a syntactically invalid Python file alongside a valid file; verify the report's error list narrows the conclusion. |
| gosec | Scan a disposable Go module with a documented rule trigger and inspect its package/file coverage. | Make one imported dependency unavailable or select a build tag that excludes a file; verify coverage and processing errors are preserved. |
| brakeman | Scan a disposable Rails fixture with a known unsafe flow and review the warning's source context. | Compare against a controlled safe flow and a missing/invalid Rails input; do not turn a failure into a no-warning result. |
| cppcheck | Analyze an owned C/C++ fixture containing a known bounds or lifetime defect using its real compilation database. | Compare a valid guarded case and a mismatched macro/include configuration; distinguish modeling gaps from bugs. |
| trivy | Scan synthetic configuration plus a supported lockfile using a recorded database/check bundle. | Disable one scanner explicitly and verify that absent results for that category are reported as unscanned. Test an unavailable DB/cache without claiming success. |

Do not execute the vulnerable fixture programs or validate candidate secrets against external services. These cases exercise static reports and source reasoning. Use fictitious test strings, never real credentials.

Once a workflow runs, give an ordinary worker a realistic request, the selected skill folder, and the disposable source without the expected answer. Compare its evidence, missed scan errors, false bug claims, and time with a baseline. This optional worker study is distinct from scanner smoke tests; no worker outcomes are claimed in the initial repository.
