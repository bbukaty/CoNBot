import time

import numpy as np
from PIL import Image
from pynput.keyboard import Key, Controller

import torch
import torch.nn as nn
import torchvision.transforms as transforms
from cloningCNN import CloningCNN

from necroEnv import NecroEnv

class CloningAgent:
    def __init__(self):
        if torch.cuda.is_available():
            self.device = torch.device('cuda')
        else:
            self.device = torch.device('cpu')
        self.cloningCNN = CloningCNN()
        self.cloningCNN.load_state_dict(torch.load("cloningCNN.pt"))
        self.cloningCNN.eval() # for stuff like dropout and batchnorm
        self.cloningCNN = self.cloningCNN.to(device=self.device)

        self.transform = transforms.ToTensor()

        self.keyboard = Controller()
        self.keyCodes = {1:Key.up, 2:Key.right, 3:Key.down, 4:Key.left}

        self.env = NecroEnv()
        time.sleep(0.2)
        # exit the pause menu
        self.keyboard.press(Key.esc)
        self.keyboard.release(Key.esc)

        with torch.no_grad():
            while True:
                self.act()
    
    def act(self):
        state = self.env.getState()
        x = self.transform(state).unsqueeze(0)
        print(x.shape)
        x = x.to(device=self.device, dtype=torch.float32)  # move to device, e.g. GPU
        scores = self.cloningCNN(x).data
        print(scores)

        _, pred = scores.max(1)
        action = pred.data.cpu().numpy()[0] + 1

        keyPress = self.keyCodes[action]
        self.keyboard.press(keyPress)
        self.keyboard.release(keyPress)

        time.sleep(0.6)


if __name__ == '__main__':
    agent = CloningAgent()