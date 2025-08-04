from pdf2image import convert_from_bytes
from PIL import Image
import pytesseract
import io
from config.settings import TESSERACT_CMD, POPPLE_PATH
from utils.helpers import limpiar_texto_ocr

pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

def procesar_archivo_ocr(content: bytes, content_type: str) -> str:
    if content_type == "application/pdf":
        images = convert_from_bytes(content, poppler_path=POPPLE_PATH)
        full_text = ""
        for idx, image in enumerate(images, 1):
            full_text += f"\n\n--- Página {idx} ---\n\n" + pytesseract.image_to_string(image)
        return limpiar_texto_ocr(full_text)

    elif content_type.startswith("image/"):
        image = Image.open(io.BytesIO(content))
        raw_text = pytesseract.image_to_string(image)
        return limpiar_texto_ocr(raw_text)

    else:
        raise ValueError("Formato de archivo no soportado (debe ser PDF o imagen)")
