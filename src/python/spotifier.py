#!/usr/bin/python

import ConfigParser
import datetime
import os
import time
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
import http_server_for_callbacks

ACCESS_TOKEN = None
USER_ID = None
REQUEST_HEADERS = None
AUTH_CODE = None


def prettify(json_obj):
  if json_obj == None:
    return {}
  x = json.dumps(json_obj, indent=2, sort_keys=True)
  if x == None:
    x = json.loads(str(json_obj))
    prettify(x)
  return x

def follows(ids, type='artist'):
  url = "https://api.spotify.com/v1/me/following/contains"
  if isinstance(ids, str):
    ids = [ids]
  params = {
    'type': type,
    'ids': ids
  }
  #print 'Asking follow for IDS: {}'.format(ids)
  r = requests.get(url, params=params, headers=REQUEST_HEADERS)
  if r.status_code != 200:
    print 'Error ', r, r.text
    return [False]*len(ids)
  r_json = r.json()
  return r_json


def get_albums_for_artist(artist):
  artists = fetch_artist(artist)
  if len(artists) == 0:
    return []
  albums = []
  for artist in artists:
    artist_id = artist['id']
    url = "https://api.spotify.com/v1/artists/{}/albums".format(artist_id)
    r = requests.get(url, headers=REQUEST_HEADERS)
    if r.status_code != 200:
      return []
    r_json = r.json()
    for album in r_json['items']:
  #    print '\t' + album['name'] + '/' + album['id']
      albums.append(album)
  return albums

def get_album_tracks (album_id):
  url = "https://api.spotify.com/v1/albums/{}/tracks".format(album_id)
  #print '\tLooking up album tracks: ',url
  r = requests.get(url, headers=REQUEST_HEADERS)
  if r.status_code != 200:
    return []
  r_json = r.json()
  return r_json['items']

def get_songs(songs):
  results = {
    'matches':[],
    'albums':[]
  }
  for song in songs:
    artist = song['artist']
    track = song['track']
    album = song['album']
    #artists = fetch_artist(artist)
    tracks = fetch_track(artist, track)
    albums = fetch_album(album)

    if len(tracks) > 0:
      """
      for track_info in tracks:
        name = track_info['name']
        print '\t...found {}'.format(name)
        results['matches'].append({
          'name': name,
          'uri': track_info['uri']
        })
      """
      track_info = tracks[0]
      name = track_info['name']
      print '\t...found {} by {}'.format(
        name.encode('ascii', errors='replace'),
        artist.encode('ascii', errors='replace')
      )
      results['matches'].append({
        'name': name,
        'uri': track_info['uri']
      })

    if len(albums) > 0:
      for album_info in albums:
        results['albums'].append(album_info)
  return results

def create_playlist(playlist_name):
  url = 'https://api.spotify.com/v1/users/{}/playlists'.format(USER_ID)
  data = {
    "name": playlist_name,
    "public": False
  }
  r = requests.post(url, data=json.dumps(data), headers=REQUEST_HEADERS)
  print 'playlist created.'
  return r.json()

def upsert_playlist(playlist_name):
  playlist = get_playlist(playlist_name)
  if playlist is None:
    playlist = create_playlist(playlist_name)
  return playlist

def add_tracks_to_playlist(track_uris, playlist_id, skip_tracks=set([])):
  print 'Adding {} tracks to playlist...'.format(len(track_uris))
  unique_tracks = list(set(track_uris))
  #print '\t...unique tracks in original set: {}'.format(len(unique_tracks))
  tracks_to_add = [track for track in unique_tracks if track not in skip_tracks]
  #print '\t...unique tracks NOT already in playlist: {}'.format(len(tracks_to_add),)
  url = 'https://api.spotify.com/v1/users/{}/playlists/{}/tracks'.format(USER_ID,playlist_id)
  data = {'uris': tracks_to_add}
  r = requests.post(url, data=json.dumps(data), headers=REQUEST_HEADERS)
  #print 'Tracks added.'

def get_userid():
  global USER_ID
  if USER_ID == None:
    url = 'https://api.spotify.com/v1/me'
#    headers = {'Authorization': 'Bearer %s' % ACCESS_TOKEN}
    user = requests.get (url, headers=REQUEST_HEADERS)
    user_json = user.json()
    #print user_json
    USER_ID = user_json['id']
  return USER_ID

def get_playlist_tracks(playlist_id):
  track_uris = set([])
  url = 'https://api.spotify.com/v1/users/{}/playlists/{}/tracks'.format(USER_ID, playlist_id)
  while True:
    r = requests.get(url, headers = REQUEST_HEADERS)
    r_json = r.json()
    if not 'items' in r_json:
      break
    uris = [ song['track']['uri'] for song in r_json['items'] ]
    new_uris = filter(lambda uri: uri not in track_uris, uris)
    track_uris |= set(new_uris)
    url = r_json['next']
    if url == None or len(url.strip())==0:
      break
  return track_uris


def get_playlist(name):
  print 'Looking for playlist {}'.format(name)
  index = 0
  playlist = {}
  playlist_id = -1
  url = 'https://api.spotify.com/v1/users/{}/playlists'.format(USER_ID)
  while playlist_id == -1:
    playlists_raw = requests.get (url, headers=REQUEST_HEADERS)
    playlists_json = playlists_raw.json()
    if not 'items' in playlists_json:
      break
    playlists = playlists_json['items']
    if len(playlists)<1:
      break
    for list in playlists:
      index = index +1
      if index % 100 == 0:
        print '\t...looking for playlist {}: {} scanned so far'.format(name,index)
      if list['name'] == name:
        return list['id'], list
    url = playlists_json['next']
  return playlist_id, playlist

def get_access_token(code):
  global ACCESS_TOKEN, REQUEST_HEADERS
  if ACCESS_TOKEN != None:
    return ACCESS_TOKEN, REQUEST_HEADERS
  CONFIG_FILE='config/settings.ini'
  #print "Config: {} exists? {}".format(CONFIG_FILE, os.path.isfile(CONFIG_FILE))
  Config = ConfigParser.ConfigParser()
  Config.read(CONFIG_FILE)
  client_secret=Config.get('auth','clientSecret')
  client_id=Config.get('auth', 'clientID')
  username=Config.get('auth','user')
  auth_raw = client_id + ':' + client_secret
  auth_encoded = base64.b64encode(auth_raw)
  #print "{} = {}".format(auth_raw, auth_encoded)
  headers = {'Authorization': 'Basic %s' % auth_encoded}
  url = "https://accounts.spotify.com/api/token"
  body = {
    'grant_type': 'authorization_code',
    'code': code,
    'redirect_uri': 'http://127.0.0.1:8000'
  }
  body_data = json.dumps(body)
  print "Getting bearer token..."
  #print "POST {} with:\n{}\nheaders: {}".format(url, body_data, headers)
  r = requests.post(url,data=body, headers=headers)
  #print r.status_code, r.content
  token = r.json()['access_token']
  ACCESS_TOKEN = token
  #print ACCESS_TOKEN
  REQUEST_HEADERS = {'Authorization': 'Bearer %s' % ACCESS_TOKEN, 'Content-Type': 'application/json'}
  print "Obtained bearer token."
  return ACCESS_TOKEN, REQUEST_HEADERS

def login_user_to_spotify():
  global AUTH_CODE
  http_thread = http_server_for_callbacks.HTTPServerThread(1, "Thread-1", 1)
  http_thread.start()
  time.sleep(1)
  CONFIG_FILE='config/settings.ini'
  #print "Config: {} exists? {}".format(CONFIG_FILE, os.path.isfile(CONFIG_FILE))
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
    'redirect_uri': 'http://127.0.0.1:8000',
    'scope':'playlist-modify-public playlist-modify-private playlist-read-private playlist-read-private user-follow-read user-read-private'
  }
  body_data = json.dumps(body)
  auth_raw = client_id + ':' + client_secret
  auth_encoded = base64.b64encode(auth_raw)
  #print "{} = {}".format(auth_raw, auth_encoded)
  headers = {'Authorization': 'Basic %s' % auth_encoded}
  url = "https://accounts.spotify.com/authorize"
  req = Request('GET', url,
    params=body
  )
  prepped_req = req.prepare()
  full_url = prepped_req.url
  #print '----------'
  #print 'GET request to: {}\nWith headers: {}\nWith body: {}'.format(url, headers, body_data)
  #print '\n\n', full_url
  #r = requests.get(url, params=body)
  webbrowser.open(full_url)
  #print '----------'
  while http_thread.AUTH_CODE == None:
    time.sleep(.25)
  print "Obtained auth code..."
  AUTH_CODE = http_thread.AUTH_CODE
  access_token, headers = get_access_token(AUTH_CODE)
  print ("Shutting down HTTP server...")
  http_thread.shutdown()
  get_userid()




def fetch_top_tracks(artist, is_id=False):
  #print 'fetching top tracks for [{}]'.format(artist)
  matches = fetch_artist(artist, is_id)
  if len(matches) == 0:
    print 'No matches for [{}]'.format(artist)
    return []
  if len(matches) > 1:
    print 'Ambiguous artist; please refine search (name or ID) to resolve to single artist.'
    for item in matches:
      print item['name'],item['id']
    return []
  id = matches[0]['id']
  url = 'https://api.spotify.com/v1/artists/{}/top-tracks?country=US'.format(id)
  #print url
  try:
    r = requests.get(url)
    r_json = r.json()
#    print prettify(r_json)
    songs = [{'name':song['name'],'id':song['id'], 'uri':song['uri']} for song in r_json['tracks'] ]
  except:
    print 'PROBLEM! (fetch_top_tracks)', r
    return []
  return songs


def fetch_related(artist, is_id=False):
  matches = fetch_artist(artist, is_id)
  if len(matches) == 0:
    print 'No matches for [{}]'.format(artist)
    return []
  if len(matches) > 1:
    print 'Ambiguous artist; please refine search (name or ID) to resolve to single artist.'
    for item in matches:
      print item['name'],item['id']
    return []
  id = matches[0]['id']
  url = 'https://api.spotify.com/v1/artists/{}/related-artists'.format(id)
  try:
    r = requests.get(url)
    r_json = r.json()
    artist_matches = [{'name':artist_info['name'],'id':artist_info['id']} for artist_info in r_json['artists'] ]
  except:
    print 'PROBLEM! (fetch_related)', r
    return []
  return artist_matches

def fetch_artist(artist, is_id=False):
  if len(artist) == 22:
    is_id = True
    #print 'Artist [{}] is 22 chars; must be an ID, not name?!'.format(artist)
  try:
    if not is_id:
      url = 'https://api.spotify.com/v1/search?q={}&type=artist'.format(artist)
    else:
      url = 'https://api.spotify.com/v1/artists/{}'.format(artist)
  except:
    return []

  r = requests.get(url)
  r_json = r.json()
#  print prettify(r_json)
  try:
    if not is_id:
      artist_matches = [artist_info for artist_info in r_json['artists']['items'] if artist_info['name'].lower() == artist.lower()]
    else:
      artist_matches = [r_json]
  except:
    print 'PROBLEM! fetch_artist()', r
    return []
  return artist_matches

def fetch_track(artist, track):
  try:
    url = 'https://api.spotify.com/v1/search?q={}&type=track'.format(track)
  except:
    return []
  r = requests.get(url)
  if r.status_code == 400:
    return []
  r_json = r.json()
  if 'tracks' not in r_json:
    return []
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


