# BackendInicial

Este proyecto utiliza FastAPI y un entorno virtual de Python para gestionar dependencias.

## Crear el entorno virtual (.venv)

1. Abre una terminal en la carpeta del proyecto.
2. Ejecuta el siguiente comando:
    ```bash
    python -m venv .venv
    ```
3. Activa el entorno virtual:
    - **Windows:**
      ```bash
      .venv\Scripts\activate
      ```
    - **Linux/Mac:**
      ```bash
      source .venv/bin/activate
      ```

## Instalar dependencias

```bash
pip install -r requirements.txt
```

## Ejecutar el servicio FastAPI

Asegúrate de estar en el entorno virtual y ejecuta:

```bash
uvicorn main:app --reload
```

## Ejecutar el servicio Workers
```bash
python workers/reembolso_worker.py
```
Reemplaza `main:app` por el módulo y la instancia de tu aplicación si es diferente.