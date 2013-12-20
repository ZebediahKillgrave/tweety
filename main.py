import sys
from time import time
try:
    import keys
except ImportError:
    print >> sys.stderr, "Error : could not import key module (read the README)."
    exit(1)
import tweepy
import sqlitedict

"""
db is a dict we will save in tweepy.db sqlite file.
We just need to init the "last_id" key if it does not exist.
"""
db = sqlitedict.SqliteDict("tweepy.db", autocommit = True)
try:
    db["last_id"]
except KeyError:
    db["last_id"] = 0

class TwitterLimit(Exception):
    """Custom exception handling twiter api reset time for the display"""
    def __init__(self, message, reset):
        Exception.__init__(self, "%s [reset in %dsec]" % (message, reset - time()))

class Tweet(object):
    """Tweet class containing all the data we need to save about the mentions"""
    def __init__(self, tweet):
        self.id = tweet.id
        self.author = tweet.user.screen_name
        self.tweet = tweet.text
        self.retweets = tweet.retweets()
        self.rt_authors = [rt.user.screen_name for rt in self.retweets]
        self.date = tweet.created_at
        self.hashtags = [word for word in tweet.text.split() if self.word_is_hashtag(word)]

    def word_is_hashtag(self, word):
        return (word[0] == '#' and len(word) > 1)

    def archive(self):
        db[self.id] = {
            "author"            : self.author,
            "tweet"             : self.tweet,
            "retweets"          : len(self.retweets),
            "rt_authors"        : self.rt_authors,
            "date"              : self.date,
            "hashtags"          : self.hashtags
            }
        if db["last_id"] < self.id:
            db["last_id"] = self.id

    def __str__(self):
        return "[%s] %s : %s\n(RT : %s (%d), HT : %s)" % (self.date, self.author, self.tweet,
                                                          self.rt_authors, len(self.retweets),
                                                          self.hashtags)

class AuthHandler(object):
    """Simple class that will connect us to twitter api when instantiate"""
    def __init__(self, consumer, consumer_secret, token, token_secret):
        self.auth = tweepy.OAuthHandler(consumer, consumer_secret)
        self.auth.set_access_token(token, token_secret)
        self.api = tweepy.API(self.auth)

class RateLimit(object):
    """This class will check the remaining calls to twitter api on demand and
    raise a TwitterLimit exception if there is no more call available"""
    def __init__(self, limits):
        self.resources = limits["resources"]
        self.rate_limit_context = limits["rate_limit_context"]

    def check_remaining(self, category, name, done = 0):
        current = self.resources[category]["/%s/%s" % (category, name)]
        if current["remaining"] - done <= 0:
            raise TwitterLimit("Limit reached for %s" % (name), current["reset"])

class MentionManager(object):
    """Main class of the program, it's used to get all the new mentions with an
    id above the last_id we already got and to archive them into the database."""
    def __init__(self, api):
        self.limits = RateLimit(api.rate_limit_status())
        self.limits.check_remaining("statuses", "mentions_timeline")
        self.mentions = api.mentions_timeline()
        self.mentions.reverse()
        self.tweets = []

    def get_new_mentions(self, last_id):
        for mention in self.mentions:
            if mention.id < last_id:
                return
            self.limits.check_remaining("statuses", "retweets/:id", len(self.tweets))
            self.tweets.append(Tweet(mention))

    def archive_mentions(self):
        for tweet in self.tweets:
            tweet.archive()
            print "[+] %s" % (tweet)
        if not self.tweets:
            print "No tweet to archive."

def main():
    auth = AuthHandler(keys.consumer_key, keys.consumer_secret,
                       keys.access_token, keys.access_token_secret)
    try:
        engine = MentionManager(auth.api)
        engine.get_new_mentions(db["last_id"])
    except TwitterLimit as e:
        print >> sys.stderr, e
    engine.archive_mentions()

if __name__ == "__main__":
    main()
