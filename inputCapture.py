import time
import os
import threading
from Queue import Queue
import win32gui
import mss
import mss.tools
from pynput.keyboard import Key, Listener


class InputCapture:
    def __init__(self, gameWindowName, dt):
        self.dt = dt

        try:
            self.capsFolder = "caps/" + str(int(max(os.listdir("caps"))) + 1) + "/"
        except:
            self.capsFolder = "caps/1/"
        os.mkdir(self.capsFolder)

        self.capNumber = 0
        self.isCapturing = True
        self.sct = mss.mss()

        self.keyNames = ["Up","Right","Down","Left"]
        self.keyCodes = [Key.up, Key.right, Key.down, Key.left]
        self.keyStates = {keyCode : False for keyCode in self.keyCodes}
        self.inputQueue = Queue()
        self.labelFile = open(self.capsFolder + "labels.txt", mode="a")

        self.gameBbox = self.getWindowBbox(gameWindowName)

        self.captureThread = threading.Thread(target=self.captureFrames)
        self.captureThread.start()

        with Listener(on_press=self.onKeyPress,on_release=self.onKeyRelease) as listener:
            listener.join()
            print "Listener thread joined."
        
        self.labelFile.close()

    def getWindowBbox(self, windowName):
        gameWindow = win32gui.FindWindow(None, windowName)
        if gameWindow == 0:
            print "Could not find game window for \"" + windowName + "\". Exiting."
            exit()
        win32gui.SetForegroundWindow(gameWindow)

        bbox = list(win32gui.GetWindowRect(gameWindow))
        bbox[0] += 8
        bbox[1] += 31
        width = bbox[2]-bbox[0]
        height = bbox[3]-bbox[1]
        # TODO: fix borders around window
        return {'top': bbox[1], 'left': bbox[0], 'width': width-8, 'height': height-8}
        
    def captureFrames(self):
        # TODO: see if using windows api calls is faster https://www.quora.com/How-can-we-take-screenshots-using-Python-in-Windows
        while self.isCapturing:
            tic = time.time()
            while not self.inputQueue.empty():
                currInput, isPress = self.inputQueue.get()
                self.keyStates[currInput] = isPress
            
            pressedList = '\n'
            for keyName, keyCode in zip(self.keyNames, self.keyCodes):
                pressedList += 'v' if self.keyStates[keyCode] else '^'
            self.labelFile.write(pressedList)

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

    def onKeyPress(self, key):
        if key in self.keyCodes:
            self.inputQueue.put((key, True))
        elif key == Key.esc:
            # stop the game capture thread
            self.isCapturing = False
            print('Waiting for thread...')
            self.captureThread.join()
            print('Thread joined, exiting.')
            # stop the keyboard listener thread
            return False
    
    def onKeyRelease(self, key):
        if key in self.keyCodes:
            self.inputQueue.put((key, False))

if __name__ == '__main__':
    g1 = "Crypt of the NecroDancer"
    g2 = "Risk of Rain"
    inputCapture = InputCapture(g1, 1/14.0)
