"""Build SalesEngine_V26.1_FULL.md — single master with all deliverables."""

parts = []

# COVER + TOC
parts.append("""# SALESENGINE V26.1 · FULL PACKAGE

> **Viens fails. Visi materiāli. Viens avots patiesībai.**
> Kompilēts: 2026.04.24 · Versija: V26.1-FULL-001
> Autors: Lauris Leitāns (Lawrence Ap)

---

## SATURS

1. [MASTER CORPUS](#1-master-corpus) — V26.1 kanoniskā teorētiskā bāze (29 sadaļas + 6 pielikumi)
2. [OPERATOR CHEAT SHEET](#2-operator-cheat-sheet) — 1-lapas karte dzīvajam zvanam
3. [AI SALES ARCHITECT PROMPT](#3-ai-sales-architect-system-prompt) — sistēmas prompts skriptu ģenerēšanai
4. [89 CALL ANALYSIS](#4-89-call-analysis) — dzīvo zvanu statistiska analīze un uzlabojumi
5. [CHANGELOG](#5-changelog) — avoti, deduplikācija, pretrunu atrisināšana
6. [DEPLOY CHECKLIST](#6-deploy-checklist) — kā sākt lietot šo sistēmu komandā

---

""")

# 1. MASTER CORPUS
parts.append("# 1. MASTER CORPUS\n\n")
with open('SalesEngine_V26_MASTER.md', 'r', encoding='utf-8') as f:
    parts.append(f.read())
parts.append("\n\n---\n\n")

# 2. OPERATOR CHEAT SHEET
parts.append("# 2. OPERATOR CHEAT SHEET\n\n")
parts.append("> **Piezīme:** Šī ir teksta versija. PDF versija (1 lapa A4) atrodama atsevišķi `OPERATOR_CHEAT_SHEET.pdf`.\n\n")
with open('/tmp/cheat_sheet.md', 'r', encoding='utf-8') as f:
    cheat = f.read()
# Bump headings deeper
cheat = cheat.replace('\n# ', '\n## ').replace('\n## ', '\n### ').replace('\n### ', '\n#### ')
# Actually we shifted twice — fix: apply only once
# Easier: rewrite
with open('/tmp/cheat_sheet.md', 'r', encoding='utf-8') as f:
    lines = f.read().split('\n')
new_lines = []
for ln in lines:
    if ln.startswith('# '):
        new_lines.append('## ' + ln[2:])
    elif ln.startswith('## '):
        new_lines.append('### ' + ln[3:])
    elif ln.startswith('### '):
        new_lines.append('#### ' + ln[4:])
    else:
        new_lines.append(ln)
parts.append('\n'.join(new_lines))
parts.append("\n\n---\n\n")

# 3. AI SALES ARCHITECT PROMPT
parts.append("# 3. AI SALES ARCHITECT SYSTEM PROMPT\n\n")
with open('AI_SALES_ARCHITECT_PROMPT.md', 'r', encoding='utf-8') as f:
    ai_prompt = f.read()
# Shift headings
lines = ai_prompt.split('\n')
new_lines = []
for ln in lines:
    if ln.startswith('# '):
        new_lines.append('## ' + ln[2:])
    elif ln.startswith('## '):
        new_lines.append('### ' + ln[3:])
    elif ln.startswith('### '):
        new_lines.append('#### ' + ln[4:])
    else:
        new_lines.append(ln)
parts.append('\n'.join(new_lines))
parts.append("\n\n---\n\n")

# 4. 89 CALL ANALYSIS
parts.append("# 4. 89 CALL ANALYSIS\n\n")
with open('CALL_ANALYSIS_89.md', 'r', encoding='utf-8') as f:
    ca = f.read()
lines = ca.split('\n')
new_lines = []
for ln in lines:
    if ln.startswith('# '):
        new_lines.append('## ' + ln[2:])
    elif ln.startswith('## '):
        new_lines.append('### ' + ln[3:])
    elif ln.startswith('### '):
        new_lines.append('#### ' + ln[4:])
    else:
        new_lines.append(ln)
parts.append('\n'.join(new_lines))
parts.append("\n\n---\n\n")

# 5. CHANGELOG
parts.append("# 5. CHANGELOG\n\n")
with open('V26_CHANGELOG.md', 'r', encoding='utf-8') as f:
    ch = f.read()
lines = ch.split('\n')
new_lines = []
for ln in lines:
    if ln.startswith('# '):
        new_lines.append('## ' + ln[2:])
    elif ln.startswith('## '):
        new_lines.append('### ' + ln[3:])
    else:
        new_lines.append(ln)
parts.append('\n'.join(new_lines))
parts.append("\n\n---\n\n")

# 6. DEPLOY CHECKLIST
parts.append("""# 6. DEPLOY CHECKLIST

## NEDĒĻA 1 — PERSONĪGAIS LAUNCH

- [ ] Izprintē `OPERATOR_CHEAT_SHEET.pdf` — turi pie datora katra zvana laikā
- [ ] Izveido ChatGPT Custom GPT:
  - Instructions: kopē System Prompt no [§3](#3-ai-sales-architect-system-prompt)
  - Knowledge: augšupielādē šo FULL.md
  - Testē ar zobārstniecības piemēru (sk. §3)
- [ ] Pirms katra zvana: V∞ check (§2.I), 3 iespējamie iebildumi iepriekš noteikti
- [ ] Pēc katra zvana: 14 pašaudita punkti (§1 pielikums) + score 0-13 pierakstīts

## NEDĒĻA 2-4 — KOMANDAS ONBOARDING

- [ ] Share šo FULL.md ar katru operatoru (read-only)
- [ ] Organizē 2h workshop: izskaidro V∞ + 4 Meta blokus + Domino mezglus
- [ ] Katram operatoram personīgs ChatGPT ar AI Sales Architect promptu
- [ ] Weekly call review: 1 zvans uz nedēļu score 0-13 + uzlabojuma plāns
- [ ] D1 FRAME un D9 SELF-SELL obligāti 100% zvanu (no analizes atklājumiem)

## MĒNESIS 2-3 — SISTEMATIZĀCIJA

- [ ] GitHub repo — visa materiāla versionēšana
- [ ] Automatizēta post-call scoring — Fathom → analyze_calls.py → Google Sheet
- [ ] Team Slack/Discord ar #call-reviews kanālu
- [ ] Nedēļas score trend dashboard

## MĒNESIS 4+ — MĒROGS

- [ ] Web app ar React UI (AI Sales Architect UI + form + output)
- [ ] Sales simulator ar AI klientu imitāciju
- [ ] API integrācija ar CRM (HubSpot/Salesforce)
- [ ] Sharpify.io produkta launch (sk. §1 XXI sadaļa)

---

**KONTAKTS:** Lawrence Ap · lauris.leitaans@gmail.com

**LICENCE:** Proprietary · Konfidenciāls · Netiek izplatīts bez autora atļaujas

**NEXT VERSION:** V26.2 planoēts, kad būs pieejami papildu dati no live-call automatizētas scoring pipeline.
""")

full = ''.join(parts)
with open('SalesEngine_V26.1_FULL.md', 'w', encoding='utf-8') as f:
    f.write(full)

words = len(full.split())
lines = full.count('\n')
print(f"FULL doc: {len(full):,} chars · {words:,} words · {lines:,} lines")
