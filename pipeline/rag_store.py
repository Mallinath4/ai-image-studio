import os
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from datetime import datetime

# ── Paths ─────────────────────────────────────────────────────────────────────
HISTORY_DIR = "history"
IMAGES_DIR  = os.path.join(HISTORY_DIR, "images")
INDEX_PATH  = os.path.join(HISTORY_DIR, "prompt_index.faiss")
META_PATH   = os.path.join(HISTORY_DIR, "metadata.json")

# Auto-create folders
os.makedirs(IMAGES_DIR, exist_ok=True)

# ── Embedder (loaded once) ────────────────────────────────────────────────────
_embedder = None

def get_embedder() -> SentenceTransformer:
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedder

# ── Index helpers ─────────────────────────────────────────────────────────────
def load_index():
    if os.path.exists(INDEX_PATH) and os.path.exists(META_PATH):
        index = faiss.read_index(INDEX_PATH)
        with open(META_PATH, "r") as f:
            metadata = json.load(f)
    else:
        index    = faiss.IndexFlatL2(384)  # MiniLM dim = 384
        metadata = []
    return index, metadata

def save_index(index, metadata):
    faiss.write_index(index, INDEX_PATH)
    with open(META_PATH, "w") as f:
        json.dump(metadata, f, indent=2)

# ── Core RAG functions ────────────────────────────────────────────────────────

def add_to_rag(original_prompt: str, enhanced_prompt: str,
               theme: str, image_path: str):
    """Save a completed generation into the RAG FAISS store."""
    embedder         = get_embedder()
    index, metadata  = load_index()

    vec = embedder.encode([original_prompt], normalize_embeddings=True)
    index.add(np.array(vec, dtype="float32"))

    metadata.append({
        "original_prompt":  original_prompt,
        "enhanced_prompt":  enhanced_prompt,
        "theme":            theme,
        "image_path":       image_path,
        "timestamp":        datetime.now().isoformat()
    })

    save_index(index, metadata)


def retrieve_similar(query: str, top_k: int = 2) -> list:
    """Retrieve top_k most similar past generations."""
    embedder         = get_embedder()
    index, metadata  = load_index()

    if index.ntotal == 0:
        return []

    vec = embedder.encode([query], normalize_embeddings=True)
    distances, indices = index.search(
        np.array(vec, dtype="float32"),
        min(top_k, index.ntotal)
    )

    results = []
    for idx in indices[0]:
        if 0 <= idx < len(metadata):
            results.append(metadata[idx])
    return results


def get_rag_context_string(query: str) -> str:
    """Return a formatted context string from similar past prompts."""
    similar = retrieve_similar(query, top_k=2)
    if not similar:
        return ""

    parts = []
    for item in similar:
        parts.append(
            f"- Theme: {item['theme']} | "
            f"Past prompt: {item['enhanced_prompt'][:120]}..."
        )
    return "\n".join(parts)


def get_generation_history() -> list:
    """Return full generation history, newest first."""
    _, metadata = load_index()
    return list(reversed(metadata))
