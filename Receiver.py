import zmq
import pyaudio
from cv2 import VideoCapture
import cv2
import numpy
import struct
import bz2
import time
import sys

ip = "127.0.0.1"
port = 8000

try:
    ip = sys.argv[1] 
    port = sys.argv[2]
except:
    print("Please include the server IP and port")
    exit()


PyAudio = pyaudio.PyAudio()
stream = PyAudio.open(8000,1,pyaudio.paFloat32 ,False,True,None,None,256,True,None,None)
context = zmq.Context()
SubscribeSocket = context.socket(zmq.SUB)
SubscribeSocket.connect("tcp://"+ip+":%s" % port) #Connect to server
SubscribeSocket.setsockopt(zmq.SUBSCRIBE, b"")

def AddFPS(frame1,string):
    cv2.putText(frame1,string,(0,25),cv2.FONT_HERSHEY_SIMPLEX,1,(255,0,0),2, cv2.LINE_AA)
    return frame1

frames = 0
fps = 30
timea = time.time() 

while True:
    
    compressed = SubscribeSocket.recv() #Receive packet
    buffer = bz2.decompress(compressed)
    if buffer[0] == ord("A"):
        stream.write(buffer[1:])
        continue
    shape = struct.unpack("HH",buffer[1:5])
    frameBytes = buffer[5:] #Get Frame Bytes
    frame = numpy.frombuffer(frameBytes,dtype = numpy.uint8).reshape((shape[0],shape[1],3)) #Convert bytes to frame array
    frame = cv2.resize(frame,(int(640*1.5),int(480*1.5))) #Upscale Frame    
    frames += 1
    if(time.time() - timea > 5):
        timea = time.time()
        fps = frames//5
        frames = 0
    
    cv2.imshow("Video",AddFPS(frame,str(fps)+" FPS")) #Display the frame
    cv2.waitKey(1)
   