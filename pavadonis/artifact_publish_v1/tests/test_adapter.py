"""Obligātie testi 1–7 no specifikācijas (8. tests: skat. INSTALL.md)."""

import hashlib
import os
import tempfile
import unittest
from pathlib import Path

from artifact_publish_v1 import (ArtifactPublishBlocked, ArtifactPublishConfig,
                                 ArtifactPublishV1Adapter, payload_digest)
from artifact_publish_v1.adapter import IDEMPOTENCY_KEY

FOLDER = "folderAllowed123"
PNG = b"\x89PNG\r\n\x1a\n" + b"x" * 1000


class FakeDrive:
    def __init__(self):
        self.files = {}
        self.uploads = 0
        self.corrupt_readback = False

    def find_by_app_property(self, folder_id, key, value):
        return [fid for fid, f in self.files.items()
                if folder_id in f["parents"] and f["appProperties"].get(key) == value
                and not f["trashed"]]

    def upload(self, *, data, name, folder_id, mime_type, app_properties):
        self.uploads += 1
        fid = f"file{self.uploads}"
        self.files[fid] = {"id": fid, "name": name, "size": str(len(data)),
                           "mimeType": mime_type, "parents": [folder_id], "trashed": False,
                           "sha256Checksum": hashlib.sha256(data).hexdigest(),
                           "md5Checksum": hashlib.md5(data).hexdigest(),
                           "webViewLink": f"https://drive.google.com/file/d/{fid}/view",
                           "appProperties": dict(app_properties)}
        return fid

    def get_metadata(self, file_id):
        meta = dict(self.files[file_id])
        if self.corrupt_readback:
            meta["sha256Checksum"] = "0" * 64
        return meta


class AdapterTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        base = Path(self._tmp.name).resolve()
        self.root = base / "allowed"
        self.root.mkdir()
        self.src = self.root / "Ritvars_CRM_2026-09-29.png"
        self.src.write_bytes(PNG)
        self.outside = base / "outside.png"
        self.outside.write_bytes(PNG)
        self.drive = FakeDrive()
        self.approved = set()
        cfg = ArtifactPublishConfig(allow_roots=(str(self.root),),
                                    destinations={"google_drive": (FOLDER,)})
        self.adapter = ArtifactPublishV1Adapter(
            cfg, drive_client=self.drive,
            approval_verifier=lambda digest, payload: digest in self.approved)

    def tearDown(self):
        self._tmp.cleanup()

    def payload(self, **over):
        p = {"source_path": str(self.src), "expected_sha256": hashlib.sha256(PNG).hexdigest(),
             "expected_size": len(PNG), "provider": "google_drive",
             "destination": FOLDER, "file_name": "Ritvars_CRM_2026-09-29.png"}
        p.update(over)
        return p

    def approve(self, p):
        self.approved.add(payload_digest(p))
        return p

    def assertBlocked(self, p, fragment):
        with self.assertRaises(ArtifactPublishBlocked) as ctx:
            self.adapter.execute(p)
        self.assertIn(fragment, ctx.exception.reason)
        self.assertEqual(self.drive.uploads, 0)
        return ctx.exception

    # 1
    def test_allowed_file_publishes_and_readback_matches(self):
        res = self.adapter.execute(self.approve(self.payload()))
        r = res.result
        for key in ("provider", "source_path", "sha256", "bytes", "file_id",
                    "file_name", "url", "readback", "compare"):
            self.assertIn(key, r)
        self.assertTrue(r["compare"]["match"])
        self.assertEqual(r["bytes"], len(PNG))
        self.assertEqual(res.artifacts, [{"type": "google_drive_file", "file_id": "file1",
                                          "url": r["url"], "source_sha256": r["sha256"]}])
        self.assertTrue(self.adapter.verify(r)["verified"])

    # 2
    def test_outside_allow_root_rejected(self):
        self.assertBlocked(self.approve(self.payload(source_path=str(self.outside))),
                           "allow_root")
        self.assertBlocked(self.approve(self.payload(
            source_path=str(self.root / ".." / "outside.png"))), "..")
        self.assertBlocked(self.approve(self.payload(source_path="outside.png")),
                           "absolūtam")

    @unittest.skipIf(os.name == "nt", "symlink izveidei Windows vajag privilēģijas")
    def test_symlink_out_of_root_rejected(self):
        link = self.root / "link.png"
        link.symlink_to(self.outside)
        self.assertBlocked(self.approve(self.payload(source_path=str(link))), "saiti")

    # 3
    def test_disallowed_provider_or_destination_rejected(self):
        self.assertBlocked(self.approve(self.payload(provider="dropbox")), "provider")
        self.assertBlocked(self.approve(self.payload(destination="otherFolder")),
                           "destination")

    # 4
    def test_sha256_mismatch_rejected_before_upload(self):
        e = self.assertBlocked(self.approve(self.payload(expected_sha256="a" * 64)), "SHA256")
        self.assertEqual(e.evidence["sha256"], hashlib.sha256(PNG).hexdigest())

    # 5
    def test_size_mismatch_rejected(self):
        self.assertBlocked(self.approve(self.payload(expected_size=len(PNG) + 1)), "size")

    # 6
    def test_readback_mismatch_blocks(self):
        self.drive.corrupt_readback = True
        with self.assertRaises(ArtifactPublishBlocked) as ctx:
            self.adapter.execute(self.approve(self.payload()))
        self.assertIn("readback", ctx.exception.reason)
        self.assertFalse(ctx.exception.evidence["compare"]["match"])
        self.drive.corrupt_readback = False
        meta = self.drive.files["file1"]
        meta["size"] = "1"  # vēlāka neatbilstība: verify arī nedrīkst apstiprināt
        res = {"file_id": "file1", "file_name": meta["name"], "bytes": len(PNG),
               "sha256": hashlib.sha256(PNG).hexdigest(), "md5": hashlib.md5(PNG).hexdigest(),
               "destination": FOLDER, "idempotency_key": meta["appProperties"][IDEMPOTENCY_KEY]}
        self.assertFalse(self.adapter.verify(res)["verified"])

    # 7
    def test_retry_is_idempotent(self):
        p = self.approve(self.payload())
        first = self.adapter.execute(p).result
        second = self.adapter.execute(p).result
        self.assertEqual(self.drive.uploads, 1)
        self.assertEqual(first["file_id"], second["file_id"])
        self.assertTrue(second["reused_existing"])

    def test_duplicate_existing_files_block(self):
        p = self.approve(self.payload())
        self.adapter.execute(p)
        dup = dict(self.drive.files["file1"], id="file2")
        self.drive.files["file2"] = dup
        with self.assertRaises(ArtifactPublishBlocked) as ctx:
            self.adapter.execute(p)
        self.assertIn("vairāki", ctx.exception.reason)

    # approval piesaiste konkrētam payload
    def test_requires_approval_bound_to_exact_payload(self):
        self.approve(self.payload())
        self.assertBlocked(self.payload(file_name="cits.png"), "approval")
        self.approved.clear()
        self.assertBlocked(self.payload(), "approval")

    def test_evidence_and_result_contain_no_secrets(self):
        res = self.adapter.execute(self.approve(self.payload()))
        blob = repr((res.result, res.evidence, res.artifacts)).lower()
        for word in ("token", "authorization", "bearer", "secret"):
            self.assertNotIn(word, blob)

    def test_bad_inputs_rejected(self):
        cases = {"missing": {"source_path": str(self.src)},
                 "bool_size": self.payload(expected_size=True),
                 "bad_sha": self.payload(expected_sha256="xyz"),
                 "slash_name": self.payload(file_name="a/b.png")}
        exe = self.root / "run.exe"
        exe.write_bytes(b"MZ")
        cases["exe"] = self.payload(source_path=str(exe),
                                    expected_sha256=hashlib.sha256(b"MZ").hexdigest(),
                                    expected_size=2)
        for label, p in cases.items():
            with self.subTest(label):
                if len(p) == 6:
                    self.approve(p)
                with self.assertRaises(ArtifactPublishBlocked):
                    self.adapter.execute(p)
        self.assertEqual(self.drive.uploads, 0)

    def test_constructor_requires_approval_verifier(self):
        cfg = ArtifactPublishConfig(allow_roots=(str(self.root),),
                                    destinations={"google_drive": (FOLDER,)})
        with self.assertRaises(ValueError):
            ArtifactPublishV1Adapter(cfg, drive_client=self.drive, approval_verifier=None)


if __name__ == "__main__":
    unittest.main()
