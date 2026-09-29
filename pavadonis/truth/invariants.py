"""Invarianti: noteikumi, kam vienmēr jābūt spēkā. Pārkāpums → uzdevums ar idempotences atslēgu.

Ievaddati (`ctx`) ir vienkāršas vārdnīcas; PAVADONIS pusē tās ielādē no bus.sqlite,
Sorsora, Kalendāra (integrācijas robeža). Laiki: UNIX sekundes (float).

ctx = {
  "now": float,
  "messages":  [{"client_id", "sent_at", "channel"}],              # nosūtītas klientu ziņas
  "tasks":     [{"task_id", "state", "state_since"}],               # PAVADONIS uzdevumi
  "clients":   [{"client_id", "paid": bool, "build_owner": str|None}],
  "meetings":  [{"meeting_id", "client_id", "starts_at"}],
  "briefs":    [{"meeting_id", "created_at"}],
  "calls":     [{"call_id", "client_id", "ended_at"}],
  "followups": [{"call_id", "done_at"}],
  "facts":     FactStore | None, "required_facts": [str]
}
Trūkstošs ctx lauks → invariants tiek izlaists un atzīmēts kā SKIPPED (nevis PASS).
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Callable

H = 3600.0


@dataclass(frozen=True)
class Violation:
    invariant: str
    severity: str        # P0 | P1 | P2
    subject: str         # klients, uzdevums, fakts
    detail: str

    @property
    def key(self) -> str:
        return hashlib.sha256(f"{self.invariant}|{self.subject}".encode()).hexdigest()[:24]


@dataclass(frozen=True)
class Invariant:
    name: str
    severity: str
    needs: tuple[str, ...]
    check: Callable[[dict], list[Violation]]
    description: str = ""


def _max_one_message_per_24h(ctx: dict) -> list[Violation]:
    by_client: dict[str, list[float]] = {}
    for m in ctx["messages"]:
        by_client.setdefault(m["client_id"], []).append(m["sent_at"])
    out = []
    for cid, times in by_client.items():
        times.sort()
        for a, b in zip(times, times[1:]):
            if b - a < 24 * H:
                out.append(Violation("max_one_message_per_client_24h", "P0", cid,
                                     f"2 ziņas {int((b - a) / 60)} min intervālā"))
                break
    return out


def _no_long_working(ctx: dict) -> list[Violation]:
    limit = ctx.get("max_working_s", 2 * H)
    return [Violation("no_task_working_over_2h", "P1", t["task_id"],
                      f"WORKING {int((ctx['now'] - t['state_since']) / 60)} min")
            for t in ctx["tasks"]
            if t["state"] == "WORKING" and ctx["now"] - t["state_since"] > limit]


def _paid_has_build_owner(ctx: dict) -> list[Violation]:
    return [Violation("paid_client_has_build_owner", "P0", c["client_id"], "samaksājis, nav izbūves atbildīgā")
            for c in ctx["clients"] if c.get("paid") and not c.get("build_owner")]


def _meeting_has_brief(ctx: dict) -> list[Violation]:
    lead = ctx.get("brief_lead_s", 2 * H)
    briefs = {b["meeting_id"]: b["created_at"] for b in ctx["briefs"]}
    out = []
    for m in ctx["meetings"]:
        due = m["starts_at"] - lead
        if ctx["now"] < due:
            continue  # vēl nav jābūt
        made = briefs.get(m["meeting_id"])
        if made is None or made > due:
            out.append(Violation("meeting_has_brief_2h_before", "P1", m["meeting_id"],
                                 "nav brīfinga" if made is None else "brīfings par vēlu"))
    return out


def _call_has_followup(ctx: dict) -> list[Violation]:
    window = ctx.get("followup_window_s", 24 * H)
    done = {f["call_id"]: f["done_at"] for f in ctx["followups"]}
    out = []
    for c in ctx["calls"]:
        deadline = c["ended_at"] + window
        d = done.get(c["call_id"])
        if (d is None and ctx["now"] > deadline) or (d is not None and d > deadline):
            out.append(Violation("call_has_followup_24h", "P1", c["call_id"],
                                 "nav follow-up" if d is None else "follow-up par vēlu"))
    return out


def _required_facts_fresh(ctx: dict) -> list[Violation]:
    store = ctx["facts"]
    out = []
    for key in ctx["required_facts"]:
        f = store.get(key)
        if f.status != "FRESH":
            out.append(Violation("required_facts_fresh", "P1", key, f.status))
    return out


BUILTIN_INVARIANTS: tuple[Invariant, ...] = (
    Invariant("max_one_message_per_client_24h", "P0", ("messages",), _max_one_message_per_24h,
              "Neviens klients nesaņem 2 ziņas 24 h laikā."),
    Invariant("paid_client_has_build_owner", "P0", ("clients",), _paid_has_build_owner,
              "Katram samaksājušam klientam ir izbūves atbildīgais."),
    Invariant("meeting_has_brief_2h_before", "P1", ("meetings", "briefs"), _meeting_has_brief,
              "Katrai tikšanās reizei brīfings vismaz 2 h iepriekš."),
    Invariant("call_has_followup_24h", "P1", ("calls", "followups"), _call_has_followup,
              "Katram zvanam follow-up 24 h laikā."),
    Invariant("no_task_working_over_2h", "P1", ("tasks",), _no_long_working,
              "Neviens uzdevums nav WORKING ilgāk par 2 h."),
    Invariant("required_facts_fresh", "P1", ("facts", "required_facts"), _required_facts_fresh,
              "Obligātie fakti (piem. oracle.ssh.ok) nav novecojuši."),
)


def run_invariants(ctx: dict, invariants=BUILTIN_INVARIANTS) -> dict:
    """Atgriež {"violations": [...], "passed": [...], "skipped": [...], "errors": [...]}."""
    report = {"violations": [], "passed": [], "skipped": [], "errors": []}
    for inv in invariants:
        if any(ctx.get(n) is None for n in inv.needs):
            report["skipped"].append(inv.name)
            continue
        try:
            found = inv.check(ctx)
        except Exception as exc:  # viena invarianta kļūda neaptur pārējos
            report["errors"].append({"invariant": inv.name, "error": f"{type(exc).__name__}: {exc}"})
            continue
        (report["violations"].extend(found) if found else report["passed"].append(inv.name))
    return report


def violations_to_tasks(violations: list[Violation]) -> list[dict]:
    """Uzdevumu payload rindai. idempotency_key ir stabils: atkārtota pārbaude nerada dublikātus."""
    return [{"idempotency_key": f"invariant:{v.key}", "priority": v.severity,
             "title": f"{v.invariant}: {v.subject}", "detail": v.detail,
             "invariant": v.invariant, "subject": v.subject} for v in violations]
