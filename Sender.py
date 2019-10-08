import zmq
import pyaudio
from cv2 import VideoCapture
import cv2
import numpy
import struct

ip = "0.0.0.0"
port = 8000
camNumber = 0

context = zmq.Context()
PublishSocket = context.socket(zmq.PUB)
PublishSocket.set_hwm(2) #Set ZMQ high water mark
PublishSocket.bind("tcp://"+ip+":%s" % port) # Bind server to ip
capture = VideoCapture(camNumber) #Video Source

frames = 0

while True:
    buffer = b""
    ret,frame = capture.read() #Read camera 
    if frames < 2:  #Skipping frames
        frames += 1
        continue
    else:
        frames = 0
    frame = cv2.resize(frame,(240,320)) #Downsize the video frame   
    frameBytes = frame.tobytes() #Convert it to bytes   
    buffer += struct.pack("HH",frame.shape[0],frame.shape[1]) #Pack frame size into packet
    buffer += frameBytes #Add frame data to packet
    PublishSocket.send(buffer) #Send Packet
    cv2.waitKey(1)