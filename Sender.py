import zmq
import pyaudio
from cv2 import VideoCapture
import cv2
import numpy
import struct

port = 8000
camNumber = 0

PyAudio = pyaudio.PyAudio()
context = zmq.Context()
PublishSocket = context.socket(zmq.PUB)
PublishSocket.set_hwm(2)
PublishSocket.bind("tcp://0.0.0.0:%s" % port)
capture = VideoCapture(camNumber)


   
def Audio(in_data,frame_count,time_info,status_flag):
    PublishSocket.send(b"A"+in_data) 
    return (None,0)

stream = PyAudio.open(2048*8,1,pyaudio.paInt16,True,False,None,None,2048,True,None,None,Audio)       
    
stream.start_stream()

old_frame = capture.read()
while True:
    buffer = b"V"
    ret,frame = capture.read()
    if numpy.array_equal(old_frame,frame):
        cv2.waitKey(1)
        continue
    frameBytes = frame.tobytes()
    buffer += struct.pack("HH",frame.shape[0],frame.shape[1])
    buffer += frameBytes
    PublishSocket.send(buffer)
    old_frame = frame
    cv2.waitKey(120)