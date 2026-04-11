import streamlit as st
from ai_logic import MimiBrain
from streamlit_mic_recorder import speech_to_text

# --- 1. CẤU HÌNH GIAO DIỆN & CSS ---
st.set_page_config(page_title="Mimi Companion", page_icon="🐾", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #FFF6F6; }
    h1, h2, h3 { color: #FF7E67; font-family: 'Comic Sans MS', 'Nunito', sans-serif; text-align: center; }
    
    /* Làm đẹp nút bấm tổng thể */
    .stButton > button {
        background-color: #FF7E67 !important; color: white !important;
        border-radius: 20px !important; border: none !important; font-weight: bold !important;
        padding: 15px 30px !important; width: 100%; transition: 0.3s;
    }
    .stButton > button:hover { background-color: #FF5A3D !important; transform: scale(1.02); }
    
    /* CSS cho Thẻ chủ đề (Topic Cards) */
    div[data-testid="column"] {
        background-color: white; border-radius: 15px; padding: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); text-align: center; border: 2px solid #FFEAEA;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. QUẢN LÝ TRẠNG THÁI (ROUTER TÍCH HỢP) ---
if "page" not in st.session_state:
    st.session_state.page = "welcome"
if "user_info" not in st.session_state:
    st.session_state.user_info = None
if "current_topic" not in st.session_state:
    st.session_state.current_topic = None
if "mimi_bot" not in st.session_state:
    st.session_state.mimi_bot = None
if "current_question" not in st.session_state:
    st.session_state.current_question = None

# Hàm chuyển trang nhanh
def switch_page(page_name):
    st.session_state.page = page_name
    st.rerun()

# ==========================================
# 🛑 TRANG 1: MÀN HÌNH WELCOME
# ==========================================
if st.session_state.page == "welcome":
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.image("https://cdn-icons-png.flaticon.com/512/3750/3750731.png", width=150, use_container_width=True)
    st.title("Hello, this is MIMI")
    st.markdown("<h3 style='color: gray; font-size: 20px;'>Your friendly speaking partner</h3>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Let's Start"):
            switch_page("auth")

# ==========================================
# 🛑 TRANG 2: MÀN HÌNH ĐĂNG NHẬP / ĐĂNG KÝ
# ==========================================
elif st.session_state.page == "auth":
    st.title("🔐 Trạm kiểm soát của Mimi")
    
    tab_login, tab_signup = st.tabs(["Đăng Nhập", "Tạo Tài Khoản"])
    
    with tab_login:
        st.subheader("Chào mừng bạn quay lại!")
        email = st.text_input("📧 Email")
        pwd = st.text_input("🔑 Mật khẩu", type="password")
        api_key = st.text_input("⚡ Nhập Gemini API Key (Bắt buộc):", type="password")
        
        if st.button("Đăng Nhập"):
            if api_key:
                st.session_state.mimi_bot = MimiBrain(api_key=api_key)
                st.session_state.user_info = {"name": "Học viên", "avatar": "https://cdn-icons-png.flaticon.com/512/4140/4140048.png"}
                switch_page("practice")
            else:
                st.error("Bạn quên nhập API Key rồi!")

    with tab_signup:
        st.subheader("Gia nhập đội của Mimi!")
        new_email = st.text_input("📧 Email của bạn")
        nickname = st.text_input("🏷️ Nickname (Tên gọi thân mật)")
        new_pwd = st.text_input("🔑 Mật khẩu mới", type="password")
        
        col_g, col_a = st.columns(2)
        with col_g:
            gender = st.radio("🚻 Giới tính:", ["Nam", "Nữ", "Khác"])
        with col_a:
            avatar_choice = st.selectbox("🖼️ Chọn Avatar:", ["Cậu bé vui vẻ", "Cô bé đáng yêu", "Mèo con"])
            
        new_api = st.text_input("⚡ Nhập Gemini API Key mới:", type="password")
        
        if st.button("Đăng Ký & Bắt Đầu"):
            if new_api and nickname:
                st.session_state.mimi_bot = MimiBrain(api_key=new_api)
                avt_url = "https://cdn-icons-png.flaticon.com/512/4140/4140048.png"
                if avatar_choice == "Cô bé đáng yêu": avt_url = "https://cdn-icons-png.flaticon.com/512/4140/4140047.png"
                elif avatar_choice == "Mèo con": avt_url = "https://cdn-icons-png.flaticon.com/512/3750/3750731.png"
                
                st.session_state.user_info = {"name": nickname, "avatar": avt_url}
                switch_page("practice")
            else:
                st.error("Vui lòng nhập Nickname và API Key nhé!")

# ==========================================
# 🛑 TRANG 3: LUYỆN NÓI (CHỌN CHỦ ĐỀ & CHAT)
# ==========================================
elif st.session_state.page == "practice":
    
    # --- THANH ĐIỀU HƯỚNG TRÊN CÙNG ---
    col_back, col_space, col_user = st.columns([1, 4, 2])
    with col_back:
        if st.button("🚪 Đăng xuất"):
            st.session_state.clear()
            switch_page("welcome")
    with col_user:
        st.markdown(f"**Chào, {st.session_state.user_info['name']}!** 🎓")

    st.divider()

    # --- NẾU CHƯA CHỌN CHỦ ĐỀ: HIỂN THỊ CÁC THẺ ---
    if not st.session_state.current_topic:
        st.title("📚 Hôm nay bạn muốn nói về gì?")
        st.markdown("<br>", unsafe_allow_html=True)
        
        r1_c1, r1_c2 = st.columns(2)
        r2_c1, r2_c2 = st.columns(2)
        
        with r1_c1:
            st.image("https://cdn-icons-png.flaticon.com/512/3349/3349080.png", width=80)
            st.subheader("Gia đình & Bạn bè")
            if st.button("Chọn Chủ đề này", key="btn_family"):
                st.session_state.current_topic = "Family and Friends"
                st.rerun()
                
        with r1_c2:
            st.image("https://cdn-icons-png.flaticon.com/512/2809/2809793.png", width=80)
            st.subheader("Sở thích cá nhân")
            if st.button("Chọn Chủ đề này", key="btn_hobby"):
                st.session_state.current_topic = "Hobbies and Free time"
                st.rerun()

        with r2_c1:
            st.image("https://cdn-icons-png.flaticon.com/512/3014/3014491.png", width=80)
            st.subheader("Ẩm thực & Món ăn")
            if st.button("Chọn Chủ đề này", key="btn_food"):
                st.session_state.current_topic = "Food and Drinks"
                st.rerun()

        with r2_c2:
            st.image("https://cdn-icons-png.flaticon.com/512/2060/2060284.png", width=80)
            st.subheader("Thú cưng")
            if st.button("Chọn Chủ đề này", key="btn_pet"):
                st.session_state.current_topic = "Pets and Animals"
                st.rerun()

    # --- NẾU ĐÃ CHỌN CHỦ ĐỀ: VÀO PHÒNG CHAT ---
    else:
        if st.button("🔙 Đổi chủ đề khác"):
            st.session_state.current_topic = None
            st.session_state.current_question = None
            st.rerun()

        st.title(f"🎙️ Phòng tập: {st.session_state.current_topic}")
        
        # Kích hoạt AI tạo câu hỏi đầu tiên
        if not st.session_state.current_question:
            with st.spinner("Mimi đang soạn bài..."):
                try:
                    q_data = st.session_state.mimi_bot.generate_question(st.session_state.current_topic)
                    st.session_state.current_question = q_data
                except Exception as e:
                    if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                        st.warning("⏳ Mimi đang cạn năng lượng (hết lượt API)! Bạn đợi xíu rồi thử lại nha.")
                    else:
                        st.error(f"Lỗi: {e}")

        # --- GIAO DIỆN CHAT ---
        if st.session_state.current_question:
            q = st.session_state.current_question
            
            with st.chat_message("assistant", avatar="https://cdn-icons-png.flaticon.com/512/4082/4082041.png"):
                st.write(f"**{q.mimi_greeting}**")
                st.subheader(f"🗣️ {q.question_en}")
                
                with st.expander("👀 Xem gợi ý dịch"):
                    st.info(f"🇻🇳 {q.full_translation_vi}")
                    st.success(f"💡 Từ khóa: {', '.join(q.hint_keywords)}")

            with st.chat_message("user", avatar=st.session_state.user_info['avatar']):
                st.write("🎙️ **Lượt của bạn:**")
                
                user_text = speech_to_text(
                    language='en-US',
                    start_prompt="🔴 Bấm để nói",
                    stop_prompt="⏹️ Đang thu âm...",
                    key='my_stt_chat'
                )
                
                if user_text:
                    st.write(f"📝 *Bạn nói:* **{user_text}**")
                    
                    with st.spinner("🐹 Mimi đang chấm bài..."):
                        try:
                            eval_data = st.session_state.mimi_bot.evaluate_answer(q.question_en, user_text)
                            
                            st.success(f"🎉 **{eval_data.overall_encouragement}**")
                            if eval_data.logic_check:
                                st.warning(f"🧠 {eval_data.logic_check}")
                            st.info(f"🌟 **Mimi gợi ý:**\n> {eval_data.native_suggestion}")

                            st.divider()
                            st.write("### 🔍 Góc Sửa Lỗi Chi Tiết")
                            if eval_data.grammar_errors:
                                for err in eval_data.grammar_errors:
                                    st.error(f"❌ '{err.original}' ➔ ✅ **'{err.correction}'** \n👉 *{err.explanation}*")
                            if eval_data.vocabulary_improvements:
                                for vocab in eval_data.vocabulary_improvements:
                                    st.info(f"✨ '{vocab.original}' ➔ **'{vocab.correction}'** \n👉 *{vocab.explanation}*")
                            
                            # NÚT CHUYỂN CÂU HỎI TIẾP THEO
                            st.divider()
                            st.success("Mimi đã chuẩn bị sẵn câu hỏi tiếp theo rồi nè!")
                            if st.button("Tiếp tục trò chuyện ➡️", use_container_width=True):
                                st.session_state.current_question = eval_data.next_question
                                st.rerun()

                        except Exception as e:
                            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                                st.warning("⏳ Ối, Mimi đang cạn năng lượng (hết lượt API)! Em đợi khoảng 1 phút rồi nói lại nha!")
                            else:
                                st.error(f"❌ Mimi đang gặp sự cố: {e}")