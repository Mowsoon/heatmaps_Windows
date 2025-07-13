import cv2
import numpy as np
import uuid
import shutil
import tempfile


from pathlib import Path
from config import GENERATED_DIR

def draw_heatmap(data, map_path: Path):
    delete_heatmap()
    img = create_img(map_path)

    overlay = generate_heatmap("signal", -90, -30, data, img)

    output_filename = f"{uuid.uuid4()}.jpg"
    output_path = GENERATED_DIR / output_filename
    cv2.imwrite(str(output_path), overlay)

    return {"url": f"/static/generated/{output_filename}",
            "points": data}


def channel_heatmap(data, map_path: Path):
    delete_heatmap()
    img = create_img(map_path)

    overlay = generate_heatmap("count", 0, 20, data, img)

    output_filename = f"{uuid.uuid4()}.jpg"
    output_path = GENERATED_DIR / output_filename
    cv2.imwrite(str(output_path), overlay)

    return {"url": f"/static/generated/{output_filename}",
            "points": data}
def delete_heatmap():
    for file in GENERATED_DIR.iterdir():
        file.unlink()

def create_img(map_path: Path):
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp_file:
        shutil.copy(map_path, tmp_file.name)
        tmp_path = tmp_file.name

    img = cv2.imread(tmp_path)
    if img is None:
        raise Exception(f"cv2.imread failed even after sanitizing: {tmp_path}")
    return img

def generate_heatmap(key: str, min: int, max: int, data, img, ):
    h, w = img.shape[:2]
    mask = np.zeros((h, w), dtype=np.float32)
    for point in data:
        x, y = int(point["x"]), int(point["y"])
        value = float(point[key])
        norm_value = np.clip((value - min) / (max - min), 0, 1)
        intensity = int(norm_value * 255)
        circle_mask = np.zeros_like(mask)
        cv2.circle(circle_mask, (x, y), 30, intensity, -1)
        mask = cv2.add(mask, circle_mask)

    mask = np.clip(mask, 0, 255).astype(np.uint8)

    blur = cv2.GaussianBlur(mask, (0, 0), sigmaX=30, sigmaY=30)
    heatmap_color = cv2.applyColorMap(blur, cv2.COLORMAP_TURBO)

    alpha = 0.6
    overlay = cv2.addWeighted(heatmap_color, alpha, img, 1 - alpha, 0)

    return overlay