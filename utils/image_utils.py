import io
import os
from PIL import Image, PngImagePlugin
from datetime import datetime

IMAGES_DIR = "history/images"
os.makedirs(IMAGES_DIR, exist_ok=True)


def save_image(image: Image.Image, prompt: str,
               seed: int, theme: str) -> str:
    """Save image to disk with embedded PNG metadata. Returns filepath."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename  = f"flux_{theme.lower()}_{timestamp}_s{seed}.png"
    filepath  = os.path.join(IMAGES_DIR, filename)

    meta = PngImagePlugin.PngInfo()
    meta.add_text("prompt", prompt)
    meta.add_text("seed", str(seed))
    meta.add_text("theme", theme)
    meta.add_text("model", "FLUX.1-schnell")
    meta.add_text("generated_at", timestamp)

    image.save(filepath, "PNG", pnginfo=meta)
    return filepath


def image_to_bytes(image: Image.Image) -> bytes:
    """Convert PIL image to PNG bytes for Streamlit download."""
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    return buf.getvalue()


def get_download_filename(theme: str, seed: int) -> str:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"flux_{theme.lower()}_{ts}_seed{seed}.png"
