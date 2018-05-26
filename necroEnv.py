import numpy as np
import win32gui
import mss
import mss.tools
from PIL import Image, ImageOps


class NecroEnv:
    def __init__(self):
        self.windowName = "Crypt of the NecroDancer"
        self.gameBbox = self.getWindowBbox(self.windowName)
        self.capper = mss.mss()
        self.downsamplingMethod = Image.NEAREST
        try:
            self.meanImage = np.load("stats/dsetMean.npy")
            self.stdImage = np.load("stats/dsetStd.npy")
        except:
            print("Couldn't find train dataset statistics. Aborting.")
        self.capNum = 0

    def getWindowBbox(self, windowName):
        gameWindow = win32gui.FindWindow(None, windowName)
        if gameWindow == 0:
            print("Could not find game window for \"" + windowName + "\". Exiting.")
            exit()
        win32gui.SetForegroundWindow(gameWindow)

        bbox = list(win32gui.GetWindowRect(gameWindow))
        # fix idiosyncrasies of win32gui window rect acquisition
        bbox[0] += 8
        bbox[1] += 31
        width = bbox[2]-bbox[0]
        height = bbox[3]-bbox[1]
        # return a 'monitor' object in the format that the mss library wants
        return {'top': bbox[1], 'left': bbox[0], 'width': width-8, 'height': height-8}

    def getState(self):
        if win32gui.GetWindowText(win32gui.GetForegroundWindow()) != self.windowName:
            print("Game window no longer active. Exiting.")
            exit()
        
        self.capNum += 1
        screenCap = self.capper.grab(self.gameBbox)
        mss.tools.to_png(screenCap.rgb, screenCap.size, output="testing/{}.png".format(self.capNum))
        # img = Image.frombytes('RGB', screenCap.size, screenCap.bgra, 'raw', 'BGRX')
        img = Image.open("testing/{}.png".format(self.capNum))
        # add padding, this makes the image a pixel-perfect 15x15 grid of Crypt tiles
        padded = ImageOps.expand(img, (30,38,26,18))
        # each 'pixel' in the game is actually a 3x3 grid of pixels, so this first downscale by 3 has no data loss
        resized = padded.resize((360,360), self.downsamplingMethod)
        # now the lossy resize to the final size
        final = resized.resize((180,180), self.downsamplingMethod)
        final.save("testing/{}.png".format(self.capNum))
        imgArr = np.array(final, np.float64)
        normalized = (imgArr - self.meanImage) / self.stdImage
        normalized[self.stdImage == 0] = 0
        return normalized