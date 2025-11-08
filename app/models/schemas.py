from pydantic import BaseModel


class PingResponse(BaseModel):
    msg: str


class UsuarioCreate(BaseModel):
    usuario: str
    contrasenia: str
    saldo: float = 0.0


class UsuarioOut(BaseModel):
    _id: str
    usuario: str
    contrasenia: str
    saldo: float
    apuestas: list = []


class PartidoCreate(BaseModel):
    local: str
    visitante: str
    cuota_local: float
    cuota_empate: float
    cuota_visitante: float
    fecha: str  # ISO date YYYY-MM-DD
    hora: str  # HH:MM
    resultado: str = "Pendiente"


class PartidoOut(BaseModel):
    _id: str
    local: str
    visitante: str
    cuota_local: float
    cuota_empate: float
    cuota_visitante: float
    fecha: str
    hora: str
    resultado: str
