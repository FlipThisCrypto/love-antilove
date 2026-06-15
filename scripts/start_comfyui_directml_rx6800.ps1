$ErrorActionPreference = "Continue"

$repoRoot = Split-Path -Parent $PSScriptRoot
$workspaceRoot = Split-Path -Parent $repoRoot
$comfyRoot = Join-Path $workspaceRoot "ComfyUI"
$python = Join-Path $comfyRoot ".venv-directml\Scripts\python.exe"
$logDir = Join-Path $workspaceRoot "logs"
$logPath = Join-Path $logDir "comfyui-directml-rx6800.log"

New-Item -ItemType Directory -Force -Path $logDir | Out-Null

if (!(Test-Path $python)) {
  throw "ComfyUI DirectML Python was not found at $python"
}

Push-Location $comfyRoot
try {
  & $python main.py --listen 127.0.0.1 --port 8188 --disable-auto-launch --directml 1 *> $logPath
}
finally {
  Pop-Location
}
