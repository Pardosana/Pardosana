# PAVADONIS rīki (manuālai uzstādīšanai)

Katrs modulis ir neatkarīgs un papildina esošo PAVADONIS (Office PC + Oracle), neaizstāj to.
Neviens no tiem nav uzstādīts automātiski; statuss katrā README/INSTALL.

| Mape | Kam | Sākt ar |
|---|---|---|
| `oracle/` | **P0: SSH atjaunošana** + atmiņas stabilizācija | [`oracle/RUNBOOK_SSH_RECOVERY.md`](oracle/RUNBOOK_SSH_RECOVERY.md) |
| `resilience/` | Circuit breaker, kas izdzīvo restartu; kļūdu klasifikācija | `resilience/breaker.py` (testi: `python -m unittest discover -t . -s resilience/tests`) |
| `artifact_publish_v1/` | ProductionWorker adapteris: publicēšana uz Google Drive ar readback | [`artifact_publish_v1/INSTALL.md`](artifact_publish_v1/INSTALL.md) |
| `commander_browser/` | "Ielogojies vienreiz" Commander Chrome profils | [`commander_browser/INSTALL.md`](commander_browser/INSTALL.md) |

Testi (no šīs mapes): `python -m unittest discover -t . -s <mape>/tests`.
Kanons un spēju moduļi ChatGPT Commanderim: Drive dokumenti "PAVADONIS — BŪVES KANONS …" un "PAVADONIS — SPĒJU MODUĻI …".
