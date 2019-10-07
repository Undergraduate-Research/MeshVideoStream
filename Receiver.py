import zmq
import pyaudio
from cv2 import VideoCapture
import cv2
import numpy
import struct

ip = "127.0.0.1"
port = 8000


PyAudio = pyaudio.PyAudio()
stream = PyAudio.open(2048*8,1,pyaudio.paInt16,False,True,None,None,2048,True,None,None)
context = zmq.Context()
SubscribeSocket = context.socket(zmq.SUB)
SubscribeSocket.connect("tcp://"+ip+":%s" % port)
SubscribeSocket.setsockopt(zmq.SUBSCRIBE, b"")
       
while True:
    buffer = SubscribeSocket.recv()
    #print(buffer[0])
    if buffer[0] == ord(b"A"):
        stream.write(buffer[1:])
        continue
    shape = struct.unpack("HH",buffer[1:5])
    frameBytes = buffer[5:]
    frame = numpy.frombuffer(frameBytes,dtype = numpy.uint8).reshape((shape[0],shape[1],3))
    cv2.imshow("Video",frame)
    cv2.waitKey(1)
   