#!/usr/bin/python

import base64
import biplist
import datetime
from getopt import getopt
import json
import sys
import urllib
import urllib2

USERNAME = None
PASSWORD = None

def dthandler(o):
    if isinstance(o, datetime.datetime):
        return o.isoformat()
    else:
        raise TypeError()

def path_call(url):
    headers = {'User-Agent': "Path/2.1.2 CFNetwork/548.0.4 Darwin/11.0.0", 'Accept': "*/*",
               'Accept-Charset': 'utf-8', 'X-PATH-CLIENT': "iOS/2.1.2",
               'X-PATH-TIMEZONE': "Europe/Bucharest",
               'X-PATH-LOCALE': "ro_RO", 'X-PATH-LANGUAGE': "en",
               'Accept-Language': "en-us", 'Accept-Encoding': "gzip, deflate",
               'Authorization': "Basic %s" % base64.encodestring("%s:%s" % (USERNAME, PASSWORD)).replace("\n", "")}

    return biplist.readPlistFromString(urllib2.urlopen(urllib2.Request(url, headers=headers)).read())

def path_search_user(name):
    return path_call("https://api.path.com/3/user/search?%s" % urllib.urlencode({'query': name}))

def path_get_moments(user_id, older_than):
    url = "https://api.path.com/3/moment/feed?user_id=%s" % user_id
    if older_than is not None:
        url = "%s&older_than=%s" % (url, older_than)

    return path_call(url)

def search_user(name):
    content = path_search_user(name)

    for id in content['people_ids']:
        print id, content['people'][id]['first_name'], content['people'][id]['last_name']

def get_moments(user_id):
    older_than = None

    page = 0

    while True:
        page += 1

        has_next = False

        content = path_get_moments(user_id, older_than)

        for moment in content['moments']:
            if older_than is None or moment['created'] < older_than:
                older_than = moment['created']
                has_next = True

        sys.stdout.write("%s\n" % json.dumps(content, default=dthandler))

        sys.stderr.write("page: %s; oldest: %s\n" % (page, datetime.datetime.fromtimestamp(older_than).strftime("%Y-%m-%d")))

        if not has_next:
            break

if __name__ == '__main__':
    do_search = None
    do_get_moments = None

    for opt, val in getopt(sys.argv[1:], "s:m:u:p:")[0]:
        if opt == "-u":
            USERNAME = val
        elif opt == "-p":
            PASSWORD = val
        elif opt == "-s":
            do_search = val
        elif opt == "-m":
            do_get_moments = val

    if do_search is not None:
        search_user(do_search)
    elif do_get_moments is not None:
        get_moments(do_get_moments)
