---
name: gosec
description: Analyze Go packages with gosec, review security findings, and resolve package-loading, dependency, build-tag, or suppression gaps in the scan.
---

# gosec Go package analysis

Read this entire SKILL.md before acting. Required inputs are the local module/package scope, installed gosec and compatible Go toolchain, and the intended build configuration. Completion requires findings plus package/file coverage and processing errors. For workspaces, tags, unavailable dependencies, tests, or suppression review, read [references/package-coverage.md](references/package-coverage.md) completely first.

gosec analyzes Go source using its package/type context. Use it for Go-specific security checks and review the source behind each result. It is not a dependency vulnerability inventory. A package that did not load is an unscanned/partial area, even if other packages produced findings.

## Scan a module

Run this from the intended module root. Loading packages can need cached or retrievable dependencies; record a missing dependency instead of silently fetching/changing project dependencies. `./...` does not promise coverage of every nested module in a monorepo.

```bash
repo=$(pwd -P)
out=$(mktemp -d "${TMPDIR:-/tmp}/gosec.XXXXXX")
gosec -version >"$out/version.txt" 2>&1
go version >"$out/go-version.txt" 2>&1
cd "$repo"
if gosec -fmt=json -out="$out/findings.json" ./... \
  >"$out/stdout.log" 2>"$out/stderr.log"; then
  scan_status=0
else
  scan_status=$?
fi
printf '%s\n' "$scan_status" >"$out/status.txt"
printf 'Reports: %s\n' "$out"
```

Read `Issues`, `Stats`, the report's Go/package processing errors, and stderr together. Status 1 can mean findings or processing errors. `-no-fail` changes status behavior and is not a cure for incomplete package loading. Retain rule ID, location, severity, confidence, and source context for reviewed issues.

Default rule sets, excluded directories, tests, and analyzer behavior depend on the installed release and configuration. Capture consequential settings. Do not start by hiding low-confidence findings or excluding whole packages merely to obtain a zero status.

## Review the actual defect condition

For file/path issues, check how a path is constructed, constrained, and used. For process/query APIs, check argument or query construction and the actual source of data. For integer/bounds issues, inspect types, range checks, architecture assumptions, and whether the checked value is the one later used. Severity and confidence guide review order; neither establishes reachability.

Go language changes can invalidate assumptions behind older warnings. Evaluate the source's toolchain and language version, especially when a check concerns loop variables, conversions, or newer library APIs. Read installed rule descriptions rather than transferring an old rule ID's meaning blindly.

If a fix is requested, rerun the same configuration and the project's relevant Go checks in the requested scope. Report module/build scope, versions, rule/config selection, errors, status and report paths, and dispositions with source reasons. An empty report for packages that failed to load is not a clean result.

Primary references: [gosec usage](https://github.com/securego/gosec) and [CLI option definitions](https://github.com/securego/gosec/blob/master/cmd/gosec/main.go).
