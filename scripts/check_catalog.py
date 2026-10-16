#!/usr/bin/env python3
"""Validate an optional library catalogue using only the Python standard library."""

import argparse
import json
from pathlib import Path
import re


IDENTIFIER = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
TAG = re.compile(r"(task|execution|target|language|artifact):[a-z0-9]+(?:-[a-z0-9]+)*\Z")
UNREVIEWED = "classification:unreviewed"


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def check_catalog(root):
    root = Path(root).resolve()
    catalog_path = root / "catalog.json"
    report = {"catalog_present": catalog_path.exists(), "catalog_entries": 0,
              "catalog_unreviewed": 0, "errors": []}
    errors = report["errors"]
    if not report["catalog_present"]:
        return report
    try:
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"),
                             object_pairs_hook=unique_object)
    except (OSError, UnicodeError, ValueError) as error:
        errors.append(f"catalog.json: cannot read catalogue: {error}")
        return report
    if not isinstance(catalog, dict):
        errors.append("catalog.json: expected an object")
        return report
    if set(catalog) != {"schema_version", "library_id", "skills"}:
        errors.append("catalog.json: expected schema_version, library_id and skills only")
    if type(catalog.get("schema_version")) is not int or catalog["schema_version"] != 1:
        errors.append("catalog.json: schema_version must be 1")
    library_id = catalog.get("library_id")
    if not isinstance(library_id, str) or not IDENTIFIER.fullmatch(library_id):
        errors.append("catalog.json: invalid library_id")
    entries = catalog.get("skills")
    if not isinstance(entries, list):
        errors.append("catalog.json: skills must be a list")
        return report

    seen = set()
    for position, entry in enumerate(entries):
        label = f"catalog.json skills[{position}]"
        if not isinstance(entry, dict):
            errors.append(f"{label}: expected an object")
            continue
        if set(entry) != {"id", "path", "tags", "requires"}:
            errors.append(f"{label}: expected id, path, tags and requires only")
        skill_id = entry.get("id")
        if (not isinstance(skill_id, str) or not IDENTIFIER.fullmatch(skill_id)
                or len(skill_id) > 64):
            errors.append(f"{label}: invalid skill id")
            continue
        if skill_id in seen:
            errors.append(f"{label}: duplicate skill id {skill_id}")
        seen.add(skill_id)
        expected_path = f"skills/{skill_id}"
        if entry.get("path") != expected_path:
            errors.append(f"{label}: path must be {expected_path}")
        else:
            directory = root / expected_path
            entrypoint = directory / "SKILL.md"
            if (not directory.resolve().is_relative_to(root)
                    or not entrypoint.resolve().is_relative_to(directory.resolve())):
                errors.append(f"{label}: skill path escapes its package or library")
            elif not entrypoint.is_file():
                errors.append(f"{label}: missing {expected_path}/SKILL.md")
            else:
                try:
                    text = entrypoint.read_text(encoding="utf-8")
                    header = re.match(r"\A---\n(.*?)\n---(?:\n|$)", text, re.S)
                    names = [] if not header else re.findall(
                        r"^name:\s*([^\n]+)$", header.group(1), re.M)
                    if len(names) != 1 or names[0].strip().strip("\"'") != skill_id:
                        errors.append(f"{label}: id does not match SKILL.md name")
                except (OSError, UnicodeError) as error:
                    errors.append(f"{label}: cannot read SKILL.md: {error}")

        tags = entry.get("tags")
        if not isinstance(tags, list) or any(not isinstance(tag, str) for tag in tags):
            errors.append(f"{label}: tags must be a list of strings")
        else:
            if len(tags) != len(set(tags)):
                errors.append(f"{label}: duplicate tags")
            if any(tag != UNREVIEWED and not TAG.fullmatch(tag) for tag in tags):
                errors.append(f"{label}: unsupported tag facet or value")
            if UNREVIEWED in tags:
                report["catalog_unreviewed"] += 1
                if "execution:linux" not in tags:
                    errors.append(f"{label}: unreviewed classification needs execution:linux")
                if any(tag.startswith("task:") for tag in tags):
                    errors.append(f"{label}: unreviewed classification cannot claim task tags")
        requirements = entry.get("requires")
        if (not isinstance(requirements, list)
                or any(not isinstance(value, str) or not value.strip()
                       or value != value.strip() for value in requirements)):
            errors.append(f"{label}: requires must be a list of nonempty trimmed strings")
        elif len(requirements) != len(set(requirements)):
            errors.append(f"{label}: duplicate requirements")

    physical = {path.parent.name for path in (root / "skills").glob("*/SKILL.md")}
    for skill_id in sorted(physical - seen):
        errors.append(f"catalog.json: missing physical skill {skill_id}")
    for skill_id in sorted(seen - physical):
        errors.append(f"catalog.json: unknown physical skill {skill_id}")
    report["catalog_entries"] = len(entries)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    result = check_catalog(args.root)
    print(json.dumps(result, indent=2))
    return int(bool(result["errors"]))


if __name__ == "__main__":
    raise SystemExit(main())
