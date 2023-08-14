# -*- coding: utf-8 -*-
"""
Created on Fri Jan 11 11:16:26 2019

@author: IMI-Ranjan
"""

# General:
import tweepy           # To consume Twitter's API
import pandas as pd     # To handle data
import numpy as np      # For number computing
import re
# For plotting and visualization:
from IPython.display import display
import matplotlib.pyplot as plt
#import seaborn as sns

CONSUMER_KEY = "hFo8KyAeeSTJhxQ6NVXXYkZMT"
CONSUMER_SECRET = "KDyFEw231WSNsKM620EWFf4YR9bQuM3B5AMTOX2hUKaBPQ3Xt8"

ACCESS_TOKEN = "1037396414-DiVYQNJk06vK08C8zCzKQKkN5fTs4ODRWEu1fuU"
ACCESS_SECRET = "JUaOc1GnB8L5giaSHrRsyeZuyNwN7TSmPxNKhHZuDDShy"
def trends_(extractor):
    trend = extractor.trends_place(1) # from the end of your code
# trend is a list with only one element in it, which is a
# dict which we'll put in data.
    data = trend[0]
# grab the trends
    trends = data['trends']
# grab the name from each trend
    names = [trend['name'] for trend in trends]
# put all the names together with a ' ' separating them
    trendsName = ','.join(names)
    #print("Trending topics are:",trendsName.encode('utf-8'))
    for hash in range(len(names)):
        print(names[hash])
    #print(names)
    return names
# We import our access keys:
#from credentials import *    # This will allow us to use the keys as variables
def clean_tweet(tweet):
    '''
    Utility function to clean the text in a tweet by removing
    links and special characters using regex.
    '''
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())
# API's setup:
def twitter_setup():
    """
    Utility function to setup the Twitter's API
    with our access keys provided.
    """
    # Authentication and access using keys:
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)

    # Return API with authentication:
    api = tweepy.API(auth)
    return api

# We create an extractor object:
def main():
    extractor = twitter_setup()
    trending_now = trends_(extractor)
    #print("Trending topics are:",trending_now)
    return trending_now

if __name__== "__main__":
  main()

'''
# We create a tweet list as follows:
tweets = extractor.user_timeline(screen_name="realDonaldTrump", count=1000)
print("Number of tweets extracted: {}.\n".format(len(tweets)))

# We print the most recent 5 tweets:
print("5 recent tweets:\n")
for tweet in tweets[:5]:
    print(tweet.text)
    print()
    
# We create a pandas dataframe as follows:
data = pd.DataFrame(data=[tweet.text for tweet in tweets], columns=['Tweets'])

# We display the first 10 elements of the dataframe:
display(data.head(10))
# Internal methods of a single tweet object:
print(dir(tweets[0]))
# We print info from the first tweet:
print(tweets[0].id)
print(tweets[0].created_at)
print(tweets[0].source)
print(tweets[0].favorite_count)
print(tweets[0].retweet_count)
print(tweets[0].geo)
print(tweets[0].coordinates)
print(tweets[0].entities)
# We add relevant features:
data['len']  = np.array([len(tweet.text) for tweet in tweets])
data['ID']   = np.array([tweet.id for tweet in tweets])
data['Date'] = np.array([tweet.created_at for tweet in tweets])
data['Source'] = np.array([tweet.source for tweet in tweets])
data['Likes']  = np.array([tweet.favorite_count for tweet in tweets])
data['RTs']    = np.array([tweet.retweet_count for tweet in tweets])
#Some additional features
data['created_at']= np.array([tweet.created_at for tweet in tweets])

data['text'] = list(map(lambda tweet: tweet['text'], tweet_text))
data['lang'] = list(map(lambda tweet: tweet['lang'], tweet_text))
data['country'] = list(map(lambda tweet: tweet['place']['country'] if tweet['place'] != None else None, tweet_text))
data['loc'] = list(map(lambda tweet: tweet['user']['location'] if tweet['user']['location']!=None else None,tweet_text))
data['timeframe'] = list(map(lambda tweet : tweet['created_at'] ,tweet_text))
data['timezone'] = list(map(lambda tweet : tweet['user']['time_zone'] ,tweet_text))
data['hashtags'] = list(map(lambda tweet : tweet['entities']['hashtags'],tweet_text))

# Display of first 10 elements from dataframe:
display(data.head(10))

# We extract the mean of lenghts:
mean = np.mean(data['len'])

print("The average length of tweets: {}".format(mean))

# We extract the tweet with more FAVs and more RTs:

fav_max = np.max(data['Likes'])
rt_max  = np.max(data['RTs'])

fav = data[data.Likes == fav_max].index[0]
rt  = data[data.RTs == rt_max].index[0]

# Max FAVs:
print("The tweet with more likes is: \n{}".format(data['Tweets'][fav].encode('utf-8')))
print("Number of likes: {}".format(fav_max))
print("{} characters.\n".format(data['len'][fav]))

# Max RTs:
#print("The tweet with more retweets is: \n{}".format(data['Tweets'][rt]))
print("Number of retweets: {}".format(rt_max))
print("{} characters.\n".format(data['len'][rt]))
# We create time series for data:

tlen = pd.Series(data=data['len'].values, index=data['Date'])
tfav = pd.Series(data=data['Likes'].values, index=data['Date'])
tret = pd.Series(data=data['RTs'].values, index=data['Date'])# Lenghts along time:
tlen.plot(figsize=(16,4), color='r');
# Likes vs retweets visualization:
tfav.plot(figsize=(16,4), label="Likes", legend=True)
tret.plot(figsize=(16,4), label="Retweets", legend=True);
# We obtain all possible sources:
sources = []
for source in data['Source']:
    if source not in sources:
        sources.append(source)

# We print sources list:
print("Creation of content sources:")
for source in sources:
    print("* {}".format(source))

# We create a numpy vector mapped to labels:
percent = np.zeros(len(sources))

for source in data['Source']:
    for index in range(len(sources)):
        if source == sources[index]:
            percent[index] += 1
            pass

percent /= 100

# Pie chart:
pie_chart = pd.Series(percent, index=sources, name='Sources')
pie_chart.plot.pie(fontsize=11, autopct='%.2f', figsize=(6, 6))

'''