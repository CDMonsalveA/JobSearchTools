import json

import jmespath
import scrapy

from ..items import JobBoardsItem


class BancolombiaSpider(scrapy.Spider):
    name = "bancolombia"
    allowed_domains = ["empleo.grupobancolombia.com/"]
    start_urls = [
        "https://empleo.grupobancolombia.com/search/?q=&q2=&alertId=&locationsearch=&title=&department=&location=COL%2C+CO&date="
    ]

    def parse(self, response):
        jobTitles = response.css(".jobTitle-link::text").getall()
        jobLinks = response.css(".jobTitle-link::attr(href)").getall()
        jobLocations = response.css(".jobLocation::text").getall()
        JobDates = response.css(".jobDate::text").getall()[2:]

        for i in range(len(jobTitles)):
            item = JobBoardsItem()
            item["company"] = "Bancolombia"
            item["title"] = jobTitles[i].strip()
            item["location"] = jobLocations[i].strip()
            item["date"] = JobDates[i].strip()
            item["url"] = "https://empleo.grupobancolombia.com" + jobLinks[i]

            yield item
