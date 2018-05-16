import os
import numpy as np
from PIL import Image, ImageOps

meanImage = np.load("stats/dsetMean.npy")
stdImage = np.load("stats/dsetStd.npy")

for classNum in os.listdir("classes/images"):
    classFolder = "classes/images/{}/".format(classNum)
    for imageName in os.listdir(classFolder):
        imgArr = np.array(Image.open(classFolder + imageName), np.float64)
        # os.remove(classFolder + imageName)
        normalized = (imgArr - meanImage) / stdImage
        normalized[stdImage == 0] = 0
        
        np.save("classes/numpy/{}/".format(classNum) + imageName[:-4], normalized)