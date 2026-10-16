# Skill catalogue for selective loading

[`catalog.json`](../catalog.json) is optional selection metadata for schedulers such as Board. It lists every physical skill once while leaving the flat, independently installable packages unchanged. A copied skill does not need the catalogue or repository helpers. The canonical name and discovery description remain in its `SKILL.md`.

## Schema version 1

```json
{
  "schema_version": 1,
  "library_id": "sast",
  "skills": [
    {
      "id": "semgrep",
      "path": "skills/semgrep",
      "tags": ["execution:linux", "task:static-analysis"],
      "requires": []
    }
  ]
}
```

This abbreviated example shows the shape, not the full catalogue. `id` must equal the package folder and frontmatter name; `path` is exactly `skills/<id>` relative to this checkout. Consumers identify a package across libraries using `library_id` plus `id`, and detect duplicate Pi names before exposing a combined selection. Paths must remain inside their package and library. Do not rename or copy packages to create category views.

Tags are overlapping facets, not exclusive folders:

| Facet | Meaning |
|---|---|
| `task:` | A supported task, such as `source-review`, `static-analysis`, `finding-triage`, `config-diagnostics`, `offline-analysis`, `data-inspection`, `archive-inspection`, `runtime-inspection`, or `build-diagnostics`. |
| `execution:` | The environment for the documented procedure. Current Linux guidance uses `execution:linux`; this does not classify every inspected target as Linux. |
| `target:` | A known target technology, such as `rails`. Absence means unspecified, not unsupported. |
| `language:` | An explicitly supported language, such as `python`, `go`, `ruby`, `c`, `cpp`, `php`, `javascript`, `java`, or `csharp`. |
| `artifact:` | Relevant input/output kind, such as `source`, `binary`, `core`, `config`, `archive`, `json`, `document`, or `scan-report`. |

`classification:unreviewed` marks entries whose routing classification has not been reviewed. Such entries retain `execution:linux` and make no `task:` claims. This marker concerns catalogue classification only: its absence is not a claim of complete schema migration, runtime testing or worker effectiveness. The initial classification reviews all seven complete scanner entrypoints. It preserves Trivy's configuration/dependency/secret role rather than claiming application dataflow coverage.

`requires` holds declared executable names that Board currently checks through the daemon account's PATH. It is currently empty because the packages' executable requirements have not been classified. An empty list means unspecified prerequisites, not dependency-free or ready to execute. The skill itself remains the source of its task prerequisites. Tags and requirements do not grant permissions or enforce an execution boundary.

## Board and Pi

This integration targets Debian-derived Linux hosts. `execution:linux` describes the documented execution environment; it does not establish tool installation or compatibility with other distributions.

Install the full checkout where the local Board daemon's worker account can read it. Add the absolute path to its `catalog.json` file to Board's `skills.catalogs` list, then select a small profile by task and technology. Board resolves matching catalogue records to complete skill directories; Pi receives only the selected directories through repeatable `--skill` arguments. Keeping `--no-skills` disables unrelated automatic discovery while explicit paths remain available in Pi 1.3. A root catalogue does not itself change Pi discovery.

Keep profiles and routing decisions in Board. Combine a small common selection with task/language additions; use separate facts for the worker's OS and the target technology. Missing classification or a missing tool is a recorded coverage gap, not permission to silently claim complete coverage. A profile may be selected explicitly when the initial task is ambiguous. Board's per-attempt manifest records profile IDs, catalogue/package hashes, source/snapshot paths and estimated metadata cost; retain Git revisions separately when needed. A later task can use a different selection without altering packages.

Skill metadata exposure, reading an entrypoint, following its conditional references, and a correct worker outcome are separate observations. The catalogue does not establish a fixed safe skill count or improved efficiency. Compare useful outcomes, omitted prerequisites, actual loading, irrelevant reads, time and usage on matched tasks before tuning a budget.

## Maintain and check

Add a record when adding a physical package. Review the actual supported task before replacing `classification:unreviewed` with factual facets; avoid inferring capabilities from the tool name alone. Keep prerequisites unknown until supported. Catalogue classification need not rewrite the skill body or replace its source/validation record.

```bash
python3 -B scripts/check_catalog.py
python3 -B scripts/check_repository.py
python3 -B -m unittest discover -s tests -v
```

The standard-library checker rejects malformed/duplicate JSON keys, unknown schema fields, duplicate IDs/tags/requirements, noncanonical or escaping paths, name mismatches, unsupported facets, and missing/unknown packages. The repository checker includes it when a catalogue is present. No catalogue is required for an isolated skill copy. These checks establish catalogue consistency and packaging, not installed capabilities or successful scans.
