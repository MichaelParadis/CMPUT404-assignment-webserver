#  coding: utf-8 
import socketserver
import os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos, Michael Paradis
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

    def __init__(self,request,client_address, server):
        self.request_uri_trailing_slash = False
        self.data = None
        self.http_path = None
        self.response_data = b""
        self.web_root = os.getcwd() + "/www"
        super().__init__(request,client_address,server)



    def handle(self):
        self.data = self.request.recv(1024)
        if not self.check_method():
            self.response_data += bytearray("HTTP/1.1 405 Method Not Allowed\r\n\r\n", 'utf-8')
            self.request.sendall(self.response_data)
            return
        request_path = self.get_requested_path()
        if request_path is None:
            # Error with path
            return

        # Try serving file
        if os.path.isfile(request_path):
            self.serve_file(request_path)
            return True
        # Check if directory
        if self.request_uri_trailing_slash:
            # check if index.html exists.
            if os.path.isfile(request_path + '/index.html'):
                self.serve_file(request_path + '/index.html')
                return True
            else:
                self.serve_404()
                return True
        # directory without trailing slash
        else:
            # Check if directory exist
            # send 301
            if(os.path.isfile(request_path + '/index.html')):
                self.serve_301(self.http_path +'/')
                return True
            # Else 404
            else:
                self.serve_404()
                return True



    def serve_301(self, new_path):
        self.request.sendall(bytearray("HTTP/1.1 301 Moved Permanently\r\n", 'utf-8'))
        self.request.sendall(bytearray("Location: {}\r\n\r\n".format(new_path), 'utf-8'))

    def serve_404(self):
        self.request.sendall(bytearray("HTTP/1.1 404 Not Found\r\n\r\n", 'utf-8'))

    def serve_file(self, request_path):
        file = open(request_path, 'r')
        self.request.send(b'HTTP/1.1 200 OK \r\n')
        self.request.send(bytearray('Content-Type: text/{}\r\n'.format(request_path.split('.')[-1]), 'utf-8'))
        line = file.readline()
        data = line
        # read the entire line. Would want to set a max size to allow for request limiting on an actual server
        while line:
            line = file.readline()
            data += line
        file.close()
        self.request.send(b'\r\n')
        self.request.send(bytearray(data, 'utf-8'))

    """Checks the HTTP method will return false if the method is not allow"""
    def check_method(self):
        http_method = self.data.decode('utf-8').split()[0].upper()
        return http_method == "GET"

    """
        Returns the path on the os for the requested resource.
        Will return None if there is an error getting the path.
    """
    def get_requested_path(self):
        http_req = self.data.decode('utf-8').split()
        if len(http_req) > 2:
            http_path = http_req[1] # Check if path case matters
            self.http_path = http_path
            if http_path[-1] == '/':
                self.request_uri_trailing_slash = True

            os_path = self.web_root + os.path.normpath(http_path)
            return os_path
        return None


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
