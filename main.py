"""
TODO:
 - Use OAuth to connect to twitter API - done
 - Find every mentions                 - done
 - Store :                             - done
    * Tweet                            - done
    * Author                           - done
    * Hashtags                         - done
    * Date & time                      - done
    * Retweet number                   - done
    * List of retweeters               - done
"""

import sys
try:
    import keys
except ImportError:
    print >> sys.stderr, """Error : Could not import keys module.
You must follow the How To in README.md"""
    exit(1)
import tweepy
import sqlitedict

db = sqlitedict.SqliteDict('tweepy.db', autocommit=True)
try:
    last_id = db['last_id']
except KeyError:
    db['last_id'] = 0

auth = tweepy.OAuthHandler(keys.consumer_key, keys.consumer_secret)
auth.set_access_token(keys.access_token, keys.access_token_secret)

api = tweepy.API(auth)

print api.me().name

mentions = api.mentions_timeline()
mentions.reverse()

def word_is_hashtag(word):
    return (word[0] == '#' and len(word) > 0)

for mention in mentions:
    try:
        retweets = mention.retweets()
    except tweepy.error.TweepError as e:
        print >> sys.stderr, "Error %d : %s" % (e[0][0]["code"], e[0][0]["message"])
        
    if mention.id > db["last_id"]:
        db["last_id"] = mention.id
        db[mention.id] = {
            "author"        : mention.user.screen_name,
            "tweet"         : mention.text,
            "retweets"      : len(retweets),
            "rt_authors"    : [rt.user.screen_name for rt in retweets],
            "hashtags"      : [word for word in mention.text.split() if word_is_hashtag(word)],
            "date"          : mention.created_at
            }
        print "Added : %s" % (db[mention.id])
