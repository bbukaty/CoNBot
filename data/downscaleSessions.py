import os
from PIL import Image, ImageOps

downsamplingMethods = [Image.NEAREST, Image.BILINEAR, Image.BICUBIC]
downsamplingMethod = downsamplingMethods[0]

# make folders for classes
validLabels = ["1","2","3","4"]
classFolders = ["downscaledIndiv", "downscaledQuad", "224scaledIndiv", "224scaledQuad", "normalized"]
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

    # if not os.path.isfile(sessFolder + "buffered.sentinel"):
    #     print("Error: Session has not been input buffered yet. Skipping.")
    #     continue
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
        if capFileIndex < 3:
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
            final224 = cap.resize((224,224), downsamplingMethod) #no padding, this is for pretrained models
            final224.save("classes/224scaledIndiv/{}/sess{}_{}_resized.png".format(capLabel, sessNum, capFileNum))
            final.save("classes/downscaledIndiv/{}/sess{}_{}_resized.png".format(capLabel, sessNum, capFileNum))
        else:
            cap1 = Image.open(capsFolder + str(capFileNum) + ".png")
            cap2 = Image.open(capsFolder + str(capFileNums[capFileIndex-1]) + ".png") #back in time
            cap3 = Image.open(capsFolder + str(capFileNums[capFileIndex-2]) + ".png") 
            cap4 = Image.open(capsFolder + str(capFileNums[capFileIndex-3]) + ".png") 
            capLabel = inputSequence[capFileIndex]

            if capLabel == '0': # ignore images labeled None for now
                continue

            # add padding, this makes the image a pixel-perfect 15x15 grid of Crypt tiles
            paddedIndiv = ImageOps.expand(cap1, (30,38,26,18))
            # each 'pixel' in the game is actually a 3x3 grid of pixels, so this first downscale by 3 has no data loss
            resizedIndiv = paddedIndiv.resize((360,360), downsamplingMethod)
            # now the lossy resize to the final size
            finalIndiv = resizedIndiv.resize((180,180), downsamplingMethod)
            #final224Indiv = resizedIndiv.resize((224,224),downsamplingMethod) #oh fuck this is wrong
            final224Indiv = cap1.resize((224,224),downsamplingMethod)
            final224Indiv.save("classes/224scaledIndiv/{}/sess{}_{}_resized.png".format(capLabel, sessNum, capFileNum))
            finalIndiv.save("classes/downscaledIndiv/{}/sess{}_{}_resized.png".format(capLabel, sessNum, capFileNum))
            # above saves just the first to special spot in case needed for other things (like stats)
            
            paddedCap2 = ImageOps.expand(cap2, (30,38,26,18))
            paddedCap3 = ImageOps.expand(cap3, (30,38,26,18))
            paddedCap4 = ImageOps.expand(cap4, (30,38,26,18))
            
            resizedCap2 = paddedCap2.resize((360,360), downsamplingMethod)
            resizedCap3 = paddedCap3.resize((360,360), downsamplingMethod)
            resizedCap4 = paddedCap4.resize((360,360), downsamplingMethod)
            
            finalCap2 = resizedCap2.resize((180,180), downsamplingMethod)
            finalCap3 = resizedCap3.resize((180,180), downsamplingMethod)
            finalCap4 = resizedCap4.resize((180,180), downsamplingMethod)
            
            final224Cap2 = cap2.resize((224,224),downsamplingMethod)
            final224Cap3 = cap3.resize((224,224),downsamplingMethod)
            final224Cap4 = cap4.resize((224,224),downsamplingMethod)
            
            #https://stackoverflow.com/questions/30227466/combine-several-images-horizontally-with-python
            otherImages = (finalIndiv, finalCap2, finalCap3, finalCap4)
            concatenatedSequence = Image.new('RGB', (720, 180))
            x_offset = 0
            for image in otherImages:
                concatenatedSequence.paste(image, (x_offset,0))
                x_offset += image.size[0]
            
            other224Images = (final224Indiv, final224Cap2,final224Cap3,final224Cap4)
            concatenated224Sequence = Image.new('RGB',(224*4,224))
            x_offset = 0
            for image in other224Images:
                concatenated224Sequence.paste(image, (x_offset,0))
                x_offset += image.size[0]
            
            concatenated224Sequence.save("classes/224scaledQuad/{}/sess{}_{}_resized.png".format(capLabel, sessNum, capFileNum))
            concatenatedSequence.save("classes/downscaledQuad/{}/sess{}_{}_resized.png".format(capLabel, sessNum, capFileNum))
            
                
    
    # note that this batch has been processed
    open(sessFolder + "downscaled.sentinel", "w").close()