<#
.SYNOPSIS
  Tieši VIENS SSH mēģinājums uz Oracle ar diagnostiku failā un 15 min bloķēšanu atkārtojumam.

.DESCRIPTION
  - Pirms mēģinājuma pārbauda cooldown failu; ja pēdējais mēģinājums bija nesen, NEmēģina.
  - Mēģinājumu ieraksta cooldown failā PIRMS savienojuma (arī avārijas gadījumā tas skaitās).
  - ssh pats raksta -v žurnālu failā (-E), neatkarīgi no rīku slāņa stdout.
  - BatchMode=yes: nav paroles uzvednes, nav atkārtojumu.
  - Klasificē rezultātu no žurnāla un izveido JSON evidence.
  Nav cilpu. Nedrīkst palaist no WATCHDOG/TICK/SUPERVISOR.

.OUTPUTS
  Exit 0 = OK, 1 = mēģinājums neizdevās (skat. classification), 3 = cooldown, 2 = kļūda pirms mēģinājuma.
#>
param(
  [string]$TargetHost = "151.145.57.217",
  [string]$User = "opc",
  [ValidateRange(1, 65535)][int]$Port = 22,
  [ValidateRange(1, 1440)][int]$CooldownMin = 15,
  [string]$StateDir = (Join-Path $env:LOCALAPPDATA "PAVADONIS\oracle-probe"),
  [switch]$IgnoreCooldown
)
$ErrorActionPreference = "Stop"

New-Item -ItemType Directory -Force $StateDir | Out-Null
$stateFile = Join-Path $StateDir "last_attempt.json"
$now = [DateTime]::UtcNow

if ((Test-Path $stateFile) -and -not $IgnoreCooldown) {
  try {
    $last = [DateTime]::Parse((Get-Content $stateFile -Raw | ConvertFrom-Json).attempt_utc).ToUniversalTime()
    $next = $last.AddMinutes($CooldownMin)
    if ($now -lt $next) {
      Write-Output ("COOLDOWN: pēdējais mēģinājums {0:u}; nākamais drīkst pēc {1:u}." -f $last, $next)
      exit 3
    }
  } catch {
    Write-Output "COOLDOWN fails bojāts ($stateFile) - fail closed. Pārbaudi un izdzēs ar roku."
    exit 2
  }
}

$ssh = (Get-Command ssh.exe -ErrorAction SilentlyContinue).Source
if (-not $ssh) { Write-Output "ssh.exe nav atrasts (OpenSSH Client)."; exit 2 }

$stamp = $now.ToString("yyyyMMddTHHmmssZ")
$log = Join-Path $StateDir "ssh-$stamp.log"
@{ attempt_utc = $now.ToString("o"); host = $TargetHost; port = $Port } | ConvertTo-Json |
  Set-Content -Encoding UTF8 $stateFile

$remote = "uptime; free -m; (systemctl is-active sshd || systemctl is-active ssh) 2>/dev/null"
$sshArgs = @("-v", "-E", $log, "-o", "BatchMode=yes", "-o", "ConnectTimeout=15",
             "-o", "ConnectionAttempts=1", "-o", "ServerAliveInterval=10", "-o", "ServerAliveCountMax=2",
             "-p", "$Port", "$User@$TargetHost", $remote)
$started = Get-Date
# PowerShell 5.1: ar "Stop" native stderr (2>&1) kļūst par izņēmumu un pārtrauc skriptu.
$ErrorActionPreference = "Continue"
$stdout = & $ssh @sshArgs 2>&1 | ForEach-Object { "$_" } | Out-String
$code = $LASTEXITCODE
$ErrorActionPreference = "Stop"
$elapsed = [math]::Round(((Get-Date) - $started).TotalSeconds, 1)

$logText = if (Test-Path $log) { Get-Content $log -Raw } else { "" }
$all = "$logText`n$stdout"
$class =
  if ($code -eq 0) { "OK" }
  elseif ($all -match "Connection timed out|Operation timed out") { "TCP_TIMEOUT" }
  elseif ($all -match "Connection refused") { "TCP_REFUSED" }
  elseif ($all -match "No route to host|Network is unreachable|Could not resolve") { "NETWORK" }
  elseif ($all -match "Permission denied") { "AUTH_DENIED" }
  elseif ($all -match "Host key verification failed|REMOTE HOST IDENTIFICATION HAS CHANGED") { "HOSTKEY_MISMATCH" }
  elseif (($all -match "kex_exchange_identification|Connection closed by|Connection reset") -and
          ($logText -notmatch "Remote protocol version")) { "CLOSED_BEFORE_BANNER" }
  elseif ($logText -match "Remote protocol version") { "FAILED_AFTER_BANNER" }
  else { "UNKNOWN" }

$meaning = @{
  OK                   = "SSH strādā. Nākamais: stabilize_memory.sh bez argumentiem."
  TCP_TIMEOUT          = "Nav TCP atbildes: serveris iekāris, IP nomesta ugunsmūrī vai OCI Security List/NSG. Ej uz OCI Console (Console history, Metrics, Security List)."
  TCP_REFUSED          = "Serveris dzīvs, bet sshd neklausās portā. Vajag Serial Console vai Run Command."
  NETWORK              = "Tīkla vai DNS problēma Office PC pusē."
  AUTH_DENIED          = "Serveris un sshd strādā; atslēga netiek pieņemta. NEatkārtot - pārbaudīt authorized_keys caur konsoli."
  HOSTKEY_MISMATCH     = "Servera atslēga mainījusies. NEturpināt, kamēr nav pārbaudīts, ka tas ir tas pats serveris."
  CLOSED_BEFORE_BANNER = "TCP izveidojas, sshd aizver pirms sveiciena: sods (PerSourcePenalties/MaxStartups) vai atmiņas trūkums."
  FAILED_AFTER_BANNER  = "sshd atbild, kļūme vēlāk (kex/auth). Skat. žurnālu."
  UNKNOWN              = "Neklasificēts. Skat. žurnālu."
}

$evidence = [ordered]@{
  attempt_utc    = $now.ToString("o")
  target         = "$User@${TargetHost}:$Port"
  exit_code      = $code
  elapsed_s      = $elapsed
  classification = $class
  meaning        = $meaning[$class]
  log_file       = $log
  log_present    = [bool]$logText
  stdout_tail    = ($stdout -split "`n" | Select-Object -Last 8) -join "`n"
}
$evidenceFile = Join-Path $StateDir "evidence-$stamp.json"
$evidence | ConvertTo-Json | Set-Content -Encoding UTF8 $evidenceFile
$evidence | ConvertTo-Json
if ($class -eq "OK") { exit 0 } else { exit 1 }
