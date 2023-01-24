#  coding: utf-8 
import socketserver
from os import path

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
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

    def get_data(self, filePath):
        with open(filePath, 'r') as file:
            data = file.read()
        return data

    def send_error(self, code, message = '', requestPath = ''):
        locationHeader = f"Location: http://127.0.0.1:8080{requestPath}/" if code == 301 else ""
        error = f"HTTP/1.1 {code} {message}\r\n{locationHeader}"
        self.request.sendall(bytearray(error,'utf-8'))

    def send_data(self, fileType, filePath):
        data = self.get_data(filePath)
        msg = f"HTTP/1.1 200 OK\r\nContent-Type: text/{fileType}; charset=utf-8\r\n\r\n{data}"
        self.request.sendall(bytearray(msg,'utf-8'))

    def is_servable_dir(self, dirPath):
        return self.is_servable_file(f"{dirPath}/")

    def is_servable_file(self, filePath):
        dirName = path.dirname(f"{filePath}").split("/")
        return True if dirName[-1] == "www" or dirName[-2] == "www" else False

    def handle(self):
        self.data = self.request.recv(1024).strip()
        # print ("Got a request of: %s\n" % self.data)

        # Split incoming data by line
        dataList = self.data.decode("utf-8").split('\r\n')
        # Process request type ie. GET, POST, etc.
        requestType = dataList[0].split(' ')[0]

        if requestType != 'GET':
            self.send_error(405, "Method Not Allowed")

        else:
            # Proccess request path
            requestPath = dataList[0].split(' ')[1]
            print('PATH:', path)

            if requestPath[-1] != "/":
                filePath = f"www{requestPath}"
                if path.isfile(filePath) and self.is_servable_file(filePath):
                    fileType = "css" if filePath[len(filePath)-3:] == "css" else "html"
                    self.send_data(fileType, filePath)
                elif path.isdir(filePath) and self.is_servable_dir(filePath):
                    self.send_error(301, "Moved Permanently", requestPath)
                else:
                    self.send_error(404, "File Not Found")
            else:
                filePath = f"www{requestPath}/index.html"
                if path.isfile(filePath) and self.is_servable_file(filePath):
                    self.send_data("html", filePath)
                else:
                    self.send_error(404, "File Not Found")

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
