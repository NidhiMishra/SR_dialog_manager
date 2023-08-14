# -*- coding: utf-8 -*-

import feedparser
import webbrowser
import random
import unirest, urllib
import json
import re


class NewsCategory:
    def __init__(self,lab,url):
        self.labels=lab
        self.url=url

class OnlineNews:
    def __init__(self):
        self.categories=[]
        self.setCategories()
        self.setRandomWords()

    def addCategory(self,lab,url):
        self.categories.append(NewsCategory(lab,url))

    def setCategories(self):
        self.addCategory(['news', 'singapore'],'http://www.straitstimes.com/news/singapore/rss.xml')
        self.addCategory(['news', 'asia'],'http://www.straitstimes.com/news/asia/rss.xml')
        self.addCategory(['news', 'sports'],'http://www.straitstimes.com/news/sport/rss.xml')
        self.addCategory(['news', 'sport'],'http://www.straitstimes.com/news/sport/rss.xml')
        self.addCategory(['news', 'business'],'http://www.straitstimes.com/news/business/rss.xml')
        self.addCategory(['news', 'world'],'http://www.straitstimes.com/news/world/rss.xml')
        self.addCategory(['news', 'china'],'https://sg.news.yahoo.com/rss/china')
        self.addCategory(['news', 'india'],'http://www.thehindu.com/news/?service=rss')
        self.addCategory(['news', 'us'],'https://sg.news.yahoo.com/rss/us')
        self.addCategory(['news', 'united states'],'https://sg.news.yahoo.com/rss/us')
        self.addCategory(['news', 'entertainment'],'https://sg.news.yahoo.com/rss/entertainment')
        self.addCategory(['news', 'europe'],'https://sg.news.yahoo.com/rss/europe')
        self.addCategory(['new', 'singapore'],'http://www.straitstimes.com/news/singapore/rss.xml')
        self.addCategory(['new', 'asia'],'http://www.straitstimes.com/news/asia/rss.xml')
        self.addCategory(['new', 'sports'],'http://www.straitstimes.com/news/sport/rss.xml')
        self.addCategory(['new', 'sport'],'http://www.straitstimes.com/news/sport/rss.xml')
        self.addCategory(['new', 'business'],'http://www.straitstimes.com/news/business/rss.xml')
        self.addCategory(['new', 'world'],'http://www.straitstimes.com/news/world/rss.xml')
        self.addCategory(['new', 'china'],'https://sg.news.yahoo.com/rss/china')
        self.addCategory(['new', 'india'],'http://www.thehindu.com/news/?service=rss')
        self.addCategory(['new', 'us'],'https://sg.news.yahoo.com/rss/us')
        self.addCategory(['new', 'united states'],'https://sg.news.yahoo.com/rss/us')
        self.addCategory(['new', 'entertainment'],'https://sg.news.yahoo.com/rss/entertainment')
        self.addCategory(['new', 'europe'],'https://sg.news.yahoo.com/rss/europe')

        self.default=NewsCategory(['news'],'http://www.todayonline.com/hot-news/feed')
        self.expands=[['explain', 'news'],['more information', 'news'],['detail', 'news']]
        self.sources=[['news', 'source'],['where do you get the news']]


    def setRandomWords(self):
        self.ran_news_start = random.choice(['I found the following news articles.',
                                    'Here are the most relevant news headlines.',
                                    'These are the few new stories I found online.',
                                    'Here are the latest news headlines.'])

        self.ran_news_end = random.choice(['And there are more stories. You can view them in my computer.',
                                    'You can go to my computer and get more information about the news.',
                                    'More detailed explanation about the news can be found in my computer.',
                                    'You can read More detailed news stories from my computer.'])
							
							


    def online_search(self,chat_input):
        res=self.search_other(chat_input)
        return res

    def online_news_search(self,chat_input):
        self.setRandomWords()
        chat_input=chat_input.lower()
        res=self.search_categories(chat_input)
        if res!=None:
            return res

        res=self.search_sources(chat_input)
        if res!=None:
            return res

        res=self.search_expands(chat_input)
        if res!=None:
            return res

        res=self.search_default(chat_input)
        if res!=None:
            return res

        return None


    def search_categories(self,chat_input):
        for category in self.categories:
            if all(word in chat_input for word in category.labels):
                res = self.ran_news_start + " "+ self.description(category.url) + " "+ self.ran_news_end
                webbrowser.open(category.url)
                print res
                return res

    def search_default(self,chat_input):
        if all(word in chat_input for word in self.default.labels):
            res = self.ran_news_start + " "+ self.description(self.default.url) + " "+ self.ran_news_end
            webbrowser.open(self.default.url)
            print res
            return res

    def search_sources(self,chat_input):
        for source in self.sources:
            if all(word in chat_input for word in source):
                res = random.choice(['singapore strait times,singapore today  and yahoo news',
                                'Mostly i get information from strait times,singapore  today and yahoo news articles',
                                'i get the information from strait times,singapore  today and yahoo news pages',
                                'currently i get the information from strait times,singapore  today and yahoo news pages'])
                print res
                return res

    def search_expands(self,chat_input):
        for expand in self.expands:
            if all(word in chat_input for word in expand):
                res=self.ran_news_end
                print res
                return res

    def search_other(self,chat_input):
        q = urllib.quote(chat_input)
        #print q
        url = "https://jeannie.p.mashape.com/text/?clientFeatures=all&input="+q+"&locale=en&location=1.29%2C103.86&out=simple%2Fjson&timeZone=%2B480"
        headers={
            "X-Mashape-Key": "DhmrdzHcERmshYYg5PdsVXDhXkHcp1ckRDUjsnw2BUCh2QjCHg",
            "Accept": "application/json"
            }
        response = unirest.post(url, headers = headers)
        params = json.loads(response.raw_body)
        #print response.raw_body
        unirest.timeout(5)
        try:
            res =  params['output'][0]['actions']['say']['text'].encode('ascii', 'ignore')
            #print res
            res = re.sub('\(.*?\)','', res)
            res = re.sub('\<.*?\>','', res)
            res = re.sub('\[.*?\]','', res)
            Sentences = re.split('[?!.][\s]*',res)

            if(len( Sentences ) > 2):
                s1 = re.sub('\(.*?\)','', Sentences[0])
                s2 = re.sub('\(.*?\)','', Sentences[1])
                res = s1 + '. ' + s2

            res = self.clean_string(res)
            print res
            return res
        except:
            return None

    def good_word(self,word):
        import string
        for c in word:
            if not c in string.printable:
                return False
        return True

    def clean_string(self,str):
        return ' '.join([w for w in str.split() if self.good_word(w)])

    def description(self,url):
        feed = feedparser.parse(url)
        rssfeed =  (feed['entries'][0].title).encode('ascii', 'ignore')  + '.' #+ (feed['entries'][1].title).encode('ascii', 'ignore')+ '.'+(feed['entries'][2].title).encode('ascii', 'ignore')+'.'
        return rssfeed


if __name__=="__main__":
    News=OnlineNews()
    while True:
        input=raw_input("Please start your searching: ")
        News.online_search(input)
        print "\n"

		




