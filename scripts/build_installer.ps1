param(
    [string]$Python = "C:\Users\admin\AppData\Local\Programs\Python\Python313\python.exe",
    [switch]$SkipExeBuild
)

$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$DistDir = Join-Path $Root "dist\PyCalc"
$InstallerDir = Join-Path $Root "packaging\installer"
$InstallerBuildDir = Join-Path $InstallerDir "build"
$Payload = Join-Path $InstallerBuildDir "PyCalc_payload.zip"
$SedFile = Join-Path $InstallerBuildDir "PyCalc_Setup.sed"
$ReleaseDir = Join-Path $Root "release"
$SetupExe = Join-Path $ReleaseDir "PyCalc_Setup.exe"
$IExpress = Join-Path $env:WINDIR "System32\iexpress.exe"

if (-not $SkipExeBuild) {
    & (Join-Path $PSScriptRoot "build_exe.ps1") -Python $Python
}

if (-not (Test-Path (Join-Path $DistDir "PyCalc.exe"))) {
    throw "Executavel nao encontrado em dist\PyCalc. Rode scripts\build_exe.ps1 antes."
}

if (-not (Test-Path $IExpress)) {
    throw "IExpress nao encontrado neste Windows."
}

if (Test-Path $InstallerBuildDir) {
    Remove-Item -LiteralPath $InstallerBuildDir -Recurse -Force
}

New-Item -ItemType Directory -Force $InstallerBuildDir, $ReleaseDir | Out-Null

if (Test-Path $SetupExe) {
    Remove-Item -LiteralPath $SetupExe -Force
}

Copy-Item -LiteralPath (Join-Path $InstallerDir "install_pycalc.cmd") -Destination $InstallerBuildDir
Copy-Item -LiteralPath (Join-Path $InstallerDir "install_pycalc.ps1") -Destination $InstallerBuildDir

Compress-Archive -Path (Join-Path $DistDir "*") -DestinationPath $Payload -Force

$sed = @"
[Version]
Class=IEXPRESS
SEDVersion=3

[Options]
PackagePurpose=InstallApp
ShowInstallProgramWindow=0
HideExtractAnimation=1
UseLongFileName=1
InsideCompressed=0
CAB_FixedSize=0
CAB_ResvCodeSigning=0
RebootMode=N
InstallPrompt=%InstallPrompt%
DisplayLicense=%DisplayLicense%
FinishMessage=%FinishMessage%
TargetName=%TargetName%
FriendlyName=%FriendlyName%
AppLaunched=%AppLaunched%
PostInstallCmd=%PostInstallCmd%
AdminQuietInstCmd=%AdminQuietInstCmd%
UserQuietInstCmd=%UserQuietInstCmd%
SourceFiles=SourceFiles

[Strings]
InstallPrompt=
DisplayLicense=
FinishMessage=PyCalc instalado com sucesso.
TargetName=$SetupExe
FriendlyName=PyCalc Setup
AppLaunched=install_pycalc.cmd
PostInstallCmd=<None>
AdminQuietInstCmd=
UserQuietInstCmd=
FILE0="install_pycalc.cmd"
FILE1="install_pycalc.ps1"
FILE2="PyCalc_payload.zip"

[SourceFiles]
SourceFiles0=$InstallerBuildDir\

[SourceFiles0]
%FILE0%=
%FILE1%=
%FILE2%=
"@

Set-Content -LiteralPath $SedFile -Value $sed -Encoding ASCII

$IExpressExitCode = 0
$NativeErrorPreferenceExists = Get-Variable -Name PSNativeCommandUseErrorActionPreference -ErrorAction SilentlyContinue
if ($NativeErrorPreferenceExists) {
    $PreviousNativeErrorPreference = $PSNativeCommandUseErrorActionPreference
    $PSNativeCommandUseErrorActionPreference = $false
}

try {
    & $IExpress /N /Q $SedFile
    $IExpressExitCode = $LASTEXITCODE
}
finally {
    if ($NativeErrorPreferenceExists) {
        $PSNativeCommandUseErrorActionPreference = $PreviousNativeErrorPreference
    }
}

$Deadline = (Get-Date).AddSeconds(120)
while ((-not (Test-Path $SetupExe)) -and ((Get-Date) -lt $Deadline)) {
    Start-Sleep -Milliseconds 500
}

if (-not (Test-Path $SetupExe)) {
    throw "IExpress terminou sem gerar $SetupExe."
}

if (($null -ne $IExpressExitCode) -and ($IExpressExitCode -ne 0)) {
    Write-Warning "IExpress retornou codigo $IExpressExitCode, mas o instalador foi gerado corretamente."
}

Write-Host "Instalador gerado em $SetupExe"
exit 0
