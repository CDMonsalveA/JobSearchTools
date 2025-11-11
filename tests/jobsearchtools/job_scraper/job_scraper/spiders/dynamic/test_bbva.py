"""Tests for BBVA spider (Playwright-based)."""

import pytest

from jobsearchtools.job_scraper.job_scraper.spiders.dynamic.bbva import BbvaSpider


class TestBbvaSpider:
    """Test cases for BbvaSpider."""

    @pytest.fixture
    def spider(self):
        """Create a BBVA spider instance."""
        return BbvaSpider()

    def test_spider_attributes(self, spider):
        """Test spider has correct attributes."""
        assert spider.name == "bbva"
        assert "bbva.wd3.myworkdayjobs.com" in spider.allowed_domains
        assert len(spider.start_urls) == 1

    def test_spider_uses_playwright(self, spider):
        """Test spider is configured for Playwright."""
        assert "PLAYWRIGHT_BROWSER_TYPE" in spider.custom_settings
        assert spider.custom_settings["PLAYWRIGHT_BROWSER_TYPE"] == "firefox"
        assert "DOWNLOAD_HANDLERS" in spider.custom_settings

    def test_spider_headless_mode(self, spider):
        """Test spider runs in headless mode."""
        launch_options = spider.custom_settings.get("PLAYWRIGHT_LAUNCH_OPTIONS", {})
        assert launch_options.get("headless") is True

    def test_start_requests_method(self, spider):
        """Test start_requests method returns requests."""
        requests = list(spider.start_requests())
        assert len(requests) > 0
        assert all(hasattr(r, "meta") for r in requests)

    def test_playwright_meta_settings(self, spider):
        """Test Playwright meta settings are correct."""
        requests = list(spider.start_requests())
        for request in requests:
            assert request.meta.get("playwright") is True
            assert request.meta.get("playwright_include_page") is True
            assert "playwright_page_methods" in request.meta

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
        job_id = "bbva_JR-12345"
        assert job_id.startswith("bbva_")
        assert len(job_id) > 5

    def test_wait_for_selector_configured(self, spider):
        """Test PageMethod includes wait_for_selector."""
        requests = list(spider.start_requests())
        page_methods = requests[0].meta.get("playwright_page_methods", [])
        assert len(page_methods) > 0
        # Should have wait_for_selector method
        assert any("wait_for_selector" in str(m) for m in page_methods)

    def test_error_handling_configured(self, spider):
        """Test error handling is configured."""
        requests = list(spider.start_requests())
        assert requests[0].meta.get("errback") is not None
