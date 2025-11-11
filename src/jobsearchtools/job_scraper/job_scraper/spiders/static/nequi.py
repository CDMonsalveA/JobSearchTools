"""Nequi job listings spider."""

import json
from datetime import datetime

import scrapy

from ...items import JobScraperItem


class NequiSpider(scrapy.Spider):
    """Spider for scraping job listings from Nequi careers page."""

    name = "nequi"
    allowed_domains = ["lapipolnequi.buk.co"]
    start_urls = ["https://lapipolnequi.buk.co/trabaja-con-nosotros"]

    def parse(self, response):
        """
        Parse job listing links from Nequi careers main page.

        Args:
            response: Scrapy response object

        Yields:
            Request: Follow request to job detail pages
        """
        self.logger.info(f"Parsing Nequi jobs from {response.url}")

        job_links = response.css(
            "a.btn.btn-secondary.btn-md.btn-auto-responsive.text-capitalize::attr(href)"
        ).getall()

        for link in job_links:
            yield response.follow(link, callback=self.parse_job_details)

    def parse_job_details(self, response):
        """
        Parse job details from individual job pages.

        Args:
            response: Scrapy response object

        Yields:
            JobScraperItem: Job listing data
        """
        # Extract job details from JSON-LD structured data
        json_ld = response.xpath('//script[@type="application/ld+json"]/text()').get()

        if json_ld:
            try:
                data = json.loads(json_ld)

                item = JobScraperItem()
                item["company"] = data.get("hiringOrganization", {}).get(
                    "name", "Nequi"
                )
                item["title"] = data.get("title")
                item["location"] = (
                    data.get("jobLocation", {})
                    .get("address", {})
                    .get("addressLocality")
                )
                item["date_posted"] = data.get("datePosted")
                item["job_id"] = f"nequi_{data.get('identifier', {}).get('name', '')}"
                item["url"] = response.url

                item["date_extracted"] = datetime.now().isoformat()
                item["salary"] = None
                item["description"] = data.get("description")
                item["was_opened"] = True  # We visited the detail page

                yield item

            except json.JSONDecodeError:
                self.logger.error(f"Failed to parse JSON-LD from {response.url}")

        self.logger.debug(f"Finished parsing Nequi job at {response.url}")
