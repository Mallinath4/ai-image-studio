import json
import os
from pathlib import Path
from datetime import datetime

LIBRARY_PATH = "data/prompt_library.json"

def save_to_library(prompt, tags=None, category="General"):
    os.makedirs("data", exist_ok=True)
    library = load_library()
    library.append({
        "prompt": prompt,
        "tags": tags or [],
        "category": category,
        "created_at": datetime.now().isoformat()
    })
    with open(LIBRARY_PATH, "w") as f:
        json.dump(library, f, indent=2)

def load_library():
    if Path(LIBRARY_PATH).exists():
        with open(LIBRARY_PATH, "r") as f:
            return json.load(f)
    return []

def search_library(query):
    library = load_library()
    q = query.lower()
    return [
        item for item in library
        if q in item["prompt"].lower()
        or any(q in tag.lower() for tag in item.get("tags", []))
        or q in item.get("category", "").lower()
    ]

def delete_from_library(index):
    library = load_library()
    if 0 <= index < len(library):
        library.pop(index)
        with open(LIBRARY_PATH, "w") as f:
            json.dump(library, f, indent=2)
