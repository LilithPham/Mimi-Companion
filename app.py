import streamlit as st
import streamlit.components.v1 as components 
from ai_logic import MimiBrain
from database_service import create_session, save_feedback, get_user_history, login_user, register_user
from streamlit_cookies_controller import CookieController 
import base64
import io
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

# ==========================================
# 🎙️ VY'S AUDIO PROCESSOR (OPTIMIZED)
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(dotenv_path=os.path.join(BASE_DIR, ".env"), override=True)

class AudioProcessor:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Không tìm thấy GEMINI_API_KEY trong .env!")
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-flash-latest",
            google_api_key=api_key,
            temperature=0,
        )

    def process(self, audio_bytes: bytes, mime: str = "audio/wav") -> dict:
        wav_b64 = base64.b64encode(audio_bytes).decode("utf-8")
        message = HumanMessage(content=[
            {"type": "media", "mime_type": mime, "data": wav_b64},
            {"type": "text", "text": "Transcribe the spoken English in this audio exactly as heard. Return ONLY the transcript text, nothing else."},
        ])
        
        response = self.llm.invoke([message])
        
        if isinstance(response.content, list):
            transcript_parts = []
            for item in response.content:
                if isinstance(item, dict) and "text" in item:
                    transcript_parts.append(item["text"])
                else:
                    transcript_parts.append(str(item))
            transcript = " ".join(transcript_parts).strip()
        else:
            transcript = str(response.content).strip()
            
        return {"transcript": transcript, "language": "en"}

# --- 1. CONFIG & ANIMAL DATA ---
st.set_page_config(page_title="Mimi Companion", page_icon="🐾", layout="wide")

ANIMAL_DATA = {
    "Dog": "🐶", "Cat": "🐱", "Hamster": "🐹", "Hippo": "🦛", 
    "Frog": "🐸", "Rabbit": "🐰", "Koala": "🐨", "Fox": "🦊", 
    "Whale": "🐳", "Otter": "🦦", "Squirrel": "🐿️", "Hedgehog": "🦔"
}

try:
    with open("style.css", "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass

# --- 🍪 KHỞI TẠO BỘ ĐIỀU KHIỂN COOKIE 🍪 ---
cookies = CookieController()

# --- 2. HÀM ĐIỀU HƯỚNG VÀ NẠP DỮ LIỆU ---
def switch_page(page_name):
    st.session_state.page = page_name
    st.rerun()

def load_history_from_db():
    """Hàm kéo dữ liệu từ Firebase của Quyên về đắp lên giao diện (Review & Notebook)"""
    if st.session_state.user_info:
        res = get_user_history(st.session_state.user_info["id"])
        if res.get("success"):
            history_list = []
            for session_obj in res["data"]:
                topic = session_obj["session"].get("topic", "Chủ đề cũ")
                for fb in session_obj["chatHistory"]:
                    history_list.append({
                        "question": "[Câu hỏi cũ từ Database]",
                        "translation": "",
                        "user_transcript": fb.get("message", ""),
                        "feedback": f"Lịch sử luyện tập chủ đề: {topic}",
                        "logic_check": "",
                        "native_suggestion": fb.get("correction", ""),
                        "grammar_errors": [{"original": "Lỗi", "correction": fb.get("grammarMistake", ""), "explanation": "Ghi chú từ DB"}] if fb.get("grammarMistake") else [],
                        "vocabulary": [],
                        "topic": topic
                    })
            st.session_state.review_history = history_list

# --- 3. SESSION STATE MANAGEMENT ---
if "page" not in st.session_state:
    st.session_state.page = "welcome"
if "user_info" not in st.session_state:
    st.session_state.user_info = None
if "selected_mimi" not in st.session_state:
    st.session_state.selected_mimi = None
if "current_topic" not in st.session_state:
    st.session_state.current_topic = None
if "mimi_bot" not in st.session_state:
    st.session_state.mimi_bot = None
if "current_question" not in st.session_state:
    st.session_state.current_question = None
if "current_firebase_session_id" not in st.session_state:
    st.session_state.current_firebase_session_id = None

if "audio_state" not in st.session_state:
    st.session_state.audio_state = "idle" 
if "recorded_text" not in st.session_state:
    st.session_state.recorded_text = ""
if "turn_count" not in st.session_state:
    st.session_state.turn_count = 0  
if "messages" not in st.session_state:
    st.session_state.messages = []   
if "show_feedback" not in st.session_state:
    st.session_state.show_feedback = False
if "eval_data" not in st.session_state:
    st.session_state.eval_data = None
if "final_transcript" not in st.session_state:
    st.session_state.final_transcript = ""
if "review_history" not in st.session_state:
    st.session_state.review_history = [] 

if "audio_processor" not in st.session_state:
    try:
        st.session_state.audio_processor = AudioProcessor()
    except ValueError:
        st.session_state.audio_processor = None

# --- 🔄 KIỂM TRA TỰ ĐỘNG ĐĂNG NHẬP QUA COOKIE 🔄 ---
saved_user_id = cookies.get("mimi_user_id")
saved_user_name = cookies.get("mimi_user_name")
if saved_user_id and saved_user_name and st.session_state.user_info is None:
    st.session_state.user_info = {"id": saved_user_id, "name": saved_user_name}
    st.session_state.mimi_bot = MimiBrain()
    load_history_from_db() # Nạp lịch sử cũ ngay khi vào app
    switch_page("animal_selection") 

# ==========================================
# 🛑 PAGES 1 & 2 & 3: WELCOME, AUTH, SELECTION
# ==========================================
if st.session_state.page == "welcome":
    st.markdown("<br><br>", unsafe_allow_html=True)
    col_img1, col_img_center, col_img3 = st.columns([1.5, 1, 1.5])
    with col_img_center:
        st.image("https://cdn-icons-png.flaticon.com/512/616/616490.png", use_container_width=True)
    st.markdown("<h1 style='text-align: center; color: #FF7E67; font-size: 3rem; margin-bottom: 0; margin-top: 10px;'>Hello, this is MIMI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.2rem; color: #7A7A7A;'>Your friendly speaking partner</p><br>", unsafe_allow_html=True)
    col_btn1, col_btn_center, col_btn3 = st.columns([1, 1, 1])
    with col_btn_center:
        if st.button("🚀 Let's Start", key="welcome_start", use_container_width=True):
            switch_page("auth")

elif st.session_state.page == "auth":
    st.title("🔐 Mimi's Security Station")
    tab_login, tab_signup = st.tabs(["Login", "Sign Up"])
    
    with tab_login:
        email = st.text_input("📧 Email")
        pwd = st.text_input("🔑 Password", type="password")
        if st.button("Login Now", type="primary"):
            if email and pwd:
                with st.spinner("Đang kiểm tra thông tin..."):
                    result = login_user(email, pwd)
                    if result["success"]:
                        cookies.set("mimi_user_id", result["user_id"], max_age=7*24*3600)
                        cookies.set("mimi_user_name", result["name"], max_age=7*24*3600)
                        
                        st.session_state.user_info = {"id": result["user_id"], "name": result["name"]}
                        load_history_from_db() # Nạp lịch sử cũ
                        
                        st.success(f"Chào mừng {result['name']} trở lại! Đang chuyển hướng...")
                        components.html("<script>setTimeout(function() { window.parent.location.reload(); }, 1000);</script>", height=0)
                    else:
                        st.error(f"❌ {result['error']}")
            else: 
                st.error("Vui lòng nhập Email và Password!")
                
    with tab_signup:
        nickname = st.text_input("🏷️ Nickname (Tên hiển thị)")
        new_email = st.text_input("📧 Email Address")
        new_pwd = st.text_input("🔑 Create Password", type="password")
        if st.button("Create Account", type="primary"):
            if nickname and new_email and new_pwd:
                with st.spinner("Đang tạo tài khoản trên hệ thống..."):
                    result = register_user(new_email, new_pwd, nickname)
                    if result["success"]:
                        cookies.set("mimi_user_id", result["user_id"], max_age=7*24*3600)
                        cookies.set("mimi_user_name", result["name"], max_age=7*24*3600)
                        
                        st.session_state.user_info = {"id": result["user_id"], "name": result["name"]}
                        st.session_state.review_history = [] # Tài khoản mới nên sổ tay trống
                        
                        st.success("Đăng ký thành công! Đang chuyển hướng...")
                        components.html("<script>setTimeout(function() { window.parent.location.reload(); }, 1000);</script>", height=0)
                    else:
                        st.error(f"❌ {result['error']}")
            else: 
                st.error("Vui lòng điền đầy đủ thông tin!")

elif st.session_state.page == "animal_selection":
    st.title("🐾 Choose Mimi animal type")
    st.markdown("### Select your companion for today's session!")
    cols = st.columns(3)
    animals_list = list(ANIMAL_DATA.keys())
    for i, name in enumerate(animals_list):
        with cols[i % 3]:
            icon = ANIMAL_DATA[name]
            st.markdown(f"<h1 style='font-size: 60px; margin-bottom: 0;'>{icon}</h1>", unsafe_allow_html=True)
            if st.button(f"Select {name}", key=f"select_{name}"):
                st.session_state.selected_mimi = name
                switch_page("practice")

# ==========================================
# 🛑 PAGE 4: PRACTICE & REVIEW (WITH SIDEBAR)
# ==========================================
elif st.session_state.page == "practice":
    mimi_icon = ANIMAL_DATA.get(st.session_state.selected_mimi, "🐹")
    
    with st.sidebar:
        st.markdown(f"## {mimi_icon} Mimi Menu")
        st.write(f"Hello, **{st.session_state.user_info['name']}**!")
        nav_choice = st.radio("Chế độ:", ["🗣️ Chat with Mimi", "📚 Review your chat", "📓 Mimi's Notebook"]) 
        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            cookies.remove("mimi_user_id")
            cookies.remove("mimi_user_name")
            st.session_state.clear()
            st.success("Đã đăng xuất thành công! Hẹn gặp lại nhé...")
            components.html("<script>setTimeout(function() { window.parent.location.reload(); }, 1000);</script>", height=0)

    # ==========================================
    # 📚 TAB 2: REVIEW YOUR CHAT
    # ==========================================
    if nav_choice == "📚 Review your chat":
        st.title("📚 Lịch sử học tập của bạn")
        
        if not st.session_state.review_history:
            st.info("Trang giấy trắng! Hãy trò chuyện với Mimi bên tab 'Chat' để ghi lại lịch sử học tập nhé.")
        else:
            st.success(f"Bạn đã hoàn thành {len(st.session_state.review_history)} lượt tương tác!")
            
            for idx, item in enumerate(st.session_state.review_history):
                with st.expander(f"🔄 Lượt {idx + 1}: {item['question']}"):
                    st.write(f"**🤖 Mimi hỏi:** {item['question']}")
                    st.write(f"_{item['translation']}_")
                    st.write(f"**👤 Bạn trả lời:** {item['user_transcript']}") 
                    st.divider()
                    
                    st.write(f"**Lời khuyên:** {item['feedback']}")
                    if item['logic_check']:
                        st.warning(f"**Lưu ý Logic:** {item['logic_check']}")
                    
                    st.info(f"**Cách nói tự nhiên hơn:** {item['native_suggestion']}")
                    
                    if item['grammar_errors']:
                        st.write("### 🔍 Lỗi Ngữ Pháp")
                        for err in item['grammar_errors']:
                            # Handle cả 2 trường hợp: object dict (từ code cũ) và object pydantic (từ code AI)
                            original = err.original if hasattr(err, 'original') else err.get("original", "")
                            correction = err.correction if hasattr(err, 'correction') else err.get("correction", "")
                            explanation = err.explanation if hasattr(err, 'explanation') else err.get("explanation", "")
                            st.write(f"- ❌ {original} ➔ ✅ **{correction}**")
                            st.caption(f"Giải thích: {explanation}")
                            
                    if item['vocabulary']:
                        st.write("### ✨ Nâng cấp Từ Vựng")
                        for voc in item['vocabulary']:
                            st.write(f"- Thử dùng: **{voc.correction}** thay vì '{voc.original}'")
                            st.caption(f"Lý do: {voc.explanation}")

    # ==========================================
    # 📓 TAB 3: MIMI'S NOTEBOOK
    # ==========================================
    elif nav_choice == "📓 Mimi's Notebook":
        st.title("📓 Mimi's Notebook")
        st.markdown("### 🌟 Những từ vựng và cấu trúc bạn cần ghi nhớ")

        saved_vocab = []
        for item in st.session_state.review_history:
            if item.get('vocabulary'):
                for voc in item['vocabulary']:
                    saved_vocab.append({
                        "topic": item.get('topic', st.session_state.current_topic),
                        "original": voc.original,
                        "correction": voc.correction,
                        "explanation": voc.explanation
                    })

        if not saved_vocab:
            st.info("Sổ tay đang trống! Hãy trò chuyện với Mimi bên mục Chat để tích lũy từ vựng hay nhé.")
        else:
            st.success(f"🔥 Xuất sắc! Bạn đã tích lũy được {len(saved_vocab)} từ vựng/cấu trúc mới hôm nay!")
            
            for idx, voc in enumerate(saved_vocab):
                st.markdown(f"""
                <div style="background-color: #FFF5F5; padding: 15px; border-radius: 10px; border-left: 5px solid #FF7E67; margin-bottom: 15px;">
                    <span style="background-color: #FF7E67; color: white; padding: 2px 8px; border-radius: 5px; font-size: 0.8rem;">✨ {voc['topic']}</span>
                    <h4 style="margin-top: 10px; margin-bottom: 5px; color: #2C3E50;">
                        Thay vì dùng: <del style="color: #c0392b;">"{voc['original']}"</del> ➔ Hãy nói: <b style="color: #27ae60;">"{voc['correction']}"</b>
                    </h4>
                    <p style="margin: 0; color: #7F8C8D; font-size: 0.95rem;">💡 <i>{voc['explanation']}</i></p>
                </div>
                """, unsafe_allow_html=True)

    # ==========================================
    # 🗣️ TAB 1: CHAT WITH MIMI
    # ==========================================
    elif nav_choice == "🗣️ Chat with Mimi":
        if not st.session_state.current_topic:
            st.markdown("<h1 style='text-align: center; color: #2C3E50; margin-bottom: 30px;'>📚 What would you like to talk about?</h1>", unsafe_allow_html=True)
            topics_data = [
                {"title": "Family & Friends", "icon": "https://cdn-icons-png.flaticon.com/128/12649/12649716.png", "val": "Family and Friends"},
                {"title": "Personal Hobbies", "icon": "https://cdn-icons-png.flaticon.com/128/3588/3588658.png", "val": "Hobbies and Free time"},
                {"title": "Food & Dining", "icon": "https://cdn-icons-png.flaticon.com/128/2276/2276931.png", "val": "Food and Drinks"},
                {"title": "Pets & Animals", "icon": "https://cdn-icons-png.flaticon.com/128/8182/8182996.png", "val": "Pets and Animals"},
                {"title": "Travel & Holidays", "icon": "https://cdn-icons-png.flaticon.com/128/5333/5333722.png", "val": "Travel and Holidays"}, 
                {"title": "School & Study", "icon": "https://cdn-icons-png.flaticon.com/128/13540/13540886.png", "val": "School and Study"},
                {"title": "Work & Jobs", "icon": "https://cdn-icons-png.flaticon.com/128/3850/3850285.png", "val": "Work and Jobs"},
                {"title": "Sports & Health", "icon": "https://cdn-icons-png.flaticon.com/128/4163/4163684.png", "val": "Sports and Health"}
            ]
            for i in range(0, len(topics_data), 4): 
                cols = st.columns(4) 
                for j in range(4):
                    if i + j < len(topics_data):
                        topic = topics_data[i + j]
                        with cols[j]:
                            html_content = f"""
                            <div style="height: 160px; display: flex; flex-direction: column; align-items: center; justify-content: flex-start;">
                                <img src="{topic['icon']}" width="80" style="margin-bottom: 15px;">
                                <h4 style="text-align: center; color: #34495E; margin: 0; line-height: 1.3;">{topic['title']}</h4>
                            </div>
                            """
                            st.markdown(html_content, unsafe_allow_html=True)
                            
                            if st.button("Select", key=f"btn_{topic['val']}", use_container_width=True):
                                st.session_state.current_topic = topic["val"]
                                st.session_state.messages = []
                                
                                # 🔥 TẠO SESSION TRÊN FIREBASE KHI CHỌN CHỦ ĐỀ
                                res = create_session(st.session_state.user_info["id"], topic["val"])
                                if res.get("success"):
                                    st.session_state.current_firebase_session_id = res["sessionId"]
                                
                                st.session_state.turn_count = 0
                                st.session_state.show_feedback = False
                                st.rerun()
        else:
            col1, col2 = st.columns([1, 5])
            with col1:
                if st.button("🔙 Switch Topic"):
                    st.session_state.current_topic = None
                    st.session_state.current_question = None
                    st.session_state.messages = []
                    st.session_state.turn_count = 0
                    st.session_state.audio_state = "idle"
                    st.session_state.recorded_text = ""
                    st.session_state.show_feedback = False
                    st.session_state.current_firebase_session_id = None
                    st.rerun()
            with col2:
                st.title(f"🎙️ Practice: {st.session_state.current_topic}")
            
            if not st.session_state.current_question:
                with st.spinner(f"{st.session_state.selected_mimi} is preparing..."):
                    try:
                        q_data = st.session_state.mimi_bot.generate_question(st.session_state.current_topic)
                        st.session_state.current_question = q_data
                    except Exception as e:
                        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                            st.error("⏳ Hệ thống đang quá tải (Limit API). Hãy chờ 1 phút rồi chọn lại chủ đề nhé!")
                        else:
                            st.error(f"❌ Lỗi: {e}")

            if st.session_state.current_question:
                q = st.session_state.current_question
                
                for msg in st.session_state.messages:
                    avatar_icon = mimi_icon if msg["role"] == "assistant" else "👤"
                    with st.chat_message(msg["role"], avatar=avatar_icon):
                        st.write(msg["content"])

                with st.chat_message("assistant", avatar=mimi_icon):
                    st.write(f"**{q.mimi_greeting}**")
                    st.subheader(f"🗣️ {q.question_en}")
                    with st.expander("👀 View Translation"):
                        st.write(f"🇻🇳 {q.full_translation_vi}")

                with st.chat_message("user", avatar="👤"):
                    audio_value = st.audio_input("🎙️ Nhấn vào micro để ghi âm:", key=f"mimi_mic_{st.session_state.turn_count}")

                    if audio_value is None and st.session_state.audio_state == "stopped":
                        st.session_state.audio_state = "idle"
                        st.session_state.recorded_text = ""
                        st.session_state.show_feedback = False 
                        st.rerun()

                    if audio_value is not None and st.session_state.audio_state != "stopped":
                        try:
                            audio_bytes = audio_value.read()
                            processor = st.session_state.audio_processor
                            if processor is None:
                                st.error("❌ GEMINI_API_KEY chưa được cấu hình!")
                            else:
                                with st.spinner("🎧 Mimi đang phiên âm..."):
                                    stt_result = processor.process(audio_bytes, mime="audio/wav")
                                
                                st.session_state.recorded_text = stt_result["transcript"]
                                st.session_state.audio_state = "stopped"
                                st.session_state.show_feedback = False 
                                st.rerun()
                        except Exception as e:
                            st.error(f"❌ Lỗi xử lý audio: {e}")

                    st.markdown("<br>", unsafe_allow_html=True)

                    if st.session_state.audio_state == "stopped":
                        st.success("✅ Bạn có thể chỉnh sửa lại chữ ở bên dưới nếu AI nghe nhầm.")

                        final_transcript = st.text_area(
                            "📝 Transcript từ Whisper:",
                            value=st.session_state.recorded_text,
                            key=f"editor_{st.session_state.turn_count}"
                        )
                        
                        if st.button("Gửi cho Mimi chấm bài", type="primary"):
                            if final_transcript:
                                with st.spinner(f"{st.session_state.selected_mimi} is evaluating..."):
                                    try:
                                        eval_data = st.session_state.mimi_bot.evaluate_answer(q.question_en, final_transcript)
                                        
                                        st.session_state.eval_data = eval_data
                                        st.session_state.final_transcript = final_transcript
                                        st.session_state.show_feedback = True
                                        st.rerun()
                                    except Exception as e:
                                        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                                            st.warning("⏳ Hệ thống đang quá tải. Hãy đợi 1 phút và bấm gửi lại nhé!")
                                        else:
                                            st.error(f"❌ An error occurred: {e}")
                            else:
                                st.warning("Vui lòng nhập câu trả lời trước khi gửi!")

                if st.session_state.get("show_feedback", False):
                    eval_data = st.session_state.eval_data
                    saved_transcript = st.session_state.final_transcript
                    
                    st.success(f"🎉 **{eval_data.overall_encouragement}**")
                    if eval_data.logic_check:
                        st.warning(f"🧠 {eval_data.logic_check}")
                    st.info(f"🌟 **{st.session_state.selected_mimi} suggests:**\n> {eval_data.native_suggestion}")

                    st.divider()
                    st.write("### 🔍 Correction Corner")
                    if eval_data.grammar_errors:
                        for err in eval_data.grammar_errors:
                            st.error(f"❌ '{err.original}' ➔ ✅ **'{err.correction}'** \n👉 *{err.explanation}*")
                    if eval_data.vocabulary_improvements:
                        for vocab in eval_data.vocabulary_improvements:
                            st.info(f"✨ '{vocab.original}' ➔ **'{vocab.correction}'** \n👉 *{vocab.explanation}*")
                    
                    st.divider()
                    st.success(f"{st.session_state.selected_mimi} has the next question ready!")
                    
                    if st.button("Continue Conversation ➡️", use_container_width=True):
                        # 🔥 LƯU DỮ LIỆU LÊN FIREBASE
                        if st.session_state.current_firebase_session_id:
                            grammar_str = " | ".join([f"{e.original}->{e.correction}" for e in eval_data.grammar_errors]) if eval_data.grammar_errors else ""
                            save_feedback(
                                session_id=st.session_state.current_firebase_session_id,
                                user_id=st.session_state.user_info["id"],
                                message=saved_transcript,
                                correction=eval_data.native_suggestion,
                                grammar_mistake=grammar_str,
                                score=10.0 # Tạm gắn điểm 10, version sau AI sẽ tự chấm
                            )

                        history_item = {
                            "question": q.question_en,
                            "translation": q.full_translation_vi,
                            "user_transcript": saved_transcript,
                            "feedback": eval_data.overall_encouragement,
                            "logic_check": eval_data.logic_check,
                            "native_suggestion": eval_data.native_suggestion,
                            "grammar_errors": eval_data.grammar_errors,
                            "vocabulary": eval_data.vocabulary_improvements,
                            "topic": st.session_state.current_topic
                        }
                        st.session_state.review_history.append(history_item)

                        st.session_state.messages.append({"role": "user", "content": f"🎙️ *{saved_transcript}*"})
                        
                        st.session_state.current_question = eval_data.next_question
                        st.session_state.audio_state = "idle" 
                        st.session_state.recorded_text = ""
                        st.session_state.turn_count += 1
                        st.session_state.show_feedback = False
                        st.session_state.eval_data = None
                        st.session_state.final_transcript = ""
                        
                        st.rerun()