#!/usr/bin/python

import calendar
import datetime
import rfc822
import simplejson
import sys
import urllib
import urllib2
import time
import traceback

def cleanup_status(status):
    status['created_at'] = datetime.fromtimestamp(calendar.timegm(rfc822.parsedate(status['created_at'])))
    return status

def user_timeline(screen_name, page, count=200, max_id=None):
    params = {'screen_name': screen_name, 'page': page, 'count': count, 'trim_user': 1, 'include_rts': 1, 'exclude_replies': 0}
    if max_id:
        params['max_id'] = max_id
    try:
        response = urllib2.urlopen("http://api.twitter.com/1/statuses/user_timeline.json?" + urllib.urlencode(params))
    except urllib2.HTTPError:
        traceback.print_exc()
        return []
    try:
        return [s for s in simplejson.loads(response.read()) if not s['in_reply_to_status_id']]
    except:
        traceback.print_exc()
        return []
    finally:
        response.close()

def main(screen_name):
    page = 1
    while True:
        sys.stderr.write("page %s\n" % page)
        tweets = user_timeline(screen_name, page)
        for tweet in tweets:
            print tweet
        time.sleep(25)
        if tweets:
            page += 1

if __name__ == '__main__':
    main(sys.argv[1])
