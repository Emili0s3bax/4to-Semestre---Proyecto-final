from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos
class Post(BaseModel):
    id: int
    url: str
    titulo: str

class Usuario(BaseModel):
    id: int
    nombre: str

# Bases de datos en memoria
posts = []
usuarios = []

# --- Endpoints Posts ---

@app.get("/posts", response_model=List[Post])
async def get_posts():
    return posts

@app.post("/posts")
async def create_post(post: Post):
    posts.append(post)
    return post

@app.delete("/posts/{post_id}")
async def delete_post(post_id: int):
    for index, post in enumerate(posts):
        if post.id == post_id:
            return posts.pop(index)
    raise HTTPException(status_code=404, detail="Post no encontrado")

# --- Endpoints Usuarios ---

@app.get("/usuarios", response_model=List[Usuario])
async def get_usuarios():
    return usuarios

@app.post("/usuarios")
async def create_usuario(usuario: Usuario):
    usuarios.append(usuario)
    return usuario

@app.delete("/usuarios/{usuario_id}")
async def delete_usuario(usuario_id: int):
    for index, user in enumerate(usuarios):
        if user.id == usuario_id:
            return usuarios.pop(index)
    raise HTTPException(status_code=404, detail="Usuario no encontrado")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)