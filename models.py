from sqlmodel import Field, SQLModel, Relationship
from typing import List, Optional

# ==============================================================================
# Modelos del Usuario
# ==============================================================================

class UsuarioBase(SQLModel):
    nombre: str
    username: str
    email: str
    edad: int
    avatar_color: str = "#e60023"

class Usuario(UsuarioBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str
    
    # Relaciones estrictas bidireccionales
    posts: List["Post"] = Relationship(
        back_populates="autor", 
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    comentarios: List["Comentario"] = Relationship(
        back_populates="autor", 
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    notificaciones: List["Notificacion"] = Relationship(
        back_populates="usuario",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

class UsuarioCreate(SQLModel):
    nombre: str
    username: str
    email: str
    password: str
    edad: int

class UsuarioUpdate(SQLModel):
    nombre: Optional[str] = None
    username: Optional[str] = None
    email: Optional[str] = None
    edad: Optional[int] = None
    password: Optional[str] = None

class UsuarioResponse(UsuarioBase):
    id: int

# ==============================================================================
# Modelos de Publicación (Post)
# ==============================================================================

class PostBase(SQLModel):
    titulo: str
    descripcion: Optional[str] = None
    url: str  # URL de la imagen (AWS S3 o local)
    categoria: str
    autor_id: int = Field(foreign_key="usuario.id")
    autor_nombre: str
    fecha_publicacion: str

class Post(PostBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Relaciones estrictas
    autor: Usuario = Relationship(back_populates="posts")
    comentarios: List["Comentario"] = Relationship(
        back_populates="post", 
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

# ==============================================================================
# Modelos de Comentarios
# ==============================================================================

class Comentario(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    texto: str
    
    # Claves foráneas (FK) estrictas
    post_id: int = Field(foreign_key="post.id")
    autor_id: int = Field(foreign_key="usuario.id")
    
    autor_nombre: str
    autor_avatar_color: str
    fecha: str
    
    # Relaciones
    post: Post = Relationship(back_populates="comentarios")
    autor: Usuario = Relationship(back_populates="comentarios")

class ComentarioCreate(SQLModel):
    texto: str
    post_id: int
    autor_id: int
    autor_nombre: str
    autor_avatar_color: str

# ==============================================================================
# Modelos de Categorías
# ==============================================================================

class Categoria(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str

# ==============================================================================
# Modelos de Notificación (Módulo Extra)
# ==============================================================================

class Notificacion(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuario.id")
    tipo: str  # "comentario" o "guardado"
    texto: str
    fecha: str
    leido: bool = False
    
    # Relación
    usuario: Usuario = Relationship(back_populates="notificaciones")
