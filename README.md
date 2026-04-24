# SalesEngine V26.1 · DOMINO ENGINE

> **Kognitīvi-arhitektoniska B2B pārdošanas zvanu sistēma latviski.** Katrs jautājums ir domino, kas automātiski iedarbina nākamo. Klients pats sev pierāda, ka jārīkojas. Operators nepārdod — **projektē loģisko vidi**.

**Versija:** V26.1 · **Kompilēts:** 2026.04.24 · **Bāze:** V1→V25 (29 avotu faili)

---

## ⚡ ĀTRĀ SĀKUMS

1. **Lasi FULL**: [`docs/FULL.md`](docs/FULL.md) — viss vienā failā (91 lpp PDF versija: [`SalesEngine_V26.1_FULL.pdf`](SalesEngine_V26.1_FULL.pdf))
2. **Izprintē Cheat Sheet**: [`docs/02_OPERATOR_CHEAT_SHEET.pdf`](docs/02_OPERATOR_CHEAT_SHEET.pdf) — 1 A4 lapa dzīvam zvanam
3. **Iestati AI asistentu**: Kopē [`docs/03_AI_SALES_ARCHITECT_PROMPT.md`](docs/03_AI_SALES_ARCHITECT_PROMPT.md) → ChatGPT Custom GPT

---

## 📁 STRUKTŪRA

```
salesengine/
├── README.md                         ← šis fails
├── SalesEngine_V26.1_FULL.pdf       ← 91 lpp PDF ar VISU
├── SalesEngine_V26.1_FULL.docx      ← Word versija
├── docs/
│   ├── FULL.md                       ← Viens markdown ar visu
│   ├── 01_MASTER_CORPUS.md           ← V26.1 kanoniskā teorija (29 sadaļas + pielikumi)
│   ├── 02_OPERATOR_CHEAT_SHEET.html  ← Cheat sheet avots
│   ├── 02_OPERATOR_CHEAT_SHEET.pdf   ← 1-lapas A4 print-ready
│   ├── 03_AI_SALES_ARCHITECT_PROMPT.md  ← System prompt LLM-iem
│   ├── 04_CALL_ANALYSIS_89.md        ← 89 zvanu datu analīze
│   └── 05_CHANGELOG.md               ← Konsolidācijas žurnāls
├── scripts/
│   ├── analyze_calls.py              ← Regex signāla detekcija Fathom transkriptiem
│   └── build_full.py                 ← FULL.md būve no avotu failiem
├── data/
│   ├── calls_index.json              ← 89 zvanu metadata
│   ├── calls_signals.json            ← Pattern detekcijas rezultāti
│   └── calls_full.json               ← Kombinētais (metadata + signāli + score)
└── deploy/                           ← Deploy instrukcijas (nākamajā iterācijā)
```

---

## 🧠 SISTĒMAS KODOLS

### Filozofija
> *"Tu neesi pārdevējs — Tu esi **Kognitīvās vides dizaineris**."*
> **Formula:** *Rīcības sāpes < Bezdarbības sāpes = Lēmums.*

### 4 Meta Bloki × 14-20 Domino mezgli

| Meta | Domino | Laiks | Funkcija |
|---|---|---|---|
| **1 · Entry & Frame** | D1–D3 | 2 min | Noņem "pārdevēja" masku, iestata autoritāti |
| **2 · Diagnosis & Gap** | D4–D8 | 15 min | Klients pats verbalizē € zaudējumu |
| **3 · Model & Vision** | D9–D12 | 10 min | Klients pats vērtē risinājumu 1-10 |
| **4 · Pressure & Close** | D13–D14.5 | 8 min | Cena kā fakts, close ar datumu |

### 4 Neuro-slāņi (V26.1 jaunums)
- **V∞ Stāvoklis** — operatora iekšējā telpa (tukšums + pārpilnība)
- **Dual Engine** — VALUE/STATUS + SAFETY/CONTROL
- **3D Neuro Layer** — Logic + Body + Tribe
- **Discovery Compression** — 4 jautājumi (Q1-Q4) līdz saknei

---

## 📊 DATU BĀZE

- **89 Fathom zvani** analizēti pret V26.1 arhitektūru (sk. [`docs/04_CALL_ANALYSIS_89.md`](docs/04_CALL_ANALYSIS_89.md))
- **78 stundas** kopējā zvana laika · 4 680 min
- **Atklātās vājās vietas:** D1 Frame 83% skip · D9 Self-sell 66% skip · Operator talk 64% zvanu >60%
- **Vidējais health score:** 6.8 / 13

### Reproducēt analīzi
```bash
cd scripts
python3 analyze_calls.py /path/to/Dzivie+zvani.md
```

---

## 🚀 DEPLOY CEĻI

### Līmenis 1 — Personīgā lietošana (1 diena)
- Printē Cheat Sheet PDF
- Setup ChatGPT Custom GPT ar AI Prompt
- Pirms katra zvana — V∞ check
- Pēc katra zvana — 14 pašaudits

### Līmenis 2 — Komanda (2-4 nedēļas)
- Share `docs/FULL.md` ar operatoriem
- 2h workshop: V∞ + 4 Meta + Domino
- Weekly call review ar 0-13 score
- Obligāti: D1 FRAME + D9 SELF-SELL katrā zvanā

### Līmenis 3 — Sistēma (2-3 mēneši)
- Automatizēta post-call scoring → Google Sheet
- Team Slack ar #call-reviews
- Trend dashboard

### Līmenis 4 — Mērogs (4+ mēneši)
- Web app ar AI Architect UI
- Sales simulator ar AI klientu
- CRM integrācija

Pilns deploy čeklists: [`docs/FULL.md` §6](docs/FULL.md#6-deploy-checklist)

---

## 🔧 TECH STACK

**Dokumentu būve:**
- Markdown → DOCX: `pandoc`
- Markdown → PDF: `weasyprint` (Python, CSS-bāzēts)
- HTML → PDF: `weasyprint`

**Datu analīze:**
- Python 3.10+
- Regex pattern detekcija
- JSON output

**AI integrācijas (planned):**
- OpenAI API / Anthropic Claude
- ChatGPT Custom GPT
- n8n / Make workflows

---

## 📋 KONTRIBUCIJAS

Šis repo ir **proprietary / konfidenciāls**. Lūgums neizplatīt bez autora atļaujas.

**Iteratīvi uzlabojumi:**
1. Fork → private branch
2. Eksperimentē ar jauniem mezgliem / frāzēm
3. Validē pret vismaz 10 dzīviem zvaniem
4. PR ar score salīdzinājumu pirms/pēc

---

## 🗓️ VERSIJU VĒSTURE

| Versija | Datums | Galvenās izmaiņas |
|---|---|---|
| V1-V24 | 2024-2026 | Iteratīva evolūcija (sk. Master Corpus §XXI) |
| **V25** | 2026.04.21 | Ultimate Monolith — apvieno V1-V24 |
| **V26** | 2026.04.23 | Deduplikācija no 24 avotu failiem |
| **V26.1** | 2026.04.24 | +5 failu batch2 (V∞, Dual Engine, 3D Neuro, CARE, META 7-domino) |

Pilns changelog: [`docs/05_CHANGELOG.md`](docs/05_CHANGELOG.md)

---

## 📞 KONTAKTS

**Autors:** Lawrence Ap · Lauris Leitāns
**E-pasts:** lauris.leitaans@gmail.com
**Produkts:** META Lead Gen + SalesEngine metodoloģija

---

**LICENCE:** Proprietary · Visas tiesības aizsargātas © 2026
