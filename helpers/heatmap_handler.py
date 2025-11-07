import cv2
import numpy as np
import uuid
import shutil
import tempfile
from pathlib import Path
from typing import List, Dict, Any
from config import GENERATED_DIR

# Define a type alias for the data points for clarity
DataPoint = Dict[str, Any]


def draw_heatmap(data: List[DataPoint], map_path: Path) -> Dict[str, Any]:
    """
    Generates a signal strength heatmap image.

    This function takes signal data points (dBm), creates a heatmap overlay,
    and blends it with the base map image.
    """
    delete_heatmap()  # Clear any previously generated images
    img = create_img(map_path)  # Load the base map image

    # Generate the heatmap overlay using signal strength values
    # Signal (dBm) typically ranges from -90 (worst) to -30 (best)
    overlay = generate_heatmap("signal", -90, -30, data, img)

    # Create a unique filename for the generated image
    output_filename = f"{uuid.uuid4()}.jpg"
    output_path = GENERATED_DIR / output_filename

    # Save the final blended image to the 'generated' directory
    try:
        cv2.imwrite(str(output_path), overlay)
    except Exception as e:
        print(f"Error writing heatmap image: {e}")
        return {"error": "Failed to save heatmap image"}

    # Return the URL to the new image and the original data points
    # (data points are used by frontend JS for hover-tooltips)
    return {"url": f"/static/generated/{output_filename}",
            "points": data}


def channel_heatmap(data: List[DataPoint], map_path: Path) -> Dict[str, Any]:
    """
    Generates a channel congestion heatmap image.

    This function takes channel count data, creates a heatmap overlay,
    and blends it with the base map image.
    """
    delete_heatmap()  # Clear any previously generated images
    img = create_img(map_path)  # Load the base map image

    # Generate the heatmap overlay using channel counts
    # We'll map count values from 0 (min) to 20 (max congestion)
    overlay = generate_heatmap("count", 0, 20, data, img)

    # Create a unique filename for the generated image
    output_filename = f"{uuid.uuid4()}.jpg"
    output_path = GENERATED_DIR / output_filename

    # Save the final blended image to the 'generated' directory
    try:
        cv2.imwrite(str(output_path), overlay)
    except Exception as e:
        print(f"Error writing heatmap image: {e}")
        return {"error": "Failed to save heatmap image"}

    # Return the URL and data points, same as draw_heatmap
    return {"url": f"/static/generated/{output_filename}",
            "points": data}


def delete_heatmap():
    """
    Clears all files from the 'generated' directory.
    This prevents old heatmap images from accumulating.
    """
    for file in GENERATED_DIR.iterdir():
        try:
            file.unlink()
        except Exception as e:
            print(f"Error deleting old heatmap file {file}: {e}")


def create_img(map_path: Path) -> np.ndarray:
    """
    Loads an image from the specified path using OpenCV.

    Includes a workaround by copying to a temp file, which can help
    resolve issues with file paths containing special characters.
    """
    # Create a temporary file and copy the original image content to it
    # This helps cv2.imread handle complex file paths or permissions issues
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp_file:
        shutil.copy(map_path, tmp_file.name)
        tmp_path = tmp_file.name

    # Read the image from the temporary path
    img = cv2.imread(tmp_path)

    # Clean up the temporary file
    try:
        Path(tmp_path).unlink()
    except Exception as e:
        print(f"Error deleting temp image file {tmp_path}: {e}")

    if img is None:
        raise Exception(f"cv2.imread failed to load image: {map_path}")

    return img


def generate_heatmap(key: str, min_val: int, max_val: int, data: List[DataPoint], img: np.ndarray) -> np.ndarray:
    """
    Core heatmap generation logic using OpenCV.

    1. Creates a "mask" (a blank canvas) the size of the image.
    2. Draws circles on the mask for each data point, where the
       circle's intensity is based on the normalized data value.
    3. Blurs the mask to create a smooth gradient.
    4. Applies a color map (e.g., COLORMAP_TURBO) to the blurred mask.
    5. Blends the color heatmap with the original map image.
    """
    h, w = img.shape[:2]

    # 1. Create a floating-point mask for accumulating intensities
    mask = np.zeros((h, w), dtype=np.float32)

    # 2. Draw circles for each data point
    for point in data:
        x, y = int(point["x"]), int(point["y"])
        value = float(point[key])

        # Normalize the value to a 0.0 - 1.0 range
        norm_value = np.clip((value - min_val) / (max_val - min_val), 0, 1)

        # Convert normalized value to 0-255 intensity
        intensity = int(norm_value * 255)

        # Create a temporary mask for this single point
        circle_mask = np.zeros_like(mask)
        # Draw a filled circle with the calculated intensity
        cv2.circle(circle_mask, (x, y), 30, intensity, -1)

        # Add this circle to the main mask
        mask = cv2.add(mask, circle_mask)

    # Clip mask values to 0-255 and convert to 8-bit unsigned integer
    mask = np.clip(mask, 0, 255).astype(np.uint8)

    # 3. Blur the mask to create the smooth heatmap gradient
    # A large sigma value (e.g., 30) creates a wide, smooth blur
    blur = cv2.GaussianBlur(mask, (0, 0), sigmaX=30, sigmaY=30)

    # 4. Apply a color map to the blurred mask
    heatmap_color = cv2.applyColorMap(blur, cv2.COLORMAP_TURBO)

    # 5. Blend the heatmap with the original image
    alpha = 0.6  # 60% heatmap, 40% original image
    overlay = cv2.addWeighted(heatmap_color, alpha, img, 1 - alpha, 0)

    return overlay