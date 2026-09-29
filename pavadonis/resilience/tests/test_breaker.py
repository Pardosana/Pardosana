import tempfile
import unittest
from pathlib import Path

from resilience import ErrorClass, FileCircuitBreaker, classify_error


class Clock:
    def __init__(self):
        self.t = 1_000_000.0

    def __call__(self):
        return self.t


class BreakerTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.path = Path(self._tmp.name) / "breaker.json"
        self.clock = Clock()

    def tearDown(self):
        self._tmp.cleanup()

    def make(self):
        return FileCircuitBreaker(self.path, "oracle-ssh", cooldown_s=900, clock=self.clock)

    def test_classify_ssh_and_http(self):
        self.assertIs(classify_error("ssh: connect to host 1.2.3.4 port 22: Connection timed out"), ErrorClass.TRANSIENT)
        self.assertIs(classify_error("kex_exchange_identification: Connection closed by remote host"), ErrorClass.TRANSIENT)
        self.assertIs(classify_error("opc@1.2.3.4: Permission denied (publickey)."), ErrorClass.AUTH)
        self.assertIs(classify_error("HTTP 429 Too Many Requests"), ErrorClass.QUOTA)
        self.assertIs(classify_error("readback mismatch on size"), ErrorClass.LOGIC)
        self.assertIs(classify_error("something odd"), ErrorClass.UNKNOWN)

    def test_state_survives_restart(self):
        self.make().record_failure("Connection timed out")
        restarted = self.make()  # jauns objekts = procesa restarts
        ok, why = restarted.allow()
        self.assertFalse(ok, why)

    def test_half_open_allows_exactly_one(self):
        b = self.make()
        b.record_failure("Connection timed out")
        self.clock.t += 901
        self.assertTrue(b.allow()[0])
        self.assertFalse(self.make().allow()[0])  # arī pēc restarta otru nedod

    def test_failure_in_half_open_reopens_longer(self):
        b = self.make()
        b.record_failure("timed out")
        self.clock.t += 901
        b.allow()
        b.record_failure("timed out")
        st = b.state()
        self.assertEqual(st["state"], "OPEN")
        self.assertEqual(st["open_until"], self.clock.t + 1800)

    def test_abandoned_half_open_reopens(self):
        b = self.make()
        b.record_failure("timed out")
        self.clock.t += 901
        self.assertTrue(b.allow()[0])      # process saņem atļauju un avarē
        self.clock.t += 901
        self.assertFalse(self.make().allow()[0])
        self.assertEqual(b.state()["state"], "OPEN")

    def test_success_closes(self):
        b = self.make()
        b.record_failure("timed out")
        self.clock.t += 901
        b.allow()
        b.record_success()
        self.assertEqual(b.allow(), (True, "CLOSED"))

    def test_auth_blocks_forever_until_reset(self):
        b = self.make()
        b.record_failure("Permission denied (publickey)")
        self.clock.t += 10 ** 7
        self.assertFalse(b.allow()[0])
        b.reset()
        self.assertTrue(b.allow()[0])

    def test_quota_uses_retry_after(self):
        b = self.make()
        b.record_failure("429", retry_after_s=60)
        self.clock.t += 61
        self.assertTrue(b.allow()[0])

    def test_corrupt_file_fails_closed(self):
        self.path.write_text("{not json", encoding="utf-8")
        self.assertFalse(self.make().allow()[0])

    def test_breakers_are_independent(self):
        self.make().record_failure("timed out")
        other = FileCircuitBreaker(self.path, "drive-api", clock=self.clock)
        self.assertTrue(other.allow()[0])


if __name__ == "__main__":
    unittest.main()
