from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pyzeebe import ZeebeClient, create_camunda_cloud_channel
from dotenv import load_dotenv
from models import SolicitudReembolso
import os
import json
import asyncio
import logging
from uuid import uuid4
from datetime import datetime
import signal

# Configurar logging básico
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar variables de entorno desde .env
load_dotenv()

# Obtener credenciales de Camunda Cloud
CAMUNDA_CLIENT_ID = os.getenv("CAMUNDA_CLIENT_ID")
CAMUNDA_CLIENT_SECRET = os.getenv("CAMUNDA_CLIENT_SECRET")
CAMUNDA_CLUSTER_ID = os.getenv("CAMUNDA_CLUSTER_ID")
CAMUNDA_REGION = os.getenv("CAMUNDA_REGION", "lhr-1")

# Validar credenciales
if not all([CAMUNDA_CLIENT_ID, CAMUNDA_CLIENT_SECRET, CAMUNDA_CLUSTER_ID]):
    logger.error("Faltan credenciales de Camunda Cloud. Verifica las variables de entorno.")
    raise ValueError("Faltan credenciales de Camunda Cloud. Verifica las variables de entorno.")

# Crear canal de conexión a Camunda Cloud
logger.info(f"Conectando a Camunda Cloud SaaS en la región {CAMUNDA_REGION}")
channel = create_camunda_cloud_channel(
    client_id=CAMUNDA_CLIENT_ID,
    client_secret=CAMUNDA_CLIENT_SECRET,
    cluster_id=CAMUNDA_CLUSTER_ID,
    region=CAMUNDA_REGION
)

# Crear cliente Zeebe
zeebe_client = ZeebeClient(channel)
logger.info("Cliente Zeebe para Camunda Cloud creado correctamente")

# Inicializar aplicación FastAPI
app = FastAPI()

# Middleware CORS (para desarrollo permite todos los orígenes, en producción restringir)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambiar a lista de dominios permitidos en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/reembolso")
async def enviar_reembolso(
    solicitud: str = Form(...),
    archivo: UploadFile = File(...)
):
    try:
        logger.info("Recibida solicitud de reembolso")

        # Convertir string JSON a dict
        try:
            data = json.loads(solicitud)
        except json.JSONDecodeError:
            logger.warning("Solicitud no es un JSON válido")
            raise HTTPException(status_code=422, detail="❌ La solicitud no es un JSON válido.")

        # Validar con Pydantic
        try:
            solicitud_obj = SolicitudReembolso(**data)
        except Exception as e:
            logger.warning(f"Validación fallida: {str(e)}")
            raise HTTPException(status_code=422, detail=f"❌ Validación fallida: {str(e)}")

        # Guardar archivo localmente con nombre único + timestamp
        os.makedirs("archivos", exist_ok=True)
        extension = os.path.splitext(archivo.filename)[1]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_unico = f"{uuid4().hex}_{timestamp}{extension}"
        archivo_path = os.path.join("archivos", nombre_unico)

        with open(archivo_path, "wb") as f:
            contenido = await archivo.read()
            f.write(contenido)
        logger.info(f"Archivo guardado en {archivo_path}")

        # Preparar variables para Zeebe
        variables = solicitud_obj.dict(by_alias=True)
        variables["archivoNombre"] = nombre_unico
        logger.info(f"Variables para Zeebe: {variables}")

        # Ejecutar proceso en Zeebe con timeout
        try:
            await asyncio.wait_for(
                zeebe_client.run_process(
                    bpmn_process_id="Process_1bag78u",
                    variables=variables
                ),
                timeout=15  # segundos
            )
            logger.info("Proceso enviado a Zeebe con éxito")
        except asyncio.TimeoutError:
            logger.error("Timeout al conectar con Zeebe")
            raise HTTPException(status_code=504, detail="Timeout al conectar con Zeebe")
        except Exception as e:
            logger.error(f"Error al enviar proceso a Zeebe: {e}")
            raise HTTPException(status_code=500, detail=f"Error al enviar proceso a Zeebe: {e}")

        return JSONResponse(
            status_code=200,
            content={
                "mensaje": "✅ Reembolso enviado correctamente a Camunda Cloud SaaS.",
                "archivoGuardado": nombre_unico
            }
        )

    except HTTPException as he:
        raise he

    except Exception as e:
        logger.error(f"Error inesperado en servidor: {e}")
        raise HTTPException(status_code=500, detail=f"⚠️ Error inesperado del servidor: {str(e)}")

# Endpoint para descargar archivo PDF
@app.get("/archivo/{nombre_archivo}")
async def descargar_archivo(nombre_archivo: str):
    archivo_path = os.path.join("archivos", nombre_archivo)

    if not os.path.isfile(archivo_path):
        raise HTTPException(status_code=404, detail="Archivo no encontrado.")

    return FileResponse(
        archivo_path,
        media_type="application/pdf",
        filename=nombre_archivo
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)