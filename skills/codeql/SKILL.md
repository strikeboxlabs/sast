---
name: codeql
description: Create and analyze local CodeQL databases, review path findings, and diagnose extraction or query-coverage gaps for supported source languages.
---

# CodeQL database analysis

Read this entire SKILL.md before acting. Required inputs are the local source/revision, supported language, applicable CodeQL entitlement, CLI/query packs, and extraction prerequisites. Completion requires a sound database for that source and configuration, analysis output and diagnostics, and source-based review of relevant findings.

Read selected references completely before their procedures:

| Task | Required resource |
|---|---|
| Interpreted-language scan with available query packs | Starting example below. |
| Compiled source, build/no-build selection, failed or stale extraction | [references/extraction.md](references/extraction.md) |
| Suite choice, missing packs, SARIF paths, or unexpectedly empty output | [references/queries-and-triage.md](references/queries-and-triage.md) |

CodeQL analyzes a database extracted from source. A successful query over the wrong or incomplete database can miss the intended code. Use it when supported-language semantic or dataflow queries fit the task. It is not a generic scanner for arbitrary languages. Check the [current CLI and licensing conditions](https://docs.github.com/en/code-security/concepts/code-scanning/codeql/codeql-cli) for private-code use; downloading the binary does not grant an entitlement.

## Start with a supported language

This example is for a Python checkout and a locally available Python security-extended suite. Confirm support with `codeql resolve languages`. Replace both language and suite coherently for another supported language; use the extraction reference first when builds are involved.

When Board supplies `BOARD_EVIDENCE_DIR`, keep reports in a fresh subdirectory there. Standalone use falls back to `TMPDIR` or `/tmp`. Stop if the output directory cannot be created; do not silently redirect evidence elsewhere.

```bash
repo=$(pwd -P)
output_root=${BOARD_EVIDENCE_DIR:-${TMPDIR:-/tmp}}
mkdir -p -- "$output_root" || exit 1
out=$(mktemp -d "$output_root/codeql.XXXXXX") || exit 1
codeql version >"$out/version.txt" 2>&1
if codeql database create "$out/db-python" --language=python \
  --source-root="$repo" >"$out/extraction.log" 2>"$out/extraction-errors.log"; then
  extraction_status=0
else
  extraction_status=$?
fi
printf '%s\n' "$extraction_status" >"$out/extraction-status.txt"
```

Inspect extraction diagnostics and expected source coverage before analysis. Stop this workflow if creation fails; do not run analysis over an older database as a substitute. With a completed extraction:

```bash
if codeql database analyze "$out/db-python" \
  codeql/python-queries:codeql-suites/python-security-extended.qls \
  --format=sarif-latest --sarif-category=python \
  --output="$out/findings.sarif" \
  >"$out/analysis.log" 2>"$out/analysis-errors.log"; then
  analysis_status=0
else
  analysis_status=$?
fi
printf '%s\n' "$analysis_status" >"$out/analysis-status.txt"
printf 'Database, logs, and report: %s\n' "$out"
```

If the suite cannot be resolved, use the query reference. Downloading packs is a separate network operation; preserve pack versions for reproducibility. Keep databases outside the source tree and tied to the source state at extraction. A successful analysis status indicates command completion, not zero security findings; read SARIF results and diagnostics.

For each relevant result, verify the source location and any path through calls/assignments against the extracted source. Record missing framework models, extraction gaps, or unresolved reachability. Report the database language, source state, build/extraction mode, CLI and pack versions, suite, status/log paths, and reviewed findings. Do not upload SARIF or databases merely to inspect local results.

Primary procedures: [prepare source](https://docs.github.com/en/code-security/tutorials/customize-code-scanning/prepare-code-for-analysis) and [analyze a database](https://docs.github.com/en/code-security/tutorials/customize-code-scanning/analyze-code).
