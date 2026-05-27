"""
db.py  —  Capa de base de datos para el sistema de usuarios.
Ahora usa MySQL remoto en lugar de SQLite local.

Seguridad implementada:
  - Contraseñas: bcrypt (salt automático, factor de costo 12)
  - Datos crediticios: cifrado simétrico Fernet (AES-128-CBC + HMAC)
  - Rate limiting: bloqueo tras 5 intentos fallidos por 15 minutos
  - Replay attacks OTP: tabla otp_usados con ventana de 90 s
"""

import os
import re
import mysql.connector
from dotenv import load_dotenv

_base_dir = os.path.dirname(__file__)
load_dotenv(os.path.join(_base_dir, ".env"))

_env_local = os.path.join(_base_dir, ".env.local")
if os.path.exists(_env_local):
    load_dotenv(_env_local, override=True)
from datetime import datetime, timedelta, timezone

import bcrypt
import pyotp
from cryptography.fernet import Fernet

# ---------------------------------------------------------------------------
# Configuración de conexión MySQL
# ---------------------------------------------------------------------------

DB_HOST = os.environ["DB_HOST"]
DB_PORT = int(os.environ.get("DB_PORT", 3306))
DB_USER = os.environ["DB_USER"]
DB_PASS = os.environ["DB_PASS"]
DB_NAME = os.environ["DB_NAME"]

# La clave Fernet DEBE venir de una variable de entorno en producción.
_RAW_KEY = os.environ.get("FERNET_KEY")
if _RAW_KEY:
    fernet = Fernet(_RAW_KEY.encode())
else:
    _generated = Fernet.generate_key()
    print(
        f"[db.py] ADVERTENCIA: No se encontró FERNET_KEY. "
        f"Guarda esta clave en tu archivo .env:\n"
        f"  FERNET_KEY={_generated.decode()}"
    )
    fernet = Fernet(_generated)

MAX_INTENTOS = 5
BLOQUEO_MINUTOS = 15
OTP_VENTANA_SEG = 90  # ventana anti-replay (3 períodos TOTP de 30 s)


# ---------------------------------------------------------------------------
# Conexión
# ---------------------------------------------------------------------------

def _conn():
    return mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
    )


# ---------------------------------------------------------------------------
# Creación de tablas
# ---------------------------------------------------------------------------

def init_db() -> None:
    """Crea las tablas si no existen. Llamar al inicio de la app."""
    conn = _conn()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id                INT AUTO_INCREMENT PRIMARY KEY,
            nombre            VARCHAR(255)  NOT NULL,
            email             VARCHAR(255)  UNIQUE NOT NULL,
            telefono          VARCHAR(50),
            fecha_nacimiento  VARCHAR(20),
            direccion         TEXT,
            grupo_sanguineo   VARCHAR(10),
            alergias          TEXT,
            tarjeta_tipo      VARCHAR(50),
            tarjeta_enc       TEXT,
            tarjeta_venc      TEXT,
            contrasena_hash   TEXT          NOT NULL,
            totp_secret       VARCHAR(64),
            totp_activo       TINYINT       DEFAULT 0,
            intentos_fallidos INT           DEFAULT 0,
            bloqueado_hasta   VARCHAR(50),
            creado_en         DATETIME      DEFAULT (UTC_TIMESTAMP())
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS otp_usados (
            id          INT AUTO_INCREMENT PRIMARY KEY,
            usuario_id  INT         NOT NULL,
            otp_code    VARCHAR(10) NOT NULL,
            usado_en    DATETIME    DEFAULT (UTC_TIMESTAMP()),
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
        )
    """)

    try:
        cursor.execute("""
            CREATE INDEX idx_otp_usuario ON otp_usados (usuario_id, usado_en)
        """)
    except mysql.connector.Error:
        pass  # El índice ya existe

    conn.commit()
    cursor.close()
    conn.close()


# ---------------------------------------------------------------------------
# Política de contraseñas
# ---------------------------------------------------------------------------

POLITICA_CONTRASENA = (
    "Mínimo 8 caracteres, al menos: "
    "1 mayúscula, 1 minúscula, 1 dígito, 1 carácter especial (!@#$%^&*)"
)


def validar_contrasena(pwd: str) -> tuple[bool, str]:
    """Retorna (ok, mensaje). ok=True si cumple la política."""
    if len(pwd) < 8:
        return False, "Debe tener al menos 8 caracteres."
    if not re.search(r"[A-Z]", pwd):
        return False, "Debe contener al menos una mayúscula."
    if not re.search(r"[a-z]", pwd):
        return False, "Debe contener al menos una minúscula."
    if not re.search(r"\d", pwd):
        return False, "Debe contener al menos un dígito."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", pwd):
        return False, "Debe contener al menos un carácter especial."
    return True, "OK"


def _hash_pwd(pwd: str) -> str:
    return bcrypt.hashpw(pwd.encode(), bcrypt.gensalt(rounds=10)).decode()

def _check_pwd(pwd: str, hashed: str) -> bool:
    return bcrypt.checkpw(pwd.encode(), hashed.encode())


# ---------------------------------------------------------------------------
# Cifrado de datos sensibles
# ---------------------------------------------------------------------------

def cifrar(texto: str) -> str:
    return fernet.encrypt(texto.encode()).decode()


def descifrar(token: str) -> str:
    return fernet.decrypt(token.encode()).decode()


# ---------------------------------------------------------------------------
# Registro de usuarios
# ---------------------------------------------------------------------------

def registrar_usuario(datos: dict) -> tuple[bool, str]:
    """
    Registra un nuevo usuario.
    Retorna (éxito, mensaje_o_totp_secret).
    """
    ok, msg = validar_contrasena(datos["contrasena"])
    if not ok:
        return False, f"Contraseña inválida: {msg}"

    totp_secret = pyotp.random_base32()

    try:
        conn = _conn()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO usuarios (
                nombre, email, telefono, fecha_nacimiento, direccion,
                grupo_sanguineo, alergias,
                tarjeta_tipo, tarjeta_enc, tarjeta_venc,
                contrasena_hash, totp_secret
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                datos["nombre"],
                datos["email"].lower().strip(),
                datos.get("telefono", ""),
                datos.get("fecha_nacimiento", ""),
                datos.get("direccion", ""),
                datos.get("grupo_sanguineo", ""),
                datos.get("alergias", ""),
                datos.get("tarjeta_tipo", ""),
                cifrar(datos["tarjeta_numero"]) if datos.get("tarjeta_numero") else "",
                cifrar(datos["tarjeta_venc"])   if datos.get("tarjeta_venc")   else "",
                _hash_pwd(datos["contrasena"]),
                totp_secret,
            ),
        )
        conn.commit()
        cursor.close()
        conn.close()
        return True, totp_secret
    except mysql.connector.IntegrityError:
        return False, "El correo electrónico ya está registrado."


# ---------------------------------------------------------------------------
# Autenticación
# ---------------------------------------------------------------------------

def _ahora_utc() -> datetime:
    return datetime.now(timezone.utc)


def obtener_usuario(email: str) -> dict | None:
    conn = _conn()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM usuarios WHERE email = %s",
        (email.lower().strip(),)
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row


def esta_bloqueado(usuario: dict) -> tuple[bool, str]:
    if usuario["bloqueado_hasta"]:
        hasta = datetime.fromisoformat(usuario["bloqueado_hasta"])
        if hasta.tzinfo is None:
            hasta = hasta.replace(tzinfo=timezone.utc)
        if _ahora_utc() < hasta:
            restante = int((hasta - _ahora_utc()).total_seconds() / 60) + 1
            return True, f"Cuenta bloqueada. Intenta en {restante} min."
    return False, ""


def _registrar_fallo(usuario_id: int) -> None:
    conn = _conn()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "UPDATE usuarios SET intentos_fallidos = intentos_fallidos + 1 WHERE id = %s",
        (usuario_id,)
    )
    cursor.execute(
        "SELECT intentos_fallidos FROM usuarios WHERE id = %s",
        (usuario_id,)
    )
    row = cursor.fetchone()
    if row["intentos_fallidos"] >= MAX_INTENTOS:
        hasta = (_ahora_utc() + timedelta(minutes=BLOQUEO_MINUTOS)).isoformat()
        cursor.execute(
            "UPDATE usuarios SET bloqueado_hasta = %s WHERE id = %s",
            (hasta, usuario_id)
        )
    conn.commit()
    cursor.close()
    conn.close()


def _limpiar_intentos(usuario_id: int) -> None:
    conn = _conn()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE usuarios SET intentos_fallidos = 0, bloqueado_hasta = NULL WHERE id = %s",
        (usuario_id,)
    )
    conn.commit()
    cursor.close()
    conn.close()


def _otp_ya_usado(usuario_id: int, otp_code: str) -> bool:
    """Detecta replay attacks: rechaza OTPs que ya se usaron en la ventana actual."""
    limite = (_ahora_utc() - timedelta(seconds=OTP_VENTANA_SEG)).isoformat()
    conn = _conn()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT 1 FROM otp_usados
        WHERE usuario_id = %s AND otp_code = %s AND usado_en > %s
        """,
        (usuario_id, otp_code, limite)
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row is not None


def _marcar_otp_usado(usuario_id: int, otp_code: str) -> None:
    conn = _conn()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO otp_usados (usuario_id, otp_code) VALUES (%s,%s)",
        (usuario_id, otp_code)
    )
    limite = (_ahora_utc() - timedelta(seconds=OTP_VENTANA_SEG * 2)).isoformat()
    cursor.execute(
        "DELETE FROM otp_usados WHERE usuario_id = %s AND usado_en < %s",
        (usuario_id, limite)
    )
    conn.commit()
    cursor.close()
    conn.close()


class ResultadoAuth:
    OK = "ok"
    CREDENCIALES = "credenciales_invalidas"
    BLOQUEADO = "cuenta_bloqueada"
    OTP_INVALIDO = "otp_invalido"
    OTP_REPLAY = "otp_replay"
    OTP_NO_CONFIG = "otp_no_configurado"


def autenticar(email: str, contrasena: str, otp_code: str) -> tuple[str, str]:
    """
    Valida email + contraseña + OTP.
    Retorna (ResultadoAuth.*, mensaje_legible).
    """
    usuario = obtener_usuario(email)
    if not usuario:
        return ResultadoAuth.CREDENCIALES, "Credenciales inválidas."

    bloqueado, msg = esta_bloqueado(usuario)
    if bloqueado:
        return ResultadoAuth.BLOQUEADO, msg

    if not _check_pwd(contrasena, usuario["contrasena_hash"]):
        _registrar_fallo(usuario["id"])
        restantes = MAX_INTENTOS - usuario["intentos_fallidos"] - 1
        if restantes > 0:
            return ResultadoAuth.CREDENCIALES, f"Credenciales inválidas. {restantes} intentos restantes."
        return ResultadoAuth.CREDENCIALES, "Credenciales inválidas. Cuenta bloqueada temporalmente."

    if not usuario["totp_activo"]:
        return ResultadoAuth.OTP_NO_CONFIG, "Debes configurar tu OTP antes de iniciar sesión."

    if _otp_ya_usado(usuario["id"], otp_code):
        return ResultadoAuth.OTP_REPLAY, "OTP ya utilizado. Espera el próximo código."

    totp = pyotp.TOTP(usuario["totp_secret"])
    if not totp.verify(otp_code, valid_window=1):
        _registrar_fallo(usuario["id"])
        return ResultadoAuth.OTP_INVALIDO, "Código OTP incorrecto."

    _limpiar_intentos(usuario["id"])
    _marcar_otp_usado(usuario["id"], otp_code)
    return ResultadoAuth.OK, "Autenticación exitosa."


def activar_totp(email: str) -> None:
    """Marca el OTP como configurado/activo para el usuario."""
    conn = _conn()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE usuarios SET totp_activo = 1 WHERE email = %s",
        (email.lower().strip(),)
    )
    conn.commit()
    cursor.close()
    conn.close()


# ---------------------------------------------------------------------------
# Modulo de mercado
# ---------------------------------------------------------------------------

def init_mercado_db() -> None:
    """Crea las tablas del modulo de mercado si no existen."""
    conn = _conn()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS busquedas_mercado (
            id          INT AUTO_INCREMENT PRIMARY KEY,
            usuario_id  INT         NOT NULL,
            simbolo     VARCHAR(20) NOT NULL,
            buscado_en  DATETIME    DEFAULT (UTC_TIMESTAMP()),
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS simbolos_favoritos (
            id          INT AUTO_INCREMENT PRIMARY KEY,
            usuario_id  INT          NOT NULL,
            simbolo     VARCHAR(20)  NOT NULL,
            alias       VARCHAR(100),
            creado_en   DATETIME     DEFAULT (UTC_TIMESTAMP()),
            UNIQUE KEY  uq_usuario_simbolo (usuario_id, simbolo),
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
        )
    """)

    try:
        cursor.execute("""
            CREATE INDEX idx_busquedas_usuario
            ON busquedas_mercado (usuario_id, buscado_en)
        """)
    except mysql.connector.Error:
        pass

    conn.commit()
    cursor.close()
    conn.close()


def registrar_busqueda(usuario_id: int, simbolo: str) -> None:
    """Guarda una busqueda de simbolo por el usuario."""
    conn = _conn()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO busquedas_mercado (usuario_id, simbolo) VALUES (%s, %s)",
        (usuario_id, simbolo.upper())
    )
    conn.commit()
    cursor.close()
    conn.close()


def obtener_busquedas_recientes(usuario_id: int, limite: int = 8) -> list[dict]:
    """Retorna los simbolos mas recientes buscados por el usuario (sin duplicados)."""
    conn = _conn()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT simbolo, MAX(buscado_en) AS ultima_vez
        FROM busquedas_mercado
        WHERE usuario_id = %s
        GROUP BY simbolo
        ORDER BY ultima_vez DESC
        LIMIT %s
        """,
        (usuario_id, limite)
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def obtener_usuarios_para_excel() -> list[dict]:
    """Retorna datos publicos de todos los usuarios para exportar a Excel."""
    conn = _conn()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT nombre, email, telefono, fecha_nacimiento,
               grupo_sanguineo, alergias, creado_en
        FROM usuarios
        ORDER BY creado_en DESC
        """
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows
