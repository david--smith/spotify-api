#!/usr/bin/python



# http://www.adequacy.net/category/reviews/
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
  ]))

  return urls


def parse_for_songs(url):
  print 'Getting songs from ', url
  r = requests.get(url)
  soup = BeautifulSoup(r.content)
  title_tags = soup.find_all(is_entry_title)
  for title in title_tags:
    print title
  songs = []
#  for tr in trs:
#    song = [text for text in tr.stripped_strings]
#    if len(song) >= 3 and song[0] != 'Artist':
#      artist = song[0]
#      track = song[1]
#      album = song[2]
#      songs.append({
#        'artist': artist,
#        'track': track,
#        'album': album
#      })
  #page_title = soup.title.text.strip()
  page_title = 'DOA'
  return songs, page_title


###############################
urls = get_urls()
for url in urls:
  songs, page_title = parse_for_songs(url)
