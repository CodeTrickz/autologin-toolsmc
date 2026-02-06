# PowerShell script om een Inno Setup installer te maken
# Vereist: Inno Setup moet geïnstalleerd zijn

$innoSetupPath = "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"

if (-not (Test-Path $innoSetupPath)) {
    Write-Host "Inno Setup niet gevonden op: $innoSetupPath"
    Write-Host ""
    Write-Host "Download Inno Setup van: https://jrsoftware.org/isdl.php"
    Write-Host "Of gebruik het install.bat script voor een eenvoudige installatie."
    exit 1
}

Write-Host "Maken van Inno Setup installer..."
& $innoSetupPath "installer.iss"

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Installer succesvol gemaakt!"
    Write-Host "Locatie: installer_output\SintMaartenCampusAutologin_Setup.exe"
} else {
    Write-Host ""
    Write-Host "❌ Fout bij maken van installer"
}
