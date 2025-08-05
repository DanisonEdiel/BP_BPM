from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Usa SQLite para desarrollo local (más fácil de configurar)
DB_URL = os.getenv("DATABASE_URL", "sqlite:///./empleados.db")

engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
