#!/usr/bin/env python

import os
import re
import datetime
import requests
# import spotipy
# import spotipy.util as util
import json
import base64
from slugify import slugify
from bs4 import BeautifulSoup

import spotifier

def get_playlist_name():
  return 'VELVET_LOUNGE'


def get_urls():
  urls = list(set(
  [
    'http://velvetloungedc.com/',
  ]))
  return urls


def is_band_tag(tag):
  if tag.name != 'h2' and tag.name != 'span':
    return False
  has_class = 'class' in tag.attrs
  if not has_class:
    return False
  is_headline = 'summary' in tag.attrs['class']
  is_support = 'support' in tag.attrs['class']

  if not is_headline and not is_support:
    return False
  return True


def parse_for_songs(url):
  print 'Getting songs from ', url
  r = requests.get(url)
  soup = BeautifulSoup(r.content)
  band_tags = soup.find_all(is_band_tag)
  songs = []
  for band in band_tags:
    band_text = band.text.strip()
    band_names = band_text.split(',')
    for band_name in band_names:
      #print band_name
      band_name = band_name.strip()
      albums = spotifier.get_albums_for_artist(band_name)
      if len(albums) == 0:
        continue
      print 'Band: {} -- Found {} albums'.format(band_name, len(albums))
      for album in albums:
        tracks = spotifier.get_album_tracks(album['id'])
        if len(tracks) < 1:
          continue
        songs.append({'uri': tracks[0]['uri']})
        break

  page_title = 'VELVET_LOUNGE'
  return songs, page_title


###############################
#urls = get_urls()
#for url in urls:
#  songs, page_title = parse_for_songs(url)
  #print songs
