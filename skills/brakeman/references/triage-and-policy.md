# Ignore files, comparisons, and coverage

Use this reference when a warning is missing, an ignore file exists, reports are compared, or faster/selective scans are proposed. Inputs are the app root, current and prior reports if applicable, effective Brakeman settings, and the source/configuration relevant to a warning.

## Keep scan scope visible

Brakeman can load `config/brakeman.ignore`; review ignored warnings and their reasons before explaining an empty result. `brakeman -I` is an interactive ignore-file editor, so it changes scan policy and is not a read-only investigation command. Review an existing file directly first.

File exclusions and options such as `--skip-libs`, `--no-branching`, and `--faster` reduce analysis information. Because source relationships cross files, an exclusion can affect findings elsewhere. A focused rerun may help one question, but does not replace full-app coverage. Record all such settings.

Optional checks can be inspected with `brakeman --optional-checks`; `-A` enables all checks when that broader review is desired. Increasing checks and raising a confidence threshold are different choices. `-w3` retains only high-confidence warnings; it does not lower the severity of omitted warnings.

## Compare a known report

Use a prior JSON report from the intended source revision, with equivalent tool/configuration, as the comparison input. From the app root, save a fresh result:

```bash
# Define app, baseline (an earlier JSON report), and a fresh out directory.
if brakeman --path "$app" --compare "$baseline" --no-pager \
  >"$out/comparison.json" 2>"$out/comparison-errors.log"; then
  scan_status=0
else
  scan_status=$?
fi
printf '%s\n' "$scan_status" >"$out/status.txt"
```

The comparison groups new and fixed warnings according to report matching. Verify a claimed fixed warning against the actual source change and scan settings: changing a helper model, ignore fingerprint, skipped file, or tool version may change matching without repairing the underlying issue. Keep a normal full report alongside the comparison.

## Disposition with evidence

For an apparent false positive, identify the exact value and operation and inspect the helper/control that makes it safe. An HTML-escaping helper does not automatically establish URL protocol safety or SQL parameterization. If modeling a safe helper is requested, validate its implementation and call context before changing policy.

Retain warnings that require missing runtime/configuration facts as unresolved with that fact named. Preserve the default scan evidence, justified source conclusions, scan errors, and any policy changes as separate artifacts. A suppression alone is never verification of a source fix.

Primary references: [options](https://brakemanscanner.org/docs/options/) and [ignore-file behavior](https://brakemanscanner.org/docs/ignoring_false_positives/).
