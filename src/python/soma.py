#!/usr/bin/python

import ConfigParser
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

def parse_for_songs(url):
  r = requests.get(url)
  soup = BeautifulSoup(r.content)
  trs = soup.find_all('tr')
  songs = []
  for tr in trs:
    song_raw_text = [text for text in tr.stripped_strings]
    if len(song_raw_text) >=4 and song_raw_text[1].strip() != 'Artist':
      song = {'artist': song_raw_text[1], 'track': song_raw_text[2], 'album': song_raw_text[3]}
#      print song['artist'] + ' // ' + song['track'] + ' // ' + song['album']
      songs.append(song)
  page_title = soup.title.text.strip()
#  print 'TITLE: {}'.format(page_title)
  return songs, page_title



##########################################################################

urls = ['http://somafm.com/secretagent/songhistory.html',
'http://somafm.com/sonicuniverse/songhistory.html',
'http://somafm.com/dronezone/songhistory.html',
'http://somafm.com/groovesalad/songhistory.html',
'http://somafm.com/indiepop/songhistory.html',
'http://somafm.com/spacestation/songhistory.html',
'http://somafm.com/digitalis/songhistory.html',
'http://somafm.com/earwaves/songhistory.html',
'http://somafm.com/missioncontrol/songhistory.html',
'http://somafm.com/u80s/songhistory.html',
'http://somafm.com/illstreet/songhistory.html',
'http://somafm.com/deepspaceone/songhistory.html',
'http://somafm.com/suburbsofgoa/songhistory.html',
'http://somafm.com/doomed/songhistory.html']
for url in urls:
  songs, title = parse_for_songs(url)
  spotifier.output_songs(url, title, songs)



