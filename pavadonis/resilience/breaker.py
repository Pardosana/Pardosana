"""Circuit breaker, kura stāvoklis izdzīvo procesa restartu.

Problēma, ko tas risina: ja breaker stāvoklis ir tikai atmiņā, watchdog restarts
to notīra un katrs restarts kļūst par jaunu mēģinājumu — tā pati retry cilpa.

Stāvokļi:
  CLOSED    — atļauts.
  OPEN      — aizliegts līdz open_until (īslaicīga kļūda vai kvota).
  HALF_OPEN — pēc open_until atļauts TIEŠI viens mēģinājums.
  BLOCKED   — autorizācijas vai loģikas kļūda: nekad neatkārto pats; tikai reset().

Bojāts vai nelasāms stāvokļa fails → aizliegts (fail closed).
"""

from __future__ import annotations

import enum
import json
import os
import re
import tempfile
import time
from pathlib import Path
from typing import Callable


class ErrorClass(str, enum.Enum):
    TRANSIENT = "TRANSIENT"   # timeout, 5xx, tīkls
    AUTH = "AUTH"             # 401/403, publickey denied, beidzies tokens
    QUOTA = "QUOTA"           # 429, rate limit
    LOGIC = "LOGIC"           # validācija, readback mismatch
    UNKNOWN = "UNKNOWN"       # neklasificēts → apstrādā kā TRANSIENT, bet atzīmē


_PATTERNS: list[tuple[ErrorClass, re.Pattern]] = [
    (ErrorClass.AUTH, re.compile(r"permission denied|publickey|host key verification failed|"
                                 r"\b401\b|\b403\b|unauthori[sz]ed|invalid_grant|token expired", re.I)),
    (ErrorClass.QUOTA, re.compile(r"\b429\b|rate.?limit|quota", re.I)),
    (ErrorClass.LOGIC, re.compile(r"readback mismatch|validation|invalid argument|\b400\b|\b422\b", re.I)),
    (ErrorClass.TRANSIENT, re.compile(r"timed? ?out|connection (refused|reset|closed)|"
                                      r"kex_exchange_identification|no route to host|"
                                      r"network is unreachable|\b50[0234]\b|temporar", re.I)),
]


def classify_error(err: object) -> ErrorClass:
    text = str(err)
    for cls, pat in _PATTERNS:
        if pat.search(text):
            return cls
    return ErrorClass.UNKNOWN


class FileCircuitBreaker:
    def __init__(self, path: str | os.PathLike, name: str, *, cooldown_s: float = 900,
                 clock: Callable[[], float] = time.time):
        if not re.match(r"^[A-Za-z0-9._:-]{1,80}$", name):
            raise ValueError("nederīgs breaker nosaukums")
        self.path = Path(path)
        self.name = name
        self.cooldown_s = cooldown_s
        self._clock = clock

    # ---- glabāšana ----
    def _load_all(self) -> dict | None:
        if not self.path.exists():
            return {}
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else None
        except (OSError, ValueError):
            return None

    def _save(self, entry: dict) -> None:
        data = self._load_all() or {}
        data[self.name] = entry
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=self.path.parent, prefix=".breaker-", suffix=".json")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            os.replace(tmp, self.path)
        except BaseException:
            Path(tmp).unlink(missing_ok=True)
            raise

    def state(self) -> dict:
        data = self._load_all()
        if data is None:
            return {"state": "CORRUPT"}
        return data.get(self.name, {"state": "CLOSED"})

    # ---- lēmumi ----
    def allow(self) -> tuple[bool, str]:
        """Vai drīkst mēģināt TAGAD. HALF_OPEN atļauju ieraksta pirms atgriešanas,
        lai paralēls vai pēc-restarta izsaukums nesaņemtu otru atļauju."""
        st = self.state()
        s = st.get("state")
        if s == "CORRUPT":
            return False, "stāvokļa fails bojāts — fail closed"
        if s == "BLOCKED":
            return False, f"BLOCKED ({st.get('last_error_class')}): {st.get('reason', '')}; vajag reset()"
        if s == "HALF_OPEN":
            if self._clock() > st.get("half_open_at", 0) + self.cooldown_s:
                # Pārbaudes mēģinājums netika pabeigts (avārija) → skaitās kā neveiksme.
                self.record_failure(ErrorClass.TRANSIENT)
                return False, "HALF_OPEN mēģinājums netika pabeigts — atkal OPEN"
            return False, "viens pārbaudes mēģinājums jau notiek"
        if s == "OPEN":
            if self._clock() < st.get("open_until", 0):
                return False, f"OPEN līdz {st['open_until']:.0f}"
            self._save({**st, "state": "HALF_OPEN", "half_open_at": self._clock()})
            return True, "HALF_OPEN: viens mēģinājums"
        return True, "CLOSED"

    def record_success(self) -> None:
        self._save({"state": "CLOSED", "failures": 0, "last_success": self._clock()})

    def record_failure(self, err: object, *, retry_after_s: float | None = None) -> ErrorClass:
        cls = err if isinstance(err, ErrorClass) else classify_error(err)
        st = self.state()
        failures = int(st.get("failures", 0)) + 1 if st.get("state") != "CORRUPT" else 1
        base = {"failures": failures, "last_error_class": cls.value,
                "reason": str(err)[:300], "last_failure": self._clock()}
        if cls in (ErrorClass.AUTH, ErrorClass.LOGIC):
            self._save({**base, "state": "BLOCKED"})
        else:
            wait = retry_after_s if (cls is ErrorClass.QUOTA and retry_after_s) else \
                self.cooldown_s * min(2 ** (failures - 1), 8)
            self._save({**base, "state": "OPEN", "open_until": self._clock() + wait})
        return cls

    def reset(self) -> None:
        """Tikai cilvēks vai apzināta darbība pēc cēloņa novēršanas."""
        self._save({"state": "CLOSED", "failures": 0, "reset_at": self._clock()})
