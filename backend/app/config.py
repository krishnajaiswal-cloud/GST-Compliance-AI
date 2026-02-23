import os
from pathlib import Path
from dotenv import load_dotenv
import pytesseract

load_dotenv()

# 🔹 Base directory
BASE_DIR = Path(__file__).resolve().parent

# 🔹 Directories
UPLOAD_DIR = BASE_DIR / "data" / "uploads"
EXCEL_DIR = BASE_DIR / "data" / "excel"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
EXCEL_DIR.mkdir(parents=True, exist_ok=True)

# 🔹 Gemini API Key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# 🔹 Tesseract Configuration
# Only set Windows path locally
if os.name == "nt":  # Windows
    pytesseract.pytesseract.tesseract_cmd = (
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )