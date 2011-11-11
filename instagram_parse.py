#!/usr/bin/python

import simplejson
import sys
import urllib2

if __name__ == '__main__':
    with file(sys.argv[1]) as f:
        for i, line in enumerate(f, 1):
            print i
            picture = simplejson.loads(line)
            with file("inst_pics/%s.jpg" % picture['id'], "w") as f:
                content = urllib2.urlopen(picture['images']['low_resolution']['url']).read()
                f.write(content)
