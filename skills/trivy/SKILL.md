---
name: trivy
description: Review repository dependency advisories, infrastructure configuration and candidate secrets with Trivy; distinguish package severity, application reachability and verified remediation.
---

# Trivy repository security checks

Read this entire SKILL.md before acting. Required inputs are the supplied local source/configuration scope, available Trivy, selected scanners, and required vulnerability/check data. Completion requires category-specific findings, scan status/data context, and explicit coverage limits. For dependency remediation, configuration context, secrets, or disconnected operation, first read [references/categories-and-data.md](references/categories-and-data.md) completely.

Trivy complements application SAST with dependency vulnerabilities, IaC misconfigurations, and candidate secrets. Use a source-analysis tool for application control/dataflow bugs. A filesystem dependency finding is a package/advisory observation, not proof that application code reaches the affected behavior.

## Scan the local repository

This example explicitly enables all three categories; filesystem defaults do not imply misconfiguration scanning. It may retrieve vulnerability databases, checks, and dependency metadata. Record the data/version context, and use the reference when network access is unavailable or constrained. Existing `trivy.yaml`, ignore files, and environment settings can affect output.

When Board supplies `BOARD_EVIDENCE_DIR`, keep reports in a fresh subdirectory there. Standalone use falls back to `TMPDIR` or `/tmp`. Stop if the output directory cannot be created; do not silently redirect evidence elsewhere.

```bash
repo=$(pwd -P)
output_root=${BOARD_EVIDENCE_DIR:-${TMPDIR:-/tmp}}
mkdir -p -- "$output_root" || exit 1
out=$(mktemp -d "$output_root/trivy.XXXXXX") || exit 1
trivy --version >"$out/version.txt" 2>&1
if trivy fs --scanners vuln,misconfig,secret --format json \
  --output "$out/findings.json" --exit-code 1 "$repo" \
  >"$out/stdout.log" 2>"$out/stderr.log"; then
  scan_status=0
else
  scan_status=$?
fi
printf '%s\n' "$scan_status" >"$out/status.txt"
printf 'Reports: %s\n' "$out"
```

Inspect JSON `Results` and the relevant `Vulnerabilities`, `Misconfigurations`, and `Secrets` collections, together with logs and enabled scanner/settings context. Reports may contain sensitive source/secret fragments; use IDs, file/line, and redacted summaries in user-facing findings. Do not validate candidate credentials against external services as part of static scanning.

`--exit-code 1` makes matching issues produce a nonzero status; processing/data failures can also fail. Without that option, findings do not necessarily fail the command. A category absent from output may have no findings, no recognized input, an exclusion, or no enabled scanner. Establish which before describing coverage.

For dependencies, inspect manifest/lockfile, package identity, installed/fixed version and advisory applicability. For configuration, inspect the real deployment inputs and whether the check's assumption applies. For a candidate secret, distinguish test material from a plausible credential without reproducing the value. Escalate the evidence to the requested remediation/review workflow; suppressing the result does not repair the source.

Keep advisory severity separate from application impact and consolidate repeated observations of the same package/advisory. For resolved-input requirements, finding identity and before/after evidence, use the dependency section of the required category reference. A build-system audit warning is useful evidence, but does not establish that Trivy recognized or analyzed that dependency set.

Report the source scope, version/database/check state, scanners, filters/exclusions, raw output/status paths, and category-specific decisions with remaining gaps. A repository scan does not attest to an image, running workload, Git history, or application dataflow unless those distinct targets were actually analyzed.

Primary references: [filesystem target](https://trivy.dev/docs/latest/target/filesystem/), [filesystem CLI](https://www.trivy.dev/docs/latest/guide/references/configuration/cli/trivy_filesystem/), and [report interpretation](https://www.trivy.dev/docs/latest/guide/configuration/reporting/).
