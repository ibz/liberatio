#!/usr/bin/env python

__doc__ = """Usage: %s username [start_from_number]""" % __file__

from datetime import datetime
import re
from StringIO import StringIO
import sys
import urllib
import urllib2

from lxml.html import parse

PROXY = ""
PROXY_USER = ""
PROXY_PASS = ""

def get_photo_ids(username, page=1):
    url = "http://twitpic.com/photos/%s?page=%s" % (username, page)
    html = urllib2.urlopen(url).read()
    doc = parse(StringIO(html)).getroot()
    for photo in doc.cssselect(".user-photo a"):
        photo_id = photo.attrib['href'][1:]
        yield photo_id
    if re.search(r"/photos/%s\?page=%s" % (username, page + 1), html):
        for photo_id in get_photo_ids(username, page + 1):
            yield photo_id

def save_photo(title, photo_id):
    doc = parse(urllib2.urlopen("http://twitpic.com/%s" % photo_id)).getroot()
    img = doc.cssselect("#view-photo-main #photo img#photo-display")[0]
    image_data = urllib2.urlopen(img.attrib['src']).read()
    date = re.match(r"^Posted on (.*)$", doc.cssselect("#photo-info div")[0].text).groups()[0]
    date = datetime.strptime(date, "%B %d, %Y")
    filename = "%s %s.jpg" % (date.strftime("%Y-%m-%d"), title)
    f = file(filename, "w")
    try:
        f.write(image_data)
    finally:
        f.close()

def main(username, start_from):
    for i, photo_id in enumerate(get_photo_ids(username)):
        current = i + 1
        title = str(current)
        if current < start_from:
            print "Skipping %s." % title
            continue

        sys.stdout.write("Saving %s ... " % title)
        sys.stdout.flush()
        save_photo(title, photo_id)
        print "OK"

if __name__ == '__main__':
    if len(sys.argv) >= 2:
        username = sys.argv[1]
        if len(sys.argv) == 3:
            start_from = int(sys.argv[2])
        else:
            start_from = 1

        if PROXY:
            proxy_handler = urllib2.ProxyHandler({"http" : PROXY})
            if PROXY_USER:
                passwordmgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
                passwordmgr.add_password(None, PROXY, PROXY_USER, PROXY_PASS)
                auth_handler = urllib2.ProxyBasicAuthHandler(passwordmgr)
            else:
                auth_handler = None

            opener = urllib2.build_opener(proxy_handler, auth_handler)
            urllib2.install_opener(opener)

            main(username, start_from)
    else:
        print __doc__
