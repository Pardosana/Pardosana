#!/usr/bin/env bash
# PAVADONIS Oracle atmiņas stabilizācija — papildina esošos deploy skriptus, neaizstāj tos.
#
#   sudo bash stabilize_memory.sh              # tikai diagnostika (noklusējums, neko nemaina)
#   sudo bash stabilize_memory.sh --apply      # swap + sshd OOM aizsardzība + transcriber atmiņas limits
#   sudo bash stabilize_memory.sh --rollback   # noņem visu, ko --apply pielika
#
# Ko NEdara: nemaina PAVADONIS kodu, sshd_config/PerSourcePenalties, firewall, lietotājus;
# nerestartē sshd; neaptur nevienu servisu (tikai restartē transcriber ar jauno limitu).
set -euo pipefail

MODE="${1:---diagnose}"
SWAPFILE=/swapfile.pavadonis
SWAP_MB="${SWAP_MB:-2048}"
TRANSCRIBER_UNIT="${TRANSCRIBER_UNIT:-pavadonis-teltel-transcriber.service}"
MEM_PCT="${MEM_PCT:-60}"   # transcriber MemoryMax = 60% no RAM
TAG="pavadonis-stabilize"
SYSCTL_FILE=/etc/sysctl.d/90-${TAG}.conf

say()  { printf '%s\n' "$*"; }
hdr()  { printf '\n== %s ==\n' "$*"; }
fail=0; check() { if eval "$2"; then say "PASS  $1"; else say "FAIL  $1"; fail=1; fi; }

[[ $EUID -eq 0 ]] || { say "Palaid ar sudo."; exit 2; }
case "$MODE" in --diagnose|--apply|--rollback) ;; *) say "Nezināms režīms: $MODE"; exit 2;; esac

SSH_UNIT=sshd.service
systemctl cat sshd.service >/dev/null 2>&1 || SSH_UNIT=ssh.service
mem_mb=$(awk '/MemTotal/ {print int($2/1024)}' /proc/meminfo)
have_unit() { systemctl cat "$1" >/dev/null 2>&1; }

diagnose() {
  hdr "Sistēma"
  . /etc/os-release 2>/dev/null && say "OS: ${PRETTY_NAME:-?}"; say "Arch: $(uname -m)"
  say "Shape: $(curl -sf -m 3 -H 'Authorization: Bearer Oracle' http://169.254.169.254/opc/v2/instance/shape 2>/dev/null || echo '? (nav OCI metadatu)')"
  if ! command -v sshd >/dev/null; then
    say "sshd: nav atrasts"
  elif sshd -T 2>/dev/null | grep -qi '^persourcepenalties'; then
    say "sshd: $(sshd -V 2>&1 | head -1)   unit: $SSH_UNIT"
    say "PerSourcePenalties: ATBALSTĪTS ($(sshd -T 2>/dev/null | grep -i '^persourcepenalties ' || true))"
  else
    say "sshd: $(sshd -V 2>&1 | head -1)   unit: $SSH_UNIT"
    say "PerSourcePenalties: nav šajā OpenSSH versijā — sods kā cēlonis maz ticams"
  fi
  hdr "Atmiņa"; free -m; swapon --show || true
  hdr "OOM pēdējās 7 dienās"
  journalctl -k --since '-7 days' --no-pager 2>/dev/null | grep -iE 'out of memory|oom-kill|killed process' | tail -20 || say "(nav atrasts vai journal nav pieejams)"
  hdr "PAVADONIS servisi (atmiņa)"
  { systemctl list-units --type=service --all --no-legend 'pavadonis*' 2>/dev/null || true; } | awk '{print $1}' | while read -r u; do
    [[ -n "$u" ]] || continue
    printf '%-45s %-10s MemoryCurrent=%s MemoryMax=%s\n' "$u" "$(systemctl is-active "$u" || true)" \
      "$(systemctl show -p MemoryCurrent --value "$u")" "$(systemctl show -p MemoryMax --value "$u")"
  done || true
  hdr "Lielākie procesi (RSS MB)"
  ps -eo rss,comm --sort=-rss | head -8 | awk 'NR==1{print "RSS_MB COMMAND";next}{printf "%6d %s\n",$1/1024,$2}'
}

apply() {
  hdr "Swap ${SWAP_MB} MB"
  if swapon --show=NAME --noheadings | grep -qx "$SWAPFILE"; then say "jau aktīvs"
  else
    [[ -f $SWAPFILE ]] || { fallocate -l "${SWAP_MB}M" "$SWAPFILE" 2>/dev/null || dd if=/dev/zero of="$SWAPFILE" bs=1M count="$SWAP_MB" status=none; }
    chmod 600 "$SWAPFILE"; mkswap "$SWAPFILE" >/dev/null; swapon "$SWAPFILE"
  fi
  grep -q "^$SWAPFILE " /etc/fstab || echo "$SWAPFILE none swap sw 0 0 # $TAG" >> /etc/fstab
  printf 'vm.swappiness=10\n' > "$SYSCTL_FILE"; sysctl -q -p "$SYSCTL_FILE"

  hdr "sshd aizsardzība pret OOM ($SSH_UNIT)"
  mkdir -p "/etc/systemd/system/$SSH_UNIT.d"
  printf '[Service]\nOOMScoreAdjust=-1000\n' > "/etc/systemd/system/$SSH_UNIT.d/90-$TAG.conf"
  say "drop-in ierakstīts; stāsies spēkā nākamajā sshd startā (sshd netiek restartēts)"

  hdr "Transcriber atmiņas limits"
  if have_unit "$TRANSCRIBER_UNIT"; then
    max=$(( mem_mb * MEM_PCT / 100 )); high=$(( max * 85 / 100 ))
    mkdir -p "/etc/systemd/system/$TRANSCRIBER_UNIT.d"
    printf '[Service]\nMemoryHigh=%sM\nMemoryMax=%sM\nOOMScoreAdjust=500\nRestart=on-failure\nRestartSec=30\n' "$high" "$max" \
      > "/etc/systemd/system/$TRANSCRIBER_UNIT.d/90-$TAG.conf"
    systemctl daemon-reload
    systemctl is-active -q "$TRANSCRIBER_UNIT" && systemctl restart "$TRANSCRIBER_UNIT"
    say "MemoryMax=${max}M MemoryHigh=${high}M"
  else
    systemctl daemon-reload; say "$TRANSCRIBER_UNIT nav atrasts — izlaists"
  fi
  readback
}

readback() {
  hdr "READBACK / COMPARE"
  check "swap aktīvs"               "swapon --show=NAME --noheadings | grep -qx '$SWAPFILE'"
  check "swap fstab ieraksts"       "grep -q '^$SWAPFILE ' /etc/fstab"
  check "vm.swappiness=10"          "[[ \$(sysctl -n vm.swappiness) == 10 ]]"
  check "sshd OOMScoreAdjust=-1000" "[[ \$(systemctl show -p OOMScoreAdjust --value $SSH_UNIT) == -1000 ]] || grep -q 'OOMScoreAdjust=-1000' /etc/systemd/system/$SSH_UNIT.d/90-$TAG.conf"
  check "sshd joprojām aktīvs"      "systemctl is-active -q $SSH_UNIT"
  if have_unit "$TRANSCRIBER_UNIT"; then
    check "transcriber MemoryMax iestatīts" "[[ \$(systemctl show -p MemoryMax --value $TRANSCRIBER_UNIT) != infinity ]]"
  fi
  [[ $fail -eq 0 ]] && say "RESULT: PASS" || { say "RESULT: FAIL"; exit 1; }
}

rollback() {
  hdr "Rollback"
  swapon --show=NAME --noheadings | grep -qx "$SWAPFILE" && swapoff "$SWAPFILE"
  rm -f "$SWAPFILE" "$SYSCTL_FILE"
  sed -i "\#^$SWAPFILE .*# $TAG\$#d" /etc/fstab
  rm -f "/etc/systemd/system/$SSH_UNIT.d/90-$TAG.conf" "/etc/systemd/system/$TRANSCRIBER_UNIT.d/90-$TAG.conf"
  systemctl daemon-reload
  have_unit "$TRANSCRIBER_UNIT" && systemctl is-active -q "$TRANSCRIBER_UNIT" && systemctl restart "$TRANSCRIBER_UNIT"
  say "Noņemts. (sysctl vm.swappiness atgriezīsies pēc restarta vai: sysctl -w vm.swappiness=60)"
}

case "$MODE" in
  --diagnose) diagnose ;;
  --apply)    diagnose; apply ;;
  --rollback) rollback ;;
esac
