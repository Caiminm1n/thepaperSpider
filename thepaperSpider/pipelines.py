# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import os

import jieba
import pymysql
import scrapy
from getTFIDF import TFIDF
from scrapy.exceptions import DropItem
from scrapy.pipelines.images import ImagesPipeline

from thepaperSpider.items import ImgItem, NewsThemeItem, CommentItem, UserItem, ThepaperspiderItem, CategoryItem, \
    NewsUpdateItem, StoryUpdateItem


class ThepaperspiderPipeline(object):
    def __init__(self):
        self.connect = pymysql.connect(
            host='127.0.0.1',
            port=3306,
            db='quwen',
            user='root',
            passwd='123456',
            charset='utf8',
            use_unicode=True
        )
        self.cursor = self.connect.cursor()

    def process_item(self, item, spider):
        if isinstance(item, CategoryItem):
            try:
                self.cursor.execute(
                    """insert into category(cate_name)
                        value (%s)""",
                    (item['category'])
                )
            except:
                pass
            self.connect.commit()

        if isinstance(item, ThepaperspiderItem):
            # '精选'status设为1
            print(item)
            category=item['category']
            sql = 'select cateid from category where cate_name = %s'
            self.cursor.execute(sql,(category))
            result = self.cursor.fetchone()
            cate_id = result[0]
            # story_id = item['story_id']
            if category == '主题':
                themeKeywords = item['themeKeywords']
                sql = 'select storyid from news_story where keywords = %s'
                self.cursor.execute(sql, (themeKeywords))
                result = self.cursor.fetchone()
                item['story_id'] = result[0]
                print(item)
            else:
                print(item)
            try:
                collectedCount = item['collectedCount'].replace('\n', '').replace(' ', '')
                datetime = item['datetime'].replace('\n', '').replace('\t', '')
                sql = 'insert into news(author,content,pic_url,title,keywords,description,collected_count,ctime,cate_id,story_id) value (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
                rows = self.cursor.execute(sql,(item['author'],item['newsContent'],item['newsCover'],item['title'],
                                                item['keywords'],item['description'],collectedCount,datetime,cate_id,item['story_id']))
                print(rows)
                # imgItem = ImgItem()
                # imgItem['image_urls'] = {item['title']: item['newsCover']}
                # imgItem['comefrom'] = 'imgs'
                # print(imgItem)
                # yield (imgItem)
            except:
                print("重复新闻")
                pass
            # self.cursor.execute()
            self.connect.commit()


        if isinstance(item, UserItem):
            print(item)
            try:
                self.cursor.execute(
                    """insert into user(nickname,avatar)
                        value (%s,%s)""",
                    (item['userName'],item['userImg'])
                )
            except:
                print('重复user')
                pass
            self.connect.commit()

        if isinstance(item, CommentItem):
            print(item)
            newsTitle = item['newsTitle']
            sql = 'select newsid from news where title = %s'
            self.cursor.execute(sql, (newsTitle))
            result = self.cursor.fetchone()
            news_id = result[0]
            commentAuthor = item['commentAuthor']
            sql = 'select userid from user where nickname = %s'
            self.cursor.execute(sql, (commentAuthor))
            result = self.cursor.fetchone()
            user_id = result[0]
            try:
                newsComment = item['newsComment'].replace('\n', '').replace(' ', '')
                print(newsComment)
                self.cursor.execute(
                    """insert into comment(comment_content,news_id,user_id)
                        value (%s,%s,%s)""",
                    (newsComment,news_id,user_id)
                )
            except:
                print('评论错误')
                pass
            self.connect.commit()

        if isinstance(item, NewsThemeItem):
            keywords = item['keywords']
            sql = 'select title,pic_url from news where keywords = %s'
            self.cursor.execute(sql, (keywords))
            result = self.cursor.fetchall()
            print(result)
            theme = result[0][0]
            picture = result[0][1]
            sql = 'insert into news_story(keywords,picture,theme) value (%s,%s,%s)'
            rows = self.cursor.execute(sql,(keywords,picture,theme))
            print(rows)
            self.connect.commit()
        return item

        # if item['comefrom'] == 'imgs':
        #     print(item)


# class NewsCoverPipeline(object):
#     def __init__(self):
#         self.connect = pymysql.connect(
#             host='127.0.0.1',
#             port=3306,
#             db='quwen',
#             user='root',
#             passwd='123456',
#             charset='utf8',
#             use_unicode=True
#         )
#         self.cursor = self.connect.cursor()
#
#     def process_item(self, item, spider):
#         if isinstance(item, NewsCoverItem):
#             print(item)
#             newsTitle = item['newsTitle']
#             sql = 'select newsid from news where title = %s'
#             self.cursor.execute(sql, (newsTitle))
#             result = self.cursor.fetchone()
#             news_id = result[0]
#             imgItem = ImgItem()
#             imgItem['image_urls'] = {news_id: item['newsCover']}
#             imgItem['comefrom'] = 'imgs'
#             print(imgItem)
#             yield (imgItem)
#             return item

class ImgPipeline(ImagesPipeline):

    def __init__(self, store_uri, download_func=None, settings=None):
        super().__init__(store_uri, download_func, settings)
        #本地版
        # self.imgBaseUrl = 'http://localhost:8080/images/'
        #服务器版
        self.imgBaseUrl = 'http://111.230.21.216:8080/images/newsImg/'
        self.userImgBaseUrl = 'http://111.230.21.216:8080/images/userImg/'
        self.connect = pymysql.connect(
                    host='127.0.0.1',
                    port=3306,
                    db='quwen',
                    user='root',
                    passwd='123456',
                    charset='utf8',
                    use_unicode=True
                )
        self.cursor = self.connect.cursor()

    def get_media_requests(self, item, info):
        if isinstance(item, ImgItem):
            print(item['image_urls'])
            for title,image_url in item['image_urls'].items():
                # connect = pymysql.connect(
                #             host='127.0.0.1',
                #             port=3306,
                #             db='quwen',
                #             user='root',
                #             passwd='123456',
                #             charset='utf8',
                #             use_unicode=True
                #         )
                # cursor = connect.cursor()
                # sql = 'select newsid from news where title = %s'
                # self.cursor.execute(sql, (title))
                # result = self.cursor.fetchone()
                # self.connect.commit()
                # news_id = result[0]
                yield scrapy.Request(image_url)

        if isinstance(item, UserItem):
            print(item['userImg'])
            userImg = item['userImg']
            # for userName,userImg in item['image_urls'].items():
                # connect = pymysql.connect(
                #             host='127.0.0.1',
                #             port=3306,
                #             db='quwen',
                #             user='root',
                #             passwd='123456',
                #             charset='utf8',
                #             use_unicode=True
                #         )
                # cursor = connect.cursor()
                # sql = 'select newsid from news where title = %s'
                # self.cursor.execute(sql, (title))
                # result = self.cursor.fetchone()
                # self.connect.commit()
                # news_id = result[0]
            yield scrapy.Request(userImg)

    def item_completed(self, results, item, info):
        if isinstance(item, ImgItem):
            image_paths = [x['path'] for ok, x in results if ok]
            a = os.getcwd()
            if not image_paths:
                raise DropItem("Item contains no images")
            for title,image_url in item['image_urls'].items():
                sql = 'select newsid from news where title = %s'
                self.cursor.execute(sql, (title))
                result = self.cursor.fetchone()
                # self.connect.commit()
                news_id = result[0]
                updateSql = 'update news set pic_url = %s where newsid = %s'
                rows = self.cursor.execute(updateSql, (self.imgBaseUrl+str(news_id)+".jpg",news_id))
                # updateResult = self.cursor.fetchone()
                print(rows)
                self.connect.commit()
                # news_id = updateResult[0]
                imgMd5 = image_paths[0].replace('full/','').replace('.jpg','')
                print(imgMd5)
                item['images'] = {imgMd5:news_id}
                # newname = 'newname\\'+str(news_id)+'.jpg'
                # b = os.getcwd()
                # c = image_paths[0].replace('/', '\\')
                # print(c)
                # results[0][1]['path'] = newname
                # os.rename(os.getcwd()+'\\img' + image_paths[0], os.getcwd()'\\img' + newname)
                # os.rename(os.getcwd()+'\\img\\'+c,os.getcwd()+'\\img\\'+newname)
        if isinstance(item, UserItem):
            image_paths = [x['path'] for ok, x in results if ok]
            # a = os.getcwd()
            if not image_paths:
                raise DropItem("Item contains no images")
            userName = item['userName']
            userImg = item['userImg']
            # for userName,userImg in item['image_urls'].items():
            sql = 'select userid from user where nickname = %s'
            self.cursor.execute(sql, (userName))
            result = self.cursor.fetchone()
            # self.connect.commit()
            userId = result[0]
            updateSql = 'update user set avatar = %s where userid = %s'
            rows = self.cursor.execute(updateSql, (self.userImgBaseUrl+str(userId)+".jpg",userId))
            # updateResult = self.cursor.fetchone()
            print(rows)
            self.connect.commit()
                # news_id = updateResult[0]
            imgMd5 = image_paths[0].replace('full/','').replace('.jpg','')
            print(imgMd5)
            item['images'] = {imgMd5:userId}
                # newname = 'newname\\'+str(news_id)+'.jpg'
                # b = os.getcwd()
                # c = image_paths[0].replace('/', '\\')
                # print(c)
                # results[0][1]['path'] = newname
                # os.rename(os.getcwd()+'\\img' + image_paths[0], os.getcwd()'\\img' + newname)
                # os.rename(os.getcwd()+'\\img\\'+c,os.getcwd()+'\\img\\'+newname)
        return item

class ImgFilePipeline(object):
    def process_item(self, item, spider):
        if isinstance(item, ImgItem):
            imgRootPath = 'D:\\IDEAProject\\quwenDevs\\quwen-wx-api\\src\\main\\resources\\static\\images\\newsImg\\'
            for key,value in item['images'].items():
                os.rename(os.getcwd()+"\\img\\full\\"+key+".jpg",imgRootPath+str(value)+".jpg")
                os.rename(os.getcwd()+"\\img\\thumbs\\big\\"+key+".jpg",os.getcwd()+"\\img\\thumbs\\big\\"+str(value)+".jpg")
                os.rename(os.getcwd()+"\\img\\thumbs\\small\\"+key+".jpg",os.getcwd()+"\\img\\thumbs\\small\\"+str(value)+".jpg")
                print("success")

        if isinstance(item, UserItem):
            imgRootPath = 'D:\\IDEAProject\\quwenDevs\\quwen-wx-api\\src\\main\\resources\\static\\images\\userImg\\'
            for key,value in item['images'].items():
                os.rename(os.getcwd()+"\\img\\full\\"+key+".jpg",imgRootPath+str(value)+".jpg")
                os.rename(os.getcwd()+"\\img\\thumbs\\big\\"+key+".jpg",os.getcwd()+"\\img\\thumbs\\big\\"+str(value)+".jpg")
                os.rename(os.getcwd()+"\\img\\thumbs\\small\\"+key+".jpg",os.getcwd()+"\\img\\thumbs\\small\\"+str(value)+".jpg")
                print("success")
        return item

class NewsUpdatePipeline(object):
    def __init__(self):
        self.connect = pymysql.connect(
            host='127.0.0.1',
            port=3306,
            db='quwen',
            user='root',
            passwd='123456',
            charset='utf8',
            use_unicode=True
        )
        self.cursor = self.connect.cursor()
        self.contentDict= {}

    def process_item(self, item, spider):
        if isinstance(item, NewsThemeItem):
            keywords = item['keywords']
            sql = 'select storyid from news_story where keywords = %s'
            self.cursor.execute(sql, (keywords))
            result = self.cursor.fetchone()
            print(result)
            storyid = result[0]

            sql = 'update news set story_id = %s where keywords = %s'
            rows = self.cursor.execute(sql,(storyid,keywords))
            print(rows)
            self.connect.commit()

        if isinstance(item, NewsUpdateItem):
            newsId = item['newsId']
            sql = 'select * from comment where news_id = %s'
            self.cursor.execute(sql, (newsId))
            result = self.cursor.fetchall()
            print(result)
            comment_count = len(result)
            print(comment_count)
            sql = 'select collected_count,story_id from news where newsid = %s'
            self.cursor.execute(sql,(newsId))
            result = self.cursor.fetchall()
            collected_count = result[0][0]
            storyid = result[0][1]
            sql = 'update news set comment_count = %s where newsid = %s'
            rows = self.cursor.execute(sql, (comment_count, newsId))
            print(rows)
            print(comment_count+collected_count)
            if comment_count+collected_count<200 or storyid >1:
                print('总数小于200或非主题')
                # sql = 'update news set status = %s where newsid = %s'
                # rows = self.cursor.execute(sql, ('0', newsId))
                # print(rows)
            else:
                status = int('1')
                sql = 'update news set status = %s where newsid = %s'
                rows = self.cursor.execute(sql, (status, newsId))
                print(rows)
            self.connect.commit()
            # print(collected_count)
            #
            # sql = 'update news set story_id = %s where keywords = %s'
            # rows = self.cursor.execute(sql,(storyid,keywords))
            # print(rows)
            # self.connect.commit()

        if isinstance(item, StoryUpdateItem):
            storyid = item['storyId']
            # 新闻内容相似度过滤
            # sql = 'select keywords from news_story where storyid = %s'
            # self.cursor.execute(sql,(storyid))
            # result = self.cursor.fetchall()
            # keywords = result[0][0]
            # keywordList = keywords.split(',')
            # print(keywordList)
            # sql = 'select newsid,content from news where story_id = %s'
            # self.cursor.execute(sql,(storyid))
            # contentTuple = self.cursor.fetchall()
            # newsLength = len(contentTuple)
            # for content in contentTuple:
            #     self.contentDict[content[0]]=content[1]
            #     # self.contentList.append({content[0],content[1]});
            # print(self.contentDict)
            # resultList = self.main_word(newsLength,keywordList,self.contentDict)
            sql = 'select newsid from news where story_id = %s'
            self.cursor.execute(sql, (storyid))
            result = self.cursor.fetchall()
            print(result)
            storyNewsCount = len(result)
            print(storyNewsCount)
            if storyNewsCount < 3:
                sql = 'update news set story_id = %s where story_id = %s'
                rows = self.cursor.execute(sql, ('1', storyid))
                print(rows)
                sql = 'delete from news_story where storyid = %s'
                rows = self.cursor.execute(sql,(storyid))
                print(rows)
            else:
                print('保留主题')
            self.connect.commit()
        return item

    def main_word(self,allnum, keyword, dict):  # 参数分别是（总文章数，关键词列表， id:TEXT文章）
        count_word = {}
        dict_text = {}
        TFIDF_dict = {}
        data = []
        # data = keyword
        for word in keyword:
            data.append((' '.join(jieba.cut_for_search(word))).split(' '))#以空格将分词隔开，再用split函数将其分成不同list
        keyword = []
        for wordlist in data:
            for word in wordlist:
                keyword.append(word)
        print('关键词分词以后的数据：', data)
        print(keyword)
        print('\n')
        for word in keyword:
            count_word[word] = 0
        for url, text in dict.items():
            # 计算每篇文章的关键字频率，存储，并统计关键字文章数
            data = TFIDF.jf_word(text)
            freq_word = TFIDF.frequence_word(keyword, data)
            for key, freq in freq_word.items():
                if (freq != 0):
                    count_word[key] = count_word[key] + 1
            dict_text[url] = freq_word
        for url, freq_dict in dict_text.items():
            TFIDF_dict[url] = TFIDF.get_TFIDF(allnum, freq_dict, count_word)
        array = sorted(TFIDF_dict.items(), key=lambda e: e[1], reverse=True)
        return list(array)  # 返回按TFIDF值大到小排序的（网址，TFIDF）对