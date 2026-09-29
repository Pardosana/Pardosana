import json
import os
import tempfile
import unittest
from pathlib import Path

from pavadonis.artifact_publish_v1 import JOB_TYPE, handle, rollback


class ArtifactPublishTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        base = Path(self._tmp.name)
        self.src = base / "src"
        self.dst = base / "dst"
        self.src.mkdir()
        self.dst.mkdir()
        (self.src / "deck").mkdir()
        (self.src / "deck" / "index.html").write_text("<h1>v1</h1>", encoding="utf-8")
        (self.src / "book.pdf").write_bytes(b"%PDF-1.4 test")
        (self.src / "run.exe").write_bytes(b"MZ")
        (base / "secret.txt").write_text("nē", encoding="utf-8")

    def tearDown(self):
        self._tmp.cleanup()

    def job(self, **payload):
        p = {"source_root": str(self.src), "target_root": str(self.dst),
             "name": "demo", "files": ["deck/index.html", "book.pdf"]}
        p.update(payload)
        return {"type": JOB_TYPE, "id": "t1", "payload": p}

    def test_dry_run_is_default_and_writes_nothing(self):
        r = handle(self.job())
        self.assertTrue(r["ok"], r)
        self.assertTrue(r["dry_run"])
        self.assertEqual(len(r["files"]), 2)
        self.assertEqual(list(self.dst.iterdir()), [])

    def test_publish_creates_version_and_manifest(self):
        r = handle(self.job(dry_run=False))
        self.assertTrue(r["ok"], r)
        out = Path(r["published_dir"])
        self.assertEqual((out / "deck" / "index.html").read_text(encoding="utf-8"), "<h1>v1</h1>")
        manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["job_id"], "t1")
        self.assertEqual({f["path"] for f in manifest["files"]}, {"deck/index.html", "book.pdf"})
        current = json.loads((self.dst / "demo" / "current.json").read_text(encoding="utf-8"))
        self.assertEqual(current, {"version": r["version"], "previous": None})
        self.assertFalse([p for p in (self.dst / "demo").iterdir() if p.name.startswith(".")])

    def test_rejections(self):
        cases = {
            "traversal": self.job(files=["../secret.txt"]),
            "absolute": self.job(files=[str(self.src / "book.pdf")]),
            "suffix": self.job(files=["run.exe"]),
            "missing": self.job(files=["nav.html"]),
            "dup": self.job(files=["book.pdf", "book.pdf"]),
            "empty": self.job(files=[]),
            "bad_name": self.job(name="../x"),
            "overlap": self.job(target_root=str(self.src / "deck")),
            "bad_dry": self.job(dry_run="false"),
            "wrong_type": {"type": "other", "payload": {}},
            "not_dict": None,
        }
        for label, job in cases.items():
            with self.subTest(label):
                r = handle(job)
                self.assertFalse(r["ok"])
                self.assertTrue(r["error"])
        self.assertEqual(list(self.dst.iterdir()), [])

    @unittest.skipIf(os.name == "nt", "symlinks require privileges on Windows")
    def test_symlink_rejected(self):
        (self.src / "link.txt").symlink_to(Path(self._tmp.name) / "secret.txt")
        r = handle(self.job(files=["link.txt"]))
        self.assertFalse(r["ok"])
        self.assertIn("simboliskā", r["error"])

    def test_rollback_switches_pointer_without_deleting(self):
        v1 = handle(self.job(dry_run=False))["version"]
        (self.src / "deck" / "index.html").write_text("<h1>v2</h1>", encoding="utf-8")
        v2 = handle(self.job(dry_run=False))["version"]
        self.assertNotEqual(v1, v2)
        r = rollback(str(self.dst), "demo")
        self.assertEqual(r["version"], v1)
        current = json.loads((self.dst / "demo" / "current.json").read_text(encoding="utf-8"))
        self.assertEqual(current["version"], v1)
        self.assertTrue((self.dst / "demo" / v2 / "manifest.json").is_file())


if __name__ == "__main__":
    unittest.main()
