import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import os
import hashlib # 👈 THƯ VIỆN BẢO MẬT MẬT KHẨU

# ==========================================
# 🔥 1. KHỞI TẠO KẾT NỐI FIREBASE (SỬ DỤNG SERVICE ACCOUNT)
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KEY_PATH = os.path.join(BASE_DIR, "firebase_key.json")

if not firebase_admin._apps:
    if os.path.exists(KEY_PATH):
        # Sử dụng file JSON cấu hình để xác thực quyền Admin ở máy local
        cred = credentials.Certificate(KEY_PATH)
        firebase_admin.initialize_app(cred)
    else:
        # Fallback dành cho lúc deploy lên Streamlit Cloud sau này
        cred = credentials.ApplicationDefault() 
        firebase_admin.initialize_app(cred, {
            'projectId': 'iot-secod-year',
        })

db = firestore.client()

# ==========================================
# 🔐 2. HỆ THỐNG XÁC THỰC (AUTH) BẰNG FIRESTORE
# ==========================================
def hash_password(password: str) -> str:
    """Băm mật khẩu để bảo mật trước khi lưu vào DB"""
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(email: str, password: str, nickname: str) -> dict:
    """Đăng ký tài khoản mới"""
    try:
        users_ref = db.collection("users")
        # 1. Kiểm tra email đã tồn tại chưa
        query = users_ref.where("email", "==", email).get()
        if len(query) > 0:
            return {"success": False, "error": "Email này đã được đăng ký!"}
        
        # 2. Tạo tài khoản mới với mật khẩu đã mã hóa
        hashed_pw = hash_password(password)
        new_user_ref = users_ref.document()
        user_data = {
            "email": email,
            "password": hashed_pw,
            "name": nickname,
            "createdAt": datetime.utcnow()
        }
        new_user_ref.set(user_data)
        
        # Trả về user_id (chính là ID tự tạo của document)
        return {"success": True, "user_id": new_user_ref.id, "name": nickname}
    except Exception as e:
        return {"success": False, "error": str(e)}

def login_user(email: str, password: str) -> dict:
    """Đăng nhập và kiểm tra mật khẩu"""
    try:
        users_ref = db.collection("users")
        query = users_ref.where("email", "==", email).get()
        
        if len(query) == 0:
            return {"success": False, "error": "Email không tồn tại!"}
        
        # Lấy thông tin user
        user_doc = query[0]
        user_data = user_doc.to_dict()
        
        # So sánh mật khẩu mã hóa
        if user_data["password"] == hash_password(password):
            return {"success": True, "user_id": user_doc.id, "name": user_data.get("name", "User")}
        else:
            return {"success": False, "error": "Sai mật khẩu!"}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ==========================================
# 📝 3. CHUYỂN ĐỔI TOÀN BỘ LOGIC CỦA QUYÊN SANG PYTHON
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

def save_feedback(session_id: str, user_id: str, message: str, correction: str, grammar_mistake: str, score: float) -> dict:
    try:
        feedback_ref = db.collection("feedbacks").document()
        feedback_data = {
            "sessionId": session_id,
            "userId": user_id,
            "role": "user",
            "message": message,
            "correction": correction,
            "grammarMistake": grammar_mistake,
            "score": score,
            "timestamp": datetime.utcnow()
        }
        feedback_ref.set(feedback_data)
        return {"success": True}
    except Exception as e:
        print(f"Lỗi lưu feedback: {e}")
        return {"success": False, "error": str(e)}

def complete_session(session_id: str, total_score: float) -> dict:
    try:
        session_ref = db.collection("sessions").document(session_id)
        session_ref.update({
            "status": "completed",
            "totalScore": total_score,
            "completedAt": datetime.utcnow()
        })
        return {"success": True}
    except Exception as e:
        print(f"Lỗi kết thúc session: {e}")
        return {"success": False, "error": str(e)}

def get_user_history(user_id: str) -> dict:
    try:
        sessions_ref = db.collection("sessions")
        query = sessions_ref.where("userId", "==", user_id)\
                            .where("status", "==", "completed")\
                            .order_by("examDate", direction=firestore.Query.DESCENDING)
        
        sessions_docs = query.stream()
        history_data = []

        for doc in sessions_docs:
            session_id = doc.id
            session_info = doc.to_dict()
            session_info["id"] = session_id

            feedbacks_ref = db.collection("feedbacks")
            fb_query = feedbacks_ref.where("sessionId", "==", session_id)\
                                    .order_by("timestamp", direction=firestore.Query.ASCENDING)
            
            feedbacks_docs = fb_query.stream()
            chat_history = [fb.to_dict() for fb in feedbacks_docs]

            history_data.append({
                "session": session_info,
                "chatHistory": chat_history
            })

        return {"success": True, "data": history_data}
    except Exception as e:
        print(f"Lỗi lấy lịch sử: {e}")
        return {"success": False, "error": str(e)}