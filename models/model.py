import torch
import torch.nn as nn
import torch.version
from torchvision import models
# import torchvision


# model = models.resnet50()

# model.fc = nn.Linear(2048, 4)

# model.load_state_dict(torch.load("model.pth"))

# print(model)

group_count = {"children": 0, "teen": 0, "adult": 0, "elder": 0}
print(type(group_count))
print(group_count)