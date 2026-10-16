---
name: bandit
description: Scan Python source for security-sensitive constructs with Bandit, review severity and confidence, and diagnose exclusions, parse failures, or baseline behavior.
---

# Bandit Python security review

Read this entire SKILL.md before acting. Required inputs are the intended Python source scope and an available Bandit installation. Completion requires findings with source context, scan errors/coverage, configuration and status, and a supported review decision. For project configuration, baselines, or suppression review, first read [references/configuration-and-triage.md](references/configuration-and-triage.md) completely.

Bandit runs security plugins over Python syntax trees. It is useful for risky API usage and insecure settings; a syntactic match does not establish attacker control or whole-program reachability. Use severity to describe the potential issue and confidence to describe the check's certainty; one is not a substitute for the other.

## Scan and preserve errors

From the local source root, this example excludes only conventional virtual-environment directories. Confirm that those exclusions fit the actual checkout. Keep tests in scope unless the task gives a reason to exclude them.

When Board supplies `BOARD_EVIDENCE_DIR`, keep reports in a fresh subdirectory there. Standalone use falls back to `TMPDIR` or `/tmp`. Stop if the output directory cannot be created; do not silently redirect evidence elsewhere.

```bash
repo=$(pwd -P)
output_root=${BOARD_EVIDENCE_DIR:-${TMPDIR:-/tmp}}
mkdir -p -- "$output_root" || exit 1
out=$(mktemp -d "$output_root/bandit.XXXXXX") || exit 1
bandit --version >"$out/version.txt" 2>&1
if bandit -r "$repo" -x "$repo/.venv,$repo/venv" \
  -f json -o "$out/findings.json" \
  >"$out/stdout.log" 2>"$out/stderr.log"; then
  scan_status=0
else
  scan_status=$?
fi
printf '%s\n' "$scan_status" >"$out/status.txt"
printf 'Reports: %s\n' "$out"
```

Inspect JSON `results`, `errors`, and `metrics`. For each issue, retain the test ID, filename/line, issue text, severity and confidence. Syntax errors or unreadable files can leave a partial report. A nonzero exit needs the report/log context; a zero status alone does not establish coverage. `--exit-zero` deliberately changes finding-related status and should not be silently added to a gate.

Start without severity/confidence filtering when discovering the repository's issues. A later `-ll -ii` view shows at least medium severity and confidence; it is a filtered review view, not evidence that omitted issues disappeared. Preserve the initial report.

## Decide whether the source is unsafe

Inspect the flagged call and value provenance. For example, a subprocess warning needs the actual API, `shell` behavior, and command construction; a serialization warning needs the input's trust origin and loading API. Verify the named control or safe alternative in source rather than relying on the warning title.

Report confirmed unsafe use, context-dependent findings, and false matches with a concrete source reason. If a fix is requested, rerun the same plugin/configuration on the changed scope and relevant application checks. Do not turn a new `# nosec` comment into proof of a fix.

Include source revision/scope, Bandit version/configuration, exclusions, errors, status, report path, and reviewed issues. An empty result with parse failures is a partial scan. An empty successful result covers the enabled AST plugins and scanned files only.

Primary references: [CLI options](https://bandit.readthedocs.io/en/latest/man/bandit.html) and [JSON report fields](https://bandit.readthedocs.io/en/latest/formatters/json.html).
