from fastapi import APIRouter, HTTPException, status
from sqlmodel import select
from db import SessionDep
from models import Notificacion

router = APIRouter(prefix="/api/notifications", tags=["notifications"])

@router.get("")
def get_notifications(user_id: int, session: SessionDep):
    """
    Obtiene todas las notificaciones de un usuario específico.
    Se ordenan de manera descendente (las más recientes primero).
    """
    statement = select(Notificacion).where(Notificacion.usuario_id == user_id).order_by(Notificacion.id.desc())
    return session.exec(statement).all()

@router.post("/read-all")
def read_all_notifications(user_id: int, session: SessionDep):
    """
    Marca todas las notificaciones del usuario como leídas.
    Pone la insignia 'leido' en True en la base de datos.
    """
    statement = select(Notificacion).where(Notificacion.usuario_id == user_id, Notificacion.leido == False)
    notifs = session.exec(statement).all()
    
    for n in notifs:
        n.leido = True
        session.add(n)
        
    session.commit()
    return {"status": "ok"}
