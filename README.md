# sast

For selective Board/Pi loading, use the optional [skill catalogue](docs/catalog.md). Packages remain independently installable; category views do not require moving folders.

Independent Agent Skills for finding and reviewing security bugs through a CLI. Start with the tool that fits the source language and question; install only the skill folders the worker needs. Each package contains its own operational guidance and conditional references.

These skills target the Linux image you control. They document tool use; they do not install scanners, provision accounts, or enable hosted analysis. The initial packages are documentation reviewed. See [validation](docs/validation.md) for the checks actually performed and remaining runtime work.

## Tool skills

| Skill | Use it for | Useful distinction |
|---|---|---|
| [semgrep](skills/semgrep/SKILL.md) | Source scanning, report triage and tested project-specific rules | Build-free source checks; test custom matching first, account for parser coverage and reconcile candidates across handoffs. |
| [codeql](skills/codeql/SKILL.md) | Database-backed analysis and paths through supported languages, including C# | Sound extraction, matching query packs and applicable licensing; preserve SDK and database provenance. |
| [bandit](skills/bandit/SKILL.md) | Python security checks | AST checks with separate severity and confidence; not a whole-program dataflow proof. |
| [gosec](skills/gosec/SKILL.md) | Go package security checks | Package loading, build tags, dependencies, and processing errors determine coverage. |
| [brakeman](skills/brakeman/SKILL.md) | Ruby on Rails security checks | Rails-specific interpretation of controllers, models, views, and request data. |
| [cppcheck](skills/cppcheck/SKILL.md) | C/C++ defects such as lifetime, bounds, and uninitialized-value problems | Prefer real compilation settings; distinguish suspected defects from modeling gaps. |
| [trivy](skills/trivy/SKILL.md) | Repository dependencies, IaC misconfigurations, and exposed secrets | Separate advisory severity from application impact; consolidate repeated package/advisory observations. |

For a mixed repository, start with Semgrep and add the relevant language specialist. Choose CodeQL when its supported language and extraction model match the question. Use Trivy alongside source analysis for manifests and deployment files. Running every tool is not a completion criterion, and agreement between scanners does not establish reachability.

Bearclaw is omitted at the user's request. No Bearer package is implied by that name.

## Start here

- [Setup, install a skill, and validate](GETTING_STARTED.md)
- [Authoring schema](authoring/schema.md) and [creation prompt](authoring/create-skill.prompt.md)
- [Source review and tool decisions](docs/source-review.md)
- [Reused research-library components](docs/reuse.md)
- [Runtime and worker evaluation cases](evaluation/README.md)

```text
skills/<tool>/SKILL.md       Discoverable, independently installable entrypoint
skills/<tool>/references/   Conditional operating knowledge
skills/<tool>/assets/       Task-specific inputs, where useful
authoring/                  Maintainer schema and prompts
scripts/, tests/            Repository checks and help-capture utilities
docs/                       Sources, reuse, and actual validation history
work/, runs/                Ignored raw inputs and execution artifacts
```

A finding should lead to a source-based explanation and an appropriate fix or review decision. Reports should identify scan failures and exclusions as well as findings. A successful empty scan means only that the selected checks reported no findings in the analyzed scope.
