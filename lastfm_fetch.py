#!/usr/bin/env python

__doc__ = """Usage: %s username""" % __file__

import gzip
import sys
from StringIO import StringIO
import time
import urllib2

from lxml.html import parse

try:
    from urlgrabber.keepalive import HTTPHandler
    opener = urllib2.build_opener(HTTPHandler())
except ImportError:
    sys.stderr.write("WARNING: urlgrabber not available. Will not use keepalive.\n")
    opener = urllib2.build_opener()

def parse_xml(url):
    request = urllib2.Request(url, None, {"Accept-encoding": "gzip"})
    response = gzip.GzipFile(fileobj=StringIO(opener.open(request).read()))
    return parse(response).getroot()

def scrape_page(url):
    doc = parse_xml(url)
    for row in reversed(doc.cssselect("table.tracklist tr")):
        try:
            artist, title = [a.text.strip() for a in row.cssselect("td.subjectCell a")]
            timestamp = row.cssselect("td.dateCell abbr")[0].attrib['title']
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
        for artist, title, timestamp in scrape_page("%s?page=%s" % (url, i)):
            yield artist, title, timestamp

def main(username):
    url = "http://last.fm/user/%s/tracks" % username
    for artist, title, timestamp in scrape_user(url):
        sys.stdout.write((u"%s\t%s\t%s\n" % (artist, title, timestamp)).encode("utf-8"))

if __name__ == '__main__':
    if len(sys.argv) == 2:
        username = sys.argv[1]
        main(username)
    else:
        print __doc__
