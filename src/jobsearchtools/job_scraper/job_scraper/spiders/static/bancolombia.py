"""Bancolombia job listings spider."""

from datetime import datetime

import scrapy

from ...items import JobScraperItem


class BancolombiaSpider(scrapy.Spider):
    """Spider for scraping job listings from Bancolombia careers page."""

    name = "bancolombia"
    allowed_domains = ["empleo.grupobancolombia.com"]
    start_urls = [
        "https://empleo.grupobancolombia.com/search/?q=&q2=&alertId=&locationsearch=&title=&department=&location=COL%2C+CO&date="
    ]

    def parse(self, response):
        """
        Parse job listings from Bancolombia careers page.

        Args:
            response: Scrapy response object

        Yields:
            JobScraperItem: Job listing data
        """
        self.logger.info(f"Parsing Bancolombia jobs from {response.url}")

        job_titles = response.css(".jobTitle-link::text").getall()
        job_links = response.css(".jobTitle-link::attr(href)").getall()
        job_locations = response.css(".jobLocation::text").getall()
        job_dates = response.css(".jobDate::text").getall()[2:]  # Skip first 2

        for title, link, location, date in zip(
            job_titles, job_links, job_locations, job_dates, strict=False
        ):
            item = JobScraperItem()
            item["company"] = "Bancolombia"
            item["title"] = title.strip() if title else None
            item["location"] = location.strip() if location else None
            item["date_posted"] = date.strip() if date else None
            item["url"] = f"https://empleo.grupobancolombia.com{link}"

            # Generate job ID from URL
            item["job_id"] = f"bancolombia_{link.split('/')[-1]}"

            item["date_extracted"] = datetime.now().isoformat()
            item["salary"] = None
            item["description"] = None
            item["was_opened"] = False

            yield item

        self.logger.info(f"Finished parsing {len(job_titles)} Bancolombia jobs")
