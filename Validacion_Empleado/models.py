from sqlalchemy import Column, String
from database import Base

class Empleado(Base):
    __tablename__ = "empleados"

    cedula = Column(String, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
