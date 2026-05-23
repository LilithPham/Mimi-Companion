import streamlit as st
from ai_logic import MimiBrain

# ==========================================
# 🎙️ VY'S AUDIO PROCESSOR
# ==========================================
import base64
import io
import os
from dotenv import load_dotenv
from pydub import AudioSegment
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(dotenv_path=os.path.join(BASE_DIR, ".env"), override=True)

class AudioProcessor:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Không tìm thấy GEMINI_API_KEY trong .env!")
        # gemini-1.5-flash supports inline audio (base64) natively
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=api_key,
            temperature=0,
        )

    def process(self, audio_bytes: bytes, mime: str = "audio/webm") -> dict:
        """Nhận raw bytes từ browser, convert sang WAV, gửi Gemini transcribe."""
        # Convert bất kỳ định dạng nào → WAV PCM (Gemini chấp nhận audio/wav)
        fmt = mime.split("/")[1].split(";")[0]
        buf = io.BytesIO(audio_bytes)
        audio = AudioSegment.from_file(buf, format=fmt)
        wav_buf = io.BytesIO()
        audio.export(wav_buf, format="wav")
        wav_b64 = base64.b64encode(wav_buf.getvalue()).decode("utf-8")

        message = HumanMessage(content=[
            {
                "type": "media",
                "mime_type": "audio/wav",
                "data": wav_b64,
            },
            {
                "type": "text",
                "text": (
                    "Transcribe the spoken English in this audio exactly as heard. "
                    "Return ONLY the transcript text, nothing else."
                ),
            },
        ])
        response = self.llm.invoke([message])
        transcript = response.content.strip()
        return {
            "transcript": transcript,
            "language": "en",
            "duration": round(len(audio) / 1000, 1),
        }

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
# --- VY: audio processor singleton ---
if "audio_processor" not in st.session_state:
    try:
        st.session_state.audio_processor = AudioProcessor()
    except ValueError:
        st.session_state.audio_processor = None

def switch_page(page_name):
    st.session_state.page = page_name
    st.rerun()

# ==========================================
# 🛑 PAGE 1: WELCOME SCREEN (Căn giữa tuyệt đối)
# ==========================================
if st.session_state.page == "welcome":
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # 1. CĂN GIỮA ICON
    col_img1, col_img_center, col_img3 = st.columns([1.5, 1, 1.5])
    with col_img_center:
        st.image("https://cdn-icons-png.flaticon.com/512/616/616490.png", use_container_width=True)
    
    # 2. TIÊU ĐỀ VÀ MÔ TẢ 
    st.markdown("<h1 style='text-align: center; color: #FF7E67; font-size: 3rem; margin-bottom: 0; margin-top: 10px;'>Hello, this is MIMI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.2rem; color: #7A7A7A;'>Your friendly speaking partner</p><br>", unsafe_allow_html=True)
    
    # 3. CĂN GIỮA NÚT BẤM
    col_btn1, col_btn_center, col_btn3 = st.columns([1, 1, 1])
    with col_btn_center:
        if st.button("🚀 Let's Start", key="welcome_start", use_container_width=True):
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
        
        if st.button("Login Now", type="primary"):
            if email and pwd:
                st.session_state.mimi_bot = MimiBrain()
                st.session_state.user_info = {"name": email.split('@')[0]}
                switch_page("animal_selection")
            else: 
                st.error("Please enter your Email and Password!")

    with tab_signup:
        st.subheader("Join the Mimi Squad!")
        nickname = st.text_input("🏷️ Nickname")
        new_email = st.text_input("📧 Email Address")
        new_pwd = st.text_input("🔑 Create Password", type="password")
        
        if st.button("Create Account", type="primary"):
            if nickname and new_email and new_pwd:
                st.session_state.mimi_bot = MimiBrain()
                st.session_state.user_info = {"name": nickname}
                switch_page("animal_selection")
            else: 
                st.error("Information missing!")

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
        st.markdown("<h1 style='text-align: center; color: #2C3E50; margin-bottom: 30px;'>📚 What would you like to talk about?</h1>", unsafe_allow_html=True)
        
        # --- DANH SÁCH 8 CHỦ ĐỀ ---
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

        # --- BỐ CỤC LƯỚI (Chia thành từng hàng, mỗi hàng 4 cột) ---
        for i in range(0, len(topics_data), 4): 
            cols = st.columns(4) 
            
            for j in range(4):
                if i + j < len(topics_data):
                    topic = topics_data[i + j]
                    with cols[j]:
                        # 🔥 Gộp chung Icon và Chữ vào 1 khối có chiều cao cố định (160px)
                        html_content = f"""
                        <div style="height: 160px; display: flex; flex-direction: column; align-items: center; justify-content: flex-start;">
                            <img src="{topic['icon']}" width="80" style="margin-bottom: 15px;">
                            <h4 style="text-align: center; color: #34495E; margin: 0; line-height: 1.3;">
                                {topic['title']}
                            </h4>
                        </div>
                        """
                        st.markdown(html_content, unsafe_allow_html=True)
                        
                        # Nút bấm tự do nằm ở dưới khối 160px
                        if st.button("Select", key=f"btn_{topic['val']}", use_container_width=True):
                            st.session_state.current_topic = topic["val"]
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
                st.write("🎙️ **Bảng điều khiển Ghi âm:**")

                # ── VY: MediaRecorder component ──────────────────────────────
                # Inject JS recorder + hidden base64 output into Streamlit via
                # st.components.v1.html.  The recorder posts its result back by
                # writing to a hidden <textarea> whose value Streamlit reads via
                # a form submit.  This keeps everything inside one rerun cycle.
                import streamlit.components.v1 as components

                recorder_html = """
<style>
  #rec-wrap{font-family:sans-serif;display:flex;flex-direction:column;gap:10px}
  .rec-row{display:flex;gap:8px;flex-wrap:wrap}
  button{padding:8px 16px;border-radius:8px;border:1px solid #ccc;background:#fff;cursor:pointer;font-size:14px}
  button:disabled{opacity:.4;cursor:not-allowed}
  #status{font-size:13px;color:#555;min-height:20px}
  #timer{font-family:monospace;font-size:13px;color:#555}
  audio{width:100%;margin-top:6px;border-radius:8px}
</style>
<div id="rec-wrap">
  <div class="rec-row">
    <button id="btn-rec"     onclick="startRec()">▶️ Record</button>
    <button id="btn-pause"   onclick="togglePause()" disabled>⏸️ Pause</button>
    <button id="btn-stop"    onclick="stopRec()"     disabled>⏹️ Stop & Send</button>
    <button id="btn-reset"   onclick="resetRec()">🔄 Reset</button>
    <span   id="timer">0:00</span>
  </div>
  <div id="status">Nhấn Record để bắt đầu ghi âm.</div>
  <div id="audio-wrap"></div>
  <!-- Hidden form that posts base64 WAV back to Streamlit parent -->
  <form id="audio-form" method="POST">
    <input type="hidden" id="audio-b64" name="audio_b64" value="">
    <input type="hidden" id="audio-mime" name="audio_mime" value="">
  </form>
</div>
<script>
let mediaRec, chunks=[], stream, timerInt, elapsed=0, paused=false;

function tick(){
  elapsed++;
  let m=Math.floor(elapsed/60), s=elapsed%60;
  document.getElementById('timer').textContent=m+':'+(s<10?'0':'')+s;
}

async function startRec(){
  if(paused && mediaRec){
    mediaRec.resume(); clearInterval(timerInt); timerInt=setInterval(tick,1000);
    document.getElementById('btn-pause').textContent='⏸️ Pause'; paused=false;
    document.getElementById('status').textContent='🔴 Đang ghi âm...'; return;
  }
  try{ stream=await navigator.mediaDevices.getUserMedia({audio:true}); }
  catch(e){ document.getElementById('status').textContent='⚠️ Không thể truy cập micro: '+e.message; return; }
  chunks=[]; elapsed=0; paused=false;
  mediaRec=new MediaRecorder(stream);
  mediaRec.ondataavailable=e=>{ if(e.data.size>0) chunks.push(e.data); };
  mediaRec.onstop=finishRec;
  mediaRec.start(250);
  timerInt=setInterval(tick,1000);
  document.getElementById('btn-rec').disabled=true;
  document.getElementById('btn-pause').disabled=false;
  document.getElementById('btn-stop').disabled=false;
  document.getElementById('status').textContent='🔴 Đang ghi âm...';
}

function togglePause(){
  if(!mediaRec) return;
  if(mediaRec.state==='recording'){
    mediaRec.pause(); clearInterval(timerInt); paused=true;
    document.getElementById('btn-pause').textContent='▶️ Resume';
    document.getElementById('status').textContent='⏸️ Đã tạm dừng. Nhấn Resume để nói tiếp.';
  } else {
    mediaRec.resume(); timerInt=setInterval(tick,1000); paused=false;
    document.getElementById('btn-pause').textContent='⏸️ Pause';
    document.getElementById('status').textContent='🔴 Đang ghi âm...';
  }
}

function stopRec(){
  if(!mediaRec) return;
  mediaRec.stop(); stream.getTracks().forEach(t=>t.stop()); clearInterval(timerInt);
  document.getElementById('btn-rec').disabled=false;
  document.getElementById('btn-pause').disabled=true;
  document.getElementById('btn-stop').disabled=true;
  document.getElementById('status').textContent='⏳ Đang xử lý...';
}

function resetRec(){
  if(mediaRec && mediaRec.state!=='inactive'){ mediaRec.stop(); }
  if(stream) stream.getTracks().forEach(t=>t.stop());
  clearInterval(timerInt); chunks=[]; elapsed=0; paused=false;
  document.getElementById('btn-rec').disabled=false;
  document.getElementById('btn-pause').disabled=true;
  document.getElementById('btn-stop').disabled=true;
  document.getElementById('btn-pause').textContent='⏸️ Pause';
  document.getElementById('timer').textContent='0:00';
  document.getElementById('status').textContent='Nhấn Record để bắt đầu ghi âm.';
  document.getElementById('audio-wrap').innerHTML='';
  window.parent.postMessage({type:'streamlit:setComponentValue', value:null}, '*');
}

function finishRec(){
  const mime = chunks[0]?.type || 'audio/webm';
  const blob = new Blob(chunks, {type: mime});
  const url  = URL.createObjectURL(blob);

  // Playback preview
  const a=document.createElement('audio'); a.src=url; a.controls=true;
  document.getElementById('audio-wrap').innerHTML=''; 
  document.getElementById('audio-wrap').appendChild(a);
  document.getElementById('status').textContent='✅ Xong! Đang gửi lên Gemini...';

  // Convert to base64 and send to Streamlit
  const reader=new FileReader();
  reader.onload=()=>{
    const b64=reader.result.split(',')[1];
    window.parent.postMessage({
      type:'streamlit:setComponentValue',
      value: JSON.stringify({audio_b64: b64, mime: mime})
    }, '*');
  };
  reader.readAsDataURL(blob);
}
</script>
"""
                audio_result = components.html(recorder_html, height=160, scrolling=False)

                # ── VY: Process audio when component returns data ────────────
                if audio_result:
                    import json as _json
                    try:
                        payload = _json.loads(audio_result)
                        audio_bytes = base64.b64decode(payload["audio_b64"])
                        mime        = payload.get("mime", "audio/webm")
                        processor   = st.session_state.audio_processor
                        if processor is None:
                            st.error("❌ GEMINI_API_KEY chưa được cấu hình trong .env!")
                        else:
                            with st.spinner("🎧 Gemini đang phiên âm..."):
                                stt_result = processor.process(audio_bytes, mime)
                            st.session_state.recorded_text = stt_result["transcript"]
                            st.session_state.audio_state   = "stopped"
                            st.rerun()
                    except Exception as e:
                        st.error(f"❌ Lỗi xử lý audio: {e}")

                st.markdown("<br>", unsafe_allow_html=True)

                if st.session_state.audio_state == "recording":
                    st.info("🔴 Đang ghi âm...")

                elif st.session_state.audio_state == "paused":
                    st.warning("⏸️ Đã tạm dừng. Nhấn Resume để nói tiếp.")

                elif st.session_state.audio_state == "stopped":
                    st.success("✅ Đã thu âm xong! Sẵn sàng gửi cho hệ thống AI...")

                    st.session_state.recorded_text = st.text_area(
                        "📝 Transcript từ Whisper (có thể sửa trước khi gửi):",
                        value=st.session_state.recorded_text
                    )
                    
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