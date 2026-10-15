# SAST skill schema v0.1

Adapted from research-library's tool schema v0.8. The unit is one independently installable `skills/<tool>/SKILL.md`, with optional resources inside that folder. Use the [Semgrep package](../skills/semgrep/SKILL.md) as an example, not a required size or layout.

## Scope and format

Use standard Agent Skills frontmatter with one-line `name` and `description` fields. The lowercase hyphenated name matches the folder and is at most 64 characters. The description identifies actual tool tasks and distinguishes likely misroutes, such as Trivy repository analysis versus application SAST.

Target the one Linux image the user controls. Improve documentation now; verify paths, installed options, build tools, and relevant versions in a later on-image pass. Do not invent environment facts or create empty required references. Shared image facts may live in skill-local references; node-specific details and raw evidence stay ignored.

Each package must work when copied alone. Authoring scripts and maintenance records are not runtime dependencies. Do not create an umbrella skill or require a scanner orchestration framework.

## First read and conditional depth

Near the top, tell the worker to read the entire entrypoint before acting. Identify the common task's essential inputs, required resources, and completion evidence. Current complete material need not be re-read mechanically.

For several substantial modes, provide a small task map: what situation requires each local reference, and what decision it enables. Read a selected reference fully before its procedure. Keep unrelated references unloaded. Short coherent workflows can remain inline.

Review the first 150 lines for discoverability, then read the complete selected task and its resources. This is a partial-read authoring check, not a universal harness limit or length target.

## Operational knowledge

Teach what changes the next decision: choosing a useful rule suite, obtaining sound extraction, identifying excluded inputs, understanding a trace, distinguishing severity from confidence, or recovering from a parse/load error. Connect commands with their inputs, meaningful results, and next steps. Avoid copied help pages, generic security rituals, recipe quotas, and repeated instructions.

For SAST workflows, account for the relevant subset of:

- Source root and revision or working-tree state; language/framework and build configuration.
- Tool version/edition, rules or query packs, configuration, and suppressions.
- Scanned inputs and meaningful gaps: unsupported languages, parse errors, build failures, timeouts, ignored files, absent dependencies, or outdated data.
- Raw machine-readable output, logs, and exit status. Explain each tool's status semantics rather than treating every nonzero status as findings.
- Source-based review: location, trust boundary or defect condition, existing controls, consequence, and fix/review decision. Distinguish a reported pattern from a supported bug.

Completion should answer the requested question with evidence and bounded coverage. Empty output, an empty SARIF `results` array, or a zero exit code is not proof that code is secure. A missing prerequisite is a capability gap, not a successful scan. Do not require every possible scanner or workflow to run.

Use only required or genuinely useful helper scripts. Give exact skill-relative paths and explain when to run them. Label invented output illustrative. Prefer synthetic fixtures with an explicit expected distinction over running unknown project code. A source change needs its own task authorization; a scan report alone does not request autofix or suppression edits.

## Sources and acceptance

Verify important options and interpretations against primary documentation or installed help. Retain useful upstream recovery links with the affected procedure. Keep review dates, full source trails, reuse attribution, and test history in [source review](../docs/source-review.md), [reuse](../docs/reuse.md), and [validation](../docs/validation.md).

Reconcile the whole affected workflow when revisiting a skill. Correct or merge weaker text, preserve useful conditional domain knowledge, and avoid cosmetic rewrites of already conforming packages. Record reviewed/no-change outcomes and concrete deferrals; overlapping tools may each deserve a useful narrow package. A name-only mention is not evidence for a workflow.

Separate documentation review, syntax parsing, scanner execution, and independent worker outcomes. Missing runtime access does not prevent acceptance of documentation-reviewed guidance, but cannot support a runtime claim. Authoring execution restrictions govern what the author runs; supported documentation still needs an honest account of operational effects.

Update the README catalogue, run the checker and relevant tests, and inspect packaging by copying the skill alone. Test changed command behavior on the controlled image when available. Record the schema version and actually reviewed skills in the maintenance record.
