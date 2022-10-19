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
# you may use urllib to encode data appropriately
import urllib.parse
import errno

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        temp = data.split("\r\n")[0].split(" ")[1]
        return temp

    def get_headers(self,data):
        temp = data.split("\r\n\r\n")[0]
        return temp

    def get_body(self, data):
        temp = data.split("\r\n\r\n")[1]
        return temp
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        code = 500
        body = ""

        host, port, path = self.url_parser(url)

        try:
            self.connect(host, port)
        except:
            if (host == "localhost"):
                self.connect("127.0.0.1", port)
        finally:
            print("Error connection to port and host!")
        
        try:
            req = self.request_formatter("GET", host, port, path)
            self.sock.sendall(req)
        except IOError as e:
            if e.errno == errno.EPIPE:
                pass
            # Handling of the error


        resp = self.recvall(self.sock)

        self.sock.close()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # print out response stored in resp
        temp = int(self.get_code(resp))
        body = self.get_body(resp)
        print(body)
        
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""

        host, port, path = self.url_parser(url)

        try:
            self.connect(host, port)
        except:
            if (host == "localhost"):
                self.connect("127.0.0.1", port)
        finally:
            print("Error connection to port and host!")

        try:
            req = self.request_formatter("POST", host, port, path, args)
            self.sock.sendall(req)
        except IOError as e:
            if e.errno == errno.EPIPE:
                pass
            # Handling of the error

        resp = self.recvall(self.sock)

        self.sock.close()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        code = int(self.get_code(resp))
        body = self.get_body(resp)
        print(body)

        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
    def url_parser(self, url):
        ''' This function traverses a url.
            Input: url is a string containing information to be processed.
            Returns: host(string), port number(int), and path of an url(string).
        '''
        host, port, path = [None,None,None]

        # Case 1:

        if (url[0:7] == "http://"):
            host = url[7:]
        else:
            try:
                host = url
            except Exception as e:
                print("Invalid url!"); print(e)
        
        #Case 2:

        if ("/" in host):
            char_index = host.index("/")
            path, host = [ host[char_index:], host[0:char_index] ]

        if (":" in host):
            char_index = host.index(":")
            port, host = [ int(host[char_index+1:]), host[0:char_index] ]

        if (path == None):
            path = "/"
        
        return host, port, path
    
    def request_formatter(self, instruction, host, port, path, args=None):
        ''' This function formats the results of a request.
            Input: instruction, host and path are strings; host is an int.
            Returns: a formatted string stored in formal_request.
        '''
        if (instruction == "GET"):
            req_format = "GET {path_var} HTTP/1.1\r\n" \
                               "Host: {host_var}\r\n" \
                               "Connection: keep-alive\r\n"
        elif (instruction == "POST"):
            req_format = "POST {path_var} HTTP/1.1\r\n" \
                               "Host: {host_var}\r\n" \
                               "Connection: keep-alive\r\n"
        
        if (port):
            formal_request= req_format.format(path_var = path, host_var = host+":"+str(port))
        else:
            formal_request = req_format.format(path_var = path, host_var = host)
        
        if (instruction == "POST"):
            formal_request = formal_request + "Content-Type: application/x-www-form-urlencoded\r\n"
            if (isinstance(args, dict) and args.keys() != []):
                #args = urllib.parse(args)
                formal_request = formal_request + "Content-Length: "+str(len(args))+"\r\n\r\n"
                #formal_request = formal_request + args+"\r\n"
            else:
                formal_request = formal_request + "Content-Length: 0\r\n"
        
        formal_request = formal_request + "\r\n"
        return formal_request.encode('utf-8')


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
