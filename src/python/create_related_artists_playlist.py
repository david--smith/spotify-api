#!/usr/bin/python

import os
import sys
import re
import datetime
import requests
import spotipy
import spotipy.util as util
import json
import base64
from slugify import slugify
from bs4 import BeautifulSoup

import spotifier

band=sys.argv[1]
bands = spotifier.fetch_related(band)
if len(bands) > 0:
  spotifier.login_user_to_spotify()
  playlist = spotifier.create_playlist('RELATED TO {}'.format(sys.argv[1]))
  #print spotifier.prettify(playlist)

  for band in bands:
    top_tracks = spotifier.fetch_top_tracks(band['id'])
    track_uris = [track['uri'] for track in top_tracks]
    for track in top_tracks:
      print band['name'],'--',track['name']
      spotifier.add_tracks_to_playlist(track_uris, playlist['id'])