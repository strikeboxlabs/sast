# Maintaining sast

- Start with `GETTING_STARTED.md`, `authoring/schema.md`, and `authoring/create-skill.prompt.md`. This repository authors skills for CLI static analysis of supplied source and configuration.
- Package each tool as `skills/<tool>/SKILL.md`. Keep all required resources inside that folder. Runtime guidance must not depend on another skill, repository-wide helpers, or research-library.
- Write for competent CLI workers: tool selection, supported task, meaningful commands, interpretation, recovery, and completion evidence. Keep entrypoints small and move substantial conditional work into linked references.
- Put the instruction to read the entire entrypoint before acting near the top. Identify required inputs and task-specific references. Review the first 150 lines for discoverability, then review the full selected workflow; 150 is an authoring check, not a harness limit.
- Verify consequential options and conclusions against primary documentation or the installed tool. Account for the analyzed language, engine, rules, extraction/build settings, skipped inputs, and errors. Never infer a clean scan from exit status alone.
- Keep source review dates, tool decisions, and full source trails under `docs/`. Separate documentation review, syntax checks, real scanner execution, and worker outcomes. Do not invent runtime results or target-image paths.
- Target the user's controlled Linux image. A later on-image pass may enrich skill-local references with verified shared paths, versions, and relevant option facts. Raw/private input belongs in ignored `work/`; raw scan output belongs in ignored `runs/`.
- Keep work within the requested local source review. Scanner installation, application builds, remote validation of secrets, report uploads, source changes, and CI policy changes have their own effects; document those effects where relevant and use existing task authorization.
- During source intake, reconcile the whole affected workflow instead of appending overlapping snippets. Preserve useful prior guidance. Record actually reviewed packages and concrete deferred gaps in `docs/source-review.md`.
- Update the README catalogue for accepted skills. Run `python3 -B scripts/check_repository.py`, `python3 -B -m unittest discover -s tests -v`, and `git diff --check` after packaging changes. Test changed scanner behavior on the controlled image when available.
- Do not copy unrelated assessment methodologies, historical scan output, credentials, or machine settings from another repository. Skill installation does not install tools.
