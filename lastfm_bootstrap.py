#!/usr/bin/env python

__doc__ = """Usage: %s username password backup_file""" % __file__

import gzip
from md5 import md5
import random
import string
from StringIO import StringIO
import sys
import time
import urllib2

track_template = \
""" <item>
  <artist>%(artist)s</artist>
  <album></album>
  <track>%(title)s</track>
  <duration></duration>
  <timestamp>%(timestamp)s</timestamp>
  <playcount>%(playcount)s</playcount>
  <filename></filename>
  <uniqueID></uniqueID>
  <source>2</source>
  <authorisationKey></authorisationKey>
  <userActionFlags>0</userActionFlags>
  <path></path>
  <fpId></fpId>
  <mbId></mbId>
  <playerId></playerId>
  <mediaDeviceId></mediaDeviceId>
 </item>
"""

def bootstrap(username, password, tracks):
    timestamp = str(int(time.time()))
    auth = md5(md5(password).hexdigest() + timestamp).hexdigest()
    authlower = md5(md5(password).hexdigest().lower() + timestamp).hexdigest().lower()

    buffer = StringIO()
    buffer.write("--AaB03x\r\n")
    buffer.write("content-disposition: form-data; name=\"agency\"\r\n")
    buffer.write("\r\n")
    buffer.write("0\r\n")
    buffer.write("--AaB03x\r\n")
    buffer.write("content-disposition: form-data; name=\"bootstrap\"; filename=\"iTunes_bootstrap.xml.gz\"\r\n")
    buffer.write("Content-Transfer-Encoding: binary\r\n")
    buffer.write("\r\n")
    zip = gzip.GzipFile("iTunes_bootstrap.xml", "w", 6, buffer)
    zip.write("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n")
    zip.write("<bootstrap version=\"1.0\" product=\"iTunes\">\n")
    for track in tracks:
        zip.write(track_template % track)
    zip.write("</bootstrap>\n")
    zip.close()
    buffer.write("\r\n")
    buffer.write("--AaB03x--")
    buffer.seek(0)

    url_template = "http://bootstrap.last.fm/bootstrap/index.php?user=%(username)s&time=%(timestamp)s&auth=%(auth)s&authlower=%(authlower)s"
    url = url_template % {'username': username, 'timestamp': timestamp, 'auth': auth, 'authlower': authlower}

    headers = {"Content-type": "multipart/form-data, boundary=AaB03x", "Cache-Control": "no-cache", "Accept": "*/*"}

    urllib2.urlopen(urllib2.Request(url, buffer.read(), headers))

def prepare_tracks(tracks):
    grouped_tracks = {}
    for track in tracks:
        artist, title = track['artist'], track['title']
        if artist not in grouped_tracks:
            grouped_tracks[artist] = {}
        artist_tracks = grouped_tracks[artist]
        if title not in artist_tracks:
            track['playcount'] = 0
            artist_tracks[title] = track
        artist_tracks[title]['playcount'] += 1
    def iterate():
        for artist_tracks in grouped_tracks.values():
            for track in artist_tracks.values():
                yield track
    return sorted(iterate(), key=lambda t: t['timestamp'])

def parse_tracks(fileobj):
    tracks = []
    for line in fileobj.readlines():
        artist, title, timestamp = line.decode('utf-8').strip().split("\t")
        tracks.append({'artist': artist.encode('utf-8'), 'title': title.encode('utf-8'),
                       'timestamp': int(time.mktime(time.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")))})
    return tracks

def main(username, password, filename):
    f = open(filename, "r")
    try:
        tracks = prepare_tracks(parse_tracks(f))
    finally:
        f.close()
    bootstrap(username, password, tracks)

if __name__ == '__main__':
    if len(sys.argv) == 4:
        username, password, filename = sys.argv[1:]
        main(username, password, filename)
    else:
        print __doc__
