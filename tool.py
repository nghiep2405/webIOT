import firebase_admin
from firebase_admin import credentials, firestore
from fastapi import FastAPI, Request, HTTPException
import logging
from pydantic import BaseModel
from datetime import datetime
from pytz import timezone, UTC

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
                # Nếu không có tzinfo, giả sử là UTC rồi chuyển về VN
                if raw_come_in.tzinfo is None:
                    raw_come_in = UTC.localize(raw_come_in)
                dt_vn = raw_come_in.astimezone(tz_vn)
                formatted_come_in = dt_vn.strftime("%d/%m/%Y %H:%M:%S")
            else:
                formatted_come_in = str(raw_come_in)

            customers_list.append({
                "age_group": data.get("age_group", ""),
                "come_in": formatted_come_in,
            })

        return {"customers": customers_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting customer info: {str(e)}")
    
# API để khởi tạo dữ liệu khách hàng ảo
@app.post("/init-fake-customers")
def init_fake_customers():
    try:
        fake_data = [
            # {"age_group": "Elderly", "come_in": "23/07/2025 07:38:22"},
            # {"age_group": "Children", "come_in": "21/07/2025 22:23:05"},
            # {"age_group": "Teen", "come_in": "20/07/2025 10:15:00"},
            # {"age_group": "Adult", "come_in": "19/07/2025 14:45:30"},
            # {"age_group": "Elderly", "come_in": "18/07/2025 09:00:00"},
            # {"age_group": "Adult", "come_in": "17/07/2025 16:20:10"},
            # {"age_group": "Teen", "come_in": "16/07/2025 11:11:11"},
            # {"age_group": "Children", "come_in": "15/07/2025 08:08:08"},
            # {"age_group": "Elderly", "come_in": "14/07/2025 20:20:20"},
            {"age_group": "Teen", "come_in": "23/07/2025 13:13:13"},
        ]
        for item in fake_data:
            # Lưu vào Firestore, parse come_in sang datetime nếu cần
            try:
                come_in_dt = datetime.strptime(item["come_in"], "%d/%m/%Y %H:%M:%S")
            except Exception:
                come_in_dt = item["come_in"]
            db.collection("customer").add({
                "age_group": item["age_group"],
                "come_in": come_in_dt
            })
        return {"message": "Fake customers initialized successfully", "count": len(fake_data)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error initializing fake customers: {str(e)}")