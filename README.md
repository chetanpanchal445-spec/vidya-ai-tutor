# 🎓 Vidya AI — Education Tutor for Remote India

> **GenAI for GenZ Hackathon Project** | Built for rural Indian students with low-bandwidth connectivity and limited resources.

![Vidya AI Banner](https://img.shields.io/badge/GenAI_for_GenZ-Hackathon_2025-FF6B00?style=for-the-badge)
![Claude API](https://img.shields.io/badge/Powered_by-Claude_AI-blue?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

---

## 🌍 The Problem

Rural Indian students like **Priya, 15, from Rajasthan** face a harsh reality:
- 1 teacher for 40+ students
- Spotty 2G internet connections
- No access to private tutors
- Their only resource: a 340-page state-board textbook

Existing AI tutors are built for cities — high-cost, high-latency, and financially inaccessible.

---

## 💡 Our Solution

**Vidya AI** is a personalized tutoring system that:
1. Ingests state-board textbooks (PDF/text)
2. Answers student questions in **real time**
3. Is optimized for **lowest cost per query** and **minimal data transfer**

Instead of sending 85,000 tokens (the whole textbook) to an LLM every time, Vidya AI first **extracts only the relevant paragraphs** (~3,000 tokens), then generates the answer. This results in **~95% token reduction per query**.

---

## 🧠 How It Works

```
Student types question
        │
        ▼
┌─────────────────────┐
│  STEP 1: COMPRESS   │  ← Send full textbook + question to Claude
│  Find relevant      │    Claude returns ONLY the relevant paragraphs
│  paragraphs only    │    (340 pages → ~4 pages)
└─────────────────────┘
        │
        ▼
┌─────────────────────┐
│  STEP 2: ANSWER     │  ← Send only relevant content to Claude
│  Generate a clear   │    Claude answers in simple language
│  student-level      │    with Indian everyday examples
│  explanation        │
└─────────────────────┘
        │
        ▼
   Student gets answer ✅
   (Cost: ₹0.03 instead of ₹0.38)
```

**No vector database. No embeddings. No chunking. Just 2 API calls.**

---

## 📊 Key Metrics

| Metric | Baseline RAG | Vidya AI |
|--------|-------------|----------|
| Tokens per query | ~85,000 | ~3,400 |
| Cost per query | ₹0.38 | ₹0.03 |
| Setup complexity | High (vector DB, embeddings) | Zero |
| Works on 2G? | ❌ | ✅ |

---

## 🚀 Features

- 📖 **Upload or paste textbook** — supports TXT files or direct paste
- 🧬 **6 subjects** — Biology, Physics, Chemistry, Math, History, Geography
- 🗜️ **Smart compression** — only relevant content sent to AI
- 💡 **Simple explanations** — tuned for Indian high school students
- 💰 **Live savings counter** — tracks tokens saved and ₹ saved per session
- 📋 **Session history** — view all questions asked this session
- ⚡ **2-API-call pipeline** — no infrastructure needed

---

## 🛠️ Tech Stack

- **Frontend**: Pure HTML, CSS, JavaScript (single file, no framework)
- **AI**: Claude API (`claude-sonnet-4-20250514`) via Anthropic
- **Architecture**: 2-step prompt pipeline (compress → generate)
- **Hosting**: Works as a static file — no server needed

---

## 📁 Project Structure

```
vidya-ai/
│
├── index.html          ← The entire app (single file)
├── README.md           ← This file
├── sample_textbooks/
│   └── biology_ch8.txt ← Sample osmosis chapter for testing
└── screenshots/
    └── demo.png        ← App screenshot
```

---

## ⚡ Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/vidya-ai.git
cd vidya-ai
```

### 2. Open the app

Just open `index.html` in your browser — no installation needed!

```bash
# On Mac
open index.html

# On Linux
xdg-open index.html

# On Windows
start index.html
```

### 3. Get an API key

- Go to [console.anthropic.com](https://console.anthropic.com)
- Create a free account and generate an API key
- The app uses the Anthropic API directly from the browser

> **Note**: For production use, you'd want a backend proxy to keep your API key secure. For this hackathon demo, the key is handled by the Claude.ai environment.

### 4. Test it

1. The app loads with a sample Biology chapter (Osmosis) pre-filled
2. Type a question like: *"What is osmosis?"*
3. Click **Ask Vidya Tutor**
4. Watch the pipeline compress and answer!

---

## 🎯 Design Decisions

### Why NOT a RAG pipeline?

Road A (RAG) requires:
- A vector database (Pinecone, Weaviate)
- Running an embedding model on every textbook chunk
- Re-indexing when the textbook changes
- ₹₹₹ infrastructure costs

For an NGO running this on a shoestring budget for rural India — that's a steep hill.

### Why 2-step prompting?

Road B (our approach) uses Claude's ability to **read and filter** in a single API call. We ask Claude to act as a smart study partner: *"Don't read the whole book. Flip to the right chapter. Scan for the relevant paragraphs."*

The result: same quality, ~95% lower cost, zero infrastructure.

### Why single HTML file?

- Works offline after first load
- Easy to deploy anywhere (GitHub Pages, WhatsApp file sharing, USB stick)
- No build step, no dependencies, no node_modules
- Any teacher can host it

---

## 🌟 Bonus Features (Implemented)

- [x] **Savings counter** — visible ₹ savings to show NGO admins the value
- [x] **Session history** — tracks all questions in the current session
- [x] **Subject switching** — tutor persona adapts to the selected subject
- [ ] **Conversation compression** — compress chat history between turns (planned)
- [ ] **Model routing** — use cheaper model for simple factual questions (planned)
- [ ] **Pre-compressed cache** — batch compress common exam topics at start of day (planned)

---

## 👥 Team

Built for the **GenAI for GenZ** program by HPE × Intel.

---

## 📄 License

MIT License — free to use, modify, and deploy for educational purposes.

---

## 🙏 Acknowledgements

- [Anthropic](https://anthropic.com) for Claude API
- HPE × Intel for the GenAI for GenZ program
- Inspired by the 250 million rural Indian students who deserve better education tools
