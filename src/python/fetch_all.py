#!/usr/bin/python

import spotifier
import provider_soma

PROVIDERS = [provider_soma]

spotifier.login_user_to_spotify()

for provider in PROVIDERS:
  playlist_name = provider.get_playlist_name()
  playlist_id, playlist = spotifier.get_playlist(playlist_name)
  if playlist_id == -1:
    print 'ERROR: COULD NOT FIND PLAYLIST "{}"'.format(playlist_name)
    continue

  urls = provider.get_urls()
  for url in urls:
    songs, page_title = provider.parse_for_songs(url)
    song_and_album_matches = spotifier.get_songs(songs)
    song_matches = song_and_album_matches['matches']
    song_uris = [song['uri'] for song in song_matches]
    spotifier.add_tracks_to_playlist(song_uris, playlist_id)


