from http.server import BaseHTTPRequestHandler,HTTPServer,ThreadingHTTPServer
import socket
import json
from cv2 import VideoCapture
import cv2
import numpy
import base64
import time

capture = VideoCapture(0) #Video Source

messageHistory = []
lastTenMessages = []



def GetFrame():
    global frame
    ret,raw_frame = capture.read() #Read camera
    frame2 = cv2.resize(raw_frame,(320//2,240//2)) # Resize the frame
    frame =base64.b64encode(cv2.imencode('.jpeg',frame2)[1].tostring()) #Convert it to JPEG data then base64 encode

GetFrame()
    
    

def loadHTML():
    htmlFile = open("Client.html","rb")
    html = htmlFile.read()
    htmlFile.close()
    return html

def loadHistoryViewer():
    htmlFile = open("HistoryViewer.html","rb")
    html = htmlFile.read()
    htmlFile.close()
    return html
    
def loadVideo():
    htmlFile = open("ClientVideo.html","rb")
    html = htmlFile.read()
    htmlFile.close()
    return html

class ClientHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        #print(self.path)
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(loadHTML())
            self.server.path = self.path
        elif self.path == "/history":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(loadHistoryViewer())
            self.server.path = self.path
        elif self.path == "/messages":
            self.send_response(200)
            self.send_header("Content-type", 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(lastTenMessages).encode("utf-8"))
            self.server.path = self.path
        elif self.path == "/history":
            self.send_response(200)
            self.send_header("Content-type", 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(messageHistory).encode("utf-8"))
            self.server.path = self.path
        elif self.path == "/frame":
            self.send_response(200)
            self.send_header("Content-type", 'application/data')
            self.end_headers()
            self.wfile.write(frame)
            self.server.path = self.path
        if self.path == "/video":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(loadVideo())
            self.server.path = self.path   
        
    def do_POST(self):
        message = {} 
        contentLen = int(self.headers.get('Content-Length'))
        
        if self.headers.get('Content-Type') == 'application/json':
            message = json.loads(self.rfile.read(contentLen).decode("utf-8"))
            message["time"]=int(time.time())
	    
        else:
            self.send_response(400)
            self.end_headers()
            return   
        messageHistory.append(message)
        lastTenMessages.append(message)
        if len(lastTenMessages) > 50:
            lastTenMessages.pop(0)
        self.send_response(202)
        self.end_headers()   
        
def init_server(server_class=ThreadingHTTPServer, handler_class=ClientHandler):
    server_address = ('0.0.0.0', 80)
    httpd = server_class(server_address, handler_class)
    #httpd.serve_forever()
    while True:
        httpd.handle_request()
        GetFrame()
        cv2.waitKey(1)
    
     
init_server()