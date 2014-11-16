#!/usr/bin/python

import ConfigParser
import os
import requests
import spotipy
import spotipy.util as util
import json
import base64


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
print 'Request to: {}\nWith headers: {}\nWith body: {}'.format(url, headers, body_data)
r = requests.post(url, data=body, headers=headers)
print '----------'
print r.status_code, r.content
r_json = r.json()
print json.dumps(r_json, sort_keys=True, indent=2, separators=(',', ': '))
print r_json['access_token']




    ##################################

#https://developer.spotify.com/web-api/authorization-guide/#client_credentials_flow
  #POST https://accounts.spotify.com/api/token
