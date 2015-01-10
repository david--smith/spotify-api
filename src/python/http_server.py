#!/usr/bin/python

import sys
import BaseHTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
from multiprocessing import Process
import time
import thread
import threading



class myThread (threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
    def run(self):
      HandlerClass = SimpleHTTPRequestHandler
      ServerClass  = BaseHTTPServer.HTTPServer
      Protocol     = "HTTP/1.0"
      server_address = ('127.0.0.1', 8000)
      HandlerClass.protocol_version = Protocol
      self.httpd = ServerClass(server_address, HandlerClass)
      sa = self.httpd.socket.getsockname()
      print "Serving HTTP on", sa[0], "port", sa[1], "..."
      self.httpd.serve_forever()
    def shutdown(self):
      self.httpd.shutdown()

http_thread = myThread(1, "Thread-1", 1)
http_thread.start()
print ('Did i get past serving? YES!')
time.sleep(10)
print ("Shutting down...")
http_thread.shutdown()
