import os
import asyncio
import grpc
from pyzeebe import ZeebeClient, create_camunda_cloud_channel
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Credenciales de Camunda Cloud
CLIENT_ID = os.getenv("CAMUNDA_CLIENT_ID")
CLIENT_SECRET = os.getenv("CAMUNDA_CLIENT_SECRET")
CLUSTER_ID = os.getenv("CAMUNDA_CLUSTER_ID")
REGION = os.getenv("CAMUNDA_REGION", "lhr-1")

print("Verificando conexión a Camunda Cloud SaaS...")
print(f"Client ID: {CLIENT_ID}")
print(f"Cluster ID: {CLUSTER_ID}")
print(f"Region: {REGION}")

async def main():
    try:
        # Crear canal de conexión a Camunda Cloud
        print("Creando canal de conexión...")
        channel = create_camunda_cloud_channel(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            cluster_id=CLUSTER_ID,
            region=REGION
        )
        
        # Crear cliente Zeebe
        print("Creando cliente Zeebe...")
        client = ZeebeClient(channel)
        
        # Intentar una operación simple para verificar la conexión
        print("Verificando conexión...")
        # La API puede variar según la versión de pyzeebe
        # Intentaremos un método simple que debería funcionar
        try:
            # Intento 1: topology (versión más reciente)
            topology = await client.topology()
            print("\n✅ CONEXIÓN EXITOSA A CAMUNDA CLOUD!")
            print(f"Detalles: {topology}")
        except AttributeError:
            try:
                # Intento 2: publish_message (método común)
                await client.publish_message(name="test_connection", correlation_key="test")
                print("\n✅ CONEXIÓN EXITOSA A CAMUNDA CLOUD!")
                print("Se pudo enviar un mensaje de prueba.")
            except Exception as inner_e:
                # Si es un error de conexión, fallará
                # Si es un error de que el mensaje no existe, la conexión funciona
                if "NOT_FOUND" in str(inner_e) or "no message subscription exists" in str(inner_e).lower():
                    print("\n✅ CONEXIÓN EXITOSA A CAMUNDA CLOUD!")
                    print("La conexión funciona, pero no hay suscripciones para el mensaje de prueba.")
                else:
                    raise inner_e
        
    except grpc.RpcError as grpc_e:
        print("\n❌ ERROR DE CONEXIÓN GRPC:")
        print(f"Código: {grpc_e.code()}")
        print(f"Detalles: {grpc_e.details()}")
        print("\nPosibles soluciones:")
        print("1. Verifica que las credenciales en el archivo .env sean correctas")
        print("2. Asegúrate de tener conexión a Internet")
        print("3. Verifica que tu cuenta de Camunda Cloud esté activa")
        print("4. Comprueba que el cluster esté en ejecución")
    except Exception as e:
        print("\n❌ ERROR DE CONEXIÓN:")
        print(f"{type(e).__name__}: {str(e)}")
        print("\nPosibles soluciones:")
        print("1. Verifica que las credenciales en el archivo .env sean correctas")
        print("2. Asegúrate de tener conexión a Internet")
        print("3. Verifica que tu cuenta de Camunda Cloud esté activa")
        print("4. Comprueba que el cluster esté en ejecución")

if __name__ == "__main__":
    # Ejecutar de forma segura
    asyncio.run(main())
