import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import os
import hashlib

# ==========================================
# 🔥 1. KHỞI TẠO KẾT NỐI FIREBASE
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KEY_PATH = os.path.join(BASE_DIR, "firebase_key.json")

if not firebase_admin._apps:
    if os.path.exists(KEY_PATH):
        cred = credentials.Certificate(KEY_PATH)
        firebase_admin.initialize_app(cred)
    else:
        cred = credentials.ApplicationDefault() 
        firebase_admin.initialize_app(cred, {
            'projectId': 'iot-secod-year',
        })

db = firestore.client()

# ==========================================
# 🔐 2. HỆ THỐNG XÁC THỰC (AUTH)
# ==========================================
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(email: str, password: str, nickname: str) -> dict:
    try:
        users_ref = db.collection("users")
        query = users_ref.where("email", "==", email).get()
        if len(query) > 0:
            return {"success": False, "error": "Email này đã được đăng ký!"}
        
        hashed_pw = hash_password(password)
        new_user_ref = users_ref.document()
        user_data = {
            "email": email,
            "password": hashed_pw,
            "name": nickname,
            "createdAt": datetime.utcnow()
        }
        new_user_ref.set(user_data)
        return {"success": True, "user_id": new_user_ref.id, "name": nickname}
    except Exception as e:
        return {"success": False, "error": str(e)}

def login_user(email: str, password: str) -> dict:
    try:
        users_ref = db.collection("users")
        query = users_ref.where("email", "==", email).get()
        
        if len(query) == 0:
            return {"success": False, "error": "Email không tồn tại!"}
        
        user_doc = query[0]
        user_data = user_doc.to_dict()
        if user_data["password"] == hash_password(password):
            return {"success": True, "user_id": user_doc.id, "name": user_data.get("name", "User")}
        else:
            return {"success": False, "error": "Sai mật khẩu!"}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ==========================================
# 📝 3. LƯU TRỮ VÀ KÉO LỊCH SỬ (ĐÃ FIX LỖI INDEX)
# ==========================================
def create_session(user_id: str, topic: str) -> dict:
    try:
        session_ref = db.collection("sessions").document()
        session_data = {
            "userId": user_id,
            "topic": topic,
            "examDate": datetime.utcnow(),
            "status": "in_progress",
            "createdAt": datetime.utcnow()
        }
        session_ref.set(session_data)
        return {"success": True, "sessionId": session_ref.id}
    except Exception as e:
        print(f"Lỗi tạo session: {e}")
        return {"success": False, "error": str(e)}

def save_feedback(session_id: str, user_id: str, question: str, message: str, correction: str, grammar_mistake: str, vocabulary: list, score: float) -> dict:
    try:
        feedback_ref = db.collection("feedbacks").document()
        feedback_data = {
            "sessionId": session_id,
            "userId": user_id,
            "role": "user",
            "question": question,
            "message": message,
            "correction": correction,
            "grammarMistake": grammar_mistake,
            "vocabulary": vocabulary, 
            "score": score,
            "timestamp": datetime.utcnow()
        }
        feedback_ref.set(feedback_data)
        return {"success": True}
    except Exception as e:
        print(f"Lỗi lưu feedback: {e}")
        return {"success": False, "error": str(e)}

def get_user_history(user_id: str) -> dict:
    try:
        sessions_ref = db.collection("sessions")
        # 🔥 FIX 1: Chỉ lấy dữ liệu về, KHÔNG DÙNG order_by để Firebase khỏi chặn
        query = sessions_ref.where("userId", "==", user_id)
        
        sessions_docs = query.stream()
        history_data = []

        # Chuyển dữ liệu thành list
        sessions_list = []
        for doc in sessions_docs:
            s_info = doc.to_dict()
            s_info["id"] = doc.id
            sessions_list.append(s_info)

        # 🔥 FIX 2: Sắp xếp các buổi học bằng Python (Bài học mới nhất xếp trước)
        sessions_list.sort(key=lambda x: x.get("createdAt").timestamp() if hasattr(x.get("createdAt"), "timestamp") else 0, reverse=True)

        for session_info in sessions_list:
            session_id = session_info["id"]

            feedbacks_ref = db.collection("feedbacks")
            fb_query = feedbacks_ref.where("sessionId", "==", session_id)
            feedbacks_docs = fb_query.stream()
            
            chat_history = [fb.to_dict() for fb in feedbacks_docs]

            # 🔥 FIX 3: Sắp xếp các câu nói trong buổi học bằng Python (Cũ nhất lên trước để đọc từ trên xuống)
            chat_history.sort(key=lambda x: x.get("timestamp").timestamp() if hasattr(x.get("timestamp"), "timestamp") else 0)

            history_data.append({
                "session": session_info,
                "chatHistory": chat_history
            })

        return {"success": True, "data": history_data}
    except Exception as e:
        print(f"Lỗi lấy lịch sử: {e}")
        return {"success": False, "error": str(e)}