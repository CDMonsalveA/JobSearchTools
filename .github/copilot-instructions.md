# Copilot Instructions for JobSearchTools

## Project Overview

JobSearchTools is a production-ready job search automation toolkit built with Python 3.11+ and Scrapy. The project scrapes job listings from multiple Colombian company career sites and stores them in a PostgreSQL database. The architecture supports both static HTML and JavaScript-rendered pages via Scrapy-Playwright integration. The system runs on Docker every 4 hours and sends email notifications for new job listings.

## Architecture

### Scrapy Project Structure

The production structure is located in `src/jobsearchtools/job_scraper/` with spiders organized into:
- `spiders/static/` - For traditional HTML scraping (8 spiders: avianca, bancolombia, citi, ecopetrol, mastercard, nequi, scotiabank, sura)
- `spiders/dynamic/` - For JavaScript-heavy sites requiring Playwright (2 spiders: bbva, visa)

### Configuration System

Configuration lives in `src/jobsearchtools/config/config.py` using a singleton pattern (`config` instance). Key settings:
- Database path: `src/jobsearchtools/db/jobsearchtools.db`
- Scrapy settings integration via `config.get("scrapy", {})`
- Override defaults by calling `config.set(key, value)` or passing dict to `Config()`

Example from `settings.py`:
```python
from jobsearchtools.config.config import config
BOT_NAME = config.get("scrapy", {}).get("bot_name", "job_scraper")
```

### Data Pipeline

**Items Schema** (`job_scraper/items.py`):
```python
job_id          # Primary key, must be unique per company
title           # Job title
company         # Company name (hardcoded in spider)
location        # City or "Remote"
description     # Full job description (optional, from detail page)
salary          # Salary info if available
url             # Application URL
date_posted     # Posting date from site
date_extracted  # UTC timestamp when scraped
was_opened      # Track if job detail was visited (nullable)
```

**Pipeline**: `SQLiteUniqueJobsPipeline` deduplicates by `job_id` before insertion. The pipeline auto-detects project root by searching for `pyproject.toml` or `.git`, enabling correct database path resolution from any execution context.

### Spider Development Patterns

**Static HTML Spider Template**:
```python
class CompanySpider(scrapy.Spider):
    name = "company"
    allowed_domains = ["company.com"]
    start_urls = ["https://careers.company.com/jobs"]

    def parse(self, response):
        # Extract job data from listings
        # Yield response.follow() for detail pages
        # Use cb_kwargs to pass partial item to detail parser
```

**Dynamic Playwright Spider** (see `job_scraper/spiders/dynamic/visa.py`):
- Set custom settings: `PLAYWRIGHT_BROWSER_TYPE`, `DOWNLOAD_HANDLERS`
- Override `start_requests()` with `meta={"playwright": True, "playwright_include_page": True}`
- Use `async def parse()` and extract `page = response.meta["playwright_page"]`
- Always `await page.close()` and implement `async def errback()` for cleanup

**Middleware**: `SetRandomUserAgentMiddleware` rotates user agents from `USER_AGENTS` list in settings to avoid detection.

## Development Workflow

### Environment Setup
```powershell
# Poetry manages dependencies (Poetry v2.0+)
poetry install
poetry shell
```

### Running Scrapers
```powershell
# From Scrapy project root (where scrapy.cfg exists)
cd src/jobsearchtools/job_scraper
scrapy crawl mastercard  # or any other spider name

# Or run all spiders via scheduler
python -m jobsearchtools.scheduler
```

### Testing
```powershell
# Run all tests with coverage (see pyproject.toml for config)
pytest

# Coverage report outputs to htmlcov/index.html
# Tests follow pattern: tests/jobsearchtools/job_scraper/job_scraper/test_*.py
```

**Test Structure**: Tests mirror `src/` structure. Use `pytest.mark` decorators (`@pytest.mark.unit`, `@pytest.mark.integration`) for selective runs.

### Code Quality
- **Ruff** handles linting and formatting (line-length: 88, target: py311)
- Pre-commit hooks run Ruff automatically (see `.pre-commit-config.yaml`)
- Enable hooks: `pre-commit install`
- Key lint rules: enforces imports sorting (isort), pyupgrade syntax, ignores S101 (assert) and T201 (print) in tests

## Project-Specific Conventions

### Code Style Requirements
- **No emojis** in code, comments, or docstrings - maintain professional tone
- Use double quotes for strings (Ruff formatted)
- Follow PEP 8 naming: `snake_case` for functions/variables, `PascalCase` for classes
- Comprehensive docstrings for classes/functions with Args/Returns sections

### Import Organization
```python
# Standard library
import json
from datetime import datetime

# Third-party
import scrapy
from scrapy_playwright.page import PageMethod

# Local application
from ...items import JobScraperItem
from jobsearchtools.config.config import config
```

### Spider Naming
- Spider `name` attribute: lowercase company name (e.g., `"mastercard"`)
- Class name: PascalCase + "Spider" suffix (e.g., `MastercardSpider`)
- File name: matches spider name (e.g., `mastercard.py`)

### Database Considerations
- Current: SQLite at `src/jobsearchtools/db/jobsearchtools.db`
- Future: PostgreSQL migration planned (branch: `Add-SQL-pipeline`)
- Always use `job_id` for deduplication; format: `{company}_{unique_id}`

### Logging
- Use spider's logger: `self.logger.info()`, `self.logger.debug()`
- Log key events: job found, duplicate skipped, pagination followed
- Log User-Agent in parse method for debugging rate limits

## Key Files Reference

- `pyproject.toml` - Dependencies, Ruff config, pytest settings, coverage rules
- `src/jobsearchtools/config/settings.py` - Pydantic-based configuration with environment variables
- `src/jobsearchtools/config/config.py` - Legacy configuration (still used by tests)
- `src/jobsearchtools/job_scraper/job_scraper/pipelines.py` - PostgreSQL pipeline with connection pooling
- `src/jobsearchtools/job_scraper/job_scraper/extensions.py` - Email notifications and health monitoring
- `src/jobsearchtools/job_scraper/job_scraper/settings.py` - Scrapy configuration
- `src/jobsearchtools/scheduler.py` - APScheduler for running spiders every 4 hours
- `.pre-commit-config.yaml` - Git hooks for code quality

## Common Tasks

**Add New Spider**:
1. Create spider in `src/jobsearchtools/job_scraper/job_scraper/spiders/static/` or `dynamic/`
2. Import `JobScraperItem`, populate required fields
3. Set unique `job_id` format: `{spider.name}_{company_job_id}`
4. Test from `src/jobsearchtools/job_scraper/`: `scrapy crawl {spider_name}`

**Update Configuration**:
```python
from jobsearchtools.config.config import config
config.set("db", {"type": "postgresql", "name": "jobs", "path": "..."})
```

**Check Coverage**:
```powershell
pytest --cov-report=term-missing
# or open htmlcov/index.html in browser
```

## Integration Points

- **Scrapy-Playwright**: Installed but only enabled per-spider via custom settings
- **IPython**: Default Scrapy shell (`scrapy shell {url}`)
- **dotenv**: Loads environment variables from `.env` (not committed)
- **Poetry**: Lock file (`poetry.lock`) must be committed for reproducible builds

## Best Practices

- Always respect `ROBOTSTXT_OBEY` and `DOWNLOAD_DELAY` settings
- Use `response.follow()` for relative URLs instead of manual URL construction
- Extract job descriptions from detail pages when available (improves data quality)
- Handle missing fields gracefully with `.get()` and None defaults
- Test spiders with `--loglevel=DEBUG` to diagnose issues
- Update `__planned_spiders.md` when identifying new scraping targets
