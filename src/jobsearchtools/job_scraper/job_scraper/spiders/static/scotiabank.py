"""Scotiabank job listings spider."""

from datetime import datetime

import scrapy

from ...items import JobScraperItem


class ScotiabankSpider(scrapy.Spider):
    """Spider for scraping job listings from Scotiabank careers page."""

    name = "scotiabank"
    allowed_domains = ["jobs.scotiabank.com"]
    start_urls = [
        "https://jobs.scotiabank.com/search/?q=&locationsearch=CO&sortColumn=referencedate&sortDirection=desc"
    ]

    def parse(self, response):
        """
        Parse job listings from Scotiabank careers page.

        Args:
            response: Scrapy response object

        Yields:
            JobScraperItem: Job listing data
        """
        self.logger.info(f"Parsing Scotiabank jobs from {response.url}")

        search_results = response.css(".searchResults")
        jobs = search_results.css(".data-row")

        for job in jobs:
            item = JobScraperItem()
            item["company"] = "Scotiabank"

            title = job.css("a.jobTitle-link::text").get()
            item["title"] = title.strip() if title else None

            location = job.css("span.jobLocation::text").get()
            item["location"] = location.strip() if location else None

            date = job.css("span.jobDate::text").get()
            item["date_posted"] = date.strip() if date else None

            job_url = job.css("a.jobTitle-link::attr(href)").get()
            if job_url:
                item["url"] = f"https://jobs.scotiabank.com{job_url}"
                item["job_id"] = f"scotiabank_{job_url.split('/')[-1]}"
            else:
                continue

            item["date_extracted"] = datetime.now().isoformat()
            item["salary"] = None
            item["description"] = None
            item["was_opened"] = False

            yield item

        self.logger.info("Finished parsing Scotiabank jobs")
