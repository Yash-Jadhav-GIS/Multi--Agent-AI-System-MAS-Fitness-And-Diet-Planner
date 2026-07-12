# 🥗 Multi-Agent AI System (MAS) – Fitness & Diet Planner

An intelligent multi-agent AI system that generates personalized fitness and diet plans using Large Language Models (LLMs), Retrieval-Augmented Generation (RAG), and agent-based reasoning.

## 🚀 Features

- 👤 Personalized user profiling
- 🤖 Multi-Agent architecture
- 🧠 LLM-powered recommendations
- 📚 RAG using PDF knowledge base
- 💪 Weekly workout planner
- 🥗 Personalized diet planner
- 📄 PDF report generation
- ⚡ FastAPI backend
- 🔗 LangGraph workflow
- 🛠️ Modular and scalable project structure

---

## 🏗️ Tech Stack

### Backend

- Python
- FastAPI
- LangChain
- LangGraph

### AI

- Groq API
- Ollama (optional)
- LLMs

### Database

- SQLite / PostgreSQL

### Vector Database

- ChromaDB

### PDF Processing

- PyPDF
- ReportLab

### Deployment

- Docker (optional)

---

## 📂 Project Structure

```text
project/
│
├── app/
├── agents/
├── services/
├── workflows/
├── prompts/
├── schemas/
├── utils/
├── vector_db/
├── data/
├── reports/
├── .env.example
├── requirements.txt
└── main.py
```

---

## ⚙️ Installation

### Clone Repository

```bash
git clone https://github.com/Yash-Jadhav-GIS/Multi--Agent-AI-System-MAS-Fitness-And-Diet-Planner.git

cd Multi--Agent-AI-System-MAS-Fitness-And-Diet-Planner
```

### Create Virtual Environment

```bash
python -m venv .venv
```

Windows

```bash
.venv\Scripts\activate
```

Linux / macOS

```bash
source .venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file.

```env
GROQ_API_KEY=your_api_key_here
```

> **Do not commit your `.env` file.** Keep it local.

---

## Run Application

```bash
uvicorn main:app --reload
```

Open:

```
http://127.0.0.1:8000
```

Swagger UI:

```
http://127.0.0.1:8000/docs
```

---

## Roadmap

- [x] User Profiling
- [x] Multi-Agent Workflow
- [x] Diet Recommendation
- [x] Workout Recommendation
- [x] RAG Pipeline
- [x] PDF Report Generation
- [ ] PostgreSQL Integration
- [ ] Docker Support
- [ ] Authentication
- [ ] Frontend Dashboard
- [ ] Cloud Deployment

---

## Security

- Never commit `.env`.
- Never expose API keys.
- Rotate compromised API keys immediately.

---

## Author

**Yash Jadhav**

AI Engineer | GenAI | Agentic AI | Machine Learning | GeoAI

GitHub: https://github.com/Yash-Jadhav-GIS

---

## License

This project is licensed under the MIT License.