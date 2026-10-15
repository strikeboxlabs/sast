---
name: brakeman
description: Scan Ruby on Rails applications with Brakeman, review request-to-operation security warnings, and inspect scan errors, ignored warnings, or report comparisons.
---

# Brakeman Rails analysis

Read this entire SKILL.md before acting. Required inputs are a local Rails application root and an available Brakeman executable. Completion requires warning review with source context, scan errors and effective coverage, and report/status evidence. For ignore files, comparisons, or speed/coverage settings, read [references/triage-and-policy.md](references/triage-and-policy.md) completely first.

Use Brakeman for Rails-aware source analysis across application components. It does not need the application server to run, and does not establish dependency vulnerability coverage or general coverage of arbitrary Ruby programs. In a monorepo, select each actual Rails app root rather than assuming the repository root is one application.

## Scan an application

Prefer the available installed executable. If the project requires its already provisioned bundled version, use `bundle exec brakeman` instead; do not install a bundle merely to scan source. Keep the detected Rails version and existing configuration/ignore files in the report context.

```bash
app=$(pwd -P)
out=$(mktemp -d "${TMPDIR:-/tmp}/brakeman.XXXXXX")
brakeman --version >"$out/version.txt" 2>&1
if brakeman --path "$app" --format json --output "$out/findings.json" \
  --no-pager >"$out/stdout.log" 2>"$out/stderr.log"; then
  scan_status=0
else
  scan_status=$?
fi
printf '%s\n' "$scan_status" >"$out/status.txt"
printf 'Reports: %s\n' "$out"
```

Read JSON `warnings`, `errors`, `scan_info`, and any `ignored_warnings` along with stderr. Nonzero status may reflect security warnings, scan errors, or both. Disabling exit-on-warning/error changes automation behavior and does not complete a failed analysis. Confirm that expected controllers, models, views, and libraries were considered.

## Review Rails-specific assumptions

For a warning, retain its type/check, confidence, fingerprint, file/line and relevant code. Trace request data through controller/model/view behavior to the flagged operation. Check strong parameters, parameterized queries, escaping or safe-buffer behavior, and authorization only where they address that operation's specific risk. A control's name alone is not evidence that it applies.

Inspect the actual route/caller and relevant Rails configuration before claiming a path is exposed. Brakeman's confidence expresses certainty of its warning; it is not a severity ranking. A warning involving an unknown helper may need the helper's implementation rather than an immediate source change.

When a fix is requested, rerun the same scan configuration and relevant application checks. Report source/app/version context, scan settings, coverage/errors, raw output paths, and reviewed warnings with decisions and evidence. An empty warning list with scan errors or ignored warnings needs those limitations stated.

Primary references: [quickstart](https://brakemanscanner.org/docs/quickstart/) and [options/report behavior](https://brakemanscanner.org/docs/options/).
