$ErrorActionPreference = "Stop"

$AppName = "PyCalc"
$InstallDir = Join-Path $env:LOCALAPPDATA "Programs\PyCalc"
$Payload = Join-Path $PSScriptRoot "PyCalc_payload.zip"
$ExePath = Join-Path $InstallDir "PyCalc.exe"
$StartMenuShortcut = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\PyCalc.lnk"
$DesktopShortcut = Join-Path ([Environment]::GetFolderPath("Desktop")) "PyCalc.lnk"
$UninstallCmd = Join-Path $InstallDir "Desinstalar PyCalc.cmd"
$UninstallPs1 = Join-Path $InstallDir "uninstall_pycalc.ps1"
$UninstallKey = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\PyCalc"

if (-not (Test-Path -LiteralPath $Payload)) {
    throw "Payload do PyCalc nao encontrado."
}

if (Test-Path -LiteralPath $InstallDir) {
    Remove-Item -LiteralPath $InstallDir -Recurse -Force
}

New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
Expand-Archive -LiteralPath $Payload -DestinationPath $InstallDir -Force

if (-not (Test-Path -LiteralPath $ExePath)) {
    throw "PyCalc.exe nao foi instalado corretamente."
}

function New-AppShortcut {
    param(
        [string]$ShortcutPath,
        [string]$TargetPath
    )

    $Shell = New-Object -ComObject WScript.Shell
    $Shortcut = $Shell.CreateShortcut($ShortcutPath)
    $Shortcut.TargetPath = $TargetPath
    $Shortcut.WorkingDirectory = Split-Path -Parent $TargetPath
    $Shortcut.IconLocation = "$TargetPath,0"
    $Shortcut.Save()
}

New-AppShortcut -ShortcutPath $StartMenuShortcut -TargetPath $ExePath
New-AppShortcut -ShortcutPath $DesktopShortcut -TargetPath $ExePath

$UninstallScript = @'
$ErrorActionPreference = "SilentlyContinue"

$InstallDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$StartMenuShortcut = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\PyCalc.lnk"
$DesktopShortcut = Join-Path ([Environment]::GetFolderPath("Desktop")) "PyCalc.lnk"
$UninstallKey = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\PyCalc"

Remove-Item -LiteralPath $StartMenuShortcut -Force
Remove-Item -LiteralPath $DesktopShortcut -Force
Remove-Item -LiteralPath $UninstallKey -Recurse -Force

$Cleanup = Join-Path $env:TEMP "pycalc_cleanup.ps1"
$EscapedInstallDir = $InstallDir.Replace("'", "''")
Set-Content -LiteralPath $Cleanup -Encoding UTF8 -Value "Start-Sleep -Seconds 1; Remove-Item -LiteralPath '$EscapedInstallDir' -Recurse -Force"
Start-Process powershell.exe -WindowStyle Hidden -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$Cleanup`""
'@

Set-Content -LiteralPath $UninstallPs1 -Value $UninstallScript -Encoding UTF8
Set-Content -LiteralPath $UninstallCmd -Encoding ASCII -Value "@echo off`r`npowershell.exe -NoProfile -ExecutionPolicy Bypass -File ""%~dp0uninstall_pycalc.ps1""`r`n"

New-Item -Path $UninstallKey -Force | Out-Null
Set-ItemProperty -Path $UninstallKey -Name DisplayName -Value $AppName
Set-ItemProperty -Path $UninstallKey -Name DisplayIcon -Value $ExePath
Set-ItemProperty -Path $UninstallKey -Name DisplayVersion -Value "1.0.0"
Set-ItemProperty -Path $UninstallKey -Name Publisher -Value "PyCalc"
Set-ItemProperty -Path $UninstallKey -Name InstallLocation -Value $InstallDir
Set-ItemProperty -Path $UninstallKey -Name UninstallString -Value "`"$UninstallCmd`""
Set-ItemProperty -Path $UninstallKey -Name NoModify -Value 1 -Type DWord
Set-ItemProperty -Path $UninstallKey -Name NoRepair -Value 1 -Type DWord

Write-Host "$AppName instalado em $InstallDir"
