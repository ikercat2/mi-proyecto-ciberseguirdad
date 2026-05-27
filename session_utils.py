"""
session_utils.py — Token de sesion cifrado con Fernet.

Clave efimera: se genera una vez al arrancar el proceso.
- Los tokens sobreviven recargas de pagina (misma clave en memoria).
- Al reiniciar el servidor la clave cambia => todos los tokens quedan invalidos
  y se pide credenciales de nuevo.
"""
import json
import time

from cryptography.fernet import Fernet

# Clave nueva cada vez que arranca el proceso (no se persiste en disco)
_fernet = Fernet(Fernet.generate_key())

# Duracion maxima del token aunque el navegador no se cierre (8 horas)
_TTL_SEG = 8 * 3600


def crear_token(usuario: dict) -> str:
    """Crea un token cifrado con los datos basicos del usuario."""
    payload = {
        "u": {
            "id":               usuario["id"],
            "nombre":           usuario["nombre"],
            "email":            usuario["email"],
            "telefono":         usuario.get("telefono", ""),
            "fecha_nacimiento": usuario.get("fecha_nacimiento", ""),
            "tarjeta_enc":      usuario.get("tarjeta_enc", ""),
        },
        "exp": time.time() + _TTL_SEG,
    }
    return _fernet.encrypt(json.dumps(payload).encode()).decode()


def leer_token(token: str) -> dict | None:
    """Descifra el token. Retorna el dict del usuario o None si es invalido/expirado."""
    try:
        payload = json.loads(_fernet.decrypt(token.encode()))
        if time.time() > payload.get("exp", 0):
            return None
        return payload["u"]
    except Exception:
        return None
