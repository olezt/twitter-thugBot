import random
from io import BytesIO

import requests
import tweepy

from secrets import *

auth = tweepy.OAuthHandler(C_KEY, C_SECRET)
auth.set_access_token(A_TOKEN, A_TOKEN_SECRET)

api = tweepy.API(auth)	

def retweet():
        if random.randint(1, 2)==1:
                trends = api.trends_place(1)
        else:
                trends = api.trends_place(23424833)
        randomInt = random.randint(1, 10)
        hashtag = trends[0]['trends'][randomInt]['query']
        print (trends[0]['trends'][randomInt]['name'])
        searchResults = api.search(q=hashtag, rpp=1, result_type='mixed')
        randomInt = random.randint(1, 3)
        idToRetweet = searchResults[randomInt].id_str
        api.retweet(idToRetweet)

class oleztBot():
	retweet()
	
oleztBot()
