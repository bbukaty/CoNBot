import os
import cv2
import numpy as np

validLabels = ["None","Up","Right","Down","Left"]
for label in validLabels:
    if not os.path.isdir("classes/"+label):
        os.mkdir("classes/"+label)

finalRes = 128
downsamplingMethods = [cv2.INTER_AREA, cv2.INTER_CUBIC, cv2.INTER_LINEAR, cv2.INTER_NEAREST]
downsamplingMethod = downsamplingMethods[1]

for sessNum in os.listdir("sessions")[:1]:
    print("Processing session {}...".format(sessNum))
    sessFolder = "sessions/{}/".format(sessNum)
    capsFolder = sessFolder + "caps/"

    #check if already processed
    if os.path.isfile(sessFolder + "processed.sentinel"):
        print("Session {} was already processed. Continuing.".format(sessNum))
        continue

    # delete the first input and last image to shift the inputs back by one frame
    inputSequence = []
    with open(sessFolder + "labels.txt", "r") as labels:
        inputSequence = labels.readlines()[1:] # remove first input

    with open(sessFolder + "labels.txt", "w") as labels:
        for line in inputSequence:
            labels.write(line)

    # remove newline characters in labels (we wanted them for the rewrite above)
    inputSequence = [label[:-1] for label in inputSequence]

    lastCapNum = len(os.listdir(capsFolder)) - 1
    os.remove(capsFolder + str(lastCapNum) + ".png")
    assert len(inputSequence) ==  len(os.listdir(capsFolder)), "buffer didn't work, mismatch between labels and images"

    # downscale images and add to class folder
    for capNum in range(len(inputSequence)):
        cap = cv2.imread(capsFolder + str(capNum) + ".png")
        resized = cv2.resize(cap, (finalRes,finalRes), interpolation=downsamplingMethod)
        capLabel = inputSequence[capNum]
        cv2.imwrite("classes/" + capLabel + "/sess" + sessNum + "_" + str(capNum) + "_resized.png", resized)

    # note that this batch has been processed
    open(sessFolder + "processed.sentinel", "w").close()

