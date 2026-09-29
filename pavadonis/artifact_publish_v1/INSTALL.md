# artifact_publish_v1: uzstādīšana Office PC

Uzstāda **cilvēks ar savām tiesībām** pēc koda pārskatīšanas. Aģents to nedara
un neapiet platformas drošības kontroli.

Precīzs failu saraksts un kontrolsummas: [`FILES.md`](FILES.md). Atsaukšana:
[`ROLLBACK.md`](ROLLBACK.md).

## 1. Ko adapteris dara

`ArtifactPublishV1Adapter.execute(spec)` pēc kārtas:

1. no `spec` paņem 6 payload laukus: `source_path`, `expected_sha256`,
   `expected_size`, `provider`, `destination`, `file_name`;
2. pārbauda `provider` un `destination` pret allowlist, `file_name`, un
   pārbauda, ka `source_path` ir absolūts ceļš, bez `..` un saitēm, parasts fails
   zem `allow_roots`, ar atļautu paplašinājumu un ≤ `max_bytes`;
3. pārbauda, ka approval ir piesaistīts **tieši šī payload** digest
   (`payload_digest(payload)`, SHA256 no kanoniska JSON);
4. vienreiz nolasa failu, aprēķina SHA256 un izmēru, salīdzina ar `expected_*`
   (**pirms** upload) un augšupielādē tieši šos baitus;
5. idempotence: Drive failam pievieno `appProperties.pav_idem =
   sha256(sha256|provider|destination|file_name)`; retry vispirms meklē šo atslēgu
   un, ja atrod vienu failu, augšupielādi neatkārto (divi vai vairāk failu → BLOCKED);
6. veic svaigu Drive metadata readback un salīdzina `id`, `name`, `size`,
   `parents`, `trashed=false`, `pav_idem` un `sha256Checksum`
   (ja tā nav, tad `md5Checksum`; ja nav neviena, tad BLOCKED);
7. atgriež `result_factory(result=..., evidence=..., artifacts=...)`.

Jebkura kļūme izraisa `ArtifactPublishBlocked(reason, evidence)`. Rezultāts nekad
nav DONE vai VERIFIED. `adapter.verify(result)` veic vēl vienu neatkarīgu readback
un atgriež `{"verified": bool, ...}`. Tas nemet izņēmumu.

`result` satur šādus laukus: `provider, source_path, sha256, md5, bytes, file_id,
file_name, destination, url, idempotency_key, reused_existing, readback, compare`.
`artifacts` satur `[{type, file_id, url, source_sha256}]`. Tokeni un credentials
nekur netiek glabāti.

## 2. Integrācijas robežas: kas jāpievieno PAVADONIS pusē

PAVADONIS kodu es neredzēju, tāpēc šie 5 punkti ir jāsasaista ar reālajām
PAVADONIS funkcijām. Adapteris nemin, kā tās izskatās.

| # | Robeža | Ko nodot | Kur PAVADONIS to paskatīties |
|---|---|---|---|
| B1 | `result_factory` | PAVADONIS `ExecutionResult` klase (`result, evidence, artifacts`) | kā to izveido `atomic_text_file_v1` |
| B2 | `approval_verifier(digest, payload) -> bool` | funkcija, kas atgriež `True` tikai tad, ja approval gate apstiprinājums ir piesaistīts šim `digest` | `execute_claim()` approval gate |
| B3 | `payload_from_spec(spec)` | kā no `spec` iegūt 6 laukus (noklusējums: pats `spec`) | ko `execute_claim()` padod `adapter.execute(spec)` |
| B4 | `GoogleDriveClient(access_token_provider)` | funkcija, kas atgriež derīgu OAuth access token no esošās credential glabātuves | kur PAVADONIS/Interconnect glabā Google credentials |
| B5 | BLOCKED un verify | `ArtifactPublishBlocked` jāpārvērš par BLOCKED; `verify_task()` jāizsauc `adapter.verify(result)` un jāatzīmē VERIFIED tikai, ja `verified is True` | kā `execute_claim()`/`verify_task()` apstrādā esošo adapteru kļūdas un readback |

Ja B2 nevar izpildīt, jo approval gate nepiesaista approval konkrētam payload,
**neuzstādi adapteri**: tā ir obligāta robeža, nevis opcija.

Drive scope: `https://www.googleapis.com/auth/drive.file` ir šaurākais, bet ar to
var rakstīt tikai mapēs, kurām lietotne ir piekļuvusi. Ja augšupielāde mērķa mapē
atgriež `notFound`, izmanto šīs lietotnes izveidotu mapi, nevis paplašini scope.

### Reģistrācijas paraugs `ProductionWorker.__init__()`

Vārdi `<...>` ir jāaizstāj ar reālajiem PAVADONIS nosaukumiem (B1–B4).
Capability ieraksta formu nokopē no `atomic_text_file_v1` ieraksta, un neizdomā to.

```python
from artifact_publish_v1 import (ADAPTER_NAME, ArtifactPublishConfig,
                                 ArtifactPublishV1Adapter, GoogleDriveClient)

self.adapters[ADAPTER_NAME] = ArtifactPublishV1Adapter(
    ArtifactPublishConfig.from_file(r"<PAVADONIS>\config\artifact_publish_v1.json"),
    drive_client=GoogleDriveClient(access_token_provider=<B4>),
    approval_verifier=<B2>,
    result_factory=ExecutionResult,          # B1
    payload_from_spec=<B3 vai izlaist>,
)
self.capabilities[ADAPTER_NAME] = <tāda pati forma kā atomic_text_file_v1>
```

## 3. Soļi (PowerShell)

```powershell
$PAV   = "<mape, kurā ir production_worker.py>"
$REPO  = "C:\src\Pardosana"
$STAMP = Get-Date -Format "yyyyMMdd-HHmmss"

# 1. Esošā testu komplekta bāzes līnija (PIRMS izmaiņām) — saglabā rezultātu
cd $PAV; <PAVADONIS testu komanda> *> "$env:TEMP\pav-tests-before-$STAMP.txt"

# 2. Rezerves kopija
Copy-Item -Recurse $PAV "$PAV.backup-$STAMP"

# 3. Pārbaudi failu kontrolsummas pret FILES.md
Get-ChildItem -Recurse "$REPO\pavadonis\artifact_publish_v1" -File |
  Get-FileHash -Algorithm SHA256 | Format-Table Hash, Path

# 4. Adaptera testi izolēti
cd "$REPO\pavadonis"; python -m unittest discover -t . -s artifact_publish_v1\tests -v

# 5. Kopē paketi blakus production_worker.py (vai tur, kur ir esošie adapteri)
Copy-Item -Recurse "$REPO\pavadonis\artifact_publish_v1" "$PAV\artifact_publish_v1"
Remove-Item -Recurse -Force "$PAV\artifact_publish_v1\tests"   # testi nav jāizvieto

# 6. Konfigurācija: īsta Drive mapes ID; allow_roots tik šauri, cik iespējams
Copy-Item "$REPO\pavadonis\artifact_publish_v1\config.example.json" "<konfigurācijas ceļš>"
```

7. Pievieno reģistrācijas bloku (2. sadaļa) `ProductionWorker.__init__()`.
8. **8. tests**: palaid **visu** PAVADONIS testu komplektu vēlreiz un salīdzini ar
   1. soli. Tam jābūt tādam pašam vai labākam, un `atomic_text_file_v1`,
   `sorsora_test_record_v1`, `browser_ui_v1` jāiziet. Ja kaut kas pasliktinās,
   izpildi [`ROLLBACK.md`](ROLLBACK.md).
9. Restartē worker un Commander.

## 4. Pirmais acceptance darbs

Fails `C:\Users\User\Downloads\Ritvars_CRM_2026-09-29.png`, pēdējais
verificētais izmērs ir 164724 baiti. SHA256 aprēķini uz PC, jo es to neminu:

```powershell
$f = "C:\Users\User\Downloads\Ritvars_CRM_2026-09-29.png"
(Get-Item $f).Length                                  # jābūt 164724
(Get-FileHash $f -Algorithm SHA256).Hash.ToLower()
```

Payload, kuram dod approval:

```json
{
  "source_path": "C:\\Users\\User\\Downloads\\Ritvars_CRM_2026-09-29.png",
  "expected_sha256": "<Get-FileHash rezultāts>",
  "expected_size": 164724,
  "provider": "google_drive",
  "destination": "<allowlist Drive mapes ID>",
  "file_name": "Ritvars_CRM_2026-09-29.png"
}
```

Pieņemšanas kritēriji:
- `result.compare.match == true`, `bytes == 164724`, `sha256` sakrīt;
- `adapter.verify(result).verified == true`, un tikai pēc tam VERIFIED;
- darba atkārtošana dod to pašu `file_id`, `reused_existing == true`, un Drive
  mapē ir tikai viens fails.

Piezīme: `allow_roots` ar visu `Downloads` mapi ir plašs. Ierobežo to ar
approval piesaisti, bet pēc acceptance labāk izmantot atsevišķu mapi, piemēram,
`C:\Users\User\PAVADONIS_publish`.
