import tweepy

from secrets import *
from bot import *

auth = tweepy.OAuthHandler(C_KEY, C_SECRET)
auth.set_access_token(A_TOKEN, A_TOKEN_SECRET)

api = tweepy.API(auth)

THUG_BOT_ID = '845376991557812225'

class MyStreamListener(tweepy.StreamListener):

    def on_status(self, status):
        userTweetedId = status.user.id_str
        inReplyToUserId = status.in_reply_to_user_id_str
        if userTweetedId!=THUG_BOT_ID and inReplyToUserId==None:
            mentions = status.entities.get('user_mentions')
            for mention in mentions:
                if mention.get('id_str')==THUG_BOT_ID:
                    answerTweet(status)
        
def createListener():
    print ('Create oleztThugBot listener')
    myStreamListener = MyStreamListener()
    myStream = tweepy.Stream(auth = api.auth, listener=myStreamListener)
    myStream.filter(track=['oleztThugBot'])
        
createListener()
