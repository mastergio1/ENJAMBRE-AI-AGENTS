"""Fase 2 — Barrido de población: ¿el TAMAÑO del enjambre cambia la predicción?

Controla lo que pide la auditoría: escala las cantidades por un `factor` (mismas
proporciones) y ajusta el capital por agente ×1/factor, de modo que el **capital
agregado por tipo se mantiene constante** (si no, cambiar N alteraría liquidez y
profundidad a la vez). Corre el ABM con **señales de líder CONGELADAS** (las medias
por arquetipo del caso, sin IA) y mide el acierto direccional por N, más el tiempo.

Si todos los N dan el mismo acierto (y todos por debajo del consenso A3), el tamaño
no aporta predicción: el enjambre grande es decisión de PRODUCTO/visual, no de alpha.
Exploratorio (banco histórico). Sin IA ni red.

Uso: python3 engine/calibration/barrido_poblacion.py cal.con_fecha.json cal.json [factores]
"""
import json
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # engine/

TICKS_CAL, TICKS_PREV, TICKS_POST = 60, 10, 140  # = server.TICKS_*
ZONA = 0.3


def escalar_config(config: dict, factor: float, min_cantidad: int = 1) -> dict:
    """Cantidades ×factor; capital_relativo ×1/factor (capital agregado constante).
    Esenciales (market maker) con mínimo `min_cantidad`. Puro y testeable."""
    c = json.loads(json.dumps(config))  # copia profunda
    def cant(n):
        return max(min_cantidad, int(round(n * factor)))
    total = 0
    for tipo in c["tipos"]:
        if "capital_relativo" in tipo:
            tipo["capital_relativo"] = tipo["capital_relativo"] / factor
        if tipo.get("id") == "lider_opinion":
            for arq in tipo.get("arquetipos", []):
                arq["cantidad"] = cant(arq["cantidad"])
                total += arq["cantidad"]
        elif "cantidad" in tipo:
            tipo["cantidad"] = cant(tipo["cantidad"])
            total += tipo["cantidad"]
    c["total_agentes"] = total
    return c


def _respuestas_congeladas(lideres, senales_arquetipo):
    """Una respuesta por líder (en su orden), con la media de su arquetipo. fuente
    'cache' para que el motor la trate como IA real (no como respaldo léxico)."""
    out = []
    for lid in lideres:
        a = senales_arquetipo.get(lid.arquetipo) or {}
        out.append({"senal": float(a.get("senal_media", 0.0)),
                    "confianza": float(a.get("confianza_media", 0.5)),
                    "frase": "", "fuente": "cache"})
    return out


def direccion_una(config_escalado, titular, senales_arquetipo, mercado, seed):
    """Corre una simulación con población escalada y señales congeladas; devuelve el
    % de movimiento tras la noticia (réplica del flujo de producción)."""
    from agents.lider import LiderOpinion
    from brains.mercado import perfil_de
    from model import MercadoEnjambre

    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(config_escalado, f)
        ruta = f.name
    modelo = MercadoEnjambre(seed=seed, ticks_horizonte=TICKS_CAL + TICKS_POST,
                             ruta_config=Path(ruta))
    modelo.correr(TICKS_CAL)
    lideres = [a for a in modelo.agentes_ordenados if isinstance(a, LiderOpinion)]
    respuestas = _respuestas_congeladas(lideres, senales_arquetipo)
    for _ in range(TICKS_PREV):
        modelo.step()
    previo = modelo.historial_precios[-1]
    modelo.aplicar_titular(titular, respuestas=respuestas, perfil=perfil_de(mercado or "indice"))
    for _ in range(TICKS_POST):
        modelo.step()
    final = modelo.historial_precios[-1]
    return 100.0 * (final - previo) / previo if previo else 0.0


def _casos_indice(ruta_con_fecha, ruta_raw):
    """Filas direccionables de índice con su senales_arquetipo y titular."""
    cf = json.loads(Path(ruta_con_fecha).read_text())
    crudo = json.loads(Path(ruta_raw).read_text())
    casos = crudo.get("casos", crudo) if isinstance(crudo, dict) else crudo
    idx = {}
    for c in casos:
        rr = c.get("reaccion_real") or {}
        idx[(rr.get("fecha_base"), rr.get("simbolo"))] = c
    out = []
    for r in cf:
        if r.get("mercado") != "indice":
            continue
        pc = r.get("pct_corr")
        if pc is None or abs(pc) < ZONA:
            continue
        c = idx.get((r.get("fecha"), r.get("simbolo")))
        if not c or not c.get("senales_arquetipo"):
            continue
        out.append({"titular": c["titular"], "sa": c["senales_arquetipo"],
                    "mercado": r.get("mercado"), "pct_corr": pc, "fecha": r.get("fecha")})
    return out


def _sg(x):
    return 1 if x > 0 else (-1 if x < 0 else 0)


def barrido(ruta_con_fecha, ruta_raw, factores=(1.0, 0.25, 0.1, 0.05), seed=20260101, limite=None):
    import os
    base_cfg = json.loads((Path(__file__).resolve().parent.parent / "config" / "agentes.json").read_text())
    casos = _casos_indice(ruta_con_fecha, ruta_raw)
    if limite:
        casos = casos[:limite]
    res = {}
    for factor in factores:
        cfg = escalar_config(base_cfg, factor)
        n_ag = cfg["total_agentes"]
        ok = n = 0
        t0 = time.time()
        for c in casos:
            d = direccion_una(cfg, c["titular"], c["sa"], c["mercado"], seed)
            if abs(d) < 0.01:
                continue  # el enjambre no se movió → se abstiene
            n += 1
            ok += 1 if _sg(d) == _sg(c["pct_corr"]) else 0
        dur = time.time() - t0
        acc = round(100 * ok / n, 1) if n else None
        res[factor] = {"agentes": n_ag, "acierto": acc, "n": n,
                       "seg_por_caso": round(dur / max(1, len(casos)), 2)}
        print(f"factor {factor:>5} · {n_ag:>6} agentes · acierto {acc}% (n={n}) · "
              f"{res[factor]['seg_por_caso']}s/caso", flush=True)
    return res


if __name__ == "__main__":
    cf, raw = sys.argv[1], sys.argv[2]
    fac = [float(x) for x in sys.argv[3].split(",")] if len(sys.argv) > 3 else (1.0, 0.25, 0.1, 0.05)
    barrido(cf, raw, factores=fac)
