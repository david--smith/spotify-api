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
for band in bands:
  top_tracks = spotifier.fetch_top_tracks(band['id'])
  for track in top_tracks:
    print band['name'],'--',track['name']

#print bands
#spotifier.login_user_to_spotify()
