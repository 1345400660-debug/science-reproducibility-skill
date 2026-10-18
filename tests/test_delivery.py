import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import warnings
import zipfile

SCRIPT = Path(__file__).resolve().parents[1] / "skills/paper-repro-pipeline/scripts/verify_delivery.py"
spec = importlib.util.spec_from_file_location("delivery_check", SCRIPT)
module = importlib.util.module_from_spec(spec)
# Loading the packaged script must not add a __pycache__ resource to the skill.
exec(compile(SCRIPT.read_text(encoding="utf-8"), str(SCRIPT), "exec"), module.__dict__)


class DeliveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.source = self.root / "stage"
        self.source.mkdir()
        self.data = {"README.md": b"instructions", "report.md": b"result=1", "figure.svg": b"<svg>new</svg>"}
        for name, data in self.data.items():
            (self.source / name).write_bytes(data)
        self.archive = self.root / "delivery.zip"

    def tearDown(self):
        self.temp.cleanup()

    def pack(self, files=None, prefix="delivery/"):
        with zipfile.ZipFile(self.archive, "w") as z:
            for name, data in (self.data if files is None else files).items():
                z.writestr(prefix + name, data)

    def verify(self, prefix="delivery"):
        return module.verify(self.source, self.archive, prefix, ["README.md", "report.md"])

    def test_matching_package_and_flat_layout(self):
        self.pack()
        self.assertEqual([], self.verify())
        self.pack(prefix="")
        self.assertEqual([], self.verify(""))

    def test_missing_report_fails_even_when_missing_on_both_sides(self):
        (self.source / "report.md").unlink()
        self.pack({k: v for k, v in self.data.items() if k != "report.md"})
        self.assertTrue(any("Required source file missing" in e for e in self.verify()))

    def test_stale_figure_with_valid_crc_is_rejected(self):
        self.pack({**self.data, "figure.svg": b"<svg>old</svg>"})
        with zipfile.ZipFile(self.archive) as z:
            self.assertIsNone(z.testzip())
        self.assertIn("Content mismatch: figure.svg", self.verify())

    def test_missing_and_extra_archive_files(self):
        self.pack({"README.md": b"instructions", "extra.txt": b"old"})
        errors = self.verify()
        self.assertIn("Archive file missing: report.md", errors)
        self.assertIn("Unexpected archive file: extra.txt", errors)

    def test_duplicate_and_unsafe_paths(self):
        self.pack()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            with zipfile.ZipFile(self.archive, "a") as z:
                z.writestr("delivery/report.md", b"duplicate")
                z.writestr("../outside.txt", b"bad")
        errors = self.verify()
        self.assertTrue(any("Duplicate" in e for e in errors))
        self.assertTrue(any("Unsafe" in e for e in errors))
        self.assertFalse((self.root / "outside.txt").exists())

    def test_cli_success_and_corrupt_archive_failure(self):
        self.pack()
        command = [sys.executable, str(SCRIPT), "--source", str(self.source),
                   "--archive", str(self.archive), "--prefix", "delivery",
                   "--required", "report.md"]
        self.assertEqual(0, subprocess.run(command, capture_output=True).returncode)
        self.archive.write_bytes(b"not a zip")
        result = subprocess.run(command, capture_output=True)
        self.assertEqual(1, result.returncode)
        self.assertIn(b"FAIL", result.stdout)


if __name__ == "__main__":
    unittest.main()
