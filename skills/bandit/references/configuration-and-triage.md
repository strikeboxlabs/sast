# Configuration, baselines, and suppressions

Use this reference when the project already has Bandit policy, when comparing against an accepted baseline, or when reviewing suppressed results. Inputs are the source root, configuration/baseline files with provenance, installed plugin set, and the task's review scope.

Check which configuration the command actually loads. An INI `.bandit` and YAML/TOML plugin configuration are different inputs. For a project with `[tool.bandit]`, pass `-c pyproject.toml` explicitly; TOML support may require the Bandit TOML extra in that installation. Do not invent a default project policy when none exists.

```bash
# Set repo to the checkout and out to a fresh output directory.
if bandit -r "$repo" -c "$repo/pyproject.toml" -f json \
  -o "$out/configured.json" >"$out/stdout.log" 2>"$out/stderr.log"; then
  scan_status=0
else
  scan_status=$?
fi
printf '%s\n' "$scan_status" >"$out/status.txt"
```

Rule selections (`-t`), skips (`-s`), exclusions, and severity/confidence thresholds change coverage. Review the configuration before explaining why an expected issue is absent. In a monorepo, retain package-specific context rather than applying one package's exceptions to all Python code.

## Baseline comparisons

`-b` accepts a JSON Bandit baseline. Use a known prior report from the intended revision with equivalent paths, plugin versions, configuration, and thresholds. A comparison reports what survives that baseline logic; it does not establish that baseline findings are fixed or accepted by the current task.

```bash
# Set baseline to the known earlier JSON report, repo, and fresh out.
if bandit -r "$repo" -b "$baseline" -f json -o "$out/new-findings.json" \
  >"$out/baseline.log" 2>"$out/baseline-errors.log"; then
  scan_status=0
else
  scan_status=$?
fi
printf '%s\n' "$scan_status" >"$out/status.txt"
```

Keep the original full report as well as the filtered result. Source moves or changed environments can alter matching; inspect surprising additions/removals instead of treating the comparison as a stable vulnerability identity system.

## Review suppression meaning

Bandit supports `# nosec` and specific test IDs in suppression comments. For an audit of ignored findings, use a separate scan with `--ignore-nosec`; preserve the normal-policy report for comparison. A targeted justified suppression is narrower than disabling the plugin across the repository, but editing policy still requires that task to be in scope.

When review cannot establish input origin, a framework wrapper, or a security invariant, name the missing fact. AST evidence supports the API-use observation; it does not fill that gap. Deliver the selected configuration, baseline identity where used, errors, actual reviewed findings, and reasons for dispositions.

Primary references: [configuration](https://bandit.readthedocs.io/en/latest/config.html) and [CLI/baseline options](https://bandit.readthedocs.io/en/latest/man/bandit.html).
