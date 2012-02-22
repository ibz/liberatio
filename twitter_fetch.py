#!/usr/bin/python

import calendar
import csv
import datetime
import os
import rfc822
import simplejson
import sqlite3
import sys
import urllib
import urllib2
import time
import traceback

def create_db(db_name):
    conn = sqlite3.connect(db_name)
    conn.execute("CREATE TABLE tweets (id INTEGER PRIMARY KEY, twitter_id INTEGER UNIQUE, user_id INTEGER, is_retweet INTEGER NOT NULL, created_at INTEGER NOT NULL, text TEXT NOT NULL, in_reply_to_status_id INTEGER, coordinates TEXT, geo TEXT, place TEXT, source TEXT)")
    conn.close()

def parse_twitter_date(d):
    return datetime.datetime.fromtimestamp(calendar.timegm(rfc822.parsedate(d)))

def cleanup_status(status):
    status['created_at'] = parse_twitter_date(status['created_at'])
    if 'retweeted_status' in status:
        status['retweeted_status'] = cleanup_status(status['retweeted_status'])
    return status

def user_timeline(screen_name, page, since_id=None, count=200):
    params = {'screen_name': screen_name, 'page': page, 'count': 200, 'trim_user': 1, 'include_rts': 1, 'exclude_replies': 0}
    if since_id:
        params['since_id'] = since_id

    response = urllib2.urlopen("http://api.twitter.com/1/statuses/user_timeline.json?" + urllib.urlencode(params))
    try:
        return [cleanup_status(s) for s in simplejson.loads(response.read())]
    finally:
        response.close()

FILE_PARSED = False
def user_timeline_file(filename):
    global FILE_PARSED
    if FILE_PARSED:
        return []
    with file(filename) as f:
        lines = f.readlines()
        FILE_PARSED = True

        if lines[0][0] == "{":
            # file dumped previously by me
            return [cleanup_status(eval(line.strip())) for line in lines]
        elif lines[0].startswith("var cirip = "):
            # file exported from cirip.ro
            content = lines[0][lines[0].index("["):-1]
            tweets = simplejson.loads(content)
            return [{'id': None, 'user': {'id': None}, 'created_at': parse_twitter_date(t['created_at']), 'text': t['text'], 'in_reply_to_status_id': None} for t in tweets if t['source'] == "twitter2cirip"]
        elif lines[0].startswith("User,"):
            # file from Tweet Scan
            csv_reader = csv.reader(lines[1:])
            return [{'id': int(row[5]), 'user': {'id': None}, 'created_at': datetime.datetime.fromtimestamp(int(row[2])), 'text': row[1].decode('utf-8'), 'in_reply_to_status_id': None} for row in csv_reader]

def main(screen_name=None, input_file=None, output_file=None):
    db_name = output_file or ("twitter_%s.db" % screen_name)

    if not os.path.exists(db_name):
        create_db(db_name)

    conn = sqlite3.connect(db_name)

    c = conn.execute("SELECT max(id) FROM tweets")
    since_id = c.fetchall()[0][0]

    page = 1
    fail_count = 0
    while True:
        sys.stderr.write("since_id=%s, page=%s, fail_count=%s...\n" % (since_id, page, fail_count))

        try:
            if screen_name is None:
                tweets = user_timeline_file(input_file)
            else:
                tweets = user_timeline(screen_name, page, since_id=since_id)
            fail_count = 0
        except urllib2.HTTPError:
            if fail_count < 5:
                fail_count += 1
                continue
            else:
                sys.stderr.write("fail whale keeps showing up. stopped retrying...")
                break

        if not tweets:
            break

        for tweet in tweets:
            is_retweet = 'retweeted_status' in tweet
            if is_retweet:
                tweet = tweet['retweeted_status']

            try:
                conn.execute("INSERT INTO tweets (twitter_id, user_id, is_retweet, created_at, text, in_reply_to_status_id, coordinates, geo, place, source) "
                             "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                             (tweet['id'], tweet['user']['id'], is_retweet, int(time.mktime(tweet['created_at'].timetuple())), tweet['text'], tweet['in_reply_to_status_id'],
                              simplejson.dumps(tweet['coordinates']) if tweet.get('coordinates') else None, simplejson.dumps(tweet['geo']) if tweet.get('geo') else None, simplejson.dumps(tweet['place']) if tweet.get('place') else None, tweet.get('source')))
            except sqlite3.IntegrityError:
                pass

            conn.commit()

        time.sleep(25 * (fail_count + 1))

        page += 1

    conn.close()

if __name__ == '__main__':
    if len(sys.argv) == 3:
        # read from file
        main(input_file=sys.argv[1], output_file=sys.argv[2])
    else:
        main(screen_name=sys.argv[1])
