from database import SessionLocal
from models import Empleado

def list_employees():
    """Lista todos los empleados en la base de datos"""
    db = SessionLocal()
    try:
        empleados = db.query(Empleado).all()
        print(f"Total de empleados: {len(empleados)}")
        print("\nLista de empleados:")
        print("-" * 50)
        for emp in empleados:
            print(f"Cédula: {emp.cedula} - Nombre: {emp.nombre}")
        print("-" * 50)
        
        # Verificar si existe el empleado de la factura
        factura_emp = db.query(Empleado).filter(Empleado.cedula == "1707324172001").first()
        if factura_emp:
            print(f"\n✅ El empleado de la factura está registrado correctamente:")
            print(f"   Cédula: {factura_emp.cedula}")
            print(f"   Nombre: {factura_emp.nombre}")
        else:
            print("\n❌ El empleado de la factura NO está registrado.")
            
    finally:
        db.close()

if __name__ == "__main__":
    list_employees()
