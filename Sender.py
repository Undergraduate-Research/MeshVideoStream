import zmq
import pyaudio
from cv2 import VideoCapture
import cv2
import numpy
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
PyAudio = pyaudio.PyAudio()
context = zmq.Context()
PublishSocket = context.socket(zmq.PUB)
PublishSocket.set_hwm(2) #Set ZMQ high water mark
PublishSocket.bind("tcp://"+ip+":%s" % port) # Bind server to ip
capture = VideoCapture(camNumber) #Video Source


def Audio(in_data,frame_count,time_info,status_flag):
    PublishSocket.send(bz2.compress(b"A"+in_data)) 
    return (None,0)

stream = PyAudio.open(8000,1,pyaudio.paFloat32 ,True,False,None,None,256,True,None,None,Audio)       
    

def AddFPS(frame1,string):
    cv2.putText(frame1,string,(0,25),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,0),2, cv2.LINE_AA)
    return frame1


frames = 0
fps = 30
timea = time.time()


while True:
    buffer = b"V"
    frames +=1
    ret,raw_frame = capture.read() #Read camera
    frame = cv2.resize(raw_frame,(320,240)) #Downsize the video frame 
    frameBytes = frame.tobytes() #Convert it to bytes   
    buffer += struct.pack("HH",frame.shape[0],frame.shape[1]) #Pack frame size into packet
    buffer += frameBytes #Add frame data to packet
    compressed = bz2.compress(buffer,9)
    PublishSocket.send(compressed) #Send Packet
    if(time.time() - timea > 5):
        timea = time.time()
        fps = frames//5
        frames = 0
    cv2.imshow("Video",AddFPS(raw_frame,str(fps)+" FPS")) #Display the frame
    cv2.waitKey(1)