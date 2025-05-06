import scrapy

from job_boards_search.items import JobBoardsItem

class ScotiabankSpider(scrapy.Spider):
    name = "scotiabank"
    allowed_domains = ["jobs.scotiabank.com"]
    start_urls = ["https://jobs.scotiabank.com/search/?q=&locationsearch=CO&sortColumn=referencedate&sortDirection=desc#hdrDateButton"]

    def parse(self, response):
        search_results = response.css(".searchResults")
        jobs = search_results.css(".data-row")
        for job in jobs[:5]:
            item = JobBoardsItem()
            item["company"] = "Scotiabank"
            item["title"] = job.css("a.jobTitle-link::text").get().strip()
            item["location"] = job.css("span.jobLocation::text").get().strip()
            item["date"] = job.css("span.jobDate::text").get().strip()
            item["jobID"] = job.css("a.jobTitle-link::attr(href)").get().split("/")[-1]
            item["url"] = 'https://jobs.scotiabank.com' + job.css("a.jobTitle-link::attr(href)").get()
            yield item
