"""Exercise only the output-directory setup from documented examples, never scanners."""
from pathlib import Path
import os
import re
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
BASH = os.environ.get("CATALOG_TEST_BASH") or shutil.which("bash")


@unittest.skipUnless(BASH, "Bash is required to execute the directory-only fixture")
class OutputDirectoryChecks(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="scan-evidence-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def prefix(self, entrypoint):
        blocks = re.findall(r"```bash\n(.*?)```", entrypoint.read_text(encoding="utf-8"), re.S)
        for block in blocks:
            lines = block.splitlines()
            for index, line in enumerate(lines):
                if line.startswith("out=$(mktemp "):
                    return "\n".join(lines[:index + 1])
        self.fail(f"No output setup found in {entrypoint}")

    def run_setup(self, entrypoint, evidence, standalone):
        environment = dict(os.environ)
        environment["TMPDIR"] = standalone.as_posix()
        environment.pop("BOARD_EVIDENCE_DIR", None)
        if evidence is not None:
            environment["BOARD_EVIDENCE_DIR"] = evidence.as_posix()
        # The prefix ends at mktemp, before the first scanner/version invocation.
        # Git Bash rewrites inherited TMPDIR at startup; set it inside the shell
        # so this tests the documented Linux variable contract on either host.
        script = 'TMPDIR=$1\nexport TMPDIR\n' + self.prefix(entrypoint) + '\nprintf "fixture\\n" > "$out/report.txt"\nprintf "%s\\n" "$out"\n'
        return subprocess.run([BASH, "--noprofile", "--norc", "-c", script, "--", standalone.as_posix()],
                              env=environment, text=True, capture_output=True, timeout=15)

    def test_every_scanner_prefers_board_evidence_and_retains_standalone_fallback(self):
        for entrypoint in sorted((ROOT / "skills").glob("*/SKILL.md")):
            for board in (True, False):
                with self.subTest(skill=entrypoint.parent.name, board=board):
                    evidence = self.root / "Board Evidence" if board else None
                    standalone = self.root / "Standalone Temp"
                    result = self.run_setup(entrypoint, evidence, standalone)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    output = Path(result.stdout.strip()).resolve()
                    self.assertEqual(output.parent, (evidence or standalone).resolve())
                    self.assertEqual((output / "report.txt").read_text(), "fixture\n")

    def test_unusable_board_directory_does_not_fall_back(self):
        blocked = self.root / "blocked"
        blocked.write_text("ordinary file", encoding="utf-8")
        standalone = self.root / "unused-fallback"
        for entrypoint in sorted((ROOT / "skills").glob("*/SKILL.md")):
            with self.subTest(skill=entrypoint.parent.name):
                result = self.run_setup(entrypoint, blocked, standalone)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(standalone.exists())


if __name__ == "__main__":
    unittest.main()
