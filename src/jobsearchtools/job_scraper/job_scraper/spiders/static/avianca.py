"""Avianca job listings spider."""

import hashlib
import re
from datetime import datetime

import scrapy

from ...items import JobScraperItem


class AviancaSpider(scrapy.Spider):
    """Spider for scraping job listings from Avianca careers page."""

    name = "avianca"
    allowed_domains = ["jobs.avianca.com"]
    start_urls = [
        "https://jobs.avianca.com/search/?createNewAlert=false&q=&locationsearch=Co"
    ]

    # Spanish to English month mapping (class-level to avoid recreation)
    SPANISH_MONTHS = {
        "ene": "Jan",
        "feb": "Feb",
        "mar": "Mar",
        "abr": "Apr",
        "may": "May",
        "jun": "Jun",
        "jul": "Jul",
        "ago": "Aug",
        "sep": "Sep",
        "oct": "Oct",
        "nov": "Nov",
        "dic": "Dec",
    }

    def parse(self, response):
        """
        Parse job listings from Avianca careers page.

        Args:
            response: Scrapy response object

        Yields:
            Request: For detail pages or JobScraperItem
        """
        self.logger.info(f"Parsing Avianca jobs from {response.url}")

        jobs = response.css("tr.data-row")
        self.logger.info(f"Found {len(jobs)} job listings")

        for job in jobs:
            item = JobScraperItem()
            item["company"] = "Avianca"

            # Extract title
            title = job.css("a.jobTitle-link::text").get()
            if title:
                item["title"] = title.strip()
            else:
                self.logger.warning("Missing title, skipping job")
                continue

            # Extract and parse location
            locations = job.css(".jobLocation::text").getall()
            # Filter out empty strings and take the last non-empty one
            clean_locations = [loc.strip() for loc in locations if loc.strip()]
            item["location"] = clean_locations[-1] if clean_locations else None

            # Parse date with Spanish month names
            date_str = job.css("span.jobDate::text").get()
            if date_str:
                date_str = date_str.strip()
                try:
                    # Parse Spanish dates: "31 oct 2025"
                    for es_month, en_month in self.SPANISH_MONTHS.items():
                        date_str = date_str.replace(es_month, en_month)

                    parsed_date = datetime.strptime(date_str, "%d %b %Y")
                    item["date_posted"] = parsed_date.date().isoformat()
                except ValueError as e:
                    # Fallback: keep original string if parsing fails
                    self.logger.warning(f"Could not parse date '{date_str}': {e}")
                    item["date_posted"] = date_str
            else:
                item["date_posted"] = None

            # Extract job URL and ID
            job_url = job.css("a.jobTitle-link::attr(href)").get()
            if not job_url:
                self.logger.warning("Missing job URL, skipping")
                continue

            item["url"] = response.urljoin(job_url)

            # Extract numeric job ID from URL pattern: /job/.../1263795901/
            job_id_match = re.search(r"/(\d+)/?$", job_url)
            if job_id_match:
                item["job_id"] = f"avianca_{job_id_match.group(1)}"
            else:
                # Fallback: use hash if pattern doesn't match
                job_hash = hashlib.sha256(job_url.encode()).hexdigest()[:10]
                item["job_id"] = f"avianca_{job_hash}"
                self.logger.warning(
                    f"Could not extract ID from URL {job_url}, using hash"
                )

            item["date_extracted"] = datetime.now().isoformat()
            item["salary"] = None

            # Follow to detail page to get description
            yield response.follow(
                job_url,
                callback=self.parse_detail,
                cb_kwargs={"item": item},
                errback=self.errback_detail,
                meta={"item": item},
            )

        # Check for pagination (next page)
        next_page = response.css(
            'a.paginationItemStyle:contains("›"), a.next, link[rel="next"]::attr(href)'
        ).get()

        if next_page:
            self.logger.info(f"Following pagination: {next_page}")
            yield response.follow(next_page, callback=self.parse)
        else:
            self.logger.info("No pagination found, finished parsing")

    def parse_detail(self, response, item):
        """
        Parse job detail page for description.

        Args:
            response: Scrapy response object
            item: Partially populated JobScraperItem

        Yields:
            JobScraperItem: Completed job item with description
        """
        try:
            # Extract job description from various possible selectors
            desc = response.css(
                ".jobdescription, #jobdescription, .job-description, "
                "div[itemprop='description']"
            ).get()

            if desc:
                item["description"] = desc.strip()
            else:
                # Fallback: try to get text from main content area
                desc_text = response.css(
                    ".joqReqDescription, .jdp-job-description-card"
                ).get()
                item["description"] = desc_text.strip() if desc_text else None

            # Mark as opened since we visited the detail page
            item["was_opened"] = True

            yield item
        except Exception as e:
            self.logger.error(f"Error parsing detail page {response.url}: {e}")
            # Yield item anyway without description
            item["description"] = None
            item["was_opened"] = False
            yield item

    def errback_detail(self, failure):
        """
        Handle errors when fetching detail pages.

        Args:
            failure: Twisted failure object
        """
        self.logger.error(f"Detail page request failed: {failure.value}")
        # Yield the item without description
        item = failure.request.meta.get("item")
        if item:
            item["description"] = None
            item["was_opened"] = False
            yield item
