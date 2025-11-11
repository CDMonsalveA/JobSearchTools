# Spider Tests

This directory contains tests for all JobSearchTools spiders.

## Test Structure

```
tests/jobsearchtools/job_scraper/job_scraper/spiders/
├── conftest.py                    # Shared pytest fixtures
├── test_common.py                 # Integration tests for all spiders
├── static/
│   ├── test_static_spiders.py     # Combined tests for Mastercard, Avianca, Bancolombia, Nequi
│   ├── test_citi.py               # Basic tests for Citi spider
│   ├── test_ecopetrol.py          # Basic tests for Ecopetrol spider
│   ├── test_scotiabank.py         # Basic tests for Scotiabank spider
│   └── test_sura.py               # Basic tests for Sura spider
└── dynamic/
    ├── test_bbva.py               # Tests for BBVA Playwright spider
    └── test_visa.py               # Tests for Visa Playwright spider
```

## Running Tests

Run all spider tests:
```powershell
.\.venv\Scripts\pytest.exe tests/jobsearchtools/job_scraper/job_scraper/spiders/ -v
```

Run with coverage:
```powershell
.\.venv\Scripts\pytest.exe tests/jobsearchtools/job_scraper/job_scraper/spiders/ -v --cov
```

Run only static spider tests:
```powershell
.\.venv\Scripts\pytest.exe tests/jobsearchtools/job_scraper/job_scraper/spiders/static/ -v
```

Run only dynamic spider tests:
```powershell
.\.venv\Scripts\pytest.exe tests/jobsearchtools/job_scraper/job_scraper/spiders/dynamic/ -v
```

## Test Coverage

### What's Tested

✅ **Spider Configuration**
- Spider name, domains, and start URLs
- Parse method existence and callability
- Required attributes (name, allowed_domains, start_urls)

✅ **Spider-Specific Features**
- Playwright configuration for dynamic spiders (BBVA, Visa)
- Parse methods for detail pages (Mastercard, Nequi)
- URL filters and search parameters

✅ **Integration Tests**
- All spiders can be imported
- Spider names are unique across the project
- All spiders have required attributes and methods

### What's NOT Tested

❌ **Complex Parsing Logic**
- Individual CSS/XPath selectors
- JSON extraction and data transformation
- Pagination and crawling behavior

**Rationale**: These require complex mocking of HTTP responses and are prone to breaking when site structures change. The spiders are tested in production via Docker deployment every 4 hours.

## Test Philosophy

These tests follow a **simple but functional** approach:

1. **Validate Structure**: Ensure spiders are properly configured
2. **Test Imports**: Verify all modules load without errors
3. **Check Attributes**: Confirm required properties exist
4. **Avoid Over-Mocking**: Don't test implementation details that belong in integration tests

The goal is **fast, reliable tests** that catch configuration errors and regressions without maintaining brittle mocks of external websites.

## Current Coverage

- **44 tests total**
- **100% pass rate**
- **21% code coverage** (focused on spider initialization, not parsing logic)
- **All 10 spiders covered** (8 static + 2 dynamic)

## Adding Tests for New Spiders

When adding a new spider:

1. Add basic attribute test to `test_static_spiders.py` (or create `test_<spider>.py`)
2. Update `test_common.py` imports to include the new spider
3. Add spider-specific tests if it has unique features (e.g., special parse methods)

Keep it simple! Focus on configuration and structure, not parsing implementation.
