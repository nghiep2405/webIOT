from deepface import DeepFace
import cv2 as cv
from PIL import Image
import numpy as np
from torchvision.transforms import transforms
import torch
from torch.utils.data import DataLoader, TensorDataset
import torchvision
import torch.nn as nn
import cv2
transform = transforms.Compose([
    transforms.Resize([224, 224]),
    transforms.ToTensor(),
    transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225))
])

im = Image.open("imgs/img2.jpg")

face_list = []

face_objs = DeepFace.extract_faces(img_path = np.array(im))

face_img_bgr = [Image.fromarray((f["face"] * 255).astype(np.uint8)[..., ::-1]) for f in face_objs]

face_list.extend(transform(f) for f in face_img_bgr)

# print(face_list)
# batch = torch.stack(face_list)

# print(batch.shape)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# print(device)
batch = torch.stack(face_list)
loader = DataLoader(batch, batch_size=2, shuffle=False)
# print(loader)
net = torchvision.models.resnet50()
net.fc = nn.Linear(in_features=2048, out_features=4)
net.load_state_dict(torch.load('models/model.pth'))
net.eval()

ou = []
with torch.no_grad():
    for batch in loader:
        net.to(device)
        ou.append(net(batch.to(device)))

output = torch.cat(ou)

# import torch.nn.functional as F
# 4. Softmax để ra xác suất
probabilities = torch.softmax(output, dim=1)
print(probabilities)
# 5. Lấy class dự đoán cao nhất
predicted_class = torch.argmax(probabilities, 1)
# print(predicted_class.cpu())

stat = {"children": 0, "teen": 0, "aldult": 0, "elderly": 0}
class_name = ["children", "teen", "aldult", "elderly"]
# preds = torch.tensor([1, 0, 3, 2, 1, 1, 0])

counts = np.bincount(predicted_class.cpu().numpy(), minlength=len(stat))
# for i, count in enumerate(counts):
#     class_names.keys[i] = count
print(counts)
for idx, key in enumerate(stat.keys()):
    stat[key] += counts[idx]
  
print(stat)
# print(type(face_list[0]))
# face_img = face_objs[0]["face"]
# print(type(face_objs))
  # Chuyển đổi ảnh từ RGB [0,1] sang BGR [0,255]
# face_img_bgr = cv2.cvtColor((face_img * 255).astype(np.uint8), cv2.COLOR_RGB2BGR)
# scale_percent = 500  # Resize xuống 50%
# width = int(face_img_bgr.shape[1] * scale_percent / 100)
# height = int(face_img_bgr.shape[0] * scale_percent / 100)
# resized_img = cv2.resize(face_img_bgr, (width, height), interpolation=cv2.INTER_LINEAR)
# cv.imshow("win", face_img_bgr)
# cv.waitKey(0)
# for i, face in enumerate(face_objs):
#     face_img = face["face"]
#     # Chuyển đổi ảnh từ RGB [0,1] sang BGR [0,255]
#     face_img_bgr = cv2.cvtColor((face_img * 255).astype(np.uint8), cv2.COLOR_RGB2BGR)
#     cv2.imwrite(f"face_{i+1}.jpg", face_img_bgr)