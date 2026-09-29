#!/usr/bin/env bash
# PAVADONIS Oracle vienreizēja atkopšana (palaist uz servera: SSH, Cloud Shell vai OCI Run Command).
#
#   sudo bash recover_once.sh            # tikai pierādījumi (noklusējums, neko nemaina)
#   sudo bash recover_once.sh --apply    # + aptur transcriber TIKAI ja pierādīts OOM vaininieks;
#                                        #   + sshd: `sshd -t` → reload (vai start, ja neaktīvs)
#
# Nav cilpu. Otrs palaidiens 15 min laikā tiek atteikts (FORCE=1 to atļauj apzināti).
# Nemaina: sshd_config, firewall, PAVADONIS kodu; transcriber tiek APTURĒTS, nevis atslēgts.
set -euo pipefail
MODE="${1:---diagnose}"
case "$MODE" in --diagnose|--apply) ;; *) echo "Nezināms režīms: $MODE"; exit 2;; esac
[[ $EUID -eq 0 ]] || { echo "Palaid ar sudo."; exit 2; }

STATE=/var/lib/pavadonis; mkdir -p "$STATE/evidence"
MARK="$STATE/recover_once.last"
TRANSCRIBER_UNIT="${TRANSCRIBER_UNIT:-pavadonis-teltel-transcriber.service}"
OOM_SHARE_PCT="${OOM_SHARE_PCT:-40}"
if [[ "$MODE" == --apply && -f "$MARK" && "${FORCE:-0}" != 1 ]]; then
  age=$(( $(date +%s) - $(stat -c %Y "$MARK") ))
  if (( age < 900 )); then echo "ATTEIKTS: pēdējais --apply pirms ${age}s (<15 min). FORCE=1, ja apzināti."; exit 3; fi
fi
exec 9>/run/pavadonis-recover.lock; flock -n 9 || { echo "Jau darbojas cits recover_once."; exit 3; }

TS=$(date -u +%Y%m%dT%H%M%SZ); EV="$STATE/evidence/recover-$TS.txt"
SSH_UNIT=sshd.service; systemctl cat sshd.service >/dev/null 2>&1 || SSH_UNIT=ssh.service
log() { printf '%s\n' "$*" | tee -a "$EV"; }
sec() { log ""; log "== $* =="; }
run() { { "$@" 2>&1 || true; } | tee -a "$EV"; }

sec "BEFORE $TS"
run uptime; run free -m; run swapon --show
sec "sshd"; run systemctl is-active "$SSH_UNIT"; run sshd -V
sec "OOM kodola žurnālā (24h)"
OOM=$(journalctl -k --since '-24 hours' --no-pager 2>/dev/null | grep -iE 'out of memory|oom-kill|killed process' || true)
log "${OOM:-(nav)}"
sec "Transcriber"
TR_ACTIVE=$(systemctl is-active "$TRANSCRIBER_UNIT" 2>/dev/null || true); log "active: ${TR_ACTIVE:-nav}"
TR_MEM=$(systemctl show -p MemoryCurrent --value "$TRANSCRIBER_UNIT" 2>/dev/null || echo "")
MEM_TOTAL=$(awk '/MemTotal/ {print $2*1024}' /proc/meminfo)
TR_PCT=0; [[ "$TR_MEM" =~ ^[0-9]+$ ]] && TR_PCT=$(( TR_MEM * 100 / MEM_TOTAL ))
log "MemoryCurrent: ${TR_MEM:-?} (${TR_PCT}% RAM)"
sec "Lielākie procesi"; run bash -c "ps -eo pid,rss,comm --sort=-rss | head -8"

# Pierādījums, ka transcriber ir vaininieks: OOM ieraksts min tā unit, VAI tas patērē >= OOM_SHARE_PCT % RAM.
CULPRIT=no
if [[ "$TR_ACTIVE" == active ]]; then
  if grep -q "${TRANSCRIBER_UNIT%.service}" <<<"$OOM" || (( TR_PCT >= OOM_SHARE_PCT )); then CULPRIT=yes; fi
fi
sec "SECINĀJUMS"; log "transcriber_culprit=$CULPRIT  sshd=$(systemctl is-active "$SSH_UNIT" || true)"

if [[ "$MODE" == --diagnose ]]; then log ""; log "Diagnostika: $EV (nekas nav mainīts)"; exit 0; fi

touch "$MARK"
sec "ACTION"
if [[ $CULPRIT == yes ]]; then
  systemctl stop "$TRANSCRIBER_UNIT"; log "transcriber APTURĒTS (nav atslēgts)."
else
  log "transcriber netiek aiztikts (nav pierādījuma)."
fi
if sshd -t 2>>"$EV"; then
  if systemctl is-active -q "$SSH_UNIT"; then systemctl reload "$SSH_UNIT"; log "sshd reload (konfigurācija derīga)."
  else systemctl start "$SSH_UNIT"; log "sshd start (bija neaktīvs)."; fi
else
  log "sshd -t NEIZDEVĀS — sshd netiek restartēts. Labo konfigurāciju ar roku."
fi

sec "AFTER / COMPARE"
fail=0
chk() { if eval "$2"; then log "PASS  $1"; else log "FAIL  $1"; fail=1; fi; }
chk "sshd aktīvs" "systemctl is-active -q $SSH_UNIT"
chk "sshd klausās portā 22" "ss -ltn 2>/dev/null | grep -qE ':22\\b'"
[[ $CULPRIT == yes ]] && chk "transcriber apturēts" "! systemctl is-active -q $TRANSCRIBER_UNIT"
run free -m
log ""; log "Evidence: $EV"
log "NĀKAMAIS: viens jauns SSH no Office PC (Probe-OracleSshOnce.ps1). VERIFIED tikai pēc tā."
exit $fail
