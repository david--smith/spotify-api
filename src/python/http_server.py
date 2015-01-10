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

class HTTPServerThread (threading.Thread):
  THREAD_DATA = None
  AUTH_CODE = None
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
    self.httpd = ServerClass(server_address, MyTCPHandler)
    sa = self.httpd.socket.getsockname()
    print "Serving HTTP on", sa[0], "port", sa[1], "..."
    self.httpd.serve_forever()
  def shutdown(self):
    self.httpd.shutdown()

class MyTCPHandler(SocketServer.BaseRequestHandler):
  def handle(self):
      # self.request is the TCP socket connected to the client
      self.data = self.request.recv(1024).strip()
      #print "{} wrote:".format(self.client_address[0])
#      print 'SERVER RECEIVED: '
#      print '"""',self.data,'"""'
      HTTPServerThread.THREAD_DATA = self.data
      # just send back the same data, but upper-cased
      self.request.sendall(self.data.upper())
      regex = re.compile("code=(.*)\sHTTP")
      matches = regex.findall(self.data)
#      print 'Matches: ', matches
      if HTTPServerThread.AUTH_CODE == None and len(matches)>0:
        HTTPServerThread.AUTH_CODE = matches[0]

http_thread = HTTPServerThread(1, "Thread-1", 1)
http_thread.start()
time.sleep(1)

#data = " ".join(['foo', 'bar'])
#sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#try:
    # Connect to server and send data
#    sock.connect(('127.0.0.1', 8000))
#    print "CLIENT Sending:     {}".format(data)
#    sock.sendall(data + "\n")

    # Receive data from the server and shut down
#    received = sock.recv(1024)
#finally:
#    sock.close()

#print "CLIENT Received: {}".format(received)

spotifier.login_user_to_spotify()
while http_thread.AUTH_CODE == None:
  time.sleep(1)
#time.sleep(7)
print ("Shutting down...")
http_thread.shutdown()
print "AUTH_CODE: ", http_thread.AUTH_CODE

