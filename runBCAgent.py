import time

import numpy as np
from PIL import Image
from pynput.keyboard import Key, Controller

import torch 
import torchvision
import torch.nn as nn

from necroEnv import NecroEnv

# keyboard.press(Key.space)
# keyboard.release(Key.space)

class BCAgent:
    def __init__(self):
        self.keyboard = Controller()
        self.keyCodes = {1:Key.up, 2:Key.right, 3:Key.down, 4:Key.left}
        self.env = NecroEnv()
        time.sleep(0.2)
        # exit the pause menu
        self.keyboard.press(Key.esc)
        self.keyboard.release(Key.esc)

        while True:
            state = self.env.getState()
            action = self.keyCodes[2]
            self.keyboard.press(action)
            self.keyboard.release(action)
            time.sleep(2)


if __name__ == '__main__':
    agent = BCAgent()