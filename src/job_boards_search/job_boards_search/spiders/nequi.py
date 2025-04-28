import scrapy
import json

from ..items import JobBoardsItem
# Inside every job detail page
# <script type="application/ld+json" nonce="">
#     {"@context":"https://schema.org/","@type":"JobPosting","title":"TITLE","description":"DESCRIPTION","identifier":{"@type":"PropertyValue","name":"NEQUI SA COMPANIA DE FINANCIAMIENTO"},"datePosted":"2025-03-05 13:51:41 -0300","employmentType":"CONTRACTOR","hiringOrganization":{"@type":"Organization","name":"NEQUI SA COMPANIA DE FINANCIAMIENTO","sameAs":"lapipolnequi.buk.co","logo":"https://bukwebapp-enterprise-colombia.s3.amazonaws.com/a6cacefb-60e3-4cc1-a7b5-9411a291caee/recruiting/company/logo_url/1/d4dc3a12-2af2-46a7-9c3d-ea1e2c4cd49d-Logo_Nequi.png"},"jobLocation":{"@type":"Place","address":{"@type":"PostalAddress","streetAddress":"","addressLocality":"Medellín, Antioquia","addressRegion":"Antioquia","postalCode":"","addressCountry":"CO"}},"baseSalary":{"@type":"MonetaryAmount","currency":"COP","value":{"@type":"QuantitativeValue","minValue":"2135250","maxValue":"2135250","unitText":"MONTH"}}}
# </script>


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
        json_ld = response.xpath('//script[@type="application/ld+json"]/text()').get()
        if json_ld:
            data = json.loads(json_ld)
            job_item = JobBoardsItem()
            job_item["company"] = data["hiringOrganization"]["name"]
            job_item["title"] = data["title"]
            job_item["location"] = data["jobLocation"]["address"]["addressLocality"]
            job_item["date"] = data["datePosted"]
            job_item["jobID"] = data["identifier"]["name"]
            job_item["url"] = response.url
            yield job_item
            