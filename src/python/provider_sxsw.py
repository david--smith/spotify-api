#!/usr/bin/env python

import os
import string
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

def get_playlist_name():
  return 'SXSW'

def get_urls():
  urls = []
  for x in string.lowercase[:26]:
    urls.append('http://schedule.sxsw.com/?conference=music&lsort=name&day=ALL&event_type=showcase&a='+x)
  return urls


def is_band(tag):
  return tag.name == 'a' and 'class' in tag.attrs and 'link_item' == tag.attrs['class'][0]

def parse_for_songs(url):
  r = requests.get(url)
  soup = BeautifulSoup(r.content)
  band_tags = soup.find_all(is_band)
  songs = []
  bands = []
  for tag in band_tags:
    band_name = tag.text.strip()
    albums = spotifier.get_albums_for_artist(band_name)
    if len(albums) == 0:
      continue
    print '\tBand: {} -- Found {} albums'.format(band_name, len(albums))
    for album in albums:
      tracks = spotifier.get_album_tracks(album['id'])
      if len(tracks) < 1:
        continue
      songs.append({'uri': tracks[0]['uri']})
      break

  page_title = 'SXSW'
  return songs, page_title

##############################################
#urls = get_urls()
#for url in urls:
#  songs, page_title = parse_for_songs(url)
#  print songs
