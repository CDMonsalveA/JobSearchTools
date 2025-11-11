"""Sura job listings spider."""

from datetime import datetime

import scrapy

from ...items import JobScraperItem


class SuraSpider(scrapy.Spider):
    """Spider for scraping job listings from Sura careers page."""

    name = "sura"
    allowed_domains = ["trabajaconnosotros.sura.com"]
    start_urls = ["https://trabajaconnosotros.sura.com/search/?q=&locationsearch="]

    def parse(self, response):
        """
        Parse job listings from Sura careers page.

        Args:
            response: Scrapy response object

        Yields:
            JobScraperItem: Job listing data
        """
        self.logger.info(f"Parsing Sura jobs from {response.url}")

        for job in response.css("tr.data-row"):
            item = JobScraperItem()
            item["company"] = "Sura"

            title = job.css("a.jobTitle-link::text").get()
            item["title"] = title.strip() if title else None

            # Get location - the second element contains the actual location
            locations = job.css(".jobLocation::text").getall()
            item["location"] = locations[1].strip() if len(locations) > 1 else None

            date = job.css("span.jobDate::text").get()
            item["date_posted"] = date.strip() if date else None

            # Generate job ID from URL
            job_url = job.css("a.jobTitle-link::attr(href)").get()
            if job_url:
                item["url"] = response.urljoin(job_url)
                item["job_id"] = f"sura_{job_url.split('/')[-1]}"
            else:
                continue

            item["date_extracted"] = datetime.now().isoformat()
            item["salary"] = None
            item["description"] = None
            item["was_opened"] = False

            yield item

        self.logger.info("Finished parsing Sura jobs")
