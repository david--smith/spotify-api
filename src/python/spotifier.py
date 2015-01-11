#!/usr/bin/python

import ConfigParser
import datetime
import os
import re
import spotipy
import spotipy.util as util
import json
import base64
from slugify import slugify
from bs4 import BeautifulSoup
import webbrowser

import requests
from requests import Request, Session

ACCESS_TOKEN = None
USER_ID = None
REQUEST_HEADERS = None

def get_userid():
  global USER_ID
  url = 'https://api.spotify.com/v1/me'
  headers = headers = {'Authorization': 'Bearer %s' % ACCESS_TOKEN}
  user = requests.get (url, headers=headers)
  user_json = user.json()
  print user_json
  USER_ID = user_json['id']
  return USER_ID

def get_playlist(name):
  url = 'https://api.spotify.com/v1/users/{}/playlists'.format(USER_ID)
  params = {'limit': 20}
  playlists = requests.get (url, params=params, headers=REQUEST_HEADERS)
  playlists_json = playlists.json()
  #print json.dumps(playlists_json, sort_keys=True, indent=2, separators=(',', ': '))
  for list in playlists_json['items']:
    print list['name']
    if list['name'] == name:
      return list['id'], list
  return {}

def get_access_token(code):
  global ACCESS_TOKEN, REQUEST_HEADERS
  CONFIG_FILE='config/settings.ini'
  print "Config: {} exists? {}".format(CONFIG_FILE, os.path.isfile(CONFIG_FILE))
  Config = ConfigParser.ConfigParser()
  Config.read(CONFIG_FILE)
  client_secret=Config.get('auth','clientSecret')
  client_id=Config.get('auth', 'clientID')
  username=Config.get('auth','user')
  auth_raw = client_id + ':' + client_secret
  auth_encoded = base64.b64encode(auth_raw)
  print "{} = {}".format(auth_raw, auth_encoded)
  headers = {'Authorization': 'Basic %s' % auth_encoded}
  url = "https://accounts.spotify.com/api/token"
  body = {
    'grant_type': 'authorization_code',
    'code': code,
    'redirect_uri': 'http://localhost:8000/'
  }
  body_data = json.dumps(body)
  print "\n\nGetting bearer token"
  print "POST {} with:\n{}\nheaders: {}".format(url, body_data, headers)
  r = requests.post(url,data=body, headers=headers)
  print r.status_code, r.content
  token = r.json()['access_token']
  ACCESS_TOKEN = token
  print ACCESS_TOKEN
  REQUEST_HEADERS = {'Authorization': 'Bearer %s' % ACCESS_TOKEN}
  return ACCESS_TOKEN, REQUEST_HEADERS

def login_user_to_spotify():
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
  body = {
    'client_id': client_id,
    'response_type': 'code',
    'redirect_uri': 'http://localhost:8000/',
    'scope':'playlist-modify-public playlist-modify-private playlist-read-private '
  }
  body_data = json.dumps(body)
  auth_raw = client_id + ':' + client_secret
  auth_encoded = base64.b64encode(auth_raw)
  print "{} = {}".format(auth_raw, auth_encoded)
  headers = {'Authorization': 'Basic %s' % auth_encoded}
  url = "https://accounts.spotify.com/authorize"
  req = Request('GET', url,
    params=body
  )
  prepped_req = req.prepare()
  full_url = prepped_req.url
  print '----------'
  print 'GET request to: {}\nWith headers: {}\nWith body: {}'.format(url, headers, body_data)
  print '\n\n', full_url
  #r = requests.get(url, params=body)
  webbrowser.open(full_url)
  print '----------'
#  print r.status_code, r.content
#  r_json = r.json()
#  print json.dumps(r_json, sort_keys=True, indent=2, separators=(',', ': '))
#  token=r_json['access_token']
#  return token, client_id


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
  try:
    url = 'https://api.spotify.com/v1/search?q={}&type=artist'.format(artist)
  except:
    return []

  r = requests.get(url)
  r_json = r.json()
  try:
    artist_matches = [artist_info for artist_info in r_json['artists']['items'] if artist_info['name'].lower() == artist.lower()]
  except:
    return []
  return artist_matches

def fetch_track(artist, track):
  try:
    url = 'https://api.spotify.com/v1/search?q={}&type=track'.format(track)
  except:
    return []
#  r = requests.get(url, headers=headers)
  r = requests.get(url)
  if r.status_code == 400:
    return []
  r_json = r.json()
  track_matches = [track_info for track_info in r_json['tracks']['items'] if track_info['name'].lower() == track.lower() and track_info['artists'][0]['name'].lower() == artist.lower()]
  return track_matches

def fetch_album(album):
  try:
    url = 'https://api.spotify.com/v1/search?q={}&type=album'.format(album)
  except:
    return []
#  r = requests.get(url, headers=headers)
  r = requests.get(url)
  if r.status_code == 400:
    return[]
  r_json = r.json()
  album_matches = [album_info for album_info in r_json['albums']['items'] if album_info['name'].lower() == album.lower()]
  for album in album_matches:
    url = album['href']
    r = requests.get(url)
    r_json = r.json()
    album['artist'] = r_json['artists'][0]['name']
  return album_matches


def output_songs(url, title, songs, out_filename=None):
  if out_filename == None:
    out_filename = out_filename = './output/{}-{}.html'.format(title,datetime.date.today())
  f = open(out_filename,'w')
  f.write('<html><body>\n')
  f.write('<a href="{}">{}</a>\n'.format(url, title))
  f.write('<p>\n')
  f.write('<table border=1>')
  for song in songs:
#    print json.dumps(song, sort_keys=True, indent=2, separators=(',', ': '))
    artist = song['artist']
    track = song['track']
    album = song['album']
    print title + ': ' + artist + ' // ' + track + ' // ' + album
    artists = fetch_artist(artist)
    tracks = fetch_track(artist, track)
    albums = fetch_album(album)
    if len(artists) > 0:
      artist_url = ''
      for artist_info in artists:
        artist_url+='<a href="{}">{}</a>&nbsp;&nbsp;'.format(artist_info['uri'], artist_info['name'])
    else:
      artist_url = artist

    if len(tracks) > 0:
      track_url = ''
      for track_info in tracks:
        track_url+='<a href="{}">{}</a>&nbsp;&nbsp;'.format(
          track_info['uri'].encode('ascii', errors='replace'),
          track_info['name'].encode('ascii', errors='replace'))
    else:
      track_url = track

    album_url = album + '&nbsp;&nbsp;'
    if len(albums) > 0:
      for album_info in albums:
        if 'images' in album_info and len(album_info['images']) > 0:
          img_src = album_info['images'][0]['url']
        else:
          img_src='none!'
        try:
          album_url+="""<a href="{}">
          <figure>
            <img src="{}" height="72" width="72"/>
            <figcaption>by {}</figcaption>
          </figure>
          </a>&nbsp;&nbsp;""".format(album_info['uri'].encode('ascii', 'replace'),
            img_src,
            album_info['artist'].encode('ascii', errors='replace'))
        except:
          album_url='NONE'

    f.write('<tr align=left valign=top>\n')
    f.write('  <td>' + artist_url.encode('ascii', errors='replace') + '</td>\n')
    f.write('  <td>' + track_url.encode('ascii', errors='replace') + '</td>\n')
    f.write('  <td>' + album_url.encode('ascii', errors='replace') + '</td>\n')
    f.write('</tr>\n')
  f.write('</table>')
  f.write('</body></html>')
  f.close()


