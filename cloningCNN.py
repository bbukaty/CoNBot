import torch 
import torch.nn as nn

num_classes = 4

def flatten(x):
    N = x.shape[0] # read in N, C, H, W
    return x.view(N, -1)  # "flatten" the C * H * W values into a single vector per image

# We need to wrap `flatten` function in a module in order to stack it
# in nn.Sequential
class Flatten(nn.Module):
    def forward(self, x):
        return flatten(x)

class CloningCNN(nn.Sequential):
    def __init__(self):
        super().__init__(
            nn.Conv2d(3, 32, 6, stride=3, padding=9), # 32x64x64
            nn.ReLU(),
            nn.Conv2d(32, 16, 3, stride=1, padding=1), # 16x64x64
            nn.ReLU(),
            nn.Conv2d(16, 16, 3, stride=2, padding=0), # 16x32x32
            nn.ReLU(),
        #     nn.Conv2d(32, 16, 3, padding=1),
        #     nn.ReLU(),
        #     nn.Conv2d(16, 16, 3, padding=1),
        #     nn.ReLU(),
            Flatten(),
            nn.Linear(16*32*32, 200),
            nn.Linear(200, 60),
            nn.Linear(60, num_classes),
        )
