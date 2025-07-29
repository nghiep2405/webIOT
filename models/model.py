import torch
import torch.nn as nn
from torchvision.transforms import transforms
from torchvision import models
import firebase_admin
from firebase_admin import credentials, firestore
import logging
import cv2 as cv
from deepface import DeepFace
import numpy as np
from PIL import Image
from io import BytesIO
from torch.utils.data import DataLoader, TensorDataset
import torchvision


try:
    # Load credentials
    cred = credentials.Certificate("testh-4386a-firebase-adminsdk-fbsvc-40f75b0b3f.json")
    
    # Initialize Firebase app (nếu đã init thì không init lại)
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
        logging.info("✅ Firebase app initialized successfully.")

    # Initialize Firestore client
    db = firestore.client()

except Exception as e:
    db = None  # Set db là None để tránh lỗi sau này
    logging.error(f" Failed to initialize Firebase/Firestore: {e}")

# Get customer data
customers = db.collection("customer").select(["age_group"]).stream()

transform = transforms.Compose([
    transforms.Resize([224, 224]),
    transforms.ToTensor(),
    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
])

face_list = []
for customer in customers:
    im = Image.open(BytesIO(customer.to_dict().get("age_group")))

    face_objs = DeepFace.extract_faces(img_path = np.array(im))

    faces = [Image.fromarray((f["face"] * 255).astype(np.uint8)[..., ::-1]) for f in face_objs]
    
    face_list.extend(transform(f) for f in faces)


batch = torch.stack(face_list)
loader = DataLoader(batch, batch_size=32, shuffle=False)
net = torchvision.models.resnet50()
net.fc = nn.Linear(in_features=2048, out_features=4)
net.load_state_dict(torch.load('models/model.pth'))
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

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

# preds = torch.tensor([1, 0, 3, 2, 1, 1, 0])

counts = np.bincount(predicted_class.cpu().numpy(), minlength=len(stat))
# for i, count in enumerate(counts):
#     class_names.keys[i] = count

for idx, key in enumerate(stat.keys()):
    stat[key] += counts[idx]
  
print(stat)
    # face_img = face_objs[0]["face"]
    # print(type(face_objs))
    # # Chuyển đổi ảnh từ RGB [0,1] sang BGR [0,255]
# scale_percent = 500  # Resize xuống 50%
# width = int(face_img_bgr.shape[1] * scale_percent / 100)
# height = int(face_img_bgr.shape[0] * scale_percent / 100)
# resized_img = cv.resize(face_img_bgr, (width, height), interpolation=cv2.INTER_LINEAR)
# cv.imshow("win", face_img_bgr)
# cv.waitKey(0)
    

# Read image and detect face
# model = models.resnet50()

# model.fc = nn.Linear(2048, 4)

# model.load_state_dict(torch.load("model.pth"))

# print(model)

# group_count = {"children": 0, "teen": 0, "adult": 0, "elder": 0}
# print(type(group_count))
# print(group_count)