# JobSearchTools

> Automated job listing scraper and notification system for Colombian companies

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Scrapy](https://img.shields.io/badge/scrapy-2.13+-green.svg)](https://scrapy.org/)
[![PostgreSQL](https://img.shields.io/badge/postgresql-15+-blue.svg)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

## 🎯 Overview

JobSearchTools is an automated job search toolkit that:
- Scrapes job listings from multiple Colombian company career sites
- Stores jobs in a PostgreSQL database with duplicate detection
- Sends email notifications when new positions are found
- Runs on a schedule (every 4 hours by default)
- Monitors spider health and detects website structure changes
- Deploys easily via Docker on Windows

## ✨ Features

- **🕷️ Multiple Scrapers**: Support for both static HTML and JavaScript-rendered sites via Scrapy-Playwright
- **🗄️ PostgreSQL Storage**: Robust database with connection pooling and duplicate prevention
- **📧 Email Notifications**: HTML-formatted alerts with job details sent to your inbox
- **⏰ Automated Scheduling**: APScheduler runs spiders every 4 hours (configurable)
- **🏥 Health Monitoring**: Detects when spiders fail or websites change structure
- **🐳 Docker Deployment**: Complete containerized setup with docker-compose
- **🧪 Testing & Quality**: Pre-commit hooks, pytest, and ruff for code quality

## 📋 Requirements

### For Docker Deployment (Recommended)
- Docker Desktop for Windows
- 4GB RAM minimum
- 10GB disk space

### For Local Development
- Python 3.11 or higher
- Poetry 2.0+
- PostgreSQL 15+ (or Docker)

## 🚀 Quick Start with Docker

### 1. Clone and Configure

```bash
git clone https://github.com/CDMonsalveA/JobSearchTools.git
cd JobSearchTools

# Copy environment template
cp .env.example .env
```

### 2. Edit Configuration

Edit `.env` and set these required values:

```bash
# Database
DB_PASSWORD=your_secure_password

# Email (for Gmail, use App Password)
EMAIL_SMTP_USER=your_email@gmail.com
EMAIL_SMTP_PASSWORD=your_app_password
EMAIL_TO_ADDRESS=your_email@gmail.com
```

### 3. Start Services

```powershell
# Windows PowerShell
.\start.ps1

# Or manually
docker-compose -f docker-compose.yml -f docker-compose.windows.yml up -d
```

### 4. Monitor Logs

```bash
# Watch scheduler logs
docker-compose logs -f scheduler

# View all services
docker-compose ps
```

## 🛠️ Local Development Setup

### 1. Install Dependencies

```bash
# Install Poetry if not already installed
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -

# Install project dependencies
poetry install

# Activate virtual environment
poetry shell
```

### 2. Set Up Database

```bash
# Start PostgreSQL with Docker
docker run -d \
  --name jobsearch-postgres \
  -e POSTGRES_DB=jobsearchtools \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  postgres:15-alpine
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your local settings
```

### 4. Run Spiders Manually

```bash
# Navigate to Scrapy project
cd src/jobsearchtools/job_scraper

# Run a single spider
scrapy crawl mastercard

# Run with debug output
scrapy crawl mastercard -L DEBUG
```

### 5. Run Scheduler

```bash
# From project root
python -m jobsearchtools.scheduler
```

## 📁 Project Structure

```
JobSearchTools/
├── src/
│   └── jobsearchtools/
│       ├── config/
│       │   ├── config.py         # Legacy configuration
│       │   └── settings.py       # Pydantic settings with env vars
│       ├── notifications/
│       │   └── email_notifier.py # Email notification system
│       ├── job_scraper/
│       │   └── job_scraper/
│       │       ├── spiders/
│       │       │   ├── static/   # Traditional HTML spiders
│       │       │   │   └── mastercard.py
│       │       │   └── dynamic/  # Playwright-based spiders
│       │       │       └── visa.py
│       │       ├── items.py      # Job data schema
│       │       ├── pipelines.py  # PostgreSQL pipeline
│       │       ├── extensions.py # Monitoring & notifications
│       │       └── settings.py   # Scrapy configuration
│       └── scheduler.py          # APScheduler service
├── tests/                        # Test suite
├── docker-compose.yml            # Main Docker config
├── docker-compose.windows.yml    # Windows-specific overrides
├── Dockerfile                    # Application container
├── pyproject.toml               # Poetry dependencies & tools
└── .env.example                 # Environment template
```

## 🔧 Configuration

### Environment Variables

All configuration is done via environment variables in `.env`:

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_PASSWORD` | PostgreSQL password | **Required** |
| `EMAIL_SMTP_USER` | SMTP username | **Required** |
| `EMAIL_SMTP_PASSWORD` | SMTP password/app password | **Required** |
| `SCHEDULER_INTERVAL_HOURS` | Hours between spider runs | `4` |
| `SCRAPY_DOWNLOAD_DELAY` | Delay between requests (seconds) | `1.0` |
| `SCRAPY_LOG_LEVEL` | Logging level | `INFO` |

See `.env.example` for complete list.

### Adding New Spiders

#### Static HTML Spider

Create `src/jobsearchtools/job_scraper/job_scraper/spiders/static/company.py`:

```python
import scrapy
from datetime import datetime
from ...items import JobScraperItem

class CompanySpider(scrapy.Spider):
    name = "company"
    allowed_domains = ["company.com"]
    start_urls = ["https://careers.company.com/jobs"]

    def parse(self, response):
        for job in response.css(".job-listing"):
            item = JobScraperItem()
            item["job_id"] = f"company_{job.css('::attr(data-id)').get()}"
            item["title"] = job.css(".title::text").get()
            item["company"] = "Company Name"
            item["location"] = job.css(".location::text").get()
            item["url"] = response.urljoin(job.css("a::attr(href)").get())
            item["date_extracted"] = datetime.utcnow().isoformat()
            yield item
```

#### Dynamic JavaScript Spider

For sites requiring JavaScript rendering, use Playwright:

```python
from scrapy_playwright.page import PageMethod

class DynamicSpider(scrapy.Spider):
    name = "dynamic"

    custom_settings = {
        "PLAYWRIGHT_BROWSER_TYPE": "chromium",
        "DOWNLOAD_HANDLERS": {
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
    }

    def start_requests(self):
        yield scrapy.Request(
            url=self.start_urls[0],
            meta={
                "playwright": True,
                "playwright_include_page": True,
            },
        )
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/jobsearchtools/job_scraper/test_pipelines.py

# Run with markers
pytest -m unit
pytest -m integration
```

## 🔍 Monitoring & Troubleshooting

### View Logs

```bash
# Scheduler logs
docker-compose logs -f scheduler

# Database logs
docker-compose logs postgres

# All services
docker-compose logs -f
```

### Check Spider Health

The system automatically detects issues:
- Spiders that complete with 0 items scraped
- Errors during spider runs
- Database connection problems

Check logs for health warnings.

### Access Database

```bash
# Start PgAdmin (optional)
docker-compose --profile tools up -d pgadmin

# Access at http://localhost:5050
# Email: admin@jobsearchtools.com
# Password: admin (set in .env as PGADMIN_PASSWORD)
```

### Common Issues

**Issue**: Email notifications not working
**Solution**:
- For Gmail, create an [App Password](https://support.google.com/accounts/answer/185833)
- Verify `EMAIL_SMTP_PASSWORD` in `.env`
- Check `EMAIL_ENABLED=True`

**Issue**: Docker container fails to start
**Solution**:
- Verify `.env` has all required variables
- Check Docker Desktop is running
- Review logs: `docker-compose logs scheduler`

**Issue**: Spider finds no jobs
**Solution**:
- Website structure may have changed
- Run spider with DEBUG: `scrapy crawl spider_name -L DEBUG`
- Check health monitoring logs for warnings

## 📊 Database Schema

### `jobs` Table

| Column | Type | Description |
|--------|------|-------------|
| `id` | SERIAL | Primary key |
| `job_id` | VARCHAR(255) | Unique identifier (company_jobid) |
| `title` | TEXT | Job title |
| `company` | VARCHAR(255) | Company name |
| `location` | VARCHAR(255) | Job location |
| `description` | TEXT | Full job description |
| `salary` | VARCHAR(255) | Salary information |
| `url` | TEXT | Application URL |
| `date_posted` | TIMESTAMP | When job was posted |
| `date_extracted` | TIMESTAMP | When job was scraped |
| `was_opened` | BOOLEAN | If detail page was visited |

### `spider_runs` Table

Tracks spider execution history for monitoring.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Install pre-commit hooks: `pre-commit install`
4. Make your changes and commit: `git commit -m 'Add amazing feature'`
5. Push to branch: `git push origin feature/amazing-feature`
6. Open a Pull Request

### Code Style

- Use [Ruff](https://github.com/astral-sh/ruff) for formatting and linting
- Follow PEP 8 conventions
- Add docstrings to all classes and functions
- Write tests for new features

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details

## 🙏 Acknowledgments

- Built with [Scrapy](https://scrapy.org/)
- JavaScript rendering via [Playwright](https://playwright.dev/)
- Scheduling with [APScheduler](https://apscheduler.readthedocs.io/)
- Configuration management with [Pydantic Settings](https://docs.pydantic.dev/)

## 📧 Contact

Carlos Daniel Monsalve - [@CDMonsalveA](https://github.com/CDMonsalveA)

Project Link: [https://github.com/CDMonsalveA/JobSearchTools](https://github.com/CDMonsalveA/JobSearchTools)

---

**Note**: This tool is for personal job search automation. Always respect websites' robots.txt and terms of service.
