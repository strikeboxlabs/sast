# Initial source review

Review date: 2026-10-15. Schema: SAST v0.1, adapted from research-library v0.8. This review uses official documentation/upstream code for command semantics; it is not a scanner benchmark or an executed security assessment.

All seven accepted packages were reviewed as complete entrypoints and selected conditional tasks, including discovery within the first 150 lines. All entrypoints are shorter than that boundary. No accepted package is left unreviewed in this initial scope. The research-library's other tool packages were not migrated or claimed as reviewed.

## Accepted tasks and sources

| Package | Task and consequential interpretation | Primary sources reviewed |
|---|---|---|
| semgrep | Local registry/local-config scanning; JSON/SARIF and error-aware completion; baseline limits; structural rule tests and when taint analysis fits. Community/Pro features and fetched rules affect coverage. | [CLI](https://docs.semgrep.dev/cli-reference), [report fields](https://docs.semgrep.dev/semgrep-appsec-platform/json-and-sarif), [rule tests](https://docs.semgrep.dev/writing-rules/testing-rules), [pattern syntax](https://docs.semgrep.dev/writing-rules/pattern-syntax), [taint](https://docs.semgrep.dev/writing-rules/data-flow/taint-mode/overview) |
| codeql | Extract a source snapshot, select compatible query suites, save local SARIF, and review model paths. Build mode, incomplete extraction, stale databases, and missing packs can invalidate an empty result. | [CLI/entitlement](https://docs.github.com/en/code-security/concepts/code-scanning/codeql/codeql-cli), [prepare source](https://docs.github.com/en/code-security/tutorials/customize-code-scanning/prepare-code-for-analysis), [analyze](https://docs.github.com/en/code-security/tutorials/customize-code-scanning/analyze-code), [compiled languages](https://docs.github.com/en/code-security/how-tos/find-and-fix-code-vulnerabilities/manage-your-configuration/codeql-for-compiled-languages) |
| bandit | Python AST checks; independent severity/confidence; JSON errors; explicit project config, JSON baselines, and nosec auditing. | [CLI](https://bandit.readthedocs.io/en/latest/man/bandit.html), [configuration](https://bandit.readthedocs.io/en/latest/config.html), [JSON fields](https://bandit.readthedocs.io/en/latest/formatters/json.html) |
| gosec | Module/package source checks; real build variants and processing errors; inline-exclusion auditing. Status alone cannot distinguish findings from load errors. | [upstream usage](https://github.com/securego/gosec), [actual CLI flags](https://github.com/securego/gosec/blob/master/cmd/gosec/main.go) |
| brakeman | Rails application scanning; warning/source review; JSON comparison and ignore-file interpretation. Faster/selective modes reduce information and confidence is not severity. | [quickstart](https://brakemanscanner.org/docs/quickstart/), [options](https://brakemanscanner.org/docs/options/), [ignore files](https://brakemanscanner.org/docs/ignoring_false_positives/) |
| cppcheck | C/C++ diagnostics; compilation database import and macro/model interpretation; XML on stderr and configured diagnostic exit status. | [manual](https://cppcheck.sourceforge.io/manual.html), [CLI parser/help](https://github.com/danmar/cppcheck/blob/main/cli/cmdlineparser.cpp), [upstream man source](https://github.com/danmar/cppcheck/blob/main/man/cppcheck.1.xml) |
| trivy | Explicit filesystem dependency/misconfiguration/secret scanners; separate configuration target; data/cache and advisory context. Offline dependency identification is distinct from disabling updates. | [filesystem](https://trivy.dev/docs/latest/target/filesystem/), [CLI](https://www.trivy.dev/docs/latest/guide/references/configuration/cli/trivy_filesystem/), [reports](https://www.trivy.dev/docs/latest/guide/configuration/reporting/), [misconfigurations](https://www.trivy.dev/docs/latest/guide/scanner/misconfiguration/), [secrets](https://www.trivy.dev/docs/latest/guide/scanner/secret/) |

The catalogue selects complementary source-analysis tasks across languages and includes Trivy under its actual adjacent scope. Tool overlap is allowed; no claim that this is an exhaustive inventory or a ranking of all scanners is made. The included Semgrep rule is a deliberately narrow API-choice check with annotated positive/negative static inputs, not a complete security ruleset or a finding from a real application.

## Deferred and bounded scope

- Bearclaw: omitted after the user selected “Leave Bearclaw out for now.” Bearer was not substituted.
- Other scanners: no additional package is implied without a verified useful task. Future additions can follow the authoring prompt and catalogue.
- Controlled-image binary paths, exact installed editions/versions and relevant option differences: deferred to an on-image pass because the authoring host supplies no usable Linux environment. No fabricated environment references were added.
- Actual scans, scanner rule execution, and worker outcome studies: tracked separately in [validation](validation.md). Documentation review is not runtime evidence.

Upstream pages track their current branches/releases. Repeat consequential verification when installed behavior differs. The full scaffold-reuse record is in [reuse](reuse.md); raw authoring captures belong in ignored work/runs rather than in tool packages.

## Catalogue and output-path review, 2026-10-16

All seven complete entrypoints were reviewed for schema-v0.1 activation, task/resource routes, output preservation and the new Board evidence-directory precedence. The scanner commands, report interpretations and conditional references retain the previously reviewed source scope. Added catalogue tags describe their existing supported tasks; Trivy remains complementary configuration/dependency/secret analysis. No new scanner semantics, installed paths or executable readiness were inferred. See [catalogue documentation](catalog.md) and the dated [validation record](validation.md).
