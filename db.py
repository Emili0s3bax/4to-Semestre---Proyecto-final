from typing import Annotated
from fastapi import Depends, FastAPI
from sqlmodel import SQLModel, Session, create_engine

# Base de datos SQLite local
sqlite_name = "pinterest.sqlite3"
sqlite_url = f"sqlite:///{sqlite_name}"

# check_same_thread=False es necesario para SQLite en entornos multihilo como FastAPI
engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

def create_all_table(app: FastAPI):
    """
    Inicializa y genera las tablas físicas de la base de datos SQLModel
    al arrancar la aplicación FastAPI.
    """
    SQLModel.metadata.create_all(engine)
    yield

def get_session():
    """
    Generador de sesiones de base de datos.
    Asegura que cada solicitud HTTP tenga su sesión y se cierre al finalizar.
    """
    with Session(engine) as session:
        yield session

# Tipo anotado para simplificar la inyección de dependencias en las rutas de FastAPI
SessionDep = Annotated[Session, Depends(get_session)]
