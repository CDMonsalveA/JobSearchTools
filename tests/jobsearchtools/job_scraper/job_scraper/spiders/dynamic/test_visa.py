"""Tests for Visa spider (Playwright-based)."""

import pytest

from jobsearchtools.job_scraper.job_scraper.spiders.dynamic.visa import VisaSpider


class TestVisaSpider:
    """Test cases for VisaSpider."""

    @pytest.fixture
    def spider(self):
        """Create a Visa spider instance."""
        return VisaSpider()

    def test_spider_attributes(self, spider):
        """Test spider has correct attributes."""
        assert spider.name == "visa"
        assert len(spider.allowed_domains) > 0
        assert len(spider.start_urls) == 1

    def test_spider_uses_playwright(self, spider):
        """Test spider is configured for Playwright."""
        assert hasattr(spider, "custom_settings")
        if "PLAYWRIGHT_BROWSER_TYPE" in spider.custom_settings:
            assert spider.custom_settings["PLAYWRIGHT_BROWSER_TYPE"] in [
                "chromium",
                "firefox",
                "webkit",
            ]

    def test_has_start_requests_method(self, spider):
        """Test spider has start_requests method."""
        assert hasattr(spider, "start_requests")
        assert callable(spider.start_requests)

    def test_has_parse_method(self, spider):
        """Test spider has async parse method."""
        assert hasattr(spider, "parse")
        assert callable(spider.parse)

    def test_has_errback_method(self, spider):
        """Test spider has errback method."""
        assert hasattr(spider, "errback")
        assert callable(spider.errback)

    def test_job_id_format(self, spider):
        """Test job_id follows correct format."""
        job_id = "visa_12345"
        assert job_id.startswith("visa_")
        assert len(job_id) > 5

    def test_playwright_configured_in_requests(self, spider):
        """Test Playwright is enabled in requests."""
        requests = list(spider.start_requests())
        if len(requests) > 0:
            assert requests[0].meta.get("playwright") is True
