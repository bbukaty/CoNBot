import time
import os, shutil
import threading
from pynput.keyboard import Key, Listener
import win32gui
from Queue import Queue

import mss
import mss.tools

class InputCapture:
    def __init__(self, gameWindowName, dt):
        self.dt = dt

        self.capsFolder = "caps/testing/"
        shutil.rmtree(self.capsFolder)
        os.mkdir(self.capsFolder)

        self.capNumber = 0
        self.isCapturing = True
        self.sct = mss.mss()

        self.actionKeys = ["Down","Up","Right","Left"]
        self.keyCodes = [Key.down, Key.up, Key.right, Key.left]
        self.inputQueue = Queue()

        self.gameBbox = self.getWindowBbox(gameWindowName)

        self.captureThread = threading.Thread(target=self.captureFrames)
        self.captureThread.start()

        with Listener(on_press=self.onKeyboardEvent,on_release=self.onKeyboardEvent) as listener:
            print "Joining key listener..."
            listener.join()
            print "Joined."

    def getWindowBbox(self, windowName):
        gameWindow = win32gui.FindWindow(None, windowName)
        if gameWindow == 0:
            print "Could not find game window for \"" + windowName + "\". Exiting."
            exit()
        win32gui.SetForegroundWindow(gameWindow)

        bbox = win32gui.GetWindowRect(gameWindow)
        width = bbox[2]-bbox[0]
        height = bbox[3]-bbox[1]
        # TODO: fix borders around window
        return {'top': bbox[1], 'left': bbox[0], 'width': width, 'height': height}
        
    def captureFrames(self):
        # TODO: see if using windows api calls is faster https://www.quora.com/How-can-we-take-screenshots-using-Python-in-Windows
        while self.isCapturing:
            tic = time.time()
            actionCombo = ''
            while not self.inputQueue.empty():
                actionCombo +=  '_{}'.format(self.inputQueue.get())
            
            # Grab the data
            sct_img = self.sct.grab(self.gameBbox)
            # Save to the picture file
            fileName = self.capsFolder + str(self.capNumber) + actionCombo + ".png"
            mss.tools.to_png(sct_img.rgb, sct_img.size, output=fileName)

            self.capNumber += 1

            sleepAmount = self.dt-(time.time()-tic)
            if sleepAmount < 0:
                print 'Lagging, missed frame by {}'.format(-sleepAmount)
                sleepAmount = 0
            time.sleep(sleepAmount)

    def onKeyboardEvent(self, key):
        if key in self.keyCodes:
            self.inputQueue.put(key)
        elif key == Key.esc:
            # stop the game capture thread
            self.isCapturing = False
            print('Waiting for thread...')
            self.captureThread.join()
            print('Thread joined, exiting.')
            # stop the keyboard listener thread
            return False

if __name__ == '__main__':
    g1 = "Crypt of the NecroDancer"
    g2 = "Risk of Rain"
    inputCapture = InputCapture(g2, 1/14.0)
