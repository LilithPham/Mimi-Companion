# 🐾 Mimi Companion: AI-Driven Conversational English Partner

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Framework-FF4B4B?logo=streamlit&logoColor=white)
![Google Gemini](https://img.shields.io/badge/Google_Gemini-Flash-4285F4?logo=google&logoColor=white)
![Firebase](https://img.shields.io/badge/Firebase-Firestore-FFCA28?logo=firebase&logoColor=black)

**Mimi Companion** is an interactive, AI-powered EdTech platform designed to help beginner and intermediate learners overcome "speaking anxiety". By acting as a 24/7 virtual speaking partner gamified through friendly animal avatars, Mimi provides a stress-free environment for free-flowing English conversational practice.

---

## 📖 Table of Contents
- [Features](#-key-features)
- [System Architecture](#-system-architecture--data-pipeline)
- [Tech Stack](#-tech-stack)
- [NLP Analytics](#-nlp-analytics--metrics)
- [Installation & Setup](#-installation--local-setup)
- [Team & Acknowledgments](#-team)

---

## ✨ Key Features
- **Real-Time Voice Interaction:** Captures live user audio and transcribes it with high accuracy using multi-accent speech-to-text processing.
- **Structured Pedagogical Feedback:** Instead of behaving like a generic chatbot, the AI separates its responses into structured data, cleanly displaying exact **Grammar Corrections** and suggesting **Native Vocabulary**.
- **Mimi's Vocabulary Notebook:** Automatically logs advanced vocabulary suggested during conversations for later review.
- **Gamified Experience:** Users can select different virtual pet avatars, creating a zero-stress learning environment.
- **Persistent Sessions:** Securely tracks user learning history across multiple sessions using cookie-based authentication and NoSQL cloud storage.

---

## 🏗️ System Architecture & Data Pipeline
The application operates on a robust, real-time 4-step data pipeline:

1. **Audio Input (Frontend):** Raw audio bytes (WAV) are captured via the Streamlit interface and securely encoded into Base64 strings.
2. **Audio Processing Engine:** The encoded data is streamed to the Speech-to-Text model for accurate transcription.
3. **AI Core & Structured Output:** The raw transcript enters the LangChain-powered AI Brain. Using Pydantic schemas, the LLM is forced to return a predictable JSON object containing grammar evaluations and follow-up questions.
4. **Database & Storage:** The structured data is rendered on the UI and simultaneously pushed to Firebase Firestore (NoSQL) for historical tracking.

---

## 💻 Tech Stack
*   **Frontend UI/UX:** Streamlit, Custom HTML/CSS Injection
*   **AI Engine & Orchestration:** Google Gemini Flash API, LangChain
*   **Audio Processing:** Base64 Encoding, Whisper/Gemini Audio Extraction
*   **Database & Auth:** Firebase Firestore (NoSQL), Extra-Streamlit-Components (CookieController)
*   **Data Science & NLP:** Python (`collections.Counter`), Streamlit Charts

---

## 🧠 NLP Analytics & Metrics
The platform features a `My Progress` dashboard that goes beyond simple word counting. It utilizes Natural Language Processing (NLP) techniques to provide deep pedagogical insights:
*   **Type-Token Ratio (TTR):** Calculates the user's **Lexical Richness** by measuring the percentage of unique words against total spoken words.
*   **Stopword Removal & Word Frequency:** Automatically filters out common pronouns/connectors to identify the core vocabulary a user heavily repeats, prompting them to use synonyms.
*   **Error Tracking:** Analyzes the historical array to calculate the moving average of grammatical errors per sentence.

---

## 🚀 Installation & Local Setup

### Prerequisites
- Python 3.9 or higher
- A Google Gemini API Key
- Firebase Project Credentials (`firebase_key.json`)

### 1. Clone the repository
```bash
git clone [https://github.com/LilithPham/Mimi-Companion.git](https://github.com/LilithPham/Mimi-Companion.git)
cd Mimi-Companion

### 2. Install dependencies
```bash
pip install -r requirements.txt

### 3. Environment Variables
Create a .env file in the root directory and add your API keys:
```bash
GEMINI_API_KEY="your_google_api_key_here"

### 4. Run the application
The app will be available locally at http://localhost:8501.
```bash
streamlit run app.py

## 👥 Team
Developed by Computer Science students at Vietnamese-German University (VGU):

*   **Pham Minh Thu - Tech Lead, AI Core & Frontend Architecture

*   **Huynh Ngoc Vy - Audio Processing Engine

*   **Phan Thuc Quyen - Database Architecture & Analytics

This project is submitted as a capstone/group project for the Applied AI curriculum.
