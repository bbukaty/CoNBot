import time
import threading
import pythoncom, pyHook 
import numpy as np
import win32gui

import mss
import mss.tools
# import cv2
# from PIL import ImageGrab

class InputCapture:
    def __init__(self, gameWindowName="Crypt of the NecroDancer", dt=1/10.0):
        self.gameWindowName = gameWindowName
        self.dt = dt

        self.actionKeys = ["Down","Up","Right","Left"]
        self.capNumber = 0
        self.capsFolder = "caps/testing/"
        self.isCapturing = True

        self.sct = mss.mss()

        gameWindow = win32gui.FindWindow(None, self.gameWindowName)
        if gameWindow == 0:
            print "Could not find game window for \"" + self.gameWindowName + "\". Exiting."
            exit()
        win32gui.SetForegroundWindow(gameWindow)
        bbox = win32gui.GetWindowRect(gameWindow)
        print(bbox)
        width = bbox[2]-bbox[0]
        height = bbox[3]-bbox[1]
        self.gameBbox = {'top': bbox[1], 'left': bbox[0], 'width': width, 'height': height}
        print self.gameBbox

        self.captureThread = threading.Thread(target=self.captureFrames)
        
        self.captureThread.start()

        #insert code here for running other things
        # create a hook manager
        hm = pyHook.HookManager()
        # watch for all mouse events
        hm.KeyDown = self.onKeyboardEvent
        # set the hook
        hm.HookKeyboard()
        # wait forever
        pythoncom.PumpMessages()
        
    def captureFrames(self):
        # TODO: see if using windows api calls is faster https://www.quora.com/How-can-we-take-screenshots-using-Python-in-Windows
        while self.isCapturing:
            try:
                tic = time.time()
                # Grab the data
                sct_img = self.sct.grab(self.gameBbox)
                # Save to the picture file
                fileName = self.capsFolder + str(self.capNumber) + ".png"
                mss.tools.to_png(sct_img.rgb, sct_img.size, output=fileName)

                self.capNumber += 1

                sleepAmount = self.dt-(time.time()-tic)
                if sleepAmount < 0:
                    print 'Lagging, missed frame by {}'.format(-sleepAmount)
                    sleepAmount = 0
                time.sleep(sleepAmount)
            except IOError:
                pass


    def onKeyboardEvent(self, event):
        # print 'MessageName:',event.MessageName
        # print 'Time:',event.Time
        # print 'WindowName:',event.WindowName
        # print 'Ascii:', event.Ascii
        # print 'Key:', event.Key
        # print '---'
        # print event.Key
        if event.Key in self.actionKeys:
            # Grab the data
            sct_img = self.sct.grab(self.gameBbox)
            # Save to the picture file
            fileName = self.capsFolder + str(self.capNumber) + event.Key + ".png"
            mss.tools.to_png(sct_img.rgb, sct_img.size, output=fileName)
            # print('KeyboardEvent: {}'.format(self.capNumber))
            self.capNumber += 1
        elif event.Key == "Escape":
            self.isCapturing = False
            print('Waiting for thread...')
            self.captureThread.join()
            print('Thread joined, exiting.')
            exit()
    
 
        # return True to pass the event to other handlers
        return True



if __name__ == '__main__':
    inputCapture = InputCapture(dt=2.0)
