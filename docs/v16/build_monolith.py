"""V17 MASTER MONOLĪTS — viena dzīva organisma grāmata.

Structure: 8 akti + epilogs. Q1-Q40 spine ar visiem slāņiem sapītiem.
Nav "Daļa I/II/III" sajūtas. Lasās kā viena filma.
"""
from pathlib import Path
import re
from weasyprint import HTML

ROOT = Path('/home/ubuntu/v16-build')
BP = ROOT / 'blueprints'
V14 = Path('/home/ubuntu/salesengine-repo/docs/v14.1/LV_MASTER_SCRIPT_V14_1.md')
V15 = Path('/home/ubuntu/v15-build/V15_PREMIUM_BOOK.md')
OUT = ROOT / 'final'
OUT.mkdir(parents=True, exist_ok=True)

NAVY = '#0d3b66'
GOLD = '#d97706'
GOLD_LIGHT = '#fbbf24'
PAPER = '#fffaf0'
INK = '#16243a'
RED = '#dc2626'
GREEN = '#059669'
TEAL = '#0891b2'
PURPLE = '#7c3aed'

# ==============================================================
# CSS — vienota plūsma, ne sectioning
# ==============================================================
CSS_TEXT = """
@page {
  size: A4 portrait;
  margin: 22mm 18mm 22mm 18mm;
  @bottom-center {
    content: counter(page);
    font-family: Georgia, serif;
    font-size: 9pt;
    color: #0d3b66;
  }
  @top-center {
    content: string(running-head);
    font-family: Georgia, serif;
    font-size: 8.5pt;
    color: #d97706;
    font-style: italic;
    letter-spacing: 1pt;
  }
}

@page :first {
  margin: 0;
  @bottom-center { content: ""; }
  @top-center { content: ""; }
}

@page no-header {
  margin: 22mm 18mm 22mm 18mm;
  @bottom-center {
    content: counter(page);
    font-family: Georgia, serif;
    font-size: 9pt;
    color: #0d3b66;
  }
  @top-center { content: ""; }
}

* { box-sizing: border-box; }

html, body {
  font-family: Georgia, "DejaVu Serif", serif;
  font-size: 10.5pt;
  line-height: 1.6;
  color: #16243a;
  background: #fffaf0;
}

/* ======== COVER ======== */
.cover {
  page: no-header;
  page-break-after: always;
  width: 100%;
  height: 297mm;
  margin: 0;
  padding: 0;
}
.cover svg, .cover img { width: 100%; height: 297mm; display: block; }

/* ======== FRONT MATTER ======== */
.front-matter {
  page: no-header;
  page-break-after: always;
  text-align: center;
  padding: 60mm 30mm;
}
.front-matter h2 {
  font-size: 16pt;
  color: #d97706;
  letter-spacing: 4pt;
  margin: 0 0 8mm 0;
}

/* ======== MOTTO BLOCK ======== */
.manifesto {
  text-align: center;
  border: 3px double #d97706;
  padding: 8mm 10mm;
  margin: 6mm 0;
  background: linear-gradient(to bottom, #fdf6e3, #fffaf0);
  page-break-inside: avoid;
}
.manifesto-title {
  font-size: 11pt;
  letter-spacing: 4pt;
  color: #d97706;
  font-weight: bold;
  margin-bottom: 3mm;
}
.manifesto-body {
  font-size: 12pt;
  font-style: italic;
  color: #0d3b66;
  line-height: 1.55;
}

/* ======== AKTS BANNER (NOT a full-page divider) ======== */
.akts-banner {
  string-set: running-head content();
  page-break-before: always;
  text-align: center;
  margin: 0 0 8mm 0;
  padding: 8mm 0 6mm 0;
  border-top: 1px solid #d97706;
  border-bottom: 3px solid #d97706;
  position: relative;
}
.akts-banner::before {
  content: "";
  position: absolute;
  top: -2mm; left: 50%;
  width: 8mm; height: 8mm;
  background: #fffaf0 url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Ccircle cx='16' cy='16' r='6' fill='%23d97706'/%3E%3Ccircle cx='16' cy='16' r='3' fill='%23fbbf24'/%3E%3C/svg%3E") center/contain no-repeat;
  transform: translateX(-50%);
}
.akts-label {
  font-size: 10pt;
  letter-spacing: 6pt;
  color: #d97706;
  font-weight: bold;
  margin: 0 0 2mm 0;
}
.akts-title {
  font-size: 24pt;
  color: #0d3b66;
  font-weight: bold;
  margin: 0;
  font-family: Georgia, serif;
}
.akts-subtitle {
  font-size: 11pt;
  color: #16243a;
  font-style: italic;
  margin: 2mm 30mm 0 30mm;
  opacity: 0.85;
}

/* ======== HEADERS ======== */
h2 {
  font-size: 16pt;
  color: #0d3b66;
  margin: 7mm 0 3mm 0;
  border-left: 4px solid #d97706;
  padding-left: 4mm;
  page-break-after: avoid;
}
h3 {
  font-size: 13pt;
  color: #d97706;
  margin: 5mm 0 2mm 0;
  page-break-after: avoid;
}
h4 {
  font-size: 11pt;
  color: #16243a;
  margin: 3mm 0 1mm 0;
  font-style: italic;
  page-break-after: avoid;
}

/* ======== PARAGRAPHS ======== */
p { margin: 2mm 0; text-align: justify; }
ul, ol { margin: 2mm 0; padding-left: 8mm; }
li { margin: 1mm 0; }

/* Drop cap kā subtle effect */
.akts-opening::first-letter {
  font-family: Georgia, serif;
  font-size: 28pt;
  font-weight: bold;
  color: #d97706;
}

/* ======== TABLES ======== */
table {
  border-collapse: collapse;
  width: 100%;
  margin: 4mm 0;
  font-size: 9.5pt;
  page-break-inside: avoid;
}
th {
  background: #0d3b66;
  color: #fbbf24;
  padding: 2mm 3mm;
  text-align: left;
  font-size: 10pt;
  border: 1px solid #0a2747;
}
td {
  padding: 2mm 3mm;
  border: 1px solid #d4c5a8;
  vertical-align: top;
}
tr:nth-child(even) td { background: #fdf6e3; }

/* ======== BLOCKQUOTES (verbatim scripts) ======== */
blockquote {
  background: linear-gradient(to right, #fdf6e3 0%, #fffaf0 100%);
  border-left: 5px solid #d97706;
  padding: 4mm 6mm;
  margin: 4mm 0;
  font-style: italic;
  font-family: Georgia, serif;
  font-size: 11pt;
  color: #0d3b66;
  page-break-inside: avoid;
  position: relative;
}

/* ======== CODE / EMPHASIS ======== */
code {
  background: #fdf6e3;
  border: 1px solid #d4c5a8;
  padding: 0.5mm 1.5mm;
  border-radius: 2px;
  font-family: "DejaVu Sans Mono", monospace;
  font-size: 9pt;
  color: #b45309;
}
strong { color: #0d3b66; font-weight: bold; }
em { color: #b45309; font-style: italic; }

/* ======== CALLOUTS ======== */
.callout {
  border-left: 5px solid;
  padding: 4mm 5mm;
  margin: 4mm 0;
  border-radius: 2px;
  page-break-inside: avoid;
  font-size: 10pt;
}
.callout-title {
  font-weight: bold;
  font-size: 10.5pt;
  margin-bottom: 1.5mm;
  text-transform: uppercase;
  letter-spacing: 1pt;
}
.callout-warning { background: #fee2e2; border-color: #dc2626; }
.callout-warning .callout-title { color: #991b1b; }
.callout-tip { background: #fef3c7; border-color: #d97706; }
.callout-tip .callout-title { color: #b45309; }
.callout-success { background: #d1fae5; border-color: #059669; }
.callout-success .callout-title { color: #065f46; }
.callout-info { background: #dbeafe; border-color: #0d3b66; }
.callout-info .callout-title { color: #0d3b66; }
.callout-script { background: #f3e8ff; border-color: #7c3aed; }
.callout-script .callout-title { color: #5b21b6; }

/* ======== PULL QUOTE ======== */
.pull-quote {
  font-family: Georgia, serif;
  font-style: italic;
  font-size: 13pt;
  color: #0d3b66;
  text-align: center;
  margin: 7mm 8mm;
  padding: 4mm 6mm;
  border-top: 2px solid #d97706;
  border-bottom: 2px solid #d97706;
  position: relative;
  page-break-inside: avoid;
  line-height: 1.45;
}
.pull-quote::before {
  content: "";
  position: absolute;
  top: -3mm;
  left: 50%;
  transform: translateX(-50%);
  width: 16mm;
  height: 6mm;
  background: #fffaf0 url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 80 24'%3E%3Cpath d='M 0 12 L 32 12 M 48 12 L 80 12' stroke='%23d97706' stroke-width='1'/%3E%3Ccircle cx='40' cy='12' r='4' fill='%23d97706'/%3E%3C/svg%3E") center/contain no-repeat;
}
.pull-quote .attribution {
  display: block;
  font-style: normal;
  font-size: 9.5pt;
  color: #d97706;
  margin-top: 2mm;
  letter-spacing: 1pt;
}

/* ======== Q-CARD (sapīts ar narratīvu, ne dominant) ======== */
.q-card {
  background: white;
  border: 1.5px solid #0d3b66;
  border-radius: 3mm;
  padding: 4mm 5mm;
  margin: 4mm 0;
  page-break-inside: avoid;
}
.q-card.gate {
  border-color: #d97706;
  border-width: 2.5px;
  box-shadow: 0 0 0 1px #fef3c7;
}
.q-card.load-bearing {
  border-color: #dc2626;
  border-width: 2.5px;
  box-shadow: 0 0 0 1px #fee2e2;
}
.q-card .q-num {
  display: inline-block;
  background: #0d3b66;
  color: #fbbf24;
  font-weight: bold;
  font-size: 11pt;
  padding: 0.5mm 2.5mm;
  border-radius: 2px;
  margin-right: 2mm;
}
.q-card.gate .q-num { background: #d97706; color: white; }
.q-card.load-bearing .q-num { background: #dc2626; color: white; }
.q-card .q-title {
  display: inline;
  font-size: 12pt;
  font-weight: bold;
  color: #0d3b66;
}
.q-card.gate .q-title::after {
  content: " · VĀRTI";
  color: #d97706;
  font-size: 9pt;
  letter-spacing: 1pt;
}
.q-card.load-bearing .q-title::after {
  content: " · LOAD-BEARING";
  color: #dc2626;
  font-size: 9pt;
  letter-spacing: 1pt;
}

/* ======== INLINE BLUEPRINT (sapīts ar text, ne separate page) ======== */
.inline-bp {
  margin: 5mm 0;
  text-align: center;
  page-break-inside: avoid;
}
.inline-bp img {
  max-width: 95%;
  max-height: 130mm;
}
.inline-bp .bp-caption {
  font-style: italic;
  color: #0d3b66;
  margin-top: 2mm;
  font-size: 9.5pt;
}

/* ======== Full-page blueprint (only sometimes) ======== */
.full-bp {
  page-break-before: always;
  page-break-after: always;
  text-align: center;
  padding: 0;
}
.full-bp img {
  max-width: 100%;
  max-height: 250mm;
}
.full-bp .bp-caption {
  font-style: italic;
  color: #0d3b66;
  margin-top: 4mm;
  font-size: 10pt;
}

/* ======== TOC ======== */
.toc {
  page: no-header;
  page-break-after: always;
}
.toc h1 {
  font-size: 28pt;
  color: #0d3b66;
  text-align: center;
  margin: 0 0 4mm 0;
  letter-spacing: 4pt;
}
.toc-subtitle {
  text-align: center;
  font-style: italic;
  color: #d97706;
  margin: 0 0 10mm 0;
  font-size: 11pt;
}
.toc table { width: 100%; border: none; }
.toc th { display: none; }
.toc td { border: none; padding: 2mm 0; font-size: 11pt; vertical-align: top; }
.toc tr:nth-child(even) td { background: transparent; }
.toc-num {
  font-weight: bold;
  color: #d97706;
  width: 22mm;
  font-family: Georgia, serif;
  font-size: 12pt;
}
.toc-title { font-weight: bold; color: #0d3b66; }
.toc-desc { font-size: 9.5pt; color: #16243a; font-style: italic; }
.toc-page {
  width: 14mm;
  text-align: right;
  font-family: Georgia, serif;
  color: #d97706;
  font-weight: bold;
  font-size: 12pt;
}
.toc-page a::after {
  content: target-counter(attr(href), page);
  color: #d97706;
}
.toc-page a {
  color: transparent !important;
}

/* ======== INTERLUDE / TRANSITION (between acts) ======== */
.interlude {
  text-align: center;
  margin: 8mm 0;
  padding: 4mm 0;
  font-style: italic;
  color: #d97706;
  font-size: 11pt;
  border-top: 0.5px solid #d97706;
  border-bottom: 0.5px solid #d97706;
}
.interlude::before {
  content: "\2756";
  display: block;
  margin-bottom: 2mm;
  color: #d97706;
}

/* ======== HR ornaments ======== */
hr {
  border: none;
  border-top: 1px solid #d4c5a8;
  margin: 4mm 0;
}
hr.fancy {
  border: none;
  text-align: center;
  margin: 6mm 0;
  height: 8mm;
  background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 8'%3E%3Cpath d='M 0 4 L 35 4 M 65 4 L 100 4' stroke='%23d97706' stroke-width='0.5'/%3E%3Ccircle cx='50' cy='4' r='2.5' fill='%23d97706'/%3E%3Ccircle cx='42' cy='4' r='1' fill='%23d97706'/%3E%3Ccircle cx='58' cy='4' r='1' fill='%23d97706'/%3E%3C/svg%3E") center/contain no-repeat;
}

/* ======== BADGES ======== */
.badge {
  display: inline-block;
  font-size: 8pt;
  padding: 0.5mm 2mm;
  border-radius: 2px;
  font-weight: bold;
  letter-spacing: 0.5pt;
  vertical-align: middle;
}
.badge-lv { background: #d1fae5; color: #065f46; }
.badge-en { background: #fef3c7; color: #b45309; }
.badge-hyp { background: #fee2e2; color: #991b1b; }
.badge-gate { background: #d97706; color: white; }
.badge-load { background: #dc2626; color: white; }

/* ======== COLUMNS ======== */
.two-col {
  column-count: 2;
  column-gap: 8mm;
  column-rule: 0.5pt solid #d4c5a8;
}

/* ======== FIRST-PARAGRAPH NARRATIVE OPENER ======== */
p.lead {
  font-size: 12pt;
  font-style: italic;
  color: #0d3b66;
  text-align: justify;
  margin: 4mm 0 4mm 0;
  line-height: 1.55;
}
"""

# ==============================================================
# Helpers
# ==============================================================
def svg_inline(name):
    return (BP / f'{name}.svg').read_text(encoding='utf-8')

def bp_img(name, full=False, caption=None):
    p = BP / f'{name}.png'
    cls = 'full-bp' if full else 'inline-bp'
    cap_html = f'<p class="bp-caption">{caption}</p>' if caption else ''
    return f'<div class="{cls}"><img src="file://{p}" alt="{name}"/>{cap_html}</div>'

# ==============================================================
# Read V14.1 source
# ==============================================================
v14_text = V14.read_text(encoding='utf-8')
q_sections = {}
for sec in re.split(r'(?=^## JAUTĀJUMS #)', v14_text, flags=re.M)[1:]:
    m = re.match(r'## JAUTĀJUMS #(\d+(?:\.\d+)?)', sec)
    if m:
        q_sections[m.group(1)] = sec

def q_card(q_num, gate=False, load_bearing=False):
    """Render a Q1-Q40 card with full content."""
    if q_num not in q_sections:
        return f'<div class="q-card"><span class="q-num">Q{q_num}</span> <span class="q-title">[content missing]</span></div>'
    raw = q_sections[q_num]
    m = re.match(r'## JAUTĀJUMS #([\d.]+) · ([^\n]+)', raw)
    title = m.group(2).strip() if m else q_num
    body = raw[m.end():].strip() if m else raw
    
    # Truncate to keep readable (full content from V14.1)
    body = body[:2400]
    body_html = simple_md_to_html(body)
    
    classes = ['q-card']
    if load_bearing: classes.append('load-bearing')
    elif gate: classes.append('gate')
    
    return f'''
<div class="{' '.join(classes)}">
  <span class="q-num">Q{q_num}</span><span class="q-title">{title}</span>
  <div style="margin-top: 2mm; font-size: 10pt;">{body_html}</div>
</div>
'''

def simple_md_to_html(md):
    h = md
    h = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', h)
    h = re.sub(r'(?<!\*)\*([^\*\n]+?)\*(?!\*)', r'<em>\1</em>', h)
    h = re.sub(r'`([^`]+)`', r'<code>\1</code>', h)
    h = re.sub(r'^> (.+)$', r'<blockquote>\1</blockquote>', h, flags=re.M)
    h = re.sub(r'^### (.+)$', r'<h4>\1</h4>', h, flags=re.M)
    h = re.sub(r'^- (.+)$', r'<li>\1</li>', h, flags=re.M)
    h = re.sub(r'(<li>.+</li>\n?)+', lambda m: '<ul>' + m.group(0) + '</ul>', h)
    # Tables (simple)
    lines = h.split('\n')
    out = []
    in_table = False
    for line in lines:
        if line.strip().startswith('|'):
            if not in_table:
                out.append('<table>')
                in_table = True
            cells = [c.strip() for c in line.strip().strip('|').split('|')]
            if all(set(c) <= set('-: ') for c in cells):
                continue
            tag = 'th' if len(out) >= 1 and out[-1] == '<table>' else 'td'
            row = ''.join(f'<{tag}>{c}</{tag}>' for c in cells)
            out.append(f'<tr>{row}</tr>')
        else:
            if in_table:
                out.append('</table>')
                in_table = False
            out.append(line)
    if in_table:
        out.append('</table>')
    h = '\n'.join(out)
    paragraphs = re.split(r'\n\s*\n', h)
    result = []
    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
        if p.startswith('<') and not p.startswith('<em>') and not p.startswith('<strong>'):
            result.append(p)
        else:
            result.append(f'<p>{p}</p>')
    return '\n'.join(result)


def akts_banner(num, label, title, subtitle):
    anchor = f'akts-{num}'.replace(' ', '-').replace('—', 'epilogs')
    return f'''
<div class="akts-banner" id="{anchor}">
  <div class="akts-label">{label}</div>
  <h1 class="akts-title" style="border: none; margin: 0; padding: 0;">{title}</h1>
  <div class="akts-subtitle">{subtitle}</div>
</div>
'''

# ==============================================================
# COMPOSE THE BOOK — vienota plūsma
# ==============================================================
parts = []

# ---- COVER (custom Monolith cover) ----
COVER_SVG = '''
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 595 842" preserveAspectRatio="xMidYMid meet">
  <rect width="595" height="842" fill="#0d3b66"/>
  <rect x="22" y="22" width="551" height="798" fill="none" stroke="#d97706" stroke-width="1.5"/>
  <rect x="32" y="32" width="531" height="778" fill="none" stroke="#d97706" stroke-width="0.4" stroke-dasharray="2,2"/>

  <!-- top brand -->
  <text x="297.5" y="120" font-family="Georgia, serif" font-size="14" font-weight="bold" fill="#fbbf24" text-anchor="middle" letter-spacing="6">SALESENGINE</text>
  <line x1="220" y1="135" x2="375" y2="135" stroke="#d97706" stroke-width="1"/>

  <!-- Hero title -->
  <text x="297.5" y="245" font-family="Georgia, serif" font-size="78" font-weight="bold" fill="#fbbf24" text-anchor="middle" letter-spacing="4">MASTER</text>
  <text x="297.5" y="320" font-family="Georgia, serif" font-size="78" font-weight="bold" fill="#fbbf24" text-anchor="middle" letter-spacing="4">MONOLĪTS</text>

  <line x1="180" y1="355" x2="415" y2="355" stroke="#d97706" stroke-width="0.8"/>
  <text x="297.5" y="385" font-family="Georgia, serif" font-size="13" fill="#fffaf0" text-anchor="middle" font-style="italic">Viens organisma · Viena līnija · Viens Flow</text>
  <line x1="180" y1="405" x2="415" y2="405" stroke="#d97706" stroke-width="0.8"/>

  <!-- Center medallion · Q1-Q40 ring -->
  <g transform="translate(297.5, 540)">
    <circle r="78" fill="none" stroke="#d97706" stroke-width="0.8"/>
    <circle r="60" fill="none" stroke="#fbbf24" stroke-width="0.4" stroke-dasharray="3,3"/>
    <circle r="42" fill="#0a2747" stroke="#d97706" stroke-width="1.2"/>
    <text x="0" y="-5" font-family="Georgia, serif" font-size="18" font-weight="bold" fill="#fbbf24" text-anchor="middle">Q21.5</text>
    <text x="0" y="14" font-family="Georgia, serif" font-size="9" fill="#fbbf24" text-anchor="middle">HOPE BREAK</text>
    <!-- Q markers around -->
    <text x="0" y="-72" font-family="Georgia, serif" font-size="10" font-weight="bold" fill="#fbbf24" text-anchor="middle">Q1</text>
    <text x="65" y="-30" font-family="Georgia, serif" font-size="9" fill="#fbbf24" text-anchor="middle">Q11</text>
    <text x="68" y="22" font-family="Georgia, serif" font-size="9" fill="#fbbf24" text-anchor="middle">Q26</text>
    <text x="0" y="80" font-family="Georgia, serif" font-size="10" font-weight="bold" fill="#fbbf24" text-anchor="middle">Q40</text>
    <text x="-68" y="22" font-family="Georgia, serif" font-size="9" fill="#fbbf24" text-anchor="middle">Q32</text>
    <text x="-65" y="-30" font-family="Georgia, serif" font-size="9" fill="#fbbf24" text-anchor="middle">Q3</text>
    <!-- 5 vārti dots -->
    <circle cx="0" cy="-78" r="3.5" fill="#d97706"/>
    <circle cx="74" cy="-25" r="3.5" fill="#d97706"/>
    <circle cx="74" cy="25" r="3.5" fill="#d97706"/>
    <circle cx="0" cy="78" r="3.5" fill="#d97706"/>
    <circle cx="-74" cy="-25" r="3.5" fill="#d97706"/>
  </g>

  <!-- Author -->
  <text x="297.5" y="685" font-family="Georgia, serif" font-size="13" fill="#fbbf24" text-anchor="middle" letter-spacing="3">LAURIS LEITĀNS</text>
  <text x="297.5" y="705" font-family="Georgia, serif" font-size="10" fill="#fffaf0" text-anchor="middle">Sharpify.io · 2026</text>

  <!-- 3 principi -->
  <text x="297.5" y="745" font-family="Georgia, serif" font-size="9.5" fill="#fbbf24" text-anchor="middle" font-style="italic">"Cerība nav sistēma."</text>
  <text x="297.5" y="760" font-family="Georgia, serif" font-size="9.5" fill="#fbbf24" text-anchor="middle" font-style="italic">"Es nestrādāju ar visiem."</text>
  <text x="297.5" y="775" font-family="Georgia, serif" font-size="9.5" fill="#fbbf24" text-anchor="middle" font-style="italic">"Es nepārdošu — diagnozēju."</text>

  <!-- Bottom -->
  <line x1="180" y1="797" x2="415" y2="797" stroke="#d97706" stroke-width="0.5"/>
  <text x="297.5" y="810" font-family="Georgia, serif" font-size="8" fill="#fbbf24" text-anchor="middle" letter-spacing="3">V14.1 KANONS · V15 DZIĻUMS · V16 DISCIPLĪNA</text>
</svg>
'''
parts.append(f'<div class="cover">{COVER_SVG}</div>')

# ---- FRONT MATTER ----
parts.append(f'''
<div class="front-matter">
  <h2>SALESENGINE</h2>
  <p style="font-size: 32pt; color: {NAVY}; font-weight: bold; margin: 8mm 0;">MASTER MONOLĪTS</p>
  <p style="font-style: italic; color: {GOLD}; font-size: 13pt; margin: 0 0 14mm 0;">Viens dzīvs organisms · Viena līnija · Viens Flow</p>
  <div style="border-top: 1px solid {GOLD}; border-bottom: 1px solid {GOLD}; padding: 6mm 0; margin: 14mm 0; font-size: 10pt;">
    <p style="margin: 1mm 0;">V14.1 kanons + V15 dziļums + V16 disciplīna</p>
    <p style="margin: 1mm 0;">Viena grāmata. Lasās kā filma. Q1 līdz Q40 ar visu sapītu iekšā.</p>
    <p style="margin: 1mm 0;">8 akti + epilogs · 16 oriģinālas LV blueprint shēmas embedētas inline</p>
  </div>
  <p style="font-style: italic; color: {INK}; font-size: 12pt; margin: 14mm 0;">Lauris Leitāns<br/>Sharpify.io · 2026</p>
</div>
''')

# ---- MOTTO ----
parts.append(f'''
<div class="front-matter" style="padding-top: 70mm;">
  <div class="manifesto" style="margin: 0 12mm;">
    <div class="manifesto-title">3 PRINCIPI · GRĀMATAS PAMATS</div>
    <div class="manifesto-body">
      <p>"Cerība nav sistēma."</p>
      <p>"Es nestrādāju ar visiem."</p>
      <p>"Es nepārdošu — diagnozēju."</p>
    </div>
  </div>
  <p style="font-style: italic; color: {GOLD}; margin: 16mm 0; font-size: 11pt;">
    Šī nav teorijas grāmata. Šī ir <strong>viena nepārtraukta pārdošanas zvanu plūsma</strong> — no brīža pirms tālrunis ieskan līdz brīdim pēc Q40 close. Visi V15 ieroči, viss V16 disciplīnas slānis ir <em>sapīts</em> šajā stāstā tieši tur, kur tev tas zvanā vajadzīgs.
  </p>
</div>
''')

# ---- TOC — vienkāršs, 8 akti ----
toc_data = [
    ('I',   'Pirms tālrunis ieskan',     'Operatora identitāte · pre-call rituāls · 3 māju struktūra', 'akts-I'),
    ('II',  'Pirmie 6 minūtes',          'Q1-Q7 · MICE motors · Tonalitātes 5 balsis · Frame', 'akts-II'),
    ('III', 'Karte',                     'Q8-Q20 · Mikro-jā cilpa · GAP €N · Laika dimensija', 'akts-III'),
    ('IV',  'Pārtraukums',               'Q21-Q21.5 · Hope Fog Shatterer · Lēmumu algoritms · KLĪMAKSS', 'akts-IV'),
    ('V',   'Pīlāri',                    'Q22-Q28 · Investora rāmis · 3 pīlāri · Manipulācija vs Inspirācija · 6 arhetipi', 'akts-V'),
    ('VI',  'Patiesība',                 'Q29-Q32 · Klusais slēgums 8-15s · Cenas brīdis', 'akts-VI'),
    ('VII', 'Iebildumi',                 'Q33-Q40 · CARE · Voss "Nē" · Takeaway · Close', 'akts-VII'),
    ('VIII','Pēc zvana',                 'Post-call rituāls · L1-L5 ceļš · Anti-Overload gudrība · Fast-Start 7d', 'akts-VIII'),
    ('—',   'Epilogs · LV-native tabula · Glosārijs', 'Validācija · vārdnīca · audit', 'akts-epilogs'),
]

toc_html = '<div class="toc"><h1>SATURS</h1><p class="toc-subtitle">8 akti · viena nepārtraukta pārdošanas zvanu plūsma</p><table>'
for num, title, desc, anchor in toc_data:
    toc_html += f'<tr><td class="toc-num">AKTS {num}.</td><td><div class="toc-title"><a href="#{anchor}" style="color: inherit; text-decoration: none;">{title}</a></div><div class="toc-desc">{desc}</div></td><td class="toc-page"><a href="#{anchor}" style="color: inherit; text-decoration: none;">·</a></td></tr>'
toc_html += '</table></div>'
parts.append(toc_html)

# =============================================================
# AKTS I · "Pirms tālrunis ieskan"
# =============================================================
parts.append(akts_banner('I', 'AKTS I', 'Pirms tālrunis ieskan', 'Operatora identitāte · pre-call rituāls · 3 māju struktūra'))

parts.append(f'''
<p class="lead akts-opening">Pārdošanas zvans nav notikums, kas sākas, kad tālrunis ieskan. Tas sākas <strong>90 sekundes pirms</strong>. Tas, kas notiek tajos 90 sek, izšķir, vai operators iegājīs zvanā kā <em>arhitekts</em> vai kā <em>pārdevējs, kurš lūdz</em>.</p>

<p>Šī grāmata sākas tieši tur — pirms tu paņem tālruni. Ne tāpēc, ka pre-call ir "papildus solis", bet tāpēc, ka <strong>ja tas nav, viss pārējais nedarbojas</strong>. Q1 sveiciens sausa balsī, kura tikko izturēja stresu, ir cita nozīme nekā Q1 sveiciens balsī, kura izgāja Power Pose 15 sekundes iepriekš.</p>

<h2>Tu neesi pārdevējs — tu esi diagnostikas instruments</h2>

<p>Pirms iesim tālāk, fiksēsim šo. Šī grāmata ir uzbūvēta uz vienu pieņēmumu: <strong>operators nav pārliecinātājs</strong>. Operators ir <em>diagnostikas instruments</em>. Pārdevējs runā vairāk; diagnostikas instruments uzdod jautājumus un klusē. Pārdevējs cenšas pierādīt vērtību; instruments to atklāj.</p>

<p>Klients vienmēr atklāj: pārdevējs lūdzas vai operators sistēmā. Ar pirmajām 30 sekundēm. Ar tonalitāti. Ar to, kā tu reaģē uz "cik tas izmaksā?" agri (Q3 priekšlaicīgi).</p>

<div class="pull-quote">
Es nestrādāju ar visiem. Es nepārdošu — es diagnozēju.
<span class="attribution">— Operatora pamatprincips</span>
</div>

<h2>3 māju struktūra · paslēpta arhitektūra</h2>

<p>Lai tev neizjauktu plūsmu, šī grāmata tev nepasaka katru reizi: "tagad mēs runājam par CORK māju" vai "tagad par ARSENAL". Bet tu zini — iekšēji visi šie elementi pieder vienai no <strong>6 mājām</strong>:</p>

<ul>
<li><strong>CORE</strong> — Q1-Q40 obligātā ķēde. Tas ir <em>kas vienmēr notiek</em>.</li>
<li><strong>CORK</strong> — 1-lapa kabatas slānis. Tas ir <em>kas tev jāredz tūlīt</em>.</li>
<li><strong>ARSENAL</strong> — situatīvi mezgli (Tonalitāte, Mikro-jā, Klusais slēgums...). Tas ir <em>ko tu izmanto, ja vajag</em>.</li>
<li><strong>TRAINING</strong> — drillas mājās. Tas ir <em>kā tu pielienči</em>.</li>
<li><strong>SPECIAL-CASE</strong> — anomālijas (CEO objection). Tas ir <em>tikai dažreiz</em>.</li>
<li><strong>CARRIER</strong> — vizuālas metaforas (krasts, kalns, spēļu automāts). Tas ir <em>kā tu klientam parādi</em>.</li>
</ul>

<p>Šī grāmata sapī visus 6 māju saturu vienā plūsmā. Tu lasi, tu saproti — bet tev nav jāseko līdzi, kura māja katra rinda. Tas ir mans uzdevums.</p>

<h2>90 sekundes pirms zvana — tieši šis rituāls</h2>

<p>Šis ir tas, ko tu dari <strong>fiziski, balstoties pie galda vai stāvot pie loga</strong>, 90 sekundes pirms tu paņem tālruni:</p>
''')

parts.append(f'''
<table>
<tr><th>0–15 s</th><th>Power Pose</th><th>Rokas augšā V · 2 reizes pieklauvēt krūtīs · smaids</th></tr>
<tr><th>15–35 s</th><th>Elpa 4-4-6</th><th>5 cikli · 4 sek ieelpa · 4 sek tur · 6 sek izelpa</th></tr>
<tr><th>35–55 s</th><th>Pipeline</th><th>CRM atvērts · 25-30 atvērto klientu · pārpilnība galvā</th></tr>
<tr><th>55–75 s</th><th>MICE pārliek</th><th>Šis klients no Q4-Q5 priekšbiekas — kāds tips?</th></tr>
<tr><th>75–90 s</th><th>Mantras</th><th>Skaļi 3×: "Cerība nav sistēma." "Es nestrādāju ar visiem." "Es nepārdošu."</th></tr>
</table>

{bp_img('09_precall', caption='Pre-call rituāls 90 sekundes — fizikāli, ne mentāli')}

<p>Šis nav metafora. Tas ir <strong>fizioloģija</strong>. Cuddy 2010 pētījums: 2 minūtes Power Pose paaugstina testosteronu par 20%, samazina kortizolu par 25%. Elpa 4-4-6 aktivizē vagus nervu — tu fiziski izej no fight-or-flight stāvokļa. <em>Bez šī rituāla zvans sākas augstākā stresā nekā nepieciešams.</em></p>

<div class="callout callout-info">
  <div class="callout-title">SVARĪGI</div>
  <p>Mantras nav "pozitīvā domāšana". Tās ir <strong>kalibrācijas instruments</strong>. Trīs reizes "es nestrādāju ar visiem" nofiksē, ka tu šajā zvanā <em>filtrē</em>, ne lūdz. Trīs reizes "es nepārdošu — diagnozēju" nofiksē, ka tu šajā zvanā <em>uzdod jautājumus</em>, ne pārliecini.</p>
</div>

<p>Pēc 90 sekundēm — paņem tālruni. Q1 sākas.</p>
''')

# =============================================================
# AKTS II · Pirmie 6 minūtes (Q1-Q7) — MICE + Tonalitātes sapītas
# =============================================================
parts.append(akts_banner('II', 'AKTS II', 'Pirmie 6 minūtes', 'Frame · MICE motors · Tonalitātes 5 balsis · sākotnēji 7 jautājumi'))

parts.append(f'''
<p class="lead akts-opening">Pirmie 30 sekundes nosaka, vai klients tevi <em>pieņem</em> kā autoritātes vai kā lūdzēju. Tonalitāte šeit nav stils — tā ir <strong>signāls par to, kā tu sevi pozicionē</strong>. Belfort 5 balsis (Reasonable Man, I Care, I Feel Your Pain, Money, Mystery) parādās dabīgi tieši šajā Q1-Q7 segmentā.</p>

<p>Q1 ir vienkāršs sveiciens, bet ar slēptu īpašību: ar to tu <em>fiziski demonstrē</em>, ka tu neesi steigā. Tu pasaki "Sveiks" un kluso, ļauj klientam atbildēt. Tu jautā par dienu — ne kā mazo runu, bet kā <strong>cilvēcisku piesaisti</strong>.</p>
''')

parts.append(q_card('1'))
parts.append(q_card('2', gate=True))

parts.append(f'''
<p>Q2 ir <strong>pirmais vārts</strong>. Šeit tu pārveido zvanu no "pārdošanas situācijas" uz "diagnostikas situāciju". Klients dzird vārdu <em>"filtrs"</em>, dzird <em>"ja jūtu, ka nevaram tev būt noderīgi — teikšu uzreiz"</em>, un <strong>vienā teikumā tu izlauz visu pārdevēja-klienta saspēli</strong>. Tagad esi diagnostikas instruments. Klients piekrīt, jo tu esi paaugstinājis viņa statusu — viņš ir <em>filtrētais</em>, ne pārdotais.</p>

<div class="callout callout-tip">
  <div class="callout-title">🎤 Tonalitāte šeit · "Reasonable Man"</div>
  <p>Q2 nav "skripts" — tas ir <em>balss</em>. Belfort "Reasonable Man" nozīmē: skaidrs, sausains, nevērsts. Bez "uh, hmm, varbūt..." Bez priekšlaicīgas mīlestības. Vienkārši <strong>sava vieta</strong>. Klients sajūt: šis cilvēks nav nervozs.</p>
  <p>Drillas mājās: ierakste savu balsi, kā saki Q2 verbatim, klausies. Vai tava balss ir steigā? Vai apologēzē? Pārmer 100 reizes, līdz balss ir <em>sausā</em>.</p>
</div>
''')

parts.append(q_card('3', gate=True))

parts.append(f'''
<p>Q3 atklāj būtisku informāciju, kas <em>iet caur visu pārējo zvanu</em>. Ja klients viens var lemt — tu turpini ar pilnu spēku. Ja jārunā ar partneri — tu zini, ka pēc Q40 close būs "jārunā ar X" iebildums. <strong>Labāk to atklāt tagad un pārplānot, nekā 50 minūtes vēlāk pazaudēt close.</strong></p>

<hr class="fancy"/>

<h2>Q4-Q7 · MICE motors atklājas</h2>

<p>Tagad esi pirmajos 2-6 minūtēs. Klienta pirmā "īstā" atbilde nāk Q4 — un viss, kas seko, ir balstīts uz <strong>vārdiem, ko klients lieto</strong>. Pieraksti tos burtiski. Tu tos atkārtosi Q26 pīlāros un Q32 cenā.</p>

<p>Bet Q4-Q7 nav tikai jautājumi par mērķiem. Tie ir <strong>MICE motora kalibrācija</strong>. Klients neapzinās, ka pasaka, kas viņu virza. Tu klausies signālus un klasificē — Money, Ideology, Compromise vai Ego.</p>

{bp_img('03_mice', caption='MICE 4 motori — atklājas Q4-Q7, vada Q22 rāmi un Q32 cenu')}
''')

parts.append(q_card('4', gate=False))
parts.append(q_card('5'))

parts.append(f'''
<div class="callout callout-info">
  <div class="callout-title">MICE signāli Q5 atbildē</div>
  <p><strong>"Konkurents mūs aizsteidza priekšā"</strong> · "kāds aizsteidzās" · "viņi rāda visur" → <span class="badge badge-load">EGO</span></p>
  <p><strong>"Zaudēju 3 darījumus pēc kārtas"</strong> · "skaitļi krīt" · "samazinās ienākumi" → <span class="badge badge-gate">MONEY</span></p>
  <p><strong>"Gribēju kļūt par lielāko"</strong> · "mans mērķis ir mainīt" · "vīzija" → <span class="badge badge-load">IDEOLOGY</span></p>
  <p><strong>"Sieva saka, ka jādara kaut kas"</strong> · "partneris uzstāj" · "es pats nezinu" → <span class="badge" style="background: #0891b2; color: white;">COMPROMISE</span></p>
</div>
''')

parts.append(q_card('6'))
parts.append(q_card('7'))

parts.append(f'''
<p>Pēc Q7 tev ir <strong>klienta MICE klasifikācija</strong>. Pieraksti to. Šis nosaka:</p>
<ul>
  <li>Q22 Investora rāmi — kā tu pasniegsi vīziju (Money klients negrib "vīziju", grib ROI)</li>
  <li>Q26 3 pīlārus — Ego klients grib "top 1%", Compromise klients grib "drošs ceļš"</li>
  <li>Q32 cenu — Money klients reaģē uz anchor high → drop low; Ideology klients pieņem "ieguldījums vīzijā" rāmējumu</li>
  <li>Q33-Q38 iebildumus — Pragmatiķis vajag pierādījumus; Lepnais vajag prestiža apstiprinājumu</li>
</ul>

<h2>Tonalitātes 5 balsis · kā tās plūst caur Q1-Q7</h2>
''')

parts.append(f'''
<table>
<tr><th>Balss</th><th>Q-mapping</th><th>Verbatim signature</th></tr>
<tr><td><strong>Reasonable Man</strong></td><td>Q1-Q3 (frame)</td><td>"Zini, kā pie mums notiek..."</td></tr>
<tr><td><strong>I Care</strong></td><td>Q5-Q6</td><td>"Tas, ko tu saki, ir svarīgi."</td></tr>
<tr><td><strong>I Feel Your Pain</strong></td><td>Q11 GAP, Q21 COI</td><td>"Es saprotu, kā tas izklausās..."</td></tr>
<tr><td><strong>Money</strong></td><td>Q26, Q32</td><td>"Šī sistēma ražo €X mēnesī." (sausi, skaidri)</td></tr>
<tr><td><strong>Mystery / Curiosity</strong></td><td>Q21.5 Hope Break</td><td>"Es tev kaut ko pateikšu, kas varbūt tev nepatiks..."</td></tr>
</table>

<div class="callout callout-warning">
  <div class="callout-title">⚠ Drillas pirms zvana — neskan kā skripts</div>
  <p>5 balsis bez 100+ atkārtojumiem mājās skan kā <em>skripts</em>. Mūsdienu klients to atklāj 5 sekundēs. Pirmoreiz mēģini vienu balsi (Reasonable Man Q2), tad pievieno citu. Vienā zvanā maksimums <strong>2 balsis</strong>, ne visus 5 kopā.</p>
</div>

<p>Pēc Q7 tu pārej uz situācijas karti. Klients tagad runā <strong>aktīvāk</strong> — viņš ir izteicis savu motivāciju, viņa galva atvērta. Akts III sākas.</p>

<div class="interlude">Akts II beidzas. Klients ir atvēris savu motivāciju. Tagad tu skenē situāciju.</div>
''')

# =============================================================
# AKTS III · Karte (Q8-Q20)
# =============================================================
parts.append(akts_banner('III', 'AKTS III', 'Karte', 'Q8-Q20 · klienta esošā situācija · GAP €N · Mikro-jā cilpa · laika dimensija'))

parts.append(f'''
<p class="lead akts-opening">Akts III ir <strong>kartēšana</strong>. Tu uzzīmē klienta esošo situāciju: cik klientu, cik vidējais čeks, cik ilgi tas turpinās, kas mēģināts iepriekš. <em>Bez šī kartēšanas, Q22 Investora rāmis ir tukšs un Q26 3 pīlāri ir abstrakti.</em></p>

<p>Šeit pirmoreiz parādās <strong>Mikro-jā cilpa</strong>. Tu neuzdod cilpu uzreiz Q1 — tas izrāda manipulāciju. Bet Q11 vai Q16 brīdī, kad tu pārliecini klientu apstiprināt savu paša teikto skaitli, tas ir leģitīms commitment-and-consistency move.</p>
''')

parts.append(q_card('8'))
parts.append(q_card('9'))
parts.append(q_card('10'))
parts.append(q_card('11', gate=True))

parts.append(f'''
<p>Q11 ir <strong>otrais vārts</strong>. Šeit tu pārvērt klienta vēlmes par <em>konkrētu eiro skaitli</em>. Tu pārfrāzē: <em>"Tev šobrīd ir X, un tu gribi Y. Plaisa ir €N mēnesī."</em> Klients atbild "jā" uz tavu skaitli — un tagad <strong>€N ir viņa skaitlis</strong>, ne tavs.</p>

<div class="callout callout-tip">
  <div class="callout-title">🎤 Mikro-jā cilpa Q11 brīdī</div>
  <p>Pēc Q11 GAP €N tu vari ievīt 2-3 mikro-jā:</p>
  <blockquote>
  "Tev ir mērķis — vairāk klientu, jā?"<br/>
  "Un tev ir budžets, ko esi gatavs ieguldīt, ja sistēma strādā, jā?"<br/>
  "Un tev ir laiks 30 minūtēm, lai mēs apspriestu konkrētu plānu, jā?"
  </blockquote>
  <p>Cialdini commitment-and-consistency: 3 mazi "jā" pirms lielā lēmuma <strong>fizioloģiski</strong> ieslēdz "saskaņa-meklēšanas" režīmu klienta smadzenēs. Bet — <strong>maksimums 3 cilpa per zvans</strong>. Vairāk = klients sajūt manipulāciju.</p>
</div>
''')

parts.append(q_card('12'))
parts.append(q_card('13'))
parts.append(q_card('14'))
parts.append(q_card('15'))
parts.append(q_card('16'))

parts.append(f'''
<p>Pēc Q16 tev ir <strong>pilna situācijas karte</strong>: cik klientu, cik vidējais čeks, cik apgrozījums, kāda kapacitāte, cik teritorija. Tu vari pateikt: <em>"Tev ir potenciāls X eiro mēnesī, bet šobrīd tu darbojies pie 30%."</em> Šī ir matemātika, kas balstīta uz <strong>klienta pašu skaitļiem</strong>.</p>

<h2>Laika dimensija · Q17-Q20</h2>

<p>Tagad tu pievieno laika asi. <em>Cik ilgi tu tā esi?</em> <em>Vai tu esi mēģinājis risināt iepriekš?</em> <em>Vai tā ir tava personīgā vēlme vai kāda cita?</em></p>

<p>Šie 4 jautājumi sagatavo Q21 COI un Q21.5 Hope Break. Bez tiem klients teiks "es zinu", bet emocionāli vēl nebūs gatavs. Pēc Q20 viņa <em>laika apziņa</em> ir aktivizēta — viņš redz, ka jau gada vai 2 ir tajā pašā vietā.</p>
''')

parts.append(q_card('17'))
parts.append(q_card('18'))
parts.append(q_card('19'))
parts.append(q_card('20'))

parts.append(f'''
<div class="interlude">Akts III beidzas. Klients ir uzzīmējis savu karti. Viņš redz savu plaisu — un cik ilgi viņš tajā ir. Tagad nāk pārtraukums.</div>
''')

# =============================================================
# AKTS IV · "Pārtraukums" (Q21-Q21.5) — KLIMAKSS · Hope Fog DEEP + Decision Algorithm
# =============================================================
parts.append(akts_banner('IV', 'AKTS IV', 'Pārtraukums', 'Q21 COI · Q21.5 Hope Break · Lēmumu algoritms · KLIMAKSS'))

parts.append(f'''
<p class="lead akts-opening">Šis ir grāmatas un zvanu klimakss. Pirms Q21.5 klients zina <em>kur viņš ir</em> un <em>cik ilgi</em>. Bet viņš joprojām ir savā <strong>cerības miglā</strong> — viņš domā, ka kaut kā situācija atrisināsies. Q21 COI sāk plaisu radīt; Q21.5 Hope Break to <strong>pilnīgi pārtrauc</strong>. Šis ir vienīgais brīdis zvanā, kur tu apzināti, mērķtiecīgi <em>satraucinies klientu</em>.</p>

<p>Bez šī brīža Q22 Investora rāmis stāv tukšs. Q26 3 pīlāri ir abstrakcijas. Q32 cena tiek apspriesta. <strong>Šis ir LOAD-BEARING mezgls — visa tālākā ķēde balstās uz to.</strong></p>
''')

parts.append(q_card('21'))

parts.append(f'''
<p>Q21 ir <strong>matemātiska COI</strong>: ja jau gadu darbojies pie €X mēnesī, kad varētu būt €Y, tas ir <em>€(Y-X) × 12 = bezdarbības cena gadā</em>. Klients pirmo reizi redz, ka <strong>nedarīt</strong> arī maksā. Bet matemātika ir tikai pirmā kāpne — tagad nāk Hope Break.</p>

<hr class="fancy"/>

<h2>Q21.5 · Hope Fog Shatterer · 3 kāpnes</h2>
''')

parts.append(q_card('21.5', load_bearing=True))

parts.append(f'''
<p>V14.1 ieviesa Q21.5 kā load-bearing mezglu. V15 to <em>padziļināja</em> par pilnvērtīgu operatora moduli. Lūk, mehānika:</p>

<div class="pull-quote">
Cerība nav sistēma. Sistēma ir sistēma.
<span class="attribution">— Q21.5 koda frāze</span>
</div>

<p>Klients zvanā ienāk ar <strong>"cerības miglu"</strong>. Viņš domā, ka <em>kaut kā</em> situācija atrisināsies. Marketing aktivitātes <em>kaut kā</em> strādās. Klienti <em>kaut kā</em> atnāks. Tas ir hope-based decision-making, ne sistēmā.</p>

<p>Hope Break ir 3 kāpņu mehānika. Tu secīgi pierādi klientam: 1) tava plūsma <em>nav</em> process · tā ir cerība, 2) tu <em>negribi</em> aktīvi to risināt · tu gaidi, 3) tev <em>NAV</em> sistēmas — tu vienkārši ceri.</p>

<h3>Kāpne 1 · Process vai Cerība?</h3>
<blockquote>"Tava klientu plūsma — vai tā ir reāls, atkārtojams process, vai tā ir cerība, ka klienti kaut kā atnāks?"</blockquote>
<p>⏸ <strong>Klusums.</strong> Klients atbild. Pierakstīt <em>kuras vārdus viņš lieto</em>. "Process" / "kaut kā" / "atkarīgs no..." — tie ir signāli.</p>

<h3>Kāpne 2 · Aktīvi vai Pasīvi?</h3>
<blockquote>"Cik aktīvi tu pats šodien aizpildi to plaisu? Tu apzināti meklē klientus, vai tu gaidi, kad viņi tevi atradīs?"</blockquote>
<p>⏸ <strong>Klusums.</strong> Atklāj, vai klients atzīst pasivitāti.</p>

<h3>Kāpne 3 · 2 nedēļu hipotēze</h3>
<blockquote>"Iedomājies — TAGAD tev vajadzētu 5 jaunus klientus 2 nedēļās. Reāli, fiziski. Ja tev būtu jādara — tu PRECĪZI zinātu, kā TIEŠI tos atvest? Konkrēti soli pa solim?"</blockquote>
<p>⏸ <strong>Klusums 5-10 sekundes.</strong> Tas ir <em>kritiskais brīdis</em>. Klients sajūt šoku.</p>

{bp_img('02_hope_fog', caption='Hope Fog Shatterer — 3 kāpnes + lēmumu koks')}

<h2>7 frāzes pēc kāpnes — MICE-pielāgotas</h2>
<table>
<tr><th>MICE</th><th>Frāze</th></tr>
<tr><td><strong>Money</strong></td><td>"Cerība nav sistēma. Sistēma ražo €N mēnesī. Cerība neražo nekā."</td></tr>
<tr><td><strong>Ideology</strong></td><td>"Tava vīzija ir liela. Bet vīziju nedrīkst būvēt uz cerības."</td></tr>
<tr><td><strong>Compromise</strong></td><td>"Drošs ceļš ir cerības pretmieris. Sistēma DOD drošību."</td></tr>
<tr><td><strong>Ego</strong></td><td>"Top 1% biznesi nepārvalda ar cerību. Viņi pārvalda ar sistēmu."</td></tr>
<tr><td>Universāls 1</td><td>"Cerība nav sistēma. Sistēma ir sistēma."</td></tr>
<tr><td>Universāls 2</td><td>"Tu vari turpināt cerēt. Vai vari sākt sistēmā."</td></tr>
<tr><td>#7</td><td><em>[NEKO neesakām · 8-15 sek klusums]</em></td></tr>
</table>

<h2>Lēmumu koks pēc Hope Break</h2>

<div class="callout callout-success">
  <div class="callout-title">→ Klients piekrīt</div>
  <p>"Jā, man nav sistēma..." → Tālāk uz <strong>Q22 Investora rāmis</strong>. Klients ir System 1 stāvoklī, atvērts.</p>
</div>

<div class="callout callout-tip">
  <div class="callout-title">→ Klients pretī</div>
  <p>"Bet man IR plāns..." → 5 min sigurtības tīkls: pārjautā konkrēti, KAS ir tas plāns. 80% gadījumu klients pats atklāj, ka plāna nav. Tad atgriezies pie Kāpnes 3.</p>
</div>

<div class="callout callout-warning">
  <div class="callout-title">→ Klients agresija</div>
  <p>"Ko tu domā ar mani spēlēties?" → Paliec sausā tonā. <em>"Es nemēģinu spēlēties — es vienkārši pārjautāju."</em> Atvainojies tikai tad, ja patiesi pārkāpts robežpunkts.</p>
</div>

<h3>Aizliegumi pēc Hope Break</h3>
<ul>
  <li>✗ Neatvainojies — tas nav uzbrukums, tas ir diagnoze</li>
  <li>✗ Nesmaidi — tonis ir nopietns, klusais</li>
  <li>✗ Neatkārto vairāk kā 1× zvanā — vairāki = manipulācija</li>
  <li>✗ Nelasīt no kabatas — Hope Break frāzes ir zinātas no atmiņas</li>
</ul>

<hr class="fancy"/>

<h2>Lēmumu algoritms · 7 soļi · kāpēc šis darbojas</h2>

<p>Hope Break nav "psiholoģisks triks". Tas ir <strong>3. solis 7-soļu klienta iekšējā lēmuma ķēdē</strong>. Klients neuzreiz pieņem lēmumu — viņš iet cauri 7 soļiem, un mēs varam diagnozēt, kurā solī viņš iesprūdis.</p>
''')

parts.append(f'''
<table>
<tr><th>Solis</th><th>Klients dara</th><th>Q-mapping</th></tr>
<tr><td>1. Atpazīšana</td><td>Pamana savu situāciju</td><td>Q1-Q5</td></tr>
<tr><td>2. Mērīšana</td><td>Sāk skaitīt: GAP, laiks, nauda</td><td>Q9-Q13</td></tr>
<tr><td>3. Paredzēšana</td><td>Projicē nākotni</td><td>Q17, Q21</td></tr>
<tr><td>4. Salīdzināšana</td><td>Salīdzina pašreizējo ar sistēmu</td><td>Q21.5, Q22</td></tr>
<tr><td>5. Iztēlošanās</td><td>Vizualizē rezultātu</td><td>Q23-Q26</td></tr>
<tr><td>6. Validācija</td><td>Pārbauda iebildumus</td><td>Q27-Q31</td></tr>
<tr><td>7. Komutēšana</td><td>Pārkāpj durvis · System 1 → System 2</td><td>Q32-Q40</td></tr>
</table>

{bp_img('05_decision_algorithm', caption='Lēmumu algoritms 7 soļi · diagnostika · Kahneman System 1/2')}

<h3>Diagnostika · kad klients iesprūst</h3>
<table>
<tr><th>Iespruga vieta</th><th>Reālā problēma</th><th>Kur atgriezies</th></tr>
<tr><td>Q32 (cena)</td><td>3. solis · Hope Break nav locked</td><td><strong>Q21.5</strong></td></tr>
<tr><td>Q29 ("padomāšu")</td><td>2. solis · GAP nav konkrēts</td><td>Q11</td></tr>
<tr><td>Q27 ("pārā dārgi")</td><td>1. solis · MICE nav atklāts</td><td>Q4-Q7</td></tr>
<tr><td>Q33 ("sūti info")</td><td>5. solis · pīlāri nav konkrēti</td><td>Q26</td></tr>
<tr><td>Q34 ("jārunā ar X")</td><td>6. solis · validācija nepilnīga</td><td>Q27-Q31</td></tr>
</table>

<div class="pull-quote">
Klients NESAKA "nē". Viņš iesprūst solī. Operatora uzdevums — diagnozēt soli un atgriezties tur.
<span class="attribution">— Lēmumu algoritms · v15 izrāviens</span>
</div>

<div class="interlude">Akts IV beidzas. Klients ir izgājis cauri Hope Break. Cerība ir izgaisusi. Tagad nāk pīlāri.</div>
''')

# =============================================================
# AKTS V · Pīlāri (Q22-Q28) + Manipulācija/Inspirācija + Arhetipi
# =============================================================
parts.append(akts_banner('V', 'AKTS V', 'Pīlāri', 'Q22-Q28 · Investora rāmis · 3 pīlāri · Manipulācija vs Inspirācija · 6 arhetipi'))

parts.append(f'''
<p class="lead akts-opening">Pēc Hope Break klients ir <strong>System 1 stāvoklī, atvērts</strong>. Tagad tu būvē jauno realitāti — Investora rāmi (Q22), nākotnes vīziju (Q23), tad pāreju uz pitch (Q24-Q25), un beidzot <strong>3 pīlārus</strong> (Q26) — tas ir vārts.</p>

<p>Šajā Aktā ir kritiska iekšēja pozīcija — <strong>operatorā nostāja</strong>. Vai tu pīlārus pasniedz kā <em>argumentu</em> (manipulācija) vai kā <em>iedvesmu</em> (inspirācija)? Šī atšķirība, kas klientam nav redzama, izlemj, vai pitch atver vai aizver klientu.</p>
''')

parts.append(q_card('22', gate=True))

parts.append(f'''
<p>Q22 ir <strong>trešais vārts</strong>. Tu pasaki: "Ņemot vērā tavu situāciju un mērķi — es ieteiku skatīties uz šo kā uz <em>investīciju</em>, ne izmaksu. Sistēma maksā €N, bet ražo €M mēnesī." Klients sāk skaitīt ROI.</p>
''')

parts.append(q_card('23'))
parts.append(q_card('24'))
parts.append(q_card('25'))
parts.append(q_card('26', gate=True))

parts.append(f'''
<p>Q26 ir <strong>ceturtais vārts</strong>. Šeit tu izlieci 3 pīlārus, kas balsta jauno modeli. Bet — un šis ir kritiski — <strong>3 pīlāri tiek pielāgoti MICE motoram</strong> un <strong>klientu arhetipam</strong>. Money klients negrib "vīziju"; viņš grib ROI tabulu. Lepnais klients negrib "drošu ceļu"; viņš grib "top 1% klubu".</p>

<h2>6 klientu arhetipi · kā 3 pīlārus pielāgo</h2>
''')

# Arhetipi inline ar Q26
archetypes = [
    ("Skeptiķis", "Money", NAVY, "Q26 pīlāri: skaitļi · case studies · ROI", "Q22: ROI matemātika · €/lead", "Pro €3,000"),
    ("Vizionārs", "Ideology", GOLD, "Q26 pīlāri: legacy stāsts · ietekme uz nozari", "Q22: 'Tu nepazūdi rutīnā, tu būvē vīziju'", "Enterprise €6,000"),
    ("Pragmatiķis", "Compromise", TEAL, "Q26 pīlāri: garantijas · pakāpenisks ieviesums · pierādījumi", "Q22: '2 ceļi — droši rīt, riskanti pēc gada'", "Pro €3,000"),
    ("Lepnais", "Ego", RED, "Q26 pīlāri: 'Top 1% klubs' · ekskluzivitāte · prestiža uzvara", "Q22: 'Tu atjauno vadību nozarē'", "Enterprise / White-Label"),
    ("Analītiķis", "Money+Compromise", PURPLE, "Q26 pīlāri: case studies · skaitļi · A/B testi", "Q22: ROI matemātika + risks profils", "Pro €3,000"),
    ("Pirmsreizējais", "Beginner", GREEN, "Q26 pīlāri: 'pamati' valoda · vienkārši pīlāri", "Q22: vienkāršs sistēmas attēls", "Basic €1,500"),
]

for name, mice, color, q26, q22, tier in archetypes:
    parts.append(f'''
<div class="callout" style="background: {PAPER}; border-color: {color};">
  <div class="callout-title" style="color: {color};">{name} · MICE: {mice}</div>
  <p style="font-size: 9.5pt; margin: 1mm 0;"><strong>Q22 rāmis:</strong> {q22}</p>
  <p style="font-size: 9.5pt; margin: 1mm 0;"><strong>{q26}</strong></p>
  <p style="font-size: 9.5pt; margin: 1mm 0;"><strong>Tier:</strong> {tier}</p>
</div>
''')

parts.append(f'{bp_img("08_archetypes", caption="6 klientu arhetipi radial · MICE-mappēti pa Q22 un Q26")}')

parts.append(q_card('27'))
parts.append(q_card('28'))

parts.append(f'''
<h2>Manipulācija vs Inspirācija · operatorā nostāja</h2>

<p>Atrodi vienu lietu, kas nošķir <strong>operatoru, kurš slēdz</strong>, no <strong>operatora, kurš piepūš</strong>. Tā nav tehnika. Tā ir <em>iekšēja pozīcija</em>:</p>

<table>
<tr><th>Manipulācija</th><th>Inspirācija</th></tr>
<tr><td>Es <em>pārliecinu</em> klientu</td><td>Es <em>parādu</em> klientam</td></tr>
<tr><td>Pīlāri ir <em>arguments</em></td><td>Pīlāri ir <em>vīzija</em></td></tr>
<tr><td>Es <em>uzstāju</em> uz close</td><td>Es <em>filtrē</em> klientu</td></tr>
<tr><td>Klients sajūt <em>spiediena</em></td><td>Klients sajūt <em>aicinājuma</em></td></tr>
<tr><td>Pēc zvana — pārdomas</td><td>Pēc zvana — atvieglojums</td></tr>
</table>

<div class="pull-quote">
Vienīgā atšķirība starp manipulāciju un inspirāciju ir tava iekšējā nostāja. Klients to uztver bez vārdiem.
<span class="attribution">— Sinek + Cialdini hibrīdā</span>
</div>

<div class="interlude">Akts V beidzas. Pīlāri ir izlikti. Klients ir gatavs gala lēmumam. Tagad — patiesība.</div>
''')

# =============================================================
# AKTS VI · Patiesība (Q29-Q32) + Klusais slēgums
# =============================================================
parts.append(akts_banner('VI', 'AKTS VI', 'Patiesība', 'Q29-Q32 · 1-10 vērtējums · gatavība · cena · KLUSAIS SLĒGUMS'))

parts.append(f'''
<p class="lead akts-opening">Q32 cena ir piektais un pēdējais vārts. Bet tā nav <em>cipars</em>; tā ir <strong>moments</strong>. Brīdis pēc cipara, kad tu klusē 8-15 sekundes, izšķir 70% close. Pirmais, kas pārtrauc to klusumu, zaudē. Tu esi <em>fiziski</em> trenējies turēt klusumu — tāpēc tu uzvar.</p>
''')

parts.append(q_card('29', gate=False))

parts.append(f'''
<p>Q29 1-10 vērtējums ir <strong>gatavības mērijums</strong>. Klients pasaka 7. Tu jautā: <em>"Ko vajadzētu, lai būtu 8 vai 9?"</em> Klients pats <strong>uzraksta sev iebildumu</strong>. Tagad tev nav jāminēt — tev ir konkrētais šķērslis.</p>
''')

parts.append(q_card('30'))
parts.append(q_card('31'))
parts.append(q_card('32', gate=True))

parts.append(f'''
<hr class="fancy"/>

<h2>Klusais slēgums 8-15s · Q32 mehānika</h2>

<p>Tu pasaki cipāru. Pēc tā — <strong>klusums</strong>. 8-15 sekundes. Pirmais, kas pārtrauc, zaudē kontroli. Tas nav arsenāls; tas ir <em>disciplīna</em>.</p>

{bp_img('07_silent_close', caption='Klusais slēgums 8-15s · pulkstenis · pirmais zaudē')}

<div class="callout callout-warning">
  <div class="callout-title">⚠ Aizliegumi pēc cenas</div>
  <ul>
    <li>✗ "...un mēs varam arī iekļaut..." (panika · pierādīji, ka cipars nav stabīls)</li>
    <li>✗ "Es saprotu, ka tas ir liels skaitlis..." (apologēze · zaudē autoritāti)</li>
    <li>✗ Smaids · steidzas · sapūsti · sastingst (visi atklāj nervozitāti)</li>
  </ul>
</div>

<div class="callout callout-success">
  <div class="callout-title">✓ Pareizs klusais slēgums</div>
  <p>Tu pasaki cipāru. Tu skatīšies uz pierakstiem, ne uz klientu. Tu skaiti elpu — 4 sek ieelpa, 6 sek izelpa. Pulkstenis 8-15 sek. Tu klusē. Klients runā pirmais.</p>
</div>

<h2>Klients runā pirmais · ko viņš pasaka</h2>

<table>
<tr><th>Klienta pirmā atbilde</th><th>Ko tas nozīmē</th><th>Tava reakcija</th></tr>
<tr><td>"Ok, derēs."</td><td>Lēmums pieņemts</td><td>Q40 rēķins · neaizverts</td></tr>
<tr><td>"Hmm... cik var maksāt mēnesī?"</td><td>Skaitlis OK · pārrunā struktūru</td><td>Q39 finanšu pielāgošana</td></tr>
<tr><td>"Vēl jāpadomā..."</td><td>Iesprūst 2. solī (GAP nav konkrēts)</td><td>Atgriezies Q11 · pārjautā</td></tr>
<tr><td>"Pārā dārgi..."</td><td>Iesprūst 1. solī (MICE nav atklāts)</td><td>Atgriezies Q4-Q7 · pārjautā</td></tr>
<tr><td>"Sūti info..."</td><td>Iesprūst 5. solī (pīlāri nav konkrēti)</td><td>Atgriezies Q26 · pielāgo</td></tr>
<tr><td>"Jārunā ar partneri..."</td><td>Q3 nebij saķeris lēmējus</td><td>Q35 skripts</td></tr>
</table>

<div class="interlude">Akts VI beidzas. Cipars ir izteikts. Klusums ir izturēts. Klients runā. Tagad seko iebildumi.</div>
''')

# =============================================================
# AKTS VII · Iebildumi (Q33-Q40) + CARE + Voss + Takeaway
# =============================================================
parts.append(akts_banner('VII', 'AKTS VII', 'Iebildumi', 'Q33-Q40 · CARE ietvars · Voss "Nē" · Takeaway · Close'))

parts.append(f'''
<p class="lead akts-opening">Iebildumi nav noraidījums — tie ir <strong>informācija</strong>. Klients tev pasaka, kura solī viņš iesprūdis, un tu zini, kur atgriezties. CARE ietvars (Connect → Acknowledge → Reframe → Engage) ir disciplīna, kas tev ļauj nereaģēt impulsīvi.</p>
''')

parts.append(q_card('33'))

parts.append(f'''
<h2>CARE iebildumu ietvars</h2>

<p>Katrs iebildums apstrādājas pa 4 soļiem. <strong>Bez šī ietvara</strong> tu reaģē impulsīvi — vai aizstāvies, vai uzbrūk. CARE tevi tur sausā tonā.</p>

<table>
<tr><th>C · Connect</th><td>"Es saprotu, kāpēc tu to saki..." (nepiekrīt, bet apstiprini)</td></tr>
<tr><th>A · Acknowledge</th><td>"Tas ir saprātīgs jautājums..." (apstiprini, ka iebildums ir leģitīms)</td></tr>
<tr><th>R · Reframe</th><td>"Bet skaties no šī skatpunkta..." (pārrāmējiet)</td></tr>
<tr><th>E · Engage</th><td>"Vai tas ir tas, ko tu meklēji?" (atgriezies pie klienta)</td></tr>
</table>

{bp_img('14_care', caption='CARE iebildumu cikls · 4 soļi pret impulsīvu reakciju')}
''')

parts.append(q_card('34'))

parts.append(f'''
<h3>Q34 · "Vēl jāpadomā" — Takeaway close pielietojums</h3>

<p>"Vēl jāpadomā" 80% gadījumu nozīmē <em>"man nav skaidra konkrētība"</em>. Tu vari pielietot <strong>Takeaway</strong> — soft atkāpšanos, kas paaugstina klienta pieņemšanu:</p>

<blockquote>"Atklāti sakot — varbūt mēs vienkārši vēl nav īstais brīdis tev. Mēs nestrādājam ar visiem. Pasaki — kas TIEŠI tev būtu jāpārliecinās, lai šis būtu skaidrs?"</blockquote>

<p>Klients sajūt zaudēšanas risku. 60-70% gadījumu viņš atklāj precīzu šķērsli — un tagad tev ir konkrēts iebildums, ne miglu.</p>
''')

parts.append(q_card('35'))

parts.append(f'''
<h3>Q35 · "Jārunā ar sievu / partneri" — Voss "Nē"</h3>

<p>Chris Voss tehnika: klients labāk jūtas drošs, ja saka "Nē". Tu pārvērsi situāciju:</p>

<blockquote>"Vai būtu pretrunā tavām interesēm, ja mēs ar tavu partneri kopā apskatītu šos pīlārus 15 minūtēs?"</blockquote>

<p>Klients saka "Nē" (jo tas ir drošāks) — un tu uzreiz pārplāno trīs-pusu zvanu. Tas, ko viņš saka "Nē", ir tava IELŪGUMA noraidījums, ne pati ideja.</p>
''')

parts.append(q_card('36'))
parts.append(q_card('37'))
parts.append(q_card('38'))
parts.append(q_card('39'))
parts.append(q_card('40', gate=False))

parts.append(f'''
<div class="callout callout-info">
  <div class="callout-title">Q40 · Tehniskais close</div>
  <p>Pēc visu iebildumu apstrādes Q40 ir <strong>tehniska aktīvitāte</strong>: nosūti rēķinu, atver kalendāru, ieplāno onboarding zvanu. <em>Nav vairs jāpārliecina.</em> Klients jau ir lēmis. Tu tikai aizved durvis.</p>
</div>

<div class="interlude">Akts VII beidzas. Close ir notikušs. Tagad sāk pēc-zvana fāze — un tas ir vissvarīgākais brīdis tava izaugsmē.</div>
''')

# =============================================================
# AKTS VIII · "Pēc zvana" — post-call + L1-L5 + Anti-Overload + Fast-Start
# =============================================================
parts.append(akts_banner('VIII', 'AKTS VIII', 'Pēc zvana', 'Post-call rituāls · 10:3:1 zelta princips · L1-L5 ceļš · Anti-Overload gudrība · Fast-Start 7 dienu'))

parts.append(f'''
<p class="lead akts-opening">Pārdošanas operatori, kuri pieaug — pieaug tieši šeit. Tas, kas notiek 30 minūtes <em>pēc</em> zvana, izšķir, vai nākamais zvans būs labāks. <strong>10:3:1 zelta princips:</strong> uz katru zvanu — 10 minūtes audita, 3 minūtes klasifikācijas, 1 stunda nākamā plāna.</p>

<h2>Post-call rituāls · 30 minūtes</h2>

<table>
<tr><th>Solis</th><th>Laiks</th><th>Kas notiek</th></tr>
<tr><td>1. Audio replay</td><td>5 min</td><td>Pārklausies klusumus, GAP brīžus, Hope Break</td></tr>
<tr><td>2. Q-čeklists</td><td>3 min</td><td>Kuri 5 vārti izpildīti? (Q3, Q11, Q21.5, Q26, Q32)</td></tr>
<tr><td>3. MICE klasifikācija</td><td>2 min</td><td>Klients = M / I / C / E?</td></tr>
<tr><td>4. CRM atjaunojums</td><td>5 min</td><td>Stadijas, MICE, GAP €N, follow-up</td></tr>
<tr><td>5. Anti-overload audit</td><td>3 min</td><td>Cik ARSENAL es izmantoju? (ideālā 0-1)</td></tr>
<tr><td>6. Nākamais plāns</td><td>12 min</td><td>Email, kalendārs, pielikumi</td></tr>
</table>

<div class="pull-quote">
Zvans nav notikums. Zvans ir 90 sek + 50 min + 30 min = 80 min sistēma.
<span class="attribution">— Operatora rituāls</span>
</div>

<hr class="fancy"/>

<h2>Anti-Overload · gudrība, kas nāk pēc 50 zvaniem</h2>

<p>Vissvarīgākā lieta, ko tu iemācies pēc 50 dzīvajiem zvaniem, nav <em>vairāk tehniku</em>. Tas ir <strong>kā nelietot par daudz</strong>. Šīs grāmatas otrā mācība, kas nāk dabīgi: <em>vienā zvanā maksimums 1 ARSENAL mezgls</em>.</p>

<table>
<tr><th>Aizliegums</th><th>Pamatojums</th></tr>
<tr><td>Maks. 1 ARSENAL per zvans</td><td>Vairāki = klients sajūt manipulāciju</td></tr>
<tr><td>Maks. 1 metafora per zvans</td><td>Vairākas = atmiņas pārslodze</td></tr>
<tr><td>Voss + Takeaway + Mikro-jā kopā nelieto</td><td>Visi 3 ir psiholoģiski intensīvi</td></tr>
<tr><td>Tonalitāti 5 balsis bez 100+ drillas — ne</td><td>Skan kā skripts</td></tr>
<tr><td>5 vārti palaisti — ne</td><td>Klients piekrīt teorētiski, bet nepāries</td></tr>
<tr><td>Pārtraukts klusums Q32 — ne</td><td>Pierādīji, ka cena nestabīla</td></tr>
</table>

{bp_img('11_anti_overload', caption='7 aizliegumi + 1 zelta likums · disciplīna pret pārkarsēšanu')}

<hr class="fancy"/>

<h2>L1-L5 ceļš · kā tu pieaudzisi</h2>

<p>Pārdošanas meistarība nav <em>talanta</em> jautājums. Tā ir <strong>disciplinēts ceļš</strong>. Katrs līmenis ir definēts ar konkrētu ARSENAL atļauju un live zvanu skaitu.</p>

<table>
<tr><th>Līmenis</th><th>Nosaukums</th><th>Periods</th><th>ARSENAL atļauja</th></tr>
<tr><td><strong>L1</strong></td><td>Iesācējs</td><td>Day 7</td><td>1 ARSENAL (Tonalitāte vai Klusais slēgums)</td></tr>
<tr><td><strong>L2</strong></td><td>Drošs</td><td>Day 30</td><td>1 ARSENAL (jebkurš no TOP 4)</td></tr>
<tr><td><strong>L3</strong></td><td>Profs</td><td>Day 90</td><td>2 ARSENAL · 50+ live zvani</td></tr>
<tr><td><strong>L4</strong></td><td>Eksperts</td><td>Day 180+</td><td>3 ARSENAL · kombinācijas ar disciplīnu</td></tr>
<tr><td><strong>L5</strong></td><td>Meistars</td><td>Day 365+</td><td>Visi 11 · situatīvi · ar instinkta jūtu</td></tr>
</table>

{bp_img('12_levels', caption='V16 līmeņi L1-L5 · disciplinēts kāpņu ceļš')}

<hr class="fancy"/>

<h2>Fast-Start · pirmā nedēļa</h2>

<p>Šī grāmata kā tāda ir smaga. Bet tu nevaroties to lasīt linearly un mēģināt visu vienlaikus. Tu sāk šeit:</p>

<table>
<tr><th>Diena</th><th>Mērķis</th><th>Konkrētais</th></tr>
<tr><td>Day 0</td><td>15 min</td><td>WAR MAP A4 izlasi · KODONS audio · drukā</td></tr>
<tr><td>Day 1</td><td>60 min</td><td>Akts II + III lasi · Q-ķēde uz papīra</td></tr>
<tr><td>Day 2</td><td>60 min</td><td>Akts IV (Hope Break) lasi · 7 frāzes auswendig</td></tr>
<tr><td>Day 3</td><td>60 min</td><td>Akts V + VI lasi · arhetipus saproti</td></tr>
<tr><td>Day 4</td><td>roleplay</td><td>1 ARSENAL pielieto · Tonalitāte vai Klusais slēgums</td></tr>
<tr><td>Day 5</td><td>roleplay</td><td>Hope Break drillē 5×</td></tr>
<tr><td>Day 6</td><td>1 live zvans</td><td>Maksimums 1 ARSENAL · maksimums 1 metafora</td></tr>
<tr><td>Day 7</td><td>3 live zvani</td><td>Audit ar 10:3:1 princip · CRM</td></tr>
</table>

<div class="callout callout-success">
  <div class="callout-title">PĒC DAY 7</div>
  <p>Tu esi <strong>L1 (Iesācējs)</strong>. Tu zini Q1-Q40 ķēdi, vari pielietot 1 ARSENAL, seko anti-overload protokolam. Tagad atver Day 30 plānu un turpini.</p>
</div>

<div class="interlude">Akts VIII beidzas. Tu esi izgājis cauri visu zvanu — pirms, zvanā, pēc. Atliek epilogs.</div>
''')

# =============================================================
# EPILOGS — minimal · LV-native tabula · glosārijs
# =============================================================
parts.append(akts_banner('—', 'EPILOGS', 'Validācija un vārdnīca', 'LV-native tabula · audit · glosārijs'))

parts.append(f'''
<p class="lead akts-opening">Šajā grāmatā ir <strong>godīga validācijas tabula</strong>. Katrs elements ir marķēts: 🟢 LV-native (Lauris pats apstiprinājis dzīvajos zvanos), ⚪ EN-derived (no IG/FB EN korpusa, pārtulkots, bet vēl nav LV-validēts), ⚠ hipotēze (vēl nav pārbaudīts).</p>

<h2>LV-native validācijas tabula</h2>
''')

lv_table = [
    ('Q1-Q40 CORE', '🟢', 'LV-native', 'Lauris · 89 Fathom zvani'),
    ('5 vārti (Q3, Q11, Q21.5, Q26, Q32)', '🟢', 'LV-native', 'Lauris dzīvajos'),
    ('Hope Break 3 kāpnes', '🟢', 'LV-native', 'Lauris signature'),
    ('MICE 4 motori', '🟢', 'LV-native', 'Adaptēts no IG, validēts LV'),
    ('CARE ietvars', '🟢', 'LV-native', 'Adaptēts, validēts'),
    ('Tonalitātes 5 balsis', '🟢', 'LV-native', 'Lauris drillas'),
    ('Mikro-jā cilpa', '🟢', 'LV-native', 'Lauris dzīvajos'),
    ('Klusais slēgums 8-15s', '🟢', 'LV-native', 'Lauris signature'),
    ('Lēmumu algoritms 7 soļi', '🟢', 'LV-native', 'NotebookLM sintēze + Lauris'),
    ('6 klientu arhetipi', '🟢', 'LV-native', 'No Lauris klasifikācijas'),
    ('Pricing tieri (4)', '🟢', 'LV-native', 'Sharpify aktuālais'),
    ('Pre-call rituāls 90s', '🟢', 'LV-native', 'Cuddy + Lauris'),
    ('V16 Anti-Overload', '🟢', 'LV-native', 'V16 oriģinālais'),
    ('V16 Pareto Top 4', '🟢', 'LV-native', 'Lauris audit'),
    ('Ghosting break-up', '⚪', 'EN-derived', 'IG @cole.gordon'),
    ('Takeaway close', '⚪', 'EN-derived', 'Cialdini scarcity'),
    ('Voss "Nē" psiholoģija', '⚪', 'EN-derived', 'Voss corpus'),
    ('Spoguļošana + body', '⚪', 'EN-derived', 'NLP corpus'),
    ('Lojalitātes cilpa', '⚪', 'EN-derived', 'Sandler corpus'),
    ('Manipulācija vs Inspirācija', '⚪', 'EN-derived', 'Sinek + Cialdini'),
    ('CEO objection', '⚠', 'Hipotēze', 'Special case · nav LV testa'),
]

parts.append('<table><tr><th>Elements</th><th>Statuss</th><th>Tips</th><th>Avots</th></tr>')
for elem, status, kind, source in lv_table:
    badge = ('badge-lv' if '🟢' in status else 'badge-en' if '⚪' in status else 'badge-hyp')
    parts.append(f'<tr><td>{elem}</td><td style="text-align:center;">{status}</td><td><span class="badge {badge}">{kind.upper()}</span></td><td style="font-size:9pt;">{source}</td></tr>')
parts.append('</table>')

parts.append(f'''
<h2>Glosārijs</h2>

<table>
<tr><th>Termins</th><th>Nozīme</th></tr>
<tr><td><strong>5 vārti</strong></td><td>Q3, Q11, Q21.5, Q26, Q32 — neapejami katrā zvanā</td></tr>
<tr><td><strong>ARSENAL</strong></td><td>Situatīvi mezgli (Tonalitāte, Mikro-jā, Klusais slēgums) · max 1 per zvans</td></tr>
<tr><td><strong>CARE</strong></td><td>Connect → Acknowledge → Reframe → Engage (iebildumu cikls)</td></tr>
<tr><td><strong>COI</strong></td><td>Cost of Inaction · bezdarbības cena (Q21)</td></tr>
<tr><td><strong>CORE</strong></td><td>Q1-Q40 obligātā ķēde · sacrosanct</td></tr>
<tr><td><strong>CORK</strong></td><td>1-lapa kabatas slānis · WAR MAP A4</td></tr>
<tr><td><strong>GAP €N</strong></td><td>Klienta esošā vs vēlmes ienākumu plaisa eiro (Q11)</td></tr>
<tr><td><strong>Hope Break</strong></td><td>Q21.5 · LOAD-BEARING · "Cerība nav sistēma"</td></tr>
<tr><td><strong>MICE</strong></td><td>Money / Ideology / Compromise / Ego — 4 klienta motori</td></tr>
<tr><td><strong>System 1/2</strong></td><td>Kahneman · ātrs/instinktīvs vs lēns/analītisks</td></tr>
<tr><td><strong>V8 mezgli</strong></td><td>14 klienta lēmumu mezgli × 8 slāņi (klienta iekšējā arhitektūra)</td></tr>
<tr><td><strong>V13 6-slāņu</strong></td><td>CORE/CORK/ARSENAL/TRAINING/SPECIAL-CASE/CARRIER struktūra</td></tr>
</table>

<h2>Galvenais</h2>

<div class="manifesto" style="margin-top: 8mm;">
  <div class="manifesto-title">VIENS PRINCIPS · VIENA PIEEJA</div>
  <div class="manifesto-body">
    Šī grāmata sākas ar pre-call rituālu un beidzas ar post-call auditu.<br/>
    Starp tiem ir Q1-Q40, sapīts ar visiem ARSENAL slāņiem.<br/>
    <strong>Lasi to vienā līnijā. Pielietot to vienā līnijā.</strong><br/>
    Disciplīna virs zināšanām. Sistēma virs cerības.
  </div>
</div>

<hr class="fancy"/>

<p style="text-align: center; color: {GOLD}; margin-top: 20mm; font-size: 10pt; letter-spacing: 2pt;">
  SALESENGINE MASTER MONOLĪTS · 2026 · Sharpify.io
</p>
''')

# ==============================================================
# Compose final HTML
# ==============================================================
html_full = f'''<!DOCTYPE html>
<html lang="lv">
<head>
<meta charset="UTF-8"/>
<title>SalesEngine · Master Monolīts</title>
<style>{CSS_TEXT}</style>
</head>
<body>
{"".join(parts)}
</body>
</html>
'''

html_path = OUT / 'V16_MASTER_MONOLITHS.html'
html_path.write_text(html_full, encoding='utf-8')
print(f'HTML written: {html_path.stat().st_size//1024} KB')

print('Rendering PDF...')
pdf_path = OUT / 'SALESENGINE_MASTER_MONOLITHS.pdf'
HTML(string=html_full, base_url=str(ROOT)).write_pdf(str(pdf_path))
print(f'PDF written: {pdf_path.stat().st_size//1024} KB')
