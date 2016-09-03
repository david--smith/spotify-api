#!/usr/bin/env python

import os
import sys
import re
import datetime
import time
import requests
# # import spotipy
# # import spotipy.util as util
import json
import base64
from slugify import slugify
from bs4 import BeautifulSoup

import spotifier


##############################
spotifier.login_user_to_spotify()

playlist_name = '2016-new'
playlist_id = spotifier.get_playlist(playlist_name)

if playlist_id == -1:
  print 'ERROR: COULD NOT FIND PLAYLIST "{}"'.format(playlist_name)
else:
  existing_playlist_track_uris = spotifier.get_playlist_tracks(playlist_id)

  albums = spotifier.get_following_recent_albums(limit=9999)

  for album in albums:
    print "%s by %s" % (album['name'], album['artists'][0]['name'])
    song_uris = [track['uri'] for track in album['tracks']['items']]
    spotifier.add_tracks_to_playlist(song_uris, playlist_id, existing_playlist_track_uris)
    existing_playlist_track_uris |= set(song_uris)



