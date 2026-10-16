---
name: cppcheck
description: Analyze local C/C++ source with Cppcheck for bounds, lifetime, uninitialized-value, and related defects; review compilation settings and modeling gaps.
---

# Cppcheck C/C++ defect analysis

Read this entire SKILL.md before acting. Required inputs are the intended C/C++ source scope, available Cppcheck, and relevant compilation settings when known. Completion requires diagnostics tied to source conditions, status/logs, and coverage/modeling limits. If a compilation database exists, macros/includes matter, or expected code is missing, first read [references/build-context.md](references/build-context.md) completely.

Use Cppcheck for static defect review without running the target program. Real build context improves interpretation; a default scan is provisional where macros, generated headers, platform types, or library contracts change behavior. Warnings and performance/portability diagnostics are not all security vulnerabilities.

## Start without a build database

Run from the intended source root. This starting scan enables selected additional diagnostic groups while retaining default error checks. Prefer the build-context workflow when the project supplies `compile_commands.json`.

When Board supplies `BOARD_EVIDENCE_DIR`, keep reports in a fresh subdirectory there. Standalone use falls back to `TMPDIR` or `/tmp`. Stop if the output directory cannot be created; do not silently redirect evidence elsewhere.

```bash
repo=$(pwd -P)
output_root=${BOARD_EVIDENCE_DIR:-${TMPDIR:-/tmp}}
mkdir -p -- "$output_root" || exit 1
out=$(mktemp -d "$output_root/cppcheck.XXXXXX") || exit 1
cppcheck --version >"$out/version.txt" 2>&1
if cppcheck --enable=warning,performance,portability \
  --xml --xml-version=2 --error-exitcode=1 "$repo" \
  >"$out/progress.log" 2>"$out/findings.xml"; then
  scan_status=0
else
  scan_status=$?
fi
printf '%s\n' "$scan_status" >"$out/status.txt"
printf 'Reports: %s\n' "$out"
```

Cppcheck writes XML diagnostics to stderr; progress is on stdout. Inspect the XML and progress log before treating the run as complete. If startup or parsing fails, stderr may contain failure text rather than a valid report. `--error-exitcode=1` requests a nonzero diagnostic status; it is not enough to distinguish findings from command/processing failures by status alone.

For relevant XML diagnostics, retain the ID, severity, message, source locations and any inconclusive marker. Read the complete condition in source: allocation/free ownership, bounds and lengths, initialization on all relevant branches, or arithmetic type/range. Verify assumptions against the actual build variant.

An apparent defect can depend on an unknown function contract or macro configuration. Name that gap and use the build-context reference instead of dismissing the warning or asserting a bug. Treat `--inconclusive` as an optional broader hypothesis set whose results need review, not a requirement for the initial scan.

If a fix is requested, rerun with the same compilation settings and perform relevant build/tests in the authorized scope. Report source/configuration, Cppcheck version, selected diagnostics, missing-source/modeling limits, status and raw reports, and source-based dispositions. Zero diagnostics under an invented build configuration do not establish safety.

Primary references: [manual](https://cppcheck.sourceforge.io/manual.html) and [upstream CLI implementation](https://github.com/danmar/cppcheck/blob/main/cli/cmdlineparser.cpp).
