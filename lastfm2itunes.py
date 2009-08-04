#!/usr/bin/env python

__doc__ = """Usage: %s backup_file""" % __file__

import sys
import time

import appscript

# last.fm trims track titles a little after 80 characters,
# so we need to trim them too when searching or they won't match.
MAX_TITLE_LENGTH = 80

def parse_tracks(fileobj):
    for line in fileobj:
        artist, title, timestamp = line.decode('utf-8').strip().split("\t")
        yield {'artist': artist, 'title': title,
               'timestamp': int(time.mktime(time.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")))}

def group_tracks(tracks):
    grouped_tracks = {}
    for track in tracks:
        artist, title = track['artist'].lower(), track['title'].lower()[:MAX_TITLE_LENGTH]
        if artist not in grouped_tracks:
            grouped_tracks[artist] = {}
        artist_tracks = grouped_tracks[artist]
        if title not in artist_tracks:
            track['playcount'] = 0
            artist_tracks[title] = track
        artist_tracks[title]['playcount'] += 1
    return grouped_tracks

def itunes_set_playcount(tracks):
    sys.stdout.write("Getting track list from iTunes... ")
    sys.stdout.flush()
    itunes_tracks = appscript.app("iTunes").tracks.get()
    print "DONE"

    for track in itunes_tracks:
        artist, title = track.artist.get().lower(), track.name.get().lower()[:MAX_TITLE_LENGTH]
        try:
            playcount = tracks[artist][title]['playcount']
            del tracks[artist][title]
        except KeyError:
            playcount = 0
        print "Processing %s - %s (setting playcount %s -> %s)" % (artist, title, track.played_count.get(), playcount)
        track.played_count.set(playcount)

    print "All done."

def main(filename):
    f = open(filename, "r")
    try:
        sys.stdout.write("Parsing backup file... ")
        sys.stdout.flush()
        tracks = group_tracks(parse_tracks(f))
        print "DONE"
    finally:
        f.close()
    itunes_set_playcount(tracks)

if __name__ == '__main__':
    if len(sys.argv) == 2:
        filename = sys.argv[1]
        main(filename)
    else:
        print __doc__
