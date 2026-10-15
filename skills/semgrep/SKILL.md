---
name: semgrep
description: Scan local source with Semgrep, review security findings and coverage, and develop tested project-specific pattern or taint rules.
---

# Semgrep source analysis

Read this entire SKILL.md before acting. Use the supplied local checkout, a rule configuration suited to its languages, and the available engine. Completion requires the report, scan status and coverage limits, plus source-based review of the findings relevant to the request.

Read a selected reference completely before its procedure:

| Task | Required resource for that task |
|---|---|
| Initial scan and ordinary finding review | Guidance below; no additional local resource required. |
| Unexpectedly empty results, ignored files, timeouts, or changed-code comparisons | [references/coverage-and-diffs.md](references/coverage-and-diffs.md) |
| New pattern/taint rule or a rule regression | [references/rule-development.md](references/rule-development.md); the supplied starter uses [assets/rules/python-shell-enabled.yaml](assets/rules/python-shell-enabled.yaml) and its paired [test input](assets/rules/python-shell-enabled.py). |

Semgrep is useful for broad source review without compiling the application. Match language support and rule assumptions to the actual framework. Record Community/Pro engine selection: a local Community scan does not establish cross-file coverage or the behavior of platform-only rules.

## Start a local scan

Run from the source repository root after selecting the intended checkout. `p/default` is a registry ruleset fetched over the network; use an approved local rule file/directory for a controlled rule snapshot. Record its identity and, for local rules, a digest. `--metrics=off` disables metrics; it does not make registry retrieval offline.

```bash
repo=$(pwd -P)
out=$(mktemp -d "${TMPDIR:-/tmp}/semgrep.XXXXXX")
semgrep --version >"$out/version.txt" 2>&1
if semgrep scan --config p/default --metrics=off --disable-version-check \
  --error --json-output "$out/findings.json" \
  --sarif-output "$out/findings.sarif" "$repo" \
  >"$out/stdout.log" 2>"$out/stderr.log"; then
  scan_status=0
else
  scan_status=$?
fi
printf '%s\n' "$scan_status" >"$out/status.txt"
printf 'Reports: %s\n' "$out"
```

With `--error`, status 1 can mean findings; without it, findings normally still return 0. Other failures, and errors recorded alongside findings, need inspection. Read JSON `results`, `errors`, and available path/scan summaries together with stderr. Parse failures and timeouts can leave partial findings even when a report exists. The scan does not modify source; autofix is a separate operation.

## Turn matches into useful decisions

For a reported rule ID and location, inspect the matched expression in its enclosing function and the relevant callers. Establish which input is controllable, how it reaches the operation, what validation or safe API is already present, and whether the code path is used. A rule named for injection is still a hypothesis until its assumptions hold in this source.

When a trace is available, verify each meaningful handoff in source. A missing trace is not evidence that no data path exists. Separate a confirmed unsafe condition, a plausible finding needing context, and a false match with a concrete reason. If a fix is requested, prefer a safe API or a checked invariant, then rerun the same rule/configuration and relevant application checks.

Report tool/engine, source scope/revision, rules, errors/exclusions, raw output paths, and the reviewed findings with locations and reasons. State exactly what an empty scan covered. Keep suppression changes separate from proving a fix.

Use the [CLI reference](https://docs.semgrep.dev/cli-reference) for version-specific flags and [JSON/SARIF fields](https://docs.semgrep.dev/semgrep-appsec-platform/json-and-sarif) when interpreting a report.
