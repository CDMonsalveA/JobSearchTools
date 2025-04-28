import json

import scrapy

from ..items import JobBoardsItem


class NequiSpider(scrapy.Spider):
    name = "nequi"
    allowed_domains = ["lapipolnequi.buk.co"]
    start_urls = ["https://lapipolnequi.buk.co/trabaja-con-nosotros"]

    def parse(self, response):
        # Extract job links from the main page
        job_links = response.css(
            "a.btn.btn-secondary.btn-md.btn-auto-responsive.text-capitalize::attr(href)"
        ).getall()
        for link in job_links:
            yield response.follow(link, callback=self.parse_job_details)

    def parse_job_details(self, response):
        # Extract job details from the JSON-LD script tag
        json_ld = response.xpath(
            '//script[@type="application/ld+json"]/text()'
        ).get()
        if json_ld:
            data = json.loads(json_ld)
            job_item = JobBoardsItem()
            job_item["company"] = data["hiringOrganization"]["name"]
            job_item["title"] = data["title"]
            job_item["location"] = data["jobLocation"]["address"][
                "addressLocality"
            ]
            job_item["date"] = data["datePosted"]
            job_item["jobID"] = data["identifier"]["name"]
            job_item["url"] = response.url
            yield job_item
