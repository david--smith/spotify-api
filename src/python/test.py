#!/usr/bin/env python

import ConfigParser
import os
import re
import requests
# import spotipy
# import spotipy.util as util
import json
import base64
from slugify import slugify
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
  url = 'https://api.spotify.com/v1/search?q={}&type=artist'.format(artist)
  r = requests.get(url, headers=headers)
  r_json = r.json()
  #print json.dumps(r_json['artists']['items'][0])
  artist_matches = [artist_info for artist_info in r_json['artists']['items'] if artist_info['name'].lower() == artist.lower()]
  return artist_matches

def fetch_track(artist, track):
  url = 'https://api.spotify.com/v1/search?q={}&type=track'.format(track)
  r = requests.get(url, headers=headers)
  if r.status_code == 400:
    return []
  r_json = r.json()
  #print json.dumps(r_json)
  track_matches = [track_info for track_info in r_json['tracks']['items'] if track_info['name'].lower() == track.lower() and track_info['artists'][0]['name'].lower() == artist.lower()]
  return track_matches

def fetch_album(artist, album):
  url = 'https://api.spotify.com/v1/search?q={}&type=album'.format(album)
  r = requests.get(url, headers=headers)
  if r.status_code == 400:
    return[]
  r_json = r.json()
#  print '\n'+ json.dumps(r_json) + '\n'
  album_matches = [album_info for album_info in r_json['albums']['items'] if album_info['name'].lower() == album.lower()]
  return album_matches

def has_href_printplaylist(tag):
    return tag.name == 'a' and 'printplaylist' in tag['href']

def fetch_wprb_playlists(url, limit=3):
  r = requests.get(url)
  soup = BeautifulSoup(r.content)
  url_tags = soup.find_all(has_href_printplaylist)
  index=0
  for href in url_tags:
    pl_url = 'http://wprb.com/tpm/world/' + href['href']
    print 'fetching playlist @ {}'.format(pl_url)
    fetch_wprb_playlist(pl_url)
    index=index+1
    if index>=limit:
      break

def fetch_wprb_playlist(url):
  #slug = slugify(url)
  #out_filename = './output/{}.html'.format(slug)

  r = requests.get(url)
  regex = re.compile("<td class='mid'.*>.*>(.*)</span>",re.MULTILINE)
  regex_result = regex.search(r.content)
  soup = BeautifulSoup(r.content)
  out_filename = './output/{}.html'.format(soup.title.text)
  trs = soup.find_all('tr')
  songs = []
  for tr in trs:
    song = [text for text in tr.stripped_strings]
    if len(song) > 0 and song[0] != 'Artist':
      songs.append(song)
  f = open(out_filename,'w')
  f.write('<html><body>\n')
  f.write('<a href="{}">{}</a>\n'.format(url, soup.title.text))
  f.write('<p>\n')
  f.write('<table border=1>')
  for song in songs:
    if len(song)<3:
      continue
    artist = song[0]
    track = song[1]
    album = song[2]
    print artist + ' // ' + track + ' // ' + album
    artists = fetch_artist(artist)
    tracks = fetch_track(artist, track)
    albums = fetch_album(artist, album)
    if len(artists) > 0:
      artist_url = ''
      for artist_info in artists:
        artist_url+='<a href="{}">{}</a>&nbsp;&nbsp;'.format(artist_info['uri'], artist_info['name'])
    else:
      artist_url = artist

    if len(tracks) > 0:
      track_url = ''
      for track_info in tracks:
        track_url+='<a href="{}">{}</a>&nbsp;&nbsp;'.format(track_info['uri'], track_info['name'])
    else:
      track_url = track

    album_url = album + '&nbsp;&nbsp;'
    if len(albums) > 0:
      for album_info in albums:
        if 'images' in album_info and len(album_info['images']) > 0:
          img_src = album_info['images'][0]['url']
        else:
          img_src='none!'
        album_url+='<a href="{}"><img src="{}" height="72" width="72"/></a>&nbsp;&nbsp;'.format(album_info['uri'], img_src)

    f.write('<tr align=left valign=top>\n')
    f.write('  <td>' + artist_url + '</td>\n')
    f.write('  <td>' + track_url + '</td>\n')
    f.write('  <td>' + album_url + '</td>\n')
    f.write('</tr>\n')
  f.write('</table>')
  f.write('</body></html>')
  f.close()

######################################################################

token, client_id = login_to_spotify()
headers = {'Authorization': 'Bearer %s' % token}

url = 'http://wprb.com/tpm/world/printplaylist.php?show_id=32977'
#fetch_wprb_playlist(url)

urls = [
  #'http://wprb.com/tpm/world/djplaylists.php?id=65',
#  'http://wprb.com/tpm/world/djplaylists.php?id=530',
#  'http://wprb.com/tpm/world/djplaylists.php?id=90',
#  'http://wprb.com/tpm/world/djplaylists.php?id=383',
#  'http://wprb.com/tpm/world/djplaylists.php?id=8',
  'http://wprb.com/tpm/world/djplaylists.php?id=511',
  'http://wprb.com/tpm/world/djplaylists.php?id=425',
  'http://wprb.com/tpm/world/djplaylists.php?id=435',
  'http://wprb.com/tpm/world/djplaylists.php?id=530',
  'http://wprb.com/tpm/world/djplaylists.php?id=443',
  'http://wprb.com/tpm/world/djplaylists.php?id=415',
  'http://wprb.com/tpm/world/djplaylists.php?id=104',
  'http://wprb.com/tpm/world/djplaylists.php?id=528'
  ]
for url in urls:
  fetch_wprb_playlists(url, limit=5)


url = 'https://api.spotify.com/v1/users/{}/playlists'.format(client_id)
body = {'name': 'foo1'}
headers = {'Authorization': 'Bearer %s' % token, 'Content-Type': 'application/json'}
#r = requests.post(url, data=body, headers=headers)
#print '----------'
#print r.status_code, r.content
#r_json = r.json()
#print json.dumps(r_json, sort_keys=True, indent=2, separators=(',', ': '))


    ##################################
