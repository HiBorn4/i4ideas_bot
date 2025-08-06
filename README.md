# 🤖 i4Ideas Smart Submission Assistant

![I4Ideas Banner](/public/Selection_001.png)

---

## 📘 Overview

**i4Ideas** is a smart AI-powered assistant designed to help users submit innovative ideas effortlessly.

Instead of manually categorizing ideas into complex buckets like *Productivity*, *Non-Productive*, *Quality*, or *Safety*, this chatbot walks users through a friendly, conversational interface to automatically classify and record their ideas.

It extracts and validates:
- 🎯 Idea statement
- 🚀 Implementation status
- 📊 Category & Subcategory
- 📉 Loss type
- 🛠️ Tools used
- 🧱 Rise Pillar classification
- 📈 Before/After impact metrics

This solution is especially valuable for companies looking to capture employee innovation without burdening users with forms or technical taxonomies.

---

## 🖼️ Live Demo

https://github.com/user-attachments/assets/616a1fca-3c82-4331-bada-4927cd9aad61

---

## ⚙️ Tech Stack

- 💬 **LangChain + Azure OpenAI GPT-4o**
- 🔧 **FastAPI** – backend logic and state handling
- 🗃️ **In-memory session tracking**
- 📄 **Streamlit / Gradio** – for voice/text interface
- 🔊 **Whisper** (Azure) – voice-to-text transcription
- 🎛️ **LangChain MessageHistory** – context-managed conversations

---

## 🚀 Getting Started

![How It Works](/public/Selection_002.png)

### 🔧 Backend

1. **Install dependencies**
```bash
pip install -r requirements.txt
```

2. **Run backend**
```bash
   cd backend
   uvicorn app:app --reload
```

> The backend handles LLM calls, voice transcription, and state tracking.
> It also includes `utils/` for debugging, prompt engineering, and classification helpers.

---

### 🧑‍💻 Frontend

1. **Launch Streamlit UI**

```bash
   cd backend
   streamlit run app.py
```

> This launches a web interface with voice + text chat powered by Azure GPT and Whisper.

---

## 💡 Why i4Ideas?

Manual idea submission forms can be overwhelming — users are expected to understand internal terminologies, classifications, and hierarchy.

**i4Ideas** solves this by:

* ✨ Asking only one question at a time
* 🔍 Extracting structure from free-form text
* ✅ Verifying and summarizing user inputs
* 📋 Returning final structured data in JSON and Markdown table

---

## 📁 Project Structure

```bash
i4ideas/
├── backend/
│   ├── app.py              # FastAPI app
│   ├── flow.py             # Conversation orchestration
│   ├── prompts.py          # Merged and contextual prompt management
│   ├── utils/              # Support scripts
│   ├── sessions/           # In-memory session tracking
│   └── requirements.txt
├── assets/
│   ├── banner-1.png
│   └── banner-2.png
└── README.md
```

---

## 📞 Contact

Feel free to reach out if you want to:

* Customize this bot for your org
* Integrate it with internal innovation systems
* Enhance its logic with form exports, Slack support, or database storage

---

> Created with ❤️ using GPT‑4o and LangChain.

### ✅ What’s Included
- 📷 Placeholder for **two images** at the top
- ⏺ Placeholder for **video demo**
- 📂 Full folder structure
- 🔥 Clear separation of frontend/backend usage
- 💼 Portfolio-quality description for **Upwork**, **Fiverr**, or clients
