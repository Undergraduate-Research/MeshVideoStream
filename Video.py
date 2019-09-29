import zmq
from cv2 import VideoCapture
import cv2
import numpy
import struct


class Sender:
    def __init__(self,port,camNumber):
        self.context = zmq.Context()
        self.PublishSocket = self.context.socket(zmq.PUB)
        self.PublishSocket.set_hwm(2)
        self.PublishSocket.bind("tcp://0.0.0.0:%s" % port)
        self.capture = VideoCapture(camNumber)
        
    def run(self):
        while True:
            buffer = b""
            ret,frame = self.capture.read()
            frameBytes = frame.tobytes()
            #print(len(frameBytes))
            buffer += struct.pack("I",len(frameBytes))
            buffer += struct.pack("HH",frame.shape[0],frame.shape[1])
            buffer += frameBytes
            self.PublishSocket.send(buffer)
            cv2.waitKey(1)
            
            
class Reciever:
    def __init__(self,ip,port):
        self.context = zmq.Context()
        self.SubscribSocket = self.context.socket(zmq.SUB)
        self.SubscribSocket.connect("tcp://"+ip+":%s" % port)
        self.SubscribSocket.setsockopt(zmq.SUBSCRIBE, b"")
        
    def run(self):
        while True:
            buffer = self.SubscribSocket.recv()
            frameLength = struct.unpack("I",buffer[:4])[0]
            #print(len(buffer))
            shape = struct.unpack("HH",buffer[4:8])
            frameBytes = buffer[8:frameLength+8]
            #print(len(buffer[8:]))
            buffer = buffer[frameLength:]
            frame = numpy.frombuffer(frameBytes,dtype = numpy.uint8).reshape((shape[0],shape[1],3))
            cv2.imshow("Video",frame)
            cv2.waitKey(1)