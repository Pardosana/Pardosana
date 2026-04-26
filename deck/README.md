# Domino Engine V14.1 · Deck system

Šī mape ir oficiālais **prezentācijas slānis**. Tas ir atsevišķs no master skripta un no operatora kabatas kartes — tas ir tieši `PRESENTATION CARRIER` slānis no V13 6 slāņu disciplīnas.

## Saturs

- `index.html` — interaktīvs deck viewer ar 20 slaidiem, presenter notes un present mode (`F` taustiņš).
- `assets/slide-XX-*.jpeg` — Lauris paša V14 deck slaidi (avota bildes).

## Kā lietot

1. Atver `deck/index.html` pārlūkā vai deploy uz publisku URL.
2. Izvēlies slaidu kreisajā panelī vai navigē ar `←/→`.
3. Pārslēdzies uz **Present mode** (poga vai `F`) — paslēpj sānu paneli un piezīmes, paliek tikai slaids.
4. Katram slaidam ir:
   - **Mērķis** — kāpēc tas ir deck-ā,
   - **Ko šis slide dara** — operatora kustības,
   - **Tagi** — D-mezgls / fāze / kategorija,
   - **Presenter cue** — viena rinda, ko atcerēties tieši pirms tu rādi šo slaidu.

## V13 disciplīnas saderība

- `one slide = one domino` — viens slaids reprezentē tikai vienu mezglu vai vienu kustību.
- `viena metafora uz vienu call` — deck-s satur vairākas metaforas, bet vienā zvanā operators izvēlas **vienu** dominējošo (krasts → tilts → kalns vai ūdens vai dakša). Pārējos slaidus tas zvans nelieto.
- `current cork protected` — operatora kabatas karte (1 lapa) NEKAD nesatur deck saturu. Deck dzīvo te.
- `presentation carrier` slāni iesēž tikai tad, kad ir share-screen vai whiteboard situācija. Telefona zvanā šie slaidi paliek operatora datorā kā vizuāls atgādinājums, neatklāti klientam.

## Kā paplašināt

- Lai pievienotu jaunu slaidu, ieliec attēlu `assets/` mapē un pievieno entry `index.html` `slides` masīvam.
- Saglabā `goal / moves / tags / cue` struktūru — citādi presenter mode kļūst inkonsekvents.
- A/B varianti (piemēram, `D13 v1` vs `D13 v2`) lai dzīvo kā divi atsevišķi entry, ne kā viens slide ar overlay.
