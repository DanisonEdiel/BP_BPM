import os
import logging
import asyncio
import re
from datetime import datetime
from pyzeebe import ZeebeWorker, create_insecure_channel
from dotenv import load_dotenv

# Configuración básica del logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar variables de entorno desde .env
load_dotenv()

# Obtener datos de conexión con valores por defecto y limpiar espacios
ZEEBE_HOST = os.getenv("ZEEBE_HOST", "localhost").strip()
ZEEBE_PORT = int(os.getenv("ZEEBE_PORT", "26500").strip())

# Crear canal de conexión inseguro a Zeebe
channel = create_insecure_channel(f"{ZEEBE_HOST}:{ZEEBE_PORT}")
worker = ZeebeWorker(channel)


def safe_str(value):
    """
    Convierte el valor a string en minúsculas y sin espacios
    si es cadena, sino devuelve cadena vacía.
    """
    if isinstance(value, str):
        return value.strip().lower()
    return ""


def comparar_fechas(f1, f2):
    """
    Compara dos fechas con formatos posibles: dd/mm/yyyy y yyyy-mm-dd.
    """
    formatos = ["%d/%m/%Y", "%Y-%m-%d"]

    def parse_fecha(fecha_str):
        if not fecha_str:
            return None
        for fmt in formatos:
            try:
                return datetime.strptime(fecha_str, fmt)
            except Exception:
                continue
        return None

    dt1 = parse_fecha(f1)
    dt2 = parse_fecha(f2)
    return dt1 == dt2 if dt1 and dt2 else False


def normalizar_telefono(tel):
    """
    Normaliza un número telefónico eliminando todo lo que no sea dígito,
    comparando solo los últimos 9 dígitos relevantes.
    """
    if not tel:
        return ""
    numeros = re.sub(r"\D", "", tel)
    return numeros[-9:]  # Ecuador: últimos 9 dígitos


@worker.task(task_type="comparacion-duplicidad")
def comparar_duplicidad(**variables):
    """
    Worker para comparar datos extraídos OCR vs datos originales
    y validar duplicidad o discrepancia.
    """
    logger.info("🔍 Ejecutando worker comparacion-duplicidad")
    logger.debug(f"Variables recibidas: {variables}")

    # Variables extraídas OCR
    nombreDoc = safe_str(variables.get("nombreDoc"))
    cedulaDoc = safe_str(variables.get("cedulaDoc"))
    fechaDoc = safe_str(variables.get("fechaDoc"))
    correoDoc = safe_str(variables.get("correoDoc"))
    telefonoDoc = variables.get("telefonoDoc")
    facturaNDoc = safe_str(variables.get("facturaNDoc"))
    montoDoc = float(variables.get("montoDoc", 0))

    # Variables originales
    nombre = safe_str(variables.get("nombre"))
    cedula = safe_str(variables.get("cedula"))
    fechaGasto = safe_str(variables.get("fechaGasto"))
    correo = safe_str(variables.get("correo"))
    telefono = variables.get("telefono")
    numeroFactura = safe_str(variables.get("numeroFactura"))
    monto = float(variables.get("monto", 0))

    # Comparaciones
    resultado = {
        "nombreCoincide": nombreDoc == nombre,
        "cedulaCoincide": cedulaDoc == cedula,
        "fechaCoincide": comparar_fechas(fechaDoc, fechaGasto),
        "correoCoincide": correoDoc == correo,
        "direccionCoincide": True,  # No se compara dirección
        "telefonoCoincide": normalizar_telefono(telefonoDoc) == normalizar_telefono(telefono),
        "facturaCoincide": facturaNDoc == numeroFactura,
        "montoCoincide": montoDoc == monto
    }

    # Validar si todos coinciden (True si todo coincide)
    docvalidate = all(resultado.values())

    logger.info(f"Resultado comparación: {resultado}, docvalidate={docvalidate}")

    # Retornar variables para el proceso BPM
    return {
        "docvalidate": docvalidate,
        **resultado
    }


async def main():
    logger.info("🚀 Iniciando worker 'comparacion-duplicidad'")
    await worker.work()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
