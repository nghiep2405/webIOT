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
from torch.utils.data import DataLoader
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
    transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225))
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

# Softmax để ra xác suất
probabilities = torch.softmax(output, dim=1)
print(probabilities)
# Lấy class dự đoán cao nhất
predicted_class = torch.argmax(probabilities, 1)
# print(predicted_class.cpu())

stat = {"children": 0, "teen": 0, "aldult": 0, "elderly": 0}

# Đếm số lượng
counts = np.bincount(predicted_class.cpu().numpy(), minlength=len(stat))
for idx, key in enumerate(stat.keys()):
    stat[key] += counts[idx]
  
print(stat)