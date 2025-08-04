from database import Base, engine, SessionLocal
from models import Empleado

# Crear tablas
Base.metadata.create_all(bind=engine)

# Insertar empleados de prueba
db = SessionLocal()
if not db.query(Empleado).first():
    db.add_all([
        Empleado(cedula="1234567890", nombre="Juan Perez"),
        Empleado(cedula="0987654321", nombre="Ana Torres")
    ])
    db.commit()
db.close()
