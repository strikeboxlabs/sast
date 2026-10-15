#!/usr/bin/env python3
"""Check this repository's Markdown links and portable skill packaging (Python 3.10+)."""

import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
from urllib.parse import unquote


IGNORED = {".git", "work", "runs", "__pycache__", ".venv", "node_modules"}


def markdown_parts(text):
    outside, blocks, code = [], [], []
    fence = None
    language = ""
    for line in text.splitlines():
        match = re.match(r"^\s*(`{3,}|~{3,})(.*)$", line)
        if match:
            marker, tail = match.groups()
            if fence is None:
                fence, language, code = marker, tail.strip(), []
            elif marker[0] == fence[0] and len(marker) >= len(fence) and not tail.strip():
                blocks.append((language, "\n".join(code)))
                fence = None
            else:
                code.append(line)
        elif fence:
            code.append(line)
        else:
            outside.append(line)
    return "\n".join(outside), blocks, fence is not None


def check_repository(root, bash=None):
    root = Path(root).resolve()
    errors, shell_blocks = [], []
    links = 0
    markdown_files = 0
    template_links = 0
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if any(part in IGNORED for part in relative.parts) or not path.is_file():
            continue
        if path.suffix not in {".md", ".sh"}:
            continue
        text = path.read_text(encoding="utf-8")
        if path.suffix == ".sh":
            shell_blocks.append((str(relative), text))
            continue
        markdown_files += 1
        outside, blocks, unfinished = markdown_parts(text)
        if unfinished:
            errors.append(f"Unclosed code fence: {relative}")
        shell_blocks.extend((str(relative), code) for language, code in blocks if language in {"bash", "sh"})
        skill_root = None
        if len(relative.parts) >= 3 and relative.parts[0] == "skills":
            skill_root = root / "skills" / relative.parts[1]
            # Authoring slots and real template expressions share delimiters.
            # Explicit Jinja blocks are working examples; arithmetic expressions
            # are not authoring slots. Keep named/descriptive and unclosed slots
            # checked in prose and other code, including inline shell examples.
            slot_text = outside + "\n" + "\n".join(
                code for language, code in blocks
                if language not in {"jinja", "jinja2"}
            )
            if (re.search(r"\{\{\s*[A-Za-z][^{}]*\}\}", slot_text)
                    or re.search(r"\{\{\s*[A-Za-z][^{}\n]*$", slot_text, re.M)):
                errors.append(f"Unfinished runtime placeholder: {relative}")
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", outside):
            if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target) or target.startswith("#"):
                continue
            if not skill_root and ".template." in path.name:
                # Template links resolve in the future skill folder, not authoring/.
                template_links += 1
                continue
            resolved = (path.parent / unquote(target.split("#", 1)[0].strip("<>"))).resolve()
            links += 1
            if not resolved.is_relative_to(root):
                errors.append(f"Link escapes repository: {relative} -> {target}")
            elif not resolved.exists():
                errors.append(f"Missing link: {relative} -> {target}")
            if skill_root and not resolved.is_relative_to(skill_root):
                errors.append(f"Runtime link escapes skill: {relative} -> {target}")

    skill_dirs = sorted(path for path in (root / "skills").glob("*") if path.is_dir() and path.name not in IGNORED)
    for directory in skill_dirs:
        if not (directory / "SKILL.md").is_file():
            errors.append(f"Skill folder has no SKILL.md: {directory.relative_to(root)}")
    skills = [directory / "SKILL.md" for directory in skill_dirs if (directory / "SKILL.md").is_file()]
    if not skills:
        errors.append("No skills/*/SKILL.md found")
    for path in skills:
        text = path.read_text(encoding="utf-8")
        header = re.match(r"\A---\n(.*?)\n---(?:\n|$)", text, re.S)
        if not header:
            errors.append(f"Missing frontmatter: {path.relative_to(root)}")
            continue
        fields = {}
        for line in header.group(1).splitlines():
            key, separator, value = line.partition(":")
            if separator:
                fields[key.strip()] = value.strip().strip("\"'")
        name = fields.get("name", "")
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name) or len(name) > 64 or name != path.parent.name:
            errors.append(f"Invalid or mismatched skill name: {path.relative_to(root)}")
        description = fields.get("description", "")
        if not description or len(description) > 1024 or description in {"|", ">", "|-", ">-"}:
            errors.append(f"Expected a nonempty one-line MVP description: {path.relative_to(root)}")

    parsed = 0
    if bash:
        for label, code in shell_blocks:
            result = subprocess.run([bash, "--noprofile", "--norc", "-n"], input=code, text=True, capture_output=True, timeout=10)
            parsed += 1
            if result.returncode:
                errors.append(f"Bash syntax in {label}: {result.stderr.strip()}")
    return {
        "markdown_files": markdown_files,
        "local_links_checked": links,
        "template_links_deferred": template_links,
        "skills_checked": len(skills),
        "bash_blocks_parsed": parsed,
        "bash_status": "parsed only; commands not executed" if bash else "skipped; Bash unavailable or not selected",
        "frontmatter_scope": "basic one-line name/description checks for this MVP, not a full YAML/spec validator",
        "errors": errors,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--bash", default=shutil.which("bash"), help="Bash executable for syntax-only checks; defaults to Bash on PATH")
    args = parser.parse_args()
    result = check_repository(args.root, args.bash)
    print(json.dumps(result, indent=2))
    return 1 if result["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
