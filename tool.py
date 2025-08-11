import firebase_admin
from firebase_admin import credentials, firestore
from fastapi import FastAPI, Request, HTTPException, Body
from contextlib import asynccontextmanager
import logging
from pydantic import BaseModel
from datetime import datetime, timedelta
from pytz import timezone, UTC
from PIL import Image
import base64
from io import BytesIO
import torch
import torch.nn as nn
from torchvision.transforms import transforms
from deepface import DeepFace
import numpy as np
from torch.utils.data import DataLoader
import torchvision
from concurrent.futures import ThreadPoolExecutor
import asyncio  
from google.cloud.firestore_v1.base_query import FieldFilter, And

executor = ThreadPoolExecutor(max_workers=4)
# net = None
# device = "cpu"

@asynccontextmanager
async def lifespan(app: FastAPI):
    global device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    global net
    net = torchvision.models.resnet50()
    net.fc = nn.Linear(in_features=2048, out_features=4)
    net.load_state_dict(torch.load('models/model.pth'))
    net.to(device)
    yield
    net = None
    
enter_info = {
    "Timestamp": []
}

app = FastAPI(lifespan=lifespan)

try:
    # Load credentials
    cred = credentials.Certificate("testh-4386a-firebase-adminsdk-fbsvc-40f75b0b3f.json")
    
    # Initialize Firebase app (nếu đã init thì không init lại)
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
        logging.info("✅ Firebase app initialized successfully.")

    # Initialize Firestore client
    db = firestore.client()

    # Test query để chắc chắn kết nối
    test = list(db.collections())  # Lấy danh sách collection để kiểm tra kết nối
    logging.info("✅ Connected to Firestore successfully.")

except Exception as e:
    db = None  # Set db là None để tránh lỗi sau này
    logging.error(f" Failed to initialize Firebase/Firestore: {e}")
    
class SoundHistoryRequest(BaseModel):
    user_name: str
    sound_name: str

@app.post("/register")
def register_user(name: str, password: str):
    try:
        if not name or not password:
            raise HTTPException(status_code=400, detail="Name and password are required")
        existing_users = db.collection("users").where("name", "==", name).stream()
        existing_user = next(existing_users, None)
        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists")
        
        user = db.collection("users").add({"name": name, "password": password})
        return {"message": "User registered successfully", "uid": user[1].id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/login")
def login_user(name: str, password: str):
    users = db.collection("users").where("name", "==", name).where("password", "==", password).stream()
    user = next(users, None)
    if user:
        return {"message": "Login successful", "uid": user.id}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")  
    
@app.post("/save-sound-history")
def save_sound_history(request: SoundHistoryRequest):
    try:
        # Tạo timestamp với định dạng đầy đủ
        timestamp = datetime.now()
        
        # Tạo dữ liệu lịch sử
        history_data = {
            "user_name": request.user_name,
            "sound_name": request.sound_name,
            "timestamp": timestamp,
        }
        
        # Lưu vào collection "sound_history"
        doc_ref = db.collection("sound_history").add(history_data)
        
        # Format timestamp cho response
        formatted_time = timestamp.strftime("%d/%m/%Y %H:%M:%S")
        
        return {
            "message": "Sound history saved successfully", 
            "doc_id": doc_ref[1].id,
            "timestamp": formatted_time
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving sound history: {str(e)}")

@app.get("/get-sound-history")
def get_sound_history():
    try:
        # Lấy tất cả lịch sử, sắp xếp theo thời gian mới nhất
        history_ref = db.collection("sound_history").order_by("timestamp", direction=firestore.Query.DESCENDING)
        docs = history_ref.stream()
        
        history_list = []
        for doc in docs:
            data = doc.to_dict()
            # Format timestamp khi cần thiết
            raw_timestamp = data.get("timestamp")
            formatted_time = raw_timestamp.strftime("%d/%m/%Y %H:%M:%S") if raw_timestamp else ""
            history_list.append({
                "id": doc.id,
                "user_name": data.get("user_name", ""),
                "sound_name": data.get("sound_name", ""),
                "timestamp": formatted_time,  # Hiển thị format
            })
        
        return {"history": history_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting sound history: {str(e)}")
    
@app.get("/get-info-customers")
def get_info_customers():
    try:
        customers_ref = db.collection("customer").order_by("come_in", direction=firestore.Query.DESCENDING)
        docs = customers_ref.stream()

        customers_list = []
        for doc in docs:
            data = doc.to_dict()
            raw_come_in = data.get("come_in", None)
            formatted_come_in = ""

            tz_vn = timezone("Asia/Ho_Chi_Minh")
            if isinstance(raw_come_in, datetime):
                if raw_come_in.tzinfo is None:
                    raw_come_in = UTC.localize(raw_come_in)
                dt_vn = raw_come_in.astimezone(tz_vn)
                formatted_come_in = dt_vn.strftime("%d/%m/%Y %H:%M:%S")
            else:
                formatted_come_in = str(raw_come_in)

            try:
                parts = formatted_come_in.split(" ")
                date_parts = parts[0].split("/")
                reversed_date = f"{date_parts[1]}/{date_parts[0]}/{date_parts[2]}"
                formatted_come_in = f"{reversed_date} {parts[1]}"
            except Exception as e:
                pass  # fallback nếu lỗi split

            customers_list.append({
                "come_in": formatted_come_in,
            })

        print(customers_list)
        return {"customers": customers_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting customer info: {str(e)}")

@app.get("/get-info-age-customers")
def get_info_age_customers():
    try:
        customers_ref = db.collection("customer_classification").order_by("date", direction=firestore.Query.DESCENDING)
        docs = customers_ref.stream()

        customers_list = []
        for doc in docs:
            data = doc.to_dict()
            raw_date = data.get("date", None)
            formatted_date = ""

            tz_vn = timezone("Asia/Ho_Chi_Minh")
            if isinstance(raw_date, datetime):
                if raw_date.tzinfo is None:
                    raw_date = UTC.localize(raw_date)
                dt_vn = raw_date.astimezone(tz_vn)
                formatted_date = dt_vn.strftime("%d/%m/%Y %H:%M:%S")
            else:
                formatted_date = str(raw_date)

            try:
                parts = formatted_date.split(" ")
                date_parts = parts[0].split("/")
                reversed_date = f"{date_parts[1]}/{date_parts[0]}/{date_parts[2]}"
                formatted_date = f"{reversed_date} {parts[1]}"
            except Exception:
                pass

            customers_list.append({
                "adult": int(data.get("adult", 0)),
                "children": int(data.get("children", 0)),
                "elderly": int(data.get("elderly", 0)),
                "teen": int(data.get("teen", 0)),
                "date": formatted_date,
            })

        return {"age_customers": customers_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting age customer info: {str(e)}")
    

@app.post("/upload/")
async def upload_raw_image(data: bytes = Body(..., media_type="image/jpeg")):
    time = datetime.now()
    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")

    if (len(enter_info["Timestamp"]) > 0 and time.date() != enter_info["Timestamp"][-1]):
        enter_info["Timestamp"].clear()

    enter_info["Timestamp"].append(time)
    path = f"imgs/{timestamp}.jpg"
    with open(path, "wb") as f:
        f.write(data)

    # Mã hóa base64
    image_base64 = base64.b64encode(data).decode('utf-8')

    try:
        db.collection("customer").add({
            "come_in": time,
            "image_path": path,               
            "image_base64": image_base64      
        })
    except Exception as e:
        logging.error(f"Error saving customer data: {e}")
        raise HTTPException(status_code=500, detail="Error saving customer data")
    
    return {"Status": "Success"}

@app.get("/get_enter")
async def get_enter():
    try:
        data = enter_info["Timestamp"].copy()
        l = len(data)
        if l > 0:
            enter_info["Timestamp"] = enter_info["Timestamp"][l:]
        return {"Timestamp": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting customer info: {str(e)}")
    
def base64_to_pil(b64_string: str) -> Image.Image:
    if b64_string.startswith("data:image"):
        b64_string = b64_string.split(",", 1)[1]
    image_bytes = base64.b64decode(b64_string)

    image_stream = BytesIO(image_bytes)
    img = Image.open(image_stream)
    return img

def run_model():
    start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)

    filters = And([
        FieldFilter("come_in", ">=", start),
        FieldFilter("come_in", "<", end)
    ])

    customers = (
        db.collection("customer")
        .select(["image_base64"])
        .where(filter=filters)
        .stream()
    )

    transform = transforms.Compose([
        transforms.Resize([224, 224]),
        transforms.ToTensor(),
        transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225))
    ])

    face_list = []
    for customer in customers:
        data = customer.to_dict()
        image_base64 = data["image_base64"]  # Lấy chuỗi base64 từ document
        im = base64_to_pil(image_base64)

        face_objs = DeepFace.extract_faces(img_path=np.array(im)[:,:,::-1], enforce_detection=False)

        faces = [Image.fromarray((f["face"] * 255).astype(np.uint8)) for f in face_objs]
        
        face_list.extend(transform(f) for f in faces)

    if face_list:
        batch = torch.stack(face_list)
    else:
        batch = torch.empty((0, 3, 224, 224), dtype=torch.float32)
    loader = DataLoader(batch, batch_size=32, shuffle=False)
    
    net.eval()

    ou = []
    with torch.no_grad():
        for batch in loader:
            ou.append(net(batch.to(device)))

    if ou:
        output = torch.cat(ou)
    else:
        output = torch.empty((0, 4), device=device)

    # Softmax để ra xác suất
    probabilities = torch.softmax(output, dim=1)
    # Lấy class dự đoán cao nhất
    predicted_class = torch.argmax(probabilities, 1)

    stat = {"children": 0, "teen": 0, "aldult": 0, "elderly": 0}

    # Đếm số lượng
    counts = np.bincount(predicted_class.cpu().numpy(), minlength=len(stat))
    for idx, key in enumerate(stat.keys()):
        stat[key] += int(counts[idx])

    store = {"date": start, **stat}

    db.collection("customer_classification").add(store)

@app.post("/analyze")
async def start_analyze():
    loop = asyncio.get_running_loop()
    loop.run_in_executor(executor, run_model)
    return {"Status": "Queued"}


# # API để lấy thông tin độ tuổi
