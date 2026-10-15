# Package coverage and scan policy

Use this reference when Go source is absent from results, a package fails to load, or the task involves a workspace, platform/tag variant, tests, or suppressions. Required inputs are the intended module roots, build context, dependency availability, full logs/report, and current source state.

## Match the build context

Identify the relevant `go.mod` and any `go.work`. Scan each intended module/package scope explicitly; `./...` from one module is not a monorepo inventory. Keep separate outputs for different module roots and variants. Record toolchain/language version, GOOS/GOARCH, build tags, and cgo requirements when they affect loaded files.

For a known target variant, use its actual values. This command does not choose them for you:

```bash
# Define module_root, target_os, target_arch, build_tags, and a fresh out.
cd "$module_root"
if GOOS="$target_os" GOARCH="$target_arch" gosec -tags "$build_tags" \
  -fmt=json -out="$out/variant.json" ./... \
  >"$out/variant.log" 2>"$out/variant-errors.log"; then
  scan_status=0
else
  scan_status=$?
fi
printf '%s\n' "$scan_status" >"$out/status.txt"
```

Build constraints can exclude source before rules see it. If the requested code is behind another tag/platform, select that intended variant and retain it as separate coverage. Missing headers, cgo tooling, modules, or type errors need resolution or an explicit gap; a forced partial analysis is not equivalent to a loaded package.

Dependencies may require network retrieval. If retrieval is authorized, use the project's dependency process and preserve lock/module changes for review. Otherwise use available cache and report what could not load. Scanning does not require running the application or its tests. `-tests` includes Go test files in analysis when that is the requested scope; it does not execute tests.

## Understand suppressed or filtered output

Inspect `-include`, `-exclude`, `-exclude-dir`, configuration, and generated-file settings. Flags and rule availability vary; use installed help. Lowering the issue count by filtering does not repair source. Keep initial reports for comparison.

For an audit of inline exclusions, use a separate scan with `-nosec`, which ignores `#nosec` comments. It is an override of suppressions, not a request to suppress everything. Where supported, `-track-suppressions` adds suppression metadata, and `-show-ignored` exposes ignored issues. Preserve the normal-policy report and check the installed output format/flag behavior.

When a warning is disputed, inspect the exact guarded value, operation and version conditions. Prefer a targeted explanation over a global rule exclusion. Deliver actual module/variant coverage, processing errors, filter/suppression context, and evidence for any fix or review decision. State unresolved load failures even when other packages were analyzed successfully.

Primary references: [build tags, tests, and exclusions](https://github.com/securego/gosec) and [option semantics](https://github.com/securego/gosec/blob/master/cmd/gosec/main.go).
