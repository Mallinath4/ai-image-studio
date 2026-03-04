import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"

SYSTEM_INSTRUCTION = """You are an expert AI art director and prompt engineer for FLUX.1-schnell image model.

When given a user prompt and style theme, you MUST:
1. Think carefully about composition, lighting, mood, color palette
2. Craft a rich, detailed image generation prompt
3. Suggest what to avoid as a negative prompt

Respond ONLY with valid JSON in this exact format:
{
  "enhanced_prompt": "detailed image generation prompt here",
  "thinking": "your brief artistic reasoning (2 sentences)",
  "negative_prompt": "things to avoid e.g. blurry, low quality, watermark"
}
"""

def enhance_prompt(user_prompt: str, theme_suffix: str = "") -> dict:
    """
    Call Ollama/Mistral locally to enhance and think about the user prompt.
    Returns dict with enhanced_prompt, thinking, negative_prompt.
    Falls back gracefully if Ollama is not running.
    """
    combined = f"User prompt: {user_prompt}"
    if theme_suffix:
        combined += f"\nDesired theme/style: {theme_suffix}"
    combined += "\n\nOutput JSON only:"

    payload = {
        "model": "mistral",
        "prompt": f"{SYSTEM_INSTRUCTION}\n\n{combined}",
        "stream": False
    }

    try:
        resp = requests.post(OLLAMA_URL, json=payload, timeout=90)
        resp.raise_for_status()
        raw = resp.json().get("response", "").strip()

        # Extract JSON block if wrapped in markdown
        if "```json" in raw:
            raw = raw.split("```json").split("```").strip()[1]
        elif "```" in raw:
            raw = raw.split("```").split("```")[0].strip()

        result = json.loads(raw)
        return {
            "enhanced_prompt": result.get("enhanced_prompt", user_prompt),
            "thinking": result.get("thinking", ""),
            "negative_prompt": result.get("negative_prompt", "blurry, low quality, watermark")
        }

    except Exception as e:
        # Graceful fallback — no crash, just use plain prompt
        suffix = f", {theme_suffix}" if theme_suffix else ""
        return {
            "enhanced_prompt": f"{user_prompt}{suffix}, ultra detailed, 8k, perfect lighting, masterpiece",
            "thinking": f"Ollama unavailable ({str(e)[:60]}). Using basic enhancement.",
            "negative_prompt": "blurry, low quality, watermark, distorted, ugly"
        }
