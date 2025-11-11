"""BBVA job listings spider (dynamic with Playwright)."""

from datetime import datetime

import scrapy
from scrapy_playwright.page import PageMethod

from ...items import JobScraperItem


class BbvaSpider(scrapy.Spider):
    """Spider for scraping job listings from BBVA careers page using Playwright."""

    name = "bbva"
    allowed_domains = ["bbva.wd3.myworkdayjobs.com"]
    start_urls = [
        "https://bbva.wd3.myworkdayjobs.com/es/BBVA?locationCountry=e8106cd6a3534f2dba6fdee2d41db89d"
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
        Start requests with Playwright enabled.

        Yields:
            Request: Scrapy request with Playwright meta
        """
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
                    "playwright_page_methods": [
                        PageMethod("wait_for_selector", "nav[aria-label='pagination']"),
                        PageMethod(
                            "evaluate",
                            "window.scrollTo(0, document.body.scrollHeight)",
                        ),
                        PageMethod("wait_for_timeout", 2000),
                    ],
                    "errback": self.errback,
                },
                callback=self.parse,
            )

    async def parse(self, response):
        """
        Parse job listings from BBVA careers page.

        Args:
            response: Scrapy response object with Playwright page

        Yields:
            JobScraperItem: Job listing data
        """
        page = response.meta["playwright_page"]
        content = await page.content()
        await page.close()

        # Parse the HTML content
        selector = scrapy.Selector(text=content)
        jobs = selector.css("li.css-1q2dra3")

        self.logger.info(f"Found {len(jobs)} BBVA jobs")

        for job in jobs:
            item = JobScraperItem()
            item["company"] = "BBVA"
            item["title"] = job.css("a::text").get()
            item["location"] = job.css(
                "div[data-automation-id='locations'] dd::text"
            ).get()
            item["date_posted"] = job.css(
                "div[data-automation-id='postedOn'] dd::text"
            ).get()

            job_id = job.css("ul[data-automation-id='subtitle'] li::text").get()
            item["job_id"] = f"bbva_{job_id}" if job_id else None

            job_url = job.css("a::attr(href)").get()
            if job_url:
                item["url"] = f"https://bbva.wd3.myworkdayjobs.com{job_url}"
            else:
                item["url"] = None

            item["date_extracted"] = datetime.now().isoformat()
            item["salary"] = None
            item["description"] = None
            item["was_opened"] = False

            yield item

        self.logger.info(f"Finished parsing {len(jobs)} BBVA jobs")

    async def errback(self, failure):
        """
        Handle request failures and close Playwright page.

        Args:
            failure: Twisted failure object
        """
        page = failure.request.meta.get("playwright_page")
        if page:
            await page.close()
        self.logger.error(f"Request failed: {failure}")
