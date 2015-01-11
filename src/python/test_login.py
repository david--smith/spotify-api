#!/usr/bin/python

import socket
import spotifier
import sys
import BaseHTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
from multiprocessing import Process
import time
import thread
import threading
import SocketServer
import requests
import re
import json


spotifier.login_user_to_spotify()
playlist_id, playlist = spotifier.get_playlist('WXDU')
print json.dumps(playlist, sort_keys=True, indent=2, separators=(',', ': ')), playlist_id


# spotify:track:7pRG3TnLmhNurKn5NF58cX




