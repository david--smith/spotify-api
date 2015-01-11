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
      if HTTPServerThread.AUTH_CODE != None and 'favicon' not in self.data:
        print 'SERVER RECEIVED: '
        print '"""',self.data,'"""'
      HTTPServerThread.THREAD_DATA = self.data
      # just send back the same data, but upper-cased
      self.request.sendall("""
        <script>window.close();</script>
        """)
      regex = re.compile("code=(.*)\sHTTP")
      matches = regex.findall(self.data)
      if HTTPServerThread.AUTH_CODE == None and len(matches)>0:
        HTTPServerThread.AUTH_CODE = matches[0]
