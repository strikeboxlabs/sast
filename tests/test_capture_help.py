"""Exercise capture evidence and failure reporting with real subprocesses."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "capture_help.py"


class CaptureTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="cli-skills-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def run_capture(self, *extra, tool=None, output=None):
        target = output or self.root / "capture with spaces"
        result = subprocess.run(
            [sys.executable, str(SCRIPT), tool or sys.executable, "--output", str(target), *extra],
            capture_output=True, text=True, timeout=15,
        )
        return result, target

    def test_real_help_and_version_are_retained(self):
        result, target = self.run_capture("--environment-id", "test-only")
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads((target / "capture.json").read_text(encoding="utf-8"))
        self.assertTrue(report["capture_complete"])
        self.assertEqual(report["environment_id_supplied"], "test-only")
        self.assertIn(b"Python", (target / "version.stdout.txt").read_bytes())
        self.assertGreater((target / "help.stdout.txt").stat().st_size, 0)
        self.assertEqual(report["commands"]["help"]["exit_code"], 0)

    def test_exit_failure_and_separate_streams_are_preserved(self):
        code = "import sys; print('partial output'); print('failure details', file=sys.stderr); sys.exit(7)"
        result, target = self.run_capture("--help-arg=-c", "--help-arg=" + code)
        self.assertEqual(result.returncode, 1)
        report = json.loads((target / "capture.json").read_text(encoding="utf-8"))
        self.assertFalse(report["capture_complete"])
        self.assertEqual(report["commands"]["help"]["exit_code"], 7)
        self.assertIn(b"partial output", (target / "help.stdout.txt").read_bytes())
        self.assertIn(b"failure details", (target / "help.stderr.txt").read_bytes())

    def test_timeout_is_incomplete_and_retains_partial_output(self):
        code = "import time; print('before timeout', flush=True); time.sleep(10)"
        result, target = self.run_capture("--timeout", "0.5", "--help-arg=-c", "--help-arg=" + code)
        self.assertEqual(result.returncode, 1)
        report = json.loads((target / "capture.json").read_text(encoding="utf-8"))
        self.assertTrue(report["commands"]["help"]["timed_out"])
        self.assertFalse(report["capture_complete"])
        self.assertIn(b"before timeout", (target / "help.stdout.txt").read_bytes())

    def test_missing_tool_records_failure(self):
        result, target = self.run_capture(tool=str(self.root / "missing-executable"))
        self.assertEqual(result.returncode, 1)
        report = json.loads((target / "capture.json").read_text(encoding="utf-8"))
        self.assertIsNone(report["resolved_executable"])
        self.assertFalse(report["capture_complete"])
        self.assertIsNotNone(report["commands"]["version"]["error"])

    def test_existing_capture_is_never_overwritten(self):
        result, target = self.run_capture()
        self.assertEqual(result.returncode, 0, result.stderr)
        original = {path.name: path.read_bytes() for path in target.iterdir()}
        second, _ = self.run_capture(output=target)
        self.assertNotEqual(second.returncode, 0)
        self.assertEqual(original, {path.name: path.read_bytes() for path in target.iterdir()})

    def test_invalid_timeout_creates_no_capture(self):
        for value in ("0", "-1", "nan", "inf"):
            with self.subTest(timeout=value):
                result, target = self.run_capture("--timeout=" + value)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(target.exists())


if __name__ == "__main__":
    unittest.main()
