# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ThepaperspiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    author = scrapy.Field()
    datetime = scrapy.Field()
    newsCover = scrapy.Field()
    newsContent = scrapy.Field()
    keywords = scrapy.Field()
    description = scrapy.Field()
    collectedCount = scrapy.Field()
    category = scrapy.Field()
    comefrom = scrapy.Field()
    story_id = scrapy.Field()
    themeKeywords = scrapy.Field()
    pass

class CategoryItem(scrapy.Item):
    category = scrapy.Field()
    comefrom = scrapy.Field()
    pass

class CommentItem(scrapy.Item):
    newsTitle = scrapy.Field()
    commentAuthor = scrapy.Field()
    newsComment = scrapy.Field()
    comefrom = scrapy.Field()
    pass

class UserItem(scrapy.Item):
    userName = scrapy.Field()
    userImg = scrapy.Field()
    comefrom = scrapy.Field()
    pass

class ImgItem(scrapy.Item):
    newsTitle = scrapy.Field()
    image_urls = scrapy.Field()
    images = scrapy.Field()
    comefrom = scrapy.Field()
    pass

class NewsThemeItem(scrapy.Item):
    # theme = scrapy.Field()
    keywords = scrapy.Field()
    # picture = scrapy.Field()
    pass

