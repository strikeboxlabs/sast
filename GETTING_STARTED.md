# Start using sast

For selective Board/Pi loading, use the optional [skill catalogue](docs/catalog.md). Packages remain independently installable; category views do not require moving folders.

Use a normal checkout of [strikeboxlabs/sast](https://github.com/strikeboxlabs/sast) for authoring. Clone it onto the Linux image you control before executing the Linux scanner examples.

```bash
git clone https://github.com/strikeboxlabs/sast.git
cd sast
```

## Choose and install one skill

Select a tool from the [catalogue](README.md#tool-skills). The complete folder under `skills/` is the installable unit; repository authoring files are not worker dependencies. Copy the whole selected folder to your harness's skill directory, or link it from a checkout that remains available to that harness.

For a harness that discovers `~/.agents/skills`, run this from the repository root on Linux. Existing destinations are preserved:

```bash
(
  set -eu
  repo=$(pwd -P)
  skill=semgrep
  test -f "$repo/skills/$skill/SKILL.md"
  parent="$HOME/.agents/skills"
  destination="$parent/$skill"
  mkdir -p "$parent"
  if [ -e "$destination" ] || [ -L "$destination" ]; then
    printf 'Already exists; inspect: %s\n' "$destination"
  else
    ln -s "$repo/skills/$skill" "$destination"
  fi
)
```

Use your harness's documented destination if it differs. Start a fresh session and invoke the chosen skill explicitly once to verify the loaded path. Run workers in the source repository being reviewed. Do not install this repository's maintenance `AGENTS.md` as a global worker instruction.

The scanner must already be available. Follow its official installation documentation separately if needed. CodeQL also has licensing and extraction prerequisites; Semgrep engine features depend on the selected edition. No account, upload, or cloud service is needed for the local examples except network retrieval of rules, packs, or vulnerability data where stated.

## Adapt to the controlled Linux image

The Windows authoring host does not establish Linux paths or scanner behavior. On the actual image, inspect the executable, version, supported options, and relevant dependency/build environment. Record reusable image facts inside the selected skill's existing reference, or add `references/environment.md` and link it near the opening. Keep node-specific details in ignored `work/`.

The reused capture helper saves version/help output without claiming a scan was performed. From the repository root, choose a fresh output directory:

```bash
capture_id=$(date -u '+%Y%m%dT%H%M%SZ')
python3 scripts/capture_help.py semgrep --output "work/semgrep/$capture_id"
```

For commands whose version syntax differs:

```bash
capture_id=$(date -u '+%Y%m%dT%H%M%SZ')
python3 scripts/capture_help.py codeql --version-arg=version \
  --output "work/codeql/$capture_id"
python3 scripts/capture_help.py gosec --version-arg=-version --help-arg=-help \
  --output "work/gosec/$capture_id"
```

Inspect `capture.json`, exit statuses, and both streams. A capture records help/version calls only. Use the [evaluation cases](evaluation/README.md) for later workflow validation and document actual outcomes in [validation](docs/validation.md).

## Author and check

Python 3.10+ runs the repository helpers and standard-library tests. Bash is optional for syntax checking; neither check executes scanner examples.

```bash
python3 -B scripts/check_repository.py
python3 -B -m unittest discover -s tests -v
git diff --check
git status --short
```

On Windows use `python` in place of `python3`. `--bash /path/to/bash` selects a syntax parser explicitly. The checker validates local links, basic frontmatter, placeholders, fences, and skill boundaries; it is not a semantic scanner validator or a full YAML parser. The tests include copying each skill alone before checking it.

Follow [the schema](authoring/schema.md) and [creation prompt](authoring/create-skill.prompt.md) for additions. Store raw sources in `work/`, scan output in `runs/`, portable source-to-task notes in `docs/`, and installable content in `skills/`. Review new files as well as ordinary Git diffs before committing or publishing.
