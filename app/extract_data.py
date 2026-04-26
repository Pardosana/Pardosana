"""Extract structured data from LV_MASTER_SCRIPT_V14_1.md → data.json for the web app."""
import re, json, pathlib

src = pathlib.Path("/home/ubuntu/salesengine/LV_MASTER_SCRIPT_V14_1.md").read_text()

# 1) Questions (Q1..Q40 + Q21.5)
questions = []
# Match #21.5 as well as #4
q_pattern = r"\n(## JAUTĀJUMS #(\d+(?:\.\d+)?) ·[^\n]+)\n"
q_blocks = re.split(q_pattern, src)
i = 1
while i < len(q_blocks):
    header = q_blocks[i]
    num_str = q_blocks[i+1]
    num = float(num_str) if "." in num_str else int(num_str)
    body = q_blocks[i+2] if i+2 < len(q_blocks) else ""
    body = re.split(r"\n(?=# [^#])", body)[0]
    title_match = re.match(r"## JAUTĀJUMS #[\d\.]+ · (.+)", header)
    title = title_match.group(1).strip() if title_match else ""
    priority = title.count("⭐")
    title_clean = re.sub(r"⭐+", "", title).strip()
    title_clean = re.sub(r"\(.*?\)", "", title_clean).strip()
    dkods_m = re.search(r"\*\*D-kods:\*\* ([^\n]+)", body)
    merkis_m = re.search(r"\*\*Mērķis:\*\* ([^\n]+)", body)
    phrases = re.findall(r"^> \*\"([^\"]+)\"\*", body, re.MULTILINE)
    # Mark Hope Break specially
    is_hope_break = "HOPE BREAK" in title.upper() or "CERĪBA NAV SISTĒMA" in title.upper()
    questions.append({
        "num": num,
        "num_display": num_str,
        "title": title_clean,
        "priority": priority,
        "dkods": dkods_m.group(1).strip() if dkods_m else "",
        "merkis": merkis_m.group(1).strip() if merkis_m else "",
        "phrases": phrases,
        "raw": body.strip(),
        "is_hope_break": is_hope_break,
        "layer": "CORE"
    })
    i += 3

# Sort by num
questions.sort(key=lambda q: float(q["num"]))

# 2) Mezgli — 14 mezgli + Hope Break (13.6.5)
mezgli_section = re.search(r"# XIII\. V8 MOLECULAR.+?(?=\n# XIV\.)", src, re.DOTALL)
mezgli = []
if mezgli_section:
    body = mezgli_section.group(0)
    sections = re.split(r"\n## 13\.\d+(?:\.\d+)? · ", body)[1:]
    for sec in sections:
        first_line, rest = sec.split("\n", 1)
        rm = re.match(r"([A-ZĀĒĪŌŪČĢĶĻŅŠŽ /\-]+?)(?:\s*/\s*[A-ZĀĒĪŌŪČĢĶĻŅŠŽ ]+)?(?:\s*\(([^)]+)\))?\s*(?:⭐+\s*[A-Z0-9 \-]*)?$", first_line.strip())
        name = first_line.strip().split("(")[0].split("⭐")[0].strip()
        q_range_m = re.search(r"\(([^)]+)\)", first_line)
        q_range = q_range_m.group(1) if q_range_m else ""
        layers = {}
        for line in rest.split("\n"):
            m = re.match(r"\| \*\*([^*]+)\*\* \| (.+?) \|\s*$", line)
            if m:
                key = m.group(1).strip().lower().replace(" ", "_")
                layers[key] = m.group(2).strip()
        if layers:
            is_hope_break = "HOPE" in name.upper() or "CERĪBA" in name.upper()
            mezgli.append({"name": name, "q_range": q_range, "layers": layers, "is_hope_break": is_hope_break})

# 3) Client types
ct_section = re.search(r"# XIV\. CLIENT TYPE.+?(?=\n# XV\.)", src, re.DOTALL)
client_types = []
if ct_section:
    for m in re.finditer(r"## 14\.\d+ · ([A-ZĀĒĪŌŪČĢĶĻŅŠŽ\- /]+)\n\n(.+?)(?=\n## 14\.|\n# )", ct_section.group(0), re.DOTALL):
        name = m.group(1).strip()
        if "DETEKTORS" in name or "NOTEIKUMS" in name:
            continue
        client_types.append({"name": name, "raw": m.group(2).strip()})

# 4) Response trees
rt_section = re.search(r"# XV\. RESPONSE TREES.+?(?=\n# XVI\.)", src, re.DOTALL)
trees = []
if rt_section:
    for m in re.finditer(r'## 15\.\d+ · "([^"]+)"\n\n(.+?)(?=\n## 15\.|\n# )', rt_section.group(0), re.DOTALL):
        trees.append({"trigger": m.group(1), "raw": m.group(2).strip()})

# 5) Elite rules
er_section = re.search(r"# XIX\. PREMIUM.+?(?=\n# XX\.)", src, re.DOTALL)
elite_rules = []
if er_section:
    for m in re.finditer(r"\| \*\*(\d+)\*\* \| \*\*([^*]+)\*\* \| ([^|]+) \|", er_section.group(0)):
        elite_rules.append({"num": int(m.group(1)), "rule": m.group(2).strip(), "explain": m.group(3).strip()})

# 6) Reset phrases
reset_section = re.search(r"## 17\.12.+?(?=\n## |\n# )", src, re.DOTALL)
reset_phrases = []
if reset_section:
    reset_phrases = re.findall(r"- \*\"([^\"]+)\"\*", reset_section.group(0))

# 7) Elite weapons by client type
ct_full = re.search(r"# XIV\. CLIENT TYPE.+?(?=\n# XV\.)", src, re.DOTALL)
ct_weapons = {}
if ct_full:
    for m in re.finditer(r"## 14\.\d+ · ([A-ZĀĒĪŌŪČĢĶĻŅŠŽ\- /]+)\n\n.+?\*\*Elite ieroči:\*\*\n((?:- \*\"[^\"]+\"\*\n)+)", ct_full.group(0), re.DOTALL):
        weapons = re.findall(r"- \*\"([^\"]+)\"\*", m.group(2))
        ct_weapons[m.group(1).strip()] = weapons

# 8) Visual Carrier — 9 metaphors (NEW V14.1)
vc_section = re.search(r"# XX\. PRESENTATION CARRIER.+?(?=\n# XXI\.)", src, re.DOTALL)
visual_carrier = []
if vc_section:
    body = vc_section.group(0)
    # Parse metaphor table
    for m in re.finditer(r"\| (\d) \| \*\*([A-ZĀĒĪŌŪČĢĶĻŅŠŽ ]+)\*\*[^|]* \| ([^|]+) \| ([^|]+) \| ([^|]+) \|", body):
        visual_carrier.append({
            "num": int(m.group(1)),
            "name": m.group(2).strip(),
            "represents": m.group(3).strip(),
            "node": m.group(4).strip(),
            "when": m.group(5).strip()
        })
    # Extract metaphor phrases
    phrases = {}
    for m in re.finditer(r"\*\*([A-ZĀĒĪŌŪČĢĶĻŅŠŽ]+):\*\*\n> \*\"([^\"]+)\"\*", body):
        phrases[m.group(1).strip()] = m.group(2).strip()
    if visual_carrier:
        for vc in visual_carrier:
            key = vc["name"].split()[0]
            if key in phrases:
                vc["phrase"] = phrases[key]

# 9) Layers (V13.1 6-layer discipline) — NEW
layers_section = re.search(r"## 0\. V13 STRUKTURĀLĀ DISCIPLĪNA.+?(?=\n## I\.)", src, re.DOTALL)
layers_def = []
if layers_section:
    for m in re.finditer(r"\| \*\*\d+\*\* \| \*\*([A-Z /\-]+)\*\* \| ([^|]+) \| ([^|]+) \|", layers_section.group(0)):
        layers_def.append({
            "name": m.group(1).strip(),
            "contains": m.group(2).strip(),
            "when": m.group(3).strip()
        })

# 10) Prompt core laws
prompt_core = []
pc_match = re.search(r"### Prompt core likumi.+?(?=\n---)", src, re.DOTALL)
if pc_match:
    for m in re.finditer(r"\d+\. \*\*([^*]+)\*\* — (.+)", pc_match.group(0)):
        prompt_core.append({"law": m.group(1).strip(), "explain": m.group(2).strip()})

data = {
    "version": "V14.1 LV-V13-COMPLIANT",
    "date": "2026-04-25",
    "questions": questions,
    "mezgli": mezgli,
    "client_types": client_types,
    "client_weapons": ct_weapons,
    "response_trees": trees,
    "elite_rules": elite_rules,
    "reset_phrases": reset_phrases,
    "visual_carrier": visual_carrier,
    "layers": layers_def,
    "prompt_core": prompt_core,
}

out = pathlib.Path("/home/ubuntu/salesengine/app/data.json")
out.write_text(json.dumps(data, ensure_ascii=False, indent=2))
# Also generate data.js (used by index.html)
js_out = pathlib.Path("/home/ubuntu/salesengine/app/data.js")
js_out.write_text("const DATA = " + json.dumps(data, ensure_ascii=False, indent=2) + ";")
print(f"Extracted: {len(questions)} questions, {len(mezgli)} mezgli, {len(client_types)} types, {len(trees)} trees, {len(elite_rules)} rules")
print(f"V14.1 NEW: {len(visual_carrier)} visual carriers, {len(layers_def)} layers, {len(prompt_core)} prompt-core laws")
print(f"Hope Break questions: {sum(1 for q in questions if q.get('is_hope_break'))}")
print(f"Hope Break mezgli: {sum(1 for m in mezgli if m.get('is_hope_break'))}")
print(f"File: {out} ({out.stat().st_size} bytes)")
