# Commander Chrome profils: ielogojies vienreiz, un tas atceras

Atsevišķs Chrome profils tikai PAVADONIS Commander vajadzībām. Tu tajā **pats
vienreiz** pieslēdzies Instagram (un citām vajadzīgajām vietnēm). Pieteikšanās
saglabājas profilā arī pēc Chrome un datora restarta. Commander pievienojas šim
profilam caur vadības portu uz `127.0.0.1`.

## Kāpēc atsevišķs profils, nevis tavs parastais Chrome

- Kopš Chrome 136 vadības ports parastajā (noklusējuma) profilā tiek ignorēts. Tas
  ir Chrome drošības noteikums, un mēs to neapejam.
- Commander redz **tikai** šo profilu. Tavs e-pasts, banka, Drive un parastās
  cilnes tam nav pieejamas.
- Parastais Chrome netiek aizvērts vai restartēts.

## Drošības noteikumi

1. **Parole netiek glabāta nekur.** Aģents to nekad neievada un nesaņem. Tu
   pieslēdzies ar roku, arī 2FA. Saglabājas tikai vietnes sesija, tāpat kā
   parastā pārlūkā.
2. **Šajā profilā pieslēdzies tikai tiem kontiem, kas Commander patiešām
   vajadzīgi.** Jebkura programma, kas darbojas uz datora ar tavu lietotāju, var
   pievienoties portam `127.0.0.1:9223`, tātad šīm sesijām.
3. Profila mapei pirmajā reizē tiek iestatītas tiesības: tikai tavs Windows
   lietotājs un SYSTEM.
4. Ports klausās tikai uz `127.0.0.1` (Chrome noklusējums). Neatver to tīklam un
   nepievieno `--remote-debugging-address`.
5. `login-state` pārbaude atgriež tikai `true`/`false`. Sīkdatņu vērtības netiek
   nolasītas izvadei un netiek saglabātas.
6. Konta datiem (ieraksti, statistika) labāk izmanto oficiālo Meta/Instagram API.
   Pārlūks ir paredzēts tam, kam API nav.

## Uzstādīšana (cilvēks, PowerShell)

```powershell
$REPO = "C:\src\Pardosana"

# 1. Palaid Commander Chrome (pirmajā reizē izveidos profilu).
#    -ExecutionPolicy Bypass attiecas tikai uz šo vienu palaišanu (neparakstīts lokāls skripts).
powershell -ExecutionPolicy Bypass -File "$REPO\pavadonis\commander_browser\Start-CommanderChrome.ps1" `
  -StartUrl "https://www.instagram.com/"
```

2. Atvērtajā logā **pats** pieslēdzies Instagram, arī ar 2FA. Ja Instagram piedāvā
   "Saglabāt pieteikšanās informāciju", apstiprini to. Aizver logu kā parasti.
3. Palaid skriptu vēlreiz. Instagram jau jābūt pieslēgtam bez jaunas pieteikšanās.
4. Pārbaude:

```powershell
cd "$REPO\pavadonis"
python -m commander_browser status                  # "running": true
python -m commander_browser login-state instagram   # "logged_in": true (vajag Playwright)
```

5. Lai Commander Chrome startētu kopā ar Windows (neobligāti), izveido
   Task Scheduler uzdevumu "At log on" ar to pašu komandu. Tas darbojas ar tavām
   tiesībām.

## Integrācijas robeža ar `browser_ui_v1`

`browser_ui_v1` kodu es neredzēju. Tam jāpievienojas `http://127.0.0.1:9223`
(`commander_browser.cdp_endpoint()`), nevis jāpalaiž savs pārlūks, piemēram, ar
Playwright `chromium.connect_over_cdp(endpoint)` un esošo `browser.contexts[0]`.
Jāizmanto tas pats princips kā tagad, tikai pievienošanās vietā, kur tagad notiek
palaišana. Pēc šīs izmaiņas palaid visu PAVADONIS testu komplektu.

## Atsaukšana

- **Izrakstīties no vienas vietnes:** Commander Chrome logā izraksties no tās vietnes.
- **Noņemt visu:** aizver Commander Chrome logu un izdzēs profila mapi:
  ```powershell
  Remove-Item -Recurse -Force "$env:LOCALAPPDATA\PAVADONIS\commander-chrome-profile"
  ```
  Līdz ar to tiek dzēstas visas šī profila sesijas. Tavs parastais Chrome netiek ietekmēts.
- Ja izveidoji Task Scheduler uzdevumu, izdzēs to.
- Ja ir aizdomas, ka kāds piekļuvis profilam: Instagram iestatījumos izvēlies
  "Kur tu esi pieteicies" un beidz šo sesiju.

## Statuss

Kods un testi (7) iziet Linux vidē. PowerShell skripts šeit **nav palaists**, jo
šajā vidē PowerShell nav pieejams. Uz Office PC tas nav uzstādīts un nav pārbaudīts.
