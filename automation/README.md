# SalesEngine V14.1 · Automation engine

Šī mape ir **automation skelets** SalesEngine V14.1 sistēmai. Mērķis — savienot operatoru pirms zvana, zvana laikā un pēc zvana ar reālu datu plūsmu.

## Augsta līmeņa flow

```
Google Calendar event (T-30 min)
        │
        ▼
Pre-call brief generator
  · klienta meklēšana (web + CRM)
  · klienta tipa hipotēze (6 V14 tipi)
  · pielāgots Q-flow
  · 3 prognozētie iebildumi + response trees
  · COI math draft
        │
        ▼
Live call (Fathom recording)
  · operatoram cork-card priekšā
  · Conductor traffic light
  · (opcionāli) live LLM cue
        │
        ▼
Fathom transcript webhook
        │
        ▼
LLM post-call analyzer
  · score 1-13
  · vājākais mezgls
  · 3 lietas, kas nostrādāja
  · 3 lietas, ko mainīt (ar V14 verbatim alt)
  · next-step frāze + datums
        │
        ▼
CRM writeback (Sharpify u.c.)
  · deal stage update
  · note ar score un summary
  · follow-up task ar datumu
```

## Failu struktūra

| Fails | Mērķis |
| --- | --- |
| `config.py` | Konfigurācijas nolasīšana no env vars (Fathom / Calendar / LLM / CRM). |
| `fathom_client.py` | Fathom API wrapper — meeting list, transcript fetch. |
| `calendar_client.py` | Google Calendar OAuth + event fetch. |
| `llm_analyzer.py` | OpenAI / Anthropic post-call analīze pret V14.1 master script. |
| `crm_writer.py` | CRM writeback (sākumā Sharpify stub). |
| `pre_call.py` | Pre-call brief generators. |
| `post_call.py` | Post-call orchestration. |
| `main.py` | Komandrindas entrypoint (cron / manual run). |

## Statusi

- **Skelets uzbūvēts:** YES (visi faili ar tipētiem stubiem un klāt pievienotiem prompt template).
- **Live integrācija:** NO — gaida credentials (Fathom API key, Google Calendar OAuth, LLM API key, Sharpify API).
- **Pirmais pareizais starta solis:** uzstādīt env vars un palaist `python automation/main.py --dry-run`.

## Drošība

- Visi tokens nāk no env vars vai Devin secrets.
- Nekādi credentials nav komitēti repo.
- Fathom API: 60 req/min limit — ieliek `time.sleep(1.0)` starp request paketēm.
- Google Calendar: read-only scope (`https://www.googleapis.com/auth/calendar.events.readonly`).
- LLM: temperature ≤ 0.3 visiem analītiskajiem zvaniem.
