import sqlitedict

RESET   = "\033[0m"
RED     = "\033[031m"
GREEN   = "\033[032m"
BLUE    = "\033[034m"
YELLOW  = "\033[033m"


db = sqlitedict.SqliteDict('tweepy.db')

try:
    print "%sLast id : %s%s" % (RED, db["last_id"], RESET)
except KeyError:
    exit(1)
for tid in db:
    try:
        date        = db[tid]["date"]
        author      = db[tid]["author"]
        tweet       = db[tid]["tweet"]
        rt_authors  = db[tid]["rt_authors"]
        retweets    = db[tid]["retweets"]
        hashtags    = db[tid]["hashtags"]
    except:
        continue
    print "%s[%s]%s %s%s%s : %s\n%s{RT : %s (%d)} {Hashtags : %s}%s" % (YELLOW, date, RESET,
                                                                        BLUE, author, RESET,
                                                                        tweet, GREEN, rt_authors,
                                                                        retweets, hashtags,
                                                                        RESET)
