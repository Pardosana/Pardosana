# Oracle SSH atjaunošana (P0): runbook

Mērķis: atjaunot SSH uz `opc@151.145.57.217` ar pierādījumiem un bez dauzīšanas.
Oracle DONE tikai pēc: svaiga SSH pieslēgšanās → systemd enable → restarta tests → reāls E2E.

## Rīki šajā mapē

| Fails | Kur palaiž | Ko dara |
|---|---|---|
| `Probe-OracleSshOnce.ps1` | Office PC | **Viens** SSH mēģinājums, `ssh -v -E` žurnāls failā, 15 min cooldown failā (izdzīvo restartu), klasifikācija + JSON evidence. Exit 0 OK / 1 neizdevās / 3 cooldown. |
| `recover_once.sh` | Oracle serveris | Pēc noklusējuma tikai pierādījumi. `--apply`: aptur transcriber **tikai** ar pierādījumu (OOM ieraksts vai ≥ 40 % RAM), `sshd -t` → reload/start, AFTER/COMPARE. 15 min bloķēšana otram `--apply`. |
| `stabilize_memory.sh` | Oracle serveris | Swap, sshd OOM aizsardzība, transcriber `MemoryMax` (tikai ja diagnostika to pamato). |
| `../resilience/` | Office PC kods | Failā saglabāts circuit breaker (`FileCircuitBreaker`) un `classify_error`. Stāvoklis izdzīvo watchdog restartu; AUTH/LOGIC kļūdas → BLOCKED līdz `reset()`. |

## Secība

**0. Neviens automātisks process nedauza SSH.** (Office PC aģents to jau pārbaudīja: 0 uzdevumu, 0 procesu.)
`office_node.py` breaker jāpārslēdz uz `resilience.FileCircuitBreaker`, lai restarts to nenotīra:

```python
from resilience import FileCircuitBreaker
br = FileCircuitBreaker(r"<PAVADONIS>\state\breakers.json", "oracle-ssh", cooldown_s=900)
ok, why = br.allow()
if ok:
    try:
        connect()          # esošā pieslēgšanās funkcija
        br.record_success()
    except Exception as e:
        br.record_failure(e)   # AUTH → BLOCKED; timeout → OPEN 15/30/60 min
```

**1. OCI Console (cilvēks, tikai lasīšana; var darīt paralēli cooldown laikam).**
Ieteicams savā parastajā pārlūkā, nevis aģenta vadītā Commander Chrome (tas dotu aģentam pilnas OCI admin tiesības).
- Instance → *Console history* → *Capture*: meklē `Out of memory`, `oom-kill`, `soft lockup`, `hung_task`, `panic`.
- Instance → *Metrics*: Memory un CPU pēdējās 24 h.
- Subnet → *Security List* un NSG: ports 22 atvērts Office IP vai `0.0.0.0/0`.
- Ieraksti **Shape**.

**2. Viens mēģinājums no Office PC** (tikai pēc cooldown):
```powershell
powershell -ExecutionPolicy Bypass -File .\Probe-OracleSshOnce.ps1
```

**3. Lēmums pēc `classification`:**

| Klasifikācija | Rīcība |
|---|---|
| `OK` | `scp recover_once.sh stabilize_memory.sh opc@…:~` → `sudo bash recover_once.sh` (tikai pierādījumi) → ja pamatots, `--apply`. |
| `TCP_TIMEOUT` | Skat. 1. soli. OOM/iekāršana konsolē → **Reboot** (pamatots ar pierādījumu) → pēc 3 min vēlreiz 2. solis. Konsole vesela → Security List/NSG vai ugunsmūris: mēģini no **OCI Cloud Shell** (cita IP). |
| `CLOSED_BEFORE_BANNER` | Sods vai atmiņa. Mēģinājums no Cloud Shell atšķir: izdodas → sods (gaidīt, neatkārtot no Office); neizdodas → atmiņa → Reboot. |
| `TCP_REFUSED` | sshd nedarbojas. OCI *Run command* (ja Cloud Agent spraudnis ieslēgts): `sudo systemctl start sshd`; citādi Reboot. |
| `AUTH_DENIED` | **Neatkārtot.** Serveris strādā; pārbaudīt `~opc/.ssh/authorized_keys` caur Run command vai konsoli. |
| `HOSTKEY_MISMATCH` | **Apstāties.** Pārliecināties, ka IP pieder tam pašam serverim, pirms known_hosts maiņas. |

**4. Pēc SSH OK:** `recover_once.sh --apply` tikai, ja pierādījumi to pamato → `stabilize_memory.sh` (diagnoze, tad `--apply`, ja vajag) → vēl viens `Probe-OracleSshOnce.ps1` kā **svaigs readback** → tikai tad `SSH: VERIFIED`.

**5. Tad commissioning** ar esošajiem deploy/commission skriptiem: systemd enable, `systemctl restart` tests, servera reboot tests, E2E TASK → CLAIM → EXECUTE → READBACK → COMPARE → PASS.

## Ko šie rīki NEdara
Nemaina `sshd_config`, ugunsmūri, OCI tīklu, PAVADONIS kodu; neatkārto mēģinājumus; neievada paroles; neatslēdz servisus (tikai aptur).
