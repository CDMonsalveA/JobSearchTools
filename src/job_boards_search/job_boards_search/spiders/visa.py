import scrapy


class VisaSpider(scrapy.Spider):
    name = "visa"
    allowed_domains = ["corporate.visa.com"]
    start_urls = ["https://corporate.visa.com/en/jobs/?cities=Bogot%C3%A1&sortProperty=createdOn&sortOrder=DESC"]

    def parse(self, response):
        pass
