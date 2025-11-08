from typing import Dict, Any

from app.repositories.base import FullRepo


def crear_partido(*args, **kwargs) -> str:
    """Create a partido.

    Supports two calling styles for backward compatibility:
      - crear_partido(local, visitante, cuota_local, cuota_empate, cuota_visitante, fecha, hora, resultado, repo)
      - crear_partido(partido_dict_or_model, repo=repo)
    """
    # backward compatible style: many positional args ending with repo
    if len(args) >= 9:
        # original signature
        local, visitante, cuota_local, cuota_empate, cuota_visitante, fecha, hora, resultado, repo = args[:9]
        partido = {
            "local": local,
            "visitante": visitante,
            "cuota_local": cuota_local,
            "cuota_empate": cuota_empate,
            "cuota_visitante": cuota_visitante,
            "fecha": fecha,
            "hora": hora,
            "resultado": resultado,
        }
        pid = repo.insertar_partido(partido)
        return pid

    # new style: first arg is mapping or Pydantic model, or passed via kwargs
    repo = kwargs.get("repo") or (args[1] if len(args) >= 2 else None)
    data = args[0] if len(args) >= 1 else kwargs.get("partido") or kwargs
    # accept pydantic model (support model_dump for Pydantic v2)
    if hasattr(data, "model_dump"):
        partido = data.model_dump()
    elif hasattr(data, "dict"):
        partido = data.dict()
    elif isinstance(data, dict):
        partido = dict(data)
    else:
        # try to extract attributes
        partido = {k: getattr(data, k) for k in ("local", "visitante", "cuota_local", "cuota_empate", "cuota_visitante", "fecha", "hora", "resultado") if hasattr(data, k)}

    pid = repo.insertar_partido(partido)
    return pid


def obtener_partido(pid: str, repo: FullRepo) -> Dict:
    p = repo.obtener_partido(pid)
    return p


def cambiar_cuota_partido(pid: str, condicion: str, nueva_cuota: float, repo: FullRepo):
    # condicion in {"1","X","2"}
    if condicion not in {"1", "X", "2"}:
        return None
    field = {
        "1": "cuota_local",
        "X": "cuota_empate",
        "2": "cuota_visitante",
    }[condicion]
    ok = repo.update_partido(pid, {field: nueva_cuota})
    return ok


def termina_partido(pid: str, resultado: str, repo: FullRepo):
    """Set the result of a match and settle bets.

    Returns list of settled apuesta ids or None on error/invalid input.
    """
    if resultado not in {"1", "X", "2"}:
        return None
    partido = repo.obtener_partido(pid)
    if not partido:
        return None

    # verify partido date/time: cannot finish before the scheduled date/time
    from datetime import datetime
    fecha = partido.get("fecha")
    hora = partido.get("hora")
    try:
        partido_dt = datetime.strptime(f"{fecha} {hora}", "%Y-%m-%d %H:%M")
    except Exception:
        # invalid date format - refuse
        return None
    now = datetime.now()
    if now < partido_dt:
        # partido not yet occurred
        return None
    # update partido result
    updated = repo.update_partido(pid, {"resultado": resultado})
    if not updated:
        return None

    # settle bets
    apuestas = repo.get_apuestas_by_partido(pid)
    settled = []
    for a in apuestas:
        elegido = a.get("elegido")
        cantidad = float(a.get("cantidad", 0.0))
        usuario_id = a.get("usuario_id")
        if elegido == resultado:
            # determine cuota
            cuota = None
            if resultado == "1":
                cuota = partido.get("cuota_local", 1.0)
            elif resultado == "X":
                cuota = partido.get("cuota_empate", 1.0)
            elif resultado == "2":
                cuota = partido.get("cuota_visitante", 1.0)
            # add winnings (note: stake was already subtracted when bet placed)
            ganancia = cantidad * float(cuota)
            # get current user
            usuario = repo.obtener_usuario(usuario_id)
            if usuario:
                nuevo_saldo = float(usuario.get("saldo", 0.0)) + ganancia
                repo.update_usuario_saldo(usuario_id, nuevo_saldo)
        # if lost do nothing (stake already deducted)
        settled.append(a.get("_id"))

    return settled
