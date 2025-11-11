"""Tests for dynamic Playwright-based spiders (BBVA, Visa)."""

import pytest

from jobsearchtools.job_scraper.job_scraper.spiders.dynamic.bbva import BbvaSpider
from jobsearchtools.job_scraper.job_scraper.spiders.dynamic.visa import VisaSpider


class TestDynamicSpiders:
    """Test dynamic spiders that use Playwright."""

    @pytest.mark.parametrize(
        "spider_class,expected_name,expected_domain",
        [
            (BbvaSpider, "bbva", "bbva.wd3.myworkdayjobs.com"),
            (VisaSpider, "visa", "corporate.visa.com"),
        ],
    )
    def test_spider_configuration(self, spider_class, expected_name, expected_domain):
        """Test spider has correct name and domain configuration."""
        spider = spider_class()
        assert spider.name == expected_name
        assert expected_domain in spider.allowed_domains

    @pytest.mark.parametrize("spider_class", [BbvaSpider, VisaSpider])
    def test_has_start_requests_method(self, spider_class):
        """Test dynamic spiders override start_requests for Playwright."""
        spider = spider_class()
        assert hasattr(spider, "start_requests")
        assert callable(spider.start_requests)

    @pytest.mark.parametrize("spider_class", [BbvaSpider, VisaSpider])
    def test_has_async_parse_method(self, spider_class):
        """Test dynamic spiders have async parse method."""
        spider = spider_class()
        assert hasattr(spider, "parse")
        assert callable(spider.parse)


class TestBbvaSpider:
    """Test BBVA-specific functionality."""

    @pytest.fixture
    def spider(self):
        """Create BBVA spider instance."""
        return BbvaSpider()

    def test_has_custom_settings(self, spider):
        """Test BBVA spider has Playwright settings configured."""
        assert hasattr(spider, "custom_settings")
        settings = spider.custom_settings
        assert "PLAYWRIGHT_BROWSER_TYPE" in settings
        assert "DOWNLOAD_HANDLERS" in settings

    def test_targets_colombia(self, spider):
        """Test BBVA spider is configured for Colombian jobs."""
        assert "bbva.wd3.myworkdayjobs.com" in spider.allowed_domains

    def test_has_errback_method(self, spider):
        """Test BBVA spider has error callback for Playwright cleanup."""
        assert hasattr(spider, "errback")
        assert callable(spider.errback)


class TestVisaSpider:
    """Test Visa-specific functionality."""

    @pytest.fixture
    def spider(self):
        """Create Visa spider instance."""
        return VisaSpider()

    def test_has_custom_settings(self, spider):
        """Test Visa spider has Playwright settings configured."""
        assert hasattr(spider, "custom_settings")
        settings = spider.custom_settings
        assert "PLAYWRIGHT_BROWSER_TYPE" in settings
        assert "DOWNLOAD_HANDLERS" in settings

    def test_targets_colombia(self, spider):
        """Test Visa spider is configured for Colombian jobs."""
        assert any("Bogot" in url for url in spider.start_urls)

    def test_has_errback_method(self, spider):
        """Test Visa spider has error callback for Playwright cleanup."""
        assert hasattr(spider, "errback")
        assert callable(spider.errback)
