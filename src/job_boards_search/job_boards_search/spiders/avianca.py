import scrapy

from ..items import JobBoardsItem

class AviancaSpider(scrapy.Spider):
    name = "avianca"
    allowed_domains = ["jobs.avianca.com"]
    start_urls = ["https://jobs.avianca.com/search/?createNewAlert=false&q=&locationsearch=Co"]

    def parse(self, response):
        """
        company: str = "Avianca"
        title: a.jobTitle-link::text
        location: span.jobLocation::text
        date: span.jobDate::text
        JobID: None
        url: jobs.avianca.com + a.jobTitle-link::attr(href)
        """
        for job in response.css("tr.data-row")[:5]:
            item = JobBoardsItem()
            item["company"] = "Avianca"
            item["title"] = job.css("a.jobTitle-link::text").get()
            item["location"] = job.css(".jobLocation::text").getall()[1].strip()
            item["date"] = job.css("span.jobDate::text").get().strip()
            item["jobID"] = None
            item["url"] = response.urljoin(job.css("a.jobTitle-link::attr(href)").get())
            yield item
