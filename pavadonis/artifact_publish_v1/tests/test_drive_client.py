import io
import json
import unittest
import urllib.error
import urllib.parse

from artifact_publish_v1 import DriveError, GoogleDriveClient
from artifact_publish_v1.drive import UPLOAD_API

TOKEN = "ya29.SECRET-TOKEN"


class _Resp:
    def __init__(self, body=b"", headers=None):
        self._body, self.headers = body, headers or {}

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def read(self):
        return self._body


class FakeOpener:
    def __init__(self, responses):
        self.responses, self.requests = list(responses), []

    def __call__(self, req, timeout):
        self.requests.append(req)
        r = self.responses.pop(0)
        if isinstance(r, Exception):
            raise r
        return r


class DriveClientTest(unittest.TestCase):
    def client(self, *responses):
        self.opener = FakeOpener(responses)
        return GoogleDriveClient(lambda: TOKEN, urlopen=self.opener)

    def test_upload_uses_resumable_session_with_app_properties(self):
        c = self.client(_Resp(headers={"Location": f"{UPLOAD_API}/files?upload_id=abc"}),
                        _Resp(json.dumps({"id": "fid_1"}).encode()))
        fid = c.upload(data=b"abc", name="a.png", folder_id="fold_1",
                       mime_type="image/png", app_properties={"pav_idem": "f" * 64})
        self.assertEqual(fid, "fid_1")
        init, put = self.opener.requests
        self.assertEqual(json.loads(init.data), {"name": "a.png", "parents": ["fold_1"],
                                                 "appProperties": {"pav_idem": "f" * 64}})
        self.assertIn("supportsAllDrives=true", init.full_url)
        self.assertEqual(put.get_method(), "PUT")
        self.assertEqual(put.data, b"abc")

    def test_rejects_foreign_upload_location(self):
        c = self.client(_Resp(headers={"Location": "https://evil.example/x"}))
        with self.assertRaises(DriveError):
            c.upload(data=b"a", name="a.png", folder_id="f", mime_type="image/png",
                     app_properties={})

    def test_find_query_is_scoped(self):
        c = self.client(_Resp(json.dumps({"files": [{"id": "x1"}]}).encode()))
        self.assertEqual(c.find_by_app_property("fold_1", "pav_idem", "a" * 64), ["x1"])
        q = urllib.parse.parse_qs(urllib.parse.urlsplit(self.opener.requests[0].full_url).query)["q"][0]
        self.assertIn("'fold_1' in parents", q)
        self.assertIn("trashed = false", q)
        self.assertIn("value='" + "a" * 64 + "'", q)

    def test_rejects_injection_in_ids(self):
        c = self.client()
        with self.assertRaises(DriveError):
            c.find_by_app_property("x' or '1'='1", "pav_idem", "a" * 64)
        with self.assertRaises(DriveError):
            c.get_metadata("../../about")

    def test_error_message_has_no_token(self):
        body = json.dumps({"error": {"errors": [{"reason": "notFound"}]}}).encode()
        err = urllib.error.HTTPError("u", 404, "Not Found", {}, io.BytesIO(body))
        c = self.client(err)
        with self.assertRaises(DriveError) as ctx:
            c.get_metadata("fid_1")
        self.assertEqual(ctx.exception.status, 404)
        self.assertIn("notFound", str(ctx.exception))
        self.assertNotIn(TOKEN, str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
