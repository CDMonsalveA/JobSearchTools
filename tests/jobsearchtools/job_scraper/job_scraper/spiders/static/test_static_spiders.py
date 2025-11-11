"""Simple functional tests for static spiders."""

import pytest

from jobsearchtools.job_scraper.job_scraper.spiders.static.avianca import (
    AviancaSpider,
)
from jobsearchtools.job_scraper.job_scraper.spiders.static.bancolombia import (
    BancolombiaSpider,
)
from jobsearchtools.job_scraper.job_scraper.spiders.static.mastercard import (
    MastercardSpider,
)
from jobsearchtools.job_scraper.job_scraper.spiders.static.nequi import NequiSpider


class TestStaticSpiders:
    """Test static spiders basic functionality."""

    @pytest.mark.parametrize(
        "spider_class,expected_name,expected_domain",
        [
            (MastercardSpider, "mastercard", "careers.mastercard.com"),
            (AviancaSpider, "avianca", "jobs.avianca.com"),
            (BancolombiaSpider, "bancolombia", "empleo.grupobancolombia.com"),
            (NequiSpider, "nequi", "lapipolnequi.buk.co"),
        ],
    )
    def test_spider_attributes(self, spider_class, expected_name, expected_domain):
        """Test spider has correct basic attributes."""
        spider = spider_class()
        assert spider.name == expected_name
        assert expected_domain in spider.allowed_domains
        assert len(spider.start_urls) > 0
        assert hasattr(spider, "parse")
        assert callable(spider.parse)


class TestMastercardSpider:
    """Test Mastercard spider specifics."""

    @pytest.fixture
    def spider(self):
        """Create a Mastercard spider instance."""
        return MastercardSpider()

    def test_has_parse_detail_method(self, spider):
        """Test spider has parse_detail method for job details."""
        assert hasattr(spider, "parse_detail")
        assert callable(spider.parse_detail)


class TestAviancaSpider:
    """Test Avianca spider specifics."""

    @pytest.fixture
    def spider(self):
        """Create an Avianca spider instance."""
        return AviancaSpider()

    def test_start_url_search_filter(self, spider):
        """Test start URL includes Colombia search filter."""
        assert any("locationsearch=Co" in url for url in spider.start_urls)


class TestNequiSpider:
    """Test Nequi spider specifics."""

    @pytest.fixture
    def spider(self):
        """Create a Nequi spider instance."""
        return NequiSpider()

    def test_has_parse_job_details_method(self, spider):
        """Test spider has parse_job_details method."""
        assert hasattr(spider, "parse_job_details")
        assert callable(spider.parse_job_details)


class TestBancolombiaSpider:
    """Test Bancolombia spider specifics."""

    @pytest.fixture
    def spider(self):
        """Create a Bancolombia spider instance."""
        return BancolombiaSpider()

    def test_start_url_has_location_filter(self, spider):
        """Test start URL includes location filter."""
        assert any("location=" in url for url in spider.start_urls)
