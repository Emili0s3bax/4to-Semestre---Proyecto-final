from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session, select
import os

# Cargar variables de entorno locales desde el archivo .env si existe
if os.path.exists(".env"):
    print("Cargando variables de entorno desde el archivo .env...")
    with open(".env", "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                try:
                    key, val = line.split("=", 1)
                    os.environ[key.strip()] = val.strip().strip('"').strip("'")
                except ValueError:
                    pass

from db import create_all_table, engine, SessionDep
from models import Categoria, Post, Usuario
from app.routers import auth, posts, notifications
from app.routers.auth import get_current_user

# Inicializar la aplicación FastAPI con el ciclo de vida de la base de datos
app = FastAPI(lifespan=create_all_table)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir archivos estáticos
static_dir = "static"
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Incluir los enrutadores modulares del backend
app.include_router(auth.router)
app.include_router(posts.router)
app.include_router(notifications.router)

# ==============================================================================
# ENDPOINTS ADICIONALES PARA USUARIOS
# ==============================================================================

@app.get("/users")
def get_all_users(session: SessionDep, skip: int = 0, limit: int = 100):
    """
    Obtiene la lista de todos los usuarios registrados.
    Solo devuelve información pública: id, nombre, username, avatar_color.
    """
    statement = select(Usuario).offset(skip).limit(limit)
    users = session.exec(statement).all()
    
    return [
        {
            "id": user.id,
            "nombre": user.nombre,
            "username": user.username,
            "avatar_color": user.avatar_color
        }
        for user in users
    ]


@app.get("/users/count")
def get_users_count(session: SessionDep):
    """
    Obtiene el número total de usuarios registrados.
    """
    statement = select(Usuario)
    users = session.exec(statement).all()
    return {"total_usuarios": len(users)}


@app.get("/users/{user_id}")
def get_user_by_id(user_id: int, session: SessionDep):
    """
    Obtiene un usuario específico por su ID.
    """
    user = session.get(Usuario, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    return {
        "id": user.id,
        "nombre": user.nombre,
        "username": user.username,
        "email": user.email,
        "edad": user.edad,
        "avatar_color": user.avatar_color
    }


# ==============================================================================
# EVENTO DE INICIALIZACIÓN
# ==============================================================================

@app.on_event("startup")
def seed_data():
    with Session(engine) as session:
        # 1. Sembrar Categorías por defecto
        statement_cats = select(Categoria)
        existing_cats = session.exec(statement_cats).all()
        
        default_categories = ["Naturaleza", "Arte", "Paisajes", "Animales", "Viajes"]
        
        if not existing_cats:
            for cat_name in default_categories:
                session.add(Categoria(nombre=cat_name))
            session.commit()
            print("Categorías iniciales sembradas.")

        # 2. Sembrar un usuario administrador de demostración
        statement_user = select(Usuario).where(Usuario.username == "pinterest")
        admin_user = session.exec(statement_user).first()
        if not admin_user:
            import hashlib
            hashed_pass = hashlib.sha256("admin123".encode("utf-8")).hexdigest()
            admin_user = Usuario(
                nombre="Pinterest Team",
                username="pinterest",
                email="team@pinterest.com",
                edad=25,
                hashed_password=hashed_pass,
                avatar_color="#e60023"
            )
            session.add(admin_user)
            session.commit()
            session.refresh(admin_user)
            print("Usuario de demostración creado.")

        # 3. Sembrar Posts iniciales
        statement_posts = select(Post)
        existing_posts = session.exec(statement_posts).all()
        if not existing_posts:
            demo_posts = [
                Post(
                    titulo="Valle de la Naturaleza",
                    descripcion="Un hermoso amanecer entre las colinas y la neblina primaveral.",
                    url="https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?w=600",
                    categoria="Naturaleza",
                    autor_id=admin_user.id,
                    autor_nombre=admin_user.nombre,
                    fecha_publicacion="28 de mayo, 2026"
                ),
                Post(
                    titulo="Acuarela Abstracta",
                    descripcion="Explosión de colores pastel y formas orgánicas en lienzo de algodón.",
                    url="https://images.unsplash.com/photo-1579783902614-a3fb3927b6a5?w=600",
                    categoria="Arte",
                    autor_id=admin_user.id,
                    autor_nombre=admin_user.nombre,
                    fecha_publicacion="28 de mayo, 2026"
                ),
                Post(
                    titulo="Montañas del Norte",
                    descripcion="Parque Nacional Yosemite, majestuosas formaciones rocosas reflejadas en el agua.",
                    url="https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=600",
                    categoria="Paisajes",
                    autor_id=admin_user.id,
                    autor_nombre=admin_user.nombre,
                    fecha_publicacion="27 de mayo, 2026"
                ),
                Post(
                    titulo="Zorro en la Nieve",
                    descripcion="Un espécimen curioso explorando el bosque blanco durante el invierno.",
                    url="https://images.unsplash.com/photo-1474511320723-9a56873867b5?w=600",
                    categoria="Animales",
                    autor_id=admin_user.id,
                    autor_nombre=admin_user.nombre,
                    fecha_publicacion="26 de mayo, 2026"
                ),
                Post(
                    titulo="Playas del Caribe",
                    descripcion="Atardecer tropical bajo palmeras con aguas cristalinas.",
                    url="https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=600",
                    categoria="Viajes",
                    autor_id=admin_user.id,
                    autor_nombre=admin_user.nombre,
                    fecha_publicacion="25 de mayo, 2026"
                ),
                Post(
                    titulo="Espacio de Trabajo Minimalista",
                    descripcion="Diseño moderno y limpio con setup de programación en Go y Python.",
                    url="https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=600",
                    categoria="Arte",
                    autor_id=admin_user.id,
                    autor_nombre=admin_user.nombre,
                    fecha_publicacion="24 de mayo, 2026"
                )
            ]
            for post in demo_posts:
                session.add(post)
            session.commit()
            print("Posts iniciales de demostración sembrados.")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

