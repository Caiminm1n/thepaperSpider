# -*- coding: utf-8 -*-
import pymysql
import scrapy

from thepaperSpider.items import NewsUpdateItem, StoryUpdateItem


class UpdateSpider(scrapy.Spider):
    name = 'update'
    allowed_domains = ['news.baidu.com']
    start_urls = ['https://news.baidu.com/']
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
        sql = 'select storyid from news_story'
        result = self.cursor.execute(sql)
        storyTuple = self.cursor.fetchall()
        for story in storyTuple:
            storyId = story[0]
            item = StoryUpdateItem()
            item['storyId'] = storyId
            yield item
        print(storyTuple)
        self.connect.commit()
        # pass
