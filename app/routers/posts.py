import os
import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Form, File, UploadFile
from sqlmodel import select
from db import SessionDep
from models import Post, Comentario, ComentarioCreate, Categoria, Usuario, Notificacion
from app.s3_helper import upload_file_to_s3

router = APIRouter(tags=["posts"])

# Asegurar que el directorio de subidas locales existe
UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("/posts")
def get_posts(
    session: SessionDep, 
    category: Optional[str] = None, 
    search: Optional[str] = None,
    user_id: Optional[int] = None
):
    """Obtiene los posts con filtrado por categoría, búsqueda y autor."""
    statement = select(Post)
    
    # Filtrar por usuario creador
    if user_id:
        statement = statement.where(Post.autor_id == user_id)
        
    # Filtrar por categoría (ignorando "Todos")
    if category and category != "Todos":
        statement = statement.where(Post.categoria == category)
        
    # Filtrar por término de búsqueda en título, descripción y autor
    if search:
        search_term = f"%{search.lower()}%"
        statement = statement.where(
            (Post.titulo.collate("NOCASE").like(search_term)) | 
            (Post.descripcion.collate("NOCASE").like(search_term)) |
            (Post.autor_nombre.collate("NOCASE").like(search_term))
        )
        
    # Ordenar de más nuevo a más viejo
    statement = statement.order_by(Post.id.desc())
    return session.exec(statement).all()

@router.get("/posts/{post_id}")
def get_post_by_id(post_id: int, session: SessionDep):
    """Obtiene un post y sus comentarios asociados."""
    post_db = session.get(Post, post_id)
    if not post_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Post no encontrado"
        )
    
    return {
        "post": post_db, 
        "comentarios": post_db.comentarios
    }

@router.post("/posts", status_code=status.HTTP_201_CREATED)
async def create_post(
    session: SessionDep,
    titulo: str = Form(...),
    descripcion: Optional[str] = Form(None),
    categoria: str = Form(...),
    autor_id: int = Form(...),
    file: UploadFile = File(...)
):
    """Crea un nuevo Post subiendo una imagen a AWS S3 (con respaldo local)."""
    # Verificar que el usuario autor existe
    usuario = session.get(Usuario, autor_id)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario creador no encontrado."
        )

    # Validar extensión del archivo
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in [".jpg", ".jpeg", ".png", ".gif", ".webp"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo debe ser una imagen válida (.jpg, .png, .gif, .webp)."
        )

    # Crear nombre único
    unique_filename = f"{uuid.uuid4()}{file_ext}"

    # Leer archivo
    content = await file.read()
    source_url = None
    
    # Intentar subida a S3
    try:
        source_url = upload_file_to_s3(content, unique_filename, file.content_type)
        print(f"Subido con éxito a S3: {source_url}")
    except Exception as e:
        print(f"Advertencia: Falló carga en S3 ({str(e)}). Usando almacenamiento local...")
        # Guardado local como respaldo
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        try:
            with open(file_path, "wb") as buffer:
                buffer.write(content)
            source_url = f"/static/uploads/{unique_filename}"
        except Exception as local_err:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al guardar la imagen en local y en S3: {str(local_err)}"
            )

    # Normalizar categoría
    normalized_category = categoria.strip().title()

    # Agregar la categoría a la BD si es nueva
    statement_cat = select(Categoria).where(Categoria.nombre == normalized_category)
    existing_cat = session.exec(statement_cat).first()
    if not existing_cat:
        new_cat = Categoria(nombre=normalized_category)
        session.add(new_cat)
        session.commit()

    # Formatear la fecha en español
    fecha_hoy = datetime.now().strftime("%d de %B, %Y")
    meses_en = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    meses_es = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    for en, es in zip(meses_en, meses_es):
        fecha_hoy = fecha_hoy.replace(en, es)

    # Crear el Post en base de datos
    nuevo_post = Post(
        titulo=titulo,
        descripcion=descripcion,
        url=source_url,  # Guardamos bajo el campo 'url'
        categoria=normalized_category,
        autor_id=autor_id,
        autor_nombre=usuario.nombre,
        fecha_publicacion=fecha_hoy
    )

    session.add(nuevo_post)
    session.commit()
    session.refresh(nuevo_post)
    return nuevo_post

@router.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, session: SessionDep):
    """Elimina un post de la base de datos y borra su archivo si era local."""
    post_db = session.get(Post, post_id)
    if not post_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Post no encontrado"
        )
    
    # Si la imagen era local, borrarla física del disco
    if post_db.url.startswith("/static/"):
        image_rel_path = post_db.url.lstrip("/")
        if os.path.exists(image_rel_path):
            try:
                os.remove(image_rel_path)
            except Exception as e:
                print(f"Error al eliminar archivo local {image_rel_path}: {e}")

    session.delete(post_db)
    session.commit()
    return None

@router.post("/comments", status_code=status.HTTP_201_CREATED)
def add_comment(data: ComentarioCreate, session: SessionDep):
    """Agrega un comentario a un post y crea una notificación (Extra)."""
    post_db = session.get(Post, data.post_id)
    if not post_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post no encontrado"
        )

    fecha_comentario = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    nuevo_comentario = Comentario(
        texto=data.texto,
        post_id=data.post_id,
        autor_id=data.autor_id,
        autor_nombre=data.autor_nombre,
        autor_avatar_color=data.autor_avatar_color,
        fecha=fecha_comentario
    )
    
    session.add(nuevo_comentario)
    session.commit()
    session.refresh(nuevo_comentario)
    
    # Generar notificación para el autor si el comentario es de otro usuario (Módulo Extra)
    if post_db.autor_id and data.autor_id != post_db.autor_id:
        fecha_notif = datetime.now().strftime("%d/%m/%Y %H:%M")
        notif = Notificacion(
            usuario_id=post_db.autor_id,
            tipo="comentario",
            texto=f"{data.autor_nombre} comentó en tu publicación '{post_db.titulo}': \"{data.texto}\"",
            fecha=fecha_notif,
            leido=False
        )
        session.add(notif)
        session.commit()
        
    return nuevo_comentario

@router.get("/categories")
def get_categories(session: SessionDep):
    """Retorna todas las categorías."""
    statement = select(Categoria)
    return session.exec(statement).all()

@router.post("/posts/{post_id}/save")
def save_post_endpoint(post_id: int, payload: dict, session: SessionDep):
    """Guarda un post local y genera notificación al creador original (Extra)."""
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=400, detail="Falta user_id del usuario.")
    
    post_db = session.get(Post, post_id)
    if not post_db:
        raise HTTPException(status_code=404, detail="Post no encontrado.")
    
    usuario_accion = session.get(Usuario, user_id)
    if not usuario_accion:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    
    # Generar notificación para el creador si no es él mismo quien guarda (Módulo Extra)
    if post_db.autor_id != user_id:
        fecha_notif = datetime.now().strftime("%d/%m/%Y %H:%M")
        notif = Notificacion(
            usuario_id=post_db.autor_id,
            tipo="guardado",
            texto=f"{usuario_accion.nombre} guardó tu publicación '{post_db.titulo}'",
            fecha=fecha_notif,
            leido=False
        )
        session.add(notif)
        session.commit()
        
    return {"status": "ok"}
