"""
session_utils.py — Token de sesion cifrado con Fernet.

El token es un JSON cifrado que contiene los datos basicos del usuario
y un timestamp de expiracion. Se guarda como cookie de sesion en el
navegador (sin fecha de expiracion => se borra al cerrar el navegador).
"""
import json
import os
import time

from cryptography.fernet import Fernet
from dotenv import load_dotenv

_base = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(_base, ".env"))
_local = os.path.join(_base, ".env.local")
if os.path.exists(_local):
    load_dotenv(_local, override=True)

_RAW_KEY = os.environ.get("FERNET_KEY")
_fernet  = Fernet(_RAW_KEY.encode()) if _RAW_KEY else Fernet(Fernet.generate_key())

# Duracion maxima del token aunque el navegador no se cierre (12 horas)
_TTL_SEG = 12 * 3600


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
