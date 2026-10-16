"""Exercise reconciliation with synthetic reports and inert local source files."""

import copy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "skills/semgrep/scripts/reconcile_triage.py"


class SemgrepTriageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / "source"
        self.root.mkdir()
        self.source = self.root / "sample.cs"
        self.source.write_text("// Café: an inert fixture\nfirst();\nsecond();\n", encoding="utf-8")
        self.control = self.root / "configuration.cs"
        self.control.write_text("// Separate policy evidence\nsetting = false;\n", encoding="utf-8")
        self.report = self.base / "scan.json"
        self.match = {"check_id": "test.audit.example", "path": "sample.cs",
                      "start": {"line": 2, "col": 1, "offset": 29},
                      "end": {"line": 2, "col": 8, "offset": 36}}
        self.write(self.report, {"results": [self.match], "errors": []})
        self.ledger = self.base / "triage.json"

    def write(self, path, value):
        path.write_text(json.dumps(value), encoding="utf-8")

    def read(self):
        return json.loads(self.ledger.read_text(encoding="utf-8"))

    def run_cli(self, *extra, script=SCRIPT, reports=None):
        args = [sys.executable, "-B", str(script), "--source-root", str(self.root),
                "--ledger", str(self.ledger)]
        for report in reports or [self.report]:
            args += ["--report", str(report)]
        return subprocess.run(args + list(extra), capture_output=True, text=True)

    def init(self):
        proc = self.run_cli("--init")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return self.read()

    def fail_ledger(self, ledger, message):
        self.write(self.ledger, ledger)
        proc = self.run_cli()
        self.assertEqual(proc.returncode, 2, proc.stdout)
        self.assertIn(message, proc.stderr)

    def resolve(self, ledger, disposition="rejected"):
        row = ledger["entries"][0]
        row.update(disposition=disposition, reason="Reviewed policy at the operation",
                   evidence=[{"path": "configuration.cs", "line": 1, "end_line": 2,
                              "sha256": hashlib.sha256(self.control.read_bytes()).hexdigest(),
                              "note": "Policy construction evidence"}], unresolved_questions=[])
        return ledger

    def test_init_and_partial_review_have_bounded_counts_without_snippets(self):
        ledger = self.init()
        self.assertEqual(ledger["version"], 1)
        self.assertEqual(len(ledger["entries"]), 1)
        self.assertEqual(ledger["entries"][0]["path"], str(self.source.resolve()))
        self.assertNotIn("first();", self.ledger.read_text())
        proc = self.run_cli()
        self.assertEqual(proc.returncode, 0, proc.stderr)
        counts = json.loads(proc.stdout)
        self.assertEqual({k: counts[k] for k in ("raw_matches", "unique_matches", "unresolved")},
                         {"raw_matches": 1, "unique_matches": 1, "unresolved": 1})
        self.assertIn("no security assurance", counts["meaning"])

    def test_absolute_and_relative_matches_share_identity_but_keep_raw_counts(self):
        second = self.base / "other.json"
        absolute = {**self.match, "path": str(self.source)}
        self.write(second, {"results": [absolute, self.match], "errors": [{"type": "PartialParsing"}]})
        proc = self.run_cli("--init", reports=[self.report, second])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        summary = json.loads(proc.stdout)
        self.assertEqual(summary["raw_matches"], 3)
        self.assertEqual(summary["unique_matches"], 1)
        self.assertEqual(summary["scan_diagnostics"], 1)
        self.assertEqual(len(self.read()["entries"]), 1)

    def test_match_end_is_part_of_identity(self):
        other = copy.deepcopy(self.match)
        other["end"]["col"] = 7
        self.write(self.report, {"results": [self.match, other]})
        self.init()
        self.assertEqual(len(self.read()["entries"]), 2)

    def test_init_never_overwrites_existing_ledger(self):
        self.init()
        original = self.ledger.read_bytes()
        proc = self.run_cli("--init")
        self.assertEqual(proc.returncode, 2)
        self.assertEqual(self.ledger.read_bytes(), original)

    def test_missing_duplicate_unknown_and_changed_identity_are_rejected(self):
        original = self.init()
        cases = [([], "missing ledger"),
                 (original["entries"] * 2, "duplicate ledger"),
                 ([{**original["entries"][0], "id": "unknown"}], "unknown ledger"),
                 ([{**original["entries"][0], "rule_id": "another.rule"}], "rule_id changed")]
        for entries, message in cases:
            with self.subTest(message=message):
                self.fail_ledger({**original, "entries": entries}, message)

    def test_confirmed_and_rejected_need_current_source_evidence(self):
        original = self.init()
        for disposition in ("confirmed", "rejected"):
            ledger = self.resolve(copy.deepcopy(original), disposition)
            self.write(self.ledger, ledger)
            proc = self.run_cli()
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(json.loads(proc.stdout)[disposition], 1)

    def test_unresolved_assumptions_cannot_coexist_with_resolved_disposition(self):
        ledger = self.resolve(self.init())
        ledger["entries"][0]["unresolved_questions"] = ["Is this the configured handler?"]
        self.fail_ledger(ledger, "open questions require unresolved")

    def test_resolved_rows_need_nonblank_reason_and_evidence(self):
        original = self.resolve(self.init())
        for changes, message in [({"reason": " "}, "reason must be nonblank"),
                                 ({"evidence": []}, "needs source evidence")]:
            ledger = copy.deepcopy(original)
            ledger["entries"][0].update(changes)
            self.fail_ledger(ledger, message)

    def test_evidence_requires_file_in_range_and_correct_digest(self):
        original = self.resolve(self.init())
        cases = [({"path": "missing.cs"}, "source file does not exist"),
                 ({"line": 30, "end_line": 31}, "beyond source file"),
                 ({"line": 2, "end_line": 1}, "positive line range"),
                 ({"sha256": "stale"}, "evidence digest changed or missing"),
                 ({"path": str(self.base / "outside.cs")}, "outside source root")]
        for changes, message in cases:
            ledger = copy.deepcopy(original)
            ledger["entries"][0]["evidence"][0].update(changes)
            with self.subTest(changes=changes):
                self.fail_ledger(ledger, message)

    def test_source_edit_invalidates_a_disposition(self):
        ledger = self.resolve(self.init())
        self.source.write_text("// changed\nfirst();\nsecond();\n", encoding="utf-8")
        self.fail_ledger(ledger, "source_sha256 changed")

    def test_mitigation_edit_invalidates_a_disposition(self):
        ledger = self.resolve(self.init())
        self.control.write_text("// Changed policy\nsetting = true;\n", encoding="utf-8")
        self.fail_ledger(ledger, "evidence digest changed")

    def test_report_edit_invalidates_even_an_unchanged_match(self):
        ledger = self.init()
        self.write(self.report, {"results": [self.match], "errors": [], "changed": True})
        self.fail_ledger(ledger, "report paths/digests changed")

    def test_malformed_ledger_types_are_reported(self):
        original = self.init()
        cases = [({**original, "version": True}, "version must be 1"),
                 ({**original, "entries": {}}, "entries must be a list"),
                 ({**original, "entries": [None]}, "entry must be an object")]
        for ledger, message in cases:
            self.fail_ledger(ledger, message)
        for changes, message in [({"disposition": []}, "invalid disposition"),
                                 ({"unresolved_questions": [""]}, "nonblank strings"),
                                 ({"evidence": {}}, "evidence must be a list"),
                                 ({"start": {"line": True, "col": 1}}, "positive integers")]:
            ledger = copy.deepcopy(original)
            ledger["entries"][0].update(changes)
            self.fail_ledger(ledger, message)

    def test_malformed_reports_fail_without_creating_a_ledger(self):
        for report, message in [({"results": {}}, "results must be a list"),
                                ({"results": [], "errors": {}}, "errors must be a list"),
                                ({"results": [None]}, "result must be an object"),
                                ({"results": [{**self.match, "start": {"line": 0, "col": 1}}]},
                                 "positive integers")]:
            self.write(self.report, report)
            proc = self.run_cli("--init")
            self.assertEqual(proc.returncode, 2)
            self.assertIn(message, proc.stderr)
            self.assertFalse(self.ledger.exists())

    def test_empty_report_and_diagnostics_are_not_security_assurance(self):
        self.write(self.report, {"results": [], "errors": [{"type": "PartialParsing"}]})
        self.init()
        summary = json.loads(self.run_cli().stdout)
        self.assertEqual(summary["unique_matches"], 0)
        self.assertEqual(summary["scan_diagnostics"], 1)
        self.assertIn("no security assurance", summary["meaning"])

    def test_standalone_package_has_no_repository_dependency(self):
        isolated = self.base / "standalone-semgrep"
        shutil.copytree(SCRIPT.parents[1], isolated)
        proc = self.run_cli("--init", script=isolated / "scripts/reconcile_triage.py")
        self.assertEqual(proc.returncode, 0, proc.stderr)


if __name__ == "__main__":
    unittest.main()
