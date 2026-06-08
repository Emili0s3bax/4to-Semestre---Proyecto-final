import hashlib
import random
from fastapi import APIRouter, HTTPException, status
from sqlmodel import select
from db import SessionDep
from models import Usuario, UsuarioCreate, UsuarioUpdate, UsuarioResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])

# Colores de avatar de usuario al estilo Pinterest
AVATAR_COLORS = [
    "#e60023",  # Pinterest Red
    "#0076d3",  # Blue
    "#008a15",  # Green
    "#e600b3",  # Pink
    "#e6b300",  # Yellow/Gold
    "#00b3e6",  # Teal
    "#7600d3",  # Purple
    "#d35400",  # Orange
    "#1abc9c",  # Turquoise
    "#2c3e50"   # Dark Blue-Gray
]

def hash_password(password: str) -> str:
    """Función para hashear contraseñas usando SHA-256."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

@router.post("/register", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UsuarioCreate, session: SessionDep):
    # Verificar si el username o email ya existen
    statement_username = select(Usuario).where(Usuario.username == user_data.username)
    statement_email = select(Usuario).where(Usuario.email == user_data.email)
    
    if session.exec(statement_username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre de usuario ya está registrado."
        )
    
    if session.exec(statement_email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo electrónico ya está registrado."
        )
    
    # Crear nuevo usuario
    hashed = hash_password(user_data.password)
    random_color = random.choice(AVATAR_COLORS)
    
    usuario = Usuario(
        nombre=user_data.nombre,
        username=user_data.username,
        email=user_data.email,
        edad=user_data.edad,
        hashed_password=hashed,
        avatar_color=random_color
    )
    
    session.add(usuario)
    session.commit()
    session.refresh(usuario)
    return usuario

@router.post("/login", response_model=UsuarioResponse)
def login(login_data: dict, session: SessionDep):
    # identifier puede ser email o username
    identifier = login_data.get("identifier")
    password = login_data.get("password")
    
    if not identifier or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El identificador y la contraseña son obligatorios."
        )
    
    # Buscar por email o username
    statement = select(Usuario).where((Usuario.email == identifier) | (Usuario.username == identifier))
    user = session.exec(statement).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El usuario no existe o las credenciales son incorrectas."
        )
    
    # Validar password
    hashed_input = hash_password(password)
    if user.hashed_password != hashed_input:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="La contraseña es incorrecta."
        )
        
    return user

@router.put("/users/{user_id}", response_model=UsuarioResponse)
def update_user(user_id: int, user_data: UsuarioUpdate, session: SessionDep):
    user = session.get(Usuario, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado."
        )
        
    # Validaciones de unicidad si se actualiza username o email
    if user_data.username and user_data.username != user.username:
        statement = select(Usuario).where(Usuario.username == user_data.username)
        if session.exec(statement).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El nuevo nombre de usuario ya está en uso."
            )
        user.username = user_data.username
        
    if user_data.email and user_data.email != user.email:
        statement = select(Usuario).where(Usuario.email == user_data.email)
        if session.exec(statement).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El nuevo correo electrónico ya está en uso."
            )
        user.email = user_data.email
        
    if user_data.nombre is not None:
        user.nombre = user_data.nombre
        
    if user_data.edad is not None:
        user.edad = user_data.edad
        
    if user_data.password:
        user.hashed_password = hash_password(user_data.password)
        
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
