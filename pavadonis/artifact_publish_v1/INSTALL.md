# artifact_publish_v1: manuāla uzstādīšana

Šo moduli uzstāda **cilvēks ar savām tiesībām** uz Office PC pēc koda pārskatīšanas.
Aģenti to neuzstāda: platformas drošības kontrole to bloķē, un tā tas arī ir paredzēts.

## Ko modulis dara

Paņem sarakstu ar failiem no `source_root` un publicē tos kā **jaunu, nemainīgu versiju**
mapē `target_root/<name>/<version>/`, pievienojot `manifest.json` ar sha256 kontrolsummām.
Aktīvo versiju norāda `target_root/<name>/current.json`.

- Pēc noklusējuma **dry-run**: tikai pārbauda un parāda, ko publicētu, neko neraksta.
- **Nav tīkla piekļuves**, nav ārējo atkarību (tikai Python ≥ 3.10 standarta bibliotēka).
- **Neko nepārraksta un nedzēš.** Atsaukšana (rollback) tikai pārslēdz `current.json`.
- Noraida: `..` ceļus, absolūtus ceļus, simboliskās saites, neatļautus failu tipus
  (piem., `.exe`, `.ps1`, `.bat`), dublikātus, pārklājošas `source_root`/`target_root`,
  failus > 100 MB, kopā > 500 MB vai > 500 failus.

## Pieņēmumi par PAVADONIS (pārbaudi pirms uzstādīšanas!)

PAVADONIS saskarnes specifikāciju es neredzēju, tāpēc pieņēmu šo:

1. Job-bus handleris ir Python funkcija `handle(job: dict) -> dict`.
2. Job formāts: `{"type": "artifact_publish_v1", "id": "...", "payload": {...}}`
   (pilns apraksts ir `core.py` augšā).
3. Handleri reģistrē pēc `type` vērtības.

Ja PAVADONIS dara citādi, pielāgo tikai reģistrācijas vietu vai uztaisi plānu adapteri,
nevis `core.py` drošības pārbaudes.

## Uzstādīšanas soļi (Windows, PowerShell)

```powershell
# 0. Mainīgie: pielāgo savai instalācijai
$PAV   = "C:\PAVADONIS"                 # esošā PAVADONIS mape
$REPO  = "C:\src\Pardosana"             # šī repo klons
$STAMP = Get-Date -Format "yyyyMMdd-HHmmss"

# 1. Rezerves kopija PIRMS jebkādām izmaiņām
Copy-Item -Recurse $PAV "$PAV.backup-$STAMP"

# 2. Pārbaudi moduli izolēti (no repo saknes)
cd $REPO
python -m unittest pavadonis.artifact_publish_v1.tests.test_core -v

# 3. Nokopē moduli (nemaina nevienu esošu PAVADONIS failu)
New-Item -ItemType Directory -Force "$PAV\jobs\artifact_publish_v1" | Out-Null
Copy-Item "$REPO\pavadonis\artifact_publish_v1\*.py" "$PAV\jobs\artifact_publish_v1\"

# 4. Izveido publicēšanas mapi (ārpus darba mapes!)
New-Item -ItemType Directory -Force "$PAV\publish" | Out-Null
```

5. **Reģistrē handleri PAVADONIS job-bus**: vienīgā rinda, kas maina esošo kodu.
   Piemērs (pielāgo PAVADONIS reģistra formai):

   ```python
   from jobs.artifact_publish_v1 import JOB_TYPE, handle
   JOB_HANDLERS[JOB_TYPE] = handle
   ```

6. Restartē PAVADONIS Commander.

## Pārbaude pēc uzstādīšanas

1. Esošie job tipi joprojām strādā (palaid vienu parastu job).
2. Dry-run job ar vienu nekaitīgu failu atgriež `"ok": true, "dry_run": true`,
   un `publish` mapē nekas neparādās.
3. Tas pats job ar `"dry_run": false` izveido `publish\<name>\<version>\manifest.json`.
4. Job ar `"files": ["..\\kaut kas.txt"]` atgriež `"ok": false`.

CLI pārbaudei bez job-bus:

```powershell
python -m pavadonis.artifact_publish_v1 --job job.json
python -m pavadonis.artifact_publish_v1 --rollback C:\PAVADONIS\publish deck
```

## Atsaukšana

- **Publikācijas atsaukšana:** `--rollback TARGET_ROOT NAME [VERSION]`.
- **Moduļa noņemšana:** izdzēs reģistrācijas rindu (5. solis), izdzēs
  `$PAV\jobs\artifact_publish_v1`, restartē Commander.
- **Pilna atgriešana:** aizstāj `$PAV` ar `$PAV.backup-<STAMP>`.

## Statuss

Kods ir uzrakstīts un notestēts Linux vidē. **Uz Office PC tas nav uzstādīts**
un nav pārbaudīts pret īsto PAVADONIS job-bus.
