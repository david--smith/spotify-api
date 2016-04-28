#!/usr/bin/env python

import os
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
  return 'CATS_CRADLE'


def is_band_tag(tag):
  if tag.name != 'a':
    return False
  return '/event/' in tag['href']


def get_urls():
  urls = list(set(
  [
    'http://www.catscradle.com/events/',
  ]))
  return urls


def parse_for_songs(url):
  print 'Getting songs from ', url
  r = requests.get(url)
  soup = BeautifulSoup(r.content)
  band_tags = soup.find_all(is_band_tag)
  songs = []
  for band in band_tags:
#    print band
    band_name_raw = band.text
    if band_name_raw == 'Tickets' or band_name_raw =='More Info':
      continue
    band_names = [name.strip() for name in band_name_raw.split(',')]
#    artists = spotifier.fetch_artist(band_name)
#    print artists
    for band_name in band_names:
      print band_name
      albums = spotifier.get_albums_for_artist(band_name)
      if len(albums) == 0:
        continue
  #    print 'Found {} albums'.format(len(albums))
      for album in albums:
        tracks = spotifier.get_album_tracks(album['id'])
        if len(tracks) < 1:
          continue
        songs.append({'uri': tracks[0]['uri']})
        break

  page_title = 'CATSCRADLE'
  return songs, page_title


###############################
#urls = get_urls()
#for url in urls:
#  songs, page_title = parse_for_songs(url)
#  print songs
