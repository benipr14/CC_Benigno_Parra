from fastapi import APIRouter, Depends, HTTPException, status
from app.api.deps import get_user_repo
from app.services.partido_service import crear_partido, obtener_partido, cambiar_cuota_partido, termina_partido
from app.models.schemas import PartidoCreate, PartidoOut

router = APIRouter(prefix="/api/v1/partidos", tags=["partidos"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_partido(payload: PartidoCreate, repo=Depends(get_user_repo)):
    # payload is validated by Pydantic
    pid = crear_partido(payload, repo=repo)
    return {"_id": pid}


@router.get("/{pid}", response_model=PartidoOut)
def get_partido(pid: str, repo=Depends(get_user_repo)):
    p = obtener_partido(pid, repo)
    if not p:
        raise HTTPException(status_code=404, detail="Partido no encontrado")
    return p


@router.post("/{pid}/cuota")
def post_cambiar_cuota(pid: str, payload: dict, repo=Depends(get_user_repo)):
    condicion = payload.get("condicion")
    nueva = payload.get("nueva")
    ok = cambiar_cuota_partido(pid, condicion, nueva, repo)
    if ok is None:
        raise HTTPException(status_code=400, detail="Condicion no válida")
    if not ok:
        raise HTTPException(status_code=404, detail="Partido no encontrado")
    return {"ok": True}


@router.post("/{pid}/resultado")
def post_terminar_partido(pid: str, payload: dict, repo=Depends(get_user_repo)):
    resultado = payload.get("resultado")
    settled = termina_partido(pid, resultado, repo)
    if settled is None:
        raise HTTPException(status_code=400, detail="No se pudo terminar el partido (entrada inválida o partido no encontrado)")
    return {"liquidadas": settled}
