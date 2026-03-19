# 📚 Shiksha-AI — Education Tutor for Remote India

> **Submitted to:** GenAI for GenZ Program · HPE × Intel  
> **Presented by:** Archana Vaidheeswaran

---

## 🌟 The Problem

Rural Indian students like **Priya, 15, from Rajasthan** have:
- No private tutor · 1 teacher for 40 students
- Only their state-board textbook as a resource
- A slow 2G internet connection

AI tutors exist — but they're **too expensive and too slow** for rural India.

---

## 💡 The Solution

**Shiksha-AI** is a personalized tutoring system that:
1. Ingests state-board textbooks (PDF, ~340 pages = ~85,000 tokens)
2. When a student asks a question, **compresses** the textbook to only the relevant paragraphs (~3,500 tokens)
3. Sends **only those paragraphs** to the LLM for a clear, simple answer

**Result: 96% reduction in API cost and data transfer per query.**

---

## 🏗️ Architecture

```
Student types question
        │
        ▼
┌─────────────────────────────────────────┐
│  Step 1: Compress   (ScaleDown API)     │
│  85,000 tokens  ──▶  ~3,500 tokens      │
│  (whole textbook)    (relevant only)    │
└─────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────┐
│  Step 2: Generate   (GPT-4o)            │
│  Send only relevant content             │
│  ──▶  Clear answer for student          │
└─────────────────────────────────────────┘
```

---

## 🚀 Features

### Core Pipeline
| Feature | Description |
|---|---|
| 📄 PDF Textbook Ingestion | Upload any state-board PDF textbook |
| ✂️ ScaleDown Compression | Compress 85K tokens → ~3.5K per query |
| 🎓 AI Answer Generation | GPT-4o answers only from relevant content |

### Bonus Features
| Bonus | Description |
|---|---|
| 🗜️ History Compression | Compress previous Q&A turns before each new question |
| 🔀 Smart Model Routing | gpt-4o-mini for simple / gpt-4o for complex questions |
| 💰 Savings Counter | Live NGO dashboard: tokens saved + rupees saved |
| ⚡ Topic Pre-caching | Batch-compress common exam topics at start of day |

---

## 💸 Cost Comparison

| Approach | Tokens per Query | Cost per Query |
|---|---|---|
| ❌ Baseline (full textbook) | ~85,000 tokens | ₹3.80 |
| ✅ Shiksha-AI (compressed) | ~3,500 tokens | ₹0.17 |
| **Savings** | **96% fewer tokens** | **₹3.63 saved** |

---

## 🗂️ Project Structure

```
shiksha-ai/
├── index.html          ← Complete frontend (login + tutor + dashboard)
├── app.py              ← Python Flask backend
├── requirements.txt    ← Python dependencies
└── README.md           ← This file
```

---

## ⚙️ Setup & Run

### 1. Clone
```bash
git clone https://github.com/YOUR_USERNAME/shiksha-ai.git
cd shiksha-ai
```

### 2. Install
```bash
pip install -r requirements.txt
```

### 3. Configure
```bash
# Set environment variables:
export OPENAI_API_KEY=sk-...
export SCALEDOWN_API_KEY=your-scaledown-key
export SECRET_KEY=any-random-string
```

### 4. Run backend
```bash
python app.py
# → http://localhost:5000
```

### 5. Open frontend
Open `index.html` in your browser directly — no build step needed.

> **Demo Mode:** Works without API keys. Login, chat simulation, and savings counter all run locally.

---

## 🔑 Demo Accounts

| Role | Email | Password |
|---|---|---|
| 🎓 Student | student@shiksha.ai | shiksha123 |
| 🏫 Teacher | teacher@shiksha.ai | teach123 |
| 🏢 NGO Admin | admin@shiksha.ai | admin123 |

---

## 📡 API Reference

| Method | Endpoint | Description |
|---|---|---|
| POST | /api/login | Authenticate user |
| POST | /api/logout | Sign out |
| POST | /api/upload-textbook | Upload PDF textbook |
| POST | /api/ask | Ask a question (core pipeline) |
| GET | /api/savings | Session savings data |
| GET | /api/history | Chat history |
| POST | /api/precache-topics | Pre-compress common topics |

---

## 🧠 Why ScaleDown over RAG?

Traditional RAG needs: vector DB setup, embedding model, re-indexing on updates.  
For an NGO on a shoestring budget — that's a steep hill.

ScaleDown does "find the relevant part" in **one API call**: no embeddings, no vector DB, no chunking debates.

---

## 🙏 Acknowledgements

Built for the **GenAI for GenZ** program by **HPE × Intel**.  
Inspired by the real educational challenges of students in rural India.

---

## 📄 License

MIT — free to use, modify, and deploy for educational purposes.
