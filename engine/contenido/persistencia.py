"""Persistencia de la capa de contenido (SQLite — simple a propósito).

Regla de CONTENIDO.md: desde el primer commit de esta capa, TODA
simulación se guarda. Una sola base, tres tablas. La ruta se puede
mover con la variable de entorno ENJAMBRE_DB (los tests usan una
temporal; en Render apuntará al disco persistente).
"""

import hashlib
import json
import os
import secrets
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

RUTA_DEFECTO = Path(__file__).parent.parent / "datos" / "enjambre.db"

ESQUEMA = """
CREATE TABLE IF NOT EXISTS simulaciones (
  id            TEXT PRIMARY KEY,
  titular       TEXT NOT NULL,
  fuente        TEXT,
  fecha         TEXT NOT NULL,
  seed          INTEGER NOT NULL,
  resumen_json  TEXT NOT NULL,
  lideres_json  TEXT NOT NULL,
  serie_precios TEXT NOT NULL,
  frames_ref    TEXT,
  destacada     INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS titulares (
  id         TEXT PRIMARY KEY,
  titular    TEXT NOT NULL,
  fuente     TEXT NOT NULL,
  fecha      TEXT NOT NULL,
  simbolos   TEXT,
  veredicto  TEXT NOT NULL,
  motivo     TEXT,
  sim_id     TEXT REFERENCES simulaciones(id)
);
CREATE TABLE IF NOT EXISTS suscriptores (
  email      TEXT PRIMARY KEY,
  fecha_alta TEXT NOT NULL,
  origen     TEXT,
  activo     INTEGER DEFAULT 1,
  token_baja TEXT NOT NULL
);
"""


def ahora_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def conectar(ruta: str | Path | None = None) -> sqlite3.Connection:
    """Abre (y crea si no existe) la base con su esquema."""
    ruta = Path(ruta or os.environ.get("ENJAMBRE_DB", RUTA_DEFECTO))
    ruta.parent.mkdir(parents=True, exist_ok=True)
    conexion = sqlite3.connect(ruta)
    conexion.row_factory = sqlite3.Row
    conexion.executescript(ESQUEMA)
    return conexion


# ---------- simulaciones ----------

def id_simulacion(titular: str, seed: int) -> str:
    """Mismo criterio que la caché de cerebros: sha256(titular|seed)."""
    return hashlib.sha256(f"{titular}|{seed}".encode()).hexdigest()[:16]


def guardar_simulacion(
    conexion, *, titular: str, fuente: str, seed: int,
    resumen: dict, lideres: list[dict], serie_precios: list[float],
    frames_ref: str | None = None, destacada: bool = False,
) -> str:
    """Guarda (o reemplaza) una simulación completa. Devuelve su id."""
    sim_id = id_simulacion(titular, seed)
    conexion.execute(
        """INSERT OR REPLACE INTO simulaciones
           (id, titular, fuente, fecha, seed, resumen_json, lideres_json,
            serie_precios, frames_ref, destacada)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            sim_id, titular, fuente, ahora_iso(), seed,
            json.dumps(resumen, ensure_ascii=False),
            json.dumps(lideres, ensure_ascii=False),
            json.dumps([round(p, 4) for p in serie_precios]),
            frames_ref, int(destacada),
        ),
    )
    conexion.commit()
    return sim_id


def obtener_simulacion(conexion, sim_id: str) -> dict | None:
    fila = conexion.execute("SELECT * FROM simulaciones WHERE id = ?", (sim_id,)).fetchone()
    if fila is None:
        return None
    datos = dict(fila)
    datos["resumen"] = json.loads(datos.pop("resumen_json"))
    datos["lideres"] = json.loads(datos.pop("lideres_json"))
    datos["serie_precios"] = json.loads(datos["serie_precios"])
    return datos


def listar_simulaciones(conexion, mes: str | None = None, limite: int = 50, solo_destacadas: bool = False) -> list[dict]:
    """Listado para el archivo. `mes` en formato 'AAAA-MM'."""
    condiciones, parametros = [], []
    if mes:
        condiciones.append("fecha LIKE ?")
        parametros.append(f"{mes}%")
    if solo_destacadas:
        condiciones.append("destacada = 1")
    donde = f"WHERE {' AND '.join(condiciones)}" if condiciones else ""
    filas = conexion.execute(
        f"SELECT id, titular, fuente, fecha, destacada FROM simulaciones {donde} "
        "ORDER BY fecha DESC LIMIT ?", (*parametros, limite),
    ).fetchall()
    return [dict(f) for f in filas]


def marcar_destacada(conexion, sim_id: str) -> None:
    conexion.execute("UPDATE simulaciones SET destacada = 1 WHERE id = ?", (sim_id,))
    conexion.commit()


# ---------- titulares (el log del portero) ----------

def registrar_titular(
    conexion, *, titular: str, fuente: str, veredicto: str,
    motivo: str = "", simbolos: str = "", sim_id: str | None = None,
) -> str:
    titular_id = hashlib.sha256(titular.encode()).hexdigest()[:16]
    conexion.execute(
        """INSERT OR REPLACE INTO titulares
           (id, titular, fuente, fecha, simbolos, veredicto, motivo, sim_id)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (titular_id, titular, fuente, ahora_iso(), simbolos, veredicto, motivo, sim_id),
    )
    conexion.commit()
    return titular_id


def titulares_recientes(conexion, horas: int = 48) -> list[dict]:
    """Los titulares ya evaluados (para el detector de duplicados)."""
    desde = (datetime.now(timezone.utc) - timedelta(hours=horas)).isoformat(timespec="seconds")
    filas = conexion.execute(
        "SELECT titular, veredicto, fecha FROM titulares WHERE fecha >= ?", (desde,)
    ).fetchall()
    return [dict(f) for f in filas]


# ---------- suscriptores (la tabla nace ahora; el boletín llega en la Etapa 8) ----------

def agregar_suscriptor(conexion, email: str, origen: str = "web") -> str:
    """Alta de suscriptor. Devuelve su token de baja de un clic."""
    token = secrets.token_urlsafe(24)
    conexion.execute(
        """INSERT INTO suscriptores (email, fecha_alta, origen, activo, token_baja)
           VALUES (?, ?, ?, 1, ?)
           ON CONFLICT(email) DO UPDATE SET activo = 1""",
        (email.strip().lower(), ahora_iso(), origen, token),
    )
    conexion.commit()
    fila = conexion.execute("SELECT token_baja FROM suscriptores WHERE email = ?", (email.strip().lower(),)).fetchone()
    return fila["token_baja"]


def dar_de_baja(conexion, token: str) -> bool:
    """Desuscripción de un clic. True si el token existía."""
    cursor = conexion.execute("UPDATE suscriptores SET activo = 0 WHERE token_baja = ?", (token,))
    conexion.commit()
    return cursor.rowcount > 0
