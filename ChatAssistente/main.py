from fastapi import FastAPI, Request
from google import generativeai as genai
from google.generativeai import types
from dotenv import load_dotenv
import os
import json

load_dotenv()

# Configura la API key de Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = FastAPI()
model_name = "gemini-2.5-flash"

# Define el modelo con instrucciones del sistema
model = genai.GenerativeModel(
    model_name=model_name,
    system_instruction="Responde solo en JSON estructurado. No uses markdown. Solo JSON plano. No incluyas explicaciones fuera del JSON."
)

@app.post("/verificar-politicas")
async def verificar_politicas(request: Request):
    data = await request.json()

    # Construcción del prompt
    prompt = f"""
Eres un asistente financiero especializado en validar políticas contables. Evalúa si la siguiente solicitud de gasto cumple con las políticas contables de la empresa. No decides si el gasto es aprobado o rechazado, solo validas su conformidad.

Responde exclusivamente en JSON plano con los siguientes campos:

- cumplePoliticas (true o false): indica si el gasto cumple o no con las políticas.
- observaciones (lista de texto): hallazgos, posibles incumplimientos o advertencias.
- recomendaciones (lista de texto): sugerencias para cumplir mejor las políticas.
- respuestaNatural (texto): explicación comprensible para el solicitante.

Datos recibidos:
Nombre: {data['nombre']}
Monto: {data['monto']}
Tipo de gasto: {data['tipoGasto']}
Medio de pago: {data['medioPago']}
Fecha: {data['fechaGasto']}
Empleado registrado: {data.get('empleadoEncontrado', False)}
Documento válido: {data.get('docvalidate', False)}
Descripción: {data.get('descripcion', '')}
    """

    # Generación de respuesta
    response = model.generate_content(
        prompt,
        generation_config=types.GenerationConfig(
            temperature=0.2
        )
    )

    # Extraer y parsear JSON plano
    raw_output = response.candidates[0].content.parts[0].text.strip()
    parsed = json.loads(raw_output)

    return parsed
