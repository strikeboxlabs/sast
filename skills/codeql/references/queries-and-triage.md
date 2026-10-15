# Query selection and finding review

Use this reference for selecting suites, resolving packs, interpreting path findings, or reviewing empty results. Inputs are a completed database with known source/build provenance, matching language query packs, and the requested security question.

## Make the query scope reproducible

Use a named code-scanning/security suite or specific query suited to the language. Do not run every file in a pack root: some queries are supporting or diagnostic rather than alert queries. A security-extended suite broadens checks and can increase review noise. It does not guarantee completeness.

Inspect the selected suite before a long run:

```bash
codeql resolve queries \
  codeql/python-queries:codeql-suites/python-security-extended.qls
```

When a required pack is unavailable locally and fetching it is within scope, `codeql pack download codeql/python-queries` retrieves it. Select and record an explicit compatible version for reproducible work; the unversioned name follows available registry versions. Alternatively `database analyze --download` can fetch missing referenced packs. Do not represent a network/pack-resolution failure as an empty scan. A language mismatch requires a matching database and pack, not a forced query invocation.

Record the CLI, query pack versions, suite, source revision, build configuration, and output category. Use distinct SARIF categories for separate language/part analyses that may later be combined or uploaded. Running queries again against the same database can explore another question without rerunning a build, provided the source snapshot remains the one being reviewed.

## Review the evidence behind an alert

Read each relevant SARIF run's rule metadata and `results`. Follow `locations`, `relatedLocations`, and `codeFlows` where present. A path is the analysis model's proposed route; verify important transitions in source, including wrapper behavior, runtime configuration, validation, and whether a claimed control covers the value actually used.

Record the input/source, sensitive operation or defect condition, trust boundary, existing controls, and practical consequence. Deduplicate overlapping alerts by the underlying source condition while preserving the tool/rule evidence. Avoid converting a generic API-use alert into an asserted exploit without supporting source facts.

For empty or unexpectedly sparse output, inspect analysis logs and diagnostic notifications, confirm that the intended suite resolved and ran, and revisit extraction coverage. An empty `results` array says nothing about files that were never extracted or flows a library model cannot represent. Successful CLI execution and absence of findings are separate facts.

If fixes are requested, compare the source change against the reported condition, then re-extract changed source before claiming CodeQL verification of the fix. A newly suppressed alert proves only that it was suppressed. Deliver report/log paths, source locations, disposition and reasoning, and specific coverage limits.

Primary reference: [analyzing code with queries](https://docs.github.com/en/code-security/tutorials/customize-code-scanning/analyze-code).
