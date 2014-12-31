#!/usr/bin/python

import ConfigParser
import datetime
import os
import re
import requests
import spotipy
import spotipy.util as util
import json
import base64
from slugify import slugify
from bs4 import BeautifulSoup


def fetch_artist(artist):
  url = 'https://api.spotify.com/v1/search?q={}&type=artist'.format(artist)
  r = requests.get(url)
  r_json = r.json()
  #print json.dumps(r_json['artists']['items'][0])
  artist_matches = [artist_info for artist_info in r_json['artists']['items'] if artist_info['name'].lower() == artist.lower()]
  return artist_matches

def fetch_track(artist, track):
  url = 'https://api.spotify.com/v1/search?q={}&type=track'.format(track)
#  r = requests.get(url, headers=headers)
  r = requests.get(url)
  if r.status_code == 400:
    return []
  r_json = r.json()
  #print json.dumps(r_json)
  track_matches = [track_info for track_info in r_json['tracks']['items'] if track_info['name'].lower() == track.lower() and track_info['artists'][0]['name'].lower() == artist.lower()]
  return track_matches

def fetch_album(artist, album):
  url = 'https://api.spotify.com/v1/search?q={}&type=album'.format(album)
#  r = requests.get(url, headers=headers)
  r = requests.get(url)
  if r.status_code == 400:
    return[]
  r_json = r.json()
#  print '\n'+ json.dumps(r_json) + '\n'
  album_matches = [album_info for album_info in r_json['albums']['items'] if album_info['name'].lower() == album.lower()]
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
    print json.dumps(song, sort_keys=True, indent=2, separators=(',', ': '))
    artist = song['artist']
    track = song['track']
    album = song['album']
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


