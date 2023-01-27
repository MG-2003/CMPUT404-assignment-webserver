#  coding: utf-8 
import socketserver
from os import path
from os import listdir

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
        # Get client-requested data
        with open(filePath, 'r') as file:
            data = file.read()
        return data

    def send_error(self, code, message = '', requestPath = ''):
        # Send error back to client
        locationHeader = f"Location: http://127.0.0.1:8080{requestPath}/" if code == 301 else ""
        error = f"HTTP/1.1 {code} {message}\r\n{locationHeader}"
        self.request.sendall(bytearray(error,'utf-8'))

    def send_data(self, fileType, filePath):
        # Send requested data back to client
        data = self.get_data(filePath)
        msg = f"HTTP/1.1 200 OK\r\nContent-Type: text/{fileType}; charset=utf-8\r\n\r\n{data}"
        self.request.sendall(bytearray(msg,'utf-8'))
    
    def get_servable_requests(self, filePath = "www"):
        # List of all possible directories and files that can be served (are within www dir)
        requests = []
        for i in listdir(filePath):
            requests.append(i)
            if path.isdir(f"{filePath}/{i}"):
                dirR = self.get_servable_requests(f"{filePath}/{i}")
                for x in dirR:
                    requests.append(x)
        return requests

    def is_servable_dir(self, dirPath):
        return True if dirPath.split("/")[-1] in self.get_servable_requests() else False

    def is_servable_file(self, filePath):
        return True if filePath.split("/")[-1] in self.get_servable_requests() else False

    def handle(self):
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)

        # Split incoming data by line
        dataList = self.data.decode("utf-8").split('\r\n')
        # Process request type ie. GET, POST, etc.
        requestType = dataList[0].split(' ')[0]

        # Send 405 if request isn't supported
        if requestType != 'GET':
            self.send_error(405, "Method Not Allowed")

        else:
            # Proccess request path
            requestPath = dataList[0].split(' ')[1]
            print('PATH:', path)

            # If request ends with slash, we assume they're requesting the index.html file in the requested dir
            if requestPath[-1] != "/":
                filePath = f"www{requestPath}"
                if path.isfile(filePath) and self.is_servable_file(filePath):
                    #Grab the file extension (last element of the filePath, and information after the .) ex. /deep/base.css, would grab "css" frm base.css
                    fileType = filePath.split("/")[-1].split(".")[-1]
                    self.send_data(fileType, filePath)
                elif path.isdir(filePath) and self.is_servable_dir(filePath):
                    self.send_error(301, "Moved Permanently", requestPath)
                else:
                    self.send_error(404, "File Not Found")
            else:
                filePath = f"www{requestPath}index.html"
                print("FILEPATH", filePath)
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
