import os
import time
import threading
from queue import Queue
import win32gui
import mss
import mss.tools
from pynput.keyboard import Key, Listener


class InputCapture:
    def __init__(self, gameWindowName, dt, sessionsFolder):
        self.dt = dt
        if not os.path.isdir(sessionsFolder):
            print("Error: Sessions directory {} is not a valid directory. Aborting.".format(sessionsFolder))
            exit()
        try:
            sessNums = [int(folderName) for folderName in os.listdir(sessionsFolder)]
            self.sessFolder = "{}/{}/".format(sessionsFolder, max(sessNums)+1)
        except:
            self.sessFolder = "{}/1/".format(sessionsFolder)
        os.mkdir(self.sessFolder)
        self.capsFolder = self.sessFolder + "caps/"
        os.mkdir(self.capsFolder)

        self.gameBbox = self.getWindowBbox(gameWindowName)
        self.capNumber = 0
        self.isCapturing = True
        self.sct = mss.mss()

        self.keys = {Key.up:1, Key.right:2, Key.down:3, Key.left:4}

        self.labelFile = open(self.sessFolder + "labels.txt", mode="a")

        with Listener(on_press=self.onKeyPress) as listener:
            listener.join()
            print("Listener thread joined.")
        
        self.labelFile.close()

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

    def onKeyPress(self, key):
        if key in self.keys: # discard input not in the list of expected keys
            # Grab the data
            sct_img = self.sct.grab(self.gameBbox)
            # Save to the picture file
            fileName = "{}{}.png".format(self.capsFolder, self.capNumber)
            mss.tools.to_png(sct_img.rgb, sct_img.size, output=fileName)

            self.labelFile.write("{}\n".format(self.keys[key]))
            self.capNumber += 1
        elif key == Key.esc:
            # stop the keyboard listener thread
            return False

if __name__ == '__main__':
    g1 = "Crypt of the NecroDancer"
    g2 = "Risk of Rain"
    inputCapture = InputCapture(g1, 1/14.0, "sessions")
