#!/usr/bin/env python

__doc__ = """Usage: %s username password""" % __file__

import cookielib
import gzip
import sys
from StringIO import StringIO
import time
import urllib
import urllib2

from lxml.html import parse

jar = cookielib.CookieJar()

try:
    from urlgrabber.keepalive import HTTPHandler
    opener = urllib2.build_opener(HTTPHandler(urllib2.HTTPCookieProcessor(jar)))
except ImportError:
    sys.stderr.write("WARNING: urlgrabber not available. Will not use keepalive.\n")
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(jar))

def parse_xml(url):
    request = urllib2.Request(url, None, {"Accept-encoding": "gzip"})
    response = gzip.GzipFile(fileobj=StringIO(opener.open(request).read()))
    return parse(StringIO(response.read().decode('utf-8'))).getroot()

def scrape_page(url):
    doc = parse_xml(url)
    for row in reversed(doc.cssselect("table.tracklist tr")):
        try:
            artist, title = [a.text.strip() for a in row.cssselect("td.subjectCell a")]
            timestamp = row.cssselect("td.dateCell time")[0].attrib['datetime']
            yield artist, title, timestamp
        except Exception:
            pass

def scrape_user(url):
    doc = parse_xml(url)
    try:
        page_count = int(doc.cssselect("a.lastpage")[0].text)
    except:
        page_count = 1
    for i in reversed(range(1, page_count + 1)):
        sys.stderr.write("page %s/%s...\n" % (i, page_count))
        time.sleep(0.5)
        for artist, title, timestamp in scrape_page("%s?page=%s" % (url, i)):
            yield artist, title, timestamp

def login(username, password):
    opener.open("https://www.last.fm/login", urllib.urlencode([('username', username), ('password', password)]))

def main(username, password):
    login(username, password)

    url = "http://www.last.fm/user/%s/tracks" % username
    for artist, title, timestamp in scrape_user(url):
        sys.stdout.write((u"%s\t%s\t%s\n" % (artist, title, timestamp)).encode("utf-8"))

if __name__ == '__main__':
    if len(sys.argv) == 3:
        username, password = sys.argv[1:]
        main(username, password)
    else:
        print __doc__
