"""Respaldo de la calibración a GitHub — la caja fuerte fuera de Render.

El disco del plan free de Render es efímero: cada redeploy lo borra.
Este módulo sube el acumulado de casos (enjambre vs mercado real) como
JSON al repositorio, en una rama SEPARADA de `main` (un commit a `main`
redesplegaría el motor: el perro mordiéndose la cola). Antes de subir,
FUSIONA con lo ya respaldado — ningún borrón de disco pierde historia.

Sin token configurado no hace nada, y el corrector sigue igual.

Variables de entorno:
- GITHUB_RESPALDO_TOKEN  token "fine-grained" con permiso Contents (RW)
                         SOLO sobre este repositorio
- GITHUB_RESPALDO_REPO   "usuario/repo" (defecto: el repo del proyecto)
- GITHUB_RESPALDO_RAMA   rama destino (defecto: respaldo-datos — NUNCA main)
- GITHUB_RESPALDO_RUTA   ruta del archivo (defecto: datos/calibracion.json)
"""

import base64
import json
import os
from datetime import datetime, timezone

import httpx

from contenido import persistencia

API = "https://api.github.com"
REPO_DEFECTO = "mastergio1/ENJAMBRE-AI-AGENTS"
RAMA_DEFECTO = "respaldo-datos"
RUTA_DEFECTO = "datos/calibracion.json"


def hay_token() -> bool:
    return bool(os.environ.get("GITHUB_RESPALDO_TOKEN"))


def exportar_casos(conexion) -> list[dict]:
    """Los casos de calibración como dicts planos: destacadas corregidas
    (origen 'en_vivo') y exámenes históricos del backtest ('historico')."""
    filas = conexion.execute(
        """SELECT s.id, s.fecha, s.titular, s.resumen_json, s.reaccion_real,
                  s.epilogo, s.fuente, t.simbolos
           FROM simulaciones s LEFT JOIN titulares t ON t.sim_id = s.id
           WHERE s.reaccion_real IS NOT NULL
             AND (s.destacada = 1 OR s.fuente = 'backtest')
           ORDER BY s.fecha"""
    ).fetchall()
    casos = []
    for fila in filas:
        resumen = json.loads(fila["resumen_json"])
        reaccion = json.loads(fila["reaccion_real"])
        casos.append({
            "sim_id": fila["id"],
            "origen": "historico" if fila["fuente"] == "backtest" else "en_vivo",
            "fecha": fila["fecha"],
            "titular": fila["titular"],
            "simbolos": fila["simbolos"] or reaccion.get("simbolo", ""),
            "direccion_pct": resumen.get("direccion_pct"),
            "volatilidad_pct": resumen.get("volatilidad_pct"),
            "reaccion_real": reaccion,
            "epilogo": fila["epilogo"],
        })
    return casos


def fusionar(previos: list[dict], nuevos: list[dict]) -> list[dict]:
    """Une por sim_id (lo nuevo pisa lo viejo) y ordena por fecha.

    Esta fusión es la que hace al respaldo inmune a los borrones de disco:
    tras un redeploy la base local parte vacía, pero lo ya subido se
    conserva y solo se le suman los casos nuevos.
    """
    por_id = {c["sim_id"]: c for c in previos}
    por_id.update({c["sim_id"]: c for c in nuevos})
    return sorted(por_id.values(), key=lambda c: c.get("fecha") or "")


def respaldar(conexion=None) -> dict:
    """Exporta los casos y los sube fusionados. NUNCA lanza.

    Devuelve {"subido": bool, "casos": int, "motivo"?: str}.
    """
    if not hay_token():
        return {"subido": False, "casos": 0, "motivo": "sin GITHUB_RESPALDO_TOKEN"}
    propia = conexion is None
    conexion = conexion or persistencia.conectar()
    try:
        nuevos = exportar_casos(conexion)
    finally:
        if propia:
            conexion.close()
    if not nuevos:
        return {"subido": False, "casos": 0, "motivo": "sin casos que respaldar"}
    return _subir(nuevos)


def _subir(nuevos: list[dict]) -> dict:
    repo = os.environ.get("GITHUB_RESPALDO_REPO", REPO_DEFECTO)
    rama = os.environ.get("GITHUB_RESPALDO_RAMA", RAMA_DEFECTO)
    ruta = os.environ.get("GITHUB_RESPALDO_RUTA", RUTA_DEFECTO)
    url = f"{API}/repos/{repo}/contents/{ruta}"
    cabeceras = {
        "Authorization": f"Bearer {os.environ['GITHUB_RESPALDO_TOKEN']}",
        "Accept": "application/vnd.github+json",
    }
    try:
        # 1. leer lo ya respaldado (para fusionar) y su sha (para actualizar)
        actual = httpx.get(url, params={"ref": rama}, headers=cabeceras, timeout=15)
        sha, previos = None, []
        if actual.status_code == 200:
            datos = actual.json()
            sha = datos.get("sha")
            crudo = base64.b64decode(datos.get("content") or "").decode("utf-8")
            previos = (json.loads(crudo) or {}).get("casos", [])

        casos = fusionar(previos, nuevos)
        hoy = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        contenido = {
            "generado": persistencia.ahora_iso(),
            "nota": ("Casos de calibración de El Enjambre: reacción simulada vs "
                     "movimiento real (corrector automático). Registro educativo."),
            "casos": casos,
        }
        cuerpo = {
            "message": f"Respaldo de calibración {hoy} ({len(casos)} casos)",
            "content": base64.b64encode(
                json.dumps(contenido, ensure_ascii=False, indent=1).encode("utf-8")
            ).decode("ascii"),
            "branch": rama,
        }
        if sha:
            cuerpo["sha"] = sha
        respuesta = httpx.put(url, headers=cabeceras, json=cuerpo, timeout=20)
        respuesta.raise_for_status()
        return {"subido": True, "casos": len(casos)}
    except Exception as error:  # red, token, rama inexistente: no tumba nada
        return {"subido": False, "casos": len(nuevos),
                "motivo": f"{type(error).__name__}: {str(error)[:120]}"}
