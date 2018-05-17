import os
from PIL import Image, ImageOps

downsamplingMethods = [Image.NEAREST, Image.BILINEAR, Image.BICUBIC]
downsamplingMethod = downsamplingMethods[0]

# make folders for classes
validLabels = ["1","2","3","4"]
classFolders = ["images", "numpy"]
for classFolder in classFolders:
    if not os.path.isdir("classes/{}/".format(classFolder)):
        os.mkdir("classes/{}/".format(classFolder))
    for label in validLabels:
        if not os.path.isdir("classes/{}/{}/".format(classFolder, label)):
            os.mkdir("classes/{}/{}/".format(classFolder, label))

for sessNum in os.listdir("sessions"):

    print("Downscaling images from session {}...".format(sessNum))
    sessFolder = "sessions/{}/".format(sessNum)
    capsFolder = sessFolder + "caps/"

    if not os.path.isfile(sessFolder + "buffered.sentinel"):
        print("Error: Session has not been input buffered yet. Skipping.")
        continue
    if os.path.isfile(sessFolder + "downscaled.sentinel"):
        print("Error: Session has already been downscaled. Skipping.")
        continue

    inputSequence = []
    with open(sessFolder + "labels.txt", "r") as labels:
        inputSequence = [label[:-1] for label in labels.readlines()] # index removes newline char

    # we need a sorted list of the image numbers in the folder
    # so we can iterate through the images and their corresponding labels
    capFiles = os.listdir(capsFolder)
    capFileNums = [int(capFile[:-4]) for capFile in capFiles] # -4 index removes '.png'	
    capFileNums = sorted(capFileNums) # os.listdir gave us these in random order

    # downscale images and add to class folder
    for capFileIndex, capFileNum in enumerate(capFileNums):
        cap = Image.open(capsFolder + str(capFileNum) + ".png")
        capLabel = inputSequence[capFileIndex]

        if capLabel == '0': # ignore images labeled None for now
            continue

        # add padding, this makes the image a pixel-perfect 15x15 grid of Crypt tiles
        padded = ImageOps.expand(cap, (30,38,26,18))
        # each 'pixel' in the game is actually a 3x3 grid of pixels, so this first downscale by 3 has no data loss
        resized = padded.resize((360,360), downsamplingMethod)
        # now the lossy resize to the final size
        final = resized.resize((180,180), downsamplingMethod)
        final.save("classes/images/" + capLabel + "/sess" + sessNum + "_" + str(capFileNum) + "_resized.png")
    
    # note that this batch has been processed
    open(sessFolder + "downscaled.sentinel", "w").close()