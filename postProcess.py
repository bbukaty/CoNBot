import os
import cv2
import numpy as np

finalRes = 256

# delete the first input and last image to shift the inputs back by one frame
# also, downscale images
for sessNum in os.listdir("sessions"):
    print("Processing session {}...".format(sessNum))
    sessFolder = "sessions/{}/".format(sessNum)
    if os.path.isfile(sessFolder + "processed.sentinel"):
        print("Session {} was already processed. Continuing.".format(sessNum))
        continue

    with open(sessFolder + "labels.txt", "r") as labels:
        inputSequence = labels.readlines()

    with open(sessFolder + "labels.txt", "w") as labels:
        for line in inputSequence[1:]: # remove first input
            labels.write(line)
    
    capFiles = os.listdir(sessFolder + "caps")
    capNums = [int(capFile[:-4]) for capFile in capFiles] # -4 index removes '.png'
    os.remove(sessFolder + "caps/" + str(max(capNums)) + ".png")
    capFiles = os.listdir(sessFolder + "caps") # get the list of files again because we removed one (duct tape code lol)

    for capFile in capFiles:
        cap = cv2.imread(sessFolder + "caps/" + capFile)

        resized = cv2.resize(cap, (128,128), interpolation=cv2.INTER_NEAREST)
        resized2 = cv2.resize(cap, (128,128), interpolation=cv2.INTER_LINEAR)
        resized3 = cv2.resize(cap, (128,128), interpolation=cv2.INTER_AREA)
        resized4 = cv2.resize(cap, (128,128), interpolation=cv2.INTER_CUBIC)

        cv2.imwrite(sessFolder + "caps/" + capFile[:-4] + "_n_.png", resized)
        cv2.imwrite(sessFolder + "caps/" + capFile[:-4] + "_l_.png", resized2)
        cv2.imwrite(sessFolder + "caps/" + capFile[:-4] + "_a_.png", resized3)
        cv2.imwrite(sessFolder + "caps/" + capFile[:-4] + "_c_.png", resized4)

    open(sessFolder + "processed.sentinel", "w").close()

