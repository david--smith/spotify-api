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
  return 'COMET'


def get_urls():
  urls = list(set(
  [
    'http://www.sashalordpresents.com/upcoming-events',
  ]))
  return urls


def is_band_tag(tag):
  if tag.name != 'div':
    return False
  has_class = 'class' in tag.attrs
  if not has_class:
    return False
  is_headline = 'summary-title' in tag.attrs['class']
  is_support = '!!!' in tag.attrs['class']

  if not is_headline and not is_support:
    return False
  return True


def parse_for_songs(url):
  print 'Getting songs from ', url
  r = requests.get(url)
  soup = BeautifulSoup(r.content)
  band_tags = soup.find_all(is_band_tag)
  songs = []
  cleaned_band_names = []
  for band in band_tags:
    band_text = band.text.strip()
    band_names = band_text.split(',')
    cleaned_band_names.extend(band_names)
    for band_name in band_names:
      band_name = band_name.strip()
      if band_name.startswith('and '):
        band_name = band_name[4:]
      band_name = band_name.replace('(Record Release)', '')
      band_name = band_name.strip()
      cleaned_band_names.append(band_name)
      more_names = band_name.split('w/')
      for new_one in more_names:
        cleaned_band_names.append(new_one)
        #print '\t' + new_one

  for band_name in set(cleaned_band_names):
    band_name = band_name.strip()
    #print band_name
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

  page_title = 'COMET'
  return songs, page_title


###############################
#urls = get_urls()
#for url in urls:
#  songs, page_title = parse_for_songs(url)
  #print songs
