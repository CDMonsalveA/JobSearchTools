"""Tests for Sura spider."""

import pytest

from jobsearchtools.job_scraper.job_scraper.spiders.static.sura import SuraSpider


class TestSuraSpider:
    """Test cases for SuraSpider."""

    @pytest.fixture
    def spider(self):
        """Create a Sura spider instance."""
        return SuraSpider()

    def test_spider_attributes(self, spider):
        """Test spider has correct attributes."""
        assert spider.name == "sura"
        assert len(spider.allowed_domains) > 0
        assert len(spider.start_urls) == 1

    def test_spider_has_parse_method(self, spider):
        """Test spider has parse method."""
        assert hasattr(spider, "parse")
        assert callable(spider.parse)

    def test_company_name(self, spider):
        """Test company name is Sura."""
        assert spider.name == "sura"

    def test_job_id_format(self, spider):
        """Test job_id follows correct format."""
        job_id = "sura_12345"
        assert job_id.startswith("sura_")
        assert len(job_id) > 5
