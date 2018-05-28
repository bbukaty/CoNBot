import os
import numpy as np
from PIL import Image

# calculate number of training examples to use in our running mean
numTrain = 0
for label in os.listdir("classes/downscaledIndiv"):
    numTrain += len(os.listdir("classes/downscaledIndiv/{}/".format(label)))
print("Found {} training images.".format(numTrain))

# init empty arrays for mean image
meanImage = np.zeros((180,180,3), np.float)
meanImageSquared = np.zeros_like(meanImage)

for label in os.listdir("classes/downscaledIndiv"):
    classFolder = "classes/downscaledIndiv/{}/".format(label)

    for imageName in os.listdir(classFolder):
        resizedImage = Image.open(classFolder + imageName)
        meanImage += np.array(resizedImage, np.float64) / numTrain
        meanImageSquared += np.array(resizedImage, np.float64)**2 / numTrain

diff = np.maximum(meanImageSquared - meanImage**2, 0) # fix minor numerical instabilities
stdImage = np.sqrt(diff)

np.save("stats/dsetMean", meanImage)
np.save("stats/dsetStd", stdImage)