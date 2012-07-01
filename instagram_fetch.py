#!/usr/bin/python

from getopt import getopt
import simplejson
import sys
import urllib
import urllib2

CLIENT_ID = "e322b6feae104fa9b9c714bb54fb6519"
REDIRECT_URI = "http://ibz.me"
CLIENT_SECRET = "a4eb2d7c8ac14c15b0ddabac0761d4ca"

ACCESS_TOKEN = "381694.e322b6f.af3cca764da74ca9ab24d1526ca6913b"

def fetch(url):
    while url:
        page = simplejson.loads(urllib2.urlopen(url).read())

        for picture in page['data']:
            print simplejson.dumps(picture)

        url = page.get('pagination', {}).get('next_url')

        sys.stderr.write("%s\n" % url)

if __name__ == '__main__':
    if ACCESS_TOKEN is None:
        print "Visit this URL: https://api.instagram.com/oauth/authorize/?client_id=%s&redirect_uri=%s&response_type=code" % (CLIENT_ID, REDIRECT_URI)
        code = raw_input("Code: ")

        params = urllib.urlencode({'client_id': CLIENT_ID, 'client_secret': CLIENT_SECRET,
                                   'grant_type': 'authorization_code',
                                   'redirect_uri': REDIRECT_URI,
                                   'code': code})
        try:
            print urllib2.urlopen("https://api.instagram.com/oauth/access_token", params).read()
        except urllib2.HTTPError, e:
            sys.stderr.write("%s\n" % e.read())

    for opt, val in getopt(sys.argv[1:], "sl")[0]:
        if opt == "-s":
            fetch("https://api.instagram.com/v1/users/self/media/recent/?access_token=%s" % ACCESS_TOKEN)
        elif opt == "-l":
            fetch("https://api.instagram.com/v1/users/self/media/liked/?access_token=%s" % ACCESS_TOKEN)
