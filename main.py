"""
TODO:
 - Use OAuth to connect to twitter API - done
 - Find every mentions                 - done
 - Store :                             - todo
    * Tweet                            - done
    * Author                           - done
    * Hashtags                         - done
    * Date & time                      - todo
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
# mentions.reverse()

print "   # MENTIONS"
for mention in mentions:
    retweets = mention.retweets()
    print "%s: \"%s\" RT : %s, hastags : %s" % (mention.user.screen_name, mention.text, [rt.user.screen_name for rt in retweets], [word for word in mention.text.split() if word[0] == '#' and len(word) > 1])
