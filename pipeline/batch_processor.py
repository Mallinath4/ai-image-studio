import time
import pandas as pd
from pathlib import Path
from datetime import datetime


def validate_csv(df):
    """Returns (is_valid, error_message)"""
    if "prompt" not in df.columns:
        return False, "CSV must have a 'prompt' column."
    if df["prompt"].isnull().any():
        return False, "Some prompts are empty. Please fix the CSV."
    return True, ""


def process_batch(df, enhance_fn, generate_fn, save_fn, add_rag_fn,
                  default_theme="Realistic", default_quality="high",
                  progress_callback=None):
    """
    df columns: prompt (required), theme (optional), width (optional), height (optional)
    Returns list of result dicts
    """
    results = []
    total = len(df)

    for idx, row in df.iterrows():
        try:
            prompt      = str(row["prompt"]).strip()
            theme       = str(row.get("theme",  default_theme))
            width       = int(row.get("width",  768))
            height      = int(row.get("height", 768))

            enhanced    = enhance_fn(prompt, "")
            final_p     = enhanced["enhanced_prompt"]

            t0          = time.time()
            image, seed = generate_fn(final_p, width, height, default_quality, -1)
            elapsed     = round(time.time() - t0, 1)

            path        = save_fn(image, final_p, seed, theme)
            add_rag_fn(prompt, final_p, theme, path)

            results.append({
                "index":   idx,
                "prompt":  prompt,
                "theme":   theme,
                "seed":    seed,
                "time_s":  elapsed,
                "path":    path,
                "status":  "success"
            })
        except Exception as e:
            results.append({
                "index":  idx,
                "prompt": str(row.get("prompt", "")),
                "status": "failed",
                "error":  str(e)
            })

        if progress_callback:
            progress_callback(idx + 1, total)

        time.sleep(1.5)  # gentle rate-limit

    return results
