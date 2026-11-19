<#
.SYNOPSIS
  Richtet den SSH/rsync-Deploy für grabmale-aus-lehsen.de ein (einmalig, Windows).

.DESCRIPTION
  1. erzeugt einen eigenen SSH-Schlüssel (ed25519) nur für GitHub Actions
  2. liest die Fingerabdrücke des Servers (known_hosts) und lässt sie bestätigen
  3. legt die Repository-Secrets an: SSH_HOST, SSH_PORT, SSH_USER, SSH_PRIVATE_KEY, SSH_KNOWN_HOSTS
  4. legt die GitHub-Umgebungen "staging" und "production" an (production nur von main, mit Freigabe)
  5. zeigt den öffentlichen Schlüssel an (und kopiert ihn in die Zwischenablage),
     optional wird er direkt per SSH (Passwort-Login) auf dem Server eingetragen.

  Voraussetzungen: GitHub CLI (gh, angemeldet per "gh auth login"), Windows-OpenSSH (ssh, ssh-keygen, ssh-keyscan).

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File scripts\setup-secrets.ps1

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File scripts\setup-secrets.ps1 -SshHost ssh.example.de -SshUser web123 -SshPort 22

.EXAMPLE
  # Nur Schlüssel erzeugen und Fingerabdrücke anzeigen, nichts in GitHub ändern:
  powershell -ExecutionPolicy Bypass -File scripts\setup-secrets.ps1 -SshHost ssh.example.de -SshUser web123 -DryRun
#>
[CmdletBinding()]
param(
  [string]$SshHost,
  [string]$SshUser,
  [int]$SshPort = 0,
  [string]$Repo = "web-lionify/website-grabmale-lehsen",
  [switch]$DryRun
)

# "Continue": native Programme (gh, ssh) schreiben Hinweise nach stderr – Fehler werden per Exit-Code geprüft.
$ErrorActionPreference = "Continue"

function Fail([string]$msg) { Write-Host "Fehler: $msg" -ForegroundColor Red; exit 1 }

function Require-Command([string]$name, [string]$hint) {
  if (-not (Get-Command $name -ErrorAction SilentlyContinue)) { Fail "$name fehlt. $hint" }
}

# Native Programm ausführen und bei Exit-Code != 0 abbrechen
function Invoke-Native([string]$what, [scriptblock]$block) {
  & $block
  if ($LASTEXITCODE -ne 0) { Fail "$what fehlgeschlagen (Exit-Code $LASTEXITCODE)." }
}

# Secret aus Datei setzen (Umleitung über cmd, damit mehrzeilige Werte unverändert ankommen)
function Set-SecretFromFile([string]$name, [string]$file) {
  cmd /c "gh secret set $name --repo $Repo < `"$file`" 2>&1" | Out-Null
  if ($LASTEXITCODE -ne 0) { Fail "Secret $name konnte nicht gesetzt werden." }
  Write-Host "  Secret $name gesetzt"
}

function Write-LfFile([string]$path, [string]$text) {
  $text = ($text -replace "`r`n", "`n").TrimEnd("`n") + "`n"
  [IO.File]::WriteAllText($path, $text, (New-Object Text.UTF8Encoding($false)))
}

Require-Command gh          "Installieren: winget install GitHub.cli"
Require-Command ssh-keygen  "Windows-Feature 'OpenSSH-Client' aktivieren."
Require-Command ssh-keyscan "Windows-Feature 'OpenSSH-Client' aktivieren."

if (-not $DryRun) {
  gh auth status *> $null
  if ($LASTEXITCODE -ne 0) { Fail "Bitte zuerst 'gh auth login' ausführen." }
}

Write-Host ""
Write-Host "SSH-Deploy für $Repo" -ForegroundColor Cyan
Write-Host "  Staging:   staging.grabmale-aus-lehsen.de -> /webseite/staging/"
Write-Host "  Produktiv: grabmale-aus-lehsen.de         -> /webseite/produktiv/"
if ($DryRun) { Write-Host "  DRY-RUN: In GitHub wird nichts geändert." -ForegroundColor Yellow }
Write-Host ""

if (-not $SshHost) { $SshHost = (Read-Host "SSH-Server (Hostname)").Trim() }
if (-not $SshUser) { $SshUser = (Read-Host "SSH-Benutzer").Trim() }
if ($SshPort -le 0) {
  $p = (Read-Host "SSH-Port [22]").Trim()
  $SshPort = if ($p) { [int]$p } else { 22 }
}
if (-not $SshHost -or -not $SshUser) { Fail "Server und Benutzer sind Pflicht." }

$work = Join-Path ([IO.Path]::GetTempPath()) ("grabmale-deploy-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $work -ErrorAction Stop | Out-Null
$keyFile   = Join-Path $work "deploy_key"
$khFile    = Join-Path $work "known_hosts"
$valueFile = Join-Path $work "value.txt"

try {
  # 1. Schlüssel ohne Passphrase (leeres Argument: PS 5.1 braucht '""', PS 7.3+ '')
  $emptyPass = if ($PSVersionTable.PSVersion -ge [version]"7.3") { '' } else { '""' }
  Invoke-Native "ssh-keygen" { ssh-keygen -q -t ed25519 -N $emptyPass -C "github-actions deploy grabmale-aus-lehsen" -f $keyFile }
  $publicKey = (Get-Content "$keyFile.pub" -Raw).Trim()

  # 2. Server-Fingerabdrücke
  Write-Host ""
  Write-Host "Lese Server-Fingerabdrücke von ${SshHost}:$SshPort ..."
  $kh = cmd /c "ssh-keyscan -p $SshPort -T 10 $SshHost 2>nul" | Where-Object { $_ -and -not $_.StartsWith("#") }
  if (-not $kh) {
    # Ausweichweg: ssh-keyscan von Windows-OpenSSH 9.5 scheitert an manchen Servern
    # ("unsupported KEX method sntrup761..."). ssh selbst holt den Host-Schlüssel zuverlässig;
    # er wird mit accept-new in eine eigene Datei geschrieben, eine Anmeldung findet nicht statt.
    $tmpKh = Join-Path $work "known_hosts_ssh"
    cmd /c "ssh -p $SshPort -o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=accept-new -o HashKnownHosts=no -o UserKnownHostsFile=`"$tmpKh`" -o PreferredAuthentications=none $SshUser@$SshHost exit <nul >nul 2>nul"
    if (Test-Path $tmpKh) { $kh = Get-Content $tmpKh | Where-Object { $_ -and -not $_.StartsWith("#") } }
  }
  if (-not $kh) { Fail "Server nicht erreichbar oder kein SSH auf Port $SshPort." }
  $knownHosts = ($kh -join "`n")
  Write-LfFile $khFile $knownHosts

  Write-Host "Fingerabdrücke (bitte mit den Angaben des Hosters vergleichen):" -ForegroundColor Cyan
  & ssh-keygen -lf $khFile | ForEach-Object { Write-Host "  $_" }
  Write-Host ""

  if ($DryRun) {
    Write-Host "DRY-RUN beendet. Öffentlicher Schlüssel (wird beim echten Lauf neu erzeugt):"
    Write-Host "  $publicKey"
    exit 0
  }

  $ok = Read-Host "Stimmen die Fingerabdrücke? [j/N]"
  if ($ok -notmatch '^[jJyY]$') { Fail "Abgebrochen – nichts wurde geändert." }

  # 3. Secrets
  Write-Host ""
  Write-Host "Lege Secrets an ..." -ForegroundColor Cyan
  Write-LfFile $valueFile $SshHost;      Set-SecretFromFile "SSH_HOST" $valueFile
  Write-LfFile $valueFile "$SshPort";    Set-SecretFromFile "SSH_PORT" $valueFile
  Write-LfFile $valueFile $SshUser;      Set-SecretFromFile "SSH_USER" $valueFile
  Set-SecretFromFile "SSH_PRIVATE_KEY" $keyFile
  Set-SecretFromFile "SSH_KNOWN_HOSTS" $khFile

  # 4. Umgebungen
  Write-Host ""
  Write-Host "Lege GitHub-Umgebungen an ..." -ForegroundColor Cyan
  $meId = (gh api user --jq .id).Trim()
  if ($LASTEXITCODE -ne 0 -or -not $meId) { Fail "GitHub-Benutzer konnte nicht ermittelt werden." }

  Invoke-Native "Umgebung staging" { gh api -X PUT "repos/$Repo/environments/staging" --silent }

  $envJson = @{
    reviewers                = @(@{ type = "User"; id = [int64]$meId })
    deployment_branch_policy = @{ protected_branches = $false; custom_branch_policies = $true }
  } | ConvertTo-Json -Depth 5 -Compress
  Write-LfFile $valueFile $envJson
  Invoke-Native "Umgebung production" { gh api -X PUT "repos/$Repo/environments/production" --input $valueFile --silent }

  $policies = cmd /c "gh api repos/$Repo/environments/production/deployment-branch-policies --jq .branch_policies[].name 2>nul"
  if (-not ($policies -contains "main")) {
    Invoke-Native "Branch-Regel main" { gh api -X POST "repos/$Repo/environments/production/deployment-branch-policies" -f name=main -f type=branch --silent }
  }
  Write-Host "  staging    (ohne Freigabe)"
  Write-Host "  production (nur Branch main, Freigabe durch dich)"

  Write-Host ""
  Write-Host "Secrets im Repo:" -ForegroundColor Cyan
  gh secret list --repo $Repo

  # 5. Öffentlichen Schlüssel auf dem Server eintragen
  Write-Host ""
  Write-Host "================================================================" -ForegroundColor Yellow
  Write-Host "Öffentlicher Schlüssel – muss auf dem Server in ~/.ssh/authorized_keys"
  Write-Host "(oder im Kundenmenü des Hosters unter 'SSH-Schlüssel'):"
  Write-Host ""
  Write-Host $publicKey
  Write-Host "================================================================" -ForegroundColor Yellow
  try { Set-Clipboard -Value $publicKey; Write-Host "(in die Zwischenablage kopiert)" } catch { }

  Write-Host ""
  $install = Read-Host "Jetzt per SSH mit Passwort auf dem Server eintragen? [j/N]"
  if ($install -match '^[jJyY]$') {
    $remote = "mkdir -p ~/.ssh && chmod 700 ~/.ssh && touch ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys && (grep -qxF '$publicKey' ~/.ssh/authorized_keys || echo '$publicKey' >> ~/.ssh/authorized_keys)"
    & ssh -p $SshPort -o UserKnownHostsFile="$khFile" -o StrictHostKeyChecking=yes "$SshUser@$SshHost" $remote
    if ($LASTEXITCODE -eq 0) { Write-Host "Schlüssel auf dem Server eingetragen." -ForegroundColor Green }
    else { Write-Host "Eintragen fehlgeschlagen – bitte manuell im Kundenmenü hinterlegen." -ForegroundColor Red }
  }

  Write-Host ""
  Write-Host "Fertig. Der private Schlüssel liegt nur noch als GitHub-Secret vor." -ForegroundColor Green
  Write-Host "Alte FTP-Secrets entfernen (wenn nicht mehr gebraucht):"
  Write-Host "  'FTP_SERVER','FTP_USERNAME','FTP_PASSWORD','FTP_SERVER_DIR' | % { gh secret delete `$_ --repo $Repo }"
}
finally {
  # Privaten Schlüssel und Hilfsdateien lokal löschen
  Remove-Item -Recurse -Force $work -ErrorAction SilentlyContinue
}
