#!/usr/bin/python

# load various twitter dumps to a sqlite db

import csv
import datetime
import os
import simplejson
import sqlite3
import sys
import time

import twitter_utils

def load(file_type, filename):
    with file(filename) as f:
        if file_type == "cirip": # file dumped with cirip.ro api
            content = f.read()
            tweets = simplejson.loads(content[content.index("["):-1])
            return [{'id': None, 'created_at': twitter_utils.parse_twitter_date(t['created_at']), 'text': t['text']}
                    for t in tweets]
        elif file_type == "tweetscan": # file from tweetscan.com
            csv_reader = csv.reader(f)
            return [{'id': int(row[5]), 'created_at': datetime.datetime.fromtimestamp(int(row[2])), 'text': row[1].decode('utf-8')}
                    for i, row in enumerate(csv_reader) if i != 0]

def main(file_type, filename, db_name):
    if not os.path.exists(db_name):
        twitter_utils.create_db(db_name)

    conn = sqlite3.connect(db_name)

    tweets = load(file_type, filename)

    sys.stderr.write("parsed %s tweets. now inserting... " % len(tweets))

    for tweet in tweets:
        try:
            conn.execute("INSERT INTO tweets (twitter_id, user_id, is_retweet, created_at, text, in_reply_to_status_id, coordinates, geo, place, source) "
                         "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                         (tweet['id'], None, False, int(time.mktime(tweet['created_at'].timetuple())), tweet['text'], None, None, None, None, None))
        except sqlite3.IntegrityError:
            pass

    conn.commit()
    conn.close()

    sys.stderr.write("done!\n")

if __name__ == '__main__':
    if len(sys.argv) != 4:
        sys.stderr.write("usage: ./twitter_load.py <cirip|tweetscan> <input_filename> <output_dbname>\n")
        sys.exit(1)
    main(*sys.argv[1:])
