from datetime import datetime

from jobsearchtools.job_scraper.job_scraper.items import JobScraperItem


class TestJobScraperItem:
    def test_fields_exist(self):
        item = JobScraperItem()
        expected_fields = [
            "job_id",
            "title",
            "company",
            "location",
            "description",
            "date_posted",
            "date_extracted",
            "was_opened",
            "url",
            "salary",
        ]
        for field in expected_fields:
            assert field in item.fields

    def test_set_and_get_fields(self):
        today = datetime.now().strftime("%Y-%m-%d")
        item = JobScraperItem()
        item["job_id"] = "123"
        item["title"] = "Software Engineer"
        item["company"] = "TestCorp"
        item["location"] = "Remote"
        item["description"] = "Develop software."
        item["date_posted"] = today
        item["date_extracted"] = today
        item["was_opened"] = True
        item["url"] = "https://example.com/job/123"
        item["salary"] = "$100k"
        assert item["job_id"] == "123"
        assert item["title"] == "Software Engineer"
        assert item["company"] == "TestCorp"
        assert item["location"] == "Remote"
        assert item["description"] == "Develop software."
        assert item["date_posted"] == today
        assert item["date_extracted"] == today
        assert item["was_opened"] is True
        assert item["url"] == "https://example.com/job/123"
        assert item["salary"] == "$100k"
