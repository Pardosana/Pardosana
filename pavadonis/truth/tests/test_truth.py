import tempfile
import unittest
from pathlib import Path

from truth import BUILTIN_INVARIANTS, FactStore, StaleFact, run_invariants, violations_to_tasks

H = 3600.0


class Clock:
    def __init__(self):
        self.t = 1_800_000_000.0

    def __call__(self):
        return self.t


class FactStoreTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.clock = Clock()
        self.store = FactStore(str(Path(self._tmp.name) / "bus.sqlite"), clock=self.clock)

    def tearDown(self):
        self.store.close()
        self._tmp.cleanup()

    def test_unknown_then_fresh_then_stale(self):
        self.assertEqual(self.store.get("oracle.ssh.ok").status, "UNKNOWN")
        self.store.assert_fact("oracle.ssh.ok", True, source="probe", evidence_ref="ev1")
        f = self.store.require_fresh("oracle.ssh.ok")
        self.assertEqual((f.value, f.ttl_s), (True, 3600))
        self.clock.t += 3601
        with self.assertRaises(StaleFact):
            self.store.require_fresh("oracle.ssh.ok")

    def test_prefix_ttl_and_override(self):
        f = self.store.assert_fact("browser_session.instagram", True, source="cdp", evidence_ref="e")
        self.assertEqual(f.ttl_s, 86400)
        f = self.store.assert_fact("custom.thing", 1, source="x", evidence_ref="e", ttl_s=10)
        self.assertEqual(f.ttl_s, 10)

    def test_append_only_latest_wins_history_kept(self):
        self.store.assert_fact("oracle.ssh.ok", True, source="p", evidence_ref="a")
        self.clock.t += 10
        self.store.assert_fact("oracle.ssh.ok", False, source="p", evidence_ref="b")
        self.assertFalse(self.store.get("oracle.ssh.ok").value)
        self.assertEqual([h["evidence_ref"] for h in self.store.history("oracle.ssh.ok")], ["b", "a"])

    def test_old_observation_does_not_override_newer(self):
        self.store.assert_fact("oracle.ssh.ok", False, source="p", evidence_ref="new")
        self.store.assert_fact("oracle.ssh.ok", True, source="p", evidence_ref="old",
                               observed_at=self.clock.t - 100)
        self.assertEqual(self.store.get("oracle.ssh.ok").evidence_ref, "new")

    def test_rejects_fact_without_evidence_or_bad_key_or_future(self):
        with self.assertRaises(ValueError):
            self.store.assert_fact("a.b", 1, source="x", evidence_ref="")
        with self.assertRaises(ValueError):
            self.store.assert_fact("Bad Key", 1, source="x", evidence_ref="e")
        with self.assertRaises(ValueError):
            self.store.assert_fact("a.b", 1, source="x", evidence_ref="e", observed_at=self.clock.t + 3600)

    def test_survives_reopen(self):
        self.store.assert_fact("regression.office_pc", 309, source="pytest", evidence_ref="run1")
        again = FactStore(str(Path(self._tmp.name) / "bus.sqlite"), clock=self.clock)
        self.assertEqual(again.get("regression.office_pc").value, 309)
        again.close()


class InvariantTest(unittest.TestCase):
    def ctx(self, **over):
        now = 1_800_000_000.0
        base = {"now": now, "messages": [], "tasks": [], "clients": [], "meetings": [],
                "briefs": [], "calls": [], "followups": []}
        base.update(over)
        return base

    def names(self, report):
        return sorted({v.invariant for v in report["violations"]})

    def test_all_pass_on_clean_data(self):
        r = run_invariants(self.ctx())
        self.assertEqual(r["violations"], [])
        self.assertIn("required_facts_fresh", r["skipped"])  # nav facts → SKIPPED, nevis PASS

    def test_double_message_detected(self):
        now = 1_800_000_000.0
        r = run_invariants(self.ctx(messages=[{"client_id": "c1", "sent_at": now - 5 * H},
                                              {"client_id": "c1", "sent_at": now - 1 * H},
                                              {"client_id": "c2", "sent_at": now - 30 * H},
                                              {"client_id": "c2", "sent_at": now - 1 * H}]))
        self.assertEqual([v.subject for v in r["violations"]], ["c1"])

    def test_paid_without_owner(self):
        r = run_invariants(self.ctx(clients=[{"client_id": "c1", "paid": True, "build_owner": None},
                                             {"client_id": "c2", "paid": True, "build_owner": "Kristaps"},
                                             {"client_id": "c3", "paid": False}]))
        self.assertEqual([v.subject for v in r["violations"]], ["c1"])

    def test_brief_rules(self):
        now = 1_800_000_000.0
        r = run_invariants(self.ctx(
            meetings=[{"meeting_id": "m_ok", "starts_at": now + 1 * H},
                      {"meeting_id": "m_missing", "starts_at": now + 1 * H},
                      {"meeting_id": "m_late", "starts_at": now + 1 * H},
                      {"meeting_id": "m_future", "starts_at": now + 10 * H}],
            briefs=[{"meeting_id": "m_ok", "created_at": now - 3 * H},
                    {"meeting_id": "m_late", "created_at": now - 0.5 * H}]))
        self.assertEqual(sorted(v.subject for v in r["violations"]), ["m_late", "m_missing"])

    def test_followup_rules(self):
        now = 1_800_000_000.0
        r = run_invariants(self.ctx(
            calls=[{"call_id": "ok", "ended_at": now - 30 * H}, {"call_id": "missing", "ended_at": now - 30 * H},
                   {"call_id": "late", "ended_at": now - 30 * H}, {"call_id": "recent", "ended_at": now - 2 * H}],
            followups=[{"call_id": "ok", "done_at": now - 25 * H}, {"call_id": "late", "done_at": now - 1 * H}]))
        self.assertEqual(sorted(v.subject for v in r["violations"]), ["late", "missing"])

    def test_long_working(self):
        now = 1_800_000_000.0
        r = run_invariants(self.ctx(tasks=[{"task_id": "t1", "state": "WORKING", "state_since": now - 3 * H},
                                           {"task_id": "t2", "state": "WORKING", "state_since": now - 1 * H},
                                           {"task_id": "t3", "state": "BLOCKED", "state_since": now - 9 * H}]))
        self.assertEqual([v.subject for v in r["violations"]], ["t1"])

    def test_required_facts(self):
        with tempfile.TemporaryDirectory() as d:
            clock = Clock()
            store = FactStore(str(Path(d) / "f.sqlite"), clock=clock)
            store.assert_fact("regression.office_pc", 309, source="p", evidence_ref="e")
            r = run_invariants(self.ctx(facts=store, required_facts=["regression.office_pc", "oracle.ssh.ok"]))
            self.assertEqual([(v.subject, v.detail) for v in r["violations"]], [("oracle.ssh.ok", "UNKNOWN")])
            store.close()

    def test_missing_input_is_skipped_not_passed(self):
        r = run_invariants({"now": 0.0, "clients": []})
        self.assertIn("paid_client_has_build_owner", r["passed"])
        self.assertIn("max_one_message_per_client_24h", r["skipped"])

    def test_broken_invariant_does_not_stop_others(self):
        r = run_invariants(self.ctx(clients=[{"paid": True}]))  # trūkst client_id
        self.assertEqual(r["errors"][0]["invariant"], "paid_client_has_build_owner")
        self.assertIn("no_task_working_over_2h", r["passed"])

    def test_tasks_are_idempotent(self):
        ctx = self.ctx(clients=[{"client_id": "c1", "paid": True}])
        a = violations_to_tasks(run_invariants(ctx)["violations"])
        b = violations_to_tasks(run_invariants(ctx)["violations"])
        self.assertEqual([t["idempotency_key"] for t in a], [t["idempotency_key"] for t in b])
        self.assertEqual(a[0]["priority"], "P0")

    def test_builtin_count(self):
        self.assertEqual(len(BUILTIN_INVARIANTS), 6)


if __name__ == "__main__":
    unittest.main()
