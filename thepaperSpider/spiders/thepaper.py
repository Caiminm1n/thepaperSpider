# -*- coding: utf-8 -*-
import re

import scrapy
from bs4 import BeautifulSoup
from scrapy import Selector
from scrapy.http import Request

from thepaperSpider.items import CategoryItem, ThepaperspiderItem, UserItem, CommentItem, ImgItem


class ThepaperSpider(scrapy.Spider):
    name = 'thepaper'
    catePass = ['视频','湃客','问政','问吧','订阅']
    cateUrlList = []
    allNewsUrlList = []
    allCommentUrlList = []
    baseUrl = "https://www.thepaper.cn"
    commentBaseUrl = "https://www.thepaper.cn/newDetail_commt.jsp?contid="
    allowed_domains = ['thepaper.cn']

    def start_requests(self):
        start_url = self.baseUrl

        return [scrapy.FormRequest(start_url,callback=self.head_url_callback)]

    def head_url_callback(self,response):
        soup = BeautifulSoup(response.body,"html5lib")
        div = soup.find_all("div",attrs={"class":"head_banner"})
        cates = div[0].find_all("a",attrs={"class":"bn_a"})
        for cate in cates:
            if cate.text in self.catePass:
                pass
            else:
                if cate.text == '精选':
                    category = cate.text
                    url = self.baseUrl + cate["href"]
                else:
                    category = cate.text
                    url = self.baseUrl+'/'+cate["href"]
                item = CategoryItem()
                item["category"] = category
                item["comefrom"] = 'category'
                yield item
                self.cateUrlList.append({category:url})
        print(self.cateUrlList)
        cate = self.cateUrlList.pop(0)
        for category,url in cate.items():
            yield Request(url,callback=self.cate_url_callback,meta={'category':category},dont_filter=True)

    def cate_url_callback(self,response):
        category = response.meta['category']
        soup = BeautifulSoup(response.body,'html5lib')
        divs= soup.find_all("div",attrs={"class":"news_tu"})
        for div in divs:
            newsUrl = div.a.attrs['href']
            newsCover = 'https:'+div.a.img.attrs['src']
            newsTitle = div.a.img.attrs['alt']
        # newsUrls = soup.find_all(href = re.compile("newsDetail_forward_\d+"))
        # print(newsUrls)
        # for newsUrl in newsUrls:
        #     print(newsUrl)
        #     url = newsUrl.attrs['href']
        #     coverUrl = 'https:'+ newsUrl.img.attrs['src']
        #     newsTitle = newsUrl.img.attrs['alt']
        # urls = re.findall("newsDetail_forward_\d+",soup.decode())
        # print(urls)
        # for url in urls:
            self.allNewsUrlList.append({category: self.baseUrl + '/' + newsUrl, newsTitle:newsCover})
        print(self.allNewsUrlList)
        if len(self.cateUrlList) == 0:
            urlDict = self.allNewsUrlList.pop(0)
            newsInfo = []
            for key in urlDict:
                newsInfo.append(key)
            category = newsInfo[0]
            newsTitle = newsInfo[1]
            newsUrl = urlDict[category]
            newsCover = urlDict[newsTitle]
            yield Request(newsUrl, callback=self.parse,
                          meta={'category': category,'newsTitle':newsTitle,'newsCover':newsCover}, dont_filter=True)
        else:
            cate = self.cateUrlList.pop(0)
            for category,url in cate.items():
                yield Request(url, callback=self.cate_url_callback, meta={'category': category}, dont_filter=True)

    def parse(self, response):
        self.logger.info("===========parse=============")
        responseUrl = response._url
        category = response.meta['category']
        newsTitle = response.meta['newsTitle']
        newsCover = response.meta['newsCover']
        # id =re.compile('\d+')
        # idResult = id.match(response._url)
        # commentId =re.findall("\d+",responseUrl)[0]
        # commentUrl = self.commentBaseUrl+commentId
        # self.allCommentUrlList.append({newsTitle:commentUrl})
        # commentDict = self.allCommentUrlList.pop(0)
        # print(commentDict)
        # for title,url in commentDict.items():
        #     yield Request(url, callback=self.comment_url_callback, meta={'title': title}, dont_filter=True)
        try:
            # commentId = re.findall("\d+", responseUrl)[0]
            # commentUrl = self.commentBaseUrl + commentId
            # self.allCommentUrlList.append({newsTitle: commentUrl})
            keywords = response.xpath("//head/meta[@name='Keywords']/@content").extract_first()
            description = response.xpath("//head/meta[@name='Description']/@content").extract_first()
            print('Keywords:'+keywords+','+'Description:'+description)
            newsContents = response.xpath("//div[@class='newscontent']")
            # newsTitle = newsContents.xpath("./h1[@class='news_title']/text()").extract_first()
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
            item["newsCover"] = newsCover
            item["newsContent"] = newsContent
            item["keywords"] = keywords
            item["description"] = description
            item["collectedCount"] = news_love
            item["category"] = category
            item["story_id"] = '1'
            item["comefrom"] = 'news'
            print(item)
            yield item
            imgItem = ImgItem()
            imgItem['image_urls'] = {newsTitle:newsCover}
            imgItem['comefrom'] = 'imgs'
            print(imgItem)
            yield(imgItem)
            commentId = re.findall("\d+", responseUrl)[0]
            commentUrl = self.commentBaseUrl + commentId
            self.allCommentUrlList.append({newsTitle: commentUrl})
            if len(self.allCommentUrlList) != 0:
                commentDict = self.allCommentUrlList.pop(0)
                print(commentDict)
                for title, url in commentDict.items():
                    yield Request(url, callback=self.comment_url_callback, meta={'title': title}, dont_filter=True)
        except:
            print("糟糕，出现exception")
            pass
        if len(self.allNewsUrlList) != 0:
            urlDict = self.allNewsUrlList.pop(0)
            newsInfo = []
            for key in urlDict:
                newsInfo.append(key)
            category = newsInfo[0]
            newsTitle = newsInfo[1]
            newsUrl = urlDict[category]
            newsCover = urlDict[newsTitle]
            yield Request(newsUrl, callback=self.parse,
                          meta={'category': category, 'newsTitle': newsTitle, 'newsCover': newsCover}, dont_filter=True)

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
            # userItem['i'] = 'user'
            yield userItem
            # userImgItem = UserImg()
            # userImgItem['userName'] = userName
            # userImgItem[]
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
