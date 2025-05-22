from collections.abc import Iterable

import scrapy
from job_boards_search.items import JobBoardsItem
from scrapy_playwright.page import PageMethod

# <li class="css-1q2dra3"><div class="css-qiqmbt"><div class="css-b3pn3b"><div class="css-b3pn3b"><h3><a aria-current="false" data-automation-id="jobTitle" data-uxi-element-id="jobItem" data-uxi-query-id="" data-uxi-widget-type="heading" data-uxi-item-rank="0" class="css-19uc56f" href="/es/BBVA/job/SING---DIR-GENERAL-PISO-4/ANALYST-I---GRM-DATA---ANALYTICS---CoE---RIESGOS_JR00068618-1?locationCountry=e8106cd6a3534f2dba6fdee2d41db89d">ANALYST I - GRM DATA &amp; ANALYTICS - CoE - RIESGOS</a></h3></div></div></div><div class="css-248241"><div class="css-1y87fhn"><div data-automation-id="remoteType" class="css-k008qs"><div aria-hidden="true" class="css-kij4qr"><span class="css-wwkk48"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" class="wd-icon-globe wd-icon" focusable="false" role="presentation" viewBox="0 0 24 24"><g fill-rule="evenodd" class="wd-icon-container"><path fill-rule="nonzero" d="M12 2c5.523 0 10 4.477 10 10s-4.477 10-10 10S2 17.523 2 12 6.477 2 12 2zm-1 13H8.314c.503 2.316 1.55 4.046 2.686 4.706V15zm4.686 0H13v4.706c1.136-.661 2.183-2.39 2.686-4.705zm-9.411.001H4.582A8.028 8.028 0 0 0 7.5 18.615c-.548-1.035-.97-2.263-1.225-3.614zm13.143 0h-1.693c-.255 1.351-.677 2.579-1.226 3.615a8.03 8.03 0 0 0 2.92-3.615zm-13.298-5H4.252a8.015 8.015 0 0 0-.19 3H6.03a16.82 16.82 0 0 1 .09-3zM11 10H8.136a14.565 14.565 0 0 0-.102 3.001L11 13v-3zm4.864 0H13v3l2.966.001a14.878 14.878 0 0 0-.102-3zm3.884 0H17.88a16.557 16.557 0 0 1 .09 3l1.968.001a8.079 8.079 0 0 0-.19-3zM7.501 5.385l-.188.132A8.04 8.04 0 0 0 5.07 8H6.5c.25-.96.59-1.842 1-2.616zM8.575 8H11V4.294C10.035 4.855 9.133 6.189 8.575 8zM13 4.294L13 8h2.425c-.557-1.81-1.459-3.144-2.424-3.706zm3.499 1.09l.089.173c.37.732.679 1.554.912 2.443h1.429a8.04 8.04 0 0 0-2.43-2.615z" class="wd-icon-fill"></path></g></svg></span></div><dl><dt class="css-y8qsrx">remote type</dt><dd class="css-129m7dg">Hybrid</dd></dl></div></div><div class="css-1y87fhn"><div data-automation-id="locations" class="css-k008qs"><div aria-hidden="true" class="css-kij4qr"><span class="css-wwkk48"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" class="wd-icon-location wd-icon" focusable="false" role="presentation" viewBox="0 0 24 24"><g fill-rule="evenodd" class="wd-icon-container"><path d="M12 2a8 8 0 0 1 8 8c0 4.418-7.635 11.645-7.635 11.645a.52.52 0 0 1-.72.01l-.025-.024c-.05-.049-.175-.169-.358-.35l-.2-.2C9.273 19.283 4 13.669 4 10a8 8 0 0 1 8-8zm0 5a3 3 0 1 0 0 6 3 3 0 0 0 0-6z" class="wd-icon-background"></path><path fill-rule="nonzero" d="M12 2a8 8 0 0 1 8 8c0 4.418-7.635 11.645-7.635 11.645a.52.52 0 0 1-.72.01l-.025-.024c-.05-.049-.175-.169-.358-.35l-.2-.2C9.273 19.283 4 13.669 4 10a8 8 0 0 1 8-8zm0 2a6 6 0 0 0-6 6c0 .72.404 1.818 1.186 3.14.572.964 1.316 2.005 2.192 3.086A45.646 45.646 0 0 0 12 19.181l.114-.118a45.53 45.53 0 0 0 2.514-2.842c.875-1.082 1.62-2.124 2.191-3.09C17.6 11.814 18 10.72 18 10a6 6 0 0 0-6-6zm0 8a2 2 0 1 0 0-4 2 2 0 0 0 0 4zm0 2a4 4 0 1 1 0-8 4 4 0 0 1 0 8z" class="wd-icon-fill"></path></g></svg></span></div><dl><dt class="css-y8qsrx">locations</dt><dd class="css-129m7dg">SING - DIR GENERAL PISO 4</dd></dl></div></div></div><div class="css-zoser8"><div class="css-1y87fhn"><div data-automation-id="postedOn" class="css-k008qs"><div aria-hidden="true" class="css-kij4qr"><span class="css-wwkk48"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" class="wd-icon-clock wd-icon" focusable="false" role="presentation" viewBox="0 0 24 24"><g fill-rule="evenodd" class="wd-icon-container"><circle cx="12" cy="12" r="9" class="wd-icon-background"></circle><path d="M12 2c5.523 0 10 4.477 10 10s-4.477 10-10 10S2 17.523 2 12 6.477 2 12 2zm0 2a8 8 0 1 0 0 16 8 8 0 0 0 0-16z" class="wd-icon-fill"></path><path d="M10.503 14a.497.497 0 0 1-.503-.505V7.503c0-.278.214-.503.505-.503h.99c.279 0 .505.233.505.503V12h4.497c.278 0 .503.214.503.505v.99a.509.509 0 0 1-.503.505h-5.994z" class="wd-icon-accent"></path></g></svg></span></div><dl><dt class="css-y8qsrx">posted on</dt><dd class="css-129m7dg">Publicado hace 3 días</dd></dl></div></div></div><div class="css-zoser8"><div class="css-1y87fhn"><div data-automation-id="timeLeftToApply" class="css-k008qs"><div aria-hidden="true" class="css-kij4qr"><span class="css-wwkk48"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" class="wd-icon-calendar wd-icon" focusable="false" role="presentation" viewBox="0 0 24 24"><g fill-rule="evenodd" class="wd-icon-container"><path d="M4 5h16v4H4z" class="wd-icon-background"></path><path d="M7.495 2c.279 0 .505.216.505.495V4h8V2.495c0-.273.214-.495.505-.495h.99c.279 0 .505.216.505.495V4h2.007c.548 0 .993.451.993.99v15.075c0 .47-.368.86-.854.925a.995.995 0 0 1-.14.01H3.994a1 1 0 0 1-.176-.016c-.465-.08-.817-.46-.817-.919V4.991C3 4.444 3.445 4 3.993 4H6V2.495C6 2.222 6.214 2 6.505 2zM19 10H5v9h14v-9zm-8.49 2c.27 0 .49.215.49.49v3.02c0 .27-.215.49-.49.49H7.49a.488.488 0 0 1-.49-.49v-3.02c0-.27.215-.49.49-.49h3.02zM19 6H5v2h14V6z" class="wd-icon-fill"></path></g></svg></span></div><dl><dt class="css-y8qsrx">end date and time left to apply</dt><dd class="css-129m7dg">Fecha final: 2 de mayo de 2025</dd></dl></div></div></div><ul data-automation-id="subtitle" class="css-14a0imc"><li class="css-h2nt8k">JR00068618</li></ul></li>


class BbvaSpider(scrapy.Spider):
    name = "bbva"
    allowed_domains = ["bbva.wd3.myworkdayjobs.com"]
    start_urls = ["https://bbva.wd3.myworkdayjobs.com/es/BBVA?locationCountry=e8106cd6a3534f2dba6fdee2d41db89d"]
    custom_settings = {
        "PLAYWRIGHT_BROWSER_TYPE": "firefox",
        "PLAYWRIGHT_LAUNCH_OPTIONS": {"headless": True},
        "PLAYWRIGHT_BROWSER_LAUNCH_OPTIONS": {"headless": True},
        "DOWNLOAD_HANDLERS": {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
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
        """Parse the response."""
        page = response.meta["playwright_page"]
        content = await page.content()
        await page.close()
        response = scrapy.Selector(text=content)

        # Extract jobs
        jobs = response.css("li.css-1q2dra3")
        self.logger.info(f"Found {len(jobs)} jobs")
        for job in jobs[:10]:
            item = JobBoardsItem()
            item["company"] = "BBVA"
            item["title"] = job.css("a::text").get()
            item["location"] = job.css("div[data-automation-id='locations'] dd::text").get()
            item["date"] = job.css("div[data-automation-id='postedOn'] dd::text").get()
            item["jobID"] = job.css("ul[data-automation-id='subtitle'] li::text").get()
            item["url"] = "https://bbva.wd3.myworkdayjobs.com" + job.css("a::attr(href)").get("")
            if item["location"] == "Publicado hoy":
                yield item

    async def errback(self, failure):
        """Handle errors."""
        page = failure.request.meta["playwright_page"]
        await page.close()
        self.logger.error(f"Request failed: {failure}")
        self.logger.error(f"Error: {failure.value}")
