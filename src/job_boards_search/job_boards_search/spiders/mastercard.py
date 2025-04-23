import json

import jmespath
import scrapy

from ..items import JobBoardsItem


class MastercardSpider(scrapy.Spider):
    name = "mastercard"
    allowed_domains = ["careers.mastercard.com"]
    start_urls = ["https://careers.mastercard.com/us/en/bogota-colombia"]

    def parse(self, response):
        data = response.css("script").re_first(r"phApp\.ddo\s*=\s*({.*?});", default="")
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
