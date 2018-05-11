import time
import os, shutil
import threading
import pythoncom, pyHook 
import numpy as np
import win32gui
from Queue import Queue

import mss
import mss.tools
# import cv2
# from PIL import ImageGrab

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
        self.inputQueue = Queue()

        self.gameBbox = self.getWindowBbox(gameWindowName)

        self.captureThread = threading.Thread(target=self.captureFrames)
        self.captureThread.start()

        #insert code here for running other things
        # create a hook manager
        hm = pyHook.HookManager()
        # watch for keyboard events
        hm.KeyDown = self.onKeyboardEvent
        # set the hook
        hm.HookKeyboard()
        # wait forever
        pythoncom.PumpMessages()

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
                actionCombo +=  '_' + self.inputQueue.get()
            
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



    def onKeyboardEvent(self, event):
        # print 'MessageName:',event.MessageName
        # print 'Time:',event.Time
        # print 'WindowName:',event.WindowName
        # print 'Ascii:', event.Ascii
        # print 'Key:', event.Key
        # print '---'
        # print event.Key
        if event.Key in self.actionKeys:
            self.inputQueue.put(event.Key)
            # print('KeyboardEvent: {}'.format(self.capNumber))
        elif event.Key == "Escape":
            self.isCapturing = False
            print('Waiting for thread...')
            self.captureThread.join()
            print('Thread joined, exiting.')
            exit()
    
 
        # return True to pass the event to other handlers
        return True



if __name__ == '__main__':
    g1 = "Crypt of the NecroDancer"
    g2 = "Risk of Rain"
    inputCapture = InputCapture(g2, 1/14.0)
