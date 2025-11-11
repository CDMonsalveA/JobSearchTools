"""Citi job listings spider."""

from datetime import datetime

import scrapy

from ...items import JobScraperItem


class CitiSpider(scrapy.Spider):
    """Spider for scraping job listings from Citi careers page."""

    name = "citi"
    allowed_domains = ["jobs.citi.com"]
    start_urls = [
        "https://jobs.citi.com/location/bogota-jobs/287/3686110-3688685-3688689/4"
    ]

    def parse(self, response):
        """
        Parse job listings from Citi careers page.

        Args:
            response: Scrapy response object

        Yields:
            JobScraperItem: Job listing data
        """
        self.logger.info(f"Parsing Citi jobs from {response.url}")

        job_listings = response.css("section#search-results-list ul li")
        for job in job_listings:
            item = JobScraperItem()
            item["company"] = "Citi"
            item["title"] = job.xpath(".//h3/text()").get()
            item["location"] = job.xpath('.//span[@class="job-location"]/text()').get()
            item["date_posted"] = None  # Date not available in listing

            job_id = job.xpath(".//@data-job-id").get()
            item["job_id"] = f"citi_{job_id}" if job_id else None

            job_url = job.xpath(".//@href").get()
            item["url"] = response.urljoin(job_url) if job_url else None

            item["date_extracted"] = datetime.now().isoformat()
            item["salary"] = None
            item["description"] = None
            item["was_opened"] = False

            yield item

        # Follow pagination
        next_page = response.css("a.next::attr(href)").get()
        if next_page:
            yield response.follow(next_page, self.parse)

        self.logger.info("Finished parsing Citi jobs")
