#!/usr/bin/python

# USAGE:
# 1. run fetch_gowalla.py first, to save your checkins to JSON
# 2. run this script, passing the JSON file as an argument
# * it will display all checkins in the JSON file in an easy to read format
# * it will fetch all photos associated to checkins and save them

import simplejson
import sys
import urllib2

with file(sys.argv[1]) as f:
    for line in f:
        try:
            event = simplejson.loads(line)
        except Exception:
            print "invalid JSON: %s" % line
        print event['created_at'], event['spot']['name'], event['spot']['url'], "|", event['message']
        for photo in event.get('_photos', []):
            photo_urls = [photo['photo_urls'][u] for u in photo['photo_urls'] if u.startswith('high_res')]
            with file(event['url'][event['url'].index('/') + 1:] + ".jpg", "w") as f:
                photo = urllib2.urlopen(photo_urls[0]).read()
                f.write(photo)
