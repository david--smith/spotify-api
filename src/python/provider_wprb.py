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
  return 'WPRB'


def has_href_printplaylist(tag):
    return tag.name == 'a' and 'printplaylist' in tag['href']

def get_urls():
  urls = []
  show_history_urls = [
  'http://wprb.com/tpm/world/djplaylists.php?id=511',
  'http://wprb.com/tpm/world/djplaylists.php?id=425',
  'http://wprb.com/tpm/world/djplaylists.php?id=435',
  'http://wprb.com/tpm/world/djplaylists.php?id=530',
  'http://wprb.com/tpm/world/djplaylists.php?id=443',
  'http://wprb.com/tpm/world/djplaylists.php?id=415',
  'http://wprb.com/tpm/world/djplaylists.php?id=104',
  'http://wprb.com/tpm/world/djplaylists.php?id=528'
  ]
  for url in show_history_urls:
    r = requests.get(url)
    soup = BeautifulSoup(r.content)
    url_tags = soup.find_all(has_href_printplaylist)
    index=0
    for href in url_tags:
      pl_url = 'http://wprb.com/tpm/world/' + href['href']
      urls.append(pl_url)
      index = index +1
      if index > WEEKS_TO_GO_BACK:
        break

  return urls


def parse_for_songs(url):
  print 'Getting songs from ', url
  r = requests.get(url)
  regex = re.compile("<td class='mid'.*>.*>(.*)</span>",re.MULTILINE)
  regex_result = regex.search(r.content)
  soup = BeautifulSoup(r.content)
  trs = soup.find_all('tr')
  songs = []
  for tr in trs:
    song = [text for text in tr.stripped_strings]
    if len(song) >= 3 and song[0] != 'Artist':
      artist = song[0]
      track = song[1]
      album = song[2]
      songs.append({
        'artist': artist,
        'track': track,
        'album': album
      })
  page_title = soup.title.text.strip()
  return songs, page_title


