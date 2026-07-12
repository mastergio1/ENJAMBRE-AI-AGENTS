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
  impacto    INTEGER DEFAULT 0,
  sim_id     TEXT REFERENCES simulaciones(id)
);
CREATE TABLE IF NOT EXISTS suscriptores (
  email          TEXT PRIMARY KEY,
  fecha_alta     TEXT NOT NULL,
  origen         TEXT,
  activo         INTEGER DEFAULT 0,   -- 0 hasta confirmar (double opt-in)
  token_baja     TEXT NOT NULL,
  token_confirma TEXT
);
"""


def ahora_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


_inicializadas: set[str] = set()


def conectar(ruta: str | Path | None = None) -> sqlite3.Connection:
    """Abre (y crea si no existe) la base con su esquema.

    Modo WAL + busy_timeout: lecturas concurrentes no bloquean la
    escritura de una simulación en curso (evita 'database is locked'
    bajo carga). El esquema se crea UNA vez por archivo y proceso —
    no en cada request, que era caro y contendía.
    """
    ruta = Path(ruta or os.environ.get("ENJAMBRE_DB", RUTA_DEFECTO))
    ruta.parent.mkdir(parents=True, exist_ok=True)
    conexion = sqlite3.connect(ruta, timeout=10)
    conexion.row_factory = sqlite3.Row
    conexion.execute("PRAGMA journal_mode=WAL")
    conexion.execute("PRAGMA busy_timeout=5000")
    clave = str(ruta)
    if clave not in _inicializadas:
        conexion.executescript(ESQUEMA)
        # migraciones suaves para bases creadas antes de estas columnas
        for tabla, columna, tipo in [
            ("titulares", "impacto", "INTEGER DEFAULT 0"),
            ("suscriptores", "token_confirma", "TEXT"),
            ("simulaciones", "epilogo", "TEXT"),  # "¿y qué pasó después?" (Etapa 9)
        ]:
            try:
                conexion.execute(f"ALTER TABLE {tabla} ADD COLUMN {columna} {tipo}")
            except sqlite3.OperationalError:
                pass
        conexion.commit()
        _inicializadas.add(clave)
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
    datos["epilogo"] = datos.get("epilogo")  # puede no existir en bases viejas
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


# ---------- el archivo / hemeroteca (Etapa 9) ----------

def archivo(conexion, *, mes: str | None = None, texto: str | None = None,
            ticker: str | None = None, pagina: int = 0, por_pagina: int = 12) -> dict:
    """La hemeroteca: destacadas navegables por mes, buscables por texto del
    titular y filtrables por ticker. Devuelve {total, pagina, por_pagina, items}."""
    condiciones = ["s.destacada = 1"]
    parametros: list = []
    if mes:
        condiciones.append("s.fecha LIKE ?")
        parametros.append(f"{mes}%")
    if texto:
        condiciones.append("s.titular LIKE ? COLLATE NOCASE")
        parametros.append(f"%{texto}%")
    if ticker:
        condiciones.append("t.simbolos LIKE ? COLLATE NOCASE")
        parametros.append(f"%{ticker}%")
    donde = " AND ".join(condiciones)

    base = f"FROM simulaciones s LEFT JOIN titulares t ON t.sim_id = s.id WHERE {donde}"
    total = conexion.execute(f"SELECT COUNT(*) {base}", parametros).fetchone()[0]

    pagina = max(0, pagina)
    filas = conexion.execute(
        f"""SELECT s.id, s.titular, s.fuente, s.fecha, s.resumen_json,
                   t.simbolos, (s.epilogo IS NOT NULL AND s.epilogo != '') AS tiene_epilogo
            {base} ORDER BY s.fecha DESC LIMIT ? OFFSET ?""",
        (*parametros, por_pagina, pagina * por_pagina),
    ).fetchall()
    return {"total": total, "pagina": pagina, "por_pagina": por_pagina,
            "items": [dict(f) for f in filas]}


def meses_disponibles(conexion) -> list[str]:
    """Los meses (AAAA-MM) que tienen al menos una destacada, más recientes primero."""
    filas = conexion.execute(
        "SELECT DISTINCT substr(fecha, 1, 7) AS mes FROM simulaciones "
        "WHERE destacada = 1 ORDER BY mes DESC"
    ).fetchall()
    return [f["mes"] for f in filas]


def guardar_epilogo(conexion, sim_id: str, texto: str) -> bool:
    """El '¿y qué pasó después?' que Giorgio completa. True si la sim existe."""
    cursor = conexion.execute(
        "UPDATE simulaciones SET epilogo = ? WHERE id = ?", (texto.strip() or None, sim_id)
    )
    conexion.commit()
    return cursor.rowcount > 0


# ---------- titulares (el log del portero) ----------

def id_titular(titular: str) -> str:
    return hashlib.sha256(titular.encode()).hexdigest()[:16]


def registrar_titular(
    conexion, *, titular: str, fuente: str, veredicto: str,
    motivo: str = "", simbolos: str = "", impacto: int = 0, sim_id: str | None = None,
) -> str:
    titular_id = id_titular(titular)
    conexion.execute(
        """INSERT OR REPLACE INTO titulares
           (id, titular, fuente, fecha, simbolos, veredicto, motivo, impacto, sim_id)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (titular_id, titular, fuente, ahora_iso(), simbolos, veredicto, motivo, impacto, sim_id),
    )
    conexion.commit()
    return titular_id


def obtener_titular(conexion, titular_id: str) -> dict | None:
    fila = conexion.execute("SELECT * FROM titulares WHERE id = ?", (titular_id,)).fetchone()
    return dict(fila) if fila else None


def vincular_simulacion(conexion, titular_id: str, sim_id: str) -> None:
    """Un titular del muro quedó simulado: la tarjeta pasa a Estado A."""
    conexion.execute(
        "UPDATE titulares SET sim_id = ?, veredicto = 'simular' WHERE id = ?",
        (sim_id, titular_id),
    )
    conexion.commit()


def titulares_del_muro(conexion, umbral_impacto: int, limite: int = 30) -> list[dict]:
    """Las tarjetas del muro: lo que amerita, destacadas primero.

    Estado C (descartadas del piso léxico o de impacto bajo) no aparece.
    """
    filas = conexion.execute(
        """SELECT t.*, s.resumen_json, COALESCE(s.destacada, 0) AS sim_destacada
           FROM titulares t LEFT JOIN simulaciones s ON s.id = t.sim_id
           WHERE t.sim_id IS NOT NULL OR t.veredicto = 'simular' OR t.impacto >= ?
           ORDER BY sim_destacada DESC, t.fecha DESC
           LIMIT ?""",
        (umbral_impacto, limite),
    ).fetchall()
    return [dict(f) for f in filas]


def titulares_recientes(conexion, horas: int = 48) -> list[dict]:
    """Los titulares ya evaluados (para el detector de duplicados)."""
    desde = (datetime.now(timezone.utc) - timedelta(hours=horas)).isoformat(timespec="seconds")
    filas = conexion.execute(
        "SELECT titular, veredicto, fecha FROM titulares WHERE fecha >= ?", (desde,)
    ).fetchall()
    return [dict(f) for f in filas]


# ---------- frames del replay 3D (solo las destacadas los conservan) ----------

def ruta_frames(sim_id: str) -> Path:
    base = (Path(os.environ.get("ENJAMBRE_DB", RUTA_DEFECTO)).parent / "frames").resolve()
    destino = (base / f"{sim_id}.bin").resolve()
    # defensa en profundidad: la ruta jamás debe salirse de base/
    if base not in destino.parents:
        raise ValueError("sim_id inválido")
    return destino


def guardar_frames(sim_id: str, frames: list[bytes]) -> str:
    """Concatena y guarda los frames binarios del replay. Devuelve la ruta."""
    ruta = ruta_frames(sim_id)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with open(ruta, "wb") as archivo:
        for frame in frames:
            archivo.write(frame)
    return str(ruta)


def leer_frames(sim_id: str) -> bytes | None:
    ruta = ruta_frames(sim_id)
    return ruta.read_bytes() if ruta.exists() else None


# ---------- suscriptores del boletín (double opt-in) ----------

def agregar_suscriptor(conexion, email: str, origen: str = "web") -> dict:
    """Alta PENDIENTE de suscriptor (double opt-in): nace inactivo hasta
    confirmar. Devuelve {email, token_confirma, token_baja, ya_activo}.
    Reenviar un alta de alguien pendiente renueva su token de confirmación;
    de alguien ya activo, no lo molesta."""
    email = email.strip().lower()
    fila = conexion.execute(
        "SELECT activo, token_confirma, token_baja FROM suscriptores WHERE email = ?", (email,)
    ).fetchone()
    if fila and fila["activo"]:
        return {"email": email, "token_confirma": fila["token_confirma"],
                "token_baja": fila["token_baja"], "ya_activo": True}

    token_confirma = secrets.token_urlsafe(24)
    token_baja = fila["token_baja"] if fila else secrets.token_urlsafe(24)
    conexion.execute(
        """INSERT INTO suscriptores (email, fecha_alta, origen, activo, token_baja, token_confirma)
           VALUES (?, ?, ?, 0, ?, ?)
           ON CONFLICT(email) DO UPDATE SET token_confirma = excluded.token_confirma""",
        (email, ahora_iso(), origen, token_baja, token_confirma),
    )
    conexion.commit()
    return {"email": email, "token_confirma": token_confirma,
            "token_baja": token_baja, "ya_activo": False}


def confirmar_suscriptor(conexion, token: str) -> str | None:
    """Segundo paso del opt-in: activa al suscriptor. Devuelve su email o None."""
    fila = conexion.execute(
        "SELECT email FROM suscriptores WHERE token_confirma = ?", (token,)
    ).fetchone()
    if not fila:
        return None
    conexion.execute(
        "UPDATE suscriptores SET activo = 1, token_confirma = NULL WHERE token_confirma = ?", (token,)
    )
    conexion.commit()
    return fila["email"]


def dar_de_baja(conexion, token: str) -> bool:
    """Desuscripción de un clic. True si el token existía."""
    cursor = conexion.execute("UPDATE suscriptores SET activo = 0 WHERE token_baja = ?", (token,))
    conexion.commit()
    return cursor.rowcount > 0


def suscriptores_activos(conexion) -> list[dict]:
    """Los que confirmaron: a quienes se envía el Pulso."""
    filas = conexion.execute(
        "SELECT email, token_baja FROM suscriptores WHERE activo = 1"
    ).fetchall()
    return [dict(f) for f in filas]
