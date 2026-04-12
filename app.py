import streamlit as st
from ai_logic import MimiBrain

# --- 1. CONFIG & ANIMAL DATA ---
st.set_page_config(page_title="Mimi Companion", page_icon="🐾", layout="centered")

ANIMAL_DATA = {
    "Dog": "🐶", "Cat": "🐱", "Hamster": "🐹", "Hippo": "🦛", 
    "Frog": "🐸", "Rabbit": "🐰", "Koala": "🐨", "Fox": "🦊", 
    "Whale": "🐳", "Otter": "🦦", "Squirrel": "🐿️", "Hedgehog": "🦔"
}

# --- 🔥 ĐỌC FILE CSS TỪ BÊN NGOÀI 🔥 ---
try:
    with open("style.css", "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    st.warning("⚠️ Không tìm thấy file style.css! Giao diện có thể hiển thị chưa đúng.")

# --- 2. SESSION STATE MANAGEMENT ---
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

# --- BIẾN CHO MÁY TRẠNG THÁI GHI ÂM ---
if "audio_state" not in st.session_state:
    st.session_state.audio_state = "idle" # Các trạng thái: idle, recording, paused, stopped
if "recorded_text" not in st.session_state:
    st.session_state.recorded_text = ""

def switch_page(page_name):
    st.session_state.page = page_name
    st.rerun()

# ==========================================
# 🛑 PAGE 1: WELCOME SCREEN
# ==========================================
if st.session_state.page == "welcome":
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.image("https://cdn-icons-png.flaticon.com/512/3750/3750731.png", width=150)
    st.title("Hello, this is MIMI")
    st.markdown("<h3 style='color: gray; font-size: 20px;'>Your friendly speaking partner</h3>", unsafe_allow_html=True)
    if st.button("🚀 Let's Start"):
        switch_page("auth")

# ==========================================
# 🛑 PAGE 2: AUTHENTICATION
# ==========================================
elif st.session_state.page == "auth":
    st.title("🔐 Mimi's Security Station")
    tab_login, tab_signup = st.tabs(["Login", "Sign Up"])
    
    with tab_login:
        st.subheader("Welcome back!")
        email = st.text_input("📧 Email")
        pwd = st.text_input("🔑 Password", type="password")
        api_key = st.text_input("⚡ Gemini API Key:", type="password")
        if st.button("Login Now"):
            if api_key:
                st.session_state.mimi_bot = MimiBrain(api_key=api_key)
                st.session_state.user_info = {"name": "Student"}
                switch_page("animal_selection")
            else: st.error("Please enter your API Key!")

    with tab_signup:
        st.subheader("Join the Mimi Squad!")
        nickname = st.text_input("🏷️ Nickname")
        new_api = st.text_input("⚡ New Gemini API Key:", type="password")
        if st.button("Create Account"):
            if new_api and nickname:
                st.session_state.mimi_bot = MimiBrain(api_key=new_api)
                st.session_state.user_info = {"name": nickname}
                switch_page("animal_selection")
            else: st.error("Information missing!")

# ==========================================
# 🛑 PAGE 3: CHOOSE MIMI ANIMAL TYPE
# ==========================================
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
# 🛑 PAGE 4: PRACTICE
# ==========================================
elif st.session_state.page == "practice":
    mimi_icon = ANIMAL_DATA.get(st.session_state.selected_mimi, "🐹")
    
    col_back, col_space, col_user = st.columns([1, 4, 2])
    with col_back:
        if st.button("🚪 Logout"):
            st.session_state.clear()
            switch_page("welcome")
    with col_user:
        st.markdown(f"**{st.session_state.user_info['name']}** {mimi_icon}")

    st.divider()

    if not st.session_state.current_topic:
        st.title("📚 What would you like to talk about?")
        st.markdown("<br>", unsafe_allow_html=True)
        
        r1_c1, r1_c2 = st.columns(2)
        r2_c1, r2_c2 = st.columns(2)
        
        with r1_c1:
            st.image("https://cdn-icons-png.flaticon.com/512/3349/3349080.png", width=80)
            st.subheader("Family & Friends")
            if st.button("Choose this Topic", key="btn_family"):
                st.session_state.current_topic = "Family and Friends"
                st.rerun()
                
        with r1_c2:
            st.image("https://cdn-icons-png.flaticon.com/512/2809/2809793.png", width=80)
            st.subheader("Personal Hobbies")
            if st.button("Choose this Topic", key="btn_hobby"):
                st.session_state.current_topic = "Hobbies and Free time"
                st.rerun()

        with r2_c1:
            st.image("https://cdn-icons-png.flaticon.com/512/3014/3014491.png", width=80)
            st.subheader("Food & Dining")
            if st.button("Choose this Topic", key="btn_food"):
                st.session_state.current_topic = "Food and Drinks"
                st.rerun()

        with r2_c2:
            st.image("https://cdn-icons-png.flaticon.com/512/2060/2060284.png", width=80)
            st.subheader("Pets & Animals")
            if st.button("Choose this Topic", key="btn_pet"):
                st.session_state.current_topic = "Pets and Animals"
                st.rerun()

    else:
        # --- CHAT INTERFACE ---
        if st.button("🔙 Switch Topic"):
            st.session_state.current_topic = None
            st.session_state.current_question = None
            st.rerun()

        st.title(f"🎙️ Practice: {st.session_state.current_topic}")
        
        if not st.session_state.current_question:
            with st.spinner(f"{st.session_state.selected_mimi} is preparing..."):
                q_data = st.session_state.mimi_bot.generate_question(st.session_state.current_topic)
                st.session_state.current_question = q_data

        if st.session_state.current_question:
            q = st.session_state.current_question
            
            with st.chat_message("assistant", avatar=mimi_icon):
                st.write(f"**{q.mimi_greeting}**")
                st.subheader(f"🗣️ {q.question_en}")
                with st.expander("👀 View Translation"):
                    st.write(f"🇻🇳 {q.full_translation_vi}")

            with st.chat_message("user"):
                st.write("🎙️ **Bảng điều khiển Ghi âm (Dành cho Vy ráp code):**")
                
                # --- DÀN NÚT BẤM STATE MACHINE ---
                col_play, col_pause, col_stop, col_reset = st.columns(4)

                with col_play:
                    if st.button("▶️ Record/Resume", disabled=(st.session_state.audio_state == "recording"), use_container_width=True):
                        st.session_state.audio_state = "recording"
                        st.rerun()

                with col_pause:
                    if st.button("⏸️ Pause", disabled=(st.session_state.audio_state != "recording"), use_container_width=True):
                        st.session_state.audio_state = "paused"
                        st.rerun()

                with col_stop:
                    if st.button("⏹️ Stop & Send", type="primary", disabled=(st.session_state.audio_state in ["idle", "stopped"]), use_container_width=True):
                        st.session_state.audio_state = "stopped"
                        st.rerun()

                with col_reset:
                    if st.button("🔄 Reset", use_container_width=True):
                        st.session_state.audio_state = "idle"
                        st.session_state.recorded_text = ""
                        st.rerun()

                # --- HIỂN THỊ TRẠNG THÁI ---
                st.markdown("<br>", unsafe_allow_html=True)
                
                if st.session_state.audio_state == "recording":
                    st.info("🔴 Đang ghi âm... (Đoạn này Vy sẽ ráp code bật Micro)")
                
                elif st.session_state.audio_state == "paused":
                    st.warning("⏸️ Đã tạm dừng. Bấm 'Record/Resume' để nói tiếp.")
                
                elif st.session_state.audio_state == "stopped":
                    st.success("✅ Đã thu âm xong! Sẵn sàng gửi cho hệ thống AI...")
                    
                    # Khung text để Thu test logic AI trong khi chờ Vy làm Audio
                    st.session_state.recorded_text = st.text_area("Vy sẽ trả text từ Whisper vào đây. Giờ Thu cứ gõ để test:", value=st.session_state.recorded_text)
                    
                    if st.button("Gửi cho Mimi chấm bài", type="primary"):
                        if st.session_state.recorded_text:
                            with st.spinner(f"{st.session_state.selected_mimi} is evaluating..."):
                                try:
                                    eval_data = st.session_state.mimi_bot.evaluate_answer(q.question_en, st.session_state.recorded_text)
                                    
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
                                    
                                    # KHI BẤM NÚT NÀY SẼ RESET LUÔN TRẠNG THÁI AUDIO
                                    if st.button("Continue Conversation ➡️", use_container_width=True):
                                        st.session_state.current_question = eval_data.next_question
                                        st.session_state.audio_state = "idle" 
                                        st.session_state.recorded_text = ""
                                        st.rerun()

                                except Exception as e:
                                    if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                                        st.warning("⏳ Oops, API limit reached! Please wait a minute and try again.")
                                    else:
                                        st.error(f"❌ An error occurred: {e}")
                        else:
                            st.warning("Vui lòng nhập câu trả lời trước khi gửi!")