#  coding: utf-8
import socketserver
import os
from urllib import request

# Copyright 2022 Abram Hindle, Eddie Antonio Santos, Darren Wang
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
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):

    def handle(self):

        self.data = self.request.recv(1024).strip()
        print("Got a request of: %s\n" % self.data)

        # formatting data into readable content
        content = self.data.decode('utf-8').split('\r\n')
        firstLineContent = content[0].split(' ')
        requestedContent = firstLineContent[1]
        method = firstLineContent[0]

        # only handle for GET requests
        if method == 'GET':
            path = './www'

            if requestedContent[-1] == '/':
                # check if looking for index page
                path = path + requestedContent + 'index.html'
            elif requestedContent.split('.')[
                    -1] == 'html' or requestedContent.split('.')[-1] == 'css':
                # check if is html/css ending
                path = path + requestedContent
            else:
                # if here, then is not html/css nor is it looking for index
                # path is fixed to check if file actually exists.
                path = path + requestedContent + '/'

            # only improperly named files are directories
            if os.path.isdir(path):
                self.request.sendall(
                    bytearray(
                        "HTTP/1.1 301 Moved Permanently\r\nLocation: " +
                        path.strip('./www') + "\r\n\r\n", "utf-8"))
                return 0

            try:
                f = open(path, 'r')
            except Exception as e:
                self.request.sendall(
                    bytearray("HTTP/1.1 404 File not found\r\n\r\n", "utf-8"))
                return 0

            # get content type
            if path[-3:] == 'css':
                contentType = "Content-Type: text/css"
            elif path[-4:] == 'html':
                contentType = "Content-Type: text/html"
            else:
                self.request.sendall(
                    bytearray("HTTP/1.1 404 File not found\r\n\r\n", "utf-8"))
                return 0

            # you can send everything at once??????
            self.request.sendall(bytearray(
                'HTTP/1.1 200 OK\r\n' \
                + contentType + '\r\n\r\n' \
                + open(path).read(), "utf-8"))

            # cleanup
            f.close()
            return 1

        else:
            self.request.sendall(
                bytearray("HTTP/1.1 405 Method Not Allowed\r\n\r\n", "utf-8"))
            return 0


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
