"""Fakti ar avotu, pierādījumu un derīguma termiņu. Tikai pievieno, nekad nelabo.

    store.assert_fact("oracle.ssh.ok", True, source="Probe-OracleSshOnce",
                      evidence_ref="evidence-20260929T2130Z.json")
    store.require_fresh("oracle.ssh.ok")   # StaleFact, ja vecāks par termiņu vai nav

Statuss:
  FRESH   — pēdējais novērojums jaunāks par TTL
  STALE   — vecāks par TTL: pirms rīcības vispirms pārbaudi
  UNKNOWN — nekad nav novērots
"""

from __future__ import annotations

import json
import re
import sqlite3
import time
from dataclasses import dataclass
from typing import Any, Callable

# Noklusējuma termiņi pēc atslēgas prefiksa (garākais sakritušais prefikss uzvar).
DEFAULT_TTLS: dict[str, float] = {
    "oracle.ssh.": 3600,
    "browser_session.": 86400,
    "heartbeat.": 7200,
    "regression.": 86400,
    "": 3600,
}
_KEY_RE = re.compile(r"^[a-z0-9_]+(\.[a-z0-9_]+)*$")


class StaleFact(Exception):
    def __init__(self, fact: "Fact"):
        super().__init__(f"{fact.key}: {fact.status}"
                         + (f" (vecums {fact.age_s:.0f}s > {fact.ttl_s:.0f}s)" if fact.age_s is not None else ""))
        self.fact = fact


@dataclass(frozen=True)
class Fact:
    key: str
    status: str               # FRESH | STALE | UNKNOWN
    value: Any = None
    source: str | None = None
    evidence_ref: str | None = None
    observed_at: float | None = None
    ttl_s: float | None = None
    age_s: float | None = None


class FactStore:
    def __init__(self, path: str, *, ttls: dict[str, float] | None = None,
                 clock: Callable[[], float] = time.time):
        self._db = sqlite3.connect(path)
        self._ttls = {**DEFAULT_TTLS, **(ttls or {})}
        self._clock = clock
        self._db.execute("""CREATE TABLE IF NOT EXISTS pav_truth_fact_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT NOT NULL, value_json TEXT NOT NULL, source TEXT NOT NULL,
            evidence_ref TEXT NOT NULL, observed_at REAL NOT NULL, ttl_s REAL NOT NULL)""")
        self._db.execute("CREATE INDEX IF NOT EXISTS pav_truth_fact_key ON pav_truth_fact_log(key, id)")
        self._db.commit()

    def close(self) -> None:
        self._db.close()

    def _ttl_for(self, key: str) -> float:
        best = max((p for p in self._ttls if key.startswith(p)), key=len)
        return self._ttls[best]

    def assert_fact(self, key: str, value: Any, *, source: str, evidence_ref: str,
                    ttl_s: float | None = None, observed_at: float | None = None) -> Fact:
        if not _KEY_RE.match(key):
            raise ValueError("nederīga atslēga (mazie burti, cipari, _ un .)")
        if not source or not evidence_ref:
            raise ValueError("fakts bez avota un pierādījuma nav fakts")
        ttl = float(ttl_s if ttl_s is not None else self._ttl_for(key))
        at = float(observed_at if observed_at is not None else self._clock())
        if at > self._clock() + 60:
            raise ValueError("observed_at nākotnē")
        self._db.execute(
            "INSERT INTO pav_truth_fact_log(key, value_json, source, evidence_ref, observed_at, ttl_s) "
            "VALUES (?,?,?,?,?,?)", (key, json.dumps(value, ensure_ascii=False), source, evidence_ref, at, ttl))
        self._db.commit()
        return self.get(key)

    def get(self, key: str) -> Fact:
        row = self._db.execute(
            "SELECT value_json, source, evidence_ref, observed_at, ttl_s FROM pav_truth_fact_log "
            "WHERE key=? ORDER BY observed_at DESC, id DESC LIMIT 1", (key,)).fetchone()
        if row is None:
            return Fact(key=key, status="UNKNOWN")
        value_json, source, ref, at, ttl = row
        age = self._clock() - at
        return Fact(key=key, status="FRESH" if age <= ttl else "STALE", value=json.loads(value_json),
                    source=source, evidence_ref=ref, observed_at=at, ttl_s=ttl, age_s=age)

    def require_fresh(self, key: str) -> Fact:
        fact = self.get(key)
        if fact.status != "FRESH":
            raise StaleFact(fact)
        return fact

    def history(self, key: str, limit: int = 20) -> list[dict]:
        rows = self._db.execute(
            "SELECT value_json, source, evidence_ref, observed_at FROM pav_truth_fact_log "
            "WHERE key=? ORDER BY observed_at DESC, id DESC LIMIT ?", (key, limit)).fetchall()
        return [{"value": json.loads(v), "source": s, "evidence_ref": r, "observed_at": a} for v, s, r, a in rows]

    def keys(self) -> list[str]:
        return [r[0] for r in self._db.execute("SELECT DISTINCT key FROM pav_truth_fact_log ORDER BY key")]
