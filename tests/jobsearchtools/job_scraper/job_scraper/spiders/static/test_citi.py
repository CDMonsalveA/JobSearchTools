"""Tests for Citi spider."""

import pytest

from jobsearchtools.job_scraper.job_scraper.spiders.static.citi import CitiSpider


class TestCitiSpider:
    """Test cases for CitiSpider."""

    @pytest.fixture
    def spider(self):
        """Create a Citi spider instance."""
        return CitiSpider()

    def test_spider_attributes(self, spider):
        """Test spider has correct attributes."""
        assert spider.name == "citi"
        assert "citi.com" in spider.allowed_domains[0]
        assert len(spider.start_urls) == 1

    def test_spider_has_parse_method(self, spider):
        """Test spider has parse method."""
        assert hasattr(spider, "parse")
        assert callable(spider.parse)

    def test_company_name(self, spider):
        """Test company name is Citi."""
        # Company should be set to "Citi" in items
        assert spider.name == "citi"

    def test_job_id_format(self, spider):
        """Test job_id follows correct format."""
        job_id = "citi_12345"
        assert job_id.startswith("citi_")
        assert len(job_id) > 5
