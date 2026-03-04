import io
import os
import random
import requests
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

# ── Your HuggingFace Token ────────────────────────────────────────────────────
HF_TOKEN = os.getenv("HF_TOKEN", "hf_xxxxxxxxxxxxxxxxxxxxxxxx")

# ── ✅ NEW correct API URL ─────────────────────────────────────────────────────
API_URL = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"

HEADERS = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}


def load_flux_pipeline():
    """No local download — HF runs FLUX.1-schnell on their servers."""
    return True


def generate_image(
    prompt: str,
    width: int = 768,
    height: int = 768,
    quality: str = "high",
    seed: int = -1
) -> tuple[Image.Image, int]:
    """
    Generate image using HuggingFace Router API.
    Exact FLUX.1-schnell model — 0GB on your machine.
    """
    if seed == -1:
        seed = random.randint(0, 2**32 - 1)

    # Safe dimension clamp
    width  = max(256, min(1024, (width  // 16) * 16))
    height = max(256, min(1024, (height // 16) * 16))

    # Quality → steps
    steps_map = {"draft": 1, "standard": 3, "high": 4}
    steps = steps_map.get(quality, 4)

    payload = {
        "inputs": prompt,
        "parameters": {
            "width":               width,
            "height":              height,
            "num_inference_steps": steps,
            "guidance_scale":      0.0,
            "seed":                seed
        }
    }

    try:
        response = requests.post(
            API_URL,
            headers=HEADERS,
            json=payload,
            timeout=120
        )

        if response.status_code == 200:
            image = Image.open(io.BytesIO(response.content)).convert("RGB")
            return image, seed

        elif response.status_code == 503:
            wait = 20
            try:
                wait = response.json().get("estimated_time", 20)
            except:
                pass
            raise Exception(
                f"⏳ Model loading on HF server. Wait ~{int(wait)}s and try again."
            )

        elif response.status_code == 401:
            raise Exception(
                "🔑 Invalid HuggingFace token. Check your HF_TOKEN in .env file."
            )

        elif response.status_code == 403:
            raise Exception(
                "🔒 Access denied. Visit:\n"
                "https://huggingface.co/black-forest-labs/FLUX.1-schnell\n"
                "and click 'Agree and access' to accept the license."
            )

        elif response.status_code == 429:
            raise Exception(
                "⚠️ Rate limit reached. Wait a few minutes and try again."
            )

        else:
            raise Exception(
                f"API Error {response.status_code}: {response.text[:300]}"
            )

    except requests.exceptions.Timeout:
        raise Exception("⏱️ Request timed out. HF server is busy — try again.")

    except requests.exceptions.ConnectionError:
        raise Exception("🌐 No internet connection. Check your network.")
