import scrapy

from ..items import JobBoardsItem


class EcopetrolSpider(scrapy.Spider):
    name = "ecopetrol"
    allowed_domains = ["jobs.ecopetrol.com.co"]
    start_urls = [
        "https://jobs.ecopetrol.com.co/search/?createNewAlert=false&q=&locationsearch=Colombia"
    ]

    def parse(self, response):
        jobTitles = response.css(".jobTitle-link::text").getall()
        jobLinks = response.css(".jobTitle-link::attr(href)").getall()
        jobIds = response.css("div[data-focus-tile]::attr(id)").getall()
        jobIds = [f"{jobId.split('-')[0]}-{jobId.split('-')[1]}" for jobId in jobIds]
        jobIds = list(set(jobIds))  # Remove duplicates
        # id="job-1282171600-desktop-section-location-value" ::text
        jobLocations = [
            response.css(f"#{jobId}-desktop-section-location-value::text").get()
            for jobId in jobIds
        ]
        # id="job-1282171600-desktop-section-date-value"
        jobDates = [
            response.css(f"#{jobId}-desktop-section-date-value::text").get()
            for jobId in jobIds
        ]
        self.logger.info(f"jobTitles: {jobTitles}")
        self.logger.info(f"jobLinks: {jobLinks}")
        self.logger.info(f"jobIds: {jobIds}")
        self.logger.info(f"jobLocations: {jobLocations}")
        self.logger.info(f"jobDates: {jobDates}")

        for i in range(len(jobTitles)):
            item = JobBoardsItem()
            item["company"] = "Ecopetrol"
            item["title"] = jobTitles[i].strip()
            item["location"] = jobLocations[i].strip()
            item["date"] = jobDates[i].strip()
            item["jobID"] = jobIds[i]
            item["url"] = "https://jobs.ecopetrol.com.co" + jobLinks[i]

            yield item
