"""
migrar.py — Migra los datos de usuarios.db (SQLite) a MySQL.
Ejecutar UNA sola vez: python migrar.py
"""

import sqlite3
import mysql.connector
from datetime import datetime


def convertir_fecha(fecha_str):
    """Convierte '2026-05-01T17:22:34Z' al formato MySQL '2026-05-01 17:22:34'."""
    if not fecha_str:
        return None
    try:
        dt = datetime.fromisoformat(fecha_str.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        return fecha_str


# --- Configuración ---
SQLITE_PATH = "usuarios.db"
MYSQL_HOST  = "172.31.47.222"
MYSQL_USER  = "nuu_user"
MYSQL_PASS  = "MiClave2025!"
MYSQL_DB    = "nuu_db"

# --- Conexiones ---
sqlite_conn = sqlite3.connect(SQLITE_PATH)
sqlite_conn.row_factory = sqlite3.Row
sqlite_cur  = sqlite_conn.cursor()

mysql_conn  = mysql.connector.connect(
    host=MYSQL_HOST, user=MYSQL_USER,
    password=MYSQL_PASS, database=MYSQL_DB
)
mysql_cur = mysql_conn.cursor()

# --- Migrar usuarios ---
sqlite_cur.execute("SELECT * FROM usuarios")
usuarios = sqlite_cur.fetchall()
print(f"Usuarios encontrados en SQLite: {len(usuarios)}")

migrados = 0
saltados = 0

for u in usuarios:
    try:
        mysql_cur.execute("""
            INSERT INTO usuarios (
                id, nombre, email, telefono, fecha_nacimiento, direccion,
                grupo_sanguineo, alergias,
                tarjeta_tipo, tarjeta_enc, tarjeta_venc,
                contrasena_hash, totp_secret, totp_activo,
                intentos_fallidos, bloqueado_hasta, creado_en
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            u["id"], u["nombre"], u["email"], u["telefono"],
            u["fecha_nacimiento"], u["direccion"], u["grupo_sanguineo"],
            u["alergias"], u["tarjeta_tipo"], u["tarjeta_enc"],
            u["tarjeta_venc"], u["contrasena_hash"], u["totp_secret"],
            u["totp_activo"], u["intentos_fallidos"],
            convertir_fecha(u["bloqueado_hasta"]),
            convertir_fecha(u["creado_en"]),
        ))
        migrados += 1
        print(f"  OK Migrado: {u['email']}")
    except mysql.connector.IntegrityError:
        saltados += 1
        print(f"  Ya existe, saltado: {u['email']}")

# --- Migrar OTPs usados ---
sqlite_cur.execute("SELECT * FROM otp_usados")
otps = sqlite_cur.fetchall()
print(f"\nRegistros OTP encontrados: {len(otps)}")

for otp in otps:
    try:
        mysql_cur.execute("""
            INSERT INTO otp_usados (id, usuario_id, otp_code, usado_en)
            VALUES (%s,%s,%s,%s)
        """, (
            otp["id"], otp["usuario_id"], otp["otp_code"],
            convertir_fecha(otp["usado_en"]),
        ))
    except mysql.connector.IntegrityError:
        pass

mysql_conn.commit()

print(f"\n--- Resumen ---")
print(f"Usuarios migrados : {migrados}")
print(f"Usuarios saltados : {saltados}")
print(f"OTPs migrados     : {len(otps)}")
print("Migracion completada.")

sqlite_cur.close()
sqlite_conn.close()
mysql_cur.close()
mysql_conn.close()
