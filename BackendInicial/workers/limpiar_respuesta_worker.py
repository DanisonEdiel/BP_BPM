import os
import logging
import asyncio
from pyzeebe import ZeebeWorker, create_insecure_channel
from dotenv import load_dotenv

# Configuración básica
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# Datos de conexión
ZEEBE_HOST = os.getenv("ZEEBE_HOST", "localhost").strip()
ZEEBE_PORT = int(os.getenv("ZEEBE_PORT", "26500").strip())

channel = create_insecure_channel(f"{ZEEBE_HOST}:{ZEEBE_PORT}")
worker = ZeebeWorker(channel)

# Worker para limpiar la respuesta antes del formulario
@worker.task(task_type="reembolso.limpiar_respuesta")
def limpiar_respuesta_llm(**variables):
    logger.info("🧹 Limpiando respuesta LLM")
    logger.debug(f"Variables recibidas: {variables}")

    # Función para formatear listas como texto con viñetas
    def lista_a_texto(lista):
        if isinstance(lista, list):
            return "\n".join([f"• {item}" for item in lista])
        return ""

    # Transformaciones
    cumple = "Sí" if variables.get("cumplePoliticas", False) else "No"
    observaciones = lista_a_texto(variables.get("observaciones", []))
    recomendaciones = lista_a_texto(variables.get("recomendaciones", []))
    respuesta_natural = variables.get("respuestaNaturalV", "")

    # Resultado para el User Task
    variables_actualizadas = {
        "cumplePoliticas": cumple,
        "observaciones": observaciones,
        "recomendaciones": recomendaciones,
        "respuestaNaturalV": respuesta_natural
    }

    logger.info("✅ Variables listas para el formulario")
    logger.debug(variables_actualizadas)
    return variables_actualizadas

# Main async
async def main():
    logger.info("🚀 Iniciando worker 'reembolso.limpiar_respuesta'")
    await worker.work()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
