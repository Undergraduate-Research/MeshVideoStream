import zmq
from cv2 import VideoCapture
import cv2
import numpy
from util import SplitGray,zeros
import struct
import bz2
import time
import sys

ip = "0.0.0.0"
port = 8000
audio = 0



try:
    ip = sys.argv[1] 
    port = sys.argv[2]
    
except:
    print("Please include the sender IP, Port")
    exit()


camNumber = 0
context = zmq.Context()
PublishSocket = context.socket(zmq.PUB)
PublishSocket.set_hwm(2) #Set ZMQ high water mark
PublishSocket.bind("tcp://"+ip+":%s" % port) # Bind server to ip
capture = VideoCapture(camNumber) #Video Source

def AddString(frame1,string):
    cv2.putText(frame1,string,(0,25),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,0),2, cv2.LINE_AA)
    return frame1


frames = 0
fps = 30
timea = time.time()
bytes = 0
bytesPerSec = 0

while True:
    buffer = b"V"
    frames +=1
    ret,raw_frame = capture.read() #Read camera
    raw_frame = cv2.cvtColor(raw_frame, cv2.COLOR_BGR2GRAY) 
    frame = cv2.resize(raw_frame,(320,240)) #Downsize the video frame
    
    frameBytes = frame.tobytes() #Convert it to bytes   
    buffer += struct.pack("HH",frame.shape[0],frame.shape[1]) #Pack frame size into packet
    buffer += frameBytes #Add frame data to packet
    compressed = bz2.compress(buffer,9)
    PublishSocket.send(compressed) #Send Packet
    bytes += len(compressed)
    if(time.time() - timea > 1):
        timea = time.time()
        fps = frames
        frames = 0
        bytesPerSec += bytes/1024/1024
        bytesPerSec = bytesPerSec/2
        bytes = 0
    cv2.imshow("Video",AddString(raw_frame,str(fps)+" FPS " + "{:04.2f} MAvg Bytes Per Second".format(bytesPerSec))) #Display the frame
    cv2.waitKey(1)