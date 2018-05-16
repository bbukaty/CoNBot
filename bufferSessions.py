import os

# make folders for classes
validLabels = ["1","2","3","4"]
classFolders = ["images", "numpy"]
for classFolder in classFolders:
    if not os.path.isdir("classes/{}/".format(classFolder)):
        os.mkdir("classes/{}/".format(classFolder))
    for label in validLabels:
        if not os.path.isdir("classes/{}/{}/".format(classFolder, label)):
            os.mkdir("classes/{}/{}/".format(classFolder, label))

# shift inputs for each session one frame backwards for more accurate timing
for sessNum in os.listdir("sessions"):
    print("Adding input buffer to session {}...".format(sessNum))
    sessFolder = "sessions/{}/".format(sessNum)
    capsFolder = sessFolder + "caps/"

    #check if already processed
    if os.path.isfile(sessFolder + "buffered.sentinel"):
        print("Session {} was already processed. Continuing.".format(sessNum))
        continue

    # delete the first input and last image to shift the inputs back by one frame
    inputSequence = []
    with open(sessFolder + "labels.txt", "r") as labels:
        inputSequence = labels.readlines()[1:] # remove first input

    with open(sessFolder + "labels.txt", "w") as labels:
        for line in inputSequence:
            labels.write(line)

    capFiles = os.listdir(capsFolder)	
    capFileNums = [int(capFile[:-4]) for capFile in capFiles] # -4 index removes '.png'	
    os.remove(capsFolder + str(max(capFileNums)) + ".png")
    
    assert len(inputSequence) ==  len(os.listdir(capsFolder)), "buffer didn't work, mismatch between labels and images"

    # note that this batch has been processed
    open(sessFolder + "buffered.sentinel", "w").close()
