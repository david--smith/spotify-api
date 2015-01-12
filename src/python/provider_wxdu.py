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
  return 'WXDU'

def get_urls():
  urls = [
  'http://www.wxdu.org/plmanager/world/currentplaylist.php',
  'http://www.wxdu.org/charts'
  ]
  return urls


def parse_for_songs(url):
  r = requests.get(url)
  soup = BeautifulSoup(r.content)
  trs = soup.find_all('tr')
  songs = []
  for tr in trs:
    song_raw_text = [text for text in tr.stripped_strings]
    if len(song_raw_text) >=4 and song_raw_text[0].strip() != 'Artist':
      song = {
        'artist': song_raw_text[0],
        'track': song_raw_text[1],
        'album': song_raw_text[2]
      }
#      print song['artist'] + ' // ' + song['track'] + ' // ' + song['album']
      songs.append(song)
  page_title = soup.title.text.strip()
#  print 'TITLE: {}'.format(page_title)
  return songs, page_title

