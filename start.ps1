# JobSearchTools - Docker Startup Script for Windows
# This script starts the JobSearchTools application using Docker Compose

Write-Host "====================================" -ForegroundColor Cyan
Write-Host "  JobSearchTools Docker Startup" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is running
$dockerRunning = docker info 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Docker is not running!" -ForegroundColor Red
    Write-Host "Please start Docker Desktop and try again." -ForegroundColor Yellow
    exit 1
}

Write-Host "✓ Docker is running" -ForegroundColor Green

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "WARNING: .env file not found!" -ForegroundColor Yellow
    Write-Host "Creating .env from .env.example..." -ForegroundColor Yellow

    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "✓ Created .env file" -ForegroundColor Green
        Write-Host ""
        Write-Host "IMPORTANT: Please edit .env file with your configuration:" -ForegroundColor Red
        Write-Host "  - DB_PASSWORD" -ForegroundColor Yellow
        Write-Host "  - EMAIL_SMTP_USER" -ForegroundColor Yellow
        Write-Host "  - EMAIL_SMTP_PASSWORD" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Press any key to open .env file for editing..."
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        notepad.exe ".env"
        Write-Host ""
        Write-Host "After saving .env, press any key to continue..."
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    } else {
        Write-Host "ERROR: .env.example not found!" -ForegroundColor Red
        exit 1
    }
}

Write-Host "✓ Configuration file found" -ForegroundColor Green
Write-Host ""

# Create directories if they don't exist
$directories = @("logs", "data", "cache")
foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir | Out-Null
        Write-Host "✓ Created directory: $dir" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "Starting JobSearchTools with Docker Compose..." -ForegroundColor Cyan
Write-Host ""

# Start Docker Compose with Windows-specific configuration
docker-compose -f docker-compose.yml -f docker-compose.windows.yml up -d

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "====================================" -ForegroundColor Green
    Write-Host "  JobSearchTools Started!" -ForegroundColor Green
    Write-Host "====================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Services running:" -ForegroundColor Cyan
    Write-Host "  - PostgreSQL Database: localhost:5432" -ForegroundColor White
    Write-Host "  - Job Scraper Scheduler: Running every 4 hours" -ForegroundColor White
    Write-Host ""
    Write-Host "Useful commands:" -ForegroundColor Cyan
    Write-Host "  View logs:        docker-compose logs -f scheduler" -ForegroundColor White
    Write-Host "  Stop services:    docker-compose down" -ForegroundColor White
    Write-Host "  Restart:          docker-compose restart" -ForegroundColor White
    Write-Host "  View status:      docker-compose ps" -ForegroundColor White
    Write-Host ""
    Write-Host "To start PgAdmin (optional):" -ForegroundColor Cyan
    Write-Host "  docker-compose --profile tools up -d pgadmin" -ForegroundColor White
    Write-Host "  Access at: http://localhost:5050" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "ERROR: Failed to start services!" -ForegroundColor Red
    Write-Host "Check the logs for details:" -ForegroundColor Yellow
    Write-Host "  docker-compose logs" -ForegroundColor White
    exit 1
}
