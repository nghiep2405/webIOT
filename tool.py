import firebase_admin
from firebase_admin import credentials, firestore
from fastapi import FastAPI, Request, HTTPException
import logging

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