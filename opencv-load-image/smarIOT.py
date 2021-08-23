import os 
from collections import deque #Coda che serve a memorizzare i punti passati dell'oggetto da rilevare
from imutils.video import VideoStream  #Importa la telecamera
import numpy as np
import argparse
import cv2
import imutils
import time
import telegram_send

# construttore dei parametri iniziali
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
	help="path to the (optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=32,
	help="max buffer size") #-- buffer la lunghezza massima della coda che permette di mantenere le cordinate x-y del oggetto tracciante
args = vars(ap.parse_args())

# definisce estremi del colore definito
# Lo spazio colore è HSV
colorLower = (0,50,20)
colorUpper = (5,255,255)


#inizilizza la coda dei punti  e le cordinato X e Y
points = deque(maxlen=args["buffer"])
counter = 0
(dX, dY) = (0, 0)
direction = ""

# Se la telecamera esterna non è disponibile prende la webcam
if  args.get("video", True):
    vs = cv2.VideoCapture(args["video"])
else:
	vs = VideoStream(src=0).start()

while True:
    #prende il frame corrente
	frame = vs.read()
    # prende il frame dalla video camera o dalla webcam
	frame = frame[1] if args.get("video", False) else frame
    #If non riusciamo a prendere il frame, vuole dire che il video è finito
    if frame is None:
		break
    frame = imutils.resize(frame, width=600)
	blurred = cv2.GaussianBlur(frame, (11, 11), 0)
	hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    #rilevamento del colore
    mask = cv2.inRange(hsv, colorLower, colorUpper)
	mask = cv2.erode(mask, None, iterations=4) #toglie via i bordi dell'oggetto
	mask = cv2.dilate(mask, None, iterations=15) #raggio di ricognizione dell'oggetto

    # trova i contorni della mask, e mettere le cordinate x y al centro 
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)
	cnts = imutils.grab_contours(cnts)
	center = None
