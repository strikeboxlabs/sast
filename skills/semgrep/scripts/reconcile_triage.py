#!/usr/bin/env python3
"""Reconcile retained Semgrep matches with source-backed review dispositions.

This checks accounting and evidence freshness, not security judgments. It reads
local files only and never executes source or contacts a service.
"""

import argparse
import hashlib
import json
from pathlib import Path
import sys


def require(condition, message):
    if not condition:
        raise ValueError(message)


def nonblank(value):
    return isinstance(value, str) and bool(value.strip())


def positive(value):
    return type(value) is int and value > 0


def digest(data):
    return hashlib.sha256(data).hexdigest()


def load_json(path):
    raw = path.read_bytes()
    value = json.loads(raw)
    require(isinstance(value, dict), f"{path}: expected a JSON object")
    return value, digest(raw)


def source_path(value, root):
    require(nonblank(value), "source path must be a nonempty string")
    path = Path(value)
    path = (path if path.is_absolute() else root / path).resolve()
    require(path.is_relative_to(root), f"source path is outside source root: {path}")
    return path


def source_info(path, cache):
    if path not in cache:
        require(path.is_file(), f"source file does not exist: {path}")
        data = path.read_bytes()
        cache[path] = (digest(data), len(data.splitlines()))
    return cache[path]


def position(value, label):
    require(isinstance(value, dict), f"{label}: expected line/col object")
    line, col = value.get("line"), value.get("col")
    require(positive(line) and positive(col), f"{label}: line and col must be positive integers")
    return {"line": line, "col": col}


def match_entry(result, root, cache):
    require(isinstance(result, dict), "report result must be an object")
    rule = result.get("check_id")
    require(nonblank(rule), "report result check_id must be a nonempty string")
    path = source_path(result.get("path"), root)
    start = position(result.get("start"), "report start")
    end = position(result.get("end"), "report end")
    require((start["line"], start["col"]) <= (end["line"], end["col"]),
            f"report location ends before it starts: {path}")
    sha, lines = source_info(path, cache)
    require(end["line"] <= lines, f"report location is beyond source file: {path}")
    identity = {"rule_id": rule, "path": str(path), "start": start, "end": end}
    match_id = digest(json.dumps(identity, sort_keys=True, separators=(",", ":")).encode())
    return {"id": match_id, **identity, "source_sha256": sha}


def collect(report_paths, root, cache):
    reports, matches, raw_count, diagnostics = [], {}, 0, 0
    for path in sorted({Path(p).resolve() for p in report_paths}):
        report, sha = load_json(path)
        results, errors = report.get("results"), report.get("errors", [])
        require(isinstance(results, list), f"{path}: results must be a list")
        require(isinstance(errors, list), f"{path}: errors must be a list")
        reports.append({"path": str(path), "sha256": sha})
        raw_count += len(results)
        diagnostics += len(errors)
        for result in results:
            row = match_entry(result, root, cache)
            matches[row["id"]] = row
    return reports, matches, raw_count, diagnostics


def validate_evidence(evidence, root, cache, label):
    require(isinstance(evidence, dict), f"{label}: evidence must be an object")
    path = source_path(evidence.get("path"), root)
    line = evidence.get("line")
    end = evidence.get("end_line", line)
    require(positive(line) and positive(end) and line <= end,
            f"{label}: evidence needs a positive line range")
    sha, lines = source_info(path, cache)
    require(end <= lines, f"{label}: evidence line is beyond source file: {path}")
    require(evidence.get("sha256") == sha, f"{label}: evidence digest changed or missing: {path}")
    require("note" not in evidence or isinstance(evidence["note"], str),
            f"{label}: evidence note must be a string")


def validate(ledger, root, reports, matches, cache):
    require(type(ledger.get("version")) is int and ledger["version"] == 1,
            "ledger version must be 1")
    require(ledger.get("source_root") == str(root), "ledger source_root changed")
    require(ledger.get("reports") == reports, "ledger report paths/digests changed")
    entries = ledger.get("entries")
    require(isinstance(entries, list), "ledger entries must be a list")
    seen, counts = set(), {"confirmed": 0, "rejected": 0, "unresolved": 0}
    for row in entries:
        require(isinstance(row, dict), "ledger entry must be an object")
        match_id = row.get("id")
        require(isinstance(match_id, str), "ledger entry id must be a string")
        require(match_id not in seen, f"duplicate ledger match id: {match_id}")
        require(match_id in matches, f"unknown ledger match id: {match_id}")
        seen.add(match_id)
        expected = matches[match_id]
        position(row.get("start"), "ledger start")
        position(row.get("end"), "ledger end")
        for key in ("rule_id", "path", "start", "end", "source_sha256"):
            require(row.get(key) == expected[key], f"{match_id}: {key} changed or missing")
        disposition = row.get("disposition")
        require(isinstance(disposition, str) and disposition in counts,
                f"{match_id}: invalid disposition")
        require(nonblank(row.get("reason")), f"{match_id}: reason must be nonblank")
        questions, evidence = row.get("unresolved_questions"), row.get("evidence")
        require(isinstance(questions, list) and all(nonblank(q) for q in questions),
                f"{match_id}: unresolved_questions must be a list of nonblank strings")
        require(isinstance(evidence, list), f"{match_id}: evidence must be a list")
        require(not questions or disposition == "unresolved",
                f"{match_id}: open questions require unresolved disposition")
        require(disposition == "unresolved" or bool(evidence),
                f"{match_id}: resolved disposition needs source evidence")
        for item in evidence:
            validate_evidence(item, root, cache, match_id)
        counts[disposition] += 1
    missing = set(matches) - seen
    require(not missing, f"missing ledger match ids: {', '.join(sorted(missing))}")
    return counts


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", action="append", required=True,
                        help="Retained Semgrep JSON report; repeat for multiple reports")
    parser.add_argument("--source-root", required=True)
    parser.add_argument("--ledger", required=True)
    parser.add_argument("--init", action="store_true", help="Create a new unresolved ledger; never overwrite")
    args = parser.parse_args(argv)
    try:
        root, ledger_path = Path(args.source_root).resolve(), Path(args.ledger)
        require(root.is_dir(), f"source root is not a directory: {root}")
        cache = {}
        reports, matches, raw_count, diagnostics = collect(args.report, root, cache)
        if args.init:
            entries = [{**row, "disposition": "unresolved", "reason": "Awaiting source review",
                        "evidence": [], "unresolved_questions": ["What disposition does the source support?"]}
                       for _, row in sorted(matches.items())]
            ledger = {"version": 1, "source_root": str(root), "reports": reports, "entries": entries}
            with ledger_path.open("x", encoding="utf-8") as out:
                json.dump(ledger, out, indent=2)
                out.write("\n")
        else:
            ledger, _ = load_json(ledger_path)
        counts = validate(ledger, root, reports, matches, cache)
        print(json.dumps({"raw_matches": raw_count, "unique_matches": len(matches),
                          "scan_diagnostics": diagnostics, **counts,
                          "meaning": "Match accounting and evidence freshness only; no security assurance"}))
        return 0
    except (OSError, ValueError, TypeError) as exc:
        print(f"triage reconciliation failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
