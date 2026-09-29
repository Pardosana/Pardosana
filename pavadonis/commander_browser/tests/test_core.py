import json
import unittest
from unittest import mock

from commander_browser import core

SECRET = "SESSION-VALUE-DO-NOT-LEAK"


class _Resp:
    def __init__(self, body):
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def read(self):
        return self.body


def _opener(body=None, exc=None):
    calls = []

    def urlopen(url, timeout):
        calls.append(url)
        if exc:
            raise exc
        return _Resp(body)
    urlopen.calls = calls
    return urlopen


class FakePW:
    def __init__(self, cookies):
        self.closed = False
        self.endpoint = None
        outer = self

        class Ctx:
            def cookies(self, url):
                return [dict(c) for c in cookies]

        class Browser:
            contexts = [Ctx()]

            def close(self):
                outer.closed = True

        class Chromium:
            def connect_over_cdp(self, endpoint):
                outer.endpoint = endpoint
                return Browser()

        self.chromium = Chromium()

    def __call__(self):
        return self

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


class CommanderBrowserTest(unittest.TestCase):
    def test_endpoint_is_localhost_only_and_port_validated(self):
        self.assertEqual(core.cdp_endpoint(9223), "http://127.0.0.1:9223")
        for bad in (80, 70000, True, "9223"):
            with self.assertRaises(ValueError):
                core.cdp_endpoint(bad)

    def test_status_running(self):
        op = _opener(json.dumps({"Browser": "Chrome/140.0"}).encode())
        s = core.status(9223, urlopen=op)
        self.assertEqual(s, {"running": True, "endpoint": "http://127.0.0.1:9223",
                             "browser": "Chrome/140.0"})
        self.assertEqual(op.calls, ["http://127.0.0.1:9223/json/version"])

    def test_status_not_running(self):
        s = core.status(9223, urlopen=_opener(exc=OSError("refused")))
        self.assertFalse(s["running"])

    def _login(self, cookies):
        pw = FakePW(cookies)
        with mock.patch.object(core, "status", return_value={"running": True}):
            return core.login_state("instagram", playwright_factory=pw), pw

    def test_logged_in_without_leaking_cookie_value(self):
        out, pw = self._login([{"name": "sessionid", "value": SECRET}])
        self.assertTrue(out["logged_in"])
        self.assertNotIn(SECRET, json.dumps(out))
        self.assertEqual(pw.endpoint, "http://127.0.0.1:9223")
        self.assertTrue(pw.closed)

    def test_not_logged_in(self):
        out, _ = self._login([{"name": "csrftoken", "value": "x"}])
        self.assertFalse(out["logged_in"])

    def test_not_running_does_not_connect(self):
        pw = FakePW([])
        with mock.patch.object(core, "status", return_value={"running": False}):
            out = core.login_state("instagram", playwright_factory=pw)
        self.assertIsNone(out["logged_in"])
        self.assertIsNone(pw.endpoint)

    def test_unknown_site_rejected(self):
        with self.assertRaises(ValueError):
            core.login_state("bank")


if __name__ == "__main__":
    unittest.main()
