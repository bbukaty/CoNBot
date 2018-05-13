import os
import cv2
import numpy as np

validLabels = ["None","Up","Right","Down","Left"]
for labelIndex in range(len(validLabels)):
    if not os.path.isdir("classes/"+str(labelIndex)):
        os.mkdir("classes/"+str(labelIndex))

finalRes = 128
downsamplingMethods = [cv2.INTER_AREA, cv2.INTER_CUBIC, cv2.INTER_LINEAR, cv2.INTER_NEAREST]
downsamplingMethod = downsamplingMethods[1]

for sessNum in os.listdir("sessions"):
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

    capFiles = os.listdir(capsFolder)	
    capFileNums = [int(capFile[:-4]) for capFile in capFiles] # -4 index removes '.png'	
    os.remove(capsFolder + str(max(capFileNums)) + ".png")
    # get these again now that we've removed one, duct tape code lol
    capFiles = os.listdir(capsFolder)
    capFileNums = [int(capFile[:-4]) for capFile in capFiles] # -4 index removes '.png'	

    assert len(inputSequence) ==  len(capFiles), "buffer didn't work, mismatch between labels and images"

    # downscale images and add to class folder
    for capFileIndex, capFileNum in enumerate(capFileNums):
        cap = cv2.imread(capsFolder + str(capFileNum) + ".png")
        resized = cv2.resize(cap, (finalRes,finalRes), interpolation=downsamplingMethod)
        capLabel = inputSequence[capFileIndex]
        cv2.imwrite("classes/" + capLabel + "/sess" + sessNum + "_" + str(capFileNum) + "_resized.png", resized)

    # note that this batch has been processed
    open(sessFolder + "processed.sentinel", "w").close()

