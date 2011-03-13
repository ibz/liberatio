#!/usr/bin/env python

__doc__ = """Usage: %s user_id""" % __file__

from datetime import datetime
import sys
import urllib
import urllib2
from xml.dom import minidom

FLICKR_KEY = "YOUR_API_KEY_HERE"

def call(method, **params):
    response = urllib2.urlopen("http://flickr.com/services/rest?api_key=%s&method=%s&%s"
                               % (FLICKR_KEY, method, urllib.urlencode(params)))
    try:
        return minidom.parse(response)
    finally:
        response.close()

def get_photos(user_id):
    dom = call('flickr.photos.search', user_id=user_id, sort="date-posted-asc", per_page=500)
    photos = [{'id': int(node.getAttribute('id')),
               'title': node.getAttribute('title')}
              for node in dom.getElementsByTagName('photo')]

    for photo in photos:
        dom = call('flickr.photos.getInfo', photo_id=photo['id'])
        date_taken = datetime.strptime(dom.getElementsByTagName('dates')[0].getAttribute('taken')[:10], "%Y-%m-%d")
        photo['date_taken'] = date_taken

        dom = call('flickr.photos.getSizes', photo_id=photo['id'])
        for size in dom.getElementsByTagName('size'):
            if size.getAttribute('label') == "Large":
                photo['url'] = size.getAttribute('source')
                yield photo
                break

def save_photo(photo):
    response = urllib2.urlopen(photo['url'])
    try:
        f = file("%s %s.jpg" % (photo['date_taken'].strftime("%Y-%m-%d"), photo['title']), "w")
        try:
            f.write(response.read())
        finally:
            f.close()
    finally:
        response.close()

def main(user_id):
    sys.stdout.write("Getting photo list ... ")
    sys.stdout.flush()
    photos = get_photos(user_id)
    print "OK"
    for i, photo in enumerate(photos):
        sys.stdout.write("Saving %s. %s ... " % (i + 1, photo['title']))
        sys.stdout.flush()
        save_photo(photo)
        print "OK"

if __name__ == '__main__':
    if len(sys.argv) == 2:
        user_id = sys.argv[1]
        main(user_id)
    else:
        print __doc__
