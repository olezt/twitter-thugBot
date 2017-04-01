from apscheduler.schedulers.blocking import BlockingScheduler
from bot import *
import logging

logging.basicConfig()

sched = BlockingScheduler()

@sched.scheduled_job('interval', hours=1)
def timed_job():
    findNewTrendingTweet()

sched.start()