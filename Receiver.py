import zmq
import pyaudio
from cv2 import VideoCapture
import cv2
import numpy
import struct

ip = "10.217.47.67" #Server IP
port = 8000

context = zmq.Context()
SubscribeSocket = context.socket(zmq.SUB)
SubscribeSocket.connect("tcp://"+ip+":%s" % port) #Connect to server
SubscribeSocket.setsockopt(zmq.SUBSCRIBE, b"")
       
while True:
    buffer = SubscribeSocket.recv() #Receive packet
    shape = struct.unpack("HH",buffer[:4]) #Get frame shape
    frameBytes = buffer[4:] #Get Frame Bytes
    frame = numpy.frombuffer(frameBytes,dtype = numpy.uint8).reshape((shape[0],shape[1],3)) #Convert bytes to frame array
    frame = cv2.resize(frame,(int(640*1.5),int(480*1.5))) #Upscale Frame
    cv2.imshow("Video",frame) #Display the frame
    cv2.waitKey(1)
   