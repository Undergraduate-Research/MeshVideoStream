from http.server import BaseHTTPRequestHandler,HTTPServer
import json
import time

lastTenMessages = []

def loadHTML():
    htmlFile = open("Client.html","rb")
    html = htmlFile.read()
    htmlFile.close()
    return html

class ClientHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        print(self.path)
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(loadHTML())
            self.server.path = self.path
        elif self.path == "/messages":
            self.send_response(200)
            self.send_header("Content-type", 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(lastTenMessages).encode("utf-8"))
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
            
        lastTenMessages.append(message)
        if len(lastTenMessages) > 50:
            lastTenMessages.pop(0)
        self.send_response(202)
        self.end_headers()
        
        print(lastTenMessages)
        
        
        
        
        
def init_server(server_class=HTTPServer, handler_class=ClientHandler):
    server_address = ('127.0.0.1', 8000)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()
    
    
init_server()