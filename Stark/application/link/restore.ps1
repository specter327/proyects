Write-Host "==============================="
Write-Host " Stark-Link Clean Environment"
Write-Host "==============================="

$installPath = "$env:APPDATA\Microsoft\Protect\Service"

Write-Host ""
Write-Host "[1] Killing processes..."

Get-Process dbus-monitor -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process Stark-Link -ErrorAction SilentlyContinue | Stop-Process -Force

Write-Host ""
Write-Host "[2] Removing installation directory..."

if (Test-Path $installPath) {
    Remove-Item $installPath -Recurse -Force
    Write-Host "Removed: $installPath"
} else {
    Write-Host "Directory not found"
}

Write-Host ""
Write-Host "[3] Removing registry persistence..."

$regPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run"

if (Get-ItemProperty -Path $regPath -Name "WindowsUpdateHealth" -ErrorAction SilentlyContinue) {
    Remove-ItemProperty -Path $regPath -Name "WindowsUpdateHealth"
    Write-Host "Registry key removed"
}
else {
    Write-Host "Registry key not present"
}

Write-Host ""
Write-Host "Cleanup completed."