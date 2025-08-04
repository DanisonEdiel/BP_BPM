from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Empleado
from datetime import datetime

app = FastAPI()

# CORS (útil si Camunda está en Docker)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class EmpleadoEntrada(BaseModel):
    nombre: str
    cedula: str


@app.post("/validar-empleado")
def validar_empleado(entrada: EmpleadoEntrada):
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ahora}] /validar-empleado llamado con: nombre='{entrada.nombre}', cedula='{entrada.cedula}'")

    db: Session = SessionLocal()
    try:
        empleado = db.query(Empleado).filter(Empleado.cedula == entrada.cedula).first()
        if not empleado:
            print(f"[{ahora}] Empleado no encontrado para cédula '{entrada.cedula}'")
            return {
                "empleadoEncontrado": False,
                "mensaje": "Empleado no encontrado"
            }
        if empleado.nombre.strip().lower() != entrada.nombre.strip().lower():
            print(f"[{ahora}] Nombre no coincide para cédula '{entrada.cedula}'")
            return {
                "empleadoEncontrado": False,
                "mensaje": "Nombre no coincide"
            }
        print(f"[{ahora}] Empleado válido: '{empleado.nombre}'")
        return {
            "empleadoEncontrado": True,
            "mensaje": "Empleado válido",
            "nombre": empleado.nombre,
            "cedula": empleado.cedula
        }
    finally:
        db.close()
