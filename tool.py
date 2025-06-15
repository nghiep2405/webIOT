import firebase_admin
from firebase_admin import credentials, firestore
from fastapi import FastAPI, Request, HTTPException
import logging
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()

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