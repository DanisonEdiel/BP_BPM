from fastapi import APIRouter, File, UploadFile, Query
from fastapi.responses import JSONResponse
from services.ocr_service import procesar_archivo_ocr
from services.gemini_service import extraer_campos_desde_ocr
from config.settings import ARCHIVO_BASE_URL
import traceback
import aiohttp
import io

router = APIRouter()

@router.post("/ocr-y-analiza/")
async def ocr_y_analiza(file: UploadFile = File(...), content_type: str = None):
    try:
        contents = await file.read()
        # Si content_type no viene como parámetro, tomar del archivo (o cadena vacía)
        ct = content_type or file.content_type or ""
        texto_limpio = procesar_archivo_ocr(contents, ct)
        resultado = extraer_campos_desde_ocr(texto_limpio)

        return resultado
    except Exception as e:
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e)})


@router.get("/ocr-desde-nombre/")
async def ocr_desde_nombre(nombreArchivo: str = Query(...)):
    try:
        file_url = f"{ARCHIVO_BASE_URL}{nombreArchivo}"

        async with aiohttp.ClientSession() as session:
            async with session.get(file_url) as resp:
                if resp.status != 200:
                    return JSONResponse(status_code=resp.status, content={"error": "Error descargando archivo"})
                content_type = resp.headers.get("Content-Type", "")
                content = await resp.read()

        file_like = UploadFile(filename=nombreArchivo, file=io.BytesIO(content))

        # Aquí pasamos explícitamente el content_type al endpoint POST
        return await ocr_y_analiza(file_like, content_type=content_type)

    except Exception as e:
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e)})
