from fastapi import APIRouter, Depends, HTTPException, status
from app.models.schemas import UsuarioCreate, UsuarioOut
from app.api.deps import get_user_repo
from app.services.usuario_service import crear_usuario, obtener_usuario
from app.exceptions import UserExistsError, NotFoundError

router = APIRouter(prefix="/api/v1/usuarios", tags=["usuarios"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_usuario(payload: UsuarioCreate, repo=Depends(get_user_repo)):
    try:
        uid = crear_usuario(payload.usuario, payload.contrasenia, payload.saldo, repo)
        return {"_id": uid}
    except UserExistsError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{uid}", response_model=UsuarioOut)
def get_usuario(uid: str, repo=Depends(get_user_repo)):
    try:
        u = obtener_usuario(uid, repo)
        return u
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
