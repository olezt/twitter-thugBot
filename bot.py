import random
from io import BytesIO

import requests
import tweepy

from PIL import Image
from PIL import ImageFile
from PIL import ImageFont
from PIL import ImageDraw

import numpy as np
import cv2

import re

from secrets import *

ImageFile.LOAD_TRUNCATED_IMAGES = True

auth = tweepy.OAuthHandler(C_KEY, C_SECRET)
auth.set_access_token(A_TOKEN, A_TOKEN_SECRET)

api = tweepy.API(auth)	

face_cascade = cv2.CascadeClassifier('haarcascades/haarcascade_frontalface_default.xml')
face_cascade_alt = cv2.CascadeClassifier('haarcascades/haarcascade_frontalface_alt.xml')
face_cascade_profile = cv2.CascadeClassifier('haarcascades/haarcascade_profileface.xml')

def tweet_image(url, text, hashtag):
    filename = 'images/temp.jpg'
    request = requests.get(url, stream=True)
    if request.status_code == 200:
        i = Image.open(BytesIO(request.content))
        i.save(filename)
        result = detectFace(filename)
        text = "Nailed it! #oleztThugBot SearchQuery: "+ hashtag
        if result==0:
            scramble(filename)
            addMeme('images/editedImage.png', 'images/seriously.png')
            text = "Couldn't find any face! Shiaat #oleztThugBot SearchQuery: " + hashtag
        api.update_with_media('images/editedImage.png', status=text)
    else:
        findNewTrendingTweet()

def detectFace(filename):
    img = cv2.imread(filename, cv2.IMREAD_UNCHANGED)
    glasses = cv2.imread('images/thugLifeGlasses.png', cv2.IMREAD_UNCHANGED)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    if len(faces)<=0:
        faces = face_cascade_alt.detectMultiScale(gray, 1.3, 5)
    if len(faces)<=0:
        faces = face_cascade_profile.detectMultiScale(gray, 1.3, 5)
    if len(faces)>0:
        for (x,y,w,h) in faces:
            roi_gray = gray[y:y+h, x:x+w]
            roi_color = img[y:y+h, x:x+w]
            glasses = cv2.resize(glasses, (int(w), int(h/5)))
            x_offset=int(x)
            y_offset=int(y+(h/3.5))
            for c in range(0,3):
                img[y_offset:y_offset+glasses.shape[0], x_offset:x_offset+glasses.shape[1], c] = glasses[:,:,c] * (glasses[:,:,3]/255.0) +  img[y_offset:y_offset+glasses.shape[0], x_offset:x_offset+glasses.shape[1], c] * (1.0 - glasses[:,:,3]/255.0)
        cv2.imwrite('images/editedImage.png',img)
        return 1
    else:
        cv2.imwrite('images/editedImage.png',img)
        return 0

def scramble(filename):
    BLOCKLEN = 80  # Adjust and be careful here.

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
    result.save('images/editedImage.png')
    #Crop black edges
    img = cv2.imread('images/editedImage.png')
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    _,thresh = cv2.threshold(gray,1,255,cv2.THRESH_BINARY)
    im2, contours,hierarchy = cv2.findContours(thresh,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    cnt = contours[0]
    x,y,w,h = cv2.boundingRect(cnt)
    img = img[y:y+h,x:x+w]
    cv2.imwrite('editedImage.png',img)
    
def addMeme(filename, meme):
    img = cv2.imread(filename)
    height, width, channels = img.shape
    memeImg = cv2.imread(meme, cv2.IMREAD_UNCHANGED)
    memeImg = cv2.resize(memeImg, (int(width/2), int(height/2)))
    x_offset=int(width/2-25)
    y_offset=int(height/2)
    for c in range(0,3):
        img[y_offset:y_offset+memeImg.shape[0], x_offset:x_offset+memeImg.shape[1], c] = memeImg[:,:,c] * (memeImg[:,:,3]/255.0) + img[y_offset:y_offset+memeImg.shape[0], x_offset:x_offset+memeImg.shape[1], c] * (1.0 - memeImg[:,:,3]/255.0)
    cv2.imwrite(filename,img)

def checkForImage(searchResults, i, hashtag):
    if i<len(searchResults):
        if 'media' in searchResults[i].entities:
            for image in searchResults[i].entities['media']:
                tweet_image(image['media_url'], searchResults[i].text, hashtag)
        else:
            checkForImage(searchResults, i+1, hashtag)
    else:
        api.retweet(searchResults[i-1].id_str)

def findNewTrendingTweet():
    if random.randint(1, 3)==1:
        trends = api.trends_place(1) #globalTrends
    else:
        trends = api.trends_place(23424833) #greeceTrends
    hashtagNumber = pickHashtag(trends)
    query = trends[0]['trends'][hashtagNumber]['query']
    hashtag = trends[0]['trends'][hashtagNumber]['name']
    searchResults = api.search(q=query, count=20, result_type='mixed', include_entities=True)
    checkForImage(searchResults, 0, hashtag)
        
def pickHashtag(trends):
    noGlassesForYou = re.compile('xa|x.a.|xrisi|avgi|xrysi|xrisi|χα|χρυση|χρυσή|αυγη|αυγή|αβγη|χροισι|χ.α.', re.IGNORECASE) 
    randomInt = random.randint(1, len (trends[0]['trends'])-1)
    name = trends[0]['trends'][randomInt]['name']
    if noGlassesForYou.search(name):
        print ('X.A. related hashtag was not tweeted.')
        pickHashtag(trends)
    else:
        return randomInt;

class thugBot():
	findNewTrendingTweet()
	
thugBot()
