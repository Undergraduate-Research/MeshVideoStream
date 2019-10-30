import numpy as np
import cv2
import numba
from numba import int8

SHARPEN = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
SMOOTH = np.ones((3,3),np.float32)/9

def zeros(shape):
    return np.zeros(shape, dtype=int)


#Floyd–Steinberg dithering algorithm 
   
@numba.jit(nopython=True)
def Dither(num,derr, thresh = 175):
    div = 5 
    for y in range(num.shape[0]):
        for x in range(num.shape[1]):
            newval = derr[y,x] + num[y,x]
            if newval >= thresh:
                errval = newval - 255
                num[y,x] = 1.
            else:
                errval = newval
                num[y,x] = 0.
            if x + 1 < num.shape[1]:
                derr[y, x + 1] += errval / div
                if x + 2 < num.shape[1]:
                    derr[y, x + 2] += errval / div
            if y + 1 < num.shape[0]:
                derr[y + 1, x - 1] += errval / div
                derr[y + 1, x] += errval / div
                if y + 2< num.shape[0]:
                    derr[y + 2, x] += errval / div
                if x + 1 < num.shape[1]:
                    derr[y + 1, x + 1] += errval / div
    return (num[::-1,:] * 255)[::-1, ...].astype(np.uint8)


@numba.jit(nopython=True)
def SplitGray(in_frame,out_frame):
    for y in range(in_frame.shape[0]):
        for x in range(in_frame.shape[1]):
            out_frame[y,x] = in_frame[y,x]
    return out_frame
    
def Filter(frame,filter):
    return cv2.filter2D(frame, -1, filter)