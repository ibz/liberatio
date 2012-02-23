
import calendar
import datetime
import rfc822
import sqlite3

def create_db(db_name):
    conn = sqlite3.connect(db_name)
    conn.execute("CREATE TABLE tweets (id INTEGER PRIMARY KEY, twitter_id INTEGER UNIQUE, user_id INTEGER, is_retweet INTEGER NOT NULL, created_at INTEGER NOT NULL, text TEXT NOT NULL, in_reply_to_status_id INTEGER, coordinates TEXT, geo TEXT, place TEXT, source TEXT)")
    conn.close()

def parse_twitter_date(d):
    return datetime.datetime.fromtimestamp(calendar.timegm(rfc822.parsedate(d)))
