import os
import logging
import asyncio
from pyzeebe import ZeebeWorker, ZeebeClient, create_insecure_channel
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("reembolso.notificacion2")

# Cargar variables del entorno
load_dotenv()
ZEEBE_HOST = os.getenv("ZEEBE_HOST", "localhost").strip()
ZEEBE_PORT = int(os.getenv("ZEEBE_PORT", "26500").strip())

# Nombre del mensaje en BPMN (debe coincidir con <bpmn:message name="NotificacionSegundaEtapa">)
ZEEBE_MESSAGE_NAME = "NotificacionSegundaEtapa"

# Función para enviar mensaje a Zeebe
async def enviar_mensaje(client: ZeebeClient, correlation_key: str, variables: dict = None):
    """
    Envía un mensaje al broker Zeebe para correlacionar con un Catch Event.
    """
    await client.publish_message(
        name=ZEEBE_MESSAGE_NAME,
        correlation_key=correlation_key,
        variables=variables or {}
    )
    logger.info(f"📨 Mensaje '{ZEEBE_MESSAGE_NAME}' enviado con correlationKey: {correlation_key}")

# Función principal que contiene el worker y el cliente Zeebe
async def main():
    # Crear canal inseguro (solo desarrollo/local)
    channel = create_insecure_channel(f"{ZEEBE_HOST}:{ZEEBE_PORT}")
    worker = ZeebeWorker(channel)
    client = ZeebeClient(channel)

    @worker.task(task_type="reembolso.notificacion2")
    async def notificar_segunda(**variables):
        """
        Worker encargado de manejar la tarea 'reembolso.notificacion2'.
        Envía un mensaje al catch event de la segunda etapa.
        """
        logger.info("📥 Trabajo recibido en 'reembolso.notificacion2'")
        logger.info(f"📦 Variables: {variables}")

        # Obtener el ID de correlación desde las variables
        inicial_id = variables.get("notifica2")

        if not inicial_id:
            logger.warning("❗ No se encontró 'notifica2'; no se enviará mensaje.")
            return {"notificado": False}

        # Enviar mensaje al BPMN con la variable notifica2
        await enviar_mensaje(client, inicial_id, {"estado": "notificacion_segunda"})
        return {"notificado": True}

    logger.info(f"🚀 Worker 'reembolso.notificacion2' iniciado en {ZEEBE_HOST}:{ZEEBE_PORT}")
    await worker.work()

# Ejecutar el loop
if __name__ == "__main__":
    asyncio.run(main())
