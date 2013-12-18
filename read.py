import sqlitedict

db = sqlitedict.SqliteDict('tweepy.db', autocommit=True)

print "Last id : %s" % (db["last_id"])
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
    print "[%s] %s : %s {RT : %s (%d)} {Hashtags : %s}" % (date, author, tweet, 
                                                           rt_authors, retweets, hashtags)
