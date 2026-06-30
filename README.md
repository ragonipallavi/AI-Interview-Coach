# 🎯 AI Interview Coach

A free, local, privacy-first interview practice tool powered by **FastAPI** and **Ollama**. Practice HR, technical, or mixed interviews tailored to your role and experience level, get AI-generated questions, and receive instant scoring with actionable feedback — all running on your own machine, with no data sent to the cloud.

## ✨ Features

- **Role & level aware questions** — Generates HR, Technical, or Mixed interview questions tailored to a specific role (e.g. Data Scientist, ML Engineer, Frontend Developer, Data Analyst) and seniority level (Fresher → Lead).
- **Resume-based interviews** — Paste your resume text and get interview questions generated from your actual experience, projects, and skills.
- **Instant AI scoring** — Each answer is scored on technical accuracy, clarity, relevance, and depth, with an overall score and specific feedback for improvement.
- **Confidence scoring** — A lightweight heuristic analyzes filler words, hedging language, and confident phrasing to estimate how confidently you answered.
- **Offline fallback question banks** — If the local LLM is unavailable or returns a poor response, curated fallback questions keep the interview going without interruption.
- **Save reports** — Interview sessions can be saved as JSON reports for later review.
- **Runs entirely locally** — Uses [Ollama](https://ollama.com) to run open-source LLMs (e.g. Llama 3) on your machine. No API keys, no cloud calls, no cost.

## 🛠️ Tech Stack

- **Backend:** FastAPI, Pydantic, Uvicorn
- **LLM:** Ollama (local inference, e.g. `llama3`)
- **Frontend:** Static HTML/CSS/JS served directly by FastAPI
- **Storage:** Local JSON report files

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- [Ollama](https://ollama.com) installed and running locally, with a model pulled:
  ```bash
  ollama pull llama3
  ```

### Installation

```bash
git clone <your-repo-url>
cd ai-interview-coach
pip install -r requirements.txt
```

### Run

```bash
python server.py
```

This starts the server and automatically opens **http://localhost:8000** in your browser.

## 📡 API Endpoints

| Method | Endpoint                 | Description                                      |
|--------|---------------------------|--------------------------------------------------|
| GET    | `/`                        | Serves the frontend                              |
| POST   | `/api/start`               | Generates a set of interview questions           |
| POST   | `/api/score`                | Scores a candidate's answer to a question         |
| POST   | `/api/resume-questions`    | Generates questions based on a pasted resume      |
| POST   | `/api/save-report`         | Saves a completed interview session as a report   |

## 📂 Project Structure

```
.
├── server.py            # FastAPI backend
├── static/
│   └── index.html        # Frontend UI
├── requirements.txt
└── feedback/              # Saved interview reports (created at runtime)
```

## 🔮 Roadmap Ideas

- Voice-based answer input with speech-to-text
- Multi-round interview simulations with follow-up questions
- Exportable PDF feedback reports
- Support for additional local LLM backends

## 📄 License

MIT — free to use, modify, and share.

---

Built to help job seekers practice interviews without paywalls, subscriptions, or sending personal data to third-party APIs.
