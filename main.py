import sys
try:
    import keys
except ImportError:
    print >> sys.stderr, """Error : Could not import keys module.
You must follow the How To in README.md"""
    exit(1)
import tweepy
import sqlitedict

class Database(object):
    def __init__(self, filename, autocommit = True):
        self.db = sqlitedict.SqliteDict(filename, autocommit)
        try:
            self.db["last_id"]
        except KeyError:
            self.db["last_id"] = 0

class Tweet(object):
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

    def archive(self, db):
        db[self.id] = {
            "author"            : self.author,
            "tweet"             : self.tweet,
            "retweets"          : len(self.retweets),
            "rt_authors"        : self.rt_authors,
            "date"              : self.date,
            "hashtags"          : self.hashtags
            }

    def __str__(self):
        return "[%s] %s : %s\n(RT : %s (%d), HT : %s)" % (self.date, self.author, self.tweet,
                                                          self.rt_authors, len(self.retweets),
                                                          self.hashtags)

class AuthHandler(object):
    def __init__(self, consumer, consumer_secret, token, token_secret):
        self.auth = tweepy.OAuthHandler(consumer, consumer_secret)
        self.auth.set_access_token(token, token_secret)
        self.api = tweepy.API(self.auth)

class MentionManager(object):
    def __init__(self, api):
        self.mentions = api.mentions_timeline()
        self.mentions.reverse()
        self.tweets = []

    def get_new_mentions(self, last_id):
        for mention in self.mentions:
            if mention.id > last_id:
                try:
                    self.tweets.append(Tweet(mention))
                except tweepy.error.TweepError as e:
                    print >> sys.stderr, "Error %d : %s" % (e[0][0]["code"], e[0][0]["message"])

    def archive_mentions(self, db):
        for tweet in self.tweets:
            tweet.archive(db)

def main():
    db = Database("tweepy.db")
    auth = AuthHandler(keys.consumer_key, keys.consumer_secret,
                       keys.access_token, keys.access_token_secret)
    engine = MentionManager(auth.api)
    try:
        db.db["last_id"]
    except KeyError:
        db.db["last_id"] = 0
    finally:
        engine.get_new_mentions(db.db["last_id"])
    engine.archive_mentions(db.db)

if __name__ == "__main__":
    main()
