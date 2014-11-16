#!/usr/bin/python

import ConfigParser
import os
CONFIG_FILE='config/settings.ini'

print "Config: {} exists? {}".format(CONFIG_FILE, os.path.isfile(CONFIG_FILE))
Config = ConfigParser.ConfigParser()
Config.read(CONFIG_FILE)
print Config.get('auth','clientID')
