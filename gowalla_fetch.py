#!/usr/bin/python

# NOTE: i already deleted my gowalla account, so you will have to get an API key using your own account, since mine is useless now
# USAGE:
# 1. get an API key from https://gowalla.com/api/keys
#  * use http://localhost:8008 as redirect URL for the API key
# 2. replace CLIENT_ID and CLIENT_SECRET in this script with the ones from your own API key
# 3. run the script
#  * you will be prompted to authenticate the app by visiting a URL
#  * all your checkins will pe printed to STDOUT, in JSON format. you will need to redirect the output to a file.

import BaseHTTPServer
import os
import simplejson
import SocketServer
import sys
import time
import urllib
import urllib2

PORT = 8008

CLIENT_ID = "96779fb60aee49189066852806a16144"
CLIENT_SECRET = "542347a4f7454775ae94d94b5f9b2fdb"
REDIRECT_URI = "http://localhost:%s" % PORT

AUTH_CODE = None

class OauthHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self):
        global AUTH_CODE

        params = self.path[self.path.index("?") + 1:]
        params = dict(p.split("=") for p in params.split("&"))

        AUTH_CODE = params['code']

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write("<html><body>done. go back to the script...</body></html>")

def get_access_token():
    global AUTH_CODE

    print "waiting for redirect..."

    httpd = SocketServer.TCPServer(("", PORT), OauthHandler)
    httpd.handle_request()

    print "auth code is %s" % AUTH_CODE
    print "now need to get access token from gowalla..."

    params = urllib.urlencode({'client_id': CLIENT_ID, 'client_secret': CLIENT_SECRET,
                               'grant_type': 'authorization_code',
                               'redirect_uri': REDIRECT_URI,
                               'code': AUTH_CODE})

    response = urllib2.urlopen("https://api.gowalla.com/api/oauth/token", params).read()
    access_token = simplejson.loads(response)['access_token']

    print "access token is %s" % access_token

    with file("access_token", "w") as f:
        f.write(access_token)

    print "saved access token to the file access_token"

if __name__ == '__main__':
    if not os.path.exists('access_token'):
        print "need to authorize the app first!"
        print "visit this URL to authorize: https://gowalla.com/api/oauth/new?client_id=%s&redirect_uri=%s&response_type=code" % (CLIENT_ID, REDIRECT_URI)

        get_access_token()

    with file('access_token') as f:
        access_token = f.read()

    events_url = "http://api.gowalla.com/users/ibz/events?page=%s"
    page = 1

    while True:
        events = simplejson.loads(urllib2.urlopen(urllib2.Request(events_url % page, headers={'Accept': "application/json", 'X-Gowalla-API-Key': CLIENT_ID})).read())['activity']
        if len(events) == 0:
            break
        for event in events:
            print simplejson.dumps(event)
        time.sleep(1)
        page += 1
