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
from datetime import date, datetime, timedelta, timezone
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
CREATE TABLE IF NOT EXISTS briefs (
  fecha      TEXT PRIMARY KEY,     -- AAAA-MM-DD (uno por día)
  brief_json TEXT NOT NULL,        -- 'lo que pasó' + 'qué observa hoy' + origen
  aprobado   INTEGER DEFAULT 0     -- 1 tras el visto bueno de Giorgio
);
CREATE TABLE IF NOT EXISTS suscriptores (
  email          TEXT PRIMARY KEY,
  fecha_alta     TEXT NOT NULL,
  origen         TEXT,
  activo         INTEGER DEFAULT 0,   -- 0 hasta confirmar (double opt-in)
  token_baja     TEXT NOT NULL,
  token_confirma TEXT,
  premium        INTEGER DEFAULT 0,   -- 1 = suscriptor de pago (recibe el deep-dive completo)
  premium_hasta  TEXT                 -- vencimiento ISO (AAAA-MM-DD); NULL = sin vencimiento
);
CREATE TABLE IF NOT EXISTS contactos (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,  -- leads B2B (organizaciones)
  fecha        TEXT NOT NULL,
  nombre       TEXT NOT NULL,
  organizacion TEXT,
  email        TEXT NOT NULL,
  mensaje      TEXT
);
CREATE TABLE IF NOT EXISTS gasto_diario (
  -- el tope global de simulaciones públicas del día, en DISCO (no en memoria):
  -- así NO se reinicia con cada despliegue de Render (la muralla de la billetera
  -- debe ser un techo firme, no uno que se levanta solo en cada reinicio).
  fecha       TEXT PRIMARY KEY,     -- AAAA-MM-DD (UTC)
  consumidas  INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS eventos_correo (
  -- eventos de Resend (webhook firmado): aperturas y clics por edición.
  -- UNIQUE(fecha_ed,email,tipo) → un opened por persona = apertura ÚNICA.
  fecha_ed   TEXT,                 -- la edición (AAAA-MM-DD), del tag del envío
  email      TEXT,
  tipo       TEXT NOT NULL,        -- delivered/opened/clicked/bounced/complained
  ts         TEXT NOT NULL,
  UNIQUE(fecha_ed, email, tipo)
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
            ("suscriptores", "fecha_confirma", "TEXT"),  # anti-reenvío (auditoría C)
            ("suscriptores", "premium", "INTEGER DEFAULT 0"),  # suscripción de pago (Premium)
            ("suscriptores", "premium_hasta", "TEXT"),         # vencimiento del Premium (ISO)
            ("simulaciones", "epilogo", "TEXT"),  # "¿y qué pasó después?" (Etapa 9)
            ("simulaciones", "reaccion_real", "TEXT"),  # corrector automático (calibración)
            # centro de mando de El Pulso: la edición como máquina de estados
            ("briefs", "estado", "TEXT DEFAULT 'pendiente'"),  # pendiente/aprobada/enviada/descartada
            ("briefs", "token", "TEXT"),           # secreto para los enlaces del correo de revisión
            ("briefs", "html_preview", "TEXT"),    # el correo ya armado (WYSIWYG al aprobar)
            ("briefs", "asunto", "TEXT"),          # asunto del correo del día
            ("briefs", "enviados", "INTEGER DEFAULT 0"),
            ("briefs", "suscriptores", "INTEGER DEFAULT 0"),
            ("briefs", "generada_iso", "TEXT"),
            ("briefs", "enviada_iso", "TEXT"),
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
    cruda = datos.get("reaccion_real")
    datos["reaccion_real"] = json.loads(cruda) if cruda else None
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


# ---------- briefs de La Redacción (el análisis de mercado del día) ----------

def guardar_brief(conexion, fecha: str, brief: dict, aprobado: bool = False) -> None:
    conexion.execute(
        """INSERT INTO briefs (fecha, brief_json, aprobado) VALUES (?, ?, ?)
           ON CONFLICT(fecha) DO UPDATE SET brief_json = excluded.brief_json""",
        (fecha, json.dumps(brief, ensure_ascii=False), int(aprobado)),
    )
    conexion.commit()


def obtener_brief(conexion, fecha: str) -> dict | None:
    fila = conexion.execute(
        "SELECT brief_json, aprobado FROM briefs WHERE fecha = ?", (fecha,)
    ).fetchone()
    if fila is None:
        return None
    brief = json.loads(fila["brief_json"])
    brief["aprobado"] = bool(fila["aprobado"])
    return brief


def aprobar_brief(conexion, fecha: str) -> bool:
    cursor = conexion.execute("UPDATE briefs SET aprobado = 1 WHERE fecha = ?", (fecha,))
    conexion.commit()
    return cursor.rowcount > 0


# ---------- El centro de mando: la edición como máquina de estados ----------
# estado ∈ {pendiente, aprobada, enviada, descartada}. Nada sale a los
# suscriptores hasta que Giorgio la aprueba (desde el correo o el dashboard).

TOKEN_BAJA_SENTINEL = "__TOKEN_BAJA__"  # marcador en el preview; se reemplaza al enviar


def _fila_edicion(fila) -> dict | None:
    if fila is None:
        return None
    return {
        "fecha": fila["fecha"],
        "brief": json.loads(fila["brief_json"]),
        "estado": fila["estado"] or "pendiente",
        "token": fila["token"],
        "html_preview": fila["html_preview"],
        "asunto": fila["asunto"],
        "enviados": fila["enviados"] or 0,
        "suscriptores": fila["suscriptores"] or 0,
        "generada_iso": fila["generada_iso"],
        "enviada_iso": fila["enviada_iso"],
        "aprobado": bool(fila["aprobado"]),
    }


_COLS_EDICION = ("fecha, brief_json, aprobado, estado, token, html_preview, asunto, "
                 "enviados, suscriptores, generada_iso, enviada_iso")


def guardar_edicion(conexion, fecha: str, brief: dict, html_preview: str,
                    asunto: str, token: str, generada_iso: str) -> None:
    """Guarda la edición del día lista para revisión (estado 'pendiente').
    Regenerar el mismo día reinicia el estado y las estadísticas."""
    conexion.execute(
        """INSERT INTO briefs (fecha, brief_json, aprobado, estado, token,
                               html_preview, asunto, generada_iso, enviados, suscriptores, enviada_iso)
           VALUES (?, ?, 0, 'pendiente', ?, ?, ?, ?, 0, 0, NULL)
           ON CONFLICT(fecha) DO UPDATE SET
             brief_json=excluded.brief_json, aprobado=0, estado='pendiente',
             token=excluded.token, html_preview=excluded.html_preview,
             asunto=excluded.asunto, generada_iso=excluded.generada_iso,
             enviados=0, suscriptores=0, enviada_iso=NULL""",
        (fecha, json.dumps(brief, ensure_ascii=False), token, html_preview, asunto, generada_iso),
    )
    conexion.commit()


def obtener_edicion(conexion, fecha: str) -> dict | None:
    fila = conexion.execute(
        f"SELECT {_COLS_EDICION} FROM briefs WHERE fecha = ?", (fecha,)).fetchone()
    return _fila_edicion(fila)


def edicion_por_token(conexion, token: str | None) -> dict | None:
    """La edición apuntada por un token de correo (para los enlaces de revisión)."""
    if not token or len(token) < 16:
        return None
    fila = conexion.execute(
        f"SELECT {_COLS_EDICION} FROM briefs WHERE token = ?", (token,)).fetchone()
    return _fila_edicion(fila)


def set_estado_edicion(conexion, fecha: str, estado: str) -> bool:
    aprobado = 1 if estado in ("aprobada", "enviada") else 0
    cur = conexion.execute(
        "UPDATE briefs SET estado = ?, aprobado = ? WHERE fecha = ?", (estado, aprobado, fecha))
    conexion.commit()
    return cur.rowcount > 0


def marcar_enviada(conexion, fecha: str, enviados: int, suscriptores: int, enviada_iso: str) -> None:
    conexion.execute(
        """UPDATE briefs SET estado='enviada', aprobado=1,
             enviados=?, suscriptores=?, enviada_iso=? WHERE fecha=?""",
        (enviados, suscriptores, enviada_iso, fecha))
    conexion.commit()


def listar_ediciones(conexion, limite: int = 30) -> list[dict]:
    """El historial de ediciones para el dashboard (sin el HTML, liviano)."""
    filas = conexion.execute(
        """SELECT fecha, estado, asunto, enviados, suscriptores, generada_iso, enviada_iso
           FROM briefs ORDER BY fecha DESC LIMIT ?""", (max(1, int(limite)),)).fetchall()
    return [{"fecha": f["fecha"], "estado": f["estado"] or "pendiente", "asunto": f["asunto"],
             "enviados": f["enviados"] or 0, "suscriptores": f["suscriptores"] or 0,
             "generada_iso": f["generada_iso"], "enviada_iso": f["enviada_iso"]} for f in filas]


def actualizar_redactado(conexion, fecha: str, redactado: dict) -> bool:
    """Guarda cambios de texto del editor (dashboard) dentro del brief del día."""
    fila = conexion.execute("SELECT brief_json FROM briefs WHERE fecha = ?", (fecha,)).fetchone()
    if fila is None:
        return False
    brief = json.loads(fila["brief_json"])
    brief["redactado"] = redactado
    conexion.execute("UPDATE briefs SET brief_json = ? WHERE fecha = ?",
                     (json.dumps(brief, ensure_ascii=False), fecha))
    conexion.commit()
    return True


def actualizar_preview(conexion, fecha: str, html_preview: str) -> None:
    """Reemplaza el HTML del correo tras una edición manual (dashboard)."""
    conexion.execute("UPDATE briefs SET html_preview = ? WHERE fecha = ?", (html_preview, fecha))
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


# ---------- el corrector automático (calibración) ----------

def guardar_reaccion_real(conexion, sim_id: str, datos: dict) -> bool:
    """El movimiento real del símbolo (JSON): la materia prima de la libreta."""
    cursor = conexion.execute(
        "UPDATE simulaciones SET reaccion_real = ? WHERE id = ?",
        (json.dumps(datos, ensure_ascii=False), sim_id),
    )
    conexion.commit()
    return cursor.rowcount > 0


def destacadas_sin_correccion(conexion, antes_de: str, limite: int = 10) -> list[dict]:
    """Destacadas con ticker, anteriores a `antes_de` y aún sin corrección.
    Más antiguas primero: nada se queda esperando para siempre."""
    filas = conexion.execute(
        """SELECT s.id, s.fecha, s.resumen_json, s.epilogo, s.lideres_json, t.simbolos
           FROM simulaciones s JOIN titulares t ON t.sim_id = s.id
           WHERE s.destacada = 1 AND s.reaccion_real IS NULL
             AND t.simbolos IS NOT NULL AND t.simbolos != ''
             AND s.fecha < ?
           ORDER BY s.fecha ASC LIMIT ?""",
        (antes_de, limite),
    ).fetchall()
    return [dict(f) for f in filas]


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


# ---------- contactos B2B (el canal de organizaciones) ----------

def agregar_contacto(conexion, *, nombre: str, email: str,
                     organizacion: str = "", mensaje: str = "") -> int:
    """Guarda un lead del formulario de organizaciones. Devuelve su id."""
    cursor = conexion.execute(
        "INSERT INTO contactos (fecha, nombre, organizacion, email, mensaje) "
        "VALUES (?, ?, ?, ?, ?)",
        (ahora_iso(), nombre.strip()[:120], organizacion.strip()[:160],
         email.strip().lower()[:200], mensaje.strip()[:800]),
    )
    conexion.commit()
    return cursor.lastrowid


def listar_contactos(conexion, limite: int = 100) -> list[dict]:
    filas = conexion.execute(
        "SELECT * FROM contactos ORDER BY fecha DESC LIMIT ?", (limite,)
    ).fetchall()
    return [dict(f) for f in filas]


# ---------- suscriptores del boletín (double opt-in) ----------

# Ventana anti-abuso: no se reenvía el correo de confirmación a la misma
# dirección más seguido que esto (evita usar el alta como bombardeo de un
# tercero). Ver auditoría previa al despliegue, punto C.
VENTANA_REENVIO = timedelta(minutes=10)


def agregar_suscriptor(conexion, email: str, origen: str = "web") -> dict:
    """Alta PENDIENTE de suscriptor (double opt-in): nace inactivo hasta
    confirmar. Devuelve {email, token_confirma, token_baja, ya_activo, reenviar}.

    - Ya activo: no se le molesta (reenviar=False).
    - Pendiente con confirmación reciente (< VENTANA_REENVIO): NO se rota el
      token ni se reenvía correo (reenviar=False) — antibombardeo.
    - Nuevo o pendiente antiguo: se emite token y se pide reenviar (True).
    """
    email = email.strip().lower()
    fila = conexion.execute(
        "SELECT activo, token_confirma, token_baja, fecha_confirma FROM suscriptores WHERE email = ?",
        (email,),
    ).fetchone()
    if fila and fila["activo"]:
        return {"email": email, "token_confirma": fila["token_confirma"],
                "token_baja": fila["token_baja"], "ya_activo": True, "reenviar": False}

    ahora = datetime.now(timezone.utc)
    # ¿hay un alta pendiente con un correo de confirmación reciente? no reenviar
    if fila and fila["fecha_confirma"]:
        try:
            emitido = datetime.fromisoformat(fila["fecha_confirma"])
            if ahora - emitido < VENTANA_REENVIO:
                return {"email": email, "token_confirma": fila["token_confirma"],
                        "token_baja": fila["token_baja"], "ya_activo": False, "reenviar": False}
        except ValueError:
            pass

    token_confirma = secrets.token_urlsafe(24)
    token_baja = fila["token_baja"] if fila else secrets.token_urlsafe(24)
    ahora_txt = ahora.isoformat(timespec="seconds")
    conexion.execute(
        """INSERT INTO suscriptores
             (email, fecha_alta, origen, activo, token_baja, token_confirma, fecha_confirma)
           VALUES (?, ?, ?, 0, ?, ?, ?)
           ON CONFLICT(email) DO UPDATE SET token_confirma = excluded.token_confirma,
                                            fecha_confirma = excluded.fecha_confirma""",
        (email, ahora_txt, origen, token_baja, token_confirma, ahora_txt),
    )
    conexion.commit()
    return {"email": email, "token_confirma": token_confirma,
            "token_baja": token_baja, "ya_activo": False, "reenviar": True}


def alta_directa(conexion, email: str, origen: str = "premium") -> str:
    """Alta ACTIVA sin doble opt-in: para pagadores (Premium), que ya dieron
    consentimiento explícito al pagar. Crea el suscriptor activo o reactiva uno
    dado de baja, conservando su token. Devuelve el email normalizado."""
    email = email.strip().lower()
    fila = conexion.execute("SELECT token_baja FROM suscriptores WHERE email = ?", (email,)).fetchone()
    if fila:
        conexion.execute("UPDATE suscriptores SET activo = 1, token_confirma = NULL WHERE email = ?", (email,))
    else:
        conexion.execute(
            "INSERT INTO suscriptores (email, fecha_alta, origen, activo, token_baja) "
            "VALUES (?, ?, ?, 1, ?)",
            (email, ahora_iso(), origen, secrets.token_urlsafe(24)),
        )
    conexion.commit()
    return email


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
    """Los que confirmaron: a quienes se envía el Pulso. Cada uno trae su
    estado `premium` (1/0) YA calculado (respetando el vencimiento), para que
    el envío decida quién recibe el análisis completo y quién el teaser."""
    filas = conexion.execute(
        "SELECT email, token_baja, "
        "  CASE WHEN premium = 1 AND (premium_hasta IS NULL OR premium_hasta >= date('now')) "
        "       THEN 1 ELSE 0 END AS premium "
        "FROM suscriptores WHERE activo = 1"
    ).fetchall()
    return [dict(f) for f in filas]


# ---------- Premium: la llave que decide quién recibe el deep-dive completo ----------

def set_premium(conexion, email: str, activo: bool = True, hasta: str | None = None) -> bool:
    """Prende o apaga el Premium de un suscriptor. `hasta` = vencimiento ISO
    (AAAA-MM-DD) o None para sin vencimiento. True si el correo existe."""
    cursor = conexion.execute(
        "UPDATE suscriptores SET premium = ?, premium_hasta = ? WHERE email = ?",
        (1 if activo else 0, (hasta or None), email.strip().lower()),
    )
    conexion.commit()
    return cursor.rowcount > 0


def es_premium(conexion, email: str) -> bool:
    """True si el correo es un suscriptor Premium activo y no vencido."""
    fila = conexion.execute(
        "SELECT 1 FROM suscriptores WHERE email = ? AND activo = 1 AND premium = 1 "
        "AND (premium_hasta IS NULL OR premium_hasta >= date('now'))",
        (email.strip().lower(),),
    ).fetchone()
    return fila is not None


def contar_premium(conexion) -> int:
    """Cuántos suscriptores Premium activos (no vencidos) hay ahora mismo."""
    return conexion.execute(
        "SELECT COUNT(*) FROM suscriptores WHERE activo = 1 AND premium = 1 "
        "AND (premium_hasta IS NULL OR premium_hasta >= date('now'))"
    ).fetchone()[0]


# ---------- tope de gasto diario (en disco, sobrevive a los reinicios) ----------

def gasto_dia(conexion, fecha: str) -> int:
    """Cuántas simulaciones públicas se han consumido en `fecha` (0 si no hay fila)."""
    fila = conexion.execute(
        "SELECT consumidas FROM gasto_diario WHERE fecha = ?", (fecha,)).fetchone()
    return fila[0] if fila else 0


def sumar_gasto_dia(conexion, fecha: str, n: int = 1) -> int:
    """Suma `n` al gasto de `fecha` (crea la fila si no existe). Devuelve el total."""
    conexion.execute(
        "INSERT INTO gasto_diario (fecha, consumidas) VALUES (?, ?) "
        "ON CONFLICT(fecha) DO UPDATE SET consumidas = consumidas + excluded.consumidas",
        (fecha, n))
    conexion.commit()
    return gasto_dia(conexion, fecha)


def reiniciar_gasto(conexion) -> None:
    """Borra todo el gasto registrado (solo para los tests)."""
    conexion.execute("DELETE FROM gasto_diario")
    conexion.commit()


# ---------- eventos de correo (aperturas/clics de Resend) ----------

# tipos que aceptamos del webhook (los demás se ignoran en silencio)
_TIPOS_EVENTO = {"delivered", "opened", "clicked", "bounced", "complained"}


def registrar_evento_correo(conexion, fecha_ed: str | None, email: str, tipo: str,
                            ts: str | None = None) -> bool:
    """Registra un evento de Resend. INSERT OR IGNORE sobre (edición,email,tipo):
    contar filas = contar personas únicas (aperturas/clics únicos). Devuelve
    True si era un evento nuevo (no un duplicado)."""
    tipo = (tipo or "").strip().lower()
    if tipo not in _TIPOS_EVENTO or not email:
        return False
    cur = conexion.execute(
        "INSERT OR IGNORE INTO eventos_correo (fecha_ed, email, tipo, ts) VALUES (?, ?, ?, ?)",
        ((fecha_ed or "").strip()[:10] or None, email.strip().lower()[:200], tipo, ts or ahora_iso()),
    )
    conexion.commit()
    return cur.rowcount > 0


def _unicos(conexion, fecha_ed: str, tipo: str) -> int:
    return conexion.execute(
        "SELECT COUNT(DISTINCT email) FROM eventos_correo WHERE fecha_ed = ? AND tipo = ?",
        (fecha_ed, tipo),
    ).fetchone()[0]


def estadisticas(conexion, dias: int = 30, ediciones_correo: int = 14) -> dict:
    """El panorama para la pestaña de estadísticas del centro de mando:
    suscriptores (total/activos/pendientes, curva de crecimiento, orígenes),
    ediciones (enviadas/descartadas) y correo (aperturas/clics por edición).

    Todo sale de datos reales; si aún no hay eventos de Resend, las tasas van
    en None y la UI lo muestra como 'aún sin datos' (degradación elegante)."""
    dias = max(7, min(int(dias), 120))

    total = conexion.execute("SELECT COUNT(*) FROM suscriptores").fetchone()[0]
    activos = conexion.execute("SELECT COUNT(*) FROM suscriptores WHERE activo = 1").fetchone()[0]
    pendientes = total - activos
    tasa_confirma = round(activos / total, 3) if total else None

    # curva de crecimiento: acumulado de activos por día en la ventana
    altas = {f["d"]: f["n"] for f in conexion.execute(
        "SELECT substr(fecha_alta,1,10) d, COUNT(*) n FROM suscriptores "
        "WHERE activo = 1 GROUP BY d").fetchall()}
    inicio = date.today() - timedelta(days=dias - 1)
    base = conexion.execute(
        "SELECT COUNT(*) FROM suscriptores WHERE activo = 1 AND substr(fecha_alta,1,10) < ?",
        (inicio.isoformat(),)).fetchone()[0]
    serie, acum = [], base
    for i in range(dias):
        d = (inicio + timedelta(days=i)).isoformat()
        n = altas.get(d, 0)
        acum += n
        serie.append({"fecha": d, "altas": n, "acumulado": acum})

    por_origen = [{"origen": f["o"], "n": f["n"]} for f in conexion.execute(
        "SELECT COALESCE(NULLIF(origen,''),'—') o, COUNT(*) n FROM suscriptores "
        "WHERE activo = 1 GROUP BY o ORDER BY n DESC").fetchall()]

    # ediciones
    def _cuenta(estado):
        return conexion.execute("SELECT COUNT(*) FROM briefs WHERE estado = ?", (estado,)).fetchone()[0]
    enviadas, descartadas = _cuenta("enviada"), _cuenta("descartada")
    prom = conexion.execute(
        "SELECT AVG(enviados) FROM briefs WHERE estado = 'enviada' AND enviados > 0").fetchone()[0]

    # correo por edición (últimas enviadas)
    filas = conexion.execute(
        "SELECT fecha, asunto, enviados FROM briefs WHERE estado = 'enviada' "
        "ORDER BY fecha DESC LIMIT ?", (max(1, int(ediciones_correo)),)).fetchall()
    correo, sum_env, sum_ab, sum_cl = [], 0, 0, 0
    for f in filas:
        env = f["enviados"] or 0
        ab, cl = _unicos(conexion, f["fecha"], "opened"), _unicos(conexion, f["fecha"], "clicked")
        sum_env += env; sum_ab += ab; sum_cl += cl
        correo.append({
            "fecha": f["fecha"], "asunto": f["asunto"], "enviados": env,
            "abiertos": ab, "clics": cl,
            "tasa_apertura": round(ab / env, 3) if env else None,
            "tasa_clic": round(cl / env, 3) if env else None,
        })
    hay_eventos = conexion.execute("SELECT COUNT(*) FROM eventos_correo").fetchone()[0] > 0

    return {
        "suscriptores": {
            "total": total, "activos": activos, "pendientes": pendientes,
            "tasa_confirmacion": tasa_confirma, "serie": serie, "por_origen": por_origen,
        },
        "ediciones": {
            "enviadas": enviadas, "descartadas": descartadas,
            "promedio_enviados": round(prom, 1) if prom else None,
        },
        "correo": {
            "hay_datos": hay_eventos,
            "tasa_apertura": round(sum_ab / sum_env, 3) if sum_env else None,
            "tasa_clic": round(sum_cl / sum_env, 3) if sum_env else None,
            "por_edicion": correo,
        },
    }
