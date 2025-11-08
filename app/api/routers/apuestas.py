from fastapi import APIRouter, Depends, HTTPException, status
from app.api.deps import get_user_repo
from app.services.apuesta_service import hacer_apuesta, obtener_apuesta

router = APIRouter(prefix="/api/v1/apuestas", tags=["apuestas"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_apuesta(payload: dict, repo=Depends(get_user_repo)):
    usuario_id = payload.get("usuario_id")
    partido_id = payload.get("partido_id")
    elegido = payload.get("elegido")
    cantidad = payload.get("cantidad")
    aid = hacer_apuesta(usuario_id, partido_id, elegido, cantidad, repo)
    if aid is None:
        raise HTTPException(status_code=400, detail="No se pudo realizar la apuesta")
    return {"_id": aid}


@router.get("/{aid}")
def get_apuesta(aid: str, repo=Depends(get_user_repo)):
    a = obtener_apuesta(aid, repo)
    if not a:
        raise HTTPException(status_code=404, detail="Apuesta no encontrada")
    return a
