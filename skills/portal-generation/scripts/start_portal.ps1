# GRIT Copilot Portal - PowerShell Launcher
# Starts the portal server at http://localhost:8080

$ErrorActionPreference = "Stop"
$PORT = 8080
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$DIST_DIR = Join-Path $SCRIPT_DIR "dist"

Write-Host "=" -ForegroundColor Yellow -NoNewline
Write-Host ("=" * 59) -ForegroundColor Yellow
Write-Host "  🚀 GRIT Copilot Portal Server" -ForegroundColor Cyan
Write-Host "=" -ForegroundColor Yellow -NoNewline
Write-Host ("=" * 59) -ForegroundColor Yellow

# Check if dist exists
if (-not (Test-Path $DIST_DIR)) {
    Write-Host ""
    Write-Host "❌ Error: Portal dist directory not found" -ForegroundColor Red
    Write-Host "   Location: $DIST_DIR" -ForegroundColor Yellow
    Write-Host "   Please run 'python generate_portal.py' first" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

# Check if index.html exists
$INDEX_FILE = Join-Path $DIST_DIR "index.html"
if (-not (Test-Path $INDEX_FILE)) {
    Write-Host ""
    Write-Host "❌ Error: index.html not found" -ForegroundColor Red
    Write-Host "   Please run 'python generate_portal.py' to generate the portal" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

# Check if port is already in use
$portInUse = Get-NetTCPConnection -LocalPort $PORT -State Listen -ErrorAction SilentlyContinue
if ($portInUse) {
    Write-Host ""
    Write-Host "⚠️  Port $PORT is already in use!" -ForegroundColor Yellow
    Write-Host "   Process ID: $($portInUse.OwningProcess)" -ForegroundColor Yellow
    
    $response = Read-Host "   Stop the existing server? (y/N)"
    if ($response -eq 'y' -or $response -eq 'Y') {
        Stop-Process -Id $portInUse.OwningProcess -Force -ErrorAction SilentlyContinue
        Write-Host "   ✓ Stopped existing server" -ForegroundColor Green
        Start-Sleep -Seconds 1
    } else {
        Write-Host "   Exiting..." -ForegroundColor Yellow
        exit 1
    }
}

Write-Host ""
Write-Host "  📂 Serving from: $DIST_DIR" -ForegroundColor Gray
Write-Host "  🌐 URL:          http://localhost:$PORT" -ForegroundColor Green
Write-Host "  🛑 Stop:         Press Ctrl+C" -ForegroundColor Gray
Write-Host "=" -ForegroundColor Yellow -NoNewline
Write-Host ("=" * 59) -ForegroundColor Yellow
Write-Host ""

# Start Python HTTP server in the dist directory
try {
    Set-Location $DIST_DIR
    Write-Host "  Opening browser..." -ForegroundColor Cyan
    Start-Process "http://localhost:$PORT"
    Write-Host ""
    Write-Host "  Server is running. Waiting for requests..." -ForegroundColor Green
    Write-Host ""
    
    # Start server (this blocks until Ctrl+C)
    python -m http.server $PORT
}
catch {
    Write-Host ""
    Write-Host "❌ Error starting server: $_" -ForegroundColor Red
    exit 1
}
