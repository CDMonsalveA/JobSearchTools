"""Ecopetrol job listings spider."""

from datetime import datetime

import scrapy

from ...items import JobScraperItem


class EcopetrolSpider(scrapy.Spider):
    """Spider for scraping job listings from Ecopetrol careers page."""

    name = "ecopetrol"
    allowed_domains = ["jobs.ecopetrol.com.co"]
    start_urls = [
        "https://jobs.ecopetrol.com.co/search/?createNewAlert=false&q=&locationsearch=Colombia"
    ]

    def parse(self, response):
        """
        Parse job listings from Ecopetrol careers page.

        Args:
            response: Scrapy response object

        Yields:
            JobScraperItem: Job listing data
        """
        self.logger.info(f"Parsing Ecopetrol jobs from {response.url}")

        job_titles = response.css(".jobTitle-link::text").getall()
        job_links = response.css(".jobTitle-link::attr(href)").getall()
        job_ids = response.css("div[data-focus-tile]::attr(id)").getall()

        # Extract job ID prefix (first two parts)
        job_ids = [
            f"{job_id.split('-')[0]}-{job_id.split('-')[1]}" for job_id in job_ids
        ]
        job_ids = list(dict.fromkeys(job_ids))  # Remove duplicates preserving order

        # Get locations and dates using job IDs
        job_locations = [
            response.css(f"#{job_id}-desktop-section-location-value::text").get()
            for job_id in job_ids
        ]
        job_dates = [
            response.css(f"#{job_id}-desktop-section-date-value::text").get()
            for job_id in job_ids
        ]

        for title, link, job_id, location, date in zip(
            job_titles, job_links, job_ids, job_locations, job_dates, strict=False
        ):
            item = JobScraperItem()
            item["company"] = "Ecopetrol"
            item["title"] = title.strip() if title else None
            item["location"] = location.strip() if location else None
            item["date_posted"] = date.strip() if date else None
            item["job_id"] = f"ecopetrol_{job_id}"
            item["url"] = f"https://jobs.ecopetrol.com.co{link}"

            item["date_extracted"] = datetime.now().isoformat()
            item["salary"] = None
            item["description"] = None
            item["was_opened"] = False

            yield item

        self.logger.info(f"Finished parsing {len(job_titles)} Ecopetrol jobs")
