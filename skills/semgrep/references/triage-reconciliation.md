# Evidence-backed triage and handoffs

Read this reference before rejecting a match because a control supposedly protects it, grouping many matches into one conclusion, or passing a disposition to another worker. The inputs are the original Semgrep JSON report, its source snapshot, and source evidence for the decision. This is a reporting workflow, not permission to probe a service or execute an application.

## What supports a negative disposition

A rejected match needs evidence for the relevant condition, not merely an assertion that the component is hardened:

- Establish the input's provenance and the boundary the rule is asking about. Persisted or synchronized metadata can have an external origin even when no request parameter reaches the sink. Configuration is a trust assumption to identify, not a universal proof of safety.
- Identify the operation with an external effect and the control intended to prevent it. Check their order. Post-action validation can protect a returned value without preventing the earlier effect. A post-read length limit does not demonstrate a bounded read.
- Check effective construction and configuration when those affect the control: constructor callers, dependency-injection registration, client/handler settings, middleware, wrappers and relevant feature gates. A class-level check or comment does not establish what a framework performs before returning to that class.
- Preserve the reason and source locations that support the disposition. If a required dependency or runtime setting is unavailable, keep the candidate unresolved with that question. Distinguish a defect in source from a deployment-dependent impact claim.

A harmless synthetic test of a configuration invariant can support a defensive conclusion without network requests or production access. State exactly what it tested; a checked property is not proof of every deployment outcome. Reopen a disposition when new evidence contradicts it. A prior worker's prose is a lead to inspect, not an independent source of authority.

## Preserve every match

Use [scripts/reconcile_triage.py](../scripts/reconcile_triage.py) for grouped triage and handoffs. It needs Python 3.10+ and uses the standard library only. It reads reports/source and writes only the ledger explicitly requested with `--init`; it runs no scanner, target code or network request. Reports can contain sensitive snippets, so the ledger contains identifiers, locations and decisions rather than copying source text.

After a scan, initialize a fresh ledger. Set `skill_dir` to the installed Semgrep package; keep `repo` and `out` tied to the scan already performed:

```bash
python3 "$skill_dir/scripts/reconcile_triage.py" \
  --source-root "$repo" --report "$out/findings.json" \
  --ledger "$out/triage.json" --init
```

The initializer refuses to overwrite an existing ledger. Each unique match begins unresolved. Fill its disposition as `confirmed`, `rejected` or `unresolved`, the source-based reason, and any unresolved questions. Resolved decisions require source evidence locations and SHA-256 digests; retain the exact source bytes used to support the decision. Do not relabel an unresolved question just to obtain a zero unresolved count.

For each resolved entry, `evidence` contains objects with `path`, `line` and `sha256`; optional `end_line` and `note` identify the relevant source range and what it supports. Include a control's effective registration/configuration evidence when the negative conclusion depends on it. Compute the digest with the source file unchanged, for example `sha256sum -- "$repo/path/to/source.cs"`. A digest binds a decision to content; it is not evidence of correct reasoning.

Report and evidence source paths must resolve within `--source-root`; they may be relative or absolute within that root. An initialization binds the files currently present there, so preserve the actual scan snapshot rather than pairing an older report with a subsequently changed checkout. Keep the initialized `version`, report digests and match identities unchanged while recording decisions.

Validate after reviewing or merging worker decisions:

```bash
python3 "$skill_dir/scripts/reconcile_triage.py" \
  --source-root "$repo" --report "$out/findings.json" \
  --ledger "$out/triage.json"
```

Supply additional `--report` arguments to account for several preserved reports. Identical rule/path/location matches are deduplicated; overlapping rules can still describe one underlying defect, so unique matches are not a vulnerability count. The checker binds report and source digests, rejects stale or missing/duplicate/unknown entries, requires evidence for resolved decisions, and retains unresolved questions. Its output counts confirmed, rejected and unresolved match dispositions separately. A successful validation with unresolved entries is an incomplete assessment, not an all-clear result.

The checker cannot establish whether a reviewer correctly understood a protection or selected meaningful evidence. The ordering/construction checks above and explicit review of unresolved assumptions remain necessary. A final report must qualify rule/parser coverage and distinguish confirmed application defects from audit matches even when every ledger entry is accounted for.
