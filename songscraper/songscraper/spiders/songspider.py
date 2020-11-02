# -*- coding: utf-8 -*-
import scrapy


class SongspiderSpider(scrapy.Spider):
    name = 'songspider'
    allowed_domains = ['billboard.com']
    start_urls = ['http://billboard.com/']

    def parse(self, response):
        pass
