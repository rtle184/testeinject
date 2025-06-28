# MSI Auto-Installer Helper Script
# Run this script as Administrator

Write-Host "MSI Auto-Installer Setup" -ForegroundColor Green
Write-Host "=========================" -ForegroundColor Green

# Check if running as admin
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "This script requires Administrator privileges. Please run as Administrator." -ForegroundColor Red
    Write-Host "Press any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

# Register the protocol handler
Write-Host "Registering MSI protocol handler..." -ForegroundColor Yellow

$regPath = "HKCR:\msiexec"
if (!(Test-Path $regPath)) {
    New-Item -Path $regPath -Force | Out-Null
}

Set-ItemProperty -Path $regPath -Name "(Default)" -Value "MSI Executor Protocol"
Set-ItemProperty -Path $regPath -Name "URL Protocol" -Value ""

$iconPath = "$regPath\DefaultIcon"
if (!(Test-Path $iconPath)) {
    New-Item -Path $iconPath -Force | Out-Null
}
Set-ItemProperty -Path $iconPath -Name "(Default)" -Value "C:\Windows\System32\msiexec.exe,0"

$shellPath = "$regPath\shell\open\command"
if (!(Test-Path $shellPath)) {
    New-Item -Path $shellPath -Force | Out-Null
}

$command = "powershell.exe -WindowStyle Hidden -Command \"\$file = '%1' -replace 'msiexec://', ''; if (Test-Path \$file) { Start-Process 'msiexec.exe' -ArgumentList '/i', \$file -Verb RunAs } else { Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.MessageBox]::Show('File not found: ' + \$file, 'Error', 'OK', 'Error') }\""
Set-ItemProperty -Path $shellPath -Name "(Default)" -Value $command

Write-Host "Protocol handler registered successfully!" -ForegroundColor Green
Write-Host "You can now use msiexec://path/to/file.msi URLs to auto-install MSI files." -ForegroundColor Green
Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")