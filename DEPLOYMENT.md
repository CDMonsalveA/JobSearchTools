# Deployment Guide - JobSearchTools

This guide provides detailed instructions for deploying JobSearchTools in production on a Windows machine using Docker.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [Configuration](#configuration)
4. [Docker Deployment](#docker-deployment)
5. [Monitoring](#monitoring)
6. [Maintenance](#maintenance)
7. [Troubleshooting](#troubleshooting)
8. [Backup & Recovery](#backup--recovery)

## Prerequisites

### Software Requirements

- **Windows 10/11** with WSL2 enabled
- **Docker Desktop for Windows** (latest stable version)
  - Download: https://www.docker.com/products/docker-desktop
  - Minimum 4GB RAM allocated to Docker
  - 20GB free disk space

### Email Setup (Gmail)

For email notifications to work, you need a Gmail App Password:

1. Enable 2-Factor Authentication on your Gmail account
2. Go to: https://myaccount.google.com/apppasswords
3. Create an app password for "Mail"
4. Save this password for configuration

## Initial Setup

### 1. Clone Repository

```powershell
git clone https://github.com/CDMonsalveA/JobSearchTools.git
cd JobSearchTools
```

### 2. Verify Docker Installation

```powershell
# Check Docker is running
docker --version
docker-compose --version

# Test Docker
docker run hello-world
```

If Docker commands fail, start Docker Desktop and wait for it to fully initialize.

## Configuration

### 1. Create Environment File

```powershell
# Copy the example environment file
Copy-Item .env.example .env

# Edit with your preferred editor
notepad .env
```

### 2. Required Configuration

Edit `.env` and set these **required** values:

```bash
# Database Password (choose a strong password)
DB_PASSWORD=YourSecurePassword123!

# Email Configuration
EMAIL_SMTP_USER=your-email@gmail.com
EMAIL_SMTP_PASSWORD=your-app-password-here
EMAIL_TO_ADDRESS=recipient@gmail.com
```

### 3. Optional Configuration

Customize these based on your needs:

```bash
# Scheduler - how often to run spiders (in hours)
SCHEDULER_INTERVAL_HOURS=4

# Scrapy - adjust crawling behavior
SCRAPY_DOWNLOAD_DELAY=1.0  # Seconds between requests
SCRAPY_LOG_LEVEL=INFO       # DEBUG, INFO, WARNING, ERROR
```

### 4. Validate Configuration

```powershell
# Check environment file exists and has required values
if (Select-String -Path .env -Pattern "DB_PASSWORD.*=.+" -Quiet) {
    Write-Host "✓ DB_PASSWORD configured" -ForegroundColor Green
} else {
    Write-Host "✗ DB_PASSWORD missing!" -ForegroundColor Red
}

if (Select-String -Path .env -Pattern "EMAIL_SMTP_PASSWORD.*=.+" -Quiet) {
    Write-Host "✓ EMAIL_SMTP_PASSWORD configured" -ForegroundColor Green
} else {
    Write-Host "✗ EMAIL_SMTP_PASSWORD missing!" -ForegroundColor Red
}
```

## Docker Deployment

### Option 1: Using Start Script (Recommended)

```powershell
# Run the automated startup script
.\start.ps1
```

This script will:
- Check Docker is running
- Create `.env` from template if needed
- Create required directories
- Start all services
- Display status and useful commands

### Option 2: Manual Docker Compose

```powershell
# Start services
docker-compose -f docker-compose.yml -f docker-compose.windows.yml up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f scheduler
```

### Verify Deployment

After starting, verify services are running:

```powershell
# Check all containers
docker-compose ps

# Should show:
# jobsearchtools_db        Up (healthy)
# jobsearchtools_scheduler Up
```

### Initial Spider Run

The scheduler runs immediately on startup, then every 4 hours. Watch the first run:

```powershell
docker-compose logs -f scheduler
```

You should see:
```
[INFO] Starting scheduler with 4 hour interval
[INFO] Running spiders immediately on startup
[INFO] Starting spider run for 1 spider(s)
[INFO] Scheduling spider: mastercard
[INFO] New job stored: mastercard_123456
[INFO] Email notification sent successfully for 5 new jobs
```

## Monitoring

### View Logs

```powershell
# Real-time scheduler logs
docker-compose logs -f scheduler

# Last 100 lines
docker-compose logs --tail=100 scheduler

# Database logs
docker-compose logs postgres

# All services
docker-compose logs -f
```

### Check Service Health

```powershell
# Docker Compose status
docker-compose ps

# Detailed container info
docker inspect jobsearchtools_scheduler
docker inspect jobsearchtools_db
```

### Access Database (Optional)

#### Method 1: PgAdmin Web Interface

```powershell
# Start PgAdmin
docker-compose --profile tools up -d pgadmin

# Access at: http://localhost:5050
# Login: admin@jobsearchtools.com
# Password: (set in .env as PGADMIN_PASSWORD)
```

Add server connection:
- Host: postgres
- Port: 5432
- Database: jobsearchtools
- Username: postgres
- Password: (your DB_PASSWORD)

#### Method 2: Command Line

```powershell
# Connect to PostgreSQL container
docker exec -it jobsearchtools_db psql -U postgres -d jobsearchtools

# Query jobs
SELECT company, COUNT(*) FROM jobs GROUP BY company;

# Check recent jobs
SELECT title, company, date_extracted FROM jobs ORDER BY date_extracted DESC LIMIT 10;

# Exit
\q
```

### Email Notification Testing

To test email notifications without waiting:

```powershell
# Restart scheduler to trigger immediate run
docker-compose restart scheduler

# Watch for email notification in logs
docker-compose logs -f scheduler | Select-String "Email notification"
```

## Maintenance

### Updating Spiders

When adding or modifying spiders:

```powershell
# Rebuild the Docker image
docker-compose build scheduler

# Restart with new image
docker-compose up -d scheduler
```

### Restarting Services

```powershell
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart scheduler

# Stop all
docker-compose down

# Start again
docker-compose -f docker-compose.yml -f docker-compose.windows.yml up -d
```

### Updating Configuration

```powershell
# Edit environment
notepad .env

# Apply changes (requires restart)
docker-compose down
docker-compose -f docker-compose.yml -f docker-compose.windows.yml up -d
```

### Log Rotation

Logs are stored in `./logs/` directory. Clean old logs:

```powershell
# Delete logs older than 30 days
Get-ChildItem -Path .\logs -Recurse -File |
    Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-30)} |
    Remove-Item -Force
```

## Troubleshooting

### Scheduler Not Running

**Symptoms**: No spider runs happening

```powershell
# Check scheduler logs
docker-compose logs scheduler

# Common issues:
# 1. Missing environment variables
docker-compose config  # Verify configuration

# 2. Database connection failed
docker-compose logs postgres

# 3. Container crashed
docker-compose ps  # Check status
docker-compose restart scheduler
```

### Email Notifications Not Sending

**Symptoms**: Spiders run but no emails received

```powershell
# Check email configuration
docker exec jobsearchtools_scheduler python -c "
from jobsearchtools.config.settings import settings
print(f'Email enabled: {settings.email.enabled}')
print(f'SMTP host: {settings.email.smtp_host}')
print(f'To: {settings.email.to_address}')
"

# Test SMTP connection
docker exec jobsearchtools_scheduler python -c "
import smtplib
from jobsearchtools.config.settings import settings
try:
    server = smtplib.SMTP(settings.email.smtp_host, settings.email.smtp_port)
    server.starttls()
    server.login(settings.email.smtp_user, settings.email.smtp_password)
    server.quit()
    print('SMTP connection successful!')
except Exception as e:
    print(f'SMTP error: {e}')
"
```

**Common fixes**:
1. Regenerate Gmail App Password
2. Check EMAIL_SMTP_USER matches Gmail account
3. Verify EMAIL_SMTP_PASSWORD is correct
4. Check spam folder for notifications

### Database Connection Issues

```powershell
# Check database is healthy
docker-compose ps postgres

# Test database connection
docker exec jobsearchtools_db psql -U postgres -c "SELECT 1;"

# View database logs
docker-compose logs postgres

# Restart database
docker-compose restart postgres
```

### No Jobs Being Scraped

**Symptoms**: Spider runs complete with 0 items

This usually means website structure changed.

```powershell
# Run spider in debug mode
docker exec jobsearchtools_scheduler scrapy crawl mastercard -L DEBUG

# Check health warnings in logs
docker-compose logs scheduler | Select-String "Health check warning"
```

**Action**: Update spider selectors in code

### High Memory Usage

```powershell
# Check resource usage
docker stats

# Reduce concurrent spiders
# Edit .env:
SCHEDULER_MAX_INSTANCES=1

# Restart
docker-compose restart scheduler
```

### Port Conflicts

If ports 5432 or 5050 are in use:

```powershell
# Edit .env and change ports:
DB_PORT=5433
PGADMIN_PORT=5051

# Restart
docker-compose down
docker-compose -f docker-compose.yml -f docker-compose.windows.yml up -d
```

## Backup & Recovery

### Database Backup

```powershell
# Create backup directory
New-Item -ItemType Directory -Force -Path .\backups

# Backup database
docker exec jobsearchtools_db pg_dump -U postgres jobsearchtools > ".\backups\backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').sql"
```

### Automated Backup Script

Create `backup.ps1`:

```powershell
$BackupDir = ".\backups"
$Date = Get-Date -Format "yyyyMMdd_HHmmss"
$BackupFile = "$BackupDir\jobsearchtools_$Date.sql"

# Create backup
docker exec jobsearchtools_db pg_dump -U postgres jobsearchtools > $BackupFile

# Compress
Compress-Archive -Path $BackupFile -DestinationPath "$BackupFile.zip"
Remove-Item $BackupFile

Write-Host "Backup completed: $BackupFile.zip"

# Delete backups older than 30 days
Get-ChildItem -Path $BackupDir -Filter "*.zip" |
    Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-30)} |
    Remove-Item -Force
```

Schedule with Windows Task Scheduler to run daily.

### Restore Database

```powershell
# Stop scheduler to prevent conflicts
docker-compose stop scheduler

# Restore from backup
Get-Content .\backups\backup_20240101_120000.sql |
    docker exec -i jobsearchtools_db psql -U postgres jobsearchtools

# Restart scheduler
docker-compose start scheduler
```

### Complete System Backup

```powershell
# Backup everything
$Date = Get-Date -Format "yyyyMMdd"
$BackupName = "jobsearchtools_full_$Date"

# Stop services
docker-compose down

# Backup files
Compress-Archive -Path .env,logs,data -DestinationPath ".\backups\$BackupName.zip"

# Export database
docker-compose up -d postgres
Start-Sleep -Seconds 10  # Wait for DB to start
docker exec jobsearchtools_db pg_dump -U postgres jobsearchtools > ".\backups\$BackupName.sql"
docker-compose down

Write-Host "Full backup completed"
```

## Production Checklist

Before deploying to production:

- [ ] `.env` file configured with strong passwords
- [ ] Gmail App Password created and tested
- [ ] Docker Desktop allocated sufficient resources (4GB+ RAM)
- [ ] Backup script configured and tested
- [ ] Email notifications tested and working
- [ ] Logs directory has sufficient disk space
- [ ] Windows Firewall allows Docker Desktop
- [ ] All spiders tested individually
- [ ] Health monitoring verified in logs
- [ ] Database connection pool sized appropriately
- [ ] Scheduler interval set to desired value (4 hours default)

## Support

For issues or questions:

1. Check logs: `docker-compose logs -f`
2. Review troubleshooting section above
3. Search existing GitHub issues
4. Create new issue with logs and configuration (redact passwords!)

## Next Steps

After successful deployment:

1. Monitor the first few spider runs
2. Verify email notifications are received
3. Check database for new job entries
4. Set up automated backups
5. Add more company spiders as needed

---

**Security Note**: Never commit `.env` file to version control. Keep database and email passwords secure.
