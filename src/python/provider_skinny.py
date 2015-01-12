#!/usr/bin/python

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
  return 'SKINNY'


def is_review_title(tag):
    #h2 class="title item fn"
    return tag.name == 'h2' #and 'title item fn' in tag['class']

def get_urls():
  urls = [
  'http://www.theskinny.co.uk/music/records',
  'http://www.theskinny.co.uk/music/records/page:2',
  'http://www.theskinny.co.uk/music/records/page:3',
  ]
  return urls


def parse_for_songs(url):
  songs = []
  page_title = 'skinny'
  print 'Getting songs from ', url
  r = requests.get(url)
  soup = BeautifulSoup(r.content)
  title_tags = soup.find_all(is_review_title)
  for title in title_tags:
    title_text = [text for text in title.stripped_strings]
    regex = re.compile(ur'^(.*)\u2013(.*)$')
    matches = regex.findall(title_text[0])
    artist = matches[0][0].strip()
    album = matches[0][1].strip()
    print artist, '>', album
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
  return songs, page_title

###########################
#spotifier.login_user_to_spotify()
#urls = get_urls()
#for url in urls:
#  parse_for_songs(url)
