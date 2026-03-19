"""
Shiksha-AI Backend
Education Tutor for Remote India
Pipeline: PDF Upload → ScaleDown Compression → GPT-4o Answer
"""

from flask import Flask, request, jsonify, session
from flask_cors import CORS
import os
import json
import time
import hashlib
from datetime import datetime
import PyPDF2
import io
import openai
import requests
from functools import wraps

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "shiksha-ai-secret-2024")
CORS(app, supports_credentials=True)

# ── API Configuration ──────────────────────────────────────────────────────────
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
SCALEDOWN_API_KEY = os.environ.get("SCALEDOWN_API_KEY", "")
SCALEDOWN_URL = "https://api.scaledown.xyz/compress/raw/"

openai_client = openai.OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# ── In-memory stores (replace with DB in production) ──────────────────────────
USERS = {
    "student@shiksha.ai": {"password": "shiksha123", "role": "student", "name": "Priya Sharma"},
    "admin@shiksha.ai":   {"password": "admin123",   "role": "admin",   "name": "NGO Admin"},
    "teacher@shiksha.ai": {"password": "teach123",   "role": "teacher", "name": "Ravi Sir"},
}

textbook_store = {}        # session_id -> textbook_text
chat_history   = {}        # session_id -> list of {role, content}
savings_store  = {}        # session_id -> {tokens_original, tokens_compressed, cost_saved}

# Pre-compression cache: topic -> compressed_content
topic_cache = {}

# Common exam questions for pre-compression
COMMON_TOPICS = [
    "osmosis", "photosynthesis", "Newton's laws",
    "mitosis", "cell division", "digestive system",
    "water cycle", "respiration", "gravity",
]


# ── Auth helpers ───────────────────────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user = session.get("user")
        if not user:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated


# ── Routes: Auth ───────────────────────────────────────────────────────────────
@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    email    = data.get("email", "").strip().lower()
    password = data.get("password", "")

    user = USERS.get(email)
    if not user or user["password"] != password:
        return jsonify({"error": "Invalid credentials"}), 401

    session["user"] = {"email": email, "role": user["role"], "name": user["name"]}
    session_id = hashlib.md5(f"{email}{time.time()}".encode()).hexdigest()[:12]
    session["sid"] = session_id

    # init stores for this session
    chat_history[session_id]  = []
    savings_store[session_id] = {"tokens_original": 0, "tokens_compressed": 0, "cost_saved_inr": 0.0}

    return jsonify({
        "message": "Login successful",
        "user": {"email": email, "role": user["role"], "name": user["name"]},
        "session_id": session_id,
    })


@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logged out"})


@app.route("/api/me", methods=["GET"])
@login_required
def me():
    return jsonify({"user": session["user"], "session_id": session.get("sid")})


# ── Routes: Textbook Upload ────────────────────────────────────────────────────
@app.route("/api/upload-textbook", methods=["POST"])
@login_required
def upload_textbook():
    sid = session.get("sid")
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if not file.filename.endswith(".pdf"):
        return jsonify({"error": "Only PDF files are supported"}), 400

    try:
        reader = PyPDF2.PdfReader(io.BytesIO(file.read()))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        pages = len(reader.pages)
        tokens_approx = len(text.split()) * 1.3

        textbook_store[sid] = text
        return jsonify({
            "message": "Textbook uploaded successfully",
            "pages": pages,
            "tokens_approx": int(tokens_approx),
            "filename": file.filename,
        })
    except Exception as e:
        return jsonify({"error": f"Failed to process PDF: {str(e)}"}), 500


# ── Core Pipeline ──────────────────────────────────────────────────────────────
def compress_with_scaledown(context: str, question: str) -> tuple[str, int, int]:
    """
    Step 1: Call ScaleDown to extract only the relevant parts.
    Returns (compressed_text, original_tokens, compressed_tokens)
    """
    original_tokens = int(len(context.split()) * 1.3)

    if not SCALEDOWN_API_KEY:
        # Demo mode: simulate compression by extracting paragraphs with keywords
        keywords = question.lower().split()
        paragraphs = context.split("\n\n")
        relevant = [p for p in paragraphs if any(k in p.lower() for k in keywords)]
        compressed = "\n\n".join(relevant[:5]) if relevant else context[:2000]
        compressed_tokens = int(len(compressed.split()) * 1.3)
        return compressed, original_tokens, compressed_tokens

    headers = {
        "x-api-key": SCALEDOWN_API_KEY,
        "Content-Type": "application/json",
    }
    payload = {
        "context": context,
        "prompt": question,
        "scaledown": {"rate": "auto"},
    }
    try:
        resp = requests.post(SCALEDOWN_URL, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        compressed = resp.json().get("compressed_prompt", context[:3000])
        compressed_tokens = int(len(compressed.split()) * 1.3)
        return compressed, original_tokens, compressed_tokens
    except Exception:
        # Fallback
        compressed = context[:3000]
        return compressed, original_tokens, int(len(compressed.split()) * 1.3)


def route_model(compressed_tokens: int) -> str:
    """Bonus: Route to cheaper model for simple questions."""
    if compressed_tokens < 1000:
        return "gpt-4o-mini"
    return "gpt-4o"


def generate_answer(relevant_content: str, question: str, model: str) -> str:
    """Step 2: Call LLM with only the relevant content."""
    if not openai_client:
        # Demo mode
        return (
            f"[DEMO MODE — No OpenAI key set]\n\n"
            f"Based on the textbook content, here is a simplified answer about '{question}':\n\n"
            f"The relevant sections of your textbook explain this concept in detail. "
            f"In a real deployment with an OpenAI API key, I would give you a clear, "
            f"accurate explanation using simple language suitable for Class 10 students.\n\n"
            f"*Relevant content extracted ({len(relevant_content.split())} words)*"
        )

    system_prompt = (
        "You are a patient, encouraging tutor for Indian high school students. "
        "Explain concepts clearly using simple language and everyday examples. "
        "Answer ONLY from the provided textbook content. "
        "If the content doesn't cover the question, say so. "
        "Use relatable Indian examples (dal-chawal, mango tree, etc.) when helpful."
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Textbook content:\n{relevant_content}\n\nStudent's question: {question}"},
    ]
    response = openai_client.chat.completions.create(
        model=model, messages=messages, max_tokens=600
    )
    return response.choices[0].message.content


def compress_chat_history(history: list, new_question: str) -> list:
    """Bonus: Compress previous conversation turns to save tokens."""
    if len(history) <= 2:
        return history
    # Keep only contextually relevant previous turns (simple keyword matching)
    keywords = set(new_question.lower().split())
    compressed = []
    for turn in history[-6:]:  # max 3 QA pairs
        content_words = set(turn["content"].lower().split())
        overlap = keywords & content_words
        if len(overlap) > 2:
            compressed.append(turn)
    return compressed


# ── Routes: Ask Question ───────────────────────────────────────────────────────
@app.route("/api/ask", methods=["POST"])
@login_required
def ask_question():
    sid   = session.get("sid")
    data  = request.json
    question = data.get("question", "").strip()

    if not question:
        return jsonify({"error": "Question cannot be empty"}), 400

    textbook = textbook_store.get(sid, "")
    if not textbook:
        return jsonify({"error": "Please upload a textbook first"}), 400

    history = chat_history.get(sid, [])

    # ── Bonus: compress conversation history ──────────────────────────────────
    compressed_history = compress_chat_history(history, question)

    # ── Step 1: Compress textbook ─────────────────────────────────────────────
    relevant_content, orig_tokens, comp_tokens = compress_with_scaledown(textbook, question)

    # ── Bonus: route to cheaper model ─────────────────────────────────────────
    model = route_model(comp_tokens)

    # ── Step 2: Generate answer ────────────────────────────────────────────────
    answer = generate_answer(relevant_content, question, model)

    # ── Update stores ─────────────────────────────────────────────────────────
    history.append({"role": "user",      "content": question})
    history.append({"role": "assistant", "content": answer})
    chat_history[sid] = history

    savings = savings_store.get(sid, {"tokens_original": 0, "tokens_compressed": 0, "cost_saved_inr": 0.0})
    savings["tokens_original"]   += orig_tokens
    savings["tokens_compressed"] += comp_tokens
    tokens_saved = orig_tokens - comp_tokens
    # GPT-4o input: ~₹0.005 per 1K tokens; savings in INR
    savings["cost_saved_inr"] = round(savings["cost_saved_inr"] + (tokens_saved / 1000) * 0.005 * 85, 2)
    savings_store[sid] = savings

    compression_ratio = round((1 - comp_tokens / max(orig_tokens, 1)) * 100, 1)

    return jsonify({
        "answer": answer,
        "model_used": model,
        "tokens": {
            "original": orig_tokens,
            "compressed": comp_tokens,
            "compression_ratio": compression_ratio,
        },
        "savings": savings,
    })


# ── Routes: Savings Dashboard (Admin) ─────────────────────────────────────────
@app.route("/api/savings", methods=["GET"])
@login_required
def get_savings():
    sid = session.get("sid")
    return jsonify(savings_store.get(sid, {}))


@app.route("/api/history", methods=["GET"])
@login_required
def get_history():
    sid = session.get("sid")
    return jsonify({"history": chat_history.get(sid, [])})


@app.route("/api/clear-history", methods=["POST"])
@login_required
def clear_history():
    sid = session.get("sid")
    chat_history[sid] = []
    return jsonify({"message": "History cleared"})


# ── Routes: Pre-compress topics ───────────────────────────────────────────────
@app.route("/api/precache-topics", methods=["POST"])
@login_required
def precache_topics():
    sid     = session.get("sid")
    textbook = textbook_store.get(sid, "")
    if not textbook:
        return jsonify({"error": "No textbook loaded"}), 400

    cached = []
    for topic in COMMON_TOPICS:
        if topic not in topic_cache:
            compressed, _, _ = compress_with_scaledown(textbook, topic)
            topic_cache[topic] = compressed
            cached.append(topic)

    return jsonify({"cached_topics": cached, "total_cached": len(topic_cache)})


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "app": "Shiksha-AI",
        "version": "1.0.0",
        "openai_configured": bool(OPENAI_API_KEY),
        "scaledown_configured": bool(SCALEDOWN_API_KEY),
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)
