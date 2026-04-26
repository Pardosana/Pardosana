// ============= NAVIGATION =============
document.querySelectorAll('.nav-item').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.nav-item').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    document.getElementById('section-' + btn.dataset.section).classList.add('active');
    document.getElementById('sidebar').classList.remove('open');
    window.scrollTo(0, 0);
  });
});

function toggleTheme() {
  const t = document.body.dataset.theme === 'dark' ? 'light' : 'dark';
  document.body.dataset.theme = t;
  localStorage.setItem('theme', t);
}
if (localStorage.getItem('theme')) document.body.dataset.theme = localStorage.getItem('theme');

// ============= QUESTIONS =============
function getPhase(num) {
  if (num <= 3) return { num: 1, name: "Frame & Ievads", color: "#4f8eff" };
  if (num <= 7) return { num: 2, name: "Centrs & Motīvi", color: "#6dd3ce" };
  if (num <= 16) return { num: 3, name: "Situācijas karte", color: "#a78bfa" };
  if (num <= 20) return { num: 4, name: "Laika dimensija", color: "#fbbf24" };
  if (num <= 23) return { num: 5, name: "Gap & nākotne", color: "#f97316" };
  if (num <= 28) return { num: 6, name: "Pitch · 3 Pīlāri", color: "#10b981" };
  if (num <= 32) return { num: 7, name: "1-10 + Cena", color: "#ef4444" };
  return { num: 8, name: "Iebildumi + Close", color: "#d4a574" };
}

function renderMarkdown(s) {
  return s
    .replace(/\*\*(.+?)\*\*/g, '<b>$1</b>')
    .replace(/\*"([^"]+)"\*/g, '<span class="phrase">$1</span>')
    .replace(/`([^`]+)`/g, '<code style="background:var(--panel-2);padding:1px 6px;border-radius:3px;font-size:12px;font-family:JetBrains Mono,monospace;">$1</code>')
    .replace(/\n\n/g, '</p><p style="margin:8px 0;">')
    .replace(/^- (.+)$/gm, '<li style="margin-left:16px;">$1</li>');
}

function renderQuestions(filter = 'all') {
  const list = document.getElementById('questions-list');
  let lastPhase = 0;
  let html = '';
  DATA.questions.forEach(q => {
    const phase = getPhase(q.num);
    if (filter === 'critical' && q.priority < 2) return;
    if (filter === 'hopebreak' && !q.is_hope_break) return;
    if (filter.startsWith('phase')) {
      const p = parseInt(filter.replace('phase', ''));
      if (phase.num !== p) return;
    }
    if (phase.num !== lastPhase) {
      html += `<div class="phase-divider"><hr><span style="color:${phase.color};">Fāze ${phase.num} · ${phase.name}</span><hr></div>`;
      lastPhase = phase.num;
    }
    const stars = '⭐'.repeat(q.priority);
    const hbStyle = q.is_hope_break ? 'border:2px solid #ff6b35;background:rgba(255,107,53,0.04);' : '';
    const hbBadge = q.is_hope_break ? '<span style="background:#ff6b35;color:white;padding:2px 8px;border-radius:4px;font-size:10px;font-weight:600;margin-left:6px;">⚡ V13 HOPE BREAK</span>' : '';
    const numDisplay = q.num_display || q.num;
    html += `<div class="card" data-num="${numDisplay}" data-search="${(q.title + ' ' + q.phrases.join(' ') + ' ' + q.dkods).toLowerCase()}" style="${hbStyle}">
      <div class="card-header" onclick="this.parentNode.classList.toggle('open')">
        <div style="flex:1;">
          <div class="card-title">${q.title} ${stars ? `<span class="tag-priority">${stars}</span>` : ''}${hbBadge}</div>
          <div class="card-meta">
            ${q.dkods ? `<span class="tag-d">${q.dkods}</span>` : ''}
            <span style="background:${phase.color}22;color:${phase.color};">Fāze ${phase.num}</span>
            <span>${q.phrases.length} frāzes</span>
            <span style="background:#10b98122;color:#10b981;">[CORE]</span>
          </div>
        </div>
        <span class="card-num">Q${numDisplay}</span>
        <span class="card-toggle">▼</span>
      </div>
      <div class="card-body">
        ${q.merkis ? `<div style="margin-bottom:10px;"><b style="font-size:12px;color:var(--muted);">MĒRĶIS:</b> <span style="font-size:13px;">${q.merkis}</span></div>` : ''}
        ${q.phrases.map(p => `<div class="phrase">${p}</div>`).join('')}
        <details style="margin-top:14px;">
          <summary style="cursor:pointer;color:var(--accent);font-size:12px;font-weight:600;">📖 Pilns konteksts (raw)</summary>
          <div style="margin-top:10px;padding:12px;background:var(--panel-2);border-radius:6px;font-size:12px;line-height:1.6;white-space:pre-wrap;color:var(--muted);">${q.raw.replace(/[<>]/g, c => ({'<':'&lt;','>':'&gt;'}[c]))}</div>
        </details>
      </div>
    </div>`;
  });
  list.innerHTML = html || '<p style="color:var(--muted);text-align:center;padding:40px;">Nekas neatbilst filtram.</p>';
}
renderQuestions();

document.querySelectorAll('.filter-chip[data-filter]').forEach(chip => {
  chip.addEventListener('click', () => {
    chip.parentNode.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
    chip.classList.add('active');
    renderQuestions(chip.dataset.filter);
  });
});

// ============= SEARCH =============
document.getElementById('search').addEventListener('input', e => {
  const q = e.target.value.toLowerCase().trim();
  if (!q) {
    document.querySelectorAll('.card[data-num]').forEach(c => c.style.display = '');
    return;
  }
  document.querySelectorAll('.card[data-num]').forEach(c => {
    c.style.display = c.dataset.search.includes(q) ? '' : 'none';
  });
});

// ============= MEZGLI (V8 Molecular) =============
const MEZGLI_GRID = document.getElementById('mezgli-grid');
const LAYER_NAMES = { core: '🎯 Core', elite: '⚜️ Elite', psychology: '🧠 Psych', therapeutic: '💆 Therap', signals: '📡 Signāli', delivery: '🎙️ Delivery', if_stuck: '🚧 Iesprūdis', risks: '⚠️ Riski' };

MEZGLI_GRID.innerHTML = DATA.mezgli.map((m, i) => {
  const layers = Object.keys(m.layers);
  const hbStyle = m.is_hope_break ? 'border:2px solid #ff6b35;background:rgba(255,107,53,0.04);' : '';
  const hbBadge = m.is_hope_break ? '<span style="background:#ff6b35;color:white;padding:1px 6px;border-radius:3px;font-size:9px;margin-left:6px;">⚡ V13</span>' : '';
  return `<div class="mezgls-card" data-mezgls="${i}" style="${hbStyle}">
    <div class="mezgls-name">${m.name}${hbBadge}</div>
    <div class="mezgls-range">${m.q_range || ''}</div>
    <div class="layer-tabs">
      ${layers.map((l, j) => `<button class="layer-tab ${j === 0 ? 'active' : ''}" data-layer="${l}">${LAYER_NAMES[l] || l}</button>`).join('')}
    </div>
    <div class="layer-content" id="layer-${i}"></div>
  </div>`;
}).join('');

function renderLayer(s) {
  // Convert *"..."* phrases into chips, then handle slash separators
  if (!s) return '';
  // Split by / between phrases — render each phrase as a chip
  const chips = s.split(/\s*\/\s*/).map(p => {
    const m = p.match(/^\*"(.+?)"\*$/);
    if (m) return `<div class="phrase">${m[1]}</div>`;
    return `<div style="padding:8px 0;font-size:13px;line-height:1.6;">${renderMarkdown(p)}</div>`;
  }).join('');
  return chips;
}

document.querySelectorAll('.mezgls-card').forEach((card, i) => {
  // Render initial layer
  const firstLayer = Object.keys(DATA.mezgli[i].layers)[0];
  document.getElementById('layer-' + i).innerHTML = renderLayer(DATA.mezgli[i].layers[firstLayer] || '');
  card.querySelectorAll('.layer-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      card.querySelectorAll('.layer-tab').forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      document.getElementById('layer-' + i).innerHTML = renderLayer(DATA.mezgli[i].layers[tab.dataset.layer] || '');
    });
  });
});

// ============= CLIENT TYPES =============
const TYPES_GRID = document.getElementById('types-grid');
TYPES_GRID.innerHTML = DATA.client_types.map(t => {
  return `<div class="type-card" onclick="this.classList.toggle('active')">
    <div class="type-name">${t.name}</div>
    <div style="font-size:13px;line-height:1.7;color:var(--muted);">${renderMarkdown(t.raw.substring(0, 1200))}${t.raw.length > 1200 ? '...' : ''}</div>
  </div>`;
}).join('');

// ============= RESPONSE TREES =============
document.getElementById('trees-list').innerHTML = DATA.response_trees.map(t => {
  return `<div class="tree-card">
    <div class="tree-trigger">"${t.trigger}"</div>
    <div style="font-size:13px;line-height:1.7;color:var(--text);">${renderMarkdown(t.raw)}</div>
  </div>`;
}).join('');

// ============= ELITE RULES =============
document.getElementById('rules-grid').innerHTML = DATA.elite_rules.map(r => {
  return `<div class="rule-card">
    <span class="rule-num">${r.num.toString().padStart(2, '0')}</span>
    <div class="rule-name">${r.rule}</div>
    <div class="rule-desc">${r.explain}</div>
  </div>`;
}).join('');

// ============= LADDERS =============
document.getElementById('ladders-list').innerHTML = `
<div class="card open"><div class="card-body" style="border:none;padding:0;">
<h3 style="color:var(--accent);">1. Abstract → Contrast → Example → Self-placement</h3>
<p style="font-size:13px;color:var(--muted);margin:6px 0 12px;">Kad klients nesaprot abstraktu jautājumu — nepaliec abstrakcijā.</p>
<div class="phrase">Vai tas vairāk ir par cenu, risku vai vienkārši nedrošību?</div>
<div class="phrase">Piemēram, dažiem cilvēkiem nav skaidrs mehānisms, citiem vairāk ir bail kļūdīties.</div>
<div class="phrase">Kurš no tiem tev ir tuvāks?</div>
</div></div>

<div class="card open"><div class="card-body" style="border:none;padding:0;">
<h3 style="color:var(--accent);">2. Name the category before asking for content</h3>
<p style="font-size:13px;color:var(--muted);margin:6px 0 12px;">Cilvēks bieži nevar atbildēt, jo nezina, kāda tipa atbildi tu prasi.</p>
<div class="phrase">Es te vairāk domāju nevis 'ko tu gribi', bet kur tev šis iesprūst — loģikā, sajūtā vai lēmumā.</div>
<div class="phrase">Kur tas tev šobrīd ir vairāk?</div>
</div></div>

<div class="card open"><div class="card-body" style="border:none;padding:0;">
<h3 style="color:var(--accent);">3. Give a response frame, not the answer</h3>
<p style="font-size:13px;color:var(--muted);margin:6px 0 12px;">Iedod rāmi, kurā cilvēks var ielikt savu atbildi.</p>
<div class="phrase">Tas bieži cilvēkiem iesprūst vienā no trim vietām: nav skaidrs rezultāts, nav drošības sajūtas, vai vienkārši nav gatavības. Kurš tev tuvāks?</div>
</div></div>

<div class="card open"><div class="card-body" style="border:none;padding:0;">
<h3 style="color:var(--accent);">4. Ladder of access — kad klients saka "nezinu"</h3>
<p style="font-size:13px;color:var(--muted);margin:6px 0 12px;">4 pakāpes — neej uz dziļumu uzreiz.</p>
<div class="phrase">Kas te tev ir vismaz mazliet skaidrāks?</div>
<div class="phrase">Ja tev būtu jāmin, uz kuru pusi tas vairāk iet?</div>
<div class="phrase">Kas no šī tev tuvāk skan?</div>
<div class="phrase">Kas tev šeit jau ir zināms, bet vēl ne līdz galam noformulēts?</div>
</div></div>

<div class="card open"><div class="card-body" style="border:none;padding:0;">
<h3 style="color:var(--accent);">5. Temporary borrowed language</h3>
<p style="font-size:13px;color:var(--muted);margin:6px 0 12px;">Iedod pagaidu valodu cilvēkam, kuram nav vārdu savam mezglam.</p>
<div class="phrase">Es nezinu, vai tev šeit vārds būs 'bailes', 'nedrošība' vai 'vienkārši negribas kļūdīties' — bet uz kuru pusi tas tev vairāk skan?</div>
<div class="phrase">Es nezinu, vai te precīzākais vārds ir 'haoss', 'migla' vai 'kontroles trūkums' — bet kas tev te tuvāk?</div>
</div></div>

<div class="card open"><div class="card-body" style="border:none;padding:0;">
<h3 style="color:var(--accent);">6. Example-installation</h3>
<p style="font-size:13px;color:var(--muted);margin:6px 0 12px;">Iedod 2 mini piemērus, nevis 1 teoriju.</p>
<div class="phrase">Dažiem 'jāpadomā' nozīmē: 'man vēl nav drošības'. Citiem tas nozīmē: 'es zinu, bet vēl negribu atzīt'. Kurš tev tuvāk?</div>
</div></div>

<div class="card open"><div class="card-body" style="border:none;padding:0;">
<h3 style="color:var(--accent);">7. Difference questions</h3>
<p style="font-size:13px;color:var(--muted);margin:6px 0 12px;">Jautā pēc atšķirības, nevis definīcijas.</p>
<div class="phrase">Kas būtu citādi, ja šis tev būtu skaidrs?</div>
<div class="phrase">Kā tu saprastu atšķirību starp 'neesmu drošs' un 'vienkārši negribu to tagad darīt'?</div>
</div></div>

<div class="card open"><div class="card-body" style="border:none;padding:0;">
<h3 style="color:var(--accent);">8. Mini-map before deep question</h3>
<p style="font-size:13px;color:var(--muted);margin:6px 0 12px;">Pirms grūta jautājuma, dod īsu kontekstu.</p>
<div class="phrase">Es te tagad mēģinu saprast vienu lietu — kur tu šobrīd zaudē kontroli. Es necentos tevi nogāzt — gribu tikai redzēt, kur ir īstais mezgls. Vai būtu ok, ja paskatāmies tieši uz to?</div>
</div></div>
`;

// ============= TRAFFIC LIGHT =============
const TL_CONTENT = {
  green: '<b style="color:var(--green);">🟢 GREEN — Skaidrība ir, svars ir, klients iesaistīts.</b><br>→ Vari virzīt tālāk. Pārliecinies, ka neej pārāk strauji. Patur tempu, neuzkrustīt to ar pārliecināšanu.',
  yellow: '<b style="color:var(--yellow);">🟡 YELLOW — Daļēja skaidrība, vēl ir migla zem virsmas.</b><br>→ Vajag 1-2 precizējošus jautājumus. Ej dziļāk pirms tālāk. Iesaki: <i>"Kas te ir galvenais?"</i> · <i>"Dod vienu konkrētu piemēru."</i>',
  red: '<b style="color:var(--red);">🔴 RED — Atbildes ir fasāde, nav sāpju svara, nav ciparu, nav saknes.</b><br>→ <b>STOP.</b> Neej tālāk, kamēr nesalabo. Atgriezies uz iepriekšējo mezglu. Iesaki Comprehension Ladders: <i>"Vai tas vairāk ir par X, Y vai Z?"</i>'
};
function setTL(c) {
  document.querySelectorAll('.tl-btn').forEach(b => b.classList.toggle('active', b.dataset.color === c));
  document.getElementById('tl-status').innerHTML = TL_CONTENT[c];
}

// ============= RESET PHRASES =============
document.getElementById('reset-phrases').innerHTML = DATA.reset_phrases.map(p => `<div class="reset-pill">${p}</div>`).join('');

// ============= SIMULATOR =============
const SIM_TYPES = [
  { name: 'ANALĪTISKAIS', emoji: '🧮', desc: 'Loģika, dati, mehānisms' },
  { name: 'SKEPTISKAIS', emoji: '🤔', desc: 'Testē tevi, prasa proof' },
  { name: 'BAILĪGAIS', emoji: '😰', desc: 'Atliek, izvairās' },
  { name: 'DOMINANTAIS', emoji: '👔', desc: 'Kontrolē tempu' },
  { name: 'STATUS-DRIVEN', emoji: '💎', desc: 'Domā par līmeni' },
  { name: 'EMOCIONĀLAIS', emoji: '❤️', desc: 'Sajūta > fakti' }
];
let SIM_TYPE = null, SIM_HISTORY = [];

document.getElementById('sim-types').innerHTML = SIM_TYPES.map(t => `<button class="filter-chip" data-type="${t.name}">${t.emoji} ${t.name}<br><span style="font-size:10px;opacity:0.7;">${t.desc}</span></button>`).join('');
document.querySelectorAll('#sim-types .filter-chip').forEach(b => b.addEventListener('click', () => {
  document.querySelectorAll('#sim-types .filter-chip').forEach(c => c.classList.remove('active'));
  b.classList.add('active');
  SIM_TYPE = b.dataset.type;
  document.getElementById('sim-current-type').textContent = SIM_TYPE;
  resetSim();
  simAddMsg('client', SIM_OPENERS[SIM_TYPE] || 'Sveiki. Kā jums iet?');
}));

const SIM_OPENERS = {
  'ANALĪTISKAIS': 'Sveiki. Pirms sākam — vai jūs varētu īsi paskaidrot, kā tieši šī sistēma strādā un kāda ir konversijas matemātika?',
  'SKEPTISKAIS': 'Hm, esmu jau dzirdējis daudzus solījumus. Ko tieši jūs darāt citādāk nekā 10 citi, kas mani arī uzrunāja?',
  'BAILĪGAIS': 'Es... nezinu. Esam mēģinājuši ar reklāmām, bet... tas viss šķiet sarežģīti. Varbūt vēlāk?',
  'DOMINANTAIS': 'Tā, man ir 30 minūtes. Sāksim. Ko tu man piedāvā?',
  'STATUS-DRIVEN': 'Ar kādiem klientiem jūs strādājat? Es nestrādāju ar masu tirgu — meklēju kvalitatīvu partneri.',
  'EMOCIONĀLAIS': 'Vienkārši ļoti gribu, lai bizness sāktu kustēties. Daudz ir ieguldīts, bet nekas tā kā nestrādā...'
};

const SIM_RESPONSES = {
  'ANALĪTISKAIS': [
    { trigger: ['galvenā lieta', 'gribētos atrisināt', 'pamatu visai'], reply: 'Galvenā problēma — leadu kvalitāte un konversija. Šobrīd ~3% no Google reklāmām. Nezinu, kur ir bottleneck.', mezgls: 'MĒRĶIS', next: 'Tagad konkrēti skaitļi — Q9 Numbers Hammer.' },
    { trigger: ['cik daudz', 'cik klientu', 'apgrozījum'], reply: 'Mums ~15-20 leadu mēnesī, no tiem 2-3 kļūst par klientiem. Vidējais čeks €4500. Apgrozījums ~€90k mēnesī.', mezgls: 'SITUĀCIJA', next: 'Q15 — kapacitāte. Cik daudz vēl varētu uzņemt?' },
    { trigger: ['cenu', 'maksā', 'budžet'], reply: 'Pirms cenas — vai jūs varētu paskaidrot ROI matemātiku ar konkrētiem cipariem?', mezgls: 'PRICE', next: 'Belief vāj. Atpakaļ uz Q22 Self-Sell.' },
    { trigger: ['1.', '1-10', 'novērtē'], reply: '7 no 10. Loģiski saprotu, bet nav skaidrs, kā tieši tas atšķirsies no Google Ads, ko jau testējām.', mezgls: 'BELIEF', next: 'Diferencē mehānismu — Q24 Spogulis.' }
  ],
  'SKEPTISKAIS': [
    { trigger: ['galvenā lieta', 'gribētos atrisināt'], reply: 'Hm, tas ir slidens jautājums. Lai jūs varētu pasniegt savu produktu, tā? Es nezinu, vai gribu jums to atklāt vēl.', mezgls: 'FRAME', next: 'Drošības tests. Atkārto rāmi: "Ja nav fits — saku uzreiz."' },
    { trigger: ['ja nav fit', 'pateikšu', 'sapratīsim'], reply: 'OK, godīgi tas skan citādāk. Labi — galvenā lieta ir, ka nestabils klientu plūsma. Brīžiem 30 leadu, brīžiem 5.', mezgls: 'SITUĀCIJA', next: 'Q8 — pattern, ne simptomi.' },
    { trigger: ['cik', 'klientu', 'apgrozījum'], reply: 'Es nesaku precīzus ciparus, kamēr nezinu, ar ko jūs to izmantosiet. Kāpēc tas svarīgs?', mezgls: 'COI', next: 'Investora frame: "Lai matemātika strādā, vajag pamatdatus."' },
    { trigger: ['cena', 'maksā'], reply: 'Pirms cenas — ko tieši jūs darāt citādāk nekā 10 agency, kas mani arī tagad solās?', mezgls: 'PRICE', next: 'Q24 Spogulis — atšķirības mehānisms.' }
  ],
  'BAILĪGAIS': [
    { trigger: ['galvenā lieta', 'gribētos'], reply: 'Es... nezinu, kā to formulēt. Vienkārši sajūta, ka mēs nepelnām tik, cik varētu. Bet bail uzkraut sev vairāk darba.', mezgls: 'SĀPE', next: 'Empātiska valoda. Q5 — kas lika ierasties.' },
    { trigger: ['kas lika', 'kāpēc tagad', 'kāpēc šobrīd'], reply: 'Sieva teica, ka jāizmēģina. Es pats... vienmēr esmu domājis, ka kaut kā jārisina, bet katru reizi atlieku.', mezgls: 'DELAY DEMON', next: 'CARE: Atzīsti viņa avoidance, neuzbrūk.' },
    { trigger: ['mēģinājām', 'iepriekš'], reply: 'Jā, mēģinājām pirms 2 gadiem ar SEO. Iztērējām €3000, nekas neiznāca. Kopš tā laika baidos no šādiem soļiem.', mezgls: 'BELIEF', next: 'CARE: Pārkadrē — "Tas nebija sistēma, bija atsevišķa taktika."' },
    { trigger: ['cenu nolikt', 'ja cenu', 'malā'], reply: 'Mhm... varbūt. Bet tas atkarīgs no tā, vai sieva piekritīs. Jārunā ar viņu.', mezgls: 'OBJECTION', next: 'Response Tree #4 (Partneris): "Ja noliekam viņu malā — tu pats šo redzi pareizi?"' }
  ],
  'DOMINANTAIS': [
    { trigger: ['galvenā lieta', 'gribētos'], reply: 'Apgrozījuma augšana. Esmu pie €280k gadā, gribu €560k līdz nākamā gada beigām. Punkts.', mezgls: 'MĒRĶIS', next: 'Tieši uz lietu — Q15 kapacitāte, tad Q24 Mehānisms.' },
    { trigger: ['cik', 'mēnesī', 'budžet'], reply: 'Pietiekami. Sāc no svarīgākā — kā tieši jūs to darāt? Konkrēti.', mezgls: 'PITCH', next: 'Q24 3 Pīlāri — bez liekiem vārdiem.' },
    { trigger: ['1-10', 'novērtē'], reply: '8. Esmu gatavs sākt, ja matemātika strādā. Cik?', mezgls: 'PRICE', next: 'Q32 — €2400/€3000, divi varianti, klusums.' },
    { trigger: ['€2400', '€3000', '2400', '3000'], reply: 'OK. Kad sākam? Es negribu atvērt sarunu vairākas reizes.', mezgls: 'CLOSE', next: 'Q34 Rēķins UZREIZ. Lock datumu un maksājumu.' }
  ],
  'STATUS-DRIVEN': [
    { trigger: ['galvenā lieta'], reply: 'Es gribu nostiprināt savu pozīciju nišā. Es jau esmu top 3, bet gribu būt nepārprotami #1.', mezgls: 'IDENTITĀTE', next: 'Identity collision — Q26 piesaiste pie atsauces (Modern House, Skandi).' },
    { trigger: ['ar kādiem', 'kādiem klientiem', 'piemēri'], reply: 'Tieši to es jautāju. Ar ko jūs strādājat? Kvalitāti es atpazīstu uzreiz.', mezgls: 'BELIEF', next: 'Q26 — pielikt 1 atsauci, kas līmenim atbilst.' },
    { trigger: ['Modern House', 'Skandi', 'Indexo', 'Citadele'], reply: 'OK, tas skan nopietnāk. Bet vienlaikus — kā jūs nodrošināsiet, ka manai nišai netiek pelnīts uz "average" partnerim?', mezgls: 'BULLSEYE', next: 'Q19 Buying Instruction — kas viņam BŪTU JĀREDZ.' },
    { trigger: ['cena', 'maksā', '€2400', '€3000'], reply: 'Cena nav jautājums, ja kvalitāte garantēta. Bet — kas notiek, ja 3 mēnešos nav rezultāta?', mezgls: 'OBJECTION', next: 'Drošība — Q26 Bonuss + skaidrs šo-mēnešu plāns.' }
  ],
  'EMOCIONĀLAIS': [
    { trigger: ['galvenā lieta'], reply: 'Es... vienkārši gribu, lai sāktu strādāt. Esmu daudz ieguldījusi, bet nekas tā kā... ka tas reāli kustētos.', mezgls: 'SĀPE', next: 'Empātija pirms ciparu. Q6 — "Ko tas tev nozīmē?"' },
    { trigger: ['ko tas tev', 'tev nozīmē', 'ko tev dos'], reply: 'Ka beidzot varētu... varbūt elpot. Pēdējo gadu es pati taisu visu. Bērniem nav laika. Ja varētu paplašināties — nāktu palīgi.', mezgls: 'NEIZBĒGAMĪBA', next: 'Q21 COI emocionāls + future pacing.' },
    { trigger: ['cik tas', 'maksā tev', 'gada laikā'], reply: 'Nu... ja ņem laiku, ko es te zaudēju... varbūt 2 gadi nav kustējušies. Tas ir... daudz.', mezgls: 'COI', next: 'Q22 Self-Sell — 1-10 gatavība.' },
    { trigger: ['1.', '1-10', 'gatavība'], reply: '9. Es esmu gatava. Cena man nav lielākā problēma — vairāk bail no kārtējās vilšanās.', mezgls: 'BELIEF', next: 'Drošības frame Q26 Bonuss + skaidri pirmie 30 dienu soļi.' }
  ]
};

function simAddMsg(role, text) {
  const msgs = document.getElementById('sim-msgs');
  const div = document.createElement('div');
  div.className = 'sim-msg ' + role;
  div.innerHTML = text;
  msgs.appendChild(div);
  msgs.scrollTop = msgs.scrollHeight;
  SIM_HISTORY.push({ role, text });
}

function simSend() {
  const inp = document.getElementById('sim-input');
  const text = inp.value.trim();
  if (!text || !SIM_TYPE) {
    if (!SIM_TYPE) alert('Izvēlies klientu tipu vispirms!');
    return;
  }
  inp.value = '';
  simAddMsg('you', text);
  const lower = text.toLowerCase();
  const responses = SIM_RESPONSES[SIM_TYPE] || [];
  let matched = null;
  for (const r of responses) {
    if (r.trigger.some(t => lower.includes(t.toLowerCase()))) {
      matched = r;
      break;
    }
  }
  setTimeout(() => {
    if (matched) {
      simAddMsg('client', matched.reply);
      const fb = document.createElement('div');
      fb.className = 'sim-feedback';
      fb.innerHTML = `<b>📊 V14 analīze:</b> Tu tikko nostrādāji <b style="color:var(--accent);">${matched.mezgls}</b> mezglu.<br><b>Nākamais ieteicamais solis:</b> ${matched.next}`;
      document.getElementById('sim-msgs').appendChild(fb);
      document.getElementById('sim-msgs').scrollTop = 9999;
    } else {
      simAddMsg('client', '[' + SIM_TYPE + ' klients reaģētu uz konkrētāku jautājumu — pamēģini frāzi no Q-flow vai Comprehension Ladders.]');
      const fb = document.createElement('div');
      fb.className = 'sim-feedback';
      fb.innerHTML = '⚠️ Tava frāze nav atpazīstama V14 sistēmā. Pamēģini: <i>"Kas ir tā galvenā lieta, ko gribētos atrisināt?"</i> vai citu Q-flow jautājumu.';
      document.getElementById('sim-msgs').appendChild(fb);
    }
  }, 400);
}

function resetSim() {
  document.getElementById('sim-msgs').innerHTML = '';
  SIM_HISTORY = [];
}

// ============= V14.1 NEW: HOPE BREAK SECTION =============
(function renderHopeBreak() {
  const container = document.getElementById('hopebreak-content');
  if (!container) return;
  const hbQ = DATA.questions.find(q => q.is_hope_break);
  const hbM = DATA.mezgli.find(m => m.is_hope_break);
  if (!hbQ && !hbM) { container.innerHTML = '<p style="color:var(--muted);">Hope Break dati nav atrasti.</p>'; return; }
  let html = '';
  if (hbQ) {
    html += `<div class="card open" style="border:2px solid #ff6b35;">
      <div class="card-header">
        <div style="flex:1;">
          <div class="card-title">Q${hbQ.num_display} · ${hbQ.title}</div>
          <div class="card-meta">
            <span class="tag-d">${hbQ.dkods}</span>
            <span style="background:#ff6b3522;color:#ff6b35;">⚡ LOAD-BEARING</span>
            <span style="background:#10b98122;color:#10b981;">[CORE]</span>
          </div>
        </div>
        <span class="card-num">Q${hbQ.num_display}</span>
      </div>
      <div class="card-body">
        <div style="margin-bottom:12px;"><b style="font-size:12px;color:var(--muted);">MĒRĶIS:</b> <span style="font-size:13px;">${hbQ.merkis}</span></div>
        <h4 style="font-size:13px;margin:12px 0 8px;color:#ff6b35;">3 jautājumu kāpnes:</h4>
        ${hbQ.phrases.map((p, i) => `<div class="phrase"><b style="color:#ff6b35;">${i+1}.</b> ${p}</div>`).join('')}
        <details style="margin-top:14px;">
          <summary style="cursor:pointer;color:var(--accent);font-size:12px;font-weight:600;">📖 Pilns konteksts (raw)</summary>
          <div style="margin-top:10px;padding:12px;background:var(--panel-2);border-radius:6px;font-size:12px;line-height:1.6;white-space:pre-wrap;color:var(--muted);">${hbQ.raw.replace(/[<>]/g, c => ({'<':'&lt;','>':'&gt;'}[c]))}</div>
        </details>
      </div>
    </div>`;
  }
  if (hbM) {
    html += `<h2 style="margin-top:24px;font-size:16px;">V8 Molecular: ${hbM.name}</h2>
    <p style="font-size:12px;color:var(--muted);margin-bottom:12px;">${hbM.q_range || ''}</p>
    <div class="mezgls-card" style="border:2px solid #ff6b35;">
      <div class="mezgls-name">${hbM.name}</div>
      <div class="layer-tabs">
        ${Object.keys(hbM.layers).map((l, j) => `<button class="layer-tab ${j === 0 ? 'active' : ''}" data-hb-layer="${l}">${LAYER_NAMES[l] || l}</button>`).join('')}
      </div>
      <div class="layer-content" id="hb-layer-content"></div>
    </div>`;
  }
  html += `<div class="callout" style="margin-top:24px;border-left-color:#ff6b35;background:rgba(255,107,53,0.06);">
    <h4 style="margin-bottom:8px;">Sekvence: COI → Hope Break → Inevitability</h4>
    <ol style="padding-left:24px;font-size:13px;line-height:1.8;">
      <li><b>COI</b> (Q21): "Tev tas maksā €X mēnesī. Pareizi?" → klients atzīst</li>
      <li><b>Hope Break</b> (Q21.5): "Process vai cerība?" → klients atzīst, ka cerība</li>
      <li><b>Inevitability</b> (Q22): "Kas tieši nākamajā mēnesī būs citādi?" → klusums</li>
    </ol>
  </div>`;
  container.innerHTML = html;
  if (hbM) {
    const firstLayer = Object.keys(hbM.layers)[0];
    document.getElementById('hb-layer-content').innerHTML = renderLayer(hbM.layers[firstLayer] || '');
    document.querySelectorAll('[data-hb-layer]').forEach(tab => {
      tab.addEventListener('click', () => {
        document.querySelectorAll('[data-hb-layer]').forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        document.getElementById('hb-layer-content').innerHTML = renderLayer(hbM.layers[tab.dataset.hbLayer] || '');
      });
    });
  }
})();

// ============= V14.1 NEW: VISUAL CARRIER SECTION =============
(function renderVisualCarrier() {
  const container = document.getElementById('visual-content');
  if (!container || !DATA.visual_carrier) return;
  const emoji = {'KRASTS':'🏖️','LAUVA':'🦁','GLĀBŠANAS':'🛟','NEREDZAMĀ':'💸','CERĪBAS':'🌫️','TILTS':'🌉','GIDS':'🧭','KALNS':'⛰️','DAKŠA':'🍴'};
  let html = '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:16px;">';
  DATA.visual_carrier.forEach(vc => {
    const key = vc.name.split(' ')[0];
    const em = emoji[key] || '🎨';
    const isHB = vc.node && vc.node.includes('Hope Break');
    html += `<div class="card open" style="${isHB ? 'border:2px solid #ff6b35;' : ''}">
      <div class="card-header" style="padding:14px;">
        <div style="flex:1;">
          <div class="card-title">${em} ${vc.name}${isHB ? ' <span style="background:#ff6b35;color:white;padding:1px 6px;border-radius:3px;font-size:9px;">⚡ HOPE BREAK</span>' : ''}</div>
          <div class="card-meta"><span style="background:#9b7eff22;color:#9b7eff;">[PRESENTATION CARRIER]</span></div>
        </div>
        <span class="card-num" style="font-size:18px;">#${vc.num}</span>
      </div>
      <div class="card-body" style="padding:14px;">
        <div style="margin-bottom:10px;"><b style="font-size:11px;color:var(--muted);">REPREZENTĒ:</b> <span style="font-size:13px;">${vc.represents}</span></div>
        <div style="margin-bottom:10px;"><b style="font-size:11px;color:var(--muted);">MEZGLS:</b> <span style="font-size:13px;">${vc.node}</span></div>
        <div style="margin-bottom:10px;"><b style="font-size:11px;color:var(--muted);">KAD:</b> <span style="font-size:13px;">${vc.when}</span></div>
        ${vc.phrase ? `<div class="phrase" style="margin-top:10px;">${vc.phrase}</div>` : ''}
      </div>
    </div>`;
  });
  html += '</div>';
  html += `<div class="callout" style="margin-top:24px;border-left-color:#9b7eff;background:rgba(155,126,255,0.06);">
    <h4 style="margin-bottom:8px;">Likums: VIENA metafora uz vienu zvanu</h4>
    <p style="font-size:13px;margin-bottom:8px;"><b style="color:#10b981;">Pareizi (ūdens domēns):</b> KRASTS → CERĪBAS MIGLA → TILTS</p>
    <p style="font-size:13px;margin-bottom:8px;"><b style="color:#ef4444;">Nepareizi:</b> KRASTS + LAUVA + KALNS + DAKŠA — klients apmaldās</p>
    <p style="font-size:13px;"><b>Slide rules:</b> 1 vizuāls = 1 mezgls · 1 ideja = 1 frame · max 7 vārdi · cheap → test → final</p>
  </div>`;
  container.innerHTML = html;
})();

// ============= V14.1 NEW: LAYERS (V13 6-slāņu disciplīna) =============
(function renderLayers() {
  const container = document.getElementById('layers-content');
  if (!container || !DATA.layers) return;
  const colors = {'CORE / EXPANDED CORE':'#10b981','CURRENT CORK':'#4f8eff','ARSENAL':'#fbbf24','TRAINING':'#a78bfa','SPECIAL-CASE':'#ef4444','PRESENTATION CARRIER':'#9b7eff'};
  let html = '<div style="display:grid;gap:14px;">';
  DATA.layers.forEach((l, i) => {
    const color = colors[l.name] || '#6b7280';
    html += `<div class="card open" style="border-left:4px solid ${color};">
      <div class="card-body" style="padding:16px;">
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:10px;">
          <span style="background:${color};color:white;font-weight:700;padding:4px 10px;border-radius:4px;font-size:11px;">SLĀNIS ${i+1}</span>
          <h3 style="margin:0;font-size:15px;color:${color};">${l.name}</h3>
        </div>
        <p style="font-size:13px;line-height:1.6;margin-bottom:8px;"><b style="font-size:11px;color:var(--muted);">KAS IEKŠĀ:</b> ${l.contains}</p>
        <p style="font-size:13px;line-height:1.6;"><b style="font-size:11px;color:var(--muted);">KAD LIETOT:</b> ${l.when}</p>
      </div>
    </div>`;
  });
  html += '</div>';
  container.innerHTML = html;

  const pcContainer = document.getElementById('prompt-core-content');
  if (pcContainer && DATA.prompt_core) {
    pcContainer.innerHTML = '<ol style="padding-left:24px;line-height:2;">' +
      DATA.prompt_core.map(p => `<li><b style="color:var(--accent);">${p.law}</b> — ${p.explain}</li>`).join('') +
    '</ol>';
  }
})();
