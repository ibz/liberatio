#!/usr/bin/python

# get tweets using twitter api and insert into sqlite db

import os
import simplejson
import sqlite3
import sys
import urllib
import urllib2
import time

import twitter_utils

def cleanup_status(status):
    status['created_at'] = twitter_utils.parse_twitter_date(status['created_at'])
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

def main(screen_name, db_name):
    if not os.path.exists(db_name):
        twitter_utils.create_db(db_name)

    conn = sqlite3.connect(db_name)

    c = conn.execute("SELECT max(id) FROM tweets")
    since_id = c.fetchall()[0][0]

    page = 1
    fail_count = 0
    while True:
        sys.stderr.write("since_id=%s, page=%s, fail_count=%s...\n" % (since_id, page, fail_count))

        try:
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
    if len(sys.argv) != 3:
        sys.stderr.write("usage: ./twitter_fetch.py <screen_name> <output_dbname>\n")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
