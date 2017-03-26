import random
from io import BytesIO

import requests
import tweepy

from PIL import Image
from PIL import ImageFile
from PIL import ImageFont
from PIL import ImageDraw

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
    draw = ImageDraw.Draw(result)
    font = ImageFont.truetype("arial.ttf", 60)
    draw.text((20, 20),"OleztBot :)",(255,255,255),font=font)
    result.save('scramble.jpg')

def checkForImage(searchResults, randomInt):
    if 'media' in searchResults[randomInt].entities:
        for image in searchResults[randomInt].entities['media']:
            tweet_image(image['media_url'], searchResults[randomInt].text)
    else:
        checkForImage(searchResults, randomInt+1)
        #api.retweet(searchResults[randomInt].id_str)

def findNewTrendingTweet():
        if random.randint(1, 4)==1:
                trends = api.trends_place(1) #globalTrends
        else:
                trends = api.trends_place(23424833) #greeceTrends
        randomInt = random.randint(1, 10)
        hashtag = trends[0]['trends'][randomInt]['query']
        searchResults = api.search(q=hashtag, rpp=1, result_type='mixed')
        randomInt = random.randint(1, 3)
        checkForImage(searchResults, randomInt)
        
class oleztBot():
	findNewTrendingTweet()
	
oleztBot()
