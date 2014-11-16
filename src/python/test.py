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

url = 'http://wprb.com/tpm/world/printplaylist.php?show_id=32977'
r = requests.get(url)
print r.content
regex = re.compile("<td class='mid'.*>.*>(.*)</span>",re.MULTILINE)
regex_result = regex.search(r.content)
print regex.findall(r.content)
print '-----------'
soup = BeautifulSoup(r.content)
trs = soup.find_all('tr')
songs = []
for tr in trs:
  song = [text for text in tr.stripped_strings]
  if len(song) > 0 and song[0] is not 'Artist':
    songs.append(song)
for song in songs:
  print song[0] + ' // ' + song[1] + ' // ' + song[2]
exit()




CONFIG_FILE='config/settings.ini'

print "Config: {} exists? {}".format(CONFIG_FILE, os.path.isfile(CONFIG_FILE))
Config = ConfigParser.ConfigParser()
Config.read(CONFIG_FILE)
client_secret=Config.get('auth','clientSecret')
client_id=Config.get('auth', 'clientID')
username=Config.get('auth','user')

body = {'grant_type': 'client_credentials'}
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
headers = {'Authorization': 'Bearer %s' % token}

artist = 'wolfhounds'
url = 'https://api.spotify.com/v1/search?q={}&type=artist'.format(artist)
r = requests.get(url, headers=headers)
print r.status_code, r.content
print '----------'
r_json = r.json()
print json.dumps(r_json['artists']['items'][0])

    ##################################
