# -*- coding: utf-8 -*-
import re

import pymysql
import scrapy
# from bs4 import BeautifulSoup
from scrapy import Request, Selector

from thepaperSpider.items import NewsThemeItem, ThepaperspiderItem, UserItem, CommentItem, CategoryItem


class TopicSpider(scrapy.Spider):
    name = 'topic'
    baseUrl = "https://www.thepaper.cn"
    commentBaseUrl = "https://www.thepaper.cn/newDetail_commt.jsp?contid="
    topicUrlList = []
    allNewsUrlList = []
    allCommentUrlList = []
    allowed_domains = ['thepaper.cn']

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        self.connect = pymysql.connect(
            host='127.0.0.1',
            port=3306,
            db='quwen1',
            user='root',
            passwd='123456',
            charset='utf8',
            use_unicode=True
        )
        self.cursor = self.connect.cursor()

    # start_urls = ['http://thepaper.cn/']

    def start_requests(self):
        start_url = self.baseUrl
        return [scrapy.FormRequest(start_url,callback=self.head_url_callback)]

    def head_url_callback(self, response):
        sql = 'select keywords from news where cate_id = %s'
        self.cursor.execute(sql, ('1'))
        keywordsTuple= self.cursor.fetchall()
        for keywordTuple in keywordsTuple:
            keywordStr = keywordTuple[0]
            print(keywordStr)
            if keywordStr == '':
                pass
            else:
                if len(keywordStr.split(','))<2:
                    pass
                else:
                    item = NewsThemeItem()
                    item['keywords'] = keywordStr
                    yield item
                    keyword = keywordStr.replace(',','+').replace('“','').replace('”','')
                    url = "https://www.thepaper.cn/searchResult.jsp?inpsearch="+keyword+"&searchPre=all_0%3A&orderType=3"
                    print(url)
                    self.topicUrlList.append({keywordStr:url})
        print(self.topicUrlList)
        categoryItem = CategoryItem()
        categoryItem["category"] = '主题'
        yield categoryItem
        topic = self.topicUrlList.pop(0)
        for keywords,topicUrl in topic.items():
            yield Request(topicUrl, callback=self.topic_url_callback,meta={'keywords':keywords},dont_filter=True)


        # url = "https://www.thepaper.cn/searchResult.jsp?inpsearch=%E4%B9%A0%E8%BF%91%E5%B9%B3"
        # yield Request(url, callback=self.cate_url_callback, dont_filter=True)

    def topic_url_callback(self, response):
        keywords = response.meta['keywords']
        mainContent = response.xpath('//*[@id="mainContent"]')
        search_res = mainContent.xpath(".//div[@class='search_res']").extract()
        for search in search_res:
            selector = Selector(text=search)
            # h2 = selector.xpath(".//h2")
            newsUrl = selector.xpath(".//h2/a/@href").extract_first()
            # newsTitle = selector.xpath(".//h2/a/text()").extract_first()
            print(newsUrl)
            self.allNewsUrlList.append({keywords:self.baseUrl + '/' + newsUrl})
        print(self.allNewsUrlList)
        if len(self.topicUrlList) == 0:
            urlDict = self.allNewsUrlList.pop(0)
            for keyword,newsUrl in urlDict.items():
                yield Request(newsUrl, callback=self.parse,
                          meta={'keywords':keyword}, dont_filter=True)
        else:
            topic = self.topicUrlList.pop(0)
            for themeKeyword, topicUrl in topic.items():
                yield Request(topicUrl, callback=self.topic_url_callback, meta={'keywords': themeKeyword}, dont_filter=True)
        # soup = BeautifulSoup(response.body, 'html5lib')
        # //*[@id="mainContent"]
        # print(soup)

    def parse(self, response):
        topicKeywords = response.meta['keywords']
        responseUrl = response._url
        try:
            keywords = response.xpath("//head/meta[@name='Keywords']/@content").extract_first()
            description = response.xpath("//head/meta[@name='Description']/@content").extract_first()
            print('Keywords:' + keywords + ',' + 'Description:' + description)
            newsContents = response.xpath("//div[@class='newscontent']")
            newsTitle = newsContents.xpath("./h1[@class='news_title']/text()").extract_first()
            newsAuthor = newsContents.xpath("./div[@class='news_about']/p[1]/text()").extract_first()
            newsDate = newsContents.xpath("./div[@class='news_about']/p[2]/text()").extract_first()
            # newsCover = newsContents.xpath(".//img/@src").extract_first()
            newsContentList = newsContents.xpath("./div[@class='news_txt']/text()").extract()
            newsContent = "".join(newsContentList)
            print(newsContent)
            news_love = newsContents.xpath("./div[@class='news_love']//a[@class='zan']/text()").extract_first()
            item = ThepaperspiderItem()
            item["title"] = newsTitle
            item["author"] = newsAuthor
            item["datetime"] = newsDate
            item["newsCover"] = ''
            item["newsContent"] = newsContent
            item["keywords"] = keywords
            item["description"] = description
            item["collectedCount"] = news_love
            item["category"] = '主题'
            item['themeKeywords'] = topicKeywords
            item["comefrom"] = 'news'
            print(item)
            yield item
            commentId = re.findall("\d+", responseUrl)[0]
            commentUrl = self.commentBaseUrl + commentId
            self.allCommentUrlList.append({newsTitle: commentUrl})
            if len(self.allCommentUrlList) != 0:
                commentDict = self.allCommentUrlList.pop(0)
                print(commentDict)
                for title, url in commentDict.items():
                    yield Request(url, callback=self.comment_url_callback, meta={'title': newsTitle}, dont_filter=True)
        except:
            print("糟糕，出现exception")
            pass
        # pass
        if len(self.allNewsUrlList) != 0:
            urlDict = self.allNewsUrlList.pop(0)
            for keyword, newsUrl in urlDict.items():
                yield Request(newsUrl, callback=self.parse,
                              meta={'keywords': keyword}, dont_filter=True)

    def comment_url_callback(self,response):
        newsTitle = response.meta['title']
        # // *[ @ id = "mainContent"]
        mainContent = response.xpath('// *[ @ id = "mainContent"]')
        contentList = mainContent.xpath(".//div[@class='comment_que']").extract()
        for content in contentList:
            selector = Selector(text=content)
            aqwleft = selector.xpath(".//div[@class='aqwleft']//a/img/@src").extract_first()
            if len(re.findall("http:",aqwleft)) > 0:
                userImg = aqwleft
            else:
                userImg = 'https:' + aqwleft
            print(userImg)
            userName = selector.xpath(".//div[@class='aqwright']/h3/a/text()").extract_first()
            userItem = UserItem()
            userItem['userName'] = userName
            userItem['userImg'] = userImg
            userItem['comefrom'] = 'user'
            yield userItem
            userComment = selector.xpath(".//div[@class='aqwright']/div[1]/a/text()").extract_first()
            commentItem = CommentItem()
            commentItem['newsTitle'] = newsTitle
            commentItem['commentAuthor'] = userName
            commentItem['newsComment'] = userComment
            commentItem['comefrom'] = 'comment'
            yield commentItem
        if len(self.allCommentUrlList) != 0:
            commentDict = self.allCommentUrlList.pop(0)
            print(commentDict)
            for title, url in commentDict.items():
                yield Request(url, callback=self.comment_url_callback, meta={'title': title}, dont_filter=True)
