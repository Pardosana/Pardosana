# artifact_publish_v1: atsaukšana

Adapteris neko nedzēš Drive un nemaina esošos PAVADONIS failus, izņemot vienu
reģistrācijas bloku.

## A. Atslēgt adapteri (ātri, bez failu dzēšanas)

1. `ProductionWorker.__init__()` izdzēs vai aizkomentē `self.adapters[ADAPTER_NAME] = ...`
   un `self.capabilities[ADAPTER_NAME] = ...` rindas un `from artifact_publish_v1 import ...`.
2. Restartē worker un Commander.
3. Palaid PAVADONIS testu komplektu; rezultātam jāsakrīt ar bāzes līniju
   (INSTALL.md 1. solis).

Jauni `artifact_publish_v1` darbi tagad netiek izpildīti. Esošie adapteri paliek neskarti.

## B. Noņemt pilnībā

```powershell
Remove-Item -Recurse -Force "$PAV\artifact_publish_v1"
Remove-Item "<konfigurācijas ceļš>\artifact_publish_v1.json"
```

## C. Pilna atgriešana no rezerves kopijas

```powershell
# Aptur worker/Commander pirms šī
Rename-Item $PAV "$PAV.failed-$(Get-Date -Format yyyyMMdd-HHmmss)"
Copy-Item -Recurse "$PAV.backup-<STAMP>" $PAV
```

## D. Jau publicēti Drive faili

Adapteris tos nedzēš automātiski. Ja fails jāizņem, to manuāli dara cilvēks
Drive saskarnē. Failu atpazīst pēc `file_id` darba rezultātā vai pēc
`appProperties.pav_idem`. Pēc dzēšanas `verify()` atgriež `verified: false`,
un tas ir paredzēts.
