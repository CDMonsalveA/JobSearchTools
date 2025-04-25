from collections.abc import Iterable

import scrapy
from scrapy_playwright.page import PageMethod
from playwright.sync_api import Page

from ..items import JobBoardsItem

"""
Example of the html structure of the page:
<li class="vs-underline vs-pt-4 vs-pb-4 vs-m-0"><vs-listing><h2 class="vs-h4 vs-mb-0"><a target="_blank" rel="noopener noreferrer" class="vs-h3 vs-link-job vs-link-new-window" href="https://corporate.visa.com/en/jobs/REF060729W" aria-label="Finance Manager (Open in a new window)"> Finance Manager </a></h2><div class="vs-listing-description"><p class="vs-text vs-m-0 vs-d-lg-inline vs-pr-1"><span class="vs-bold">Location </span> Bogotá, COLOMBIA </p><p class="vs-text vs-m-0 vs-d-lg-inline vs-pr-1"><span class="vs-bold">Job # </span> REF060729W </p><p class="vs-text vs-m-0 vs-d-lg-inline vs-pr-1"><span class="vs-bold">Team </span> Finance </p><!----></div><!----><!----></vs-listing></li>
"""


class VisaSpider(scrapy.Spider):
    """Visa is loaded dinamically, so this spider uses playwright."""

    name = "visa"
    allowed_domains = ["corporate.visa.com"]
    start_urls = [
        "https://corporate.visa.com/en/jobs/?cities=Bogot%C3%A1&sortProperty=createdOn&sortOrder=DESC"
    ]

    custom_settings = {
        "PLAYWRIGHT_BROWSER_TYPE": "firefox",
        "PLAYWRIGHT_LAUNCH_OPTIONS": {"headless": True},
        "PLAYWRIGHT_BROWSER_LAUNCH_OPTIONS": {"headless": True},
        "DOWNLOAD_HANDLERS": {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        "LOG_LEVEL": "INFO",
        "LOG_FORMAT": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    }

    def start_requests(self):
        """Start the requests using playwright."""
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
                    'errback': self.errback,
                },
                callback=self.parse,
            )

    async def parse(self, response):
        """Parse the response."""
        page = response.meta["playwright_page"]
        content = await page.content()
        await page.close()
        response = scrapy.Selector(text=content)

        # Extract jobs
        jobs = response.css("li.vs-underline")
        for job in jobs[:5]:
            item = JobBoardsItem() # company, title, location, date, jobID, url
            item["company"] = "Visa"
            item["title"] = job.css("h2 a::text").get()
            item["location"] = job.css("p span:contains('Location') + span::text").get()
            item["date"] = 'N/A'
            item["jobID"] = job.css("p span:contains('Job #') + span::text").get()
            item["url"] = job.css("h2 a::attr(href)").get()

            yield item

    async def errback(self, failure):
        """Handle errors."""
        page = failure.request.meta["playwright_page"]
        await page.close()

                    