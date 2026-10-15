# Category review and data availability

Use this reference for dependency remediation, configuration context, candidate secrets, or restricted-network operation. Inputs are the selected category/target, complete scan artifacts, effective Trivy configuration, and data/cache state.

## Dependencies and advisory applicability

Use a supported manifest/lockfile for the actual package set. A manifest without resolved versions or an unsupported ecosystem can limit detection. Record the report target, package type/name, installed version, vulnerability ID, fixed version if any, and the source of advisory severity.

Inspect direct/transitive ownership and the controlling lockfile before proposing an update. A dependency advisory does not prove reachable application behavior; a reachability conclusion needs separate source evidence. `--ignore-unfixed` or severity filtering changes what is displayed, not whether the dependency is present. Preserve the initial scope and any policy exceptions when comparing after a fix.

After an authorized dependency change, rescan the updated resolved inputs with recorded data. Do not infer a container's final installed package set solely from a repository lockfile.

## IaC and deployment context

`trivy config` is useful for a configuration-only task. This selects misconfiguration analysis rather than adding dependency/secret checks implicitly:

```bash
# Define config_root as the intended configuration directory and out as fresh output.
if trivy config --format json --output "$out/configuration.json" \
  --exit-code 1 "$config_root" >"$out/configuration.log" \
  2>"$out/configuration-errors.log"; then
  scan_status=0
else
  scan_status=$?
fi
printf '%s\n' "$scan_status" >"$out/status.txt"
```

For Helm/Terraform or other parameterized inputs, identify the actual values, variables, modules, and deployment environment. A default-value check can describe a different deployment. Read check ID, cause/location and remediation, then verify the relevant effective setting. Do not deploy or apply IaC to validate a static finding.

## Candidate secrets

Secret matches are candidates, and this filesystem scan is not a full Git-history review. Check the matched file's purpose and whether the material is a documented dummy value, fixture, or plausible active credential. Keep real values out of summaries and new fixtures. Validation or rotation is a separate task with external effects; do not test the credential while explaining a local report.

Existing secret configuration, allow rules and ignore settings can hide matches. Review their actual scope before declaring a category clean. Built-in allow rules also skip silently: paths matching `test`, `example`, `vendor/`, `/usr/(share|include|lib)/`, or `.md`, and any content containing 'example'. A fixture under such a path or using example credentials will not appear in output; move it to a neutral path with renamed values to verify secret scanning. An exception justified for one fixture should not broadly silence a credential type across production code.

## Data freshness and disconnected operation

Keep Trivy version, vulnerability DB metadata/freshness, check bundle context, scanner selection, and filters with the report. A missing DB or failed check-bundle retrieval is a prerequisite failure, not evidence that the source has no issues.

`--offline-scan` prevents dependency-identification API requests; it does not by itself suppress every data update. A disconnected workflow also needs compatible cached vulnerability/check data and the relevant installed update controls, such as `--skip-db-update`, `--skip-java-db-update`, and `--skip-check-update`. Version checks and any configured remote integrations need consideration too. Inspect installed help before claiming a no-network run; report older cache data honestly. Do not add skip-update flags to a missing cache and call that a completed scan.

Primary references: [misconfiguration scanning](https://www.trivy.dev/docs/latest/guide/scanner/misconfiguration/), [secret scanning](https://www.trivy.dev/docs/latest/guide/scanner/secret/), and [filesystem flags/data controls](https://www.trivy.dev/docs/latest/guide/references/configuration/cli/trivy_filesystem/).
