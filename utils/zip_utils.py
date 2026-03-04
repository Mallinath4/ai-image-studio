import zipfile
import json
from io import BytesIO
from pathlib import Path


def create_images_zip(result_list):
    """
    result_list: list of dicts with keys 'path', 'theme', 'seed'
    Returns bytes of a ZIP file
    """
    buf = BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for item in result_list:
            p = item.get("path", "")
            if p and Path(p).exists():
                zf.write(p, Path(p).name)

        # include a small manifest
        manifest = [
            {"file": Path(i["path"]).name,
             "theme": i.get("theme"),
             "seed":  i.get("seed")}
            for i in result_list if i.get("path") and Path(i["path"]).exists()
        ]
        zf.writestr("manifest.json", json.dumps(manifest, indent=2))

    return buf.getvalue()
