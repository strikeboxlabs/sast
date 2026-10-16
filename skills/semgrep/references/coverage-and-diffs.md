# Coverage and changed-code review

Use this reference when a file expected to be scanned is absent, a run is partial, or the request concerns changes relative to a Git revision. Inputs are the local source root, complete scan logs/report, selected config and engine, and the expected file or baseline revision.

## Recover a useful scope

Start with one expected file and a rule known to support its language. Compare it against the report's scanned paths, exclusions, and errors. Check ignore configuration, VCS ignores, rule-level paths, supported extensions, size limits, parsing, and timeout messages. An explicit include filter does not necessarily undo earlier filtering. Use the installed `semgrep scan --help` to inspect the applicable ignore implementation before overriding a scope decision.

For a focused diagnostic rerun, retain the original configuration and target the file explicitly, saving a new report:

```bash
# Define repo, rules, expected_file, and a fresh out directory for this task.
if semgrep scan --config "$rules" --metrics=off --disable-version-check \
  --verbose --json "$repo/$expected_file" \
  >"$out/focused.json" 2>"$out/focused.log"; then
  scan_status=0
else
  scan_status=$?
fi
printf '%s\n' "$scan_status" >"$out/focused-status.txt"
```

If parsing fails, isolate the syntax/extension or installed parser mismatch before interpreting rule absence. If a rule times out, a narrow rerun or a justified resource adjustment can recover evidence for that rule; it does not retroactively complete the original scan. Record which gap the rerun resolved and which remain. Avoid removing ignore rules globally to fix a single missing-file question.

## Count coverage with an explicit denominator

For each run, report the selected rules/languages, distinct scanned paths, distinct paths with full syntax errors, distinct paths with partial parsing and paths affected by timeouts. Keep diagnostic-event counts separate from file counts: one path can have several errors or affected rules. Read both the JSON errors and stderr skip summary; ignored files, size limits and unsupported inputs can be absent from scanned paths.

When reporting a percentage, name the denominator and use the same run's data. For example, 100 distinct error-affected files among 2,500 scanned files is 4%. Do not divide C# errors by a separate mixed-language run's file count or equate a parsed-line percentage with fully parsed files. Partial parsing does not mean the whole file was skipped; report affected regions when available. If the report does not expose the necessary paths, retain counts without inventing a file-coverage percentage.

Prioritize manual review or a focused diagnostic for relevant error-affected files. Distinguish code inspected manually from code successfully analyzed by Semgrep. A grep for API names can help locate a gap, but does not restore parser/dataflow coverage or prove absence of a vulnerability class. Keep unresolved gaps in the final conclusion even when the scanner exits successfully.

## Compare against a baseline

Use a real locally available Git commit, such as the relevant merge base, with the intended rules and engine held constant. Confirm its meaning with the user/task context. Diff scanning answers which findings are new relative to that baseline; it does not attest to the rest of the repository.

The CLI's `--baseline-commit` has working-tree and repository prerequisites. Preserve local changes and inspect installed help before using it; do not clean/reset a checkout to satisfy the scanner. With a compatible clean checkout:

```bash
# Define repo, baseline, rules, and a fresh out directory.
cd "$repo"
git rev-parse --verify "$baseline^{commit}"
if semgrep scan --config "$rules" --baseline-commit "$baseline" \
  --metrics=off --disable-version-check --error \
  --json-output "$out/new-findings.json" \
  >"$out/diff.log" 2>"$out/diff-errors.log"; then
  scan_status=0
else
  scan_status=$?
fi
printf '%s\n' "$scan_status" >"$out/status.txt"
```

A different ruleset, engine, or ignored path can change the comparison independently of source changes. If prerequisites cannot be met, report a full-scan result or compare separately preserved source snapshots with an explicit limitation; do not label a filtered file list as a full dataflow-aware diff analysis.

The [CLI reference](https://docs.semgrep.dev/cli-reference) describes baseline behavior, resource controls, and include/exclude ordering.
