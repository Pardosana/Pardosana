<#
.SYNOPSIS
  Palaiž atsevišķu PAVADONIS Commander Chrome profilu ar vadības portu tikai uz 127.0.0.1.

.DESCRIPTION
  - Tavs parastais Chrome profils un cilnes netiek aiztikti un netiek aizvērti.
  - Profils glabājas savā mapē; pieteikšanās (Instagram u.c.) tur saglabājas starp restartiem.
  - Pirmajā reizē mapei tiek iestatītas NTFS tiesības: tikai pašreizējais lietotājs un SYSTEM.
  - Ja Commander Chrome jau darbojas uz šī porta, otru netaisa.
  Palaiž cilvēks ar savām tiesībām, nevis aģents.
#>
param(
  [string]$ProfileDir = (Join-Path $env:LOCALAPPDATA "PAVADONIS\commander-chrome-profile"),
  [ValidateRange(1024, 65535)][int]$Port = 9223,
  [string]$StartUrl = "about:blank"
)
$ErrorActionPreference = "Stop"

function Test-CdpPort([int]$p) {
  try {
    $r = Invoke-RestMethod -Uri "http://127.0.0.1:$p/json/version" -TimeoutSec 2
    return [bool]$r.Browser
  } catch { return $false }
}

if (Test-CdpPort $Port) {
  Write-Host "Commander Chrome jau darbojas uz 127.0.0.1:$Port - otru nepalaižu."
  exit 0
}

$candidates = @(
  "$env:ProgramFiles\Google\Chrome\Application\chrome.exe",
  "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe",
  "$env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe"
)
$chrome = $candidates | Where-Object { $_ -and (Test-Path $_) } | Select-Object -First 1
if (-not $chrome) { throw "chrome.exe nav atrasts standarta vietās." }

# Drošības pārbaude: nekad nelietot parasto Chrome profilu.
$defaultProfile = Join-Path $env:LOCALAPPDATA "Google\Chrome\User Data"
$resolved = [System.IO.Path]::GetFullPath($ProfileDir).TrimEnd('\')
if ($resolved -ieq $defaultProfile -or $resolved.StartsWith("$defaultProfile\", [StringComparison]::OrdinalIgnoreCase)) {
  throw "ProfileDir nedrīkst būt parastais Chrome profils ($defaultProfile)."
}

if (-not (Test-Path $resolved)) {
  New-Item -ItemType Directory -Force $resolved | Out-Null
  # Tikai pašreizējais lietotājs + SYSTEM; mantotās tiesības noņemtas.
  icacls $resolved /inheritance:r /grant:r "$($env:USERNAME):(OI)(CI)F" "SYSTEM:(OI)(CI)F" | Out-Null
  Write-Host "Izveidots jauns profils: $resolved"
}

$chromeArgs = @(
  "--user-data-dir=`"$resolved`"",
  "--remote-debugging-port=$Port",
  "--no-first-run",
  "--no-default-browser-check",
  $StartUrl
)
Start-Process -FilePath $chrome -ArgumentList $chromeArgs | Out-Null

for ($i = 0; $i -lt 20; $i++) {
  Start-Sleep -Milliseconds 500
  if (Test-CdpPort $Port) {
    Write-Host "OK: Commander Chrome darbojas, vadības ports 127.0.0.1:$Port, profils $resolved"
    exit 0
  }
}
throw "Chrome palaists, bet vadības ports 127.0.0.1:$Port neatbild."
