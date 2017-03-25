import random
from io import BytesIO

import requests
import tweepy
from PIL import Image
from PIL import ImageFile
import re

from secrets import *

ImageFile.LOAD_TRUNCATED_IMAGES = True

auth = tweepy.OAuthHandler(C_KEY, C_SECRET)
auth.set_access_token(A_TOKEN, A_TOKEN_SECRET)

api = tweepy.API(auth)	

def tweet_image(url, text):
    filename = 'temp.jpg'
    request = requests.get(url, stream=True)
    if request.status_code == 200:
        i = Image.open(BytesIO(request.content))
        i.save(filename)
        scramble(filename)
        text = re.sub(r'[@]', '[PAPAKI]', text)
        api.update_with_media('scramble.jpg', status=text)
    else:
        findNewTrendingTweet()


def scramble(filename):
    BLOCKLEN = 200  # Adjust and be careful here.

    img = Image.open(filename)
    width, height = img.size

    xblock = width // BLOCKLEN
    yblock = height // BLOCKLEN
    blockmap = [(xb * BLOCKLEN, yb * BLOCKLEN, (xb + 1) * BLOCKLEN, (yb + 1) * BLOCKLEN)
                for xb in range(xblock) for yb in range(yblock)]

    shuffle = list(blockmap)
    random.shuffle(shuffle)

    result = Image.new(img.mode, (width, height))
    for box, sbox in zip(blockmap, shuffle):
        c = img.crop(sbox)
        result.paste(c, box)
    result.save('scramble.jpg')

def findNewTrendingTweet():
        if random.randint(1, 4)==1:
                trends = api.trends_place(1) #globalTrends
        else:
                trends = api.trends_place(23424833) #greeceTrends
        randomInt = random.randint(1, 10)
        hashtag = trends[0]['trends'][randomInt]['query']
        searchResults = api.search(q=hashtag, rpp=1, result_type='mixed')
        randomInt = random.randint(1, 3)
        if 'media' in searchResults[randomInt].entities:
            for image in searchResults[randomInt].entities['media']:
                tweet_image(image['media_url'], searchResults[randomInt].text)
        else:
                api.retweet(searchResults[randomInt].id_str)
class oleztBot():
	findNewTrendingTweet()
	
oleztBot()
