# 🐾 Mimi Companion: Your Friendly AI Speaking Partner

**Mimi Companion** is an AI-powered educational platform designed specifically for "Level 0" English learners (beginners) in Vietnam. Developed as a student project at **Vietnamese-German University (VGU)**, Mimi aims to provide a safe, encouraging, and interactive environment for independent English speaking practice.

---

## 🌟 Key Features

- **Personalized Onboarding:** Welcome screen with user authentication and customizable avatars.
- **Topic-Based Learning:** Interactive cards for various daily topics (Family, Hobbies, Food, Travel, etc.).
- **Smart Conversations:** Mimi doesn't just ask questions; she listens to your answers and asks follow-up questions to keep the conversation flowing naturally.
- **Real-time AI Feedback:** - **Transcription:** Converts your speech to text instantly.
    - **Logic Check:** Ensures your answer is on-topic.
    - **Grammar & Vocabulary:** Provides detailed corrections and "Level-up" suggestions in Vietnamese.
    - **Native Suggestions:** Re-writes your sentence to sound more natural.
- **Friendly UI/UX:** A cute, pastel-themed chat interface designed to reduce learner anxiety.

---

## 🛠️ Tech Stack

- **Frontend/App Framework:** [Streamlit](https://streamlit.io/)
- **AI Brain:** [Google Gemini API](https://ai.google.dev/) (via `gemini-flash-latest`)
- **Orchestration:** [LangChain](https://www.langchain.com/)
- **Audio Processing:** `streamlit-mic-recorder` (Browser-based STT)
- **Data Modeling:** [Pydantic](https://docs.pydantic.dev/)

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.9+
- A Google Gemini API Key (Get it from [Google AI Studio](https://aistudio.google.com/))

### 2. Installation
Clone the repository and install the dependencies:
```bash
git clone [https://github.com/YOUR_USERNAME/Mimi-Companion.git](https://github.com/YOUR_USERNAME/Mimi-Companion.git)
cd Mimi-Companion
pip install -r requirements.txt
