# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class JobScraperItem(scrapy.Item):
    job_id = scrapy.Field()
    title = scrapy.Field()
    company = scrapy.Field()
    location = scrapy.Field()
    description = scrapy.Field()
    salary = scrapy.Field()
    url = scrapy.Field()
    date_posted = scrapy.Field()
    date_extracted = scrapy.Field()
    was_opened = scrapy.Field()
