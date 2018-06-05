import torch 
import torch.nn as nn
import torchvision.models as models

num_classes = 4

def flatten(x):
    N = x.shape[0] # read in N, C, H, W
    return x.view(N, -1)  # "flatten" the C * H * W values into a single vector per image

# We need to wrap `flatten` function in a module in order to stack it
# in nn.Sequential
class Flatten(nn.Module):
    def forward(self, x):
        return flatten(x)

class LinearClassifier(nn.Sequential):
    def __init__(self, dropout=0.5):
        super().__init__(
        nn.Linear(16*32*32*4,200),
        nn.ReLU(),
        nn.Dropout(dropout),
        nn.Linear(200,60),
        nn.ReLU(),
        nn.Dropout(dropout),
        nn.Linear(60,num_classes)
        )
    
class ResNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.resnet = models.resnet34(pretrained=False)
        self.resnet.conv1 = nn.Conv2d(12, 64, kernel_size=7, stride=2, padding=3, bias=False)
#         for param in self.resnet.parameters():
#             param.requires_grad = False
        
#         for param in self.resnet.avgpool.parameters():
#             param.requires_grad = True
        
#         for param in self.resnet.layer4.parameters():
#             param.requires_grad = True
        
#         for param in self.resnet.layer3.parameters():
#             param.requires_grad = True
        
        self.resnet.fc = nn.Linear(512,4)
        #https://pytorch.org/docs/master/notes/autograd.html
        #https://discuss.pytorch.org/t/how-to-perform-finetuning-in-pytorch/419/9
    def forward(self, x):
        return self.resnet(x)
        
        

class CloningCNN(nn.Sequential):
    def __init__(self, netType, dropout=0.5, hasFC=True, inChannels=3):
        if netType == 'original':
            '''
            Original model, uses weird padding/stride
            '''
            super().__init__(
            nn.Conv2d(inChannels, 32, 6, stride=3, padding=9), # 32x64x64
            nn.ReLU(),
            nn.Conv2d(32, 16, 3, stride=1, padding=1), # 16x64x64
            nn.ReLU(),
            nn.Conv2d(16, 16, 3, stride=2, padding=0), # 16x32x32
            nn.ReLU(),
            Flatten()
            )
            if hasFC:
                super().add_module("linear1", nn.Linear(16*32*32, 200))
                super().add_module("relu1", nn.ReLU())
                super().add_module("linear2", nn.Linear(200, 60))
                super().add_module("relu2", nn.ReLU())
                super().add_module("linear3", nn.Linear(60, num_classes))
        elif netType == 'improved':
            '''
            ""Improved"" architecture, using batchnorm and dropout, not very different in architecture from above
            '''
            super().__init__(
            nn.Conv2d(inChannels, 32, 6, stride=3, padding=9), # 32x64x64
            nn.ReLU(),
            nn.BatchNorm2d(32),
            nn.Conv2d(32, 16, 3, stride=1, padding=1), # 16x64x64
            nn.ReLU(),
            nn.BatchNorm2d(16),
            nn.Conv2d(16, 16, 3, stride=2, padding=0), # 16x32x32
            nn.ReLU(),
            # nn.BatchNorm2d(16), not sure how much batch norm is too much...?
            Flatten()
            )
            if hasFC:
                super().add_module("linear1", nn.Linear(16*32*32,200))
                super().add_module("relu1", nn.ReLU())
                super().add_module("drop1", nn.Dropout(dropout))
                super().add_module("linear2", nn.Linear(200,60)) #this and next line maybe overkill linear
                super().add_module("relu2", nn.ReLU())
                super().add_module("drop2", nn.Dropout(dropout))
                super().add_module("linear3", nn.Linear(60, num_classes))
        elif netType == 'deeper':
            super().__init__(
            nn.Conv2d(inChannels, 32, 6, stride=3, padding=9), # 32x64x64
            nn.ReLU(),
            nn.BatchNorm2d(32),
            nn.Conv2d(32, 32, 3, stride=1, padding=1), # 32x64x64
            nn.ReLU(),
            nn.BatchNorm2d(32),
            nn.Conv2d(32, 32, 3, stride=1, padding=1), # 32x64x64
            nn.ReLU(),
            nn.MaxPool2d(2), # 32x32x32
            nn.BatchNorm2d(32), #not sure how much batch norm is too much...?
            nn.Conv2d(32, 32, 3, stride=1, padding=1), # 32x32x32
            nn.ReLU(),
            nn.BatchNorm2d(32),
            nn.Conv2d(32, 32, 3, stride=1, padding=1), # 32x32x32
            nn.ReLU(),
            nn.MaxPool2d(2), # 32x16x16
            nn.BatchNorm2d(32),
            Flatten()
            )
            if hasFC:
                super().add_module("linear1", nn.Linear(32*16*16,200))
                super().add_module("relu1", nn.ReLU())
                super().add_module("drop1", nn.Dropout(dropout))
                super().add_module("linear2", nn.Linear(200,60)) #this and next line maybe overkill linear
                super().add_module("relu2", nn.ReLU())
                super().add_module("drop2", nn.Dropout(dropout))
                super().add_module("linear3", nn.Linear(60, num_classes))
                
    def reinitializeFC(self, numReinitialize=2):
        currentLayer = 1
        for name, module in super().named_children():
            if name[:6] == "linear":
                if currentLayer >= numReinitialize:
                    module.reset_parameters()
                currentLayer = currentLayer+1

        
        
class MultiSequentialCNN(nn.Module):
    def __init__(self, netType, dropout=0.5):
        super().__init__()
        self.CNN = CloningCNN(netType, hasFC=False)
        self.linear = LinearClassifier(dropout)
    
    def forward(self, x):
        #expects a 4-tuple of 3x180x180 images, in order current -> 1 timestep ago ->... ->3 timesteps ago
        lin1 = self.CNN(x[0])
        lin2 = self.CNN(x[1])
        lin3 = self.CNN(x[2])
        lin4 = self.CNN(x[3])
        lin = torch.cat((lin1,lin2,lin3,lin4),dim=1)
        return self.linear(lin)
        
        
        
        
        