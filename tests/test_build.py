import importlib.util
from pathlib import Path
import shutil
import tempfile
import unittest
import io
import zipfile

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("bundle_build", REPO / "scripts/build.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class BuildTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        for name in ["skills", "docs"]:
            shutil.copytree(REPO / name, self.root / name)
        shutil.copyfile(REPO / "VERSION", self.root / "VERSION")

    def tearDown(self):
        self.temp.cleanup()

    def test_repeatable_and_both_routes_contain_same_source(self):
        first = module.render(self.root)
        self.assertEqual(first, module.render(self.root))
        self.assertEqual(first["B-DSH版.zip"], first["dist/paper-repro-pipeline.zip"])
        self.assertEqual(first["C-通用平台版.zip"], first["dist/universal.zip"])
        with zipfile.ZipFile(io.BytesIO(first["dist/paper-repro-pipeline.zip"])) as z:
            self.assertIsNone(z.testzip())
            for name, data in module.source_files(self.root).items():
                self.assertEqual(z.read("paper-repro-pipeline/" + name), data)
        book = first["dist/universal/论文复现工作流-通用手册.md"].decode("utf-8")
        for name in module.RESOURCE_ORDER:
            self.assertTrue((self.root / module.SKILL_PATH / name).read_text(encoding="utf-8").strip() in book, name)

    def test_source_change_invalidates_artifacts_and_updates_both_routes(self):
        module.build(self.root)
        resource = self.root / module.SKILL_PATH / "references/workflow.md"
        resource.write_text(resource.read_text(encoding="utf-8") + "\nUnique regression evidence.\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "out of date"):
            module.build(self.root, check=True)
        module.build(self.root)
        module.build(self.root, check=True)
        with zipfile.ZipFile(self.root / "dist/paper-repro-pipeline.zip") as z:
            self.assertIn(b"Unique regression evidence.", z.read("paper-repro-pipeline/references/workflow.md"))
        self.assertIn("Unique regression evidence.", (self.root / "dist/universal/论文复现工作流-通用手册.md").read_text(encoding="utf-8"))

    def test_missing_reference_rejects_build(self):
        (self.root / module.SKILL_PATH / "references/research-pitfall-checklist.md").unlink()
        with self.assertRaisesRegex(ValueError, "missing"):
            module.render(self.root)

    def test_link_outside_skill_rejects_build(self):
        source = self.root / module.SKILL_PATH / "SKILL.md"
        source.write_text(source.read_text(encoding="utf-8") + "\n[bad](../../VERSION)\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Invalid packaged resource"):
            module.render(self.root)


if __name__ == "__main__":
    unittest.main()
