import scrapy

from ..items import JobBoardsItem


class CitiSpider(scrapy.Spider):
    name = "citi"
    allowed_domains = ["jobs.citi.com"]
    start_urls = [
        "https://jobs.citi.com/location/bogota-jobs/287/3686110-3688685-3688689/4"
    ]

    def parse(self, response):
        # Extract job listings from the response
        job_listings = response.css("section#search-results-list ul li")
        for job in job_listings:
            item = JobBoardsItem()
            item["company"] = "Citi"
            item["title"] = job.xpath(".//h3/text()").get()
            item["location"] = job.xpath(
                './/span[@class="job-location"]/text()'
            ).get()
            item["date"] = None  # Date is not available in the provided HTML
            item["jobID"] = job.xpath(".//@data-job-id").get()
            item["url"] = response.urljoin(job.xpath(".//@href").get())

            yield item
