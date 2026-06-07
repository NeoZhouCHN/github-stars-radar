param(
  [string]$Version = "0.1.0"
)

$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $Root

$PackageRoot = Join-Path $Root "dist\windows-package"
$PortableRoot = Join-Path $PackageRoot "GitHubStarsRadar"
$ZipPath = Join-Path $Root "dist\GitHubStarsRadar-$Version-windows-x64.zip"
$InstallerPath = Join-Path $Root "dist\GitHubStarsRadarSetup-$Version.exe"
$ChecksumsPath = Join-Path $Root "dist\SHA256SUMS.txt"

Remove-Item -Recurse -Force -ErrorAction SilentlyContinue `
  (Join-Path $Root "build"), `
  (Join-Path $Root "dist\github-stars-radar"), `
  $PackageRoot, `
  $ZipPath, `
  $InstallerPath, `
  $ChecksumsPath

py -m pip install --upgrade pip
py -m pip install pyinstaller

py -m PyInstaller `
  --noconfirm `
  --clean `
  --onedir `
  --name github-stars-radar `
  "mcp-server\server.py"

New-Item -ItemType Directory -Force -Path $PortableRoot | Out-Null
Copy-Item -Recurse -Force "dist\github-stars-radar\*" $PortableRoot
Copy-Item -Force ".env.example", "LICENSE", "README.md", "README.en.md" $PortableRoot
Copy-Item -Recurse -Force "prompts", "skills", "adapters" $PortableRoot

Compress-Archive -Path (Join-Path $PortableRoot "*") -DestinationPath $ZipPath -Force

$Iscc = Get-Command "ISCC.exe" -ErrorAction SilentlyContinue
if ($Iscc) {
  & $Iscc.Source "packaging\windows\installer.iss" "/DAppVersion=$Version" "/DSourceDir=$PortableRoot" "/DOutputDir=$(Join-Path $Root 'dist')"
} else {
  Write-Warning "Inno Setup ISCC.exe was not found. Portable zip was created, installer exe was skipped."
}

$Artifacts = @($ZipPath)
if (Test-Path $InstallerPath) {
  $Artifacts += $InstallerPath
}

$Lines = foreach ($Path in $Artifacts) {
  $Hash = (Get-FileHash -Algorithm SHA256 $Path).Hash.ToLowerInvariant()
  "$Hash  $(Split-Path -Leaf $Path)"
}
$Lines | Set-Content -Encoding ASCII $ChecksumsPath

Write-Host "Windows package build finished."
Write-Host "Portable zip: $ZipPath"
if (Test-Path $InstallerPath) {
  Write-Host "Installer: $InstallerPath"
}
Write-Host "Checksums: $ChecksumsPath"
