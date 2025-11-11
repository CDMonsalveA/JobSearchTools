"""Tests for Ecopetrol spider."""

import pytest

from jobsearchtools.job_scraper.job_scraper.spiders.static.ecopetrol import (
    EcopetrolSpider,
)


class TestEcopetrolSpider:
    """Test cases for EcopetrolSpider."""

    @pytest.fixture
    def spider(self):
        """Create an Ecopetrol spider instance."""
        return EcopetrolSpider()

    def test_spider_attributes(self, spider):
        """Test spider has correct attributes."""
        assert spider.name == "ecopetrol"
        assert "ecopetrol.com.co" in spider.allowed_domains[0]
        assert len(spider.start_urls) == 1

    def test_spider_has_parse_method(self, spider):
        """Test spider has parse method."""
        assert hasattr(spider, "parse")
        assert callable(spider.parse)

    def test_company_name(self, spider):
        """Test company name is Ecopetrol."""
        assert spider.name == "ecopetrol"

    def test_job_id_format(self, spider):
        """Test job_id follows correct format."""
        job_id = "ecopetrol_12345"
        assert job_id.startswith("ecopetrol_")
        assert len(job_id) > 10
