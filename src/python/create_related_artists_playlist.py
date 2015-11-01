#!/usr/bin/python

import os
import sys
import re
import datetime
import time
import requests
import spotipy
import spotipy.util as util
import json
import base64
from slugify import slugify
from bs4 import BeautifulSoup

import spotifier


def add_related_tracks_to_playlist(bands, playlist, max_artists, max_songs_per_artist, existing_playlist_songs=[]):
  for band in bands:
    # sleep periodically so as to NOT exced rate limit
    time.sleep(1)
    related_bands = spotifier.fetch_related(band['name'])

    if len(related_bands) > 0:
      for related_band in related_bands[0:max_artists]:
        print 'Related to {}: {}'.format(band['name'].encode('ascii', errors='replace'), related_band['name'].encode('ascii', errors='replace'))
#        if spotifier.follows([related_band['id']])[0]:
#          print 'Already following: {}'.format(related_band)
#          continue
        top_tracks = spotifier.fetch_top_tracks(related_band['id'])
        track_uris = [track['uri'] for track in top_tracks]
        track_uris = track_uris[0:max_songs_per_artist]
        #print "would be adding {} songs".format(len(track_uris))
        spotifier.add_tracks_to_playlist(track_uris, playlist['id'], existing_playlist_songs)
        existing_playlist_songs |= set(track_uris)


band=sys.argv[1]
related_bands = spotifier.fetch_related(band)
if len(related_bands) == 0:
  exit()

# add top tracks for the searched-for band
top_tracks = spotifier.fetch_top_tracks(band, False)
track_uris = [track['uri'] for track in top_tracks]
track_uris = track_uris
spotifier.login_user_to_spotify()
playlist = spotifier.create_playlist('{} RADIO'.format(band))
playlist_songs = set([])
spotifier.add_tracks_to_playlist(track_uris, playlist['id'], playlist_songs)
playlist_songs |= set(track_uris)

band = spotifier.fetch_artist(band)
add_related_tracks_to_playlist(band, playlist, 20, 5, playlist_songs)
add_related_tracks_to_playlist(related_bands, playlist, 4, 3, playlist_songs)

