# Start Fusion if it is not running, wait for the ClaudeJobRunner add-in to report in, then minimize Fusion.
# Usage: pwsh -NoProfile -File fusion_up.ps1 [-TimeoutSec 180] [-NoMinimize] [-Launcher <path to FusionLauncher.exe>] [-JobsDir <dir>]
# -Launcher defaults to the newest FusionLauncher.exe under %LOCALAPPDATA%\Autodesk\webdeploy\production\<hash>\
#   (the hash folder changes with each Fusion update, so it is looked up, not hard coded).
# -JobsDir defaults to $env:FUSION_JOBS_DIR, else $env:TEMP\claude-fusion\jobs (same rule as ClaudeJobRunner.py and fjob.py).
param(
    [int]$TimeoutSec = 180,
    [switch]$NoMinimize,
    [string]$Launcher = "",
    [string]$JobsDir = ""
)
if (-not $Launcher) {
    $prod = Join-Path $env:LOCALAPPDATA "Autodesk\webdeploy\production"
    $hit = Get-ChildItem -Path $prod -Filter FusionLauncher.exe -Recurse -Depth 1 -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if (-not $hit) {
        "NO LAUNCHER: FusionLauncher.exe not found under $prod. Pass -Launcher <path>."
        exit 3
    }
    $Launcher = $hit.FullName
}
if (-not $JobsDir) {
    $JobsDir = if ($env:FUSION_JOBS_DIR) { $env:FUSION_JOBS_DIR } else { Join-Path $env:TEMP "claude-fusion\jobs" }
}
$flag = Join-Path $JobsDir "runner_started.txt"
Add-Type -Namespace W -Name U -MemberDefinition @'
[DllImport("user32.dll")] public static extern bool ShowWindow(System.IntPtr h, int n);
[DllImport("user32.dll")] public static extern bool IsIconic(System.IntPtr h);
'@
$p = Get-Process Fusion360 -ErrorAction SilentlyContinue | Select-Object -First 1
if ($p) {
    "ALREADY RUNNING pid $($p.Id) since $($p.StartTime) title '$($p.MainWindowTitle)'"
    exit 0
}
$before = if (Test-Path $flag) { (Get-Item $flag).LastWriteTime } else { [datetime]::MinValue }
$t0 = Get-Date
Start-Process -FilePath $Launcher | Out-Null
$minimized = $false
while (((Get-Date) - $t0).TotalSeconds -lt $TimeoutSec) {
    Start-Sleep -Milliseconds 1000
    $p = Get-Process Fusion360 -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($p -and -not $NoMinimize -and -not $minimized -and $p.MainWindowHandle -ne 0 -and $p.MainWindowTitle -match 'Autodesk Fusion') {
        [W.U]::ShowWindow($p.MainWindowHandle, 6) | Out-Null
        $minimized = $true
        "minimized main window at +$([int]((Get-Date) - $t0).TotalSeconds) s"
    }
    if ((Test-Path $flag) -and (Get-Item $flag).LastWriteTime -gt $before) {
        "RUNNER LIVE at +$([int]((Get-Date) - $t0).TotalSeconds) s, pid $($p.Id)"
        if ($p -and -not $NoMinimize -and $p.MainWindowHandle -ne 0 -and -not [W.U]::IsIconic($p.MainWindowHandle)) {
            [W.U]::ShowWindow($p.MainWindowHandle, 6) | Out-Null
            "minimized main window"
        }
        exit 0
    }
}
"TIMEOUT: runner did not report within $TimeoutSec s (Fusion running: $([bool](Get-Process Fusion360 -ErrorAction SilentlyContinue)); jobs folder $JobsDir)"
exit 2
