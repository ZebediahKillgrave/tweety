import sys
try:
    import keys
except ImportError:
    print >> sys.stderr, """Error : Could not import keys module.
You must follow the How To in README.md"""
    exit(1)
import tweepy

auth = tweepy.OAuthHandler(keys.consumer_key, keys.consumer_secret)
auth.set_access_token(keys.access_token, keys.access_token_secret)

api = tweepy.API(auth)

print api.me().name

mentions = api.mentions_timeline()

print "   # MENTIONS"
for mention in mentions:
    print "%s: \"%s\"" % (mention.user.screen_name, mention.text)
