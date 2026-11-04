<#
  setup-server.ps1  -  run the kitchen dashboard's data server on mrpopp

  Run on mrpopp from an ADMIN PowerShell:
      powershell -ExecutionPolicy Bypass -File D:\poppboard\kitchen_screen\mrpopp\setup-server.ps1
  (first time: see the one-line download command in the guide, since the repo isn't there yet)

  What it does (safe to re-run; skips what's done):
    1. Installs Git and Python 3.12 if missing (winget).
    2. Clones/updates github.com/spencerapopp/kitchen_screen to D:\poppboard\kitchen_screen.
    3. Copies the settings and data from the Pi (asks for the Pi password, twice).
    4. Runs the server at startup as a background task that restarts itself if it stops,
       plus a 3:30 AM nightly update. Opens port 8080 on the home network only.
  The Pi keeps its own server running as a standby: if mrpopp goes down, the kitchen screen
  switches to the Pi within about a minute, and back once mrpopp is healthy for 5 minutes.
#>
param(
    [string]$Root   = 'D:\poppboard',
    [string]$PiHost = '192.168.4.45',
    [string]$PiUser = 'spencer',
    [int]$Port      = 8080
)
#Requires -RunAsAdministrator
$ErrorActionPreference = 'Continue'
$ProgressPreference = 'SilentlyContinue'

$Repo    = Join-Path $Root 'kitchen_screen'
$ConfDir = Join-Path $Root 'config'
$Conf    = Join-Path $ConfDir 'config.json'
$Data    = Join-Path $Root 'kitchen-data'
$Logs    = Join-Path $Root 'logs'
$Venv    = Join-Path $Repo 'pi\.venv-win'
$VPy     = Join-Path $Venv 'Scripts\python.exe'
$Task    = 'Kitchen dashboard server'
$Nightly = 'Kitchen dashboard nightly update'

function Say($m)  { Write-Host "`n==> $m" -ForegroundColor Cyan }
function Ok($m)   { Write-Host "    ok  $m" -ForegroundColor Green }
function Warn($m) { Write-Host "    !!  $m" -ForegroundColor Yellow }
function Fail($m) { Write-Host "`nSTOPPED: $m" -ForegroundColor Red; exit 1 }
function Refresh-Path { $env:Path = [Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [Environment]::GetEnvironmentVariable('Path','User') }

# ---------------------------------------------------------------- 1. tools
Say 'Checking tools'
$drive = Split-Path $Root -Qualifier
if (-not (Test-Path "$drive\")) { Fail "No $drive drive. Re-run with -Root <folder on another drive>." }
foreach ($d in $Root, $ConfDir, $Data, $Logs) { if (-not (Test-Path $d)) { New-Item -ItemType Directory -Path $d | Out-Null } }

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    winget install -e --id Git.Git --scope machine --accept-package-agreements --accept-source-agreements | Out-Null
    Refresh-Path
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) { Fail 'Git did not install. Install it from git-scm.com, then run this again.' }
}
Ok "git $((git --version) -replace 'git version ','')"

$Py = 'C:\Program Files\Python312\python.exe'
if (-not (Test-Path $Py)) {
    winget install -e --id Python.Python.3.12 --scope machine --accept-package-agreements --accept-source-agreements --override '/quiet InstallAllUsers=1 PrependPath=1' | Out-Null
    if (-not (Test-Path $Py)) { Fail "Python 3.12 did not install to $Py." }
}
Ok "python $(& $Py --version)"
if (-not (Get-Command scp -ErrorAction SilentlyContinue)) { Fail 'scp is missing: Settings > Apps > Optional features > add "OpenSSH Client".' }

# ---------------------------------------------------------------- 2. code
Say "Code in $Repo"
git config --system --add safe.directory ($Repo -replace '\\','/') 2>$null   # the task runs as SYSTEM
if (Test-Path (Join-Path $Repo '.git')) {
    git -C $Repo pull -q
} else {
    git clone -q https://github.com/spencerapopp/kitchen_screen.git $Repo
}
if (-not (Test-Path (Join-Path $Repo 'pi\server.py'))) { Fail 'Could not get the code from GitHub.' }
Ok "at $(git -C $Repo log -1 --format='%h %cd' --date=format:'%b %d %H:%M')"

if (-not (Test-Path $VPy)) { & $Py -m venv $Venv }
& $VPy -m pip install -q --upgrade pip 2>$null
& $VPy -m pip install -q icalendar recurring-ical-events pillow pillow-heif gkeepapi tzdata
if ($LASTEXITCODE -ne 0) { Fail 'pip install failed. Scroll up for the error.' }
Ok 'Python packages installed'

# ---------------------------------------------------------------- 3. settings + data from the Pi
Say 'Settings and data'
if (Test-Path $Conf) {
    Ok "settings already here ($Conf); leaving them alone"
} else {
    Write-Host "    Copying settings from the Pi ($PiUser@$PiHost). Enter the Pi password when asked."
    scp "${PiUser}@${PiHost}:.config/kitchen/config.json" $Conf
    if (-not (Test-Path $Conf)) { Fail "Could not copy config.json from the Pi. Check that 'ssh $PiUser@$PiHost' works." }
    Write-Host '    Copying the data files (word history, Keep session, address cache). Pi password again:'
    scp "${PiUser}@${PiHost}:kitchen-data/*.json" $Data
    Ok 'copied from the Pi'
}
# Serve the home network; the kitchen-screen-only setting doesn't apply here.
& $VPy -c @"
import json, sys
p = sys.argv[1]; c = json.load(open(p, encoding='utf-8'))
c['bind'] = '0.0.0.0'; c['port'] = int(sys.argv[2]); c.pop('dashboard_url', None)
json.dump(c, open(p, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
"@ $Conf $Port
if ($LASTEXITCODE -ne 0) { Fail "config.json isn't valid JSON: $Conf" }
# Secrets (Google, Keep, TomTom) are in there: only SYSTEM, admins and you can read it.
icacls $ConfDir /inheritance:r /grant:r "SYSTEM:(OI)(CI)F" "Administrators:(OI)(CI)F" "${env:USERNAME}:(OI)(CI)F" | Out-Null
Ok 'listening on the home network, settings folder locked down'

# ---------------------------------------------------------------- 4. run it
Say 'Background task'
$Run = Join-Path $Root 'run-server.ps1'
@"
# Started at boot by the "$Task" task (as SYSTEM). Restarts the server if it ever stops.
`$env:KITCHEN_DATA   = '$Data'
`$env:KITCHEN_CONFIG = '$Conf'
`$env:PYTHONUTF8     = '1'
while (`$true) {
    foreach (`$f in 'server.log', 'server.err.log') {
        if (Test-Path "$Logs\`$f") { Move-Item "$Logs\`$f" "$Logs\prev-`$f" -Force }
    }
    `$p = Start-Process -FilePath '$VPy' -ArgumentList '-u', '"$Repo\pi\server.py"' -NoNewWindow -Wait -PassThru ``
          -RedirectStandardOutput '$Logs\server.log' -RedirectStandardError '$Logs\server.err.log'
    Add-Content '$Logs\restarts.log' "`$(Get-Date -Format s) server stopped (exit `$(`$p.ExitCode)); restarting in 10 s"
    Start-Sleep 10
}
"@ | Set-Content -Path $Run -Encoding UTF8

$Update = Join-Path $Root 'update-server.ps1'
@"
# Nightly at 3:30 AM: get the latest code, then restart the server on it.
git -C '$Repo' pull -q *>> '$Logs\update.log'
Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object { `$_.CommandLine -like '*kitchen_screen*server.py*' } |
    ForEach-Object { Stop-Process -Id `$_.ProcessId -Force }      # run-server.ps1 starts it again in 10 s
"@ | Set-Content -Path $Update -Encoding UTF8

$ps = "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe"
$principal = New-ScheduledTaskPrincipal -UserId 'SYSTEM' -LogonType ServiceAccount -RunLevel Highest
$settings  = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit ([TimeSpan]::Zero) `
                 -RestartCount 999 -RestartInterval (New-TimeSpan -Minutes 1) -StartWhenAvailable -MultipleInstances IgnoreNew

Stop-ScheduledTask -TaskName $Task -ErrorAction SilentlyContinue
Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object { $_.CommandLine -like '*kitchen_screen*server.py*' } |
    ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
Register-ScheduledTask -TaskName $Task -Force -Principal $principal -Settings $settings `
    -Trigger (New-ScheduledTaskTrigger -AtStartup) `
    -Action (New-ScheduledTaskAction -Execute $ps -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$Run`"") | Out-Null
Register-ScheduledTask -TaskName $Nightly -Force -Principal $principal `
    -Settings (New-ScheduledTaskSettingsSet -StartWhenAvailable) `
    -Trigger (New-ScheduledTaskTrigger -Daily -At 3:30am) `
    -Action (New-ScheduledTaskAction -Execute $ps -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$Update`"") | Out-Null
Start-ScheduledTask -TaskName $Task
Ok "server starts with Windows and restarts itself; nightly update at 3:30 AM"

if (-not (Get-NetFirewallRule -DisplayName 'Kitchen dashboard' -ErrorAction SilentlyContinue)) {
    New-NetFirewallRule -DisplayName 'Kitchen dashboard' -Direction Inbound -Protocol TCP -LocalPort $Port -Action Allow -Profile Private | Out-Null
}
Ok "firewall: port $Port open on private networks only"
foreach ($p in (Get-NetConnectionProfile | Where-Object { $_.NetworkCategory -eq 'Public' })) {
    Warn "Network '$($p.Name)' is set to Public, so the Pi can't reach this server. Fix:"
    Warn "  Set-NetConnectionProfile -InterfaceAlias '$($p.InterfaceAlias)' -NetworkCategory Private"
}

# ---------------------------------------------------------------- 5. test
Say 'Testing (up to 2 minutes)'
$deadline = (Get-Date).AddMinutes(2); $page = $false; $cal = $false
while ((Get-Date) -lt $deadline -and -not ($page -and $cal)) {
    Start-Sleep 5
    try { $page = (Invoke-WebRequest -UseBasicParsing "http://localhost:$Port/pi/dashboard.html" -TimeoutSec 5).StatusCode -eq 200 } catch { }
    try { $cal  = (Invoke-WebRequest -UseBasicParsing "http://localhost:$Port/data/calendar.json" -TimeoutSec 5).StatusCode -eq 200 } catch { }
}
if (-not $page) { Fail "The server isn't answering. Last lines of its log:`n$((Get-Content "$Logs\server.err.log", "$Logs\server.log" -Tail 15 -ErrorAction SilentlyContinue) -join "`n")" }
Ok 'dashboard page answers'
if ($cal) { Ok 'calendar data is flowing' } else { Warn "no calendar data yet; check $Logs\server.log in a few minutes" }

$ip = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -like '192.168.*' } | Select-Object -First 1).IPAddress
$url = "http://${ip}:$Port/pi/dashboard.html"
Write-Host ''
Write-Host 'Done. mrpopp is serving the kitchen dashboard.' -ForegroundColor Green
Write-Host "  Open it on this PC:  $url"
Write-Host "  Server log:          $Logs\server.log  (errors: server.err.log)"
Write-Host ''
Write-Host 'Last step, on the Pi (ssh spencer@192.168.4.45), paste this one line:' -ForegroundColor Yellow
Write-Host "  cd ~/kitchen_screen && git pull && python3 -c `"import json,os;p=os.path.expanduser('~/.config/kitchen/config.json');c=json.load(open(p));c['dashboard_url']='$url';json.dump(c,open(p,'w'),indent=2)`" && sudo reboot"
