import os
from shutil import copy2
import cv2
import numpy as np

validLabels = ['^^^^','v^^^','^v^^','^^v^','^^^v']
for label in validLabels:
    if not os.path.isdir("classes/"+label):
        os.mkdir()

for sessNum in os.listdir("sessions"):
    sessFolder = "sessions/{}/".format(sessNum)

    with open(sessFolder + "labels.txt", "r") as labelFile:
        labels = [label[:-1] for label in labelFile.readlines()] # remove newline characters

        for i in range(len(os.listdir(sessFolder + "caps"))//5):
            copy2(sessFolder + "caps/" + str(i)+"_c_.png", "classes/" + labels[i] + "/sess"+sessNum+"_"+str(i)+"_c_.png")

        