#!/usr/bin/python

from collections import defaultdict
import datetime
import sqlite3
import sys
import time

def show_month_counts(db_name):
    conn = sqlite3.connect(db_name)
    c = conn.execute("SELECT created_at FROM tweets")
    counts = defaultdict(int)
    for created_at, in c:
        created_at = datetime.datetime.fromtimestamp(time.mktime(time.gmtime(created_at)))
        counts['%s-%02d' % (created_at.year, created_at.month)] += 1
    conn.close()

    for month, count in sorted(counts.iteritems(), reverse=True):
        print month, count

def main(args):
    if args[1] == "month_count":
        show_month_counts(args[0])

if __name__ == '__main__':
    main(sys.argv[1:])
