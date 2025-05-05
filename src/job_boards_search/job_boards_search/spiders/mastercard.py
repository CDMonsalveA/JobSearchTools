import json

import jmespath
import scrapy

from ..items import JobBoardsItem


class MastercardSpider(scrapy.Spider):
    name = "mastercard"
    allowed_domains = ["careers.mastercard.com"]
    start_urls = [
        "https://careers.mastercard.com/us/en/bogota-colombia",
        "https://careers.mastercard.com/us/en/bogota-colombia?from=5&s=1&rk=l-bogota-colombia",
        "https://careers.mastercard.com/us/en/bogota-colombia?from=10&s=1&rk=l-bogota-colombia",
        "https://careers.mastercard.com/us/en/bogota-colombia?from=15&s=1&rk=l-bogota-colombia",
        "https://careers.mastercard.com/us/en/bogota-colombia?from=20&s=1&rk=l-bogota-colombia",
        "https://careers.mastercard.com/us/en/bogota-colombia?from=25&s=1&rk=l-bogota-colombia",
        "https://careers.mastercard.com/us/en/bogota-colombia?from=30&s=1&rk=l-bogota-colombia",
        "https://careers.mastercard.com/us/en/bogota-colombia?from=35&s=1&rk=l-bogota-colombia",
        "https://careers.mastercard.com/us/en/bogota-colombia?from=40&s=1&rk=l-bogota-colombia",
        "https://careers.mastercard.com/us/en/bogota-colombia?from=45&s=1&rk=l-bogota-colombia",
        "https://careers.mastercard.com/us/en/bogota-colombia?from=50&s=1&rk=l-bogota-colombia",
        "https://careers.mastercard.com/us/en/bogota-colombia?from=55&s=1&rk=l-bogota-colombia",
        "https://careers.mastercard.com/us/en/bogota-colombia?from=60&s=1&rk=l-bogota-colombia",
        "https://careers.mastercard.com/us/en/bogota-colombia?from=65&s=1&rk=l-bogota-colombia",
        "https://careers.mastercard.com/us/en/bogota-colombia?from=70&s=1&rk=l-bogota-colombia",
        "https://careers.mastercard.com/us/en/bogota-colombia?from=75&s=1&rk=l-bogota-colombia",
    ]

    def parse(self, response):
        data = response.css("script").re_first(
            r"phApp\.ddo\s*=\s*({.*?});", default=""
        )
        data = json.loads(data)
        jobs = jmespath.search("eagerLoadRefineSearch.data.jobs", data)
        for job in jobs:
            item = JobBoardsItem()
            item["company"] = "Mastercard"
            item["title"] = job["title"]
            item["location"] = job["city"]
            item["date"] = job["dateCreated"]
            item["jobID"] = job["jobId"]
            item["url"] = job["applyUrl"]
            yield item
