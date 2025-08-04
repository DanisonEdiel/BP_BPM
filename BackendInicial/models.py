from pydantic import BaseModel, EmailStr

class SolicitudReembolso(BaseModel):
    nombre: str
    cedula: str
    departamento: str
    correo: EmailStr
    telefono: str
    fechaGasto: str
    tipoGasto: str
    numeroFactura: str
    monto: float
    medioPago: str
    descripcion: str

    class Config:
        validate_by_name = True
