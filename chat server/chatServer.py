from http.server import BaseHTTPRequestHandler,HTTPServer,ThreadingHTTPServer
import socket
import json
from cv2 import VideoCapture,IMWRITE_JPEG_QUALITY
import cv2
import numpy
import base64
import time

capture = VideoCapture(0) #Video Source

messageHistory = [] #Stores all messgaes
lastTenMessages = [] #Stores just the last few



def GetFrame():
    global frame
    ret,raw_frame = capture.read() #Read camera
    frame2 = cv2.resize(raw_frame,(320,240)) # Resize the frame
    frame =base64.b64encode(cv2.imencode('.jpeg',frame2,[int(IMWRITE_JPEG_QUALITY),30])[1].tostring()) #Convert it to JPEG data then base64 encode

GetFrame() #Get an intital frame
    
    

def loadHTML(): #Load the main client html file
    htmlFile = open("Client.html","rb")
    html = htmlFile.read()
    htmlFile.close()
    return html

def loadHistoryViewer(): #Load the history client html file
    htmlFile = open("HistoryViewer.html","rb")
    html = htmlFile.read()
    htmlFile.close()
    return html
    
def loadVideo(): #Load the video / text client html file
    htmlFile = open("ClientVideo.html","rb")
    html = htmlFile.read()
    htmlFile.close()
    return html

class ClientHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/": #Handle requests to the server with no path
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(loadHTML())
            self.server.path = self.path
        elif self.path == "/history": #Handle the request for history
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(loadHistoryViewer())
            self.server.path = self.path
        elif self.path == "/messages": #Handle request for messages
            self.send_response(200)
            self.send_header("Content-type", 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(lastTenMessages).encode("utf-8")) #Send the messages in JSON format
            self.server.path = self.path
        elif self.path == "/message_history": #Handle request for message history
            self.send_response(200)
            self.send_header("Content-type", 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(messageHistory).encode("utf-8")) #Send history in JSOn format
            self.server.path = self.path 
        elif self.path == "/frame": #Handle request for frame
            self.send_response(200)
            self.send_header("Content-type", 'application/data')
            self.end_headers()
            self.wfile.write(frame) #Send the frame as raw bytes that are generated in GetFrame
            self.server.path = self.path
        if self.path == "/video": #Handle request for video client
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(loadVideo())
            self.server.path = self.path   
        
    def do_POST(self): #Handle posting of messages
        message = {} 
        contentLen = int(self.headers.get('Content-Length')) #Get the length of the message data
        
        if self.headers.get('Content-Type') == 'application/json': #Make sure it is actually the correct format
            message = json.loads(self.rfile.read(contentLen).decode("utf-8")) #Decode the text to a python object using the json library
            message["time"]=int(time.time())  #Add the time into the message
	    
        else:
            self.send_response(400) #If incorrect format return an error status
            self.end_headers() 
            return   
        messageHistory.append(message) #Add message to history
        lastTenMessages.append(message) #Add message to last messages
        if len(lastTenMessages) > 50:
            lastTenMessages.pop(0) #Prune away old message
        self.send_response(202)
        self.end_headers()   
        
def init_server(server_class=ThreadingHTTPServer, handler_class=ClientHandler): 
    server_address = ('0.0.0.0', 80)
    httpd = server_class(server_address, handler_class)
    #httpd.serve_forever()
    while True:
        httpd.handle_request() #Handle Requests
        GetFrame() #Update current available frame
        cv2.waitKey(1) #Wait a bit to not freeze up opencv
    
     
init_server()