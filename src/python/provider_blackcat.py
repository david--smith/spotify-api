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
  return 'BLACKCAT'


def is_band_tag(tag):
  if tag.name != 'h2' and tag.name != 'h1':
    return False
  has_class = 'class' in tag.attrs
  if not has_class:
    return False
  is_headline = 'headline' in tag.attrs['class']
  is_support = 'support' in tag.attrs['class']

  if not is_headline and not is_support:
    return False
  return True


def get_urls():
  urls = list(set(
  [
    'http://www.blackcatdc.com/schedule.html',
  ]))
  return urls


def parse_for_songs(url):
  print 'Getting songs from ', url
  r = requests.get(url)
  soup = BeautifulSoup(r.content)
  band_tags = soup.find_all(is_band_tag)
  songs = []
  for band in band_tags:
    band_name = band.text
    #print band_name
#    artists = spotifier.fetch_artist(band_name)
#    print artists
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

  page_title = 'BLACKCAT'
  return songs, page_title


###############################
#urls = get_urls()
#for url in urls:
#  songs, page_title = parse_for_songs(url)
#  print songs
