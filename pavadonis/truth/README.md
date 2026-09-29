# truth: fakti ar termiņiem un invarianti

Divas lietas, kas ļauj PAVADONIS pašam zināt, kas ir patiess un kas ir salūzis.

## FactStore: fakts ar avotu, pierādījumu un termiņu

```python
from truth import FactStore, StaleFact
facts = FactStore(r"<PAVADONIS>\data\bus.sqlite")   # tikai savas pav_truth_* tabulas
facts.assert_fact("oracle.ssh.ok", True, source="Probe-OracleSshOnce",
                  evidence_ref="evidence-20260929T2130Z.json")
try:
    facts.require_fresh("oracle.ssh.ok")   # pirms jebkuras Oracle darbības
except StaleFact:
    ...                                    # vispirms viens probe, tad rīcība
```

- Tikai pievieno (append-only). Pēdējais novērojums pēc `observed_at` uzvar, vēsture paliek.
- Fakts bez `source` un `evidence_ref` tiek noraidīts.
- Termiņi pēc prefiksa: `oracle.ssh.*` 1 h, `browser_session.*` 24 h, `heartbeat.*` 2 h,
  `regression.*` 24 h, citi 1 h; `ttl_s=` pārraksta.
- Statusi: FRESH / STALE / UNKNOWN.

## Invarianti: noteikumi, kurus sistēma pati uzrauga

| Invariants | Prioritāte |
|---|---|
| Neviens klients nesaņem 2 ziņas 24 h laikā | P0 |
| Katram samaksājušam klientam ir izbūves atbildīgais | P0 |
| Katrai tikšanās reizei brīfings ≥ 2 h iepriekš | P1 |
| Katram zvanam follow-up 24 h laikā | P1 |
| Neviens uzdevums nav WORKING ilgāk par 2 h | P1 |
| Obligātie fakti nav novecojuši | P1 |

```python
from truth import run_invariants, violations_to_tasks
report = run_invariants(ctx)                 # ctx shēma: invariants.py augšā
tasks = violations_to_tasks(report["violations"])   # stabils idempotency_key → nav dublikātu
```

Trūkstoši ievaddati → `skipped` (nevis PASS). Kļūda vienā invariantā → `errors`, pārējie turpina.

## Ieviešana Office PC (integrācijas robeža)

1. Nokopēt `truth/` blakus `interconnect.py`; palaist `python -m unittest discover -t . -s truth/tests`.
2. Uzrakstīt **ielādētāju**, kas no bus.sqlite / Sorsora / Kalendāra izveido `ctx` vārdnīcu
   (lauki `messages`, `tasks`, `clients`, `meetings`, `briefs`, `calls`, `followups`).
   Tā ir vienīgā PAVADONIS-specifiskā daļa; neizdomāt laukus, kuru avotā nav.
3. Probe, regression un Commander Chrome pārbaudes raksta faktus ar `assert_fact`.
4. TICK (piem. ik 15 min) izsauc `run_invariants` un ievieto `violations_to_tasks` rindā,
   izmantojot esošo idempotences mehānismu pēc `idempotency_key`.
5. Pilns regression pirms un pēc.

Sāc **tikai ar lasīšanu**: vienu nedēļu invarianti tikai ziņo (EVENT_LOG), neveido uzdevumus.
Tad pārbaudi, vai pārkāpumi ir īsti, un tikai pēc tam ieslēdz uzdevumu veidošanu.
