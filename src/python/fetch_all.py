#!/usr/bin/python

import spotifier
import provider_soma
import provider_wprb
import provider_wxdu
import provider_skinny
import provider_doa
import provider_pitchfork
import provider_blackcat
import provider_dc9

PROVIDERS = [
#  provider_pitchfork,
# provider_wxdu,
#  provider_wprb,
#  provider_doa,
#  provider_soma,
#  provider_skinny,
#  provider_blackcat,
  provider_dc9,
]

spotifier.login_user_to_spotify()

for provider in PROVIDERS:
  playlist_name = provider.get_playlist_name()
  playlist_id, playlist = spotifier.get_playlist(playlist_name)

  if playlist_id == -1:
    print 'ERROR: COULD NOT FIND PLAYLIST "{}"'.format(playlist_name)
    continue

  existing_playlist_track_uris = spotifier.get_playlist_tracks(playlist_id)

  urls = provider.get_urls()
  for url in urls:
    songs, page_title = provider.parse_for_songs(url)
    # for all songs that already have URI defined, grab em
    song_provided_uris = [song['uri'] for song in songs if 'uri' in song]
    spotifier.add_tracks_to_playlist(song_provided_uris, playlist_id, existing_playlist_track_uris)
    existing_playlist_track_uris |= set(song_provided_uris)

    # for all songs that DON'T already have URIs
    songs_without_uris = [song for song in songs if 'uri' not in song]
    for song in songs_without_uris:
      artists = spotifier.fetch_artist(song['artist'])
      artists = [artist for artist in artists if artist['name'].lower() == song['artist'].lower()]
      if len (artists) == 0:
        continue
      follows = spotifier.follows([artists[0]['id']])
      if follows[0]:
        print ('\tALREADY FOLLOWING {}').format (song['artist'])
#        songs_without_uris.remove(song)
    song_and_album_matches = spotifier.get_songs(songs_without_uris)
    song_matches = song_and_album_matches['matches']
    song_uris = [song['uri'] for song in song_matches]
    spotifier.add_tracks_to_playlist(song_uris, playlist_id, existing_playlist_track_uris)
    existing_playlist_track_uris |= set(song_uris)

