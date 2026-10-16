import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_catalog.py"
SPEC = importlib.util.spec_from_file_location("check_catalog", SCRIPT)
CHECKER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECKER)


class CatalogChecks(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="skill-catalog-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.add_skill("example")
        self.catalog = {"schema_version": 1, "library_id": "example-library", "skills": [
            {"id": "example", "path": "skills/example", "tags": ["task:source-review", "execution:linux"],
             "requires": []}]}

    def add_skill(self, name):
        directory = self.root / "skills" / name
        directory.mkdir(parents=True)
        (directory / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: Inspect a local fixture.\n---\n", encoding="utf-8")
        return directory

    def check(self):
        (self.root / "catalog.json").write_text(json.dumps(self.catalog), encoding="utf-8")
        return CHECKER.check_catalog(self.root)

    def test_catalog_is_optional_for_standalone_package_copies(self):
        result = CHECKER.check_catalog(self.root)
        self.assertFalse(result["catalog_present"])
        self.assertEqual(result["errors"], [])

    def test_valid_complete_catalog(self):
        result = self.check()
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["catalog_entries"], 1)

    def test_unreviewed_entries_are_explicit(self):
        self.catalog["skills"][0]["tags"] = ["execution:linux", "classification:unreviewed"]
        result = self.check()
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["catalog_unreviewed"], 1)
        self.catalog["skills"][0]["tags"].append("task:source-review")
        self.assertTrue(any("cannot claim task" in error for error in self.check()["errors"]))

    def test_missing_and_unknown_skills_are_reported(self):
        self.add_skill("other")
        self.assertTrue(any("missing physical skill other" in error for error in self.check()["errors"]))
        self.catalog["skills"][0].update(id="absent", path="skills/absent")
        self.assertTrue(any("unknown physical skill absent" in error for error in self.check()["errors"]))

    def test_duplicate_ids_tags_and_requirements_are_rejected(self):
        self.catalog["skills"].append(dict(self.catalog["skills"][0]))
        self.catalog["skills"][0]["tags"] = ["execution:linux", "execution:linux"]
        self.catalog["skills"][0]["requires"] = ["runtime", "runtime"]
        errors = self.check()["errors"]
        for expected in ("duplicate skill id", "duplicate tags", "duplicate requirements"):
            self.assertTrue(any(expected in error for error in errors), expected)

    def test_paths_cannot_use_traversal_absolute_paths_or_wrong_folders(self):
        for path in ("../example", "/skills/example", "C:/skills/example", "skills/other"):
            with self.subTest(path=path):
                self.catalog["skills"][0]["path"] = path
                self.assertTrue(any("path must be" in error for error in self.check()["errors"]))

    def test_symlink_outside_library_is_rejected(self):
        with tempfile.TemporaryDirectory(prefix="skill-outside-") as other:
            destination = Path(other) / "external"
            destination.mkdir()
            (destination / "SKILL.md").write_text("---\nname: external\n---\n", encoding="utf-8")
            try:
                (self.root / "skills" / "external").symlink_to(destination, target_is_directory=True)
            except (OSError, NotImplementedError) as error:
                self.skipTest(f"symlinks unavailable: {error}")
            self.catalog["skills"].append({"id": "external", "path": "skills/external", "tags": [], "requires": []})
            self.assertTrue(any("escapes" in error for error in self.check()["errors"]))

    def test_id_must_match_entrypoint_name(self):
        (self.root / "skills" / "example" / "SKILL.md").write_text(
            "---\nname: different\ndescription: Example.\n---\n", encoding="utf-8")
        self.assertTrue(any("does not match" in error for error in self.check()["errors"]))

    def test_invalid_schema_fields_and_types_are_rejected(self):
        self.catalog["schema_version"] = True
        self.catalog["description"] = "not duplicated discovery text"
        self.catalog["skills"][0]["tags"] = ["unsupported:example"]
        self.catalog["skills"][0]["requires"] = [""]
        errors = self.check()["errors"]
        for expected in ("schema_version must", "expected schema_version", "unsupported tag", "nonempty trimmed"):
            self.assertTrue(any(expected in error for error in errors), expected)

    def test_duplicate_json_keys_and_malformed_json_are_rejected(self):
        for text in ('{"schema_version":1,"schema_version":1}', '{"skills":'):
            with self.subTest(text=text):
                (self.root / "catalog.json").write_text(text, encoding="utf-8")
                self.assertTrue(CHECKER.check_catalog(self.root)["errors"])

    def test_published_catalog_matches_current_packages(self):
        result = CHECKER.check_catalog(SCRIPT.parents[1])
        self.assertTrue(result["catalog_present"])
        self.assertEqual(result["errors"], [])


if __name__ == "__main__":
    unittest.main()
