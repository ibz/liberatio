#!/usr/bin/python

import datetime
from getopt import getopt
import sys

import pymongo

import path_api
import config

def search_user(name):
    response = path_api.search_user(name)

    for user_id in response['people_ids']:
        user = response['people'][user_id]
        print user_id, user['first_name'], user['last_name']

def get_moments(user_id):
    conn = pymongo.Connection()

    try:
        newer_than = conn.path.moments.find().sort("-created")[0]['created']
    except IndexError:
        newer_than = 0

    older_than = None

    while True:
        has_next = False

        content = path_api.get_moments(user_id, older_than)

        moments = sorted(content['moments'], key=lambda m: m['created'], reverse=True)

        sys.stderr.write("fetched %s moments\n" % len(moments))

        for moment in moments:
            if older_than is None or moment['created'] < older_than:
                older_than = moment['created']
                has_next = True

            if moment['created'] > newer_than:
                conn.path.moments.insert(moment)
            else:
                has_next = False

        for entity_type in ['users', 'places', 'locations', 'music']:
            for entity_id, entity in content[entity_type].iteritems():
                conn.path[entity_type].update({'id': entity_id}, entity, upsert=True)

        if not has_next:
            break

if __name__ == '__main__':
    for opt, val in getopt(sys.argv[1:], "s:m")[0]:
        if opt == "-s":
            search_user(val)
        elif opt == "-m":
            get_moments(config.PATH_USER_ID)
