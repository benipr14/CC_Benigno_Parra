import mongomock
import pytest

# Importar el módulo que vamos a testear
from Hitos.Hito2 import funciones


@pytest.fixture(autouse=True)
def mongo_db():
    """Fixture que inicializa un mongomock DB y la inyecta en el módulo funciones."""
    client = mongomock.MongoClient()
    funciones.init_db(client, db_name="CC")
    yield


# --- Helpers para tests -------------------------------------------------
def crear_usuario(nombre="user", contrasenia="pw", saldo=100.0):
    uid = funciones.insertar_usuario(nombre, contrasenia, saldo)
    return uid


def crear_partido(local="Local", visitante="Visitante", f_fecha="2026-12-01", f_hora="12:00", cuotas=(1.5, 3.0, 2.5)):
    cuota_local, cuota_empate, cuota_visitante = cuotas
    pid = funciones.insertar_partido(
        local, visitante, cuota_local, cuota_empate, cuota_visitante, f_fecha, f_hora, "Pendiente"
    )
    return pid


def realizar_apuesta(usuario_id, partido_id, elegido, cantidad):
    return funciones.hacer_apuesta(usuario_id, partido_id, elegido, cantidad)

def insertar_administrador(usuario="usuario", contrasenia="contrasenia", rol="admin"):
    return funciones.insertar_administrador(usuario, contrasenia, rol)

def cambiar_fecha_partido(partido_id, fecha="2020-01-01", hora="12:00"):
    funciones.coleccion_partidos.update_one(
        {"_id": partido_id}, {"$set": {"fecha": fecha, "hora": hora}}
    )


# --- Tests ---------------------------------------------------------------
def test_crear_usuario():
    usuario_id = crear_usuario("usuario", "contrasenia", 100.0)
    assert usuario_id is not None
    usuario = funciones.obtener_usuario(usuario_id)
    assert usuario["usuario"] == "usuario"
    assert usuario["contrasenia"] == "contrasenia"
    assert usuario["saldo"] == 100.0
    assert usuario["apuestas"] == []

def test_crear_partido():
    partido_id = crear_partido("EquipoA", "EquipoB", "2025-11-30", "15:00", (2.0, 3.5, 4.0))
    assert partido_id is not None
    partido = funciones.obtener_partido(partido_id)
    assert partido["local"] == "EquipoA"
    assert partido["visitante"] == "EquipoB"
    assert partido["cuota_local"] == 2.0
    assert partido["cuota_empate"] == 3.5
    assert partido["cuota_visitante"] == 4.0
    assert partido["fecha"] == "2025-11-30"
    assert partido["hora"] == "15:00"
    assert partido["resultado"] == "Pendiente"

def test_insertar_administrador():
    admin_id = insertar_administrador("adminuser", "adminpw", "admin")
    assert admin_id is not None
    admin = funciones.obtener_administrador(admin_id)
    assert admin["usuario"] == "adminuser"
    assert admin["contrasenia"] == "adminpw"
    assert admin["rol"] == "admin"

def test_hacer_apuesta():
    usuario_id = crear_usuario("apostador", "contrasenia", 100.0)
    partido_id = crear_partido("local", "visitante", "2024-12-01", "16:00", (2.0, 3.0, 4.0))

    # Probamos a hacer la apuesta pero no debe dejar porque el partido ya ha comenzado
    assert realizar_apuesta(usuario_id, partido_id, "1", 10.0) is None

    # Forzar que el partido no haya empezado
    cambiar_fecha_partido(partido_id, fecha="2099-01-01", hora="12:00")

    # Probamos con un partido inventado
    assert realizar_apuesta(usuario_id, "partido inventado", "1", 10.0) is None

    # Probamos con un usuario inventado
    assert realizar_apuesta("usuario inventado", partido_id, "1", 10.0) is None

    # Probamos con un usuario real pero sin saldo suficiente
    assert realizar_apuesta(usuario_id, partido_id, "1", 20000.0) is None

    # Ahora sí, hacemos una apuesta válida
    apuesta_id = realizar_apuesta(usuario_id, partido_id, "1", 20.0)
    apuesta = funciones.obtener_apuesta(apuesta_id)
    assert apuesta_id is not None
    assert apuesta["usuario_id"] == usuario_id
    assert apuesta["partido_id"] == partido_id
    assert apuesta["elegido"] == "1"
    assert apuesta["cantidad"] == 20.0

    # Comprobar que al usuario se le ha guardado la apuesta en el historial
    usuario = funciones.obtener_usuario(usuario_id)
    assert apuesta_id in usuario["apuestas"]

def test_termina_partido():
    partido_id = crear_partido("local", "visitante", "2026-12-01", "16:00", (2.0, 3.0, 4.0))
    usuario_id = crear_usuario("apostador", "pw", 100.0)
    _apuesta_id = realizar_apuesta(usuario_id, partido_id, "1", 30.0)

    #Intentamos finalizar el partido antes de que empiece pero no debe dejar
    assert funciones.termina_partido(partido_id, "1") is None

    # Forzamos que el partido ya haya pasado
    cambiar_fecha_partido(partido_id, fecha="2020-01-01", hora="12:00")

    #Probamos con un partido inventado
    assert funciones.termina_partido("partido_inexistente", "1") is None

    #Probamos a poner un resultado erroneo, distinto de "1", "X, "2"
    assert funciones.termina_partido(partido_id, "3") is None

    # Ahora sí, terminamos el partido con un resultado válido
    funciones.termina_partido(partido_id, "1")
    partido = funciones.obtener_partido(partido_id)
    assert partido["resultado"] == "1"
    # Comprobamos que el usuario gane el dinero del partido si acierta
    apuesta = funciones.obtener_apuesta(_apuesta_id)
    if apuesta["usuario_id"] == usuario_id and apuesta["elegido"] == "1":
        usuario = funciones.obtener_usuario(usuario_id)
        # saldo inicial 100 - 30 (apuesta) + 30*2.0 = 130
        assert usuario["saldo"] == pytest.approx(130.0)
    #Compruebo que si no acierta, pierde el dinero
    else:
        usuario = funciones.obtener_usuario(usuario_id)
        # saldo inicial 100 - 30 (apuesta) = 70
        assert usuario["saldo"] == pytest.approx(70.0)

def test_cambiar_cuota_partido():
    partido_id = crear_partido("local", "visitante", "2026-12-01", "16:00", (2.0, 3.0, 4.0))
    
    # Probamos una condicion inválida, distinta de "1", "X", "2"
    assert funciones.cambiar_cuota_partido(partido_id, "3", 5.0) is None

    #Probamos con un partido inexistente
    assert funciones.cambiar_cuota_partido("partido_inexistente", "1", 5.0) is None

    # Cambiar cuota local
    funciones.cambiar_cuota_partido(partido_id, "1", 2.5)
    partido = funciones.obtener_partido(partido_id)
    assert partido["cuota_local"] == 2.5
    
    # Cambiar cuota empate
    funciones.cambiar_cuota_partido(partido_id, "X", 3.5)
    partido = funciones.obtener_partido(partido_id)
    assert partido["cuota_empate"] == 3.5
    
    # Cambiar cuota visitante
    funciones.cambiar_cuota_partido(partido_id, "2", 4.5)
    partido = funciones.obtener_partido(partido_id)
    assert partido["cuota_visitante"] == 4.5

def test_cambiar_fecha_partido():
    partido_id = crear_partido("local", "visitante", "2026-12-01", "16:00", (2.0, 3.0, 4.0))
    
    #Probamos con un formato incorrecto de fecha
    assert funciones.cambiar_fecha_partido(partido_id, "2026/12/01", "16:00") is None
    
    # Comprobamos que no se puede cambiar a una fecha anterior a la actual
    assert funciones.cambiar_fecha_partido(partido_id, "2022-01-01", "12:00") is None

    #Probamos con un partido inexistente
    assert funciones.cambiar_fecha_partido("partido_inexistente", "2027-01-01", "12:00") is None

    # Cambiamos fecha y hora correctamente
    funciones.cambiar_fecha_partido(partido_id, "2027-01-15", "18:30")
    partido = funciones.obtener_partido(partido_id)
    assert partido["fecha"] == "2027-01-15"
    assert partido["hora"] == "18:30"

def test_sacar_saldo_usuario():
    usuario_id = crear_usuario("usuario_saldo", "pw", 150.0)

    # Probamos con un usuario inexistente
    assert funciones.sacar_saldo_usuario("usuario_inexistente", 50.0) is None

    # Intentar sacar más de lo que tiene
    assert funciones.sacar_saldo_usuario(usuario_id, 200.0) is None
    usuario = funciones.obtener_usuario(usuario_id)
    
    # El saldo no debe haber cambiado
    assert usuario["saldo"] == pytest.approx(150.0)

    # Sacar una cantidad válida
    funciones.sacar_saldo_usuario(usuario_id, 50.0)
    usuario = funciones.obtener_usuario(usuario_id)
    assert usuario["saldo"] == pytest.approx(100.0)

def test_ingresar_saldo_usuario():
    usuario_id = crear_usuario("usuario_ingreso", "pw", 80.0)

    # Probamos con un usuario inexistente
    assert funciones.ingresar_saldo_usuario("usuario_inexistente", 40.0) is None

    # Ingresar saldo
    funciones.ingresar_saldo_usuario(usuario_id, 40.0)
    usuario = funciones.obtener_usuario(usuario_id)
    assert usuario["saldo"] == pytest.approx(120.0)

def test_eliminar_apuesta():
    usuario_id = crear_usuario("usuario_eliminar_apuesta", "pw", 100.0)
    partido_id = crear_partido()
    apuesta_id = realizar_apuesta(usuario_id, partido_id, "1", 25.0)

    # Probamos con una apuesta inexistente
    assert funciones.eliminar_apuesta("apuesta_inexistente") is None

    # Eliminar la apuesta correctamente
    funciones.eliminar_apuesta(apuesta_id)
    assert funciones.obtener_apuesta(apuesta_id) is None

    # Comprobar que la referencia a la apuesta se ha eliminado del usuario
    usuario = funciones.obtener_usuario(usuario_id)
    assert apuesta_id not in usuario["apuestas"]

def test_eliminar_partido():
    partido_id = crear_partido()
    usuario_id = crear_usuario("usuario_con_apuesta", "pw", 100.0)
    apuesta_id = realizar_apuesta(usuario_id, partido_id, "1", 30.0)

    # Probamos con un partido inexistente
    assert funciones.eliminar_partido("partido_inexistente") is None

    # Eliminar el partido correctamente
    funciones.eliminar_partido(partido_id)
    assert funciones.obtener_partido(partido_id) is None

    # Comprobar que las apuestas relacionada también se ha eliminado
    assert funciones.obtener_apuesta(apuesta_id) is None

    # Al no haber comenzado el partido, el saldo del usuario debe ser restaurado
    usuario = funciones.obtener_usuario(usuario_id)
    assert usuario["saldo"] == pytest.approx(100.0)

    # Comprobar que la referencia a la apuesta se ha eliminado del usuario
    usuario = funciones.obtener_usuario(usuario_id)
    assert apuesta_id not in usuario["apuestas"]

def test_eliminar_usuario():
    usuario_id = crear_usuario("usuario_a_eliminar", "pw", 100.0)
    partido_id = crear_partido()
    apuesta_id = realizar_apuesta(usuario_id, partido_id, "1", 20.0)

    # Probamos con un usuario inexistente
    assert funciones.eliminar_usuario("usuario_inexistente") is None

    # Eliminar el usuario correctamente
    funciones.eliminar_usuario(usuario_id)
    assert funciones.obtener_usuario(usuario_id) is None

    # Comprobar que las apuestas del usuario también se han eliminado
    assert funciones.obtener_apuesta(apuesta_id) is None

def test_obtener_partido():
    partido_id = crear_partido("EquipoX", "EquipoY", "2025-10-10", "14:00", (2.2, 3.3, 4.4))

    # Probamos con un partido inexistente
    assert funciones.obtener_partido("partido_inexistente") is None

    # Obtener el partido correctamente
    partido = funciones.obtener_partido(partido_id)
    assert partido is not None
    assert partido["local"] == "EquipoX"
    assert partido["visitante"] == "EquipoY"
    assert partido["cuota_local"] == 2.2
    assert partido["cuota_empate"] == 3.3
    assert partido["cuota_visitante"] == 4.4
    assert partido["fecha"] == "2025-10-10"
    assert partido["hora"] == "14:00"
    assert partido["resultado"] == "Pendiente"

def test_obtener_usuario():
    usuario_id = crear_usuario("usuario_test", "pw_test", 200.0)

    # Probamos con un usuario inexistente
    assert funciones.obtener_usuario("usuario_inexistente") is None

    # Obtener el usuario correctamente
    usuario = funciones.obtener_usuario(usuario_id)
    assert usuario is not None
    assert usuario["usuario"] == "usuario_test"
    assert usuario["contrasenia"] == "pw_test"
    assert usuario["saldo"] == 200.0
    assert usuario["apuestas"] == []

def test_obtener_administrador():
    admin_id = insertar_administrador("admin_test", "admin_pw", "admin")

    # Probamos con un administrador inexistente
    assert funciones.obtener_administrador("admin_inexistente") is None

    # Obtener el administrador correctamente
    admin = funciones.obtener_administrador(admin_id)
    assert admin is not None
    assert admin["usuario"] == "admin_test"
    assert admin["contrasenia"] == "admin_pw"
    assert admin["rol"] == "admin"

def test_obtener_apuesta():
    usuario_id = crear_usuario("usuario_apuesta", "pw", 150.0)
    partido_id = crear_partido()
    apuesta_id = realizar_apuesta(usuario_id, partido_id, "X", 40.0)

    # Probamos con una apuesta inexistente
    assert funciones.obtener_apuesta("apuesta_inexistente") is None

    # Obtener la apuesta correctamente
    apuesta = funciones.obtener_apuesta(apuesta_id)
    assert apuesta is not None
    assert apuesta["usuario_id"] == usuario_id
    assert apuesta["partido_id"] == partido_id
    assert apuesta["elegido"] == "X"
    assert apuesta["cantidad"] == 40.0    

def test_cancelar_apuesta():
    usuario_id = crear_usuario("usuario_cancelar", "pw", 120.0)
    partido_id = crear_partido()
    apuesta_id = realizar_apuesta(usuario_id, partido_id, "2", 50.0)

    # Probamos con una apuesta inexistente
    assert funciones.cancelar_apuesta(usuario_id, "apuesta_inexistente") is None

    # Cancelar la apuesta correctamente
    funciones.cancelar_apuesta(usuario_id, apuesta_id)
    assert funciones.obtener_apuesta(apuesta_id) is None

    # Comprobar que la referencia a la apuesta se ha eliminado del usuario
    usuario = funciones.obtener_usuario(usuario_id)
    assert apuesta_id not in usuario["apuestas"]

    # Comprobar que el saldo del usuario se ha restaurado
    assert usuario["saldo"] == pytest.approx(120.0)

    # Ahora probamos a cancelar una apuesta de un partido que ya ha comenzado
    apuesta_id2 = realizar_apuesta(usuario_id, partido_id, "1", 30.0)
    # Forzar que el partido ya haya comenzado
    cambiar_fecha_partido(partido_id, fecha="2020-01-01", hora="12:00")
    assert funciones.cancelar_apuesta(usuario_id, apuesta_id2) is None    

def test_cambiar_nombre_usuario():
    usuario_id = crear_usuario("usuario_cambiar", "pw", 90.0)

    # Probamos con un usuario inexistente
    assert funciones.cambiar_nombre_usuario("usuario_inexistente", "nuevo_nombre") is None

    # Cambiar el nombre correctamente
    funciones.cambiar_nombre_usuario(usuario_id, "nuevo_usuario")
    usuario = funciones.obtener_usuario(usuario_id)
    assert usuario["usuario"] == "nuevo_usuario"

def test_cambiar_contrasenia_usuario():
    usuario_id = crear_usuario("usuario_contra", "pw_vieja", 90.0)

    # Probamos con un usuario inexistente
    assert funciones.cambiar_contrasenia_usuario("usuario_inexistente", "nueva_pw") is None

    # Cambiar la contraseña correctamente
    funciones.cambiar_contrasenia_usuario(usuario_id, "nueva_pw")
    usuario = funciones.obtener_usuario(usuario_id)
    assert usuario["contrasenia"] == "nueva_pw"