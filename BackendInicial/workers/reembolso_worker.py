import os
import logging
import asyncio
from pyzeebe import ZeebeWorker, create_insecure_channel
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

ZEEBE_HOST = os.getenv("ZEEBE_HOST", "localhost").strip()
ZEEBE_PORT = int(os.getenv("ZEEBE_PORT", "26500").strip())

channel = create_insecure_channel(f"{ZEEBE_HOST}:{ZEEBE_PORT}")
worker = ZeebeWorker(channel)

@worker.task(task_type="reembolso.inicio")
def recibir_solicitud(**variables):
    print("Variables recibidas:", variables)
    return variables  # si quieres devolverlas sin cambios


async def main():
    logger.info("🚀 Iniciando worker 'reembolso.inicio'")
    await worker.work()

if __name__ == "__main__":
    # ✅ Usa esta forma para evitar el conflicto de loops
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
