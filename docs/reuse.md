# Reuse from research-library

Reviewed on 2026-10-15 against local research-library commit `4f2c188fcc1477fa230ce447ef1b6243daa0cd40` (`updates`). The source checkout was clean when inspected. Reuse was requested by the repository owner; this new repository has no runtime dependency on the original checkout.

## Unmodified copies

These files retain the source bytes, verified by SHA-256 during bootstrap:

| File | SHA-256 |
|---|---|
| [.gitattributes](../.gitattributes) | `7693afe95f393d7f6e01176f4d845de8ddd2ecee8bd6211ac7d0eb4bef409ec3` |
| [.gitignore](../.gitignore) | `b0e4791cbfc3b3c152156589d86029ac9a3f9a77c2adfb95fe45cac23abfea79` |
| [scripts/check_repository.py](../scripts/check_repository.py) | `aa577a496d47d7a97c47410e5200bd0d8b2e2e98b4c957b0b56240da521712fc` |
| [scripts/capture_help.py](../scripts/capture_help.py) | `e82aeda3285dbaf5a82d3d1e70a20eccc0027d97372dc3422ddf43e1c387b2f7` |
| [tests/test_check_repository.py](../tests/test_check_repository.py) | `aca5a0afacf36b506703bc9699c98c4e17a745d5ec6ed88cdd88fab3a1bf1d39` |
| [tests/test_capture_help.py](../tests/test_capture_help.py) | `0d8814b9ea08fe0958090c8790ead6fd6894b9b9a336b6a85767d8526d585730` |

The checker covers Markdown links/fences, basic skill metadata, authoring placeholders, package boundaries, and optional Bash syntax. The test suite also checks each published folder after copying it alone. The capture helper preserves version/help streams, status, timing, and failure evidence in a fresh directory; it does not prove scanner behavior.

## Adapted approach

[GETTING_STARTED.md](../GETTING_STARTED.md), [AGENTS.md](../AGENTS.md), [the schema](../authoring/schema.md), and [creation prompt](../authoring/create-skill.prompt.md) adapt the source repository's independent packaging, progressive disclosure, activation contract, source-to-task review, and evidence distinctions to static analysis. The new schema is SAST v0.1, derived from tool schema v0.8.

The catalogue, source records, evaluation cases, seven tool packages, and small Semgrep rule/test pair were written for this repository. No research-library tool package was copied. No assessment methodologies, source PDFs, historical intake queues, machine profile settings, credentials, scan reports, or scanner binaries were imported. The new repository does not inherit the original Git history or remote.
