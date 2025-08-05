import os
import logging
import asyncio
import signal
import sys
from pyzeebe import ZeebeWorker, create_camunda_cloud_channel
from dotenv import load_dotenv

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

# Usar credenciales de Camunda Cloud SaaS
CLIENT_ID = os.getenv("CAMUNDA_CLIENT_ID")
CLIENT_SECRET = os.getenv("CAMUNDA_CLIENT_SECRET")
CLUSTER_ID = os.getenv("CAMUNDA_CLUSTER_ID")
REGION = os.getenv("CAMUNDA_REGION", "lhr-1")

# Definir la tarea del worker
def recibir_solicitud(**variables):
    logger.info("Variables recibidas: %s", variables)
    return variables  # Devolver variables sin cambios

async def main():
    # Crear un nuevo bucle de eventos
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        # Crear canal de conexión a Camunda Cloud
        logger.info(f"Conectando a Camunda Cloud SaaS (Cluster: {CLUSTER_ID}, Region: {REGION})")
        channel = create_camunda_cloud_channel(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            cluster_id=CLUSTER_ID,
            region=REGION
        )
        
        # Crear worker
        worker = ZeebeWorker(channel)
        
        # Registrar la tarea
        worker.task(task_type="reembolso.inicio")(recibir_solicitud)
        
        # Configurar manejo de señales para cierre ordenado
        def handle_signal(sig, frame):
            logger.info(f"Señal {sig} recibida, cerrando worker...")
            loop.stop()
            sys.exit(0)
            
        signal.signal(signal.SIGINT, handle_signal)
        signal.signal(signal.SIGTERM, handle_signal)
        
        # Iniciar worker
        logger.info("🚀 Iniciando worker 'reembolso.inicio'")
        await worker.work()
        
    except Exception as e:
        logger.error(f"Error en el worker: {type(e).__name__}: {str(e)}")
        return 1

if __name__ == "__main__":
    # Ejecutar la función principal
    sys.exit(asyncio.run(main()))
