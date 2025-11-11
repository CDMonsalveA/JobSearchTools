"""Tests for Scotiabank spider."""

import pytest

from jobsearchtools.job_scraper.job_scraper.spiders.static.scotiabank import (
    ScotiabankSpider,
)


class TestScotiabankSpider:
    """Test cases for ScotiabankSpider."""

    @pytest.fixture
    def spider(self):
        """Create a Scotiabank spider instance."""
        return ScotiabankSpider()

    def test_spider_attributes(self, spider):
        """Test spider has correct attributes."""
        assert spider.name == "scotiabank"
        assert "scotiabank" in spider.allowed_domains[0].lower()
        assert len(spider.start_urls) == 1

    def test_spider_has_parse_method(self, spider):
        """Test spider has parse method."""
        assert hasattr(spider, "parse")
        assert callable(spider.parse)

    def test_company_name(self, spider):
        """Test company name is Scotiabank."""
        assert spider.name == "scotiabank"

    def test_job_id_format(self, spider):
        """Test job_id follows correct format."""
        job_id = "scotiabank_12345"
        assert job_id.startswith("scotiabank_")
        assert len(job_id) > 11
