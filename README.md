# WiFi Heatmap Generator

This is a standalone web application built with FastAPI to conduct nomadic Wi-Fi coverage surveys. It allows users to upload a floor plan, perform Wi-Fi scans (signal strength and channel congestion) at different points, and visualize the results as a dynamic heatmap.

The tool is designed to be compiled into a single executable for easy distribution on both Windows and Linux.

## Features

* **Plan Management:** Upload floor plans in PNG, JPG, or PDF format.
* **Wi-Fi Scanning:** Perform active scans to capture signal strength (dBm) and channel usage.
* **Dual-Mode Heatmaps:** Visualize both **Signal Strength** (SSID-specific) and **Channel Congestion**.
* **Dynamic Visualization:** Heatmaps are generated on the backend with OpenCV (`cv2`) and include interactive tooltips on the frontend.
* **Cross-Platform:** Works on Windows (using `pywifi` + `netsh`) and Linux (using `iw`).
* **I18n Support:** Full internationalization for English and French.
* **Data Import/Export:** Save and load scan sessions as `.json` files.

## Tech Stack

* **Backend:** FastAPI, Uvicorn
* **Scanning:** `pywifi` & `netsh` (Windows), `iw` (Linux)
* **Image Processing:** `opencv-python`, `numpy`, `pdf2image`
* **Templating:** Jinja2
* **Frontend:** Vanilla JavaScript (Fetch API)
* **Packaging:** Nuitka

## Project Structure

```
.
├── helpers/        \# Core logic (scan, data, heatmap, file handling)
├── languages/      \# i18n JSON files for UI text
├── routers/        \# FastAPI endpoints (API definition)
├── static/         \# CSS, JS, and user-generated data (ignored by git)
│   ├── data/       \# Scan data (.json)
│   ├── font/       \# Help documentation images
│   ├── generated/  \# Generated heatmap images
│   └── maps/       \# User-uploaded floor plans
├── templates/      \# Jinja2 HTML templates
├── build\_app.ps1   \# Nuitka build script
├── config.py       \# Configuration, paths, and OS detection
├── main.py         \# Main FastAPI application entry point
└── requirements.txt
```

## Developer Setup

### 1. Prerequisites

* Python 3.9+
* `pip` and `venv`
* **For PDF conversion:** [Poppler](https://github.com/oschwartz10612/poppler-windows/releases/) (must be added to your system's PATH).

### 2. Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd heatmaps_windows

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# Windows
.\venv\Scripts\Activate.ps1
# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3\. Running the App (Development)

```bash
python main.py
```

The application will be available at `http://127.0.0.1:8000`.

### 4\. Building the Executable

Run the PowerShell build script:

```powershell
.\build_app.ps1
```

This will create a `build/main.dist/` directory containing the standalone `main.exe` and all its dependencies.

## Key Architecture Notes

### Windows Scan "Hack"

On Windows, `netsh` provides full scan data (including channels) but its cache only updates every \~15 seconds. `pywifi` can trigger an active scan instantly but does *not* provide channel information.

This app combines them:

1.  `WIFI_INTERFACE.scan()` (from `pywifi`) is called to *trigger* a system-level scan.
2.  The code `time.sleep(3)` waits 3 seconds.
3.  `wifi_scan_netsh()` is called to read the system's *now-fresh* cache, which contains all the data (including channels).

### Regex Language Dependency

The `netsh` output is language-dependent. The parser in `helpers/scan_handler.py` uses bilingual regex (e.g., `^(?:Band|Bande)`) to support both English and French Windows installations.


---
