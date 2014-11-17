#!/usr/bin/python

import ConfigParser
import os
import re
import requests
import spotipy
import spotipy.util as util
import json
import base64

from bs4 import BeautifulSoup

def login_to_spotify():
  CONFIG_FILE='config/settings.ini'
  print "Config: {} exists? {}".format(CONFIG_FILE, os.path.isfile(CONFIG_FILE))
  Config = ConfigParser.ConfigParser()
  Config.read(CONFIG_FILE)
  client_secret=Config.get('auth','clientSecret')
  client_id=Config.get('auth', 'clientID')
  username=Config.get('auth','user')

  ####################
  # Authorization
  ####################
  body = {'grant_type': 'client_credentials', 'scope':'playlist-modify-public playlist-modify-private '}
  body_data = json.dumps(body)
  auth_raw = client_id + ':' + client_secret
  auth_encoded = base64.b64encode(auth_raw)
  print "{} = {}".format(auth_raw, auth_encoded)
  headers = {'Authorization': 'Basic %s' % auth_encoded}
  url = "https://accounts.spotify.com/api/token"
  print '----------'
  print 'POST request to: {}\nWith headers: {}\nWith body: {}'.format(url, headers, body_data)
  r = requests.post(url, data=body, headers=headers)
  print '----------'
  print r.status_code, r.content
  r_json = r.json()
  print json.dumps(r_json, sort_keys=True, indent=2, separators=(',', ': '))
  token=r_json['access_token']
  return token, client_id

def fetch_artist(artist):
  artist = 'wolfhounds'
  url = 'https://api.spotify.com/v1/search?q={}&type=artist'.format(artist)
  r = requests.get(url, headers=headers)
  #print r.status_code, r.content
  #print '----------'
  r_json = r.json()
  #print json.dumps(r_json['artists']['items'][0])
  artist_matches = [artist_info for artist_info in r_json['artists']['items'] if artist_info['name'].lower() == artist.lower()]
  return artist_matches

def fetch_wprb_playlist(url):
  r = requests.get(url)
  #print r.content
  regex = re.compile("<td class='mid'.*>.*>(.*)</span>",re.MULTILINE)
  regex_result = regex.search(r.content)
  #print regex.findall(r.content)
  #print '-----------'
  soup = BeautifulSoup(r.content)
  trs = soup.find_all('tr')
  songs = []
  for tr in trs:
    song = [text for text in tr.stripped_strings]
    if len(song) > 0 and song[0] is not 'Artist':
      songs.append(song)

  f = open('./output/test.html','w')
  f.write('<html><body>\n')
  f.write('<table border=1>')
  for song in songs:
    artist = song[0]
    track = song[1]
    album = song[2]
    print artist + ' // ' + track + ' // ' + album
    f.write('<tr align=left valign=top>\n')
    f.write('  <td>' + artist + '</td>\n')
    f.write('  <td>' + track + '</td>\n')
    f.write('  <td>' + album + '</td>\n')
    f.write('</tr>\n')
  f.write('</table>')
  f.write('</body></html>')
  f.close()

######################################################################

token, client_id = login_to_spotify()
headers = {'Authorization': 'Bearer %s' % token}

url = 'http://wprb.com/tpm/world/printplaylist.php?show_id=32977'
fetch_wprb_playlist(url)

wolves = fetch_artist('wolfhounds')
wolf = wolves[0]
print wolf['name'] + ' == ' + wolf['uri']
print json.dumps(wolf, sort_keys=True, indent=2, separators=(',', ': '))


url = 'https://api.spotify.com/v1/users/{}/playlists'.format(client_id)
body = {'name': 'foo1'}
headers = {'Authorization': 'Bearer %s' % token, 'Content-Type': 'application/json'}
r = requests.post(url, data=body, headers=headers)
print '----------'
print r.status_code, r.content
r_json = r.json()
print json.dumps(r_json, sort_keys=True, indent=2, separators=(',', ': '))


    ##################################
