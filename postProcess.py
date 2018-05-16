import os
import numpy as np
from PIL import Image, ImageOps

downsamplingMethods = [Image.NEAREST, Image.BILINEAR, Image.BICUBIC]
downsamplingMethod = downsamplingMethods[0]

# make folders for classes
# validLabels = ["None","Up","Right","Down","Left"]
validLabels = ["Up","Right","Down","Left"]
for labelIndex in range(len(validLabels)):
    if not os.path.isdir("classes/"+str(labelIndex+1)):
        os.mkdir("classes/"+str(labelIndex+1))

# set up variables for dataset normalization statistics
numTrain = 0
# for sessNum in os.listdir("sessions"):
#     numTrain += len(os.listdir("sessions/{}/caps".format(sessNum)))

meanImage = np.zeros((180,180,3), np.float)
meanImageSquared = np.zeros_like(meanImage)

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
    # and count the number of nonzero training data
    inputSequence = [label[:-1] for label in inputSequence]
    for label in inputSequence:
        if label != '0':
            numTrain += 1

    capFiles = os.listdir(capsFolder)	
    capFileNums = [int(capFile[:-4]) for capFile in capFiles] # -4 index removes '.png'	
    os.remove(capsFolder + str(max(capFileNums)) + ".png")
    # get these again now that we've removed one, duct tape code lol
    capFiles = os.listdir(capsFolder)
    capFileNums = [int(capFile[:-4]) for capFile in capFiles] # -4 index removes '.png'	
    capFileNums = sorted(capFileNums) # os.listdir gave us these in random order
    
    assert len(inputSequence) ==  len(capFiles), "buffer didn't work, mismatch between labels and images"

print(numTrain)

for sessNum in os.listdir("sessions"):
    print("Processing session {}...".format(sessNum))
    sessFolder = "sessions/{}/".format(sessNum)
    capsFolder = sessFolder + "caps/"

    inputSequence = []
    with open(sessFolder + "labels.txt", "r") as labels:
        inputSequence = labels.readlines()
    inputSequence = [label[:-1] for label in inputSequence]

    capFiles = os.listdir(capsFolder)
    capFileNums = [int(capFile[:-4]) for capFile in capFiles] # -4 index removes '.png'	
    capFileNums = sorted(capFileNums) # os.listdir gave us these in random order

    # downscale images and add to class folder
    for capFileIndex, capFileNum in enumerate(capFileNums):
        cap = Image.open(capsFolder + str(capFileNum) + ".png")
        capLabel = inputSequence[capFileIndex]

        if capLabel == '0':
            continue

        # add padding, this makes the image a pixel-perfect 15x15 grid of Crypt tiles
        padded = ImageOps.expand(cap, (30,38,26,18))
        # each 'pixel' in the game is actually a 3x3 grid of pixels, so this first downscale by 3 has no data loss
        resized = cap.resize((360,360), downsamplingMethod)
        # now the lossy resize to the final size
        final = resized.resize((180,180), downsamplingMethod)
        final.save("classes/" + capLabel + "/sess" + sessNum + "_" + str(capFileNum) + "_resized.png")

        # compute stats over training data
        meanImage += np.array(final, np.float64) / numTrain
        meanImageSquared += np.array(final, np.float64)**2 / numTrain

    # note that this batch has been processed
    open(sessFolder + "processed.sentinel", "w").close()

stdImage = np.sqrt(meanImageSquared - meanImage**2)
np.save("stats/dsetMean", meanImage)
np.save("stats/dsetStd", stdImage)
