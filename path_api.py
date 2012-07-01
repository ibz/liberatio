import base64
import biplist
import urllib
import urllib2

import config

def call(url):
    headers = {'User-Agent': "Path/2.1.2 CFNetwork/548.0.4 Darwin/11.0.0", 'Accept': "*/*",
               'Accept-Charset': "utf-8", 'Accept-Language': "en-us", 'Accept-Encoding': "gzip, deflate",
               'X-PATH-CLIENT': "iOS/2.1.2", 'X-PATH-TIMEZONE': "UTC", 'X-PATH-LOCALE': "en_US", 'X-PATH-LANGUAGE': "en",
               'Authorization': "Basic %s" % base64.encodestring("%s:%s" % (config.PATH_USERNAME, config.PATH_PASSWORD)).strip()}

    response = urllib2.urlopen(urllib2.Request(url, headers=headers)).read()

    return biplist.readPlistFromString(response)

def search_user(name):
    return call("https://api.path.com/3/user/search?%s" % urllib.urlencode({'query': name}))

def get_moments(user_id, older_than):
    url = "https://api.path.com/3/moment/feed?user_id=%s" % user_id
    if older_than is not None:
        url = "%s&older_than=%s" % (url, older_than)

    return call(url)
