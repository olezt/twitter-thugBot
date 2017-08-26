import random
from io import BytesIO

import requests
import tweepy

#this import/download is needed to prevent heroku app crash
import imageio
imageio.plugins.ffmpeg.download()

from PIL import Image
from PIL import ImageFile
from PIL import ImageFont
from PIL import ImageDraw

from moviepy.editor import ImageSequenceClip

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
    """Tweet given url image"""
    filename = 'images/temp.jpg'
    request = requests.get(url, stream=True)
    if request.status_code == 200:
        i = Image.open(BytesIO(request.content))
        i.save(filename)
        result = detectFace(filename)
        if result==1:
            text = random.choice(list(open('yesQuotes.txt'))).rstrip() + " #oleztThugBot SearchQuery: "+ hashtag
            if random.randint(0, 2) != 0:
                createGif(filename)
                imageToTweet = 'images/editedImage.gif'
            else:
                imageToTweet = 'images/editedImage.png'
        else:
            scramble(filename)
            addMeme('images/editedImage.png', 'images/'+str(random.randint(0, 5))+'.png')
            text = random.choice(list(open('noQuotes.txt'))).rstrip() + " #oleztThugBot SearchQuery: " + hashtag
            imageToTweet = 'images/editedImage.png'
        api.update_with_media(imageToTweet, status=text)
    else:
        findNewTrendingTweet()

def createGif(filename):
    """Create a gif using initial and edited images"""
    clip = ImageSequenceClip([filename, 'images/editedImage.png'], fps=1350)
    clip.write_gif('images/editedImage.gif')

def removeDuplicateFaces(facesStraight, facesProfile):
    """Combine and remove duplicate detected faces"""
    faces = []
    if len(facesStraight)>0 and len(facesProfile)>0:
        duplicateFaces = []
        for (x1,y1,w1,h1) in facesStraight:
            for (x2,y2,w2,h2) in facesProfile:
                #weight and height produced are always equals
                if (((x1+(w1/2)) - (x2+(w2/2))) ** 2 + ((y1+(w1/2)) - (y2+(w2/2))) ** 2) <= (w2/1.5) ** 2:
                    duplicateFaces.append([x2,y2,w2,h2])
        faces = np.concatenate((facesStraight, facesProfile), axis=0)
        faces = [x for x in faces if x not in np.array(duplicateFaces)]
    elif len(facesStraight)>0:
        faces = facesStraight
    else:
        faces = facesProfile
    return faces

def detectFace(filename):
    """Detect faces on given image"""
    img = cv2.imread(filename, cv2.IMREAD_UNCHANGED)
    glasses = cv2.imread('images/thugLifeGlasses.png', cv2.IMREAD_UNCHANGED)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    facesStraight = np.array(face_cascade.detectMultiScale(gray, 1.3, 5))
    if len(facesStraight)<=0:
        facesStraight = np.array(face_cascade_alt.detectMultiScale(gray, 1.3, 5))
    facesProfile = np.array(face_cascade_profile.detectMultiScale(gray, 1.3, 5))
    faces = removeDuplicateFaces(facesStraight, facesProfile)
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
    """Scramble given image blocks"""
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
    cv2.imwrite('images/editedImage.png',img)
    
def addMeme(filename, meme):
    """Add a random meme since no face was detected"""
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
    """Check if tweet includes an image"""
    if i<len(searchResults):
        if 'media' in searchResults[i].entities:
            for image in searchResults[i].entities['media']:
                tweet_image(image['media_url'], searchResults[i].text, hashtag)
        else:
            checkForImage(searchResults, i+1, hashtag)
    else:
        findNewTrendingTweet()

def findNewTrendingTweet():
    """Find a new trending tweet to use as image source"""
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
    """Pick a trending hashtag to use as source to search for tweets"""
    noGlassesForYou = re.compile('xa|x.a.|xrisi|avgi|xrysi|xrisi|\u03c7\u03b1|\u03c7\u03c1\u03c5\u03c3\u03b7|\u03c7\u03c1\u03c5\u03c3\u03ae|\u03b1\u03c5\u03b3|\u03b1\u03b2\u03b3|\u03c7\u002e\u03b1\u002e', re.IGNORECASE)
    randomInt = random.randint(1, len (trends[0]['trends'])-1)
    name = trends[0]['trends'][randomInt]['name']
    if noGlassesForYou.search(name):
        print ('X.A. related hashtag was not tweeted.')
        pickHashtag(trends)
    else:
        return randomInt;

class thugBot():
    """Init bot by finding a trending tweet"""
    findNewTrendingTweet()

thugBot()
