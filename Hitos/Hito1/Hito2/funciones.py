from pymongo import MongoClient

# Conexión local sin autenticación
cliente = MongoClient("mongodb://localhost:27017")
db = cliente["CC"]
coleccion_usuarios = db["usuarios"]
coleccion_apuestas = db["apuestas"]
coleccion_partidos = db["partidos"]
coleccion_administradores = db["administradores"]


def init_db(client=None, db_name: str = "CC"):
    """Inicializa las colecciones del módulo con un cliente Mongo proporcionado.

    Uso en tests: pasar un mongomock.MongoClient() para tener una BD en memoria.
    """
    # Declarar globals en dos líneas para evitar líneas demasiado largas
    global cliente, db, coleccion_usuarios, coleccion_apuestas
    global coleccion_partidos, coleccion_administradores
    if client is None:
        from pymongo import MongoClient as _MongoClient

        client = _MongoClient("mongodb://localhost:27017")
    cliente = client
    db = cliente[db_name]
    coleccion_usuarios = db["usuarios"]
    coleccion_apuestas = db["apuestas"]
    coleccion_partidos = db["partidos"]
    coleccion_administradores = db["administradores"]

# INSERCIONES
def insertar_usuario(usuario, contrasenia, saldo):
    nuevo_usuario = {
        "usuario": usuario,
        "contrasenia": contrasenia,
        "saldo": saldo,
        "apuestas": [],
    }
    resultado = coleccion_usuarios.insert_one(nuevo_usuario)
    print(f"Usuario insertado con _id: {resultado.inserted_id}")
    return resultado.inserted_id


def insertar_administrador(usuario, contrasenia, rol):
    nuevo_administrador = {"usuario": usuario, "contrasenia": contrasenia, "rol": rol}
    resultado = coleccion_administradores.insert_one(nuevo_administrador)
    print(f"Administrador insertado con _id: {resultado.inserted_id}")
    return resultado.inserted_id


def insertar_partido(
    local,
    visitante,
    cuota_local,
    cuota_empate,
    cuota_visitante,
    fecha,
    hora,
    resultado="Pendiente",
):
    nuevo_partido = {
        "local": local,
        "visitante": visitante,
        "cuota_local": cuota_local,
        "cuota_empate": cuota_empate,
        "cuota_visitante": cuota_visitante,
        "fecha": fecha,
        "hora": hora,
        "resultado": resultado,
    }
    resultado = coleccion_partidos.insert_one(nuevo_partido)
    print(f"Partido insertado con _id: {resultado.inserted_id}")
    return resultado.inserted_id

def hacer_apuesta(usuario_id, partido_id, elegido, cantidad):
    from datetime import datetime

    # Obtener el partido
    partido = coleccion_partidos.find_one({"_id": partido_id})
    if not partido:
        print("No se encontró el partido.")
        return None
    # Unir fecha y hora del partido
    fecha_hora_str = f"{partido['fecha']} {partido['hora']}"
    try:
        fecha_hora_partido = datetime.strptime(fecha_hora_str, "%Y-%m-%d %H:%M")
    except Exception as e:
        print(f"Error en el formato de fecha/hora del partido: {e}")
        return
    ahora = datetime.now()
    if ahora >= fecha_hora_partido:
        print("No se puede hacer la apuesta: el partido ya ha comenzado.")
        return None
    # Comprobar saldo suficiente
    usuario = coleccion_usuarios.find_one({"_id": usuario_id})
    if not usuario:
        print("Usuario no encontrado.")
        return None
    saldo_actual = usuario.get("saldo", 0)
    if saldo_actual < cantidad:
        print("Saldo insuficiente para realizar la apuesta.")
        return None
    # Restar saldo
    coleccion_usuarios.update_one({"_id": usuario_id}, {"$inc": {"saldo": -cantidad}})
    # Insertar la apuesta
    apuesta = {
        "usuario_id": usuario_id,
        "partido_id": partido_id,
        "elegido": elegido,
        "cantidad": cantidad,
    }
    resultado_apuesta = coleccion_apuestas.insert_one(apuesta)
    apuesta_id = resultado_apuesta.inserted_id
    print(f"Apuesta insertada con _id: {apuesta_id}")
    # Añadir el id de la apuesta al array de apuestas del usuario
    coleccion_usuarios.update_one(
        {"_id": usuario_id}, {"$push": {"apuestas": apuesta_id}}
    )
    return apuesta_id


def termina_partido(partido_id, resultado):
    if resultado not in ["1", "X", "2"]:
        print("Resultado inválido. Use '1', 'X' o '2'.")
        return None
    # Obtener partido para comprobar fecha/hora
    partido = coleccion_partidos.find_one({"_id": partido_id})
    if not partido:
        print(f"No se encontró el partido con _id: {partido_id}")
        return None
    from datetime import datetime

    fecha_hora_str = f"{partido['fecha']} {partido['hora']}"
    try:
        fecha_hora_partido = datetime.strptime(fecha_hora_str, "%Y-%m-%d %H:%M")
    except Exception as e:
        print(f"Error en el formato de fecha/hora del partido: {e}")
        return None
    ahora = datetime.now()
    if ahora < fecha_hora_partido:
        print("No se puede finalizar el partido: aún no ha comenzado.")
        return None
    # Actualizar resultado del partido
    resultado_update = coleccion_partidos.update_one(
        {"_id": partido_id}, {"$set": {"resultado": resultado}}
    )
    if resultado_update.matched_count == 0:
        print(f"No se encontró el partido con _id: {partido_id}")
        return
    # Buscar apuestas relacionadas
    apuestas = list(coleccion_apuestas.find({"partido_id": partido_id}))
    for apuesta in apuestas:
        usuario_id = apuesta["usuario_id"]
        elegido = apuesta["elegido"]
        cantidad = apuesta["cantidad"]
        premio = 0.0
        # Solo si la apuesta es acertada
        if elegido == resultado:
            if resultado == "1":
                cuota = partido.get("cuota_local", 0)
            elif resultado == "X":
                cuota = partido.get("cuota_empate", 0)
            elif resultado == "2":
                cuota = partido.get("cuota_visitante", 0)
            else:
                cuota = 0
            premio = cantidad * cuota
            # Actualizar saldo del usuario
            coleccion_usuarios.update_one(
                {"_id": usuario_id}, {"$inc": {"saldo": premio}}
            )
            print(f"Usuario {usuario_id} acertó la apuesta y ganó {premio:.2f}€.")
        else:
            print(f"Usuario {usuario_id} no acertó la apuesta.")


def cambiar_cuota_partido(partido_id, condicion, nueva_cuota):
    campo_cuota = ""
    if condicion == "1":
        campo_cuota = "cuota_local"
    elif condicion == "X":
        campo_cuota = "cuota_empate"
    elif condicion == "2":
        campo_cuota = "cuota_visitante"
    else:
        print("Condición inválida. Use '1', 'X' o '2'.")
        return

    resultado = coleccion_partidos.update_one(
        {"_id": partido_id}, {"$set": {campo_cuota: nueva_cuota}}
    )
    if resultado.matched_count > 0:
        print(f"Cuota actualizada para el partido con _id: {partido_id}")
    else:
        print(f"No se encontró el partido con _id: {partido_id}")


def cambiar_fecha_partido(partido_id, nueva_fecha, nueva_hora):
    from datetime import datetime

    # Validar formato de fecha y hora
    try:
        nueva_fecha_hora = datetime.strptime(
            f"{nueva_fecha} {nueva_hora}", "%Y-%m-%d %H:%M"
        )
    except ValueError:
        print(
            "Formato incorrecto. Fecha: YYYY-MM-DD. Hora: HH:MM (24h). Ejemplo: 2025-12-01 18:00"
        )
        return
    # Validar que la nueva fecha/hora sea posterior a la actual
    ahora = datetime.now()
    if nueva_fecha_hora <= ahora:
        print("La nueva fecha y hora deben ser posteriores a la fecha y hora actual.")
        return
    resultado = coleccion_partidos.update_one(
        {"_id": partido_id}, {"$set": {"fecha": nueva_fecha, "hora": nueva_hora}}
    )
    if resultado.matched_count > 0:
        print(f"Fecha y hora actualizadas para el partido con _id: {partido_id}")
    else:
        print(f"No se encontró el partido con _id: {partido_id}")


def sacar_saldo_usuario(usuario_id, cantidad):
    usuario = coleccion_usuarios.find_one({"_id": usuario_id})
    if usuario:
        if usuario["saldo"] >= cantidad:
            nuevo_saldo = usuario["saldo"] - cantidad
            coleccion_usuarios.update_one(
                {"_id": usuario_id}, {"$set": {"saldo": nuevo_saldo}}
            )
            print(f"Saldo actualizado. Nuevo saldo: {nuevo_saldo}")
        else:
            print("Saldo insuficiente.")
    else:
        print("Usuario no encontrado.")


def ingresar_saldo_usuario(usuario_id, cantidad):
    usuario = coleccion_usuarios.find_one({"_id": usuario_id})
    if usuario:
        nuevo_saldo = usuario["saldo"] + cantidad
        coleccion_usuarios.update_one(
            {"_id": usuario_id}, {"$set": {"saldo": nuevo_saldo}}
        )
        print(f"Saldo actualizado. Nuevo saldo: {nuevo_saldo}")


def eliminar_apuesta(apuesta_id):
    resultado = coleccion_apuestas.delete_one({"_id": apuesta_id})
    if resultado.deleted_count > 0:
        print(f"Apuesta con _id: {apuesta_id} eliminada.")
        # También eliminar la referencia de la apuesta en el usuario
        coleccion_usuarios.update_many({}, {"$pull": {"apuestas": apuesta_id}})
    else:
        print(f"No se encontró la apuesta con _id: {apuesta_id}")


def eliminar_partido(partido_id):
    partido = coleccion_partidos.find_one({"_id": partido_id})
    if not partido:
        print(f"No se encontró el partido con _id: {partido_id}")
        return
    from datetime import datetime

    fecha_hora_str = f"{partido['fecha']} {partido['hora']}"
    try:
        fecha_hora_partido = datetime.strptime(fecha_hora_str, "%Y-%m-%d %H:%M")
    except Exception as e:
        print(f"Error en el formato de fecha/hora del partido: {e}")
        return
    ahora = datetime.now()
    # Obtener apuestas relacionadas antes de borrarlas
    apuestas_relacionadas = list(coleccion_apuestas.find({"partido_id": partido_id}))
    apuestas_ids = [apuesta["_id"] for apuesta in apuestas_relacionadas]
    # Si el partido no ha comenzado, devolver el dinero de las apuestas
    if ahora < fecha_hora_partido:
        for apuesta in apuestas_relacionadas:
            usuario_id = apuesta["usuario_id"]
            cantidad = apuesta["cantidad"]
            coleccion_usuarios.update_one(
                {"_id": usuario_id}, {"$inc": {"saldo": cantidad}}
            )
            print(
                f"Devolviendo {cantidad}€ al usuario {usuario_id} por apuesta cancelada."
            )
    # Eliminar el partido
    resultado = coleccion_partidos.delete_one({"_id": partido_id})
    if resultado.deleted_count > 0:
        print(f"Partido con _id: {partido_id} eliminado.")
        # Eliminar las apuestas relacionadas con este partido
        apuestas_eliminadas = coleccion_apuestas.delete_many({"partido_id": partido_id})
        print(f"Apuestas eliminadas: {apuestas_eliminadas.deleted_count}")
        # Eliminar referencias de apuestas en los usuarios
        if apuestas_ids:
            # Actualizar usuarios para eliminar referencias a las apuestas borradas
            coleccion_usuarios.update_many(
                {},
                {"$pull": {"apuestas": {"$in": apuestas_ids}}},
            )
    else:
        print(f"No se pudo eliminar el partido con _id: {partido_id}")


def eliminar_usuario(usuario_id):
    usuario = coleccion_usuarios.find_one({"_id": usuario_id})
    if usuario:
        # Eliminar todas las apuestas del usuario
        apuestas_eliminadas = coleccion_apuestas.delete_many({"usuario_id": usuario_id})
        print(f"Apuestas eliminadas del usuario: {apuestas_eliminadas.deleted_count}")
        # Eliminar el usuario
        resultado = coleccion_usuarios.delete_one({"_id": usuario_id})
        if resultado.deleted_count > 0:
            print(f"Usuario con _id: {usuario_id} eliminado.")
        else:
            print(f"No se pudo eliminar el usuario con _id: {usuario_id}.")
    else:
        print("Usuario no encontrado.")


def obtener_partido(partido_id):
    partido = coleccion_partidos.find_one({"_id": partido_id})
    if partido:
        return partido
    else:
        print(f"No se encontró el partido con _id: {partido_id}")
        return None


def obtener_usuario(usuario_id):
    usuario = coleccion_usuarios.find_one({"_id": usuario_id})
    if usuario:
        return usuario
    else:
        print(f"No se encontró el usuario con _id: {usuario_id}")
        return None

def obtener_administrador(admin_id):
    admin = coleccion_administradores.find_one({"_id": admin_id})
    if admin:
        return admin
    else:
        print(f"No se encontró el administrador con _id: {admin_id}")
        return None

def obtener_apuesta(apuesta_id):
    apuesta = coleccion_apuestas.find_one({"_id": apuesta_id})
    if apuesta:
        return apuesta
    else:
        print(f"No se encontró la apuesta con _id: {apuesta_id}")
        return None


def cancelar_apuesta(usuario_id, apuesta_id):
    apuesta = coleccion_apuestas.find_one({"_id": apuesta_id, "usuario_id": usuario_id})
    if not apuesta:
        print(
            f"No se encontró la apuesta con _id: {apuesta_id} para el usuario {usuario_id}"
        )
        return
    partido = coleccion_partidos.find_one({"_id": apuesta["partido_id"]})
    if not partido:
        print(f"No se encontró el partido asociado a la apuesta con _id: {apuesta_id}")
        return
    from datetime import datetime

    fecha_hora_str = f"{partido['fecha']} {partido['hora']}"
    try:
        fecha_hora_partido = datetime.strptime(fecha_hora_str, "%Y-%m-%d %H:%M")
    except Exception as e:
        print(f"Error en el formato de fecha/hora del partido: {e}")
        return
    ahora = datetime.now()
    if ahora >= fecha_hora_partido:
        print("No se puede cancelar la apuesta: el partido ya ha comenzado.")
        return
    # Devolver el dinero al usuario
    cantidad = apuesta["cantidad"]
    coleccion_usuarios.update_one({"_id": usuario_id}, {"$inc": {"saldo": cantidad}})
    # Eliminar la apuesta
    resultado = coleccion_apuestas.delete_one({"_id": apuesta_id})
    if resultado.deleted_count > 0:
        print(
            f"Apuesta con _id: {apuesta_id} cancelada y {cantidad}€ devueltos al usuario {usuario_id}."
        )
        # Eliminar referencia de la apuesta en el usuario
        coleccion_usuarios.update_one(
            {"_id": usuario_id}, {"$pull": {"apuestas": apuesta_id}}
        )
    else:
        print(f"No se pudo cancelar la apuesta con _id: {apuesta_id}.")


def cambiar_nombre_usuario(usuario_id, nuevo_nombre):
    resultado = coleccion_usuarios.update_one(
        {"_id": usuario_id}, {"$set": {"usuario": nuevo_nombre}}
    )
    if resultado.matched_count > 0:
        print(f"Nombre de usuario actualizado para el usuario con _id: {usuario_id}")
    else:
        print(f"No se encontró el usuario con _id: {usuario_id}")


def cambiar_contrasenia_usuario(usuario_id, nueva_contrasenia):
    resultado = coleccion_usuarios.update_one(
        {"_id": usuario_id}, {"$set": {"contrasenia": nueva_contrasenia}}
    )
    if resultado.matched_count > 0:
        print(f"Contraseña actualizada para el usuario con _id: {usuario_id}")
    else:
        print(f"No se encontró el usuario con _id: {usuario_id}")
