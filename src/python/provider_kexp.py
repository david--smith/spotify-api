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
  return 'KEXP'

def get_urls():
  urls = ['https://www.kexp.org/charts']
  return urls


def parse_for_songs(url):
  r = requests.get(url)
  soup = BeautifulSoup(r.content)
  trs = soup.find_all('tr')
  songs = []
  for tr in trs:
    row_raw_text = [text for text in tr.stripped_strings]
    index = 0
#    print row_raw_text

    if len(row_raw_text) >=3:
      artist = row_raw_text[1].encode('ascii', errors='replace').strip()
      album = row_raw_text[2].encode('ascii', errors='replace').strip()
      albums = spotifier.fetch_album(album)
      for album in albums:
        if not 'artist' in album:
          continue
        album_artist = album['artist']
        if album_artist.lower() != artist.lower():
          continue
        album_id = album['id']
        tracks = spotifier.get_album_tracks(album_id)
        if len(tracks) < 1:
          continue
        songs.append({'uri': tracks[0]['uri']})
        print "{}: {}".format(album_artist, album['name'])
        break

  page_title = 'KEXP'
  return songs, page_title

##############################################
#urls = get_urls()
#for url in urls:
#  songs, page_title = parse_for_songs(url)
#  print songs
