from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Usa variables de entorno o hardcode para desarrollo local
DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:example@localhost:5435/reembolsos")

engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
