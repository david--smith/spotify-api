#!/usr/bin/env python



# http://www.adequacy.net/category/reviews/
import os
import re
import datetime
import requests
# # import spotipy
# # import spotipy.util as util
import json
import base64
from slugify import slugify
from bs4 import BeautifulSoup

import spotifier

WEEKS_TO_GO_BACK = 2

def get_playlist_name():
  return 'DOA'


def is_entry_title(tag):
  if tag.name != 'h2':
    return False
  has_class = 'class' in tag.attrs
  if not has_class:
    return False
  return 'entry-title' in tag.attrs['class']

def get_urls():
  urls = list(set(
  ['http://www.adequacy.net/category/reviews/',
  'http://www.adequacy.net/category/reviews/page/2/',
  'http://www.adequacy.net/category/reviews/page/3/',
  'http://www.adequacy.net/category/reviews/page/4/',
  'http://www.adequacy.net/category/reviews/page/5/',
  'http://www.adequacy.net/category/reviews/page/6/',
  'http://www.adequacy.net/category/reviews/page/7/',
  'http://www.adequacy.net/category/reviews/page/8/',
  'http://www.adequacy.net/category/reviews/page/9/',
  'http://www.adequacy.net/category/reviews/page/10/',
  'http://www.adequacy.net/category/reviews/page/11/',
  'http://www.adequacy.net/category/reviews/page/12/',
  'http://www.adequacy.net/category/reviews/page/13/',
  'http://www.adequacy.net/category/reviews/page/14/',
  'http://www.adequacy.net/category/reviews/page/15/',
  'http://www.adequacy.net/category/reviews/page/16/',
  'http://www.adequacy.net/category/reviews/page/17/',
  'http://www.adequacy.net/category/reviews/page/18/',
  'http://www.adequacy.net/category/reviews/page/19/',
  'http://www.adequacy.net/category/reviews/page/20/',
  ]))

  return urls


def parse_for_songs(url):
  print 'Getting songs from ', url
  r = requests.get(url)
  soup = BeautifulSoup(r.content)
  title_tags = soup.find_all(is_entry_title)
  regex = re.compile(ur'^(.*)\u2013(.*)$')
  for title in title_tags:
    title_text = title.a.text
    matches = regex.findall(title_text)
    if len(matches) == 0 or len(matches[0])<2:
      print '\tno matches...?', matches
      continue
    artist = matches[0][0].strip()
    album = matches[0][1].strip()
    if album.lower() == 's/t' or album.lower() == 'self-titled':
      album = artist
#    print '\t', 'FOUND:', artist, '>', album
  songs = []
  albums = spotifier.fetch_album(album)
  for album in albums:
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

  page_title = 'DOA'
  return songs, page_title


###############################
#urls = get_urls()
#for url in urls:
#  songs, page_title = parse_for_songs(url)
#  print songs
