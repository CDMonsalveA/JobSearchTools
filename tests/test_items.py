"""Tests for Scrapy Items."""

from datetime import datetime

from jobsearchtools.job_scraper.job_scraper.items import JobScraperItem


class TestJobScraperItem:
    """Test JobScraperItem fields and functionality."""

    def test_required_fields_exist(self):
        """Test all required fields are defined."""
        item = JobScraperItem()
        required_fields = [
            "job_id",
            "title",
            "company",
            "location",
            "url",
            "date_extracted",
        ]
        for field in required_fields:
            assert field in item.fields

    def test_optional_fields_exist(self):
        """Test optional fields are defined."""
        item = JobScraperItem()
        optional_fields = ["description", "date_posted", "salary", "was_opened"]
        for field in optional_fields:
            assert field in item.fields

    def test_set_and_get_values(self):
        """Test setting and getting item values."""
        item = JobScraperItem()
        today = datetime.now().strftime("%Y-%m-%d")

        item["job_id"] = "test_123"
        item["title"] = "Software Engineer"
        item["company"] = "TestCorp"
        item["location"] = "Bogotá, Colombia"
        item["url"] = "https://example.com/job/123"
        item["date_extracted"] = today

        assert item["job_id"] == "test_123"
        assert item["title"] == "Software Engineer"
        assert item["company"] == "TestCorp"
        assert item["location"] == "Bogotá, Colombia"
        assert item["url"] == "https://example.com/job/123"
        assert item["date_extracted"] == today

    def test_optional_fields_can_be_none(self):
        """Test optional fields can be left empty."""
        item = JobScraperItem()
        item["job_id"] = "test_123"
        item["title"] = "Engineer"
        item["company"] = "Company"
        item["location"] = "Remote"
        item["url"] = "https://example.com"
        item["date_extracted"] = datetime.now().strftime("%Y-%m-%d")

        # Optional fields can be None
        assert item.get("description") is None
        assert item.get("salary") is None
        assert item.get("was_opened") is None
