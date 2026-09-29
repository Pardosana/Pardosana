# Oracle atmiņas stabilizācija (`stabilize_memory.sh`)

SSH atjaunošanas secība un pārējie rīki: [`RUNBOOK_SSH_RECOVERY.md`](RUNBOOK_SSH_RECOVERY.md).

Mazs skripts, kas **papildina** esošos PAVADONIS Oracle deploy/commission/audit skriptus
(tie ir Office PC kodā) un neko no tiem neaizstāj.

| Režīms | Ko dara |
|---|---|
| bez argumenta | **Tikai diagnostika**: OS, arhitektūra, OCI Shape, sshd versija un vai tā vispār atbalsta `PerSourcePenalties`, RAM/swap, OOM ieraksti 7 dienās, PAVADONIS servisu atmiņa, lielākie procesi. Neko nemaina. |
| `--apply` | 2 GB swap (`/swapfile.pavadonis`, `vm.swappiness=10`); sshd `OOMScoreAdjust=-1000`, lai atmiņas trūkums nenogalina SSH; `pavadonis-teltel-transcriber` `MemoryMax` = 60 % RAM (`MemoryHigh` 85 % no tā), `Restart=on-failure`. Tad READBACK/COMPARE; exit 1, ja kaut kas nesakrīt. |
| `--rollback` | Noņem visu, ko `--apply` pielika. |

Nemaina: PAVADONIS kodu, `sshd_config`/`PerSourcePenalties`, firewall, lietotājus. sshd netiek
restartēts. Pārstartē tikai transcriber, lai stātos spēkā limits.
Iestatāms: `SWAP_MB=4096`, `MEM_PCT=50`, `TRANSCRIBER_UNIT=...`.

## Secība

1. **Vispirms diagnostika**, nevis `--apply`. Tā atbild uz jautājumiem:
   - vai tiešām bija OOM un kurš process to izraisīja;
   - vai šī sshd versija vispār atbalsta `PerSourcePenalties` (tas ir tikai OpenSSH ≥ 9.8;
     Oracle Linux 8/9 standarta versijās to nav, un tad soda hipotēze atkrīt);
   - kāds ir Shape: `E2.1.Micro` (1 GB, nevar palielināt) vai `A1.Flex` (līdz 24 GB bez maksas).
2. `--apply` tikai tad, ja diagnostika rāda atmiņas trūkumu vai swap nav.
3. Ja Shape ir `A1.Flex`: OCI Console → Edit shape → vairāk RAM (Always Free kopā ≤ 4 OCPU / 24 GB).

## Kā to palaist, ja SSH vēl nestrādā

- Vienu mēģinājumu veic **no citas IP** (telefons caur mobilajiem datiem bez Wi‑Fi vai OCI Cloud
  Shell). Tad `scp` skriptu uz serveri un palaid `sudo bash stabilize_memory.sh`.
- Vai **OCI Run Command** (Instance → *Run command*), ja Oracle Cloud Agent spraudnis
  *Compute Instance Run Command* ir ieslēgts: ielīmē skripta saturu.

## Statuss

Sintakse ir pārbaudīta, diagnostikas režīms palaists Ubuntu konteinerā bez systemd (exit 0).
`--apply` un `--rollback` **nav** pārbaudīti uz īsta systemd servera un uz Oracle nav palaisti.
