param(
    [string]$Python = "C:\Users\admin\AppData\Local\Programs\Python\Python313\python.exe"
)

$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$Spec = Join-Path $Root "packaging\pyinstaller\PyCalc.spec"

Set-Location $Root

& $Python -m PyInstaller `
    --clean `
    --noconfirm `
    --distpath (Join-Path $Root "dist") `
    --workpath (Join-Path $Root "build") `
    $Spec
