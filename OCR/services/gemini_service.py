from config.settings import GEMINI_API_KEY, GEMINI_MODEL
from google import generativeai as genai
from google.generativeai import types
import json

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel(
    model_name=GEMINI_MODEL,
    system_instruction=(
        "Responde solo en JSON estructurado. No uses markdown. "
        "Solo JSON plano. No incluyas explicaciones fuera del JSON."
    )
)

def extraer_campos_desde_ocr(texto_limpio: str) -> dict:
    prompt = f"""
Eres un asistente experto en procesamiento OCR.

Del siguiente texto extrae los siguientes campos con estos formatos:

- nombre completo (texto con espacios normales)
- cedula_ruc (solo números)
- fecha (formato DD/MM/AAAA)
- correo electrónico válido
- dirección (texto)
- teléfono con prefijo internacional (ejemplo +593998717258)
- descripción concatenada de los productos o servicios
- número de factura tal cual aparece
- monto total (número decimal con punto)

Si algún campo no aparece, pon null.

Texto OCR:
'''{texto_limpio}'''

Devuelve SOLO un JSON plano con la estructura:

{{
  "nombre": "...",
  "cedula_ruc": "...",
  "fecha": "...",
  "correo": "...",
  "direccion": "...",
  "telefono": "...",
  "descripcion": "...",
  "numero_factura": "...",
  "monto_total": "..."
}}
"""
    response = model.generate_content(
        prompt,
        generation_config=types.GenerationConfig(temperature=0.2)
    )

    raw = response.candidates[0].content.parts[0].text.strip()

    try:
        resultado = json.loads(raw)
        return {k: v.strip() if isinstance(v, str) else v for k, v in resultado.items()}
    except:
        return {"error": "No se pudo parsear JSON del modelo", "raw_response": raw}
