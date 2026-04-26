# DAĻA VIII · LĒMUMU ALGORITMS · PRECĪZAI LĒMUMU PIEŅEMŠANAI

> **Avots:** *SalesEngine algoritms precīzai lēmumu pieņemšanai* (Lauris Leitāns audio · 88 min · NotebookLM sintēze) · konsolidēts ar V14.1 Q1–Q40 plūsmu un V8 Molecular Core Map.

> **Pamatlikums:** Klients **nepieņem lēmumu emocionāli vai loģiski izolēti**. Tas ir 7‑soļu iekšējā ķēde, kuru viņš iziet **silenti**. Operatorā esošais V15 algoritms šo ķēdi **atspoguļo ārējos jautājumos**, kas apmieiena ļautājumus tā, lai klients **pats** redz savu lēmumu. Ja kāds solis trūkst — klients **iesprūst**, un pārdevējs domā, ka problēma ir cena. **Patiesībā problēma ir izlaists solis.**

---

## 8.1 · KĀPĒC LĒMUMS NAV "EMOCIJA vs LOĢIKA"

Klasiskā pārdošanas teorija saka: *"Cilvēki pērk emocionāli, pamatojas loģiski."* Tas ir tikai **20% patiesība**. V15 algoritms parāda, ka faktiskais lēmums iziet **abas sistēmas**:

- **System 2** (analītiskā, lēnā, racionālā) — atbild par **mērīšanu, salīdzināšanu, validāciju**
- **System 1** (instinktīva, ātrā, emocionālā) — atbild par **atpazīšanu, iztēlošanos, komutēšanu**

> **Daniel Kahneman pamatprincips:** Kad operators pārdod, **System 2 automātiski bloķē** — klienta racionālā prāta meklē iemeslu, kāpēc atteikt. Tāpēc pamata pārdošanas tehnikas (System 1 valoda, ne‑pārdevēja identitāte, kolēģis‑diagnostiķis) ir **būtiskas**: tikai tad System 1 ir atvērta, un mēs varam paralēli novest klientu cauri System 2 mērīšanas soļiem **bez pretestības**.

---

## 8.2 · 7‑SOĻU LĒMUMU ALGORITMS

| Solis | Iekšējs jautājums | V15 Q‑mezgls(i) | Sistēma |
|---|---|---|---|
| **1. Atpazīšana** | *"Tas ir tas, ko es jūtu / piedzīvoju"* | Q4 ⭐⭐⭐ Galvenā lieta · Q5 Kas lika ierasties | System 1 |
| **2. Mērīšana** | *"Cik tas izmaksā šobrīd?"* | Q11 GAP · Q12 vidējais čeks · Q21 COI | System 2 |
| **3. Paredzēšana** | *"Vai tas turpināsies bez intervenes?"* | Q17 cik ilgi · ⚡ Q21.5 Hope Break | System 2 |
| **4. Salīdzināšana** | *"Vai ir labāks ceļš?"* | Q18 Zelta · Q22 Investora rāmis · Q19 vai meklēts iepriekš | System 2 |
| **5. Iztēlošanās** | *"Vai es to varu izdarīt?"* | Q23 Bridge · Q26 3 pīlāri · Future Pacing | System 1 |
| **6. Validācija** | *"Vai tas pasargā mani?"* | Q29 1–10 · Q30 gatavība · Q31 onboarding | System 2 |
| **7. Komutēšana** | *"Es iesāku"* | Q32 cena · Q33–Q40 close · *"Karti vai pārskaitījumu?"* | System 1 |

> **Operatora pielietojums:** Ja klients **iesprūst** kādā fāzē, atgriezies pie **iepriekšējā** soļa un pārliecinies, ka tas ir locked. Visbiežākie iesprūdas:
> - Iesprūst Q29 (1–10) → 2. Mērīšana nav locked → atgriezies pie Q11 GAP, pārrēķini
> - Iesprūst Q32 (cena) → 3. Paredzēšana nav locked → izdarī Q21.5 Hope Break vēlreiz
> - Iesprūst Q40 (close) → 5. Iztēlošanās nav locked → atgriezies pie Q23 Bridge ar konkrētiem 12 mēnešu skaitliem

---

## 8.3 · DETALIZĒTI PA SOĻIEM

### Solis 1 · ATPAZĪŠANA (System 1)

**Klienta iekšējs jautājums:** *"Tas, ko viņš tikko teica, atbilst manai sajūtai?"*

**Operatora uzdevums:** Pārliecināties, ka **Q4 Galvenā lieta** ir **klienta paša vārdiem**, ne mūsu interpretācijā. Ja Q4 ir *"reklāmas izmaksas par augstas"*, mēs **neatbildam** ar *"jā, mēs to atrisinām ar META"*. Mēs atbildām: *"Pareizi, tev šobrīd reklāmas izmaksas izskatās tā, ka tās aug, bet rezultāti nē. Skaidrs, vai mēs to fiksējam pareizi?"*

> **Aizliegumi:** Pārformulēt klienta sāpi mūsu vārdos. Tas atver System 2 ("vai šis cilvēks mani saprata?") un slēdz System 1.

### Solis 2 · MĒRĪŠANA (System 2)

**Klienta iekšējs jautājums:** *"Cik tas man maksā šobrīd?"*

**Operatora uzdevums:** Q11 GAP piezīme ar **konkrētu skaitli** (€5000 mēnesī starp mērķi un realitāti) → Q21 COI rēķins (€60k gadā × 5 gadi = €300k zaudētas iespējas).

> **Triks:** Klients pats jāizskaitļo cipars, ne mēs. *"Tu teici, gribi €25k mēnesī. Šobrīd tev ir €18k. Atstarpe €7k. Cik mēnesi tev šī sastrūk?"* — klients pats saka *"6 mēnesi"* → tu tikai pieliec: *"€42k zaudētu peļņu pēdējā pusgadā. Pareizi?"*

### Solis 3 · PAREDZĒŠANA (System 2 + Q21.5 ⚡)

**Klienta iekšējs jautājums:** *"Vai tas turpināsies, ja es neko nedaru?"*

**Operatora uzdevums:** **Hope Break.** Detalizētāk Daļā IX. Trīs jautājumi:
1. *"Tu to apzināti aizpildi vai gaidi?"*
2. *"Tas 'gan jau' — kā tas pēdējos 6 mēnešos strādāja?"*
3. *"Ja nākamās 2 nedēļas vajadzētu klāt 5 klientus — tu zini, kā?"*

> **Tas ir vienīgais V13 LOAD‑BEARING mezgls.** Ja izlaists, klients **vēl turpina cerēt**, ka pats no sevis kaut kas mainīsies. Bez Hope Break, cena (Q32) izklausās kā vēl viens izdevums, ne kā glābšana.

### Solis 4 · SALĪDZINĀŠANA (System 2)

**Klienta iekšējs jautājums:** *"Vai ir labāks ceļš nekā tas, ko viņš piedāvā?"*

**Operatora uzdevums:** Q18 Zelta jautājums (*"Pirms cik gadiem tu lēmumu pieņēmi galvā?"*) → klients atbild *"3 gadi"* → Q22 Investora rāmis (*"3 gadi × €60k = €180k zaudēta iespēja. Šī sistēma maksā €3000."*).

> **Triks:** Ja klients prasa *"Kāda ir alternatīva?"*, atbildi tieši: *"Alternatīva, kuru tu jau esi izmēģinājis 3 gadus — gaidīšana. Tas tev ir maksājis €180k. Šis ir cits ceļš."*

### Solis 5 · IZTĒLOŠANĀS (System 1)

**Klienta iekšējs jautājums:** *"Vai es spēšu paveikt to, ko viņš piedāvā?"*

**Operatora uzdevums:** Q23 Bridge ar **konkrētu klienta valodu** (*"Iedomājies pēc 12 mēnešiem — tev nāk 5 pieteikumi nedēļā, automātiski. Tu vairs neatbildi katram pa atsevišķi. Tu skaties skaitļus piektdienas vakarā un saproti, ka šī mēnesi pelnīji €40k."*) + Q26 3 pīlāri (Vilka metode + Sistematizācija + CRM).

> **NLP slānis:** Future pacing un Embedded Commands (sk. Daļa V) tieši šeit. *"Un kad tu jūti, ka tas ir pareizi, tad mēs vienkārši sakārtojam."*

### Solis 6 · VALIDĀCIJA (System 2)

**Klienta iekšējs jautājums:** *"Vai šis viss ir reāls? Vai es nesabrukšu, ja sāku?"*

**Operatora uzdevums:** Q29 1–10 anchor pirms cenas (*"1–10. 1 ir nepaņemtu par velti, 10 ir tieši tas. Kā novērtē?"*) → Q30 gatavības apstiprinājums (*"Ja viss tev šķiet pareizi, vai tu šodien gatavs sākt?"*) → Q31 onboarding ieskats (*"Pirmajās 7 dienās tev tikai jāatbildedz uz manu kalendāru, un mēs sakārtojam Facebook lapas, META kontu, Telegram CRM."*).

> **Aizliegumi:** Apsolīt rezultātus. *"Tu pirmajā mēnesī taisīsi €40k"* — nē. Sēdi onboarding mehānismā, ne tirgus rezultātā. Tu kontrolē sistēmu, ne tirgu.

### Solis 7 · KOMUTĒŠANA (System 1)

**Klienta iekšējs jautājums:** *"Esmu gatavs."*

**Operatora uzdevums:** Q32 cena (2 opcijas) + KLUSUMS → ja klients teic *"jā"* → Q40 *"Karti vai pārskaitījumu?"*

> **Tehnika:** **Klusums pēc cenas ir komutēšanas slānis.** Ja tu pārtrauc klusumu, tu pārtrauci klienta lēmumu pieņemšanu. Tev nav steiga.

---

## 8.4 · KAS V14.1 NEBIJA, V15 PIEVIENO

V14.1 Q1–Q40 plūsma ir **horizontāli plakana** — viens jautājums seko otram. V15 algoritms pievieno **vertikālu skatījumu**: katrs jautājums **arī** nosaka **kuru lēmumu pieņemšanas soli klients tagad iziet**. Tas ļauj operatorā:

1. **Diagnoses iesprūdas** ne tikai "klients pretestās", bet "klients iesprūdis 4. solī (Salīdzināšana)"
2. **Maršrutēt iebildumus** ne tikai pēc CARE, bet pēc soļa, kuru jāatkārto
3. **Pārtraukt zvanu**, ja klients ir 1. vai 2. solī un nevar pāriet uz 3+ — tas ir nekvalificētss leads, ne pārdošanas kļūda

> **Ekonomiska iebilde:** Šī papildu vertikālā kartes sapratne **nepalielina** Q1–Q40 garumu. Tā tikai dod operatoram **trešo dimensiju** zvana laikā.

---

## 8.5 · LAURIS PERSONĪGAIS PIETIKUMS NO AUDIO

> No NotebookLM analīzes (88 min audio): *"Sales Engine ir buvēta, analizējot 89 reālos dzīvus pārdošanas zvanus. Astoņdesmit deviņus. Kur cilvēki vienkārši mēļu, kur viņi slēpiekas pieklājības, un kur viņi patiesībā pieņem lēmumu. Tā sistēma sanāk tāda kā lielā arhitektūra ar sešiem slāņiem, 40 jautājumiem, un 14 patentētajiem loģikas mezgliem."*

**Iekšējais skats no Lauris:** Sales Engine **nav improvizācija** — nekādas toksiskas pārliecinošas tehnikas, nekādas pārmācīšanas. Tā vietā ir **algoritms**. Operatorā nav vietas haosa.

> **Galvenais princips:** Kad operatos sēž System 2 stāvoklī (analizē, plāno, mēģina pārliecināt), klienta System 2 **automātiski bloķē**. Klients meklē iemeslu, kāpēc atteikt. Operators **var pacelt** klienta System 1 (instinkta, emocionālā) tikai ja **viņš pats** ir System 1 stāvoklī — bez vajadzības, bez bailēm, bez ego. Tas ir V∞ stāvoklis.

---

## 8.6 · ALGORITMS KĀ ANTIDOTS HAOSAM

> *"Tu neesi pārdevējs. Tu esi sistēmas arhitekts. Tu nemēģini pārliecināt. Tu izpildi diagnostikas algoritmu. Klients sevi pārdod pats, mūsu darbs ir tikai turēt struktūru."*

V15 lēmumu algoritms ir mūsu **anti‑haosa instruments**:
- Bez tā: *"Klients nepērk → es nezinu kāpēc → mēģinu vēl skaļāk pārliecināt → klienta System 2 vēl ciešāk slēdzas"*
- Ar to: *"Klients nepērk → es zinu, ka iesprūdis 3. solī (Paredzēšana) → atgriežos pie Q21.5 Hope Break, izdaru pareizi → klients pāriet uz 4. soli"*

> **Šī ir Sales Engine V14.1 dziļākā loģika, V15 versijā padarīta eksplicīta.**

---
