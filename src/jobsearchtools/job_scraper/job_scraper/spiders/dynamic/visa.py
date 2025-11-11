"""
Visa spider for scraping job listings from Visa careers page.

Visa uses dynamic JavaScript rendering, so this spider uses Playwright
to render the page before scraping.
"""

from datetime import datetime

import scrapy
from scrapy_playwright.page import PageMethod

from ...items import JobScraperItem


class VisaSpider(scrapy.Spider):
    """
    Spider for scraping Visa job listings in Bogotá, Colombia.

    Uses Playwright to handle JavaScript-rendered content.
    """

    name = "visa"
    allowed_domains = ["corporate.visa.com"]
    start_urls = [
        "https://corporate.visa.com/en/jobs/"
        "?cities=Bogot%C3%A1&sortProperty=createdOn&sortOrder=DESC"
    ]

    custom_settings = {
        "PLAYWRIGHT_BROWSER_TYPE": "firefox",
        "PLAYWRIGHT_LAUNCH_OPTIONS": {"headless": True},
        "DOWNLOAD_HANDLERS": {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
    }

    def start_requests(self):
        """
        Start requests with Playwright configuration.

        Yields:
            scrapy.Request with Playwright metadata.
        """
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
                    "playwright_page_methods": [
                        PageMethod("wait_for_selector", "li.vs-underline"),
                        PageMethod("wait_for_timeout", 2000),
                    ],
                    "errback": self.errback,
                },
                callback=self.parse,
            )

    async def parse(self, response):
        """
        Parse the main job listings page.

        Args:
            response: Scrapy response object with Playwright page.

        Yields:
            JobScraperItem for each job found.
        """
        page = response.meta["playwright_page"]
        content = await page.content()
        await page.close()

        # Create a new selector from the rendered content
        selector = scrapy.Selector(text=content)

        self.logger.info(
            f"User-Agent: {response.request.headers.get('User-Agent', 'N/A')}"
        )

        # Extract job listings
        jobs = selector.css("li.vs-underline")
        self.logger.info(f"Found {len(jobs)} job listings")

        for job in jobs:
            item = JobScraperItem()

            # Extract job details
            title = job.css("h2 a::text").get()
            job_id = job.css("p:contains('Job #')::text").re_first(r"Job #\s*(\S+)")
            location_text = job.css("p:contains('Location')::text").get()
            location = (
                location_text.replace("Location", "").strip()
                if location_text
                else "Bogotá, Colombia"
            )
            url = job.css("h2 a::attr(href)").get()

            # Construct full job_id
            item["job_id"] = f"visa_{job_id}" if job_id else None
            item["title"] = title
            item["company"] = "Visa"
            item["location"] = location
            item["description"] = None  # Will be filled from detail page if needed
            item["salary"] = None
            item["url"] = url
            item["date_posted"] = None  # Visa doesn't show posting date on listings
            item["date_extracted"] = datetime.utcnow().isoformat()
            item["was_opened"] = False

            if item["job_id"] and item["url"]:
                # Could follow to detail page for description if needed
                # For now, yield the item directly
                yield item
            else:
                self.logger.warning(f"Skipping job with missing data: {title}")

    async def errback(self, failure):
        """
        Handle request failures.

        Args:
            failure: Twisted failure object.
        """
        page = failure.request.meta.get("playwright_page")
        if page:
            await page.close()
        self.logger.error(f"Request failed: {failure.request.url}")
        self.logger.error(f"Error: {failure.value}")
