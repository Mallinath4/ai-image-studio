# 🖼️ AI Image Studio
### Complete Project Documentation — v2.0.0

> Intelligent text-to-image generation powered by FLUX.1-schnell, Mistral 7B & FAISS RAG

![Version](https://img.shields.io/badge/version-2.0.0-purple)
![License](https://img.shields.io/badge/license-Apache%202.0-blue)
![Python](https://img.shields.io/badge/python-3.10+-green)

---

## 📋 Table of Contents
1. [Problem Statement](#1-problem-statement)
2. [Project Overview](#2-project-overview)
3. [System Architecture](#3-system-architecture)
4. [Technology Stack](#4-technology-stack)
5. [Project Structure](#5-project-structure)
6. [Step-by-Step Implementation](#6-step-by-step-implementation)
7. [Key Features](#7-key-features)
8. [Setup and Installation](#8-setup-and-installation)
9. [How It Works](#9-how-it-works)
10. [Future Enhancements](#10-future-enhancements)
11. [Changelog](#11-changelog)

---

## 1. Problem Statement

### The Challenge
Traditional text-to-image generation tools have several limitations:

**❌ Problems with Existing Solutions:**
- Require expensive cloud subscriptions (MidJourney $30/month, DALL-E paid API)
- Need powerful GPU hardware (RTX 3090+ for local Stable Diffusion)
- Limited customization and theme options
- No memory of past generations
- Single image generation at a time
- Complex setup for beginners
- Prompts need manual refinement for quality results

**✅ Our Solution:**
Build a **free, open-source, multi-theme AI image generator** that:
- Works on any laptop (no GPU required)
- Generates multiple themed images at once
- Remembers past generations (RAG memory)
- Auto-enhances prompts using LLM reasoning
- Beautiful, intuitive UI
- Zero cost (uses free HuggingFace API)

---

## 2. Project Overview

**AI Image Studio** is an intelligent text-to-image generation system that combines three powerful AI technologies:

| Technology | Role |
|---|---|
| **FLUX.1-schnell** | State-of-the-art image generation (12B parameters) |
| **Mistral 7B** | Local LLM for intelligent prompt enhancement |
| **FAISS + MiniLM** | Vector database for RAG memory |
| **Custom Auth** *(New)* | Signup / login / user tracking |

### Key Innovation
Unlike traditional tools, our system **learns from your style** over time using RAG (Retrieval-Augmented Generation) and can generate **multiple themed variations** of your idea in one click — all completely free.

---

## 3. System Architecture

─────────────────────────────────────────────────────────────┐
│ USER INTERFACE │
│ (Streamlit Web Application) │
└──────────────────┬──────────────────────────────────────────┘
│
┌─────────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐
│ Prompt Input │ │Theme Select │ │ AI Settings │
│ + Analyzer │ │Multi-Select │ │RAG / LLM │
└────────┬───────┘ └──────┬──────┘ └──────┬──────┘
└─────────────────┴─────────────────┘
│
┌────────────────┴────────────────┐
│ │
┌──────────▼──────────┐ ┌───────────▼───────────┐
│ RAG SYSTEM │ │ LLM REASONING │
│ FAISS Vector Search│ │ Mistral 7B (Ollama) │
└──────────┬──────────┘ └───────────┬───────────┘
└──────────────┬────────────────────┘
│
┌──────────▼──────────┐
│ PROMPT BUILDER │
│ Original + Theme + │
│ RAG Context + LLM │
└──────────┬──────────┘
│
┌──────────────────┴──────────────────┐
│ │
┌──────────▼──────────┐ ┌───────────▼───────────┐
│ FLUX.1-schnell API │◄─────────────┤ IMAGE GENERATION │
│ (HuggingFace) │ │ LOOP (per theme) │
│ Returns PNG bytes │ └───────────┬───────────┘
└──────────┬──────────┘ │
└──────────────────┬──────────────────┘
│
┌──────────▼──────────┐
│ STORAGE SYSTEM │
│ PNG + RAG + Metadata│
└─────────────────────┘

text

---

## 4. Technology Stack

### 4.1 Frontend — Streamlit + Custom CSS
- **What:** Python web framework — no HTML/CSS/JS needed
- **Why:** Rapid prototyping, built-in state management, real-time updates
- **Problem solved:** Full web UI built in hours, not weeks

### 4.2 Image Generation — FLUX.1-schnell
- **What:** 12B parameter rectified flow transformer by Black Forest Labs
- **Why:** Best quality/speed ratio — generates in 1–4 steps (vs 50 for Stable Diffusion)
- **How:** Served via HuggingFace Router API — zero local storage required
- **Problem solved:** No 24GB model download, no GPU needed

Model: black-forest-labs/FLUX.1-schnell
Parameters: 12 billion
Steps: 1–4 (Stable Diffusion needs 50+)
Speed: 10–30 seconds per image
Cost: Free (HuggingFace free tier)


### 4.3 LLM Reasoning — Mistral 7B via Ollama
- **What:** 7B parameter open-source LLM running locally on localhost:11434
- **Why:** Analyzes composition, lighting, mood — transforms basic prompts to professional quality
- **Fallback:** Rule-based enhancement if Ollama is not running

**Enhancement Example:**
Input: "cat in chair"

Output: "A white cat with green eyes sitting in a wooden chair near
a large window with soft golden hour sunlight, shadow details,
photorealistic, 8k, ultra detailed, natural lighting, sharp focus".


### 4.4 RAG Memory — FAISS + MiniLM
- **What:** Facebook AI Similarity Search + sentence-transformers/all-MiniLM-L6-v2
- **Why:** Converts prompts to 384-dim vectors, retrieves top-3 similar past generations as context
- **Effect:** Style consistency grows automatically over time
- **Problem solved:** App used to forget every session — now it remembers forever

### 4.5 Auth Layer *(New in v2.0)*
- **What:** Custom local auth with SHA-256 password hashing
- **Why:** Multi-user support, personalized generation count, no external auth service needed
- **Storage:** `auth/users.json` (never in git)
- **Features:** Signup, login (via email or username), change password, per-user gen count

### 4.6 Storage Layer
generated_images/
├── realistic_2517315211_20260304.png
├── animated_2517315212_20260304.png
└── cyberpunk_2517315213_20260304.png

data/rag_store/
├── index.faiss ← vector index
└── metadata.json ← prompt history

auth/
└── users.json ← hashed credentials (not in git)


---

## 5. Project Structure

ai-image-studio/
│
├── app.py # Main Streamlit application
│
├── auth/ # ← NEW: Authentication module
│ ├── init.py
│ └── auth_handler.py # login, signup, change_password, update_gen_count
│
├── pipeline/
│ ├── init.py
│ ├── flux_generator.py # FLUX API wrapper
│ ├── prompt_enhancer.py # Mistral LLM integration
│ └── rag_store.py # FAISS vector database
│
├── utils/
│ ├── init.py
│ └── image_utils.py # Image saving, download, utilities
│
├── assets/
│ └── style.css # Custom dark theme CSS
│
├── generated_images/ # Output directory (auto-created)
│ └── .gitkeep
│
├── data/
│ └── rag_store/ # RAG index storage (auto-created)
│ ├── index.faiss
│ └── metadata.json
│
├── .env # HuggingFace token (SECRET - not in git)
├── .gitignore
├── requirements.txt
└── README.md


> **⚠️ Note:** The `components/` directory (`img2img_tab.py`, `voice_prompt.py`, `style_mixer.py`) was removed in v2.0. Those tabs are no longer part of the core app.

---

## 6. Step-by-Step Implementation

### Step 1 — Environment Setup

```bash
mkdir ai-image-studio
cd ai-image-studio
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Mac/Linux

Step 2 — Install Dependencies
requirements.txt:
streamlit>=1.32.0
Pillow>=10.0.0
requests>=2.31.0
faiss-cpu>=1.7.4
sentence-transformers>=3.0.0
numpy>=1.26.0
python-dotenv>=1.0.0


pip install -r requirements.txt


Step 3 — HuggingFace Setup
# Create .env file
echo HF_TOKEN=hf_your_token_here > .env

# Accept FLUX model license:
# https://huggingface.co/black-forest-labs/FLUX.1-schnell
# → Click "Agree and access repository"


Step 4 — Build Auth Handler (auth/auth_handler.py) 

import json, os, hashlib
from datetime import datetime

USERS_PATH = "auth/users.json"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    if not os.path.exists(USERS_PATH):
        return {}
    with open(USERS_PATH) as f:
        return json.load(f)

def save_users(users):
    os.makedirs("auth", exist_ok=True)
    with open(USERS_PATH, "w") as f:
        json.dump(users, f, indent=2)

def signup_user(username, email, password, confirm):
    if password != confirm:
        return False, "Passwords do not match."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    users = load_users()
    for u in users.values():
        if u["username"] == username:
            return False, "Username already taken."
        if u["email"] == email:
            return False, "Email already registered."
    user_id = str(len(users) + 1)
    users[user_id] = {
        "user_id": user_id, "username": username, "email": email,
        "password": hash_password(password), "gen_count": 0,
        "created_at": datetime.now().isoformat()
    }
    save_users(users)
    return True, "Account created successfully!"

def login_user(email_or_user, password):
    hashed = hash_password(password)
    for u in load_users().values():
        if (u["email"] == email_or_user or u["username"] == email_or_user) \
                and u["password"] == hashed:
            return True, "Login successful!", u
    return False, "Invalid credentials.", None

def update_gen_count(user_id):
    users = load_users()
    if user_id in users:
        users[user_id]["gen_count"] = users[user_id].get("gen_count", 0) + 1
        save_users(users)

def change_password(user_id, current_pw, new_pw):
    users = load_users()
    if user_id not in users:
        return False, "User not found."
    if users[user_id]["password"] != hash_password(current_pw):
        return False, "Current password is incorrect."
    users[user_id]["password"] = hash_password(new_pw)
    save_users(users)
    return True, "Password updated successfully!"


Step 5 — Build FLUX Generator (pipeline/flux_generator.py)
import io, os, random, requests
from PIL import Image
from dotenv import load_dotenv

load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")
API_URL  = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"
HEADERS  = {"Authorization": f"Bearer {HF_TOKEN}", "Content-Type": "application/json"}

def load_flux_pipeline():
    return True  # API-based, no local download needed

def generate_image(prompt, width=768, height=768, quality="high", seed=-1):
    if seed == -1:
        seed = random.randint(0, 2**32 - 1)
    width  = max(256, min(1024, (width  // 16) * 16))
    height = max(256, min(1024, (height // 16) * 16))
    steps_map = {"draft": 1, "standard": 3, "high": 4}
    payload = {
        "inputs": prompt,
        "parameters": {
            "width": width, "height": height,
            "num_inference_steps": steps_map.get(quality, 4),
            "guidance_scale": 0.0, "seed": seed
        }
    }
    response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=120)
    if response.status_code == 200:
        return Image.open(io.BytesIO(response.content)).convert("RGB"), seed
    raise Exception(f"API Error {response.status_code}: {response.text}")

Step 6 — Build Prompt Enhancer (pipeline/prompt_enhancer.py)

import requests

OLLAMA_URL = "http://localhost:11434/api/generate"

THEME_KEYWORDS = {
    "Realistic":   "photorealistic, 8k, ultra detailed, natural lighting",
    "Animated":    "anime style, vibrant colors, cel shading",
    "Cyberpunk":   "cyberpunk city, neon lights, rainy streets",
    "Fantasy":     "fantasy art, magical, ethereal lighting",
    "Horror":      "dark horror, eerie atmosphere, dramatic shadows",
    "Fairy Tale":  "fairy-tale illustration, whimsical, soft pastels",
    "Ancient":     "ancient civilization, stone textures, historical",
    "Jungle":      "lush jungle, tropical, dappled sunlight",
    "Futuristic":  "futuristic, sci-fi, holographic elements",
    "Mystical":    "mystical, glowing runes, divine light",
    "Watercolor":  "watercolor painting, soft edges, artistic",
}

def enhance_prompt(user_prompt, theme_suffix=""):
    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": "mistral",
                  "prompt": f"Enhance this image prompt with composition, lighting, mood: {user_prompt}",
                  "stream": False},
            timeout=30
        )
        if response.status_code == 200:
            enhanced = response.json()["response"].strip()
            return {"enhanced_prompt": f"{enhanced}, {theme_suffix}",
                    "thinking": "Mistral analyzed composition and mood"}
    except:
        pass
    # Rule-based fallback
    parts = [user_prompt.strip()]
    if theme_suffix:
        parts.append(theme_suffix)
    parts.append("masterpiece, best quality, highly detailed")
    return {"enhanced_prompt": ", ".join(parts), "thinking": "Rule-based enhancement"}

Step 7 — Build RAG Store (pipeline/rag_store.py)
import os, json, faiss, numpy as np
from sentence_transformers import SentenceTransformer
from datetime import datetime

RAG_DIR    = "data/rag_store"
INDEX_PATH = os.path.join(RAG_DIR, "index.faiss")
META_PATH  = os.path.join(RAG_DIR, "metadata.json")
embedder   = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def add_to_rag(original_prompt, enhanced_prompt, theme, image_path):
    os.makedirs(RAG_DIR, exist_ok=True)
    if os.path.exists(INDEX_PATH):
        index = faiss.read_index(INDEX_PATH)
        with open(META_PATH) as f: metadata = json.load(f)
    else:
        index = faiss.IndexFlatL2(384)
        metadata = []
    index.add(np.array([embedder.encode([original_prompt])]))
    metadata.append({"original_prompt": original_prompt,
                     "enhanced_prompt": enhanced_prompt,
                     "theme": theme, "image_path": image_path,
                     "timestamp": datetime.now().isoformat()})
    faiss.write_index(index, INDEX_PATH)
    with open(META_PATH, "w") as f: json.dump(metadata, f, indent=2)

def get_rag_context_string(query_prompt, top_k=3):
    if not os.path.exists(INDEX_PATH): return ""
    index = faiss.read_index(INDEX_PATH)
    with open(META_PATH) as f: metadata = json.load(f)
    _, indices = index.search(
        np.array([embedder.encode([query_prompt])]), top_k)
    similar = [metadata[i]["original_prompt"] for i in indices if i < len(metadata)]
    return " | ".join(similar)

def get_generation_history():
    if not os.path.exists(META_PATH): return []
    with open(META_PATH) as f: return json.load(f)

Step 8 — Run the App
# (Optional) Start Mistral
ollama serve

# Launch app
streamlit run app.py

# Open browser
# http://localhost:8501
# → Create Account → Start generating! 🚀


🔐 Feature 1: User Authentication (New in v2.0)
Full signup / login / change-password system. SHA-256 hashed passwords stored locally in auth/users.json. Session managed via st.session_state. Per-user generation count shown in sidebar profile card.

🎨 Feature 2: Multi-Theme Generation
Select multiple themes — app generates one image per theme in a single click.

Available Themes (12):
🚫 None       🏔️ Realistic   🎬 Animated    🧚 Fairy Tale
🏛️ Ancient   🌴 Jungle      🚀 Futuristic   🤖 Cyberpunk
🐉 Fantasy   👻 Horror      🔮 Mystical     🖌️ Watercolor

Feature 3: Prompt Quality Analyzer
Real-time 0–100 score across 6 dimensions: Subject · Lighting · Style · Mood · Camera · Color

Prompt: "A cat"
Score: 17/100 — Weak 💡

Missing elements (click to add):
[💡 Lighting]  [📷 Camera]  [🎭 Mood]  [🎨 Color]  [🖌️ Style]

Feature 4: Negative Prompt Panel (New in v2.0)
Collapsible toggle with freeform input + 4 one-click presets:

blurry, ugly

text, watermark

distorted face

low quality, noise

📦 Feature 5: Batch Generation
Enter one prompt per line → generate all → download as a single ZIP file.

🌱 Feature 6: Seed Browser
Explore N random seeds side-by-side at draft quality. Click 🔒 Use Seed to lock a favourite for main generation.

🗂️ Feature 7: RAG Memory
Every generation embedded & stored in FAISS. Top-3 similar past prompts retrieved as style context. Consistency improves automatically across sessions.

8. Setup and Installation

# 1. Clone
git clone <repository-url>
cd ai-image-studio

# 2. Virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

# 3. Install packages
pip install -r requirements.txt

# 4. HuggingFace token
echo HF_TOKEN=hf_your_token > .env
# Accept FLUX license: https://huggingface.co/black-forest-labs/FLUX.1-schnell

# 5. (Optional) Mistral via Ollama
ollama pull mistral
ollama serve

# 6. Run
streamlit run app.py
# → http://localhost:8501 → Create Account → Generate!

9. How It Works
┌──────────────────────────────────────────────────────┐
│ STEP 0: Auth (New in v2.0)                           │
│  Visit app → Login or Create Account shown           │
│  Credentials validated → session started             │
│  Profile + gen count loaded into sidebar             │
└──────────────────────┬───────────────────────────────┘
                       ↓
┌──────────────────────────────────────────────────────┐
│ STEP 1: User Input                                   │
│  Type prompt → Quality Analyzer scores it live       │
│  Click suggestion chips to improve score             │
│  Select themes + size + quality                      │
│  (Optional) Add negative prompt                      │
│  Click 🚀 Generate                                   │
└──────────────────────┬───────────────────────────────┘
                       ↓
┌──────────────────────────────────────────────────────┐
│ STEP 2: RAG Retrieval                                │
│  Embed prompt via MiniLM → 384-dim vector            │
│  FAISS search → top-3 similar past prompts           │
│  Context string returned for generation              │
└──────────────────────┬───────────────────────────────┘
                       ↓
┌──────────────────────────────────────────────────────┐
│ STEP 3: Theme Loop (repeated per theme)              │
│  3A. Mistral enhances prompt (if ON)                 │
│  3B. Final = original + Mistral + theme + RAG        │
│  3C. POST to HuggingFace FLUX API → PNG received     │
│  3D. Save + update RAG store + increment gen count   │
└──────────────────────┬───────────────────────────────┘
                       ↓
┌──────────────────────────────────────────────────────┐
│ STEP 4: Display Results                              │
│  Grid: image · theme · seed · generation time        │
│  Individual download button per image                │
│  Gallery tab shows full history                      │
└──────────────────────────────────────────────────────┘


