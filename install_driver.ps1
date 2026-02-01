# PowerShell script to download and install Interception Driver

$url = "https://github.com/oblitum/Interception/releases/download/v1.0.1/Interception.zip"
$zipPath = "$PWD\Interception.zip"
$destPath = "$PWD\Interception_Driver"

Write-Host "Downloading Interception Driver..." -ForegroundColor Cyan
Invoke-WebRequest -Uri $url -OutFile $zipPath

Write-Host "Extracting..." -ForegroundColor Cyan
Expand-Archive -LiteralPath $zipPath -DestinationPath $destPath -Force

$installerPath = "$destPath\Interception\command line installer\install-interception.exe"

if (Test-Path $installerPath) {
    Write-Host "Installing Driver..." -ForegroundColor Green
    # Running the installer
    Start-Process -FilePath $installerPath -ArgumentList "/install" -Verb RunAs -Wait
    Write-Host "Installation command finished." -ForegroundColor Green
    Write-Host "YOU MUST RESTART YOUR COMPUTER FOR THIS TO WORK!" -ForegroundColor Red -BackgroundColor Yellow
} else {
    Write-Host "Could not find installer at $installerPath" -ForegroundColor Red
}
