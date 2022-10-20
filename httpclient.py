#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
import urllib
# you may use urllib to encode data appropriately
import urllib.parse
PAYLOAD_SIZE = 1024

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))

    def get_code(self, data):
        temp = data.split(' ')
        return int(temp[1])

    def get_headers(self,data):
        temp = data.split('\r\n\r\n', 1)
        return temp[0]

    def get_body(self, data):
        temp = data.split('\r\n\r\n', 1)
        return temp[1]
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(PAYLOAD_SIZE)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):

        processed_url = urllib.parse.urlparse(url)
        host = processed_url.netloc.split(":")[0]

        if processed_url.port:
            port = processed_url.port
        else: 
            port = 80

        self.connect(host,port)
        
        if processed_url.path:
            path = processed_url.path
        else:
            path = '/'

        if processed_url.query:
            path = path + ('?' + processed_url.query)
        
        req = "GET " + path + " HTTP/1.1\r\nHost: " + host + ":%d\r\nConnection: close\r\n\r\n" %port
        
        self.sendall(req)
        data = self.recvall(self.socket)
        code = self.get_code(data)
        body = self.get_body(data)
        
        print("Status Code: %d" % code)
        print("Body: \n"+ body )

        return HTTPResponse(code, body)

    def POST(self, url, args=None):

        processed_url = urllib.parse.urlparse(url)
        host = processed_url.netloc.split(":")[0]
        
        if processed_url.port:
            port = processed_url.port
        else: 
            port = 80

        self.connect(host,port)

        if processed_url.path:
            path = processed_url.path
        else:
            path = '/'

        if processed_url.query:
            path = path + '?' + processed_url.query
        req = "POST " + path + " HTTP/1.1\r\nHost: " + host + ":%d\r\n" %port
        if not args:
            req = req + "Content-Length: 0\r\nContent-Type: application/x-www-form-urlencoded\r\n\r\n"
            req = req + "Connection: close\r\n\r\n"
        else:
            byte_enc = urllib.parse.urlencode(args)
            content_length = len(str(byte_enc))
            print("Content Length = %d" %content_length)
            req = req + "Content-Length: %d\r\nContent-Type: application/x-www-form-urlencoded\r\n\r\n" %content_length
            req = req + byte_enc

        self.sendall(req)
        data = self.recvall(self.socket)
        code = self.get_code(data)
        body = self.get_body(data)

        print("Status Code: %d" % code)
        print("Body: \n"+ body )

        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))