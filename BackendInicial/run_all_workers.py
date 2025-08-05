import os
import subprocess
import sys
import time
import platform
from pathlib import Path

# Configuración
PROJECT_DIR = Path(__file__).parent
WORKERS_DIR = PROJECT_DIR / "workers"
VENV_DIR = PROJECT_DIR / ".venv"

# Determinar el comando para activar el entorno virtual según el sistema operativo
is_windows = platform.system() == "Windows"
venv_python = str(VENV_DIR / "Scripts" / "python") if is_windows else str(VENV_DIR / "bin" / "python")

print(f"Directorio del proyecto: {PROJECT_DIR}")
print(f"Directorio de workers: {WORKERS_DIR}")
print(f"Entorno virtual: {VENV_DIR}")
print(f"Python del entorno virtual: {venv_python}")

# Lista para almacenar los procesos
processes = []

# Verificar que el directorio de workers existe
if not WORKERS_DIR.exists():
    print(f"Error: El directorio {WORKERS_DIR} no existe")
    sys.exit(1)

# Verificar que el entorno virtual existe
if not VENV_DIR.exists():
    print(f"Error: El entorno virtual {VENV_DIR} no existe")
    print("Por favor, crea el entorno virtual primero con: python -m venv .venv")
    sys.exit(1)

# Obtener todos los archivos worker
worker_files = [f for f in WORKERS_DIR.glob("*_worker.py")]

if not worker_files:
    print("No se encontraron archivos worker")
    sys.exit(1)

print(f"\nSe encontraron {len(worker_files)} workers:")
for worker_file in worker_files:
    print(f"  - {worker_file.name}")

print("\nIniciando workers con Camunda Cloud SaaS...")

# Iniciar cada worker en un proceso separado
for worker_file in worker_files:
    print(f"Iniciando worker: {worker_file.name}")
    
    # Usar el Python del entorno virtual para ejecutar el worker
    process = subprocess.Popen(
        [venv_python, str(worker_file)],
        cwd=str(WORKERS_DIR),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        env=dict(os.environ)
    )
    
    processes.append((worker_file.name, process))
    print(f"Worker {worker_file.name} iniciado con PID: {process.pid}")
    
    # Pequeña pausa para evitar problemas de inicialización
    time.sleep(2)

print("\nTodos los workers están en ejecución. Presiona Ctrl+C para detenerlos.\n")

try:
    # Monitorear la salida de los procesos
    while True:
        for name, process in processes:
            # Leer la salida estándar
            output = process.stdout.readline()
            if output:
                print(f"[{name}] {output.strip()}")
            
            # Leer la salida de error
            error = process.stderr.readline()
            if error:
                print(f"[{name}] ERROR: {error.strip()}")
            
            # Verificar si el proceso ha terminado
            if process.poll() is not None:
                print(f"Worker {name} ha terminado con código: {process.returncode}")
                remaining_output, remaining_error = process.communicate()
                if remaining_output:
                    print(f"[{name}] {remaining_output.strip()}")
                if remaining_error:
                    print(f"[{name}] ERROR: {remaining_error.strip()}")
                # Reiniciar el worker
                print(f"Reiniciando worker: {name}")
                process = subprocess.Popen(
                    [venv_python, str(WORKERS_DIR / name)],
                    cwd=str(WORKERS_DIR),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1,
                    env=dict(os.environ)
                )
                # Actualizar la referencia del proceso
                for i, (n, p) in enumerate(processes):
                    if n == name:
                        processes[i] = (name, process)
                        break
        
        # Pequeña pausa para no consumir demasiada CPU
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\nDeteniendo todos los workers...")
    for name, process in processes:
        print(f"Terminando worker: {name}")
        process.terminate()
    
    # Esperar a que todos los procesos terminen
    for name, process in processes:
        process.wait()
        print(f"Worker {name} terminado")
    
    print("Todos los workers han sido detenidos")
