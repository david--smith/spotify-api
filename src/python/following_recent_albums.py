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

year=2017
playlist_name = "%d-new" % year
playlist_id = spotifier.get_playlist(playlist_name)

if playlist_id == -1:
  print 'ERROR: COULD NOT FIND PLAYLIST "{}"'.format(playlist_name)
else:
  existing_playlist_track_uris = spotifier.get_playlist_tracks(playlist_id)

  albums = spotifier.get_following_recent_albums(year=year, limit=9999)

  albums_deduped = {}
  for album in albums:
    dedupe_key = "%s by %s" % (album['name'], album['artists'][0]['name'])
    if albums_deduped.get(dedupe_key, -1) != -1:
      continue
    albums_deduped[dedupe_key]=1
    print dedupe_key
    song_uris = [track['uri'] for track in album['tracks']['items']][:3]
    # spotifier.delete_tracks_from_playlist(song_uris, playlist_id)
    spotifier.add_tracks_to_playlist(song_uris, playlist_id, existing_playlist_track_uris)
    existing_playlist_track_uris |= set(song_uris)
