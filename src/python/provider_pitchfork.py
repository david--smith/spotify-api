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
  return 'PITCHFORK'


def is_review(tag):
  if tag.name != 'a':
    return False
  return '/reviews/albums' in tag.attrs['href'].encode('ascii', errors='replace')

def get_urls():
  urls = list(set(
  ['http://pitchfork.com/reviews/albums/',
  'http://pitchfork.com/reviews/albums/2/',
  'http://pitchfork.com/reviews/albums/3/',
  'http://pitchfork.com/reviews/albums/4/',
  'http://pitchfork.com/reviews/albums/5/',
  ]))

  return urls


def parse_for_songs(url):
  songs = []
  print 'Getting songs from ', url
  r = requests.get(url)
  soup = BeautifulSoup(r.content)
  title_tags = soup.find_all(href=re.compile("/reviews/albums"))
  for title_tag in title_tags:
      matches = [text for text in title_tag.stripped_strings]
      if len(matches)<2:
        continue
      artist = matches[0].encode('ascii', errors='replace').strip()
      album = matches[1].encode('ascii', errors='replace').strip()
#      print '\t', 'FOUND:', artist, '>', album
      albums = spotifier.fetch_album(album)
      for album in albums:
        """
        if not 'artist' in album:
          print "%s does NOT have key 'artist'" % str(album)
          continue
        album_artist = album['artist']
        if album_artist.lower() != artist.lower():
          continue
        """
        album_id = album['id']
        tracks = spotifier.get_album_tracks(album_id)
        if len(tracks) < 1:
          continue
        songs.append({'uri': tracks[0]['uri']})
        print "{}: {}".format(artist, album['name'])
        break
  page_title = 'PITCHFORK'
  return songs, page_title


###############################
#urls = get_urls()
#for url in urls:
#  songs, page_title = parse_for_songs(url)
#  print songs


