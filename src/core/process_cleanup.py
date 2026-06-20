"""
Windows process cleanup for the desktop app.

This is intentionally scoped to processes that belong to this application:
- children of the current process;
- known app executables by image name during installer/uninstaller runs;
- browser helper processes whose command line contains the app data/profile path.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


APP_PROCESS_NAMES = {
    "SintMaartenCampusAutologin.exe",
    "chromedriver.exe",
}


def _run_powershell(script: str) -> None:
    if sys.platform != "win32":
        return
    try:
        subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
    except Exception:
        pass


def kill_child_process_tree(pid: int | None = None) -> None:
    """Kill child processes of pid, deepest children first."""
    if sys.platform != "win32":
        return
    pid = int(pid or os.getpid())
    script = rf"""
$root = {pid}
$all = Get-CimInstance Win32_Process | Select-Object ProcessId,ParentProcessId,Name,CommandLine
$children = @()
function Add-Children([int]$parent) {{
  foreach ($p in $all | Where-Object {{ $_.ParentProcessId -eq $parent }}) {{
    Add-Children ([int]$p.ProcessId)
    $script:children += $p
  }}
}}
Add-Children $root
foreach ($p in $children) {{
  try {{ Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue }} catch {{}}
}}
"""
    _run_powershell(script)


def cleanup_tool_processes() -> None:
    """
    Best-effort cleanup for processes that can keep app/profile directories locked.
    """
    if sys.platform != "win32":
        return

    local_appdata = Path(os.environ.get("LOCALAPPDATA", "")) / "SintMaartenCampusAutologin"
    program_files = Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "SintMaartenCampusAutologin"
    current_pid = os.getpid()

    names = ",".join(f"'{name.lower()}'" for name in APP_PROCESS_NAMES)
    appdata_token = str(local_appdata).replace("'", "''").lower()
    program_token = str(program_files).replace("'", "''").lower()

    script = rf"""
$currentPid = {current_pid}
$names = @({names})
$appDataToken = '{appdata_token}'
$programToken = '{program_token}'
$procs = Get-CimInstance Win32_Process | Select-Object ProcessId,ParentProcessId,Name,CommandLine
foreach ($p in $procs) {{
  $name = [string]$p.Name
  $cmd = ([string]$p.CommandLine).ToLowerInvariant()
  $nameLower = $name.ToLowerInvariant()
  $matchesName = $names -contains $nameLower
  $matchesToolPath = ($cmd -and (($appDataToken -and $cmd.Contains($appDataToken)) -or ($programToken -and $cmd.Contains($programToken))))
  if ($p.ProcessId -ne $currentPid -and ($matchesName -or $matchesToolPath)) {{
    try {{ Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue }} catch {{}}
  }}
}}
"""
    _run_powershell(script)
