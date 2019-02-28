# -*- coding: utf-8 -*-
import pymysql
import scrapy

from thepaperSpider.items import NewsUpdateItem


class UpdateSpider(scrapy.Spider):
    name = 'update'
    allowed_domains = ['thepaper.cn']
    start_urls = ['http://thepaper.cn/']
    newsIdList = []

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        self.connect = pymysql.connect(
            host='127.0.0.1',
            port=3306,
            db='quwen2',
            user='root',
            passwd='123456',
            charset='utf8',
            use_unicode=True
        )
        self.cursor = self.connect.cursor()

    def parse(self, response):
        sql = 'select newsid from news'
        result = self.cursor.execute(sql)
        newsTuple = self.cursor.fetchall()
        for news in newsTuple:
            newsId = news[0]
            item = NewsUpdateItem()
            item['newsId'] = newsId
            yield item
        print(newsTuple)
        pass
