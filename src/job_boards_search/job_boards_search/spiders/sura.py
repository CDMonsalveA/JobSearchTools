import scrapy
from ..items import JobBoardsItem

class SuraSpider(scrapy.Spider):
    name = "sura"
    allowed_domains = ["trabajaconnosotros.sura.com"]
    start_urls = ["https://trabajaconnosotros.sura.com/search/?q=&locationsearch=#innershell"]

    def parse(self, response):
        """
        company: str = "Sura"
        title: a.jobTitle-link::text .get().strip()
        location: span.jobLocation::text .getall()[1].strip()
        date: span.jobDate::text .get().strip()
        JobID: None
        url: response.urljoin(job.css("a.jobTitle-link::attr(href)").get())
        """
        for job in response.css("tr.data-row")[:5]:
            item = JobBoardsItem()
            item["company"] = "Sura"
            item["title"] = job.css("a.jobTitle-link::text").get().strip()
            item["location"] = job.css(".jobLocation::text").getall()[1].strip()
            item["date"] = job.css("span.jobDate::text").get().strip()
            item["jobID"] = None
            item["url"] = response.urljoin(job.css("a.jobTitle-link::attr(href)").get())
            yield item
        pass
