import time
import threading
import pythoncom, pyHook 
import numpy as np
import win32gui
import cv2
from PIL import ImageGrab

class InputCapture:
    def __init__(self, gameWindowName="Crypt of the NecroDancer", dt=1/6.0):
        self.actionKeys = ["Down","Up","Right","Left"]
        self.capNumber = 0
        self.isCapturing = True
        self.dt = dt

        self.gameWindowName = gameWindowName

        # weird pywingui stuff to get the window size for the game
        # only way to access window objects is by iterating through a list of them??
        game_bbox = [None]
        def enumForBbox(window, bbox_list):
            if win32gui.GetWindowText(window) == gameWindowName:
                win32gui.SetForegroundWindow(window)
                bbox_list[0] = win32gui.GetWindowRect(window)
        win32gui.EnumWindows(enumForBbox, game_bbox)
        self.gameBbox = game_bbox[0]

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
        while self.isCapturing:
            try:
                tic = time.time()
                cap =  np.array(ImageGrab.grab(self.gameBbox))
                cv2.imwrite("caps/"+ str(self.capNumber) + ".png", cv2.cvtColor(cap, cv2.COLOR_BGR2RGB))
                # print('Caploop: {}'.format(self.capNumber))
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
            cap = np.array(ImageGrab.grab(self.gameBbox))
            cv2.imwrite("caps/"+ str(self.capNumber) + event.Key + ".png", cv2.cvtColor(cap, cv2.COLOR_BGR2RGB))
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
    inputCapture = InputCapture()