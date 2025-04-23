# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class JobBoardsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    company = scrapy.Field()
    title = scrapy.Field()
    location = scrapy.Field()
    date = scrapy.Field()
    jobID = scrapy.Field()
    url = scrapy.Field()
