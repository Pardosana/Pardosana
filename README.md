# SalesEngine V14.1 LV-COMPLETE · V13-COMPLIANT

> **Latviešu B2B pārdošanas zvana sistēma** — V26 saturs, V13 disciplīna. Kompilēta no 50+ avotu dokumentiem, 89 dzīviem Fathom zvaniem (78+ stundas) un V8 GOLD MOLECULAR CORE MAP integrācijas. Tagad ar Hope Break (D7.5), 9-metaforu visual carrier, 6-slāņu stingru disciplīnu, deck slāni un automation skeleton (Fathom + Calendar + LLM + CRM).

**Live web app:** https://app-uuhshekq.devinapps.com  ·  **Deck:** `deck/index.html` (lokāli) vai `make deck-serve`  ·  **Automation:** `make automation-dry`

## V14.1 atjauninājums

- **Hope Break** ielikts kā Q21.5 + V8 mezgls 13.6.5 (starp COI un Inevitability).
- **Visual carrier** ar 9 metaforām un `viena metafora uz vienu call` likumu.
- **6 slāņu disciplīna** (CORE / CURRENT CORK / ARSENAL / TRAINING / SPECIAL-CASE / PRESENTATION CARRIER).
- **8 Prompt Core likumi** (final lock).
- **`deck/`** — pilns prezentācijas slānis ar 20 V14 slaidiem, presenter mode, presenter notes, A/B variantiem.
- **`automation/`** — Fathom + Google Calendar + LLM + CRM skelets ar dry-run režīmu CI pārbaudei.
- Detalizēts changelog: [`DIFF_V14_TO_V14_1.md`](DIFF_V14_TO_V14_1.md)

---

## 📦 Repo struktūra

```
salesengine-repo/
├── docs/v14/                    # Master dokumenti (4 formāti)
│   ├── LV_MASTER_SCRIPT_V14.md  # 1805 rindas, kanoniskais avots
│   ├── LV_MASTER_SCRIPT_V14.pdf # 52 lpp, A4
│   ├── LV_MASTER_SCRIPT_V14.docx
│   └── SalesEngine_V14_PREMIUM_BOOK.pdf  # 90 lpp, vāks + TOC + 5 diagrami + indekss
│
├── app/                         # Interaktīva web aplikācija (single-page HTML+JS)
│   ├── index.html               # 9 sadaļas, dark/light mode, mobile-friendly
│   ├── app.js                   # Q-flow, V8 Molecular, Klientu tipi, Trees, Likumi, Roleplay
│   ├── data.js                  # Strukturēti V14 dati (40 Q + 14 mezgli + 6 tipi + 8 trees + 12 likumi)
│   └── data.json                # Plain JSON (build artifact)
│
├── coach/
│   └── V14_AI_SALES_COACH_PROMPT.md  # Custom GPT / Claude Project system prompt + deploy gids
│
├── pocket/
│   ├── V14_POCKET_CARD.pdf      # 1 A4 landscape, 8 sekcijas — printēt un nēsāt zvanam
│   └── pocket_card.html
│
├── diagrams/                    # 5 augstas izšķirtspējas Mermaid → PNG diagrami
│   ├── 01_q_flow.png            # Q1-Q40 linear flow
│   ├── 02_v8_molecular.png      # 14 mezgli × 4 META blokos
│   ├── 03_objection_trees.png   # 5 visbiežāko iebildumu lēmumu koki
│   ├── 04_client_types.png      # 6 klientu tipu mind map
│   └── 05_conductor_traffic.png # Traffic Light loop
│
├── analysis/
│   └── CALL_ANALYSIS_89.md      # 89 zvanu pattern analīze ar D-skip statistikām
│
├── scripts/                     # Build automation
│   ├── build_full.py
│   └── analyze_calls.py
│
└── .github/workflows/build.yml  # CI auto-build (PDF + DOCX)
```

---

## 🎯 Ko šī sistēma satur

### Kanoniskais V14 dokuments (90 lpp premium book)
- **20 sadaļas:** Filozofija → 4 META Bloki → Q-by-Q Flow (40 jautājumi) → V8 Molecular (14 mezgli × 8 slāņi) → Klientu tipi (6) → Response Trees (9) → Comprehension Ladders (8) → Elite likumi (12) → Conductor Mode → CARE → NLP/Hipnoze/EFT → 89 zvanu analīze → AI Sales Architect → Pielikumi
- **Verbatim frāzes** no Lauris Fathom zvaniem (Kristaps #1, Aras #20, SS2 #4, Krišs #7, Romāns #8, Imp. Meet #3, #57, Mareks #89) un Kristapa pilnā transkripta — **bez amerikāņu closer žargona**
- **Integrētas tehnikas** no 50+ avota dokumentiem (V25, V101, Promti, Gold, V13 NLP/Hipnoze, CARE)

### Interaktīva web aplikācija
9 sadaļas, klikšķināmas, meklējamas, dark/light theme, mobile-friendly:
1. **Q-by-Q Flow** — 40 jautājumi ar fāzu filtru, kritisko Q (⭐⭐⭐) atlasi
2. **Conductor Mode** — Live Traffic Light, Reset frāzes, ZELTA LIKUMS
3. **V8 Molecular Map** — 14 mezgli × 8 slāņu tabi
4. **Klientu tipi** — 6 kartes ar elite ieročiem
5. **Response Trees** — 8 iebildumu lēmumu koki
6. **Elite likumi** — 12 augstākā līmeņa noteikumi
7. **Comprehension Ladders** — 8 sapratnes kāpnes
8. **AI Roleplay Simulator** — treniņš ar 6 klientu tipiem, V14 mezglu analīze pēc katras atbildes
9. **Par sistēmu** — statistika

### AI Sales Coach (Custom GPT prompt)
3 režīmi: **Pre-call prep** (klientu tipa hipotēze + flow + paredzamie iebildumi), **Post-call debrief** (score 1-13, kļūdu identifikācija, follow-up frāze), **Training drill** (CARE protokoli, simulēšana). Deploy ChatGPT/Claude/API 5-30 min.

### Pocket card (1 A4 landscape)
13 sekcijas vienā lapā: Pre-call · Frame · Centrs · Karte · Pitch · 1-10 · Cena · Close · Iebildumu QR · Conductor Mode · Klientu tipi · Aizliegtās frāzes · 12 Elite likumi.

### 89 dzīvu zvanu analīze
Regex-bāzēta pattern analīze visiem Fathom zvaniem (1.2M vārdi). Top atklājumi: D1 FRAME 83% skip · D9 SELF-SELL 66% skip · Operator talk >60% 64% zvanu · Top iebildums "Jau mēģinājām" 45%.

---

## 🚀 Quick Start

### Lietot live web app (mobilā/desktop):
```
https://app-uuhshekq.devinapps.com
```

### Atvērt lokāli:
```bash
cd app && python3 -m http.server 8000
# atver http://localhost:8000
```

### Setup AI Sales Coach (5 min):
1. Atver ChatGPT → "Explore GPTs" → "Create"
2. Configure → Instructions: iekopē `coach/V14_AI_SALES_COACH_PROMPT.md` System Prompt
3. Knowledge: augšupielādē `docs/v14/LV_MASTER_SCRIPT_V14.pdf` un `pocket/V14_POCKET_CARD.pdf`
4. Save un sāc lietot 3 režīmos

### Build PDF lokāli:
```bash
pip install -r requirements.txt
make build
```

---

## 📊 Statistika

| Metrika | Vērtība |
|---|---|
| Master dokumenta rindas | 1805 |
| Vārdu skaits V14 | ~22 000 |
| Q-by-Q jautājumi | 40 |
| V8 mezgli × slāņi | 14 × 8 = 112 |
| Response trees | 9 |
| Elite likumi | 12 |
| Klientu tipi | 6 |
| Comprehension ladders | 8 |
| Reset frāzes | 5 |
| Avota dokumenti | 50+ |
| Fathom zvani analizēti | 89 (78+ stundas) |
| Premium book lpp | 90 |

---

## ⚠️ Konfidencialitāte

- `Dzivie+zvani.md` (89 transkripti) **NAV** šajā repo — `.gitignore` izslēdz šos failus
- `data/` folderī ir tikai abstrahēti, atbrīvoti pattern dati
- Klienta vārdi piemēros (Modern House, Skandi, Indexo, Citadele, NBS, Foreveres) ir publiskas atsauces

---

## 🛠️ Tech

- **Web app:** Vanilla HTML/CSS/JS (single page, no build step required)
- **PDFs:** WeasyPrint (Python)
- **Diagrami:** Mermaid CLI (PNG @ 2400×1600px)
- **CI:** GitHub Actions (auto-build PDF/DOCX on push)
- **Deploy:** Devin Apps (static hosting)

---

## 📝 Versija

**V14 LV-COMPLETE** · 2026-04-25 · © Lauris Leitāns / Sharpify.io

Iepriekšējās versijas (V25 → V26 → V26.1-V26.4) saglabātas iekšējā arhīvā kā evolūcijas atsauce.
