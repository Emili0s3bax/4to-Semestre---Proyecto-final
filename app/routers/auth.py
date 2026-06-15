import hashlib
import random
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import select
from db import SessionDep
from models import Usuario, UsuarioCreate, UsuarioUpdate, UsuarioResponse

# ==============================================================================
# CONFIGURACIÓN JWT
# ==============================================================================
# !!! IMPORTANTE: Cambia esta clave por una secreta en producción !!!
SECRET_KEY = "tu-clave-secreta-muy-segura-cambiala-en-produccion-12345"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 horas

# Para manejar tokens en headers
security = HTTPBearer()

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

# ==============================================================================
# FUNCIONES DE UTILIDAD
# ==============================================================================

def hash_password(password: str) -> str:
    """Función para hashear contraseñas usando SHA-256."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def create_access_token(data: dict) -> str:
    """Crea un token JWT con fecha de expiración."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    # Importar jwt aquí para evitar error si no está instalado
    from jose import jwt
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """Decodifica y verifica un token JWT."""
    from jose import jwt, JWTError
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado"
        )


def get_current_user(session: SessionDep, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Obtiene el usuario actual a partir del token JWT."""
    token = credentials.credentials
    payload = decode_access_token(token)
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )
    
    user = session.get(Usuario, int(user_id))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado"
        )
    
    return user


def get_current_user_optional(session: SessionDep, credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """Obtiene el usuario actual si hay token, sino devuelve None."""
    try:
        if credentials:
            return get_current_user(session, credentials)
    except HTTPException:
        pass
    return None

# ==============================================================================
# ENDPOINTS DE AUTENTICACIÓN
# ==============================================================================

@router.post("/register", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UsuarioCreate, session: SessionDep):
    """
    Registra un nuevo usuario en el sistema.
    """
    # Validar edad mínima (18 años)
    if user_data.edad < 18:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El registro y acceso está restringido a mayores de edad (18 años o más)."
        )

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
    
    # No devolvemos el password hasheado por seguridad
    return usuario


@router.post("/login")
def login(login_data: dict, session: SessionDep):
    """
    Inicia sesión con username/email y contraseña.
    Devuelve token JWT y datos del usuario.
    """
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
    
    # Crear token JWT
    token_data = {"sub": str(user.id), "username": user.username}
    access_token = create_access_token(token_data)
    
    # Devolver token y datos del usuario (sin el password)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "nombre": user.nombre,
            "username": user.username,
            "email": user.email,
            "edad": user.edad,
            "avatar_color": user.avatar_color
        }
    }


@router.post("/logout")
def logout(current_user: Usuario = Depends(get_current_user)):
    """
    Cierra la sesión del usuario actual.
    (El logout es principalmente en el frontend, este endpoint es opcional)
    """
    return {"message": "Sesión cerrada correctamente"}


@router.get("/me", response_model=UsuarioResponse)
def get_me(current_user: Usuario = Depends(get_current_user)):
    """
    Obtiene la información del usuario actual (requiere token).
    """
    return current_user


@router.get("/verify")
def verify_token(current_user: Usuario = Depends(get_current_user)):
    """
    Verifica si el token es válido.
    """
    return {
        "valid": True,
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "nombre": current_user.nombre
        }
    }


# ==============================================================================
# ENDPOINTS DE ACTUALIZACIÓN DE USUARIO
# ==============================================================================

@router.put("/users/{user_id}", response_model=UsuarioResponse)
def update_user(user_id: int, user_data: UsuarioUpdate, session: SessionDep, current_user: Usuario = Depends(get_current_user)):
    """
    Actualiza los datos de un usuario (solo el propio usuario puede hacerlo).
    """
    # Solo permitir que el usuario actualice su propio perfil
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para modificar este usuario"
        )
    
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


# ==============================================================================
# ENDPOINT PARA OBTENER USUARIO POR ID (PÚBLICO)
# ==============================================================================

@router.get("/users/{user_id}", response_model=UsuarioResponse)
def get_user_by_id(user_id: int, session: SessionDep):
    """
    Obtiene información pública de un usuario por su ID.
    """
    user = session.get(Usuario, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado."
        )
    return user