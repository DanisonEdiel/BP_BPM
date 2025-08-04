import os
from dotenv import load_dotenv

load_dotenv()  # Carga las variables desde .env

# Configuración global
TESSERACT_CMD = os.getenv("TESSERACT_CMD")
POPPLE_PATH = os.getenv("POPPLE_PATH")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
ARCHIVO_BASE_URL = os.getenv("ARCHIVO_BASE_URL", "http://localhost:8000/archivo/")
