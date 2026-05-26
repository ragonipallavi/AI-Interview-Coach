# 🎯 AI Interview Coach

A fully local AI-powered interview coach — **pure HTML/CSS/JS frontend** with a **FastAPI backend**, powered by **Ollama**.

## Stack
| Layer | Tech | Why |
|---|---|---|
| Frontend | HTML + CSS + JS | Full control, no framework needed |
| Speech-to-Text | Web Speech API (built into Chrome/Edge) | Zero installs, free, works offline |
| Backend | FastAPI + Python | Lightweight, fast |
| AI / LLM | Ollama (local) | Private, free, no API key |

## Quick Start

### 1. Install Ollama + pull a model
```bash
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llama3          # HR interviews
ollama pull deepseek-coder  # Technical interviews
```

### 2. Install Python packages
```bash
pip install -r requirements.txt
```

### 3. Run
```bash
python server.py
```

Open **http://localhost:8000** in **Chrome or Edge**.

---

## Voice Input

Uses the **Web Speech API** — built into Chrome and Edge.  
**No Whisper. No ffmpeg. No installs.**

Flow:
1. Click **🎙 Start Recording** → speak your answer
2. Click **⏹ Stop Recording** → transcript appears in the editable box
3. Edit any transcription errors if needed
4. Click **✅ Submit Answer**

---

## Project Structure

```
AI-Interview-Coach/
├── server.py          ← FastAPI backend (all AI logic)
├── requirements.txt
├── README.md
├── static/
│   └── index.html     ← Entire frontend (HTML + CSS + JS)
├── uploads/           ← Auto-created
└── feedback/          ← Saved reports (JSON)
```

---

## Models Guide

| Task | Model | Pull |
|---|---|---|
| HR Questions | llama3 | `ollama pull llama3` |
| Technical QA | deepseek-coder | `ollama pull deepseek-coder` |
| Fast / Low RAM | phi3 | `ollama pull phi3` |
| Tiny RAM | tinyllama | `ollama pull tinyllama` |
