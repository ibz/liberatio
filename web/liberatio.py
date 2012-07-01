#!/usr/bin/python

import datetime
import json
import pymongo
import web

urls = ('/', 'Index')

class Index:
    def GET(self):
        conn = pymongo.Connection()
        moments = list(conn.path.moments.find())
        for moment in moments:
            moment['created_s'] = datetime.datetime.fromtimestamp(moment['created']).strftime("%Y-%m-%d %H:%M:%S")
        return web.template.frender("templates/index.html")(moments)

if __name__ == "__main__": 
    app = web.application(urls, globals())
    app.run()
