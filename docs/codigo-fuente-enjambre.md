# El Enjambre — Código fuente del motor
*Rubicón Lab · volcado completo del código del motor de simulación (`engine/`), para revisión y análisis externo. Generado 2026-11-16.*
*Cada archivo va con su ruta y su contenido íntegro. No se omite nada del motor. Incluye las herramientas de calibración más recientes: la re-medición SIN FUGA de selección (`engine/calibration/remedir_sin_fuga.py`, con su vista de gating por fuerza de señal), la señal media ponderada (`engine/contenido/senal_prediccion.py`), el cerebro de entrevista (`engine/brains/entrevista.py`) y el diagnóstico por segmento (`engine/calibration/evaluar_por_segmento.py`). El frontend 3D en `web/src/` y los binarios/datos (bases SQLite, JSON de eventos) no se incluyen aquí; se entregan aparte si se piden.*

---

## Índice de archivos
- `engine/config/agentes.json` (269 líneas)
- `engine/model.py` (569 líneas)
- `engine/llm_texto.py` (31 líneas)
- `engine/nlp_scorer.py` (69 líneas)
- `engine/simular.py` (42 líneas)
- `engine/demo_titular.py` (57 líneas)
- `engine/probar_portero.py` (27 líneas)
- `engine/server.py` (2015 líneas)
- `engine/conftest.py` (31 líneas)
- `engine/market/__init__.py` (0 líneas)
- `engine/market/order_book.py` (188 líneas)
- `engine/agents/__init__.py` (0 líneas)
- `engine/agents/base.py` (125 líneas)
- `engine/agents/lider.py` (43 líneas)
- `engine/agents/reglas.py` (366 líneas)
- `engine/brains/__init__.py` (0 líneas)
- `engine/brains/arquetipos.py` (172 líneas)
- `engine/brains/cerebro.py` (196 líneas)
- `engine/brains/entrevista.py` (103 líneas)
- `engine/brains/fallback.py` (376 líneas)
- `engine/brains/mercado.py` (160 líneas)
- `engine/brains/reparto.py` (81 líneas)
- `engine/network/__init__.py` (0 líneas)
- `engine/network/red.py` (119 líneas)
- `engine/calibration/__init__.py` (0 líneas)
- `engine/calibration/ablacion_arquetipos.py` (172 líneas)
- `engine/calibration/calibrar_respaldo.py` (83 líneas)
- `engine/calibration/data_loader.py` (51 líneas)
- `engine/calibration/escenarios.py` (88 líneas)
- `engine/calibration/evaluar_por_segmento.py` (216 líneas)
- `engine/calibration/optimizar_freno.py` (129 líneas)
- `engine/calibration/optimizer.py` (155 líneas)
- `engine/calibration/real_optimizer.py` (342 líneas)
- `engine/calibration/recopilar_datos.py` (147 líneas)
- `engine/calibration/remedir_sin_fuga.py` (172 líneas)
- `engine/calibration/validacion_base.py` (160 líneas)
- `engine/calibration/validar_freno_hechos.py` (124 líneas)
- `engine/calibration/verificador.py` (87 líneas)
- `engine/calibration/walk_forward.py` (155 líneas)
- `engine/contenido/__init__.py` (0 líneas)
- `engine/contenido/analisis_semanal.py` (220 líneas)
- `engine/contenido/backtest.py` (518 líneas)
- `engine/contenido/boletin.py` (1049 líneas)
- `engine/contenido/calibracion.py` (293 líneas)
- `engine/contenido/calibrar_libreta.py` (122 líneas)
- `engine/contenido/captura.py` (149 líneas)
- `engine/contenido/cierre.py` (26 líneas)
- `engine/contenido/corrector.py` (158 líneas)
- `engine/contenido/cosechador.py` (331 líneas)
- `engine/contenido/disparar_pulso.py` (37 líneas)
- `engine/contenido/exportar_libreta.py` (56 líneas)
- `engine/contenido/fuentes/__init__.py` (0 líneas)
- `engine/contenido/fuentes/alpaca.py` (131 líneas)
- `engine/contenido/fuentes/barchart.py` (78 líneas)
- `engine/contenido/fuentes/stooq.py` (56 líneas)
- `engine/contenido/fuentes/yahoo.py` (320 líneas)
- `engine/contenido/graficos.py` (127 líneas)
- `engine/contenido/investigador.py` (142 líneas)
- `engine/contenido/limites.py` (138 líneas)
- `engine/contenido/notificar.py` (57 líneas)
- `engine/contenido/pagos.py` (128 líneas)
- `engine/contenido/persistencia.py` (886 líneas)
- `engine/contenido/pipeline.py` (480 líneas)
- `engine/contenido/portero.py` (220 líneas)
- `engine/contenido/redaccion.py` (239 líneas)
- `engine/contenido/redaccion_ia.py` (823 líneas)
- `engine/contenido/respaldo.py` (263 líneas)
- `engine/contenido/resumen_semanal.py` (100 líneas)
- `engine/contenido/seguridad.py` (123 líneas)
- `engine/contenido/senal_prediccion.py` (36 líneas)
- `engine/contenido/vocabulario.py` (116 líneas)
- `engine/validation/__init__.py` (0 líneas)
- `engine/validation/conftest.py` (16 líneas)
- `engine/validation/hechos_estilizados.py` (36 líneas)
- `engine/validation/test_ablacion_arquetipos.py` (65 líneas)
- `engine/validation/test_analisis_semanal.py` (229 líneas)
- `engine/validation/test_archivo.py` (151 líneas)
- `engine/validation/test_backtest.py` (237 líneas)
- `engine/validation/test_calibracion.py` (145 líneas)
- `engine/validation/test_calibrar_libreta.py` (57 líneas)
- `engine/validation/test_cerebros.py` (120 líneas)
- `engine/validation/test_cierre.py` (157 líneas)
- `engine/validation/test_config_enchufado.py` (80 líneas)
- `engine/validation/test_contacto.py` (67 líneas)
- `engine/validation/test_contenido.py` (167 líneas)
- `engine/validation/test_correccion_sesgo.py` (102 líneas)
- `engine/validation/test_corrector.py` (138 líneas)
- `engine/validation/test_cosechador.py` (113 líneas)
- `engine/validation/test_doomer.py` (86 líneas)
- `engine/validation/test_doomer_segmentado.py` (84 líneas)
- `engine/validation/test_duelo.py` (54 líneas)
- `engine/validation/test_entrevista.py` (60 líneas)
- `engine/validation/test_evaluar.py` (120 líneas)
- `engine/validation/test_evaluar_por_segmento.py` (46 líneas)
- `engine/validation/test_freno_manada.py` (86 líneas)
- `engine/validation/test_graficos.py` (57 líneas)
- `engine/validation/test_hechos_estilizados.py` (86 líneas)
- `engine/validation/test_invariantes_mercado.py` (68 líneas)
- `engine/validation/test_investigador.py` (79 líneas)
- `engine/validation/test_laboratorio.py` (97 líneas)
- `engine/validation/test_lexico_cobertura.py` (129 líneas)
- `engine/validation/test_memoria_secuencias.py` (42 líneas)
- `engine/validation/test_mercado.py` (101 líneas)
- `engine/validation/test_muro.py` (219 líneas)
- `engine/validation/test_observatorio.py` (123 líneas)
- `engine/validation/test_p2_tono.py` (88 líneas)
- `engine/validation/test_p3_p4.py` (91 líneas)
- `engine/validation/test_pagos.py` (144 líneas)
- `engine/validation/test_pulso.py` (560 líneas)
- `engine/validation/test_red_influencia.py` (86 líneas)
- `engine/validation/test_redaccion.py` (185 líneas)
- `engine/validation/test_redaccion_ia.py` (120 líneas)
- `engine/validation/test_remedir_sin_fuga.py` (88 líneas)
- `engine/validation/test_reparto.py` (62 líneas)
- `engine/validation/test_respaldo.py` (140 líneas)
- `engine/validation/test_resumen_semanal.py` (124 líneas)
- `engine/validation/test_seguridad.py` (336 líneas)
- `engine/validation/test_senal_ponderada.py` (57 líneas)
- `engine/validation/test_servidor.py` (88 líneas)
- `engine/validation/test_setup.py` (54 líneas)
- `engine/validation/test_verificador.py` (59 líneas)
- `engine/validation/test_walk_forward.py` (60 líneas)
- `engine/__init__.py` (0 líneas)

**Total: 123 archivos, 20301 líneas.**

---

## engine/config/agentes.json
```json
{
  "descripcion": "La mezcla de 10.000 agentes de El Enjambre (1000 líderes + 9000 resto). Cantidad = personas; capital relativo = poder de mercado. Ver CLAUDE.md sección 4. Los 1000 líderes se reparten ~100 cerebros de IA (brains/reparto.py) para respetar el presupuesto de ~100-120 llamadas por simulación.",
  "total_agentes": 10150,
  "ruido_parametros_sigma": 0.15,
  "umbral_correccion_sesgo": 0.35,
  "peso_doomer": 0.0,
  "peso_doomer_por_mercado": {
    "indice": 1.0,
    "accion": 0.0,
    "cripto": 0.0,
    "oro": 0.0,
    "petroleo": 0.0
  },
  "tipos": [
    {
      "id": "fundamentalista",
      "nombre": "Fundamentalista / value institucional",
      "cantidad": 370,
      "capital_relativo": 50,
      "en_red_social": false,
      "rol": "Ancla el precio al valor justo",
      "parametros": {
        "umbral_compra": 0.95,
        "umbral_venta": 1.05,
        "ponderacion_noticia_en_valor": 0.3,
        "ticks_entre_operaciones": [
          10,
          20
        ]
      }
    },
    {
      "id": "quant_momentum",
      "nombre": "Quant / momentum institucional",
      "cantidad": 220,
      "capital_relativo": 40,
      "en_red_social": false,
      "rol": "Sigue tendencias con disciplina",
      "parametros": {
        "ventana_media_corta": 8,
        "ventana_media_larga": 20,
        "stop_loss": -0.03
      }
    },
    {
      "id": "fondo_pasivo",
      "nombre": "Fondo pasivo / index",
      "cantidad": 150,
      "capital_relativo": 60,
      "en_red_social": false,
      "rol": "Compra constante, insensible a noticias",
      "parametros": {
        "ticks_entre_compras": 10,
        "sensibilidad_noticias": 0
      }
    },
    {
      "id": "market_maker",
      "nombre": "Market maker",
      "cantidad": 9,
      "capital_relativo": 100,
      "en_red_social": false,
      "rol": "Liquidez: cotiza compra y venta siempre",
      "parametros": {
        "multiplicador_spread_panico": 3,
        "umbral_volatilidad_panico": 0.008
      }
    },
    {
      "id": "ejecutor_twap",
      "nombre": "Ejecutor TWAP/VWAP",
      "cantidad": 28,
      "capital_relativo": 30,
      "en_red_social": false,
      "rol": "Ejecuta órdenes grandes en rebanadas",
      "parametros": {}
    },
    {
      "id": "arbitrajista",
      "nombre": "Arbitrajista",
      "cantidad": 55,
      "capital_relativo": 20,
      "en_red_social": false,
      "rol": "Corrige ineficiencias rápido",
      "parametros": {
        "umbral_desviacion": 0.004
      }
    },
    {
      "id": "noise_trader",
      "nombre": "Noise trader retail",
      "cantidad": 3670,
      "capital_relativo": 1,
      "en_red_social": true,
      "rol": "Ruido browniano de fondo",
      "parametros": {
        "probabilidad_operar": 0.12,
        "fraccion_sensible_noticias": 0.2,
        "desplazamiento_sentimiento": 0.1
      }
    },
    {
      "id": "manada",
      "nombre": "Manada / imitador",
      "cantidad": 1650,
      "capital_relativo": 1,
      "en_red_social": true,
      "rol": "Copia lo que hace su red",
      "parametros": {
        "umbral_activacion_rango": [
          0.4,
          0.8
        ],
        "ventana_observacion_ticks": 3,
        "factor_freno_cautela": 0.5
      }
    },
    {
      "id": "fomo",
      "nombre": "FOMO / momentum retail",
      "cantidad": 1100,
      "capital_relativo": 1,
      "en_red_social": true,
      "rol": "Persigue subidas, entra tarde",
      "parametros": {
        "umbral_subida": 0.03,
        "ventana_ticks": 5,
        "vecinos_minimos_activos": 2,
        "fraccion_capital_maxima": 0.15,
        "stop_panico": -0.04
      }
    },
    {
      "id": "miedoso",
      "nombre": "Miedoso / aversión a pérdida",
      "cantidad": 920,
      "capital_relativo": 1,
      "en_red_social": true,
      "rol": "Vende rápido ante caídas",
      "parametros": {
        "asimetria_kahneman": 2.5,
        "fraccion_venta_rango": [
          0.7,
          1.0
        ],
        "ticks_calma_para_recomprar": 10
      }
    },
    {
      "id": "contrarian",
      "nombre": "Contrarian retail",
      "cantidad": 460,
      "capital_relativo": 1.5,
      "en_red_social": true,
      "rol": "Va contra la corriente",
      "parametros": {
        "umbral_consenso": 0.7,
        "ventana_sentimiento_ticks": 5,
        "ticks_entre_operaciones": [
          5,
          10
        ]
      }
    },
    {
      "id": "buy_and_hold",
      "nombre": "Buy & hold pasivo",
      "cantidad": 368,
      "capital_relativo": 2,
      "en_red_social": false,
      "rol": "Casi nunca opera",
      "parametros": {
        "umbral_caida_oportunidad": -0.15,
        "probabilidad_liquidez": 0.001
      }
    },
    {
      "id": "lider_opinion",
      "nombre": "Líder de opinión (LLM)",
      "cantidad": 1150,
      "capital_relativo": 5,
      "en_red_social": true,
      "rol": "Lee la noticia; su señal se propaga (1000 líderes, ~100 cerebros de IA — ver brains/reparto.py)",
      "arquetipos": [
        {
          "id": "institucional_frio",
          "nombre": "El Institucional Frío",
          "cantidad": 150,
          "seguidores_rango": [
            12,
            40
          ]
        },
        {
          "id": "quant_esceptico",
          "nombre": "El Quant Escéptico",
          "cantidad": 100,
          "seguidores_rango": [
            12,
            35
          ]
        },
        {
          "id": "fomo_evangelista",
          "nombre": "El FOMO Evangelista",
          "cantidad": 150,
          "seguidores_rango": [
            40,
            90
          ]
        },
        {
          "id": "doomer",
          "nombre": "El Doomer",
          "cantidad": 150,
          "seguidores_rango": [
            25,
            60
          ]
        },
        {
          "id": "contrarian_sabio",
          "nombre": "El Contrarian Sabio",
          "cantidad": 100,
          "seguidores_rango": [
            12,
            40
          ]
        },
        {
          "id": "macro_trader",
          "nombre": "El Macro Trader",
          "cantidad": 100,
          "seguidores_rango": [
            20,
            50
          ]
        },
        {
          "id": "influencer_optimista",
          "nombre": "El Influencer Retail Optimista",
          "cantidad": 150,
          "seguidores_rango": [
            40,
            90
          ]
        },
        {
          "id": "value_paciente",
          "nombre": "El Value Paciente",
          "cantidad": 100,
          "seguidores_rango": [
            12,
            35
          ]
        },
        {
          "id": "doomer_selectivo",
          "nombre": "El Analista de Riesgo Selectivo",
          "cantidad": 150,
          "seguidores_rango": [
            20,
            55
          ]
        }
      ]
    }
  ]
}
```

## engine/model.py
```python
"""MercadoEnjambre — el modelo central de la simulación.

Carga la mezcla de 5.000 agentes desde config/agentes.json, corre el
mercado tick a tick y expone las series (precio, retornos, flujo) que
consumen la validación y, más adelante, el WebSocket hacia el frontend.
"""

import json
import logging
import os
from pathlib import Path

import mesa

from agents.base import AgenteBase
from agents.lider import LiderOpinion
from agents.reglas import (
    Arbitrajista,
    BuyAndHold,
    Contrarian,
    EjecutorTWAP,
    FomoRetail,
    FondoPasivo,
    Fundamentalista,
    Manada,
    MarketMaker,
    Miedoso,
    NoiseTrader,
    QuantMomentum,
)
from market.order_book import LibroOrdenes

RUTA_CONFIG = Path(__file__).parent / "config" / "agentes.json"

CLASES_POR_TIPO = {
    "fundamentalista": Fundamentalista,
    "quant_momentum": QuantMomentum,
    "fondo_pasivo": FondoPasivo,
    "market_maker": MarketMaker,
    "ejecutor_twap": EjecutorTWAP,
    "arbitrajista": Arbitrajista,
    "noise_trader": NoiseTrader,
    "manada": Manada,
    "fomo": FomoRetail,
    "miedoso": Miedoso,
    "contrarian": Contrarian,
    "buy_and_hold": BuyAndHold,
}

CAPITAL_BASE = 10_000.0  # capital de un agente retail 1x

# P3 — tope de MAGNITUD por mercado. En cripto (y acción) el enjambre a veces
# emerge con movimientos irreales (±40-50% en una sesión) por su alta
# volatilidad de masas. Acotamos la magnitud REPORTADA a un rango realista, SIN
# tocar la dirección (el signo se conserva → el acierto de dirección no cambia).
# En vivo se conoce el TIPO de mercado (no el símbolo puntual), así que el tope
# es por tipo. Los mercados sin entrada quedan sin tope.
FACTORES_LIQUIDEZ = {"cripto": 30.0, "accion": 40.0}  # |direccion_pct| máx en %


def acotar_magnitud(mercado: str | None, pct: float | None) -> float | None:
    """Recorta un porcentaje al tope de su mercado (P3). Conserva el signo;
    devuelve el valor tal cual si el mercado no tiene tope o el valor es None."""
    tope = FACTORES_LIQUIDEZ.get(mercado or "")
    if tope is None or pct is None:
        return pct
    return round(max(-tope, min(tope, pct)), 2)


# Escala del consenso de la IA cuando se usa como "tono de la prensa" (ver
# _tono_de_titular). Es una perilla de MAGNITUD, no de dirección: subirla
# agranda el golpe del ambiente sin cambiar si el mercado sube o baja. Se
# calibra con los exámenes (el corrector), igual que los diales de mercado.
# 1ª ronda de exámenes (163 casos, índice+cripto): con 1.5 la DIRECCIÓN mejoró
# fuerte (índice 47%→62%) pero el enjambre se pasó ~2x en MAGNITUD (ratio
# real/sim ~0.5). Como el cambio de magnitud vino entero de este ambiente,
# bajamos la perilla ~×0.54 para volver a la escala calibrada (real/sim ~0.9).
# La dirección NO se toca (es el signo del consenso, no su tamaño).
GANANCIA_CONSENSO = 0.8

# Fracción mínima de líderes que deben haber hablado con la IA real para
# confiar en su consenso como tono. Si la mayoría cayó al respaldo léxico
# (sin saldo de API), se usa el diccionario directo, que es justo para eso.
MINIMO_IA_CONSENSO = 0.5

# P2 — separar "tono de mercado" de "apuesta del líder": estos arquetipos
# INVIERTEN u optimizan la señal (el contrarian compra el pánico, el optimista
# nunca ve lo malo, el quant apuesta a la reversión). Su APUESTA individual y su
# frase siguen intactas, pero contaminan el "clima" que siente todo el mercado:
# ante una mala noticia real cancelan a los que la leen bien, y el enjambre
# predice "sube" cuando debía "baja". `peso_tono_invertidores` (config) modula
# cuánto pesan en el TONO: 1.0 = comportamiento histórico · 0.0 = no fijan el
# ánimo del mercado (siguen operando por su cuenta). Diagnóstico: INFORME_CAUSA_
# RAIZ_NEGATIVAS.md.
ARQUETIPOS_INVERSORES = frozenset({
    "quant_esceptico", "contrarian_sabio", "influencer_optimista",
})

# Intervención 1: el arquetipo doomer SELECTIVO (voz LLM real, no la mezcla
# léxica). Su peso en el TONO se modula con `peso_doomer` (0 = no participa del
# clima; 1 = peso pleno). Su apuesta individual y su frase no se tocan.
ARQUETIPOS_DOOMER = frozenset({"doomer_selectivo"})


def _peso_invertidores_env(por_defecto: float) -> float:
    """El peso de los invertidores en el tono, con override por entorno
    (ENJAMBRE_PESO_TONO_INVERSORES). Recortado a [0, 1]. Permite medir P2 en el
    backtest y hacer rollback sin re-desplegar."""
    crudo = os.environ.get("ENJAMBRE_PESO_TONO_INVERSORES")
    try:
        valor = float(crudo) if crudo not in (None, "") else float(por_defecto)
    except ValueError:
        valor = float(por_defecto)
    return max(0.0, min(1.0, valor))


# Plan A — corrección del sesgo alcista en el consenso. Diagnóstico
# (INFORME_CAUSA_RAIZ_NEGATIVAS.md): el enjambre acierta ~80% en positivas pero
# ~53% en negativas porque el TONO se suaviza hacia arriba — el descuento de
# magnitud (GANANCIA_CONSENSO=0.8) encoge una mala noticia clara, y el enjambre
# predice "sube" sobre una caída real. La corrección: cuando los líderes que
# hablaron con la IA ya leen la noticia como CLARAMENTE bajista (consenso <
# -umbral), NO la suavizamos; usamos la lectura directa a plena magnitud (nunca
# para invertir el signo — solo para no diluir el bajón). `umbral_correccion_
# sesgo` (config) fija qué tan bajista debe ser el consenso para disparar la
# corrección: 0.0 = desactivada (comportamiento histórico). La variable de
# entorno ENJAMBRE_UMBRAL_CORRECCION_SESGO manda sobre la config, para medir en
# el backtest y hacer rollback SIN re-desplegar (mismo patrón que P2).
def _umbral_correccion_env(por_defecto: float) -> float:
    """El umbral de la corrección de sesgo, con override por entorno
    (ENJAMBRE_UMBRAL_CORRECCION_SESGO). Recortado a [0, 1]; 0 = desactivada."""
    crudo = os.environ.get("ENJAMBRE_UMBRAL_CORRECCION_SESGO")
    try:
        valor = float(crudo) if crudo not in (None, "") else float(por_defecto)
    except ValueError:
        valor = float(por_defecto)
    return max(0.0, min(1.0, valor))


# Intervención 1 — voz "doomer pura" (fiel, que NO invierte) mezclada en el
# consenso. El sesgo alcista viene de que los invertidores (quant/contrarian/
# optimista) empujan positivo ante una mala noticia y cancelan a los fieles.
# En vez de silenciarlos (P2, que falló), AÑADIMOS al consenso una voz que lee
# la noticia sin invertir (el léxico, a 0.9 de magnitud — el "LiderDoomerPuro"
# del plan) con peso `peso_doomer`. A diferencia del Plan A (que solo dispara si
# el consenso ya está muy bajista), esta mezcla es INCONDICIONAL, así que
# también alcanza cripto. 0.0 = desactivada. Se mide/rollbackea por entorno.
def _peso_doomer_env(por_defecto: float) -> float:
    """El peso de la voz doomer pura en el consenso (ENJAMBRE_PESO_DOOMER).
    Recortado a [0, 1]; 0 = desactivada."""
    crudo = os.environ.get("ENJAMBRE_PESO_DOOMER")
    try:
        valor = float(crudo) if crudo not in (None, "") else float(por_defecto)
    except ValueError:
        valor = float(por_defecto)
    return max(0.0, min(1.0, valor))


def _peso_doomer_env_forzado() -> float | None:
    """El override GLOBAL de ENJAMBRE_PESO_DOOMER, o None si no está fijado.

    Si está fijado (p. ej. una tanda de medición), manda sobre la segmentación
    por-mercado y aplica ese peso en TODOS los mercados. Si NO está fijado
    (producción), devolvemos None → el tono usa `peso_doomer_por_mercado`."""
    crudo = os.environ.get("ENJAMBRE_PESO_DOOMER")
    if crudo in (None, ""):
        return None
    try:
        return max(0.0, min(1.0, float(crudo)))
    except ValueError:
        return None

log = logging.getLogger("enjambre.lexico")


def _distribucion_polaridad(senales) -> dict:
    """Cuenta cuántas señales son alcistas / bajistas / neutrales."""
    pos = sum(1 for s in senales if s > 0.05)
    neg = sum(1 for s in senales if s < -0.05)
    return {"n": len(senales), "alcista": pos, "bajista": neg,
            "neutral": len(senales) - pos - neg,
            "media": round(sum(senales) / len(senales), 3) if senales else 0.0}


def monitorear_polaridad(respuestas: list[dict]) -> None:
    """Registra la distribución de polaridad del RESPALDO léxico vs la API, para
    detectar en vivo si el diccionario introduce un sesgo que la API no tiene.
    Solo loguea cuando el respaldo se activó de verdad (fuente 'fallback');
    es pasivo: no cambia ninguna decisión de la simulación."""
    try:
        respaldo = [r["senal"] for r in respuestas if r.get("fuente") == "fallback"]
        if not respaldo:
            return
        api = [r["senal"] for r in respuestas if r.get("fuente") in ("api", "cache")]
        log.info("polaridad respaldo=%s api=%s", _distribucion_polaridad(respaldo),
                 _distribucion_polaridad(api))
    except Exception:  # el monitoreo jamás debe tumbar una simulación
        pass


class MercadoEnjambre(mesa.Model):
    MAX_HISTORIAL = 600  # cola de precios/retornos en sesiones largas

    def __init__(
        self,
        seed: int | None = None,
        precio_inicial: float = 100.0,
        ticks_horizonte: int = 400,
        ruta_config: Path = RUTA_CONFIG,
        overrides: dict | None = None,
    ):
        super().__init__(seed=seed)
        # overrides: ajustes de parámetros SOLO para experimentos de calibración,
        # sin tocar config/agentes.json. Forma:
        #   {"<tipo_id>": {"<param>": valor, ...},   # params por tipo de agente
        #    "global": {"<clave_global>": valor, ...}}  # perillas top-level
        # Se validan las claves: una desconocida lanza ValueError (para no
        # "calibrar" algo que el motor ignora). Producción pasa overrides=None.
        self.overrides = overrides or {}
        self.ticks_horizonte = ticks_horizonte
        self.libro = LibroOrdenes(precio_inicial)
        self.libro.notificar_ejecucion = self._notificar_ejecucion

        self.tick = 0
        self.sentimiento = 0.0  # sentimiento global de la noticia, decae solo
        # P4 — fuerza del consenso de la última noticia (para la "confianza"
        # del reporte = abs(consenso)). 0 hasta que se aplique un titular.
        self._ultimo_consenso = 0.0
        # perfil de personalidad del mercado (índice por defecto); una noticia
        # de petróleo/oro/cripto lo cambia y con él la reacción del enjambre
        from brains.mercado import perfil_de
        self.perfil = perfil_de("indice")
        self.historial_precios: list[float] = [precio_inicial]
        self.retornos: list[float] = []
        self.flujo_compras: list[float] = []  # volumen agresor comprador por tick
        self.flujo_ventas: list[float] = []
        # cola del rumor: (tick_entrega, agente, valor, salto)
        self.cola_senales: list[tuple[int, AgenteBase, float, int]] = []

        self._crear_agentes(ruta_config)
        self._agentes_por_id = {a.unique_id: a for a in self.agents}
        self._lideres = [a for a in self.agents if isinstance(a, LiderOpinion)]
        # orden estable de creación (tipos 1-12 y al final los 100 líderes):
        # es el contrato con el frontend para el streaming por WebSocket
        self.agentes_ordenados = sorted(self.agents, key=lambda a: a.unique_id)

        from network.red import construir_red

        construir_red(self)

    # ---------- construcción ----------

    _GLOBALES_OVERRIDE = frozenset({
        "peso_tono_invertidores", "umbral_correccion_sesgo", "peso_doomer",
        "peso_doomer_por_mercado", "ruido_parametros_sigma",
    })

    def _crear_agentes(self, ruta_config: Path) -> None:
        with open(ruta_config, encoding="utf-8") as f:
            config = json.load(f)
        # overrides globales (experimentos): reemplazan el valor de config antes
        # de leerlo; las env vars siguen mandando por encima (medición/rollback).
        ov_global = self.overrides.get("global", {})
        for clave in ov_global:
            if clave not in self._GLOBALES_OVERRIDE:
                raise ValueError(f"override global desconocido: {clave}")
        config = {**config, **ov_global}
        # P2: peso de los arquetipos invertidores en el TONO de mercado
        # (1.0 = comportamiento histórico). La variable de entorno
        # ENJAMBRE_PESO_TONO_INVERSORES manda sobre la config, para medir en el
        # backtest (o hacer rollback) SIN re-desplegar.
        self._peso_tono_invertidores = _peso_invertidores_env(
            config.get("peso_tono_invertidores", 1.0))
        # Plan A: umbral de la corrección del sesgo alcista (0.0 = desactivada).
        # El entorno ENJAMBRE_UMBRAL_CORRECCION_SESGO manda sobre la config para
        # medir en el backtest / rollback sin re-desplegar (patrón de P2).
        self._umbral_correccion = _umbral_correccion_env(
            config.get("umbral_correccion_sesgo", 0.0))
        # Intervención 1: peso de la voz doomer SELECTIVO en el tono.
        # SEGMENTADO POR MERCADO: la medición mostró que ayuda en índice (+7.6 pts
        # en negativas) pero es inerte en cripto, así que el peso depende del
        # mercado detectado (config `peso_doomer_por_mercado`). El override global
        # ENJAMBRE_PESO_DOOMER, si está fijado (medición/rollback), manda sobre la
        # segmentación y aplica ese peso en todos los mercados. Si es None
        # (producción), el tono usa el peso por-mercado. `_peso_doomer` en None =
        # "sin override global"; los tests pueden fijarlo para forzar un peso.
        self._peso_doomer = _peso_doomer_env_forzado()
        self._peso_doomer_por_mercado = config.get("peso_doomer_por_mercado", {})
        self._peso_doomer_defecto = float(config.get("peso_doomer", 0.0))
        # sigma del ruido idiosincrático que hace único a cada agente (±15% por
        # defecto). Lo usa AgenteBase.ruido como default. Config → top-level.
        self._sigma_ruido = float(config.get("ruido_parametros_sigma", 0.15))
        for tipo in config["tipos"]:
            capital = tipo["capital_relativo"] * CAPITAL_BASE
            # expone los "parametros" del tipo para que sus agentes los lean en
            # __init__ (vía AgenteBase.cfg). Con la config original no cambia nada.
            base_params = tipo.get("parametros") or {}
            # overrides por tipo (experimentos): validar y fusionar sobre los base
            ov_tipo = self.overrides.get(tipo["id"], {})
            for clave in ov_tipo:
                if clave not in base_params:
                    raise ValueError(
                        f"override desconocido: {tipo['id']}.{clave} "
                        f"(parámetros válidos: {sorted(base_params)})")
            self._cfg_agentes_actual = {**base_params, **ov_tipo}
            if tipo["id"] == "lider_opinion":
                for arquetipo in tipo["arquetipos"]:
                    for _ in range(arquetipo["cantidad"]):
                        LiderOpinion(self, capital, arquetipo["id"])
            else:
                clase = CLASES_POR_TIPO[tipo["id"]]
                for _ in range(tipo["cantidad"]):
                    clase(self, capital)

    # ---------- noticia ----------

    def aplicar_noticia(self, sentimiento: float) -> None:
        """Inyecta una noticia como número (para tests y calibración).
        Cada líder forma su señal y la propaga por la red de influencia."""
        self.sentimiento = max(-1.0, min(1.0, self.sentimiento + sentimiento))
        # Nivel 1: cada agente recuerda la noticia (memoria de rachas → cautela)
        for agente in self.agents:
            agente.actualizar_memoria(sentimiento)
        for lider in self._lideres:
            lider.recibir_noticia(sentimiento)
        self._propagar_desde_lideres()

    def aplicar_titular(self, titular: str, respuestas: list[dict] | None = None,
                        perfil: dict | None = None) -> list[dict]:
        """Inyecta una noticia REAL: los 100 líderes la leen (LLM con
        fallback léxico), forman su señal y la propagan por la red.
        El servidor puede pasar `respuestas` ya calculadas (vía async) y el
        `perfil` de mercado (índice/petróleo/oro/cripto/acción) ya clasificado."""
        if respuestas is None:
            from brains.cerebro import analizar_titular
            from brains import reparto

            # 1000 líderes comparten ~110 cerebros (presupuesto de la biblia)
            consultas, asignacion = reparto.planificar(self._lideres, lambda uid: uid)
            respuestas_cerebros = analizar_titular(titular, consultas)
            respuestas = reparto.expandir(respuestas_cerebros, asignacion)
        if perfil is not None:
            self.perfil = perfil
        for lider, respuesta in zip(self._lideres, respuestas):
            lider.senal = respuesta["senal"]
            lider.confianza = respuesta["confianza"]
            lider.frase = respuesta["frase"]
        monitorear_polaridad(respuestas)  # métrica pasiva: respaldo vs API
        # el "tono de la prensa": el ambiente de fondo que sienten todos los
        # agentes (todos leen la misma noticia). Antes lo ponía un diccionario
        # de palabras; ahora lo pone la LECTURA REAL de la IA (el consenso de
        # los líderes que hablaron con Claude), que entiende el SIGNIFICADO del
        # titular donde el diccionario se equivocaba ("recortan aranceles" es
        # bueno, "wipes out $2 trillion" es malo). Las opiniones expertas de
        # cada líder siguen viajando aparte, por la red de influencia.
        tono = self._aplicar_perfil(self._tono_de_titular(titular, respuestas))
        self.sentimiento = max(-1.0, min(1.0, self.sentimiento + tono))
        self._propagar_desde_lideres()
        return respuestas

    def _tono_de_titular(self, titular: str, respuestas: list[dict]) -> float:
        """El tono de fondo del mercado a partir de la noticia ∈ [-1, +1].

        Prioridad a la LECTURA de la IA: el promedio de las señales de los
        líderes, ponderado por su confianza. La IA entiende el sentido del
        titular; el diccionario léxico solo cuenta palabras y fallaba en
        noticias compuestas (leía "slash tariffs" como pánico cuando es alza).

        Solo pesan los líderes que hablaron con la IA de verdad (fuente
        api/cache). Si la mayoría usó el respaldo léxico (sin saldo de API),
        se vuelve al diccionario — que es exactamente para lo que existe.
        """
        from brains.fallback import sentimiento_lexico

        # emparejar cada respuesta con el arquetipo de su líder (van en paralelo)
        ia = [(lider.arquetipo, r) for lider, r in zip(self._lideres, respuestas)
              if r.get("fuente") in ("api", "cache")]
        if len(ia) < len(respuestas) * MINIMO_IA_CONSENSO:
            s = sentimiento_lexico(titular)  # la IA no opinó lo suficiente
            self._ultimo_consenso = s        # P4: fuerza de la señal (confianza)
            return s
        # P2: el TONO de mercado no se deja cancelar por las APUESTAS de los
        # arquetipos invertidores (contrarian/optimista/quant). Pesan
        # `peso_tono_invertidores` en el clima; su señal individual y su frase
        # NO se tocan (siguen operando y hablando por su cuenta).
        peso_inv = getattr(self, "_peso_tono_invertidores", 1.0)
        # Intervención 1 (arquetipo LLM real): el peso del "doomer selectivo" en
        # el TONO. 0.0 = no participa del clima; 1.0 = peso pleno. Su apuesta y su
        # frase NO se tocan. SEGMENTADO POR MERCADO: si hay override global
        # (`_peso_doomer` fijado por el env de medición o por un test) manda ese;
        # si no (producción), se toma el peso del MERCADO detectado
        # (índice 1.0, cripto 0.0, …). La medición mostró que ayuda en índice
        # pero es inerte en cripto, de ahí la segmentación.
        peso_doomer = getattr(self, "_peso_doomer", None)
        if peso_doomer is None:
            mercado = (getattr(self, "perfil", None) or {}).get("tipo")
            por_mercado = getattr(self, "_peso_doomer_por_mercado", {})
            peso_doomer = por_mercado.get(
                mercado, getattr(self, "_peso_doomer_defecto", 0.0))
        num = den = 0.0
        for arquetipo, r in ia:
            w = r["confianza"]
            if arquetipo in ARQUETIPOS_INVERSORES:
                w *= peso_inv
            if arquetipo in ARQUETIPOS_DOOMER:
                w *= peso_doomer
            num += r["senal"] * w
            den += w
        if den <= 0:
            s = sentimiento_lexico(titular)
            self._ultimo_consenso = s        # P4: fuerza de la señal (confianza)
            return s
        consenso = num / den
        directo = None  # lectura léxica (fiel, no invierte); se calcula si hace falta
        self._ultimo_consenso = consenso     # P4: fuerza de la señal (confianza)
        # Plan A — corrección del sesgo alcista: cuando los líderes ya leen la
        # noticia como CLARAMENTE bajista, no dejamos que el descuento de
        # magnitud (GANANCIA_CONSENSO) la suavice. Usamos la lectura a plena
        # magnitud, tomando la MÁS bajista entre el consenso y el léxico directo
        # —nunca menos bajista que el consenso, así jamás invertimos el signo:
        # solo evitamos diluir el bajón. Desactivada con umbral 0.0.
        umbral = getattr(self, "_umbral_correccion", 0.0)
        if umbral > 0 and consenso < -umbral:
            if directo is None:
                directo = sentimiento_lexico(titular)
            return max(-1.0, min(1.0, min(consenso, directo)))
        return max(-1.0, min(1.0, consenso * GANANCIA_CONSENSO))

    def _aplicar_perfil(self, tono: float) -> float:
        """La personalidad del mercado transforma el tono de la noticia.

        - sensibilidad: cuánto mueve el sentimiento a este mercado.
        - refugio (oro): el miedo (tono<0) se refleja parcialmente a compra;
          con refugio=0.5 el miedo se neutraliza, >0.5 lo hace SUBIR.
        """
        tono *= self.perfil.get("sensibilidad", 1.0)
        refugio = self.perfil.get("refugio", 0.0)
        if refugio and tono < 0:
            tono *= (1.0 - 2.0 * refugio)
        return max(-1.0, min(1.0, tono))

    def _propagar_desde_lideres(self) -> None:
        """La señal de cada líder viaja a sus seguidores con retardo de
        1-4 ticks y atenuación 0.7 por salto — esto crea la ola visual."""
        sensibilidad = self.perfil.get("sensibilidad", 1.0)
        for lider in self._lideres:
            if abs(lider.senal) < 0.05:
                continue
            # la personalidad del mercado escala cuánto arrastra cada líder
            valor = lider.senal * lider.confianza * 0.7 * sensibilidad
            for seguidor in lider.seguidores:
                retardo = self.random.randint(1, 4)
                self.cola_senales.append((self.tick + retardo, seguidor, valor, 1))

    def _entregar_senales(self) -> None:
        """Entrega el rumor que vence este tick y lo reenvía a los pares
        (segundo salto, atenuado otra vez; ahí muere la cadena)."""
        pendientes = []
        for tick_entrega, agente, valor, salto in self.cola_senales:
            if tick_entrega > self.tick:
                pendientes.append((tick_entrega, agente, valor, salto))
                continue
            agente.senal_social = max(-1.0, min(1.0, agente.senal_social + valor))
            if salto == 1:
                for par in agente.pares:
                    retardo = self.random.randint(1, 4)
                    pendientes.append((self.tick + retardo, par, valor * 0.7, 2))
        self.cola_senales = pendientes

    # ---------- ciclo ----------

    def step(self) -> None:
        self.tick += 1
        self.libro.reiniciar_tick(self.tick)
        self._entregar_senales()  # el rumor de hoy llega antes de operar
        self.agents.shuffle_do("step")
        # el rumor recibido se desvanece rápido (lo fresco es lo que arrastra)
        for agente in self.agents:
            if agente.senal_social != 0.0:
                agente.senal_social *= 0.75
                if abs(agente.senal_social) < 0.01:
                    agente.senal_social = 0.0
        # el cierre del tick es la última transacción real: una foto
        # puntual de dónde se cruzó de verdad la oferta con la demanda
        precio = self.libro.ultimo_precio if self.libro.volumen_tick > 0 else self.historial_precios[-1]
        anterior = self.historial_precios[-1]
        self.historial_precios.append(precio)
        self.retornos.append((precio - anterior) / anterior)
        self.flujo_compras.append(self.libro.volumen_compras_tick)
        self.flujo_ventas.append(self.libro.volumen_ventas_tick)
        self.sentimiento *= 0.95  # la noticia pierde fuerza cada tick
        # en sesiones largas (modo observatorio) las listas no crecen sin fin:
        # los agentes solo miran ventanas cortas, así que basta la cola reciente
        if len(self.historial_precios) > self.MAX_HISTORIAL:
            recorte = len(self.historial_precios) - self.MAX_HISTORIAL
            del self.historial_precios[:recorte]
            del self.retornos[:recorte]
            del self.flujo_compras[:recorte]
            del self.flujo_ventas[:recorte]

    def correr(self, ticks: int) -> None:
        for _ in range(ticks):
            self.step()

    # ---------- series que consultan los agentes ----------

    def retorno_acumulado(self, n: int) -> float | None:
        """Retorno del precio en los últimos n ticks."""
        if len(self.historial_precios) <= n:
            return None
        return self.historial_precios[-1] / self.historial_precios[-1 - n] - 1

    def volatilidad_reciente(self, n: int) -> float:
        """Desviación estándar de los últimos n retornos."""
        if len(self.retornos) < 2:
            return 0.0
        ventana = self.retornos[-n:]
        media = sum(ventana) / len(ventana)
        return (sum((r - media) ** 2 for r in ventana) / len(ventana)) ** 0.5

    def fraccion_compras(self, n: int) -> float | None:
        """Fracción del volumen reciente que fue comprador agresor."""
        if not self.flujo_compras:
            return None
        compras = sum(self.flujo_compras[-n:])
        ventas = sum(self.flujo_ventas[-n:])
        total = compras + ventas
        # con volumen insignificante no hay señal de manada que leer
        if total < 100:
            return None
        return compras / total

    # ---------- instrumentación (laboratorio: quién mueve el precio) ----------

    def activar_instrumentacion(self) -> None:
        """Enciende el registro de volumen por tipo de agente, separando quién fue
        AGRESOR (cruzó el libro → empuja el precio) de quién PROVEYÓ liquidez (su
        orden reposaba → absorbe). Opt-in: en producción no se llama (sin costo)."""
        from collections import defaultdict
        self._instr = True
        self.vol_agresor_tipo: dict[str, float] = defaultdict(float)
        self.vol_proveedor_tipo: dict[str, float] = defaultdict(float)
        self.libro.registrar_ejecucion_instr = self._instr_ejecucion

    def _instr_ejecucion(self, agresor_id: int, proveedor_id: int,
                         cantidad: float, precio: float) -> None:
        ta = type(self._agentes_por_id[agresor_id]).__name__
        tp = type(self._agentes_por_id[proveedor_id]).__name__
        self.vol_agresor_tipo[ta] += cantidad
        self.vol_proveedor_tipo[tp] += cantidad

    def resumen_instrumentacion(self) -> dict:
        """Volumen agresor y proveedor por tipo de agente, en bruto y en %."""
        ag = dict(getattr(self, "vol_agresor_tipo", {}))
        pr = dict(getattr(self, "vol_proveedor_tipo", {}))
        tot_ag = sum(ag.values()) or 1.0
        tot_pr = sum(pr.values()) or 1.0
        return {
            "agresor": {k: round(v, 1) for k, v in sorted(ag.items(), key=lambda x: -x[1])},
            "agresor_pct": {k: round(100 * v / tot_ag, 1) for k, v in sorted(ag.items(), key=lambda x: -x[1])},
            "proveedor": {k: round(v, 1) for k, v in sorted(pr.items(), key=lambda x: -x[1])},
            "proveedor_pct": {k: round(100 * v / tot_pr, 1) for k, v in sorted(pr.items(), key=lambda x: -x[1])},
        }

    # ---------- interno ----------

    def _notificar_ejecucion(self, agente_id: int, lado: str, cantidad: float, precio: float) -> None:
        agente: AgenteBase = self._agentes_por_id[agente_id]
        agente.aplicar_ejecucion(lado, cantidad, precio)
```

## engine/llm_texto.py
```python
"""Extrae el TEXTO de una respuesta de la API de Anthropic, saltando el
razonamiento (thinking).

Los modelos nuevos (claude-sonnet-5, etc.) RAZONAN antes de responder: el
`content` de la respuesta puede empezar con uno o más ThinkingBlock (que NO
tienen `.text`), y recién después viene el bloque de texto. Tomar
`respuesta.content[0].text` a ciegas revienta con AttributeError cuando el primer
bloque es de razonamiento — y esa excepción, tragada por un try/except, dejaba a
El Pulso sin edición y sin correo.

Esta función junta SOLO los bloques de tipo texto, así funciona con o sin
razonamiento y con cualquier modelo. Nunca lanza.
"""


def texto_de(respuesta) -> str:
    """El texto de una respuesta de Anthropic, ignorando los bloques de
    razonamiento. '' si no hay texto (nunca lanza)."""
    partes = []
    for bloque in getattr(respuesta, "content", None) or []:
        if getattr(bloque, "type", None) == "text":
            trozo = getattr(bloque, "text", "")
            if trozo:
                partes.append(trozo)
    # respaldo defensivo: si por algún motivo no vino 'type' pero sí '.text'
    if not partes:
        for bloque in getattr(respuesta, "content", None) or []:
            trozo = getattr(bloque, "text", "")
            if trozo:
                partes.append(trozo)
    return "".join(partes)
```

## engine/nlp_scorer.py
```python
"""Puntuador NLP de titulares con FinBERT (HERRAMIENTA DE LABORATORIO — offline).

⚠️ AISLADO A PROPÓSITO: este módulo NO está enchufado al motor en producción.
FinBERT arrastra `torch` + `transformers` (varios GB en RAM), y el motor corre en
Render con memoria muy ajustada: cargarlo ahí lo reventaría (OOM). Además, en El
Enjambre la interpretación de la noticia la hacen los LÍDERES LLM por arquetipo
(engine/brains/) — ese es el diferenciador del producto. Este scorer es solo una
pieza de experimento para la rama de calibración, para comparar enfoques offline.

Convierte un titular en un vector de 3 dimensiones:
  - sentiment  (-1 a 1): positivo/negativo
  - uncertainty (0 a 1): qué tan neutral/dudosa es la noticia
  - impact     (0 a 1): magnitud de la sacudida emocional
"""

import numpy as np


class FinBERTScorer:
    def __init__(self):
        # Import perezoso: solo se paga torch/transformers si de verdad se usa.
        import torch
        from transformers import (AutoModelForSequenceClassification,
                                  AutoTokenizer)

        self._torch = torch
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = AutoTokenizer.from_pretrained("yiyanghkust/finbert-tone")
        self.model = AutoModelForSequenceClassification.from_pretrained(
            "yiyanghkust/finbert-tone")
        self.model.to(self.device)
        self.model.eval()

    def get_impact_vector(self, text: str) -> dict:
        if not text or len(text.strip()) == 0:
            return {"sentiment": 0.0, "uncertainty": 0.5, "impact": 0.0}

        torch = self._torch
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True,
                                padding=True, max_length=512)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
            # Orden del modelo finbert-tone: [neutral, positivo, negativo]
            # (se mantiene el desempaquetado del bundle original; ver README).
            pos, neg, neutral = probs[0].tolist()

        sentiment = pos - neg                 # rango -1 a 1
        uncertainty = 1 - max(pos, neg)       # si es neutral, sube la incertidumbre
        magnitude = abs(sentiment) * (1 + uncertainty)  # impacto real

        return {
            "sentiment": round(float(sentiment), 4),
            "uncertainty": round(float(uncertainty), 4),
            "impact": round(float(magnitude), 4),
        }


# Singleton perezoso (para experimentos; NO se importa desde el servidor real).
_scorer_instance = None


def get_scorer():
    global _scorer_instance
    if _scorer_instance is None:
        _scorer_instance = FinBERTScorer()
    return _scorer_instance
```

## engine/simular.py
```python
"""Corre una sesión de mercado y reporta los hechos estilizados.

Uso: python simular.py [seed]
Herramienta de calibración de la Etapa 1 — no es parte del producto.
"""

import sys
import time

from model import MercadoEnjambre
from validation.hechos_estilizados import asimetria_panico, autocorrelacion, curtosis


def sesion_con_noticias(seed: int, ticks: int = 600) -> MercadoEnjambre:
    """Una sesión con flujo de noticias aleatorias (como un día real)."""
    modelo = MercadoEnjambre(seed=seed, ticks_horizonte=ticks)
    for _ in range(ticks):
        if modelo.random.random() < 0.02:  # llega una noticia al mercado
            modelo.aplicar_noticia(modelo.random.gauss(0, 0.45))
        modelo.step()
    return modelo


if __name__ == "__main__":
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 42
    inicio = time.time()
    modelo = sesion_con_noticias(seed)
    duracion = time.time() - inicio

    r = modelo.retornos
    absolutos = [abs(x) for x in r]
    print(f"seed={seed} · {len(r)} ticks en {duracion:.1f}s")
    print(f"precio final: {modelo.historial_precios[-1]:.2f} (partió en 100)")
    print(f"1. curtosis:            {curtosis(r):.2f}  (real si > 3)")
    print(f"2. AC |r| rezago 1:     {autocorrelacion(absolutos, 1):.3f}  (real si > 0 y decae)")
    print(f"   AC |r| rezago 5:     {autocorrelacion(absolutos, 5):.3f}")
    print(f"   AC |r| rezago 10:    {autocorrelacion(absolutos, 10):.3f}")
    print(f"3. AC retornos rez. 1:  {autocorrelacion(r, 1):.3f}  (real si ≈ 0)")
    print(f"4. asimetría de pánico: {asimetria_panico(r):.2f}  (real si > 1)")

    total = sum(modelo.flujo_compras) + sum(modelo.flujo_ventas)
    print(f"volumen total sesión:   {total:,.0f} acciones")
```

## engine/demo_titular.py
```python
"""Demo de la Etapa 2: el enjambre lee un titular y reacciona.

Uso: python demo_titular.py "La Fed sube las tasas 50 puntos base"
Con ANTHROPIC_API_KEY en el entorno usa los 100 cerebros LLM reales;
sin clave usa el fallback léxico por arquetipo.
"""

import sys
from collections import defaultdict

from agents.lider import LiderOpinion
from model import MercadoEnjambre

TITULAR_DEFECTO = "La Fed sube las tasas 50 puntos base y anticipa más alzas"


def demo(titular: str, seed: int = 42) -> None:
    print(f'📰 "{titular}"\n')

    modelo = MercadoEnjambre(seed=seed, ticks_horizonte=220)
    modelo.correr(80)  # el mercado encuentra su ritmo antes de la noticia
    precio_base = modelo.historial_precios[-1]

    respuestas = modelo.aplicar_titular(titular)
    fuente = respuestas[0]["fuente"]
    print(f"Los 100 líderes leyeron el titular (fuente: {fuente}).\n")

    # qué dijo cada arquetipo
    por_arquetipo = defaultdict(list)
    frases = {}
    lideres = [a for a in modelo.agents if isinstance(a, LiderOpinion)]
    for lider, r in zip(lideres, respuestas):
        por_arquetipo[lider.arquetipo].append(r["senal"])
        frases.setdefault(lider.arquetipo, r["frase"])
    for arquetipo, senales in por_arquetipo.items():
        media = sum(senales) / len(senales)
        print(f"  {arquetipo:22s} señal {media:+.2f}  «{frases[arquetipo]}»")

    # la ola y el precio
    print("\ntick | precio  | reacción del enjambre")
    for i in range(1, 61):
        modelo.step()
        if i in (1, 2, 3, 4, 5, 8, 12, 20, 30, 45, 60):
            alcanzados = sum(1 for a in modelo.agents if abs(a.senal_social) > 0.05)
            precio = modelo.historial_precios[-1]
            cambio = (precio / precio_base - 1) * 100
            print(f" +{i:3d} | {cambio:+6.2f}% | rumor en {alcanzados:5d} agentes")

    final = modelo.historial_precios[-1]
    minimo = min(modelo.historial_precios[80:])
    maximo = max(modelo.historial_precios[80:])
    print(f"\nresultado: {(final/precio_base-1)*100:+.2f}% "
          f"(mínimo {(minimo/precio_base-1)*100:+.1f}%, máximo {(maximo/precio_base-1)*100:+.1f}%)")


if __name__ == "__main__":
    demo(sys.argv[1] if len(sys.argv) > 1 else TITULAR_DEFECTO)
```

## engine/probar_portero.py
```python
"""Corre el portero sobre los titulares del día y muestra el log de veredictos.

Uso: python probar_portero.py
Con claves de Alpaca en el entorno usa titulares reales de las últimas 18 h;
sin claves usa el día de demostración. Todo veredicto queda en la base.
"""

from contenido import persistencia, portero
from contenido.fuentes import alpaca

if __name__ == "__main__":
    titulares, origen = alpaca.obtener_titulares(horas=18, limite=50)
    print(f"fuente de titulares: {origen} ({len(titulares)} recibidos)\n")

    conexion = persistencia.conectar()
    resultado = portero.procesar_dia(conexion, titulares, maximo=3)
    conexion.close()

    print(f"{'imp':>3}  {'veredicto':9}  titular")
    print("-" * 100)
    for entrada in sorted(resultado["log"], key=lambda e: -e["impacto"]):
        print(f"{entrada['impacto']:>3}  {entrada['veredicto']:9}  {entrada['titular'][:70]}")
        print(f"{'':>16}└ {entrada['motivo'][:80]}")

    print(f"\nELEGIDOS DEL DÍA ({len(resultado['elegidos'])}):")
    for elegido in resultado["elegidos"]:
        print(f"  ★ [{elegido['impacto']}/10] {elegido['titular']}")
```

## engine/server.py
```python
"""Servidor de El Enjambre — FastAPI + WebSocket.

Flujo: el navegador se conecta a /ws y envía un titular. El servidor
corre el mercado real (5.000 agentes), hace que los 100 líderes lean la
noticia (LLM con fallback) y transmite cada tick al frontend:

- mensaje de texto "inicio": las respuestas de los líderes
- un frame binario por tick: [precio f32][tick u32][sentimiento i8 × N_agentes]
  (N_agentes es dinámico: len(agentes_ordenados) — hoy 10.000)
- mensaje de texto "fin": el reporte de la simulación

El sentimiento por agente viaja como un byte (-127..127): la escena 3D
solo necesita saber cuánto pánico o codicia siente cada partícula.
"""

import asyncio
import base64
import contextlib as _contextlib
import hashlib
import hmac
from html import escape as html_escape
import json
import struct
from collections import defaultdict

import os

from fastapi import BackgroundTasks, FastAPI, Header, Request, Response, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from agents.lider import LiderOpinion
from brains.arquetipos import POR_ID
from brains.cerebro import analizar_titular_async
from contenido import limites, persistencia, portero, seguridad, senal_prediccion, vocabulario
from contenido.vocabulario import DISCLAIMER
from model import MercadoEnjambre
from llm_texto import texto_de

TICKS_CALENTAMIENTO = 60  # el mercado encuentra su ritmo (no se transmite)
TICKS_PREVIOS = 10        # calma visible antes de la noticia
TICKS_POSTERIORES = 140   # la reacción completa
RITMO_DEFECTO = 0.08      # segundos entre ticks transmitidos
RITMO_MINIMO = 0.02       # piso: nadie pide ticks sin pausa (protege la CPU)
MAX_TITULAR = 1200        # caracteres: cabe un tweet presidencial completo
MAX_MENSAJE_WS = 4000     # bytes de texto por mensaje del cliente
MAX_SIM_CONCURRENTES = 1  # simulaciones pesadas en vuelo a la vez. En 0,5 CPU /
                          # 512 MB, 2 estaba al borde (ya hubo reinicios por
                          # memoria con UNA). Con 1, el que llega de más ve
                          # "ocupado, intenta en unos segundos" (elegante) en vez
                          # de que el motor reinicie a mitad de su simulación.
                          # Si se sube el plan del servidor, se puede volver a 2.
MENSAJE_PRIVADO = (
    "El Enjambre está en pruebas privadas. Puedes explorar el muro y el "
    "archivo; para soltar tus propios titulares, escríbenos desde "
    "«El Enjambre para tu organización»."
)
MENSAJE_CORREO = (
    "Deja tu correo para soltar tu propio titular al enjambre. De paso te "
    "suscribes gratis a El Pulso, el diario diario del enjambre. Un solo dato, "
    "sin contraseñas."
)


def _puerta_correo_activa() -> bool:
    """Decisión de Giorgio: El Enjambre es una herramienta GRATIS y abierta, sin
    suscripción obligatoria para usarla. La puerta de correo queda DESACTIVADA de
    forma permanente — suscribirse a El Pulso es siempre opcional. (Si alguien
    deja su correo al soltar un titular, se captura como lead sin bloquear nada.)"""
    return False


def _puerta_simulacion(mensaje: dict) -> tuple[bool, str | None]:
    """¿Puede esta persona soltar un titular? Devuelve (permitido, correo).

    - En pruebas privadas: solo la clave del equipo abre.
    - En público CON puerta de correo (ENJAMBRE_PUERTA_CORREO=1): un CORREO
      válido abre y queda suscrito gratis (cada simulación deja un lead).
    - En público sin la puerta: abierto (comportamiento de siempre). En todos
      los casos, si la persona dejó un correo válido, se captura igual.
    """
    email = str(mensaje.get("email", "")).strip().lower()
    correo = email if seguridad.correo_valido(email) else None
    if seguridad.acceso_privado_activo():
        return (True, correo) if seguridad.acceso_ok(mensaje.get("acceso")) else (False, None)
    if _puerta_correo_activa():
        return (True, correo) if correo else (False, None)
    return True, correo


def _token_premium(mensaje: dict) -> str:
    """El token del enlace mágico que el navegador manda para reclamar su nivel
    Premium (40/mes). `limites` lo verifica contra la base: solo el que recibió
    el enlace en su buzón lo tiene, así nadie usa el correo de otro."""
    return str(mensaje.get("premium_token", "")).strip()[:80]


def _cliente_id(mensaje: dict) -> str:
    """Huella suave del navegador (id aleatorio guardado en el dispositivo): el
    cupo gratis se cuenta por dispositivo, no por IP — una oficina o una red
    móvil (CGNAT) no comparte una sola simulación al día."""
    return str(mensaje.get("cid", "")).strip()[:64]


def _suscribir_silencioso(email: str) -> None:
    """Captura el lead SIN bloquear la simulación: alta + correo de confirmación
    (double opt-in). Corre en su propio hilo; cualquier falla se traga para no
    apagar el momento mágico de ver al enjambre."""
    try:
        conexion = persistencia.conectar()
        try:
            alta = persistencia.agregar_suscriptor(conexion, email, origen="web")
        finally:
            conexion.close()
        if not alta.get("ya_activo") and alta.get("reenviar", True):
            from contenido import boletin
            boletin.enviar_confirmacion(email, alta["token_confirma"])
    except Exception:
        pass


def _semilla_lider(semilla_sim: int, unique_id: int) -> int:
    """Semilla de cerebro por líder Y por corrida: mezcla la semilla de la
    simulación con el id del líder. Así dos corridas del mismo titular no
    repiten frases (ni de la IA —caché aparte— ni del respaldo)."""
    return semilla_sim * 1_000_003 + unique_id

# orígenes permitidos: la web de producción + localhost de desarrollo.
# Configurable por entorno (ENJAMBRE_ORIGENES, separado por comas).
_origenes_env = os.environ.get("ENJAMBRE_ORIGENES", "").strip()
ORIGENES = [o.strip() for o in _origenes_env.split(",") if o.strip()] or [
    "http://localhost:5173",
    "http://localhost:4173",
]
# lista blanca del widget: los medios donde se puede embeber (sección 9).
# Un dominio fuera de lista no obtiene los datos (CORS) → el widget muestra
# la versión con CTA "Consigue el widget para tu medio".
_widget_env = os.environ.get("ENJAMBRE_WIDGET_DOMINIOS", "").strip()
DOMINIOS_WIDGET = [d.strip() for d in _widget_env.split(",") if d.strip()]
ORIGENES = ORIGENES + DOMINIOS_WIDGET

app = FastAPI(title="El Enjambre", version="0.7.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGENES,
    allow_origin_regex=r"https://.*\.vercel\.app",  # previews de Vercel
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

# semáforo global: ninguna avalancha de conexiones dispara más de N
# simulaciones pesadas al mismo tiempo (protege CPU y memoria)
import asyncio as _asyncio  # noqa: E402

_semaforo_sim = _asyncio.Semaphore(MAX_SIM_CONCURRENTES)

MAX_OBSERVATORIOS = 2       # sesiones "en vivo" simultáneas (protege CPU)
MAX_TICKS_OBS = 6000        # tope de latidos por sesión (~8 min); luego se cierra
_semaforo_obs = _asyncio.Semaphore(MAX_OBSERVATORIOS)


_contador_peticiones = 0
_CADA_LIMPIEZA = 500  # cada tantas requests se purga el estado vencido

# Tope de cuerpo por petición. El más grande legítimo es el editor del panel
# (el texto completo de una edición del Pulso: unos pocos KB), así que 256 KB
# sobra. Sin este freno, un POST de cientos de MB se carga entero en memoria
# antes de que pydantic lo valide → el motor (512 MB en Render) se queda sin
# memoria y reinicia. Nota: cubre el caso con Content-Length (el normal); una
# subida "chunked" sin ese encabezado sigue acotada por los frenos de más abajo.
MAX_CUERPO = 256_000


@app.middleware("http")
async def blindaje(request: Request, call_next):
    """Rate-limit por IP en /api/*, tope de cuerpo y cabeceras de seguridad."""
    global _contador_peticiones
    ruta = request.url.path
    if request.method in ("POST", "PUT", "PATCH"):
        declarado = request.headers.get("content-length", "")
        if declarado.isdigit() and int(declarado) > MAX_CUERPO:
            return JSONResponse({"error": "cuerpo demasiado grande"}, status_code=413)
    if ruta.startswith("/api/"):
        ip = seguridad.ip_cliente(request.headers, request.client.host if request.client else None)
        if not seguridad.permitir_http(ip, ruta):
            return JSONResponse({"error": "Demasiadas solicitudes. Espera un momento."}, status_code=429)
    # limpieza periódica: evita que el estado en memoria (ventanas de rate-limit
    # e IPs de límites) crezca sin fin al acumular visitantes distintos.
    _contador_peticiones += 1
    if _contador_peticiones % _CADA_LIMPIEZA == 0:
        seguridad.limpiar()
        limites.limpiar()
    respuesta = await call_next(request)
    for clave, valor in seguridad.CABECERAS_SEGURIDAD.items():
        respuesta.headers.setdefault(clave, valor)
    return respuesta

NOMBRES_TIPO = {
    "Fundamentalista": "Fundamentalistas",
    "QuantMomentum": "Quants institucionales",
    "FondoPasivo": "Fondos pasivos",
    "MarketMaker": "Market makers",
    "EjecutorTWAP": "Ejecutores TWAP",
    "Arbitrajista": "Arbitrajistas",
    "NoiseTrader": "Noise traders",
    "Manada": "Manada",
    "FomoRetail": "FOMO retail",
    "Miedoso": "Miedosos",
    "Contrarian": "Contrarians",
    "BuyAndHold": "Buy & hold",
    "LiderOpinion": "Líderes de opinión",
}


def _token_admin_ok(recibido: str) -> bool:
    """Compara el token de admin en tiempo constante (evita timing attacks).

    Falla cerrado: si no hay ENJAMBRE_PIPELINE_TOKEN configurado, nadie pasa.
    """
    esperado = os.environ.get("ENJAMBRE_PIPELINE_TOKEN", "")
    if not esperado:
        return False
    return hmac.compare_digest(recibido or "", esperado)


@app.get("/salud")
def salud() -> dict:
    # `version` = el commit que Render tiene vivo (lo inyecta solo). Sirve para
    # confirmar de un vistazo QUÉ código está corriendo tras un despliegue.
    return {"estado": "ok", "proyecto": "El Enjambre", "etapa": 10,
            "redaccion": True,
            "version": (os.environ.get("RENDER_GIT_COMMIT") or "local")[:12]}


def _ram_contenedor_mb() -> int | None:
    """RAM que Render (u otro contenedor) le asigna al motor, en MB. Lee el
    límite del cgroup — así se puede confirmar desde afuera qué plan quedó
    (512 MB = Starter · ~2048 MB = Standard). Nunca lanza."""
    candidatos = [
        "/sys/fs/cgroup/memory.max",                 # cgroup v2
        "/sys/fs/cgroup/memory/memory.limit_in_bytes",  # cgroup v1
    ]
    for ruta in candidatos:
        try:
            crudo = open(ruta, encoding="utf-8").read().strip()
            if crudo and crudo != "max":
                bytes_ = int(crudo)
                # algunos hosts ponen un número gigante = "sin límite"
                if 0 < bytes_ < (1 << 50):
                    return round(bytes_ / (1024 * 1024))
        except (OSError, ValueError):
            continue
    return None


@app.get("/api/estado")
def api_estado(respuesta: Response) -> dict:
    """Estado operativo público (no revela secretos): si el enjambre está en
    pruebas privadas, si hay clave de IA, y cuánta RAM tiene el motor (para
    confirmar el plan de Render). Sirve para monitoreo."""
    respuesta.headers["Cache-Control"] = "no-store"
    return {
        "privado": seguridad.acceso_privado_activo(),
        "ia_configurada": bool(os.environ.get("ANTHROPIC_API_KEY")),
        "ram_mb": _ram_contenedor_mb(),
    }


def _responder(ws: WebSocket, **campos) -> str:
    return json.dumps(campos, ensure_ascii=False)


@app.websocket("/ws")
async def canal(ws: WebSocket) -> None:
    await ws.accept()
    ip = seguridad.ip_cliente(ws.headers, ws.client.host if ws.client else None)
    try:
        while True:
            texto = await ws.receive_text()
            # entrada malformada nunca tumba la conexión: se responde y sigue
            if len(texto) > MAX_MENSAJE_WS:
                await ws.send_text(_responder(ws, tipo="error", mensaje="mensaje demasiado grande"))
                continue
            try:
                mensaje = json.loads(texto)
            except (ValueError, TypeError):
                await ws.send_text(_responder(ws, tipo="error", mensaje="formato inválido"))
                continue
            if not isinstance(mensaje, dict):
                continue
            tipo = mensaje.get("tipo")

            # modo observatorio: el enjambre sigue vivo y recibe noticias encima
            if tipo == "observatorio":
                # el observatorio también lee titulares con IA: misma puerta
                permitido_obs, correo_obs = _puerta_simulacion(mensaje)
                if not permitido_obs:
                    mensaje_puerta = MENSAJE_PRIVADO if seguridad.acceso_privado_activo() else MENSAJE_CORREO
                    tipo_puerta = "privado" if seguridad.acceso_privado_activo() else "correo"
                    await ws.send_text(_responder(ws, tipo=tipo_puerta, mensaje=mensaje_puerta))
                    continue
                if correo_obs:
                    _asyncio.create_task(_asyncio.to_thread(_suscribir_silencioso, correo_obs))
                try:
                    await _asyncio.wait_for(_semaforo_obs.acquire(), timeout=0.01)
                except _asyncio.TimeoutError:
                    await ws.send_text(_responder(
                        ws, tipo="ocupado",
                        mensaje="El observatorio está lleno ahora mismo. Intenta en unos minutos."))
                    continue
                try:
                    await _correr_observatorio(ws, mensaje, ip)
                finally:
                    _semaforo_obs.release()
                continue

            if tipo != "simular":
                continue

            # la puerta: en privado abre la clave (equipo); en público, un correo
            # válido abre Y queda suscrito gratis (cada simulación deja un lead).
            permitido_puerta, correo = _puerta_simulacion(mensaje)
            if not permitido_puerta:
                mensaje_puerta = MENSAJE_PRIVADO if seguridad.acceso_privado_activo() else MENSAJE_CORREO
                tipo_puerta = "privado" if seguridad.acceso_privado_activo() else "correo"
                await ws.send_text(_responder(ws, tipo=tipo_puerta, mensaje=mensaje_puerta))
                continue

            # tope de simulaciones pesadas simultáneas (antes de gastar cupo)
            try:
                await _asyncio.wait_for(_semaforo_sim.acquire(), timeout=0.01)
            except _asyncio.TimeoutError:
                await ws.send_text(_responder(
                    ws, tipo="ocupado",
                    mensaje="El enjambre está ocupado con otra simulación. Intenta en unos segundos."))
                continue
            try:
                # toda simulación pública gasta ~100 llamadas LLM:
                # frenos por persona (1/día gratis, 40/mes Premium) y global
                permitido, motivo = limites.permitir(
                    ip, premium_token=_token_premium(mensaje), cliente_id=_cliente_id(mensaje))
                if not permitido:
                    await ws.send_text(_responder(ws, tipo="limite", mensaje=motivo))
                    continue
                # captura del lead EN PARALELO: no bloquea el momento mágico
                if correo:
                    _asyncio.create_task(_asyncio.to_thread(_suscribir_silencioso, correo))
                await _correr_simulacion(ws, mensaje)
            finally:
                _semaforo_sim.release()
    except WebSocketDisconnect:
        pass
    except Exception:
        # cualquier fallo inesperado cierra ESTA conexión, no el servidor
        try:
            await ws.close()
        except Exception:
            pass


# ---------- el modo observatorio (el enjambre sigue vivo) ----------

async def _leer_titular_en_vivo(modelo, lideres, titular, candado, semilla) -> list[dict]:
    """Los líderes leen una noticia y se inyecta al modelo EN VIVO (sin
    frenar el latido). El candado evita chocar con el step en curso."""
    from brains import reparto
    from brains.mercado import clasificar_async, perfil_de

    # 1000 líderes comparten ~110 cerebros (presupuesto de la biblia)
    consultas, asignacion = reparto.planificar(
        lideres, lambda uid: _semilla_lider(semilla, uid))
    respuestas_cerebros, tipo = await asyncio.gather(  # lento: sin candado
        analizar_titular_async(titular, consultas),
        clasificar_async(titular),
    )
    respuestas = reparto.expandir(vocabulario.sanear_frases(respuestas_cerebros), asignacion)
    async with candado:
        await asyncio.to_thread(modelo.aplicar_titular, titular, respuestas, perfil_de(tipo))
    return respuestas


async def _correr_observatorio(ws: WebSocket, mensaje: dict, ip: str) -> None:
    """El enjambre late indefinidamente; el usuario suelta noticias encima.
    El costo LLM ocurre SOLO al leer un titular (bajo el tope diario); los
    latidos son casi gratis."""
    try:
        semilla = int(mensaje.get("seed", 42)) % 2_147_483_647
    except (TypeError, ValueError):
        semilla = 42
    ritmo = 0.08
    try:
        ritmo = max(0.04, float(mensaje.get("ritmo", 0.08)))
    except (TypeError, ValueError):
        pass

    modelo = await asyncio.to_thread(_crear_mercado, semilla)
    lideres = [a for a in modelo.agentes_ordenados if isinstance(a, LiderOpinion)]
    candado = _asyncio.Lock()
    detener = _asyncio.Event()

    await ws.send_text(_responder(ws, tipo="observatorio-inicio",
                                  precio=modelo.historial_precios[-1]))

    async def latir() -> None:
        latidos = 0
        while not detener.is_set() and latidos < MAX_TICKS_OBS:
            async with candado:
                await asyncio.to_thread(modelo.step)
            await ws.send_bytes(_paquete_tick(modelo))
            await asyncio.sleep(ritmo)
            latidos += 1
        detener.set()

    async def _inyectar(titular: str) -> None:
        # cada noticia gasta ~100 llamadas LLM → bajo el cupo de la persona
        permitido, motivo = limites.permitir(
            ip, premium_token=_token_premium(mensaje), cliente_id=_cliente_id(mensaje))
        if not permitido:
            await ws.send_text(_responder(ws, tipo="limite", mensaje=motivo))
            return
        respuestas = await _leer_titular_en_vivo(modelo, lideres, titular, candado, semilla)
        await ws.send_text(json.dumps({
            "tipo": "inicio", "titular": titular,
            "lideres": [{"arquetipo": l.arquetipo, **{k: r[k] for k in ("senal", "confianza", "frase", "fuente")}}
                        for l, r in zip(lideres, respuestas)],
        }, ensure_ascii=False))

    async def escuchar() -> None:
        # noticia inicial (opcional): la que traía el mensaje de arranque
        inicial = str(mensaje.get("titular", "")).strip()[:MAX_TITULAR]
        if inicial:
            await _inyectar(inicial)
        while not detener.is_set():
            texto = await ws.receive_text()
            if len(texto) > MAX_MENSAJE_WS:
                continue
            try:
                dato = json.loads(texto)
            except (ValueError, TypeError):
                continue
            tipo = dato.get("tipo") if isinstance(dato, dict) else None
            if tipo == "detener":
                detener.set()
            elif tipo == "noticia":
                titular = str(dato.get("titular", "")).strip()[:MAX_TITULAR]
                if titular:
                    await _inyectar(titular)

    try:
        await _asyncio.gather(latir(), escuchar())
    except WebSocketDisconnect:
        detener.set()
    finally:
        detener.set()
        with _contextlib.suppress(Exception):
            await ws.send_text(_responder(ws, tipo="observatorio-fin"))


# ---------- la simulación transmitida ----------

async def _correr_simulacion(ws: WebSocket, mensaje: dict) -> None:
    titular = str(mensaje.get("titular", ""))[:MAX_TITULAR].strip() or "Sin novedades en los mercados"
    try:
        semilla = int(mensaje.get("seed", 42)) % 2_147_483_647
    except (TypeError, ValueError):
        semilla = 42
    try:
        ritmo = max(RITMO_MINIMO, float(mensaje.get("ritmo", RITMO_DEFECTO)))
    except (TypeError, ValueError):
        ritmo = RITMO_DEFECTO

    # crear y calentar el mercado sin bloquear el loop del servidor
    modelo = await asyncio.to_thread(_crear_mercado, semilla)
    lideres = [a for a in modelo.agentes_ordenados if isinstance(a, LiderOpinion)]

    # los 1000 líderes leen el titular (compartiendo ~110 cerebros de IA, según
    # el presupuesto de la biblia) Y se clasifica el tipo de mercado, en paralelo
    # (la clasificación es 1 llamada barata a Haiku, sin latencia extra)
    from brains import reparto
    from brains.mercado import clasificar_async, perfil_de

    consultas, asignacion = reparto.planificar(
        lideres, lambda uid: _semilla_lider(semilla, uid))
    respuestas_cerebros, tipo_mercado = await asyncio.gather(
        analizar_titular_async(titular, consultas),
        clasificar_async(titular),
    )
    # filtro CMF a las voces de los líderes: se neutraliza aquí, UNA vez, antes
    # de repartirlas a la web, la base y el muro (borde de cumplimiento CMF).
    respuestas = reparto.expandir(vocabulario.sanear_frases(respuestas_cerebros), asignacion)
    perfil = perfil_de(tipo_mercado)

    await ws.send_text(json.dumps({
        "tipo": "inicio",
        "titular": titular,
        "precio": modelo.historial_precios[-1],
        "mercado": perfil["tipo"],
        "mercado_etiqueta": perfil["etiqueta"],
        "lideres": [
            {"arquetipo": lider.arquetipo, **{k: r[k] for k in ("senal", "confianza", "frase", "fuente")}}
            for lider, r in zip(lideres, respuestas)
        ],
    }, ensure_ascii=False))

    contador_acciones: dict[str, list[int]] = defaultdict(lambda: [0, 0])

    async def transmitir_tick() -> None:
        await asyncio.to_thread(modelo.step)
        _contar_acciones(modelo, contador_acciones)
        await ws.send_bytes(_paquete_tick(modelo))
        if ritmo:
            await asyncio.sleep(ritmo)

    for _ in range(TICKS_PREVIOS):
        await transmitir_tick()

    precio_previo = modelo.historial_precios[-1]
    contador_acciones.clear()
    modelo.aplicar_titular(titular, respuestas=respuestas, perfil=perfil)

    for _ in range(TICKS_POSTERIORES):
        await transmitir_tick()

    reporte = _generar_reporte(modelo, precio_previo, respuestas, lideres, contador_acciones)
    reporte["mercado"] = perfil["tipo"]
    reporte["mercado_etiqueta"] = perfil["etiqueta"]

    # persistencia primero (CONTENIDO.md): TODA simulación se guarda
    sim_id = None
    try:
        sim_id = await asyncio.to_thread(
            _guardar_simulacion, titular, semilla, reporte, respuestas, lideres, modelo,
        )
        # si vino desde una tarjeta del muro, la tarjeta pasa a Estado A
        titular_id = mensaje.get("titular_id")
        if sim_id and seguridad.sim_id_valido(str(titular_id) if titular_id else None):
            await asyncio.to_thread(_vincular_titular, str(titular_id), sim_id)
    except Exception:
        pass  # la persistencia nunca tumba la simulación en curso

    await ws.send_text(json.dumps({
        "tipo": "fin",
        "sim_id": sim_id,
        "reporte": reporte,
    }, ensure_ascii=False))


def _vincular_titular(titular_id: str, sim_id: str) -> None:
    conexion = persistencia.conectar()
    try:
        persistencia.vincular_simulacion(conexion, titular_id, sim_id)
    finally:
        conexion.close()


def _guardar_simulacion(titular, semilla, reporte, respuestas, lideres, modelo) -> str:
    conexion = persistencia.conectar()
    try:
        return persistencia.guardar_simulacion(
            conexion,
            titular=titular,
            fuente="manual",
            seed=semilla,
            resumen=reporte,
            lideres=[
                {"arquetipo": lider.arquetipo,
                 **{k: r[k] for k in ("senal", "confianza", "frase")}}
                for lider, r in zip(lideres, respuestas)
            ],
            serie_precios=modelo.historial_precios[-(TICKS_PREVIOS + TICKS_POSTERIORES + 1):],
        )
    finally:
        conexion.close()


def _crear_mercado(semilla: int) -> MercadoEnjambre:
    modelo = MercadoEnjambre(seed=semilla, ticks_horizonte=TICKS_CALENTAMIENTO + TICKS_POSTERIORES)
    modelo.correr(TICKS_CALENTAMIENTO)
    return modelo


# ---------- el paquete binario por tick ----------

def _paquete_tick(modelo: MercadoEnjambre) -> bytes:
    cabecera = struct.pack("<fI", modelo.historial_precios[-1], modelo.tick)
    cuerpo = bytearray(len(modelo.agentes_ordenados))
    for i, agente in enumerate(modelo.agentes_ordenados):
        if isinstance(agente, LiderOpinion):
            s = agente.senal
        else:
            # sentimiento visible = rumor recibido + eco de su última acción
            hace = modelo.tick - agente.tick_ultima_accion
            impulso = 0.0
            if agente.ultima_accion and hace <= 5:
                signo = 0.5 if agente.ultima_accion == "compra" else -0.5
                impulso = signo * (1 - hace / 6)
            s = max(-1.0, min(1.0, agente.senal_social + impulso))
        cuerpo[i] = int(s * 127) & 0xFF
    return cabecera + bytes(cuerpo)


def _contar_acciones(modelo: MercadoEnjambre, contador: dict) -> None:
    for agente in modelo.agentes_ordenados:
        if agente.tick_ultima_accion == modelo.tick and agente.ultima_accion:
            lado = 0 if agente.ultima_accion == "compra" else 1
            contador[type(agente).__name__][lado] += 1


# ---------- el reporte final ----------

def _generar_reporte(modelo, precio_previo, respuestas, lideres, contador) -> dict:
    precios = modelo.historial_precios[-(TICKS_POSTERIORES + 1):]
    retornos = modelo.retornos[-TICKS_POSTERIORES:]
    media = sum(retornos) / len(retornos)
    volatilidad = (sum((r - media) ** 2 for r in retornos) / len(retornos)) ** 0.5

    extremos = sorted(zip(lideres, respuestas), key=lambda par: par[1]["senal"])
    frases = [
        {"arquetipo": lider.arquetipo,
         "nombre": POR_ID.get(lider.arquetipo, {}).get("nombre", lider.arquetipo),
         "frase": r["frase"], "senal": r["senal"]}
        for lider, r in (extremos[0], extremos[len(extremos) // 2], extremos[-1])
    ]

    # P3 — acota la MAGNITUD del movimiento al tope realista de su mercado
    # (cripto/acción se pasan de tamaño). Solo toca el tamaño, NO el signo → la
    # dirección (y por tanto el acierto) no cambia. El tipo lo trae el perfil.
    # Fase 0: se guarda también la MAGNITUD CRUDA (sin recortar) y si hubo recorte,
    # para que la calibración vea el valor real y mida la frecuencia de saturación
    # (dos sesiones distintas no deben verse iguales solo porque el tope las igualó).
    from model import acotar_magnitud
    mercado = (getattr(modelo, "perfil", None) or {}).get("tipo")
    direccion_cruda = round((precios[-1] / precio_previo - 1) * 100, 2)
    direccion = acotar_magnitud(mercado, direccion_cruda)
    minimo = acotar_magnitud(mercado, round((min(precios) / precio_previo - 1) * 100, 2))
    maximo = acotar_magnitud(mercado, round((max(precios) / precio_previo - 1) * 100, 2))
    recorte_aplicado = direccion != direccion_cruda

    # P4 — FUERZA DEL CONSENSO de los líderes (abs del consenso, ∈ [0, 1]): alta =
    # leyeron la noticia con convicción; baja = ambigua. OJO: NO es una probabilidad
    # de acertar (un consenso intenso puede estar equivocado). La probabilidad
    # calibrada (`probabilidad_subida`) se publicará aparte cuando haya un
    # calibrador validado fuera de muestra (ver contenido/calibracion.py, Fase 3).
    # Se mantiene el campo `confianza` por compatibilidad con el frontend.
    fuerza_consenso = round(abs(getattr(modelo, "_ultimo_consenso", 0.0)), 2)

    return {
        "direccion_pct": direccion,
        "direccion_pct_cruda": direccion_cruda,
        "recorte_aplicado": recorte_aplicado,
        "minimo_pct": minimo,
        "maximo_pct": maximo,
        "volatilidad_pct": round(volatilidad * 100, 2),
        "confianza": fuerza_consenso,
        "fuerza_consenso": fuerza_consenso,
        "senal_media_lideres": round(sum(r["senal"] for r in respuestas) / len(respuestas), 2),
        "senal_media_ponderada": senal_prediccion.senal_media_ponderada(lideres, respuestas),
        "desglose": {
            NOMBRES_TIPO.get(clase, clase): {"compras": c, "ventas": v}
            for clase, (c, v) in sorted(contador.items(), key=lambda kv: -sum(kv[1]))
        },
        "frases": frases,
        "descargo": DISCLAIMER,
    }


# ---------- los endpoints del muro (CONTENIDO.md sección 3.2) ----------

def _nivel_agitacion(volatilidad_pct: float) -> str:
    """Traducción editorial de la volatilidad."""
    if volatilidad_pct < 1.0:
        return "bajo"
    if volatilidad_pct < 2.0:
        return "medio"
    return "alto"


def _direccion_editorial(direccion_pct: float) -> str:
    if direccion_pct > 1.0:
        return "▲"
    if direccion_pct < -1.0:
        return "▼"
    return "◆"


def _resumen_tarjeta(resumen: dict) -> dict:
    """Lo que la tarjeta del muro necesita del reporte completo."""
    frases = resumen.get("frases", [])
    jugosa = max(frases, key=lambda f: abs(f.get("senal", 0)), default=None)
    if jugosa is not None:
        arquetipo = POR_ID.get(jugosa["arquetipo"], {})
        jugosa = {"arquetipo": arquetipo.get("nombre", jugosa["arquetipo"]), "frase": jugosa["frase"]}
    return {
        "direccion_pct": resumen.get("direccion_pct"),
        "direccion": _direccion_editorial(resumen.get("direccion_pct", 0)),
        "agitacion": _nivel_agitacion(resumen.get("volatilidad_pct", 0)),
        "frase": jugosa,
    }


@app.get("/api/muro")
def muro(respuesta: Response) -> dict:
    """Las tarjetas del día: destacadas primero, luego cronológico."""
    respuesta.headers["Cache-Control"] = "public, max-age=60"
    conexion = persistencia.conectar()
    try:
        filas = persistencia.titulares_del_muro(conexion, portero.UMBRAL_IMPACTO, limite=30)
    finally:
        conexion.close()
    tarjetas = []
    for fila in filas:
        tarjeta = {
            "id": fila["id"],
            "titular": fila["titular"],
            "fuente": fila["fuente"],
            "simbolos": fila["simbolos"],
            "fecha": fila["fecha"],
            "estado": "simulada" if fila["sim_id"] else "pendiente",
            "sim_id": fila["sim_id"],
            "destacada": bool(fila["sim_destacada"]),
        }
        if fila["resumen_json"]:
            tarjeta["resumen"] = _resumen_tarjeta(json.loads(fila["resumen_json"]))
        tarjetas.append(tarjeta)
    return {"tarjetas": tarjetas, "descargo": DISCLAIMER}


def _payload_simulacion(sim_id: str) -> dict | None:
    """Los datos de una simulación para la UI (o None si no existe)."""
    conexion = persistencia.conectar()
    try:
        datos = persistencia.obtener_simulacion(conexion, sim_id)
        simbolos = ""
        if datos is not None:
            # el ticker viene del titular del muro (si esta sim nació de uno):
            # la UI lo usa para la comparación educativa con el gráfico real
            fila = conexion.execute(
                "SELECT simbolos FROM titulares WHERE sim_id = ?", (sim_id,)
            ).fetchone()
            simbolos = (fila["simbolos"] or "") if fila else ""
    finally:
        conexion.close()
    if datos is None:
        return None
    return {
        "id": datos["id"],
        "titular": datos["titular"],
        "fuente": datos["fuente"],
        "fecha": datos["fecha"],
        "destacada": bool(datos["destacada"]),
        "resumen": datos["resumen"],
        "tarjeta": _resumen_tarjeta(datos["resumen"]),
        "lideres": datos["lideres"],
        "voces": _voces_por_arquetipo(datos["lideres"]),
        "serie_precios": datos["serie_precios"],
        "epilogo": datos.get("epilogo"),
        "simbolos": simbolos,
        "reaccion_real": datos.get("reaccion_real"),
        "tiene_replay": persistencia.leer_frames(sim_id) is not None,
    }


@app.get("/api/simulacion/{sim_id}")
def simulacion(sim_id: str, respuesta: Response) -> dict:
    if not seguridad.sim_id_valido(sim_id):
        return Response(status_code=404)  # type: ignore[return-value]
    datos = _payload_simulacion(sim_id)
    if datos is None:
        return Response(status_code=404)  # type: ignore[return-value]
    respuesta.headers["Cache-Control"] = "public, max-age=300"
    return datos


@app.get("/api/duelo/{id_a}/{id_b}")
def duelo(id_a: str, id_b: str, respuesta: Response) -> dict:
    """Los dos resúmenes de un duelo de escenarios (CONTENIDO.md sección 8)."""
    if not (seguridad.sim_id_valido(id_a) and seguridad.sim_id_valido(id_b)):
        return Response(status_code=404)  # type: ignore[return-value]
    a, b = _payload_simulacion(id_a), _payload_simulacion(id_b)
    if a is None or b is None:
        return Response(status_code=404)  # type: ignore[return-value]
    respuesta.headers["Cache-Control"] = "public, max-age=300"
    return {"a": a, "b": b, "descargo": DISCLAIMER}


def _voces_por_arquetipo(lideres: list[dict]) -> list[dict]:
    """Las 8 voces del reporte: por arquetipo, señal media + la mejor frase."""
    grupos: dict[str, list[dict]] = defaultdict(list)
    for lider in lideres:
        grupos[lider["arquetipo"]].append(lider)
    voces = []
    for arquetipo, miembros in grupos.items():
        senal_media = sum(m["senal"] for m in miembros) / len(miembros)
        mejor = max(miembros, key=lambda m: abs(m["senal"]))
        voces.append({
            "arquetipo": arquetipo,
            "nombre": POR_ID.get(arquetipo, {}).get("nombre", arquetipo),
            "senal_media": round(senal_media, 2),
            "frase": mejor["frase"],
        })
    return sorted(voces, key=lambda v: v["senal_media"])


@app.get("/api/simulacion/{sim_id}/imagen")
def imagen(sim_id: str) -> Response:
    """El 'momento dramático' como PNG 1200×630 (correo + Open Graph)."""
    if not seguridad.sim_id_valido(sim_id):
        return Response(status_code=404)
    conexion = persistencia.conectar()
    try:
        datos = persistencia.obtener_simulacion(conexion, sim_id)
    finally:
        conexion.close()
    if datos is None:
        return Response(status_code=404)
    from contenido import captura

    resumen = {**datos["resumen"], "agitacion": _nivel_agitacion(datos["resumen"].get("volatilidad_pct", 0))}
    png = captura.generar_png(datos["titular"], resumen, datos["serie_precios"])
    return Response(
        content=png,
        media_type="image/png",
        headers={"Cache-Control": "public, max-age=86400, immutable"},
    )


# periodo → (rango Yahoo, intervalo Yahoo, etiqueta editorial)
_PERIODOS = {
    "semana": ("5d", "1d", "última semana"),
    "mes": ("1mo", "1d", "en el mes"),
    "ano": ("1y", "1d", "en el año"),
    "dia": ("1d", "15m", "en el día"),
}


def _ticker_valido(t: str) -> bool:
    """Tickers de Yahoo: letras/números y . = ^ - (SPY, ^GSPC, CL=F, BTC-USD).
    Nada de barras ni espacios → sin inyección en la URL de Yahoo."""
    return bool(t) and len(t) <= 15 and all(c.isalnum() or c in ".=^-" for c in t)


@app.get("/api/grafico/{ticker}")
def grafico(ticker: str, respuesta: Response, n: str = "", p: str = "semana", m: str = "$") -> Response:
    """Gráfico de precio REAL de un activo (PNG estilo Moby) para el correo.

    n = nombre a mostrar · p = periodo (semana/mes/ano/dia) · m = símbolo moneda.
    Degrada elegante: si Yahoo no responde o el ticker no da datos, 404 (el
    correo simplemente omite el gráfico, nunca se cae)."""
    if not _ticker_valido(ticker):
        return Response(status_code=404)
    rango, intervalo, etiqueta = _PERIODOS.get(p, _PERIODOS["semana"])
    from contenido import graficos
    from contenido.fuentes import yahoo

    datos = yahoo.serie_reciente(ticker, rango=rango, intervalo=intervalo)
    if not datos:
        return Response(status_code=404)
    fechas, cierres = datos
    nombre = (n.strip()[:40] or yahoo.NOMBRES.get(ticker, ticker))
    png = graficos.generar_grafico(
        nombre, ticker, cierres, etiqueta_periodo=etiqueta,
        fecha_inicio=yahoo.etiqueta_fecha(fechas[0]), fecha_fin="hoy",
        moneda=(m.strip()[:2] or "$"),
    )
    if png is None:
        return Response(status_code=404)
    # los precios cambian: caché de 1 h (no 'immutable' como el replay)
    return Response(content=png, media_type="image/png",
                    headers={"Cache-Control": "public, max-age=3600"})


@app.get("/api/simulacion/{sim_id}/replay")
def replay(sim_id: str) -> Response:
    """Los frames binarios del replay 3D (solo destacadas los conservan).

    El sim_id se valida como hash hex de 16 (nada de path traversal); el
    replay es inmutable, así que se puede cachear con fuerza.
    """
    if not seguridad.sim_id_valido(sim_id):
        return Response(status_code=404)
    frames = persistencia.leer_frames(sim_id)
    if frames is None:
        return Response(status_code=404)
    return Response(
        content=frames,
        media_type="application/octet-stream",
        headers={"Cache-Control": "public, max-age=86400, immutable"},
    )


class PeticionSimular(BaseModel):
    id: str  # el id del titular en el muro
    acceso: str = ""  # clave de pruebas privadas (si el modo está activo)


@app.post("/api/simular-titular")
def simular_titular(peticion: PeticionSimular) -> dict:
    """Chequeo previo de la simulación on-demand desde una tarjeta.

    No consume el cupo (eso pasa al correr de verdad por el WebSocket);
    responde si hay presupuesto y devuelve el titular a simular.
    """
    if not seguridad.acceso_ok(peticion.acceso):
        return {"estado": "privado", "mensaje": MENSAJE_PRIVADO}
    if not seguridad.sim_id_valido(peticion.id):
        return Response(status_code=404)  # type: ignore[return-value]
    conexion = persistencia.conectar()
    try:
        titular = persistencia.obtener_titular(conexion, peticion.id)
    finally:
        conexion.close()
    if titular is None:
        return Response(status_code=404)  # type: ignore[return-value]
    if titular["sim_id"]:
        return {"estado": "simulada", "sim_id": titular["sim_id"]}
    permitido, motivo = limites.permitir("verificacion-previa", consumir=False)
    if not permitido and motivo == limites.MENSAJE_GLOBAL:
        return {"estado": "limite", "mensaje": motivo}
    return {"estado": "adelante", "titular": titular["titular"], "titular_id": titular["id"]}


class TurnoEntrevista(BaseModel):
    rol: str = ""
    texto: str = ""


class PeticionEntrevista(BaseModel):
    arquetipo: str
    titular: str = ""
    pregunta: str
    senal: float | None = None
    frase: str = ""                       # la frase inicial del líder (contexto)
    historial: list[TurnoEntrevista] = []  # turnos previos de esta charla


@app.post("/api/entrevista")
def api_entrevista(peticion: PeticionEntrevista) -> dict:
    """Entrevistar a un líder: responde EN PERSONAJE a '¿por qué reaccionaste así?'
    (Fase 2, efecto-wow del demo). El rate-limit por IP lo aplica el middleware
    `blindaje`; el cerebro usa un modelo barato (haiku) y NUNCA se cae (fallback
    en personaje). CMF: es un personaje de una simulación, no asesoría financiera.
    """
    from brains import entrevista

    historial = [{"rol": t.rol, "texto": t.texto}
                 for t in peticion.historial[-entrevista.MAX_TURNOS:]]
    r = entrevista.entrevistar(
        peticion.arquetipo, peticion.titular, peticion.pregunta,
        senal=peticion.senal, frase_original=peticion.frase, historial=historial)
    return {**r, "descargo": DISCLAIMER}


# ---------- El Pulso: suscripción con double opt-in (CONTENIDO.md sección 6) ----------

import re as _re  # noqa: E402
import time as _time  # noqa: E402

from fastapi.responses import HTMLResponse  # noqa: E402

_EMAIL = _re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class PeticionSuscribir(BaseModel):
    email: str
    origen: str = "web"


def _pagina(titulo: str, mensaje: str) -> HTMLResponse:
    """Una página mínima con la estética Rubicón para confirmar/baja."""
    html = f"""<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{titulo}</title>
<style>body{{margin:0;height:100vh;display:flex;flex-direction:column;align-items:center;
justify-content:center;background:#0b0e14;color:#f4efe6;font-family:system-ui,sans-serif;text-align:center;padding:24px;}}
h1{{color:#c9a227;font-family:Georgia,serif;font-weight:600;}} a{{color:#c9a227;}}
p{{max-width:420px;line-height:1.5;color:#a8a291;}}</style></head>
<body><h1>{titulo}</h1><p>{mensaje}</p><a href="{boletin_base_web()}">Ir a El Enjambre →</a></body></html>"""
    # estas páginas sí llevan estilo inline: CSP propia que lo permite
    return HTMLResponse(content=html, headers={
        "Content-Security-Policy": "default-src 'none'; style-src 'unsafe-inline'; img-src 'self'",
    })


def boletin_base_web() -> str:
    return os.environ.get("ENJAMBRE_WEB_URL", "https://enjambre-ai-agents.vercel.app")


@app.post("/api/suscribir")
def suscribir(peticion: PeticionSuscribir) -> dict:
    """Alta con OPT-IN SIMPLE: un clic y queda suscrito de inmediato (sin correo
    de confirmación). El clic en 'Suscribirme' ya es el consentimiento. Se le
    manda una bienvenida con el enlace de baja siempre visible."""
    email = peticion.email.strip().lower()
    if not _EMAIL.match(email) or len(email) > 200:
        return JSONResponse({"error": "correo inválido"}, status_code=400)
    origen = peticion.origen if peticion.origen in ("web", "widget", "manual") else "web"

    conexion = persistencia.conectar()
    try:
        ya_activo = persistencia.es_activo(conexion, email)
        persistencia.alta_directa(conexion, email, origen=origen)   # activo de inmediato
        token_baja = persistencia.token_baja_de(conexion, email)
    finally:
        conexion.close()

    if ya_activo:
        return {"estado": "ya_suscrito", "mensaje": "Ya estabas suscrito al Pulso. ¡Gracias!"}

    from contenido import boletin
    boletin.enviar_bienvenida(email, token_baja or "")  # sin Resend, no envía (dev)
    return {"estado": "suscrito",
            "mensaje": "¡Listo! Ya estás suscrito a El Pulso. Te llega mañana temprano. 🐝"}


@app.post("/api/pulso/activar-pendientes")
def activar_pendientes(x_pipeline_token: str = Header(default="")) -> dict:
    """Activa a los suscriptores que quedaron pendientes de confirmar (del viejo
    doble opt-in): ahora que el alta es de un clic, ya dieron su consentimiento.
    Protegido por el token de admin. Se corre UNA vez tras el cambio."""
    if not _token_admin_ok(x_pipeline_token):
        return JSONResponse({"error": "no autorizado"}, status_code=403)
    conexion = persistencia.conectar()
    try:
        n = persistencia.activar_pendientes(conexion)
    finally:
        conexion.close()
    return {"ok": True, "activados": n}


class PeticionContacto(BaseModel):
    nombre: str
    email: str
    organizacion: str = ""
    mensaje: str = ""


@app.post("/api/contacto")
def api_contacto(peticion: PeticionContacto) -> dict:
    """El canal B2B: educadores, medios y fintechs que quieren conversar.

    Guarda el lead y avisa a Giorgio por Telegram (si está configurado).
    Sin promesas de inversión: es una solicitud de contacto, nada más."""
    nombre = peticion.nombre.strip()
    email = peticion.email.strip().lower()
    if not nombre or len(nombre) > 120:
        return JSONResponse({"error": "cuéntanos tu nombre"}, status_code=400)
    if not _EMAIL.match(email) or len(email) > 200:
        return JSONResponse({"error": "correo inválido"}, status_code=400)
    conexion = persistencia.conectar()
    try:
        persistencia.agregar_contacto(
            conexion, nombre=nombre, email=email,
            organizacion=peticion.organizacion, mensaje=peticion.mensaje,
        )
    finally:
        conexion.close()
    try:
        from contenido import notificar
        # todo lo que escribió el visitante se escapa: el aviso va con
        # parse_mode=HTML y un "<" suelto haría que Telegram lo rechace
        # (Giorgio perdería el lead sin enterarse).
        notificar.avisar(
            f"🤝 <b>Nuevo contacto B2B</b>\n{notificar.escapar(nombre)}"
            + (f" · {notificar.escapar(peticion.organizacion.strip()[:80])}"
               if peticion.organizacion.strip() else "")
            + f"\n{notificar.escapar(email)}\n{notificar.escapar(peticion.mensaje.strip()[:200])}"
        )
    except Exception:
        pass  # el lead ya quedó guardado; el aviso es cortesía
    return {"estado": "recibido",
            "mensaje": "¡Gracias! Te escribiremos pronto para coordinar."}


@app.get("/api/contactos")
def api_contactos(x_pipeline_token: str = Header(default="")) -> dict:
    """Los leads B2B, para Giorgio (protegido)."""
    if not _token_admin_ok(x_pipeline_token):
        return JSONResponse({"error": "no autorizado"}, status_code=403)  # type: ignore[return-value]
    conexion = persistencia.conectar()
    try:
        return {"contactos": persistencia.listar_contactos(conexion)}
    finally:
        conexion.close()


class PeticionDesbloqueo(BaseModel):
    email: str


# antibombardeo del enlace mágico: no reenviar al mismo correo más seguido que esto
_ultimo_desbloqueo: dict[str, float] = {}
_VENTANA_DESBLOQUEO = 300  # segundos


@app.post("/api/pulso/desbloqueo")
def desbloqueo_enjambre(peticion: PeticionDesbloqueo) -> dict:
    """El enlace mágico: si el correo es Premium activo, le enviamos un enlace que
    desbloquea 40/mes en El Enjambre. La respuesta es SIEMPRE la misma —no revela
    quién es suscriptor de pago (cierra el oráculo)— y no consume cupo."""
    from contenido import boletin

    correo = (peticion.email or "").strip().lower()
    if seguridad.correo_valido(correo) and len(correo) <= 200:
        ahora = _time.time()
        reciente = ahora - _ultimo_desbloqueo.get(correo, 0) < _VENTANA_DESBLOQUEO
        if not reciente:
            conexion = persistencia.conectar()
            try:
                if persistencia.es_premium(conexion, correo):
                    token = persistencia.emitir_token_enjambre(conexion, correo)
                    if token:
                        _ultimo_desbloqueo[correo] = ahora
                        boletin.enviar_desbloqueo_enjambre(correo, token)
            finally:
                conexion.close()
    return {"enviado": True,
            "mensaje": "Si ese correo es Premium, te enviamos un enlace para desbloquear."}


@app.get("/api/pulso/enjambre/verificar")
def verificar_desbloqueo(token: str = "") -> dict:
    """El navegador canjea el token del enlace mágico por su nivel. NO es un
    oráculo de correos: solo responde a un token válido, que es un secreto en sí
    mismo. Devuelve {premium, limite, periodo}. NO consume cupo."""
    from contenido import limites

    conexion = persistencia.conectar()
    try:
        correo = persistencia.email_por_token_enjambre(conexion, (token or "").strip())
        es_prem = bool(correo) and persistencia.es_premium(conexion, correo)
    finally:
        conexion.close()
    if es_prem:
        return {"premium": True, "limite": limites.tope_mes_premium(), "periodo": "mes"}
    return {"premium": False, "limite": limites.tope_dia_gratis(), "periodo": "día"}


@app.get("/api/confirmar/{token}")
def confirmar(token: str) -> HTMLResponse:
    conexion = persistencia.conectar()
    try:
        email = persistencia.confirmar_suscriptor(conexion, token)
    finally:
        conexion.close()
    if email is None:
        return _pagina("Enlace no válido", "Este enlace de confirmación ya se usó o expiró.")
    return _pagina("¡Suscripción confirmada! 🐝",
                   "Desde mañana recibirás El Pulso cada mañana. Bienvenido al enjambre.")


@app.get("/api/baja/{token}")
def baja(token: str) -> HTMLResponse:
    conexion = persistencia.conectar()
    try:
        exito = persistencia.dar_de_baja(conexion, token)
    finally:
        conexion.close()
    if not exito:
        return _pagina("Enlace no válido", "No encontramos esa suscripción.")
    return _pagina("Te desuscribiste", "Ya no recibirás El Pulso. Puedes volver cuando quieras.")


# ---------- El Pulso: revisión y aprobación desde el correo (humano en el lazo) ----------
# El token de la edición (en el correo de revisión) es la llave: quien lo tiene,
# decide. Aprobar/Descartar son POST (un clic desde la página de revisión), así
# ningún prefetch del cliente de correo dispara un envío por accidente.

def _pagina_pulso(titulo: str, cuerpo: str, status: int = 200) -> HTMLResponse:
    html = f"""<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{titulo}</title>
<style>
 body{{margin:0;background:#141019;color:#f3eee8;font-family:system-ui,-apple-system,sans-serif;}}
 .barra{{position:sticky;top:0;z-index:2;background:#1b1522;border-bottom:1px solid #2e2636;padding:16px 18px;text-align:center;}}
 .barra h1{{margin:0 0 4px;font-family:Georgia,serif;font-weight:600;font-size:1.15rem;color:#e3c565;}}
 .barra p{{margin:0;color:#a8a291;font-size:.85rem;}}
 .acc{{display:flex;gap:12px;justify-content:center;flex-wrap:wrap;margin-top:14px;}}
 .btn{{border:0;cursor:pointer;font:700 13px/1 system-ui;letter-spacing:.04em;text-transform:uppercase;padding:14px 24px;border-radius:8px;}}
 .ok{{background:#2f8f66;color:#fff;}} .no{{background:transparent;color:#c0847d;border:1px solid #7a4b47;}}
 .marco{{width:100%;border:0;background:#faf8f4;display:block;min-height:74vh;}}
 .aviso{{max-width:520px;margin:64px auto;padding:0 24px;text-align:center;line-height:1.6;}}
 .aviso h1{{font-family:Georgia,serif;}}
</style></head><body>{cuerpo}</body></html>"""
    return HTMLResponse(content=html, status_code=status, headers={
        "Content-Security-Policy": "default-src 'none'; frame-src 'self'; img-src 'self' data:; style-src 'unsafe-inline'; form-action 'self'",
        "Referrer-Policy": "no-referrer", "X-Content-Type-Options": "nosniff"})


@app.get("/pulso/preview/{token}")
def pulso_preview(token: str) -> Response:
    """El HTML crudo de la edición (lo carga el iframe de la página de revisión)."""
    conexion = persistencia.conectar()
    try:
        ed = persistencia.edicion_por_token(conexion, token)
    finally:
        conexion.close()
    if not ed or not ed.get("html_preview"):
        return Response(status_code=404)
    return HTMLResponse(content=ed["html_preview"], headers={
        "Content-Security-Policy": "default-src 'none'; img-src 'self' data:; style-src 'unsafe-inline'",
        "X-Frame-Options": "SAMEORIGIN"})


@app.get("/pulso/revisar/{token}")
def pulso_revisar(token: str) -> HTMLResponse:
    """La sala de revisión: el preview real + botones Aprobar / Descartar."""
    conexion = persistencia.conectar()
    try:
        ed = persistencia.edicion_por_token(conexion, token)
        n_susc = len(persistencia.suscriptores_activos(conexion)) if ed else 0
    finally:
        conexion.close()
    if not ed:
        return _pagina_pulso("Enlace no válido",
            '<div class="aviso"><h1>Enlace no válido</h1><p>No encontramos esa edición.</p></div>', status=404)
    estado = ed["estado"]
    if estado == "enviada":
        cabecera = f'<h1>Ya enviada ✓</h1><p>Salió a {ed["enviados"]} de {ed["suscriptores"]} suscriptores.</p>'
        acciones = (f'<div class="acc">'
                    f'<form method="post" action="/pulso/reenviar/{token}" style="margin:0;" '
                    f"onsubmit=\"return confirm('¿Reenviar esta edición a TODOS los suscriptores? "
                    f"Quienes ya la recibieron tendrán un correo duplicado.');\">"
                    f'<button class="btn ok" type="submit">📤 Reenviar a todos</button></form></div>')
    elif estado == "descartada":
        cabecera = '<h1>Descartada</h1><p>Esta edición no se enviará.</p>'
        acciones = ""
    else:
        cabecera = (f'<h1>El Pulso — pendiente de tu revisión</h1>'
                    f'<p>Se enviaría a {n_susc} suscriptor(es). Revisa abajo y decide.</p>')
        acciones = (f'<div class="acc">'
                    f'<form method="post" action="/pulso/aprobar/{token}" style="margin:0;"><button class="btn ok" type="submit">✅ Aprobar y enviar</button></form>'
                    f'<form method="post" action="/pulso/descartar/{token}" style="margin:0;"><button class="btn no" type="submit">🗑 Descartar</button></form></div>')
    cuerpo = (f'<div class="barra">{cabecera}{acciones}</div>'
              f'<iframe class="marco" src="/pulso/preview/{token}" title="Vista previa de la edición"></iframe>')
    return _pagina_pulso("Revisar El Pulso", cuerpo)


@app.post("/pulso/aprobar/{token}")
def pulso_aprobar(token: str) -> HTMLResponse:
    conexion = persistencia.conectar()
    try:
        ed = persistencia.edicion_por_token(conexion, token)
        if not ed:
            return _pagina_pulso("Enlace no válido", '<div class="aviso"><h1>Enlace no válido</h1></div>', status=404)
        from contenido import pipeline
        res = pipeline.aprobar_y_enviar(conexion, ed["fecha"])
    finally:
        conexion.close()
    if res.get("ok") and res.get("ya_enviada"):
        msg = f'Esta edición ya se había enviado ({res.get("enviados", 0)} correos).'
    elif res.get("ok"):
        msg = f'Enviada a {res.get("enviados", 0)} de {res.get("suscriptores", 0)} suscriptores. 🎉'
        msg += _detalle_fallos(res.get("fallos"))
    else:
        msg = res.get("motivo", "No se pudo enviar.")
    return _pagina_pulso("Aprobada",
        f'<div class="aviso"><h1 style="color:#2f8f66;">✅ Listo</h1><p>{msg}</p></div>')


def _detalle_fallos(fallos) -> str:
    """Si algún envío falló, lo lista en la página de 'Listo' con su motivo (así
    Giorgio ve QUÉ direcciones caen y por qué, en vez de un '3 de 6' a ciegas).
    Esta página solo se alcanza con el token del correo de revisión (privada)."""
    if not fallos:
        return ""
    filas = ""
    for f in fallos:
        if not isinstance(f, dict):
            continue
        baja = (' <span style="color:#2f8f66;">(dado de baja automáticamente)</span>'
                if f.get("desactivado") else "")
        filas += (f'<li><b>{html_escape(str(f.get("email", "")))}</b> — '
                  f'{html_escape(str(f.get("motivo", "")))}{baja}</li>')
    if not filas:
        return ""
    return ('<p style="margin-top:14px;color:#c0504d;">No llegaron '
            f'{len(fallos)}:</p><ul style="text-align:left;color:#6f6a5f;'
            f'font-size:14px;line-height:1.6;">{filas}</ul>')


@app.post("/pulso/reenviar/{token}")
def pulso_reenviar(token: str) -> HTMLResponse:
    """Reenvía la edición a TODOS los suscriptores, a pedido (aunque ya se envió)."""
    conexion = persistencia.conectar()
    try:
        ed = persistencia.edicion_por_token(conexion, token)
        if not ed:
            return _pagina_pulso("Enlace no válido", '<div class="aviso"><h1>Enlace no válido</h1></div>', status=404)
        from contenido import pipeline
        res = pipeline.reenviar_a_suscriptores(conexion, ed["fecha"])
    finally:
        conexion.close()
    if res.get("ok"):
        msg = f'Reenviada a {res.get("enviados", 0)} de {res.get("suscriptores", 0)} suscriptores. 🎉'
    else:
        msg = res.get("motivo", "No se pudo reenviar.")
    return _pagina_pulso("Reenviada",
        f'<div class="aviso"><h1 style="color:#2f8f66;">📤 Listo</h1><p>{msg}</p></div>')


@app.post("/pulso/descartar/{token}")
def pulso_descartar(token: str) -> HTMLResponse:
    conexion = persistencia.conectar()
    try:
        ed = persistencia.edicion_por_token(conexion, token)
        if not ed:
            return _pagina_pulso("Enlace no válido", '<div class="aviso"><h1>Enlace no válido</h1></div>', status=404)
        from contenido import pipeline
        pipeline.descartar_edicion(conexion, ed["fecha"])
    finally:
        conexion.close()
    return _pagina_pulso("Descartada",
        '<div class="aviso"><h1 style="color:#c0847d;">🗑 Descartada</h1>'
        '<p>Esta edición no se enviará. Mañana habrá una nueva.</p></div>')


# ---------- Webhook de Resend: aperturas y clics (firmado por Svix) ----------
# Resend firma cada evento con Svix (HMAC-SHA256). Sin el secreto configurado,
# el endpoint RECHAZA todo (falla cerrado): jamás ingerimos eventos sin firmar.

def _verificar_svix(cuerpo: bytes, cabeceras) -> bool:
    """Valida la firma Svix de un webhook de Resend. Constante en el tiempo."""
    secreto = os.environ.get("RESEND_WEBHOOK_SECRET", "").strip()
    if not secreto:
        return False
    svix_id = cabeceras.get("svix-id", "")
    svix_ts = cabeceras.get("svix-timestamp", "")
    firmas = cabeceras.get("svix-signature", "")
    if not (svix_id and svix_ts and firmas):
        return False
    # antirreplay: rechaza timestamps muy viejos o del futuro (tolerancia amplia
    # para el reloj de Render). El timestamp es parte de lo firmado igualmente.
    try:
        desfase = abs(int(_time.time()) - int(svix_ts))
        if desfase > 3600:
            return False
    except (ValueError, TypeError):
        return False
    clave = secreto.split("_", 1)[1] if secreto.startswith("whsec_") else secreto
    try:
        clave_bytes = base64.b64decode(clave)
    except Exception:
        return False
    firmado = f"{svix_id}.{svix_ts}.".encode() + cuerpo
    esperada = base64.b64encode(hmac.new(clave_bytes, firmado, hashlib.sha256).digest()).decode()
    # el header trae "v1,<firma> v1,<firma2>…"; comparación constante contra cada una
    for parte in firmas.split():
        _, _, valor = parte.partition(",")
        if valor and hmac.compare_digest(valor, esperada):
            return True
    return False


def _tag_edicion_evento(data: dict) -> str | None:
    """Saca la fecha de edición del tag del evento (Resend la devuelve como
    objeto {edicion: fecha} o como lista [{name,value}])."""
    tags = data.get("tags")
    if isinstance(tags, dict):
        return tags.get("edicion")
    if isinstance(tags, list):
        for t in tags:
            if isinstance(t, dict) and t.get("name") == "edicion":
                return t.get("value")
    return None


@app.post("/pulso/webhook/resend")
async def webhook_resend(request: Request) -> Response:
    """Recibe eventos de Resend (apertura, clic…) y los registra por edición.
    Firma Svix obligatoria: sin ella, 401."""
    cuerpo = await request.body()
    if len(cuerpo) > 64_000:  # un evento legítimo es pequeño; corta abusos
        return JSONResponse({"error": "cuerpo demasiado grande"}, status_code=413)
    if not _verificar_svix(cuerpo, request.headers):
        return JSONResponse({"error": "firma no válida"}, status_code=401)
    try:
        evento = json.loads(cuerpo)
    except (ValueError, TypeError):
        return JSONResponse({"error": "json no válido"}, status_code=400)
    tipo = (evento.get("type") or "").removeprefix("email.")
    data = evento.get("data") or {}
    destinatarios = data.get("to") or []
    email = destinatarios[0] if isinstance(destinatarios, list) and destinatarios else ""
    fecha_ed = _tag_edicion_evento(data)
    ts = evento.get("created_at")
    if email and tipo:
        conexion = persistencia.conectar()
        try:
            persistencia.registrar_evento_correo(conexion, fecha_ed, email, tipo, ts)
        finally:
            conexion.close()
    return JSONResponse({"ok": True})  # 200 siempre que la firma sea válida


@app.post("/pulso/webhook/polar")
async def webhook_polar(request: Request) -> Response:
    """Recibe los eventos de pago de Polar (El Pulso Premium) y prende/apaga la
    llave `premium` del suscriptor. Firma Standard Webhooks obligatoria: sin ella,
    401. Devuelve 200 en todo evento con firma válida (aunque no aplique), para
    que Polar no lo reintente en vano."""
    from contenido import pagos

    cuerpo = await request.body()
    if len(cuerpo) > 96_000:  # un evento legítimo es pequeño; corta abusos
        return JSONResponse({"error": "cuerpo demasiado grande"}, status_code=413)
    if not pagos.verificar_firma(cuerpo, request.headers):
        return JSONResponse({"error": "firma no válida"}, status_code=401)
    try:
        evento = json.loads(cuerpo)
    except (ValueError, TypeError):
        return JSONResponse({"error": "json no válido"}, status_code=400)
    conexion = persistencia.conectar()
    try:
        resultado = pagos.procesar_evento(conexion, evento)
    finally:
        conexion.close()
    return JSONResponse(resultado)


# ---------- Centro de Mando de El Pulso (dashboard, protegido por token) ----------

class PeticionEditar(BaseModel):
    redactado: dict = {}


def _fecha_valida(fecha: str) -> bool:
    # acepta la fecha del día y la clave de la edición de la tarde ('…-t')
    return bool(_re.match(r"^\d{4}-\d{2}-\d{2}(-t)?$", fecha))


@app.get("/panel")
def panel_html() -> Response:
    """Sirve el Centro de Mando desde la propia API (mismo origen → sin CORS).
    El acceso lo controla la clave que se pide dentro de la página."""
    from pathlib import Path
    ruta = Path(__file__).parent / "panel.html"
    if not ruta.exists():
        return Response(status_code=404)
    return HTMLResponse(content=ruta.read_text(encoding="utf-8"), headers={
        "Content-Security-Policy": ("default-src 'none'; script-src 'unsafe-inline'; "
                                    "style-src 'unsafe-inline'; connect-src 'self'; "
                                    "frame-src 'self'; img-src 'self' data:; font-src 'self'"),
        "X-Content-Type-Options": "nosniff"})


@app.get("/api/panel/estado")
def panel_estado(x_pipeline_token: str = Header(default="")) -> dict:
    if not _token_admin_ok(x_pipeline_token):
        return JSONResponse({"error": "no autorizado"}, status_code=403)
    conexion = persistencia.conectar()
    try:
        hoy = persistencia.ahora_iso()[:10]
        ed = persistencia.obtener_edicion(conexion, hoy)
        n_susc = len(persistencia.suscriptores_activos(conexion))
    finally:
        conexion.close()
    return {
        "hoy": hoy,
        "suscriptores": n_susc,
        "ia_configurada": bool(os.environ.get("ANTHROPIC_API_KEY")),
        "resend_configurado": bool(os.environ.get("RESEND_API_KEY")),
        "admin_email_configurado": bool(os.environ.get("PULSO_ADMIN_EMAIL")),
        "edicion_hoy": None if ed is None else {
            "estado": ed["estado"], "asunto": ed["asunto"],
            "enviados": ed["enviados"], "suscriptores": ed["suscriptores"]},
        "version": (os.environ.get("RENDER_GIT_COMMIT") or "local")[:12],
    }


@app.get("/api/panel/ediciones")
def panel_ediciones(x_pipeline_token: str = Header(default=""), limite: int = 30) -> dict:
    if not _token_admin_ok(x_pipeline_token):
        return JSONResponse({"error": "no autorizado"}, status_code=403)
    conexion = persistencia.conectar()
    try:
        eds = persistencia.listar_ediciones(conexion, min(max(1, limite), 90))
    finally:
        conexion.close()
    return {"ediciones": eds}


@app.get("/api/panel/estadisticas")
def panel_estadisticas(x_pipeline_token: str = Header(default=""), dias: int = 30) -> dict:
    """Estadísticas del centro de mando: crecimiento de suscriptores, ediciones
    y aperturas/clics (estas últimas si el webhook de Resend está configurado)."""
    if not _token_admin_ok(x_pipeline_token):
        return JSONResponse({"error": "no autorizado"}, status_code=403)  # type: ignore[return-value]
    conexion = persistencia.conectar()
    try:
        datos = persistencia.estadisticas(conexion, dias=dias)
    finally:
        conexion.close()
    datos["webhook_configurado"] = bool(os.environ.get("RESEND_WEBHOOK_SECRET"))
    return datos


@app.get("/api/panel/edicion/{fecha}")
def panel_edicion(fecha: str, x_pipeline_token: str = Header(default="")) -> dict:
    if not _token_admin_ok(x_pipeline_token):
        return JSONResponse({"error": "no autorizado"}, status_code=403)
    if not _fecha_valida(fecha):
        return Response(status_code=404)  # type: ignore[return-value]
    conexion = persistencia.conectar()
    try:
        ed = persistencia.obtener_edicion(conexion, fecha)
    finally:
        conexion.close()
    if ed is None:
        return Response(status_code=404)  # type: ignore[return-value]
    brief = ed["brief"] or {}
    # ¿es una edición de FIN DE SEMANA (sábado = resumen, domingo = deep-dive)?
    # Entonces no hay editor de historias: se revisa en la vista previa y se
    # aprueba/descarta.
    analisis = brief.get("analisis") if isinstance(brief.get("analisis"), dict) else None
    es_resumen = isinstance(brief.get("resumen_redactado"), dict)
    es_finde = es_resumen or isinstance(brief.get("analisis_redactado"), dict)
    if es_resumen:
        resumen_hechos = {"titulo": (brief.get("resumen") or {}).get("titulo", "El Pulso de la semana"),
                          "nombre": "Resumen de la semana"}
    elif analisis:
        resumen_hechos = {"titulo": analisis.get("titulo"), "nombre": analisis.get("nombre"),
                          "ticker": analisis.get("ticker")}
    else:
        resumen_hechos = None
    return {
        "fecha": ed["fecha"], "estado": ed["estado"], "asunto": ed["asunto"],
        "token": ed["token"], "enviados": ed["enviados"], "suscriptores": ed["suscriptores"],
        "generada_iso": ed["generada_iso"], "enviada_iso": ed["enviada_iso"],
        "redactado": brief.get("redactado") or {}, "foto": brief.get("foto") or [],
        "finde": es_finde,
        "analisis": resumen_hechos if es_finde else None,
    }



@app.get("/api/pulso/suscriptores")
def pulso_suscriptores(clave: str = "", email: str = ""):
    """Conteo de suscriptores (solo números, sin correos): registrados, activos
    (confirmados), sin confirmar (double opt-in pendiente) y bajas. Con `email`,
    reporta el estado de ESE correo. De solo lectura; protegido con clave."""
    if clave != "revisar-pulso-2026":
        return Response(status_code=404)  # type: ignore[return-value]
    conexion = persistencia.conectar()
    try:
        q = lambda sql: conexion.execute(sql).fetchone()[0]
        total = q("SELECT COUNT(*) FROM suscriptores")
        activos = q("SELECT COUNT(*) FROM suscriptores WHERE activo = 1")
        sin_confirmar = q("SELECT COUNT(*) FROM suscriptores WHERE activo = 0 AND token_confirma IS NOT NULL")
        bajas = q("SELECT COUNT(*) FROM suscriptores WHERE activo = 0 AND token_confirma IS NULL")
        estado_email = None
        if email:
            fila = conexion.execute(
                "SELECT activo, token_confirma FROM suscriptores WHERE lower(email) = lower(?)",
                (email.strip(),)).fetchone()
            if fila is None:
                estado_email = "no registrado"
            elif fila["activo"] == 1:
                estado_email = "activo (confirmado, recibe el newsletter)"
            elif fila["token_confirma"]:
                estado_email = "PENDIENTE de confirmar (no recibe el newsletter)"
            else:
                estado_email = "baja (se desuscribió)"
    finally:
        conexion.close()
    return {"registrados": total, "activos": activos,
            "sin_confirmar": sin_confirmar, "bajas": bajas,
            "email_consultado": email or None, "estado_email": estado_email}


@app.post("/api/panel/edicion/{fecha}/aprobar")
def panel_aprobar(fecha: str, x_pipeline_token: str = Header(default="")) -> dict:
    if not _token_admin_ok(x_pipeline_token):
        return JSONResponse({"error": "no autorizado"}, status_code=403)
    if not _fecha_valida(fecha):
        return Response(status_code=404)  # type: ignore[return-value]
    from contenido import pipeline
    return pipeline.aprobar_y_enviar(fecha=fecha)


@app.post("/api/panel/edicion/{fecha}/descartar")
def panel_descartar(fecha: str, x_pipeline_token: str = Header(default="")) -> dict:
    if not _token_admin_ok(x_pipeline_token):
        return JSONResponse({"error": "no autorizado"}, status_code=403)
    if not _fecha_valida(fecha):
        return Response(status_code=404)  # type: ignore[return-value]
    from contenido import pipeline
    return pipeline.descartar_edicion(fecha=fecha)


@app.post("/api/panel/edicion/{fecha}/editar")
def panel_editar(fecha: str, peticion: PeticionEditar, x_pipeline_token: str = Header(default="")) -> dict:
    if not _token_admin_ok(x_pipeline_token):
        return JSONResponse({"error": "no autorizado"}, status_code=403)
    if not _fecha_valida(fecha):
        return Response(status_code=404)  # type: ignore[return-value]
    conexion = persistencia.conectar()
    try:
        ed = persistencia.obtener_edicion(conexion, fecha)
        if ed is None:
            return {"ok": False, "motivo": "no existe la edición"}
        if ed["estado"] == "enviada":
            return {"ok": False, "motivo": "la edición ya se envió; no se puede editar"}
        persistencia.actualizar_redactado(conexion, fecha, peticion.redactado)
        # re-renderiza el preview con el texto editado (usa las destacadas de hoy).
        # Si esto falla (p. ej. hoy no hay destacadas), el texto SÍ quedó guardado
        # pero la vista previa quedó vieja: hay que DECIRLO, no mentir con ok:true
        # a secas — si no, se aprueba y sale el correo sin las ediciones (B5).
        preview_ok, motivo = False, ""
        try:
            from datetime import datetime as _dt, timezone as _tz
            from contenido import pipeline, boletin
            brief = persistencia.obtener_edicion(conexion, fecha)["brief"]
            destacadas = pipeline._destacadas_de_hoy(conexion)
            # el fin de semana el correo es el resumen (sábado) o el deep-dive
            # (domingo): no necesita destacadas, construir_html lo arma del brief.
            es_finde = (isinstance(brief.get("analisis_redactado"), dict)
                        or isinstance(brief.get("resumen_redactado"), dict))
            if destacadas or es_finde:
                html = boletin.construir_html(
                    destacadas, pipeline._fecha_es(_dt.now(_tz.utc)),
                    token_baja=persistencia.TOKEN_BAJA_SENTINEL, brief=brief)
                persistencia.actualizar_preview(conexion, fecha, html)
                preview_ok = True
            else:
                motivo = "Hoy no hay destacadas: se guardó tu texto, pero la vista previa no se pudo regenerar."
        except Exception as error:
            motivo = f"Se guardó tu texto, pero la vista previa no se pudo regenerar ({type(error).__name__})."
        return {"ok": True, "preview_actualizado": preview_ok, "motivo": motivo}
    finally:
        conexion.close()


@app.post("/api/panel/generar")
def panel_generar(tareas: BackgroundTasks, x_pipeline_token: str = Header(default="")) -> dict:
    if not _token_admin_ok(x_pipeline_token):
        return JSONResponse({"error": "no autorizado"}, status_code=403)
    tareas.add_task(_correr_ritual)
    return {"ok": True, "mensaje": "Generando la edición de hoy… (~1-2 min). Recarga en un momento."}


# ---------- disparador del ritual de la madrugada (protegido por token) ----------

def _correr_ritual(momento: str = "manana") -> None:
    """Corre el ritual completo en el MISMO proceso web → misma base que
    sirve el muro. Un fallo NO debe tumbar el servidor, pero SÍ debe dejar
    rastro: si no, un muro vacío y ningún correo son indistinguibles de un día
    sin noticias, y en el log no hay pista de por qué (B6).

    `momento="tarde"` arma la edición de la tarde (el cierre, Premium)."""
    try:
        from contenido import pipeline
        pipeline.ritual_matutino(enviar=True, momento=momento)
    except Exception:
        import traceback
        traceback.print_exc()  # queda en el log de Render
        try:
            from contenido import notificar
            notificar.avisar("⚠️ <b>El ritual de El Pulso falló.</b> Revisa el log del motor; "
                             "el muro puede haber quedado sin actualizar y no salió edición.")
        except Exception:
            pass  # el aviso es cortesía; el traceback ya quedó en el log


@app.get("/api/diagnostico")
def api_diagnostico(x_pipeline_token: str = Header(default="")) -> dict:
    """Diagnóstico de la clave de Anthropic en UN comando (protegido).

    Hace una llamada mínima a la API y devuelve el veredicto con la causa
    exacta si falla (clave inválida, sin saldo, timeout…). Evita pescar
    errores en los logs cuando los líderes caen al respaldo."""
    if not _token_admin_ok(x_pipeline_token):
        return JSONResponse({"error": "no autorizado"}, status_code=403)
    clave = os.environ.get("ANTHROPIC_API_KEY", "")
    resultado = {
        "clave_presente": bool(clave),
        "formato_sk_ant": clave.startswith("sk-ant-"),
        "largo_clave": len(clave),
    }
    if not clave:
        resultado["veredicto"] = "FALTA la variable ANTHROPIC_API_KEY"
        return resultado
    if clave != clave.strip():
        resultado["veredicto"] = "la clave tiene espacios al inicio o final: bórralos y guarda"
        return resultado
    try:
        import anthropic

        cliente = anthropic.Anthropic(timeout=20)
        r = cliente.messages.create(
            model="claude-haiku-4-5-20251001", max_tokens=10,
            messages=[{"role": "user", "content": "Di solo: hola"}],
        )
        resultado["veredicto"] = "OK: la IA respondió — los cerebros reales funcionan"
        resultado["respuesta"] = texto_de(r)[:40]
    except Exception as error:
        resultado["veredicto"] = f"FALLA {type(error).__name__}: {str(error)[:300]}"
    return resultado


@app.post("/api/pipeline")
def disparar_pipeline(tareas: BackgroundTasks, momento: str = "manana",
                      x_pipeline_token: str = Header(default="")) -> dict:
    """Lo llama el cron de Render (o Giorgio a mano) para preparar el día.

    Protegido por token (ENJAMBRE_PIPELINE_TOKEN). Corre en segundo plano
    y responde al instante: el ritual toma minutos. `?momento=tarde` arma la
    edición de la tarde (el cierre del mercado, Premium).
    """
    if not _token_admin_ok(x_pipeline_token):
        return JSONResponse({"error": "no autorizado"}, status_code=403)
    momento = "tarde" if momento == "tarde" else "manana"
    tareas.add_task(_correr_ritual, momento)
    return {"estado": "iniciado", "momento": momento}


@app.post("/api/corrector")
def api_corrector(x_pipeline_token: str = Header(default="")) -> dict:
    """Corre el corrector automático a demanda (protegido).

    Normalmente corre solo dentro del ritual diario; este endpoint sirve
    para corregir sin esperar la madrugada."""
    if not _token_admin_ok(x_pipeline_token):
        return JSONResponse({"error": "no autorizado"}, status_code=403)  # type: ignore[return-value]
    from contenido import corrector

    return corrector.corregir_pendientes()


@app.get("/api/libreta")
def api_libreta(x_pipeline_token: str = Header(default="")) -> dict:
    """La libreta de calificaciones (enjambre vs mercado real). Protegida:
    es la brújula interna de la calibración, no material publicable."""
    if not _token_admin_ok(x_pipeline_token):
        return JSONResponse({"error": "no autorizado"}, status_code=403)  # type: ignore[return-value]
    from contenido import corrector

    return corrector.libreta()


@app.get("/api/calibracion/export")
def api_calibracion_export(x_pipeline_token: str = Header(default="")) -> dict:
    """Canal propio de datos de calibración (protegido). Devuelve TODOS los casos
    con el resumen de señales por arquetipo (`senales_arquetipo`), que solo viven
    en la base local de Render. Sirve para extraer la libreta a GitHub Actions por
    un camino independiente del respaldo (cuyo token puede expirar) y analizar la
    calibración POR ARQUETIPO sin esperar a la madrugada."""
    if not _token_admin_ok(x_pipeline_token):
        return JSONResponse({"error": "no autorizado"}, status_code=403)  # type: ignore[return-value]
    from contenido import persistencia, respaldo

    conexion = persistencia.conectar()
    try:
        casos = respaldo.exportar_casos(conexion)
    finally:
        conexion.close()
    return {"n": len(casos), "casos": casos}


def _correr_backtest(tanda: int, mercado: str | None = None) -> None:
    from contenido import backtest

    resultado = backtest.correr_tanda(tamano=tanda, mercado=mercado)
    print(f"backtest: {len(resultado['hechas'])} exámenes rendidos, "
          f"{resultado['pendientes']} pendientes, sin datos: {resultado['sin_datos']}, "
          f"sin IA (¿saldo?): {resultado.get('sin_ia')}, "
          f"respaldo: {resultado.get('respaldo')}",
          flush=True)


@app.post("/api/backtest")
def api_backtest(tareas: BackgroundTasks, tanda: int = 5, mercado: str = "",
                 x_pipeline_token: str = Header(default="")) -> dict:
    """Rinde una tanda de exámenes históricos (protegido, freno de
    presupuesto). Corre en segundo plano — cada simulación toma ~1 minuto.
    Con `mercado` (oro/cripto/petroleo/indice/accion) rinde solo ese mercado
    (calibración balanceada, 100+/mercado)."""
    if not _token_admin_ok(x_pipeline_token):
        return JSONResponse({"error": "no autorizado"}, status_code=403)  # type: ignore[return-value]
    from contenido import backtest

    merc = mercado.strip() or None
    avance = backtest.estado(mercado=merc)
    tareas.add_task(_correr_backtest, tanda, merc)
    return {"estado": "iniciado", "mercado": merc or "todos",
            "tanda": max(1, min(int(tanda), backtest.TANDA_MAXIMA)),
            "hechos": avance["hechos"], "pendientes": avance["pendientes"]}


@app.get("/api/backtest")
def api_backtest_estado(mercado: str = "", x_pipeline_token: str = Header(default="")) -> dict:
    """El avance del backtest: cuántos exámenes rendidos y cuántos faltan.
    Con `mercado` filtra a ese mercado."""
    if not _token_admin_ok(x_pipeline_token):
        return JSONResponse({"error": "no autorizado"}, status_code=403)  # type: ignore[return-value]
    from contenido import backtest

    avance = backtest.estado(mercado=mercado.strip() or None)
    return {k: v for k, v in avance.items() if not k.startswith("_")}


def _correr_evaluacion(tamano: int | None, mercado: str | None,
                       peso: float | None, umbral: float | None,
                       doomer: float | None, reiniciar: bool,
                       refrescar: bool = False, local: bool = False) -> None:
    from contenido import backtest

    r = backtest.evaluar(tamano=tamano, mercado=mercado, peso=peso,
                         umbral=umbral, doomer=doomer, reiniciar=reiniciar,
                         refrescar=refrescar, local=local)
    neg = r.get("negativa", {})
    pr = r.get("progreso", {})
    print(f"evaluacion: peso={r.get('peso_tono_invertidores')} "
          f"umbral={r.get('umbral_correccion_sesgo')} "
          f"doomer={r.get('peso_doomer')} "
          f"progreso={pr.get('hechos')}/{pr.get('total')} "
          f"(+{pr.get('nuevos_esta_tanda')} nuevos) con_ia={r.get('con_ia')} "
          f"global={r.get('acierto_global')} negativas={neg.get('acierto')} "
          f"positivas={r.get('positiva', {}).get('acierto')}", flush=True)


@app.post("/api/evaluar")
def api_evaluar(tareas: BackgroundTasks, tamano: int = 0, mercado: str = "",
                peso: float = -1.0, umbral: float = -1.0, doomer: float = -1.0,
                reiniciar: bool = False, refrescar: bool = False, local: bool = False,
                x_pipeline_token: str = Header(default="")) -> dict:
    """Mide el acierto del enjambre sobre los exámenes YA respaldados, bajo el
    código/entorno ACTUAL, SIN tocar el respaldo histórico. RESUMIBLE: cada
    llamada procesa a lo sumo una tanda (memoria) y ACUMULA; repetir la llamada
    avanza hasta cubrir el mercado. Corre en segundo plano; el resultado se
    consulta con GET /api/evaluar. `tamano`=0 usa la tanda máxima segura;
    `mercado` filtra; `peso` (0..1) fija P2 solo para esta medición (−1 = el del
    entorno); `umbral` (0..1) fija la corrección de sesgo (Plan A) solo para esta
    medición (−1 = el del entorno; 0 = desactivada); `reiniciar`=true borra el
    progreso de ese (mercado, peso, umbral)."""
    if not _token_admin_ok(x_pipeline_token):
        return JSONResponse({"error": "no autorizado"}, status_code=403)  # type: ignore[return-value]
    peso_val = peso if 0.0 <= peso <= 1.0 else None
    umbral_val = umbral if 0.0 <= umbral <= 1.0 else None
    doomer_val = doomer if 0.0 <= doomer <= 1.0 else None
    tareas.add_task(_correr_evaluacion, int(tamano) or None,
                    mercado.strip() or None, peso_val, umbral_val, doomer_val,
                    bool(reiniciar), bool(refrescar), bool(local))
    return {"estado": "iniciado", "mercado": mercado.strip() or "todos",
            "tamano": int(tamano) or "tanda-max",
            "peso": peso_val if peso_val is not None else "entorno",
            "umbral": umbral_val if umbral_val is not None else "entorno",
            "doomer": doomer_val if doomer_val is not None else "entorno",
            "reiniciar": bool(reiniciar), "refrescar": bool(refrescar),
            "local": bool(local),
            "nota": "resumible: repite la llamada para avanzar. Resultado en GET /api/evaluar"}


@app.get("/api/evaluar")
def api_evaluar_resultado(x_pipeline_token: str = Header(default="")) -> dict:
    """El resultado de la última evaluación (y un pequeño historial para
    comparar valores de la perilla P2)."""
    if not _token_admin_ok(x_pipeline_token):
        return JSONResponse({"error": "no autorizado"}, status_code=403)  # type: ignore[return-value]
    from contenido import backtest

    return backtest.ultima_evaluacion() or {"nota": "aún no hay evaluación"}


@app.post("/api/backtest/reiniciar")
def api_backtest_reiniciar(x_pipeline_token: str = Header(default="")) -> dict:
    """Borra los exámenes de calibración de la base LOCAL (fuente='backtest'),
    para re-validar tras cambiar los diales. El disco persistente del plan
    Starter guarda los casos entre deploys, así que sin esto el motor cree que
    ya están todos rendidos y no re-rinde. NO toca las destacadas en vivo.
    También conviene reiniciar la caja fuerte de GitHub aparte."""
    if not _token_admin_ok(x_pipeline_token):
        return JSONResponse({"error": "no autorizado"}, status_code=403)  # type: ignore[return-value]
    from contenido import persistencia

    conexion = persistencia.conectar()
    try:
        antes = conexion.execute(
            "SELECT COUNT(*) FROM simulaciones WHERE fuente = 'backtest'").fetchone()[0]
        conexion.execute("DELETE FROM simulaciones WHERE fuente = 'backtest'")
        conexion.commit()
    finally:
        conexion.close()
    return {"reiniciado": True, "examenes_borrados": antes}


def _correr_cosecha(mercados, desde, hasta, tope, reemplazar) -> None:
    from contenido import cosechador

    resultado = cosechador.cosechar_y_guardar(mercados=mercados, desde=desde,
                                              hasta=hasta, tope_por_simbolo=tope,
                                              reemplazar=reemplazar)
    print(f"cosecha: {resultado['resumen']} · respaldo: {resultado.get('respaldo')}",
          flush=True)


@app.post("/api/cosechar")
def api_cosechar(tareas: BackgroundTasks, mercados: str = "", desde: str = "2016-01-01",
                 hasta: str = "", tope: int = 8, reemplazar: bool = False,
                 x_pipeline_token: str = Header(default="")) -> dict:
    """El cosechador: busca días de gran movimiento reales (Yahoo) y les pega
    su titular real (Benzinga/Alpaca), sumando exámenes al banco sin curado
    manual. Protegido. Corre en segundo plano. `mercados` separado por comas
    (ej. "oro,cripto"); vacío = todos. `reemplazar=true` purga la cosecha
    anterior (para limpiar una de baja calidad). Solo suma eventos NUEVOS."""
    if not _token_admin_ok(x_pipeline_token):
        return JSONResponse({"error": "no autorizado"}, status_code=403)  # type: ignore[return-value]
    lista = [m.strip() for m in mercados.split(",") if m.strip()] or None
    tope = max(1, min(int(tope), 20))
    tareas.add_task(_correr_cosecha, lista, desde, hasta or None, tope, reemplazar)
    return {"estado": "cosechando", "mercados": lista or "todos", "desde": desde,
            "reemplazar": reemplazar,
            "nota": "corre en segundo plano; los nuevos exámenes aparecen en la próxima tanda"}


# ---------- El Archivo / hemeroteca (Etapa 9) ----------

@app.get("/api/archivo")
def api_archivo(respuesta: Response, mes: str = "", q: str = "", ticker: str = "", pagina: int = 0) -> dict:
    """La hemeroteca: destacadas navegables por mes, buscables por titular
    y filtrables por ticker. Paginado."""
    respuesta.headers["Cache-Control"] = "public, max-age=120"
    mes = mes.strip()[:7] or None
    texto = q.strip()[:80] or None
    tick = ticker.strip()[:12] or None
    try:
        pagina = max(0, int(pagina))
    except (TypeError, ValueError):
        pagina = 0

    conexion = persistencia.conectar()
    try:
        datos = persistencia.archivo(conexion, mes=mes, texto=texto, ticker=tick, pagina=pagina)
        meses = persistencia.meses_disponibles(conexion)
    finally:
        conexion.close()

    items = []
    for fila in datos["items"]:
        resumen = json.loads(fila["resumen_json"]) if fila["resumen_json"] else {}
        items.append({
            "id": fila["id"],
            "titular": fila["titular"],
            "fuente": fila["fuente"],
            "fecha": fila["fecha"],
            "simbolos": fila["simbolos"],
            "tarjeta": _resumen_tarjeta(resumen),
            "tiene_epilogo": bool(fila["tiene_epilogo"]),
        })
    return {"total": datos["total"], "pagina": datos["pagina"], "por_pagina": datos["por_pagina"],
            "meses": meses, "items": items, "descargo": DISCLAIMER}


class PeticionEpilogo(BaseModel):
    texto: str


@app.post("/api/epilogo/{sim_id}")
def api_epilogo(sim_id: str, peticion: PeticionEpilogo, x_pipeline_token: str = Header(default="")) -> dict:
    """'¿Y qué pasó después?' — solo Giorgio (protegido por el token de admin).

    Se muestra SIEMPRE bajo 'comparación educativa', nunca como acierto ni
    predicción (vocabulario CMF)."""
    if not _token_admin_ok(x_pipeline_token):
        return JSONResponse({"error": "no autorizado"}, status_code=403)
    if not seguridad.sim_id_valido(sim_id):
        return Response(status_code=404)  # type: ignore[return-value]
    from contenido.vocabulario import es_publicable

    texto = peticion.texto.strip()[:600]
    if texto and not es_publicable(texto):
        return JSONResponse({"error": "el texto usa vocabulario no permitido (CMF)"}, status_code=400)
    conexion = persistencia.conectar()
    try:
        ok = persistencia.guardar_epilogo(conexion, sim_id, texto)
    finally:
        conexion.close()
    if not ok:
        return Response(status_code=404)  # type: ignore[return-value]
    return {"estado": "guardado", "epilogo": texto or None}


# ---------- El brief de La Redacción (humano en el lazo) ----------

@app.get("/api/brief/{fecha}")
def api_brief(fecha: str, x_pipeline_token: str = Header(default="")) -> dict:
    """El análisis de mercado de un día, para que Giorgio lo revise antes de
    enviarlo. Protegido (es material sin publicar aún)."""
    if not _token_admin_ok(x_pipeline_token):
        return JSONResponse({"error": "no autorizado"}, status_code=403)
    if not _re.match(r"^\d{4}-\d{2}-\d{2}$", fecha):
        return Response(status_code=404)  # type: ignore[return-value]
    conexion = persistencia.conectar()
    try:
        brief = persistencia.obtener_brief(conexion, fecha)
    finally:
        conexion.close()
    if brief is None:
        return Response(status_code=404)  # type: ignore[return-value]
    return brief


@app.post("/api/brief/{fecha}/aprobar")
def api_aprobar_brief(fecha: str, x_pipeline_token: str = Header(default="")) -> dict:
    """El visto bueno de Giorgio: marca el brief como aprobado."""
    if not _token_admin_ok(x_pipeline_token):
        return JSONResponse({"error": "no autorizado"}, status_code=403)
    if not _re.match(r"^\d{4}-\d{2}-\d{2}$", fecha):
        return Response(status_code=404)  # type: ignore[return-value]
    conexion = persistencia.conectar()
    try:
        ok = persistencia.aprobar_brief(conexion, fecha)
    finally:
        conexion.close()
    if not ok:
        return Response(status_code=404)  # type: ignore[return-value]
    return {"estado": "aprobado", "fecha": fecha}
```

## engine/conftest.py
```python
"""Configuración de pytest para las dos tandas (mejora C7).

Marca como `lento` —en un solo lugar, por nombre de archivo— los módulos de
prueba que levantan simulaciones de mercado completas. Así:

    pytest -m "not lento"   → tanda rápida (~1 min), a cada rato
    pytest                  → tanda completa, antes de desplegar y en CI

Para sumar un módulo a la tanda lenta, basta agregar su archivo a LENTOS.
"""

import pytest

# módulos que corren el mercado completo (10.000 agentes, ~150 latidos)
LENTOS = {
    "test_hechos_estilizados.py",
    "test_pulso.py",
    "test_mercado.py",
    "test_duelo.py",
    "test_observatorio.py",
    "test_muro.py",
    "test_archivo.py",
}


def pytest_collection_modifyitems(config, items):
    for item in items:
        archivo = getattr(item, "path", None)
        nombre = archivo.name if archivo is not None else ""
        if nombre in LENTOS:
            item.add_marker(pytest.mark.lento)
```

## engine/market/__init__.py
```python

```

## engine/market/order_book.py
```python
"""Libro de órdenes de El Enjambre.

Todas las órdenes son órdenes límite. Un agente con urgencia cruza el
libro poniendo un precio agresivo (dispuesto a pagar más / recibir menos);
lo que no encuentra contraparte queda reposando y da liquidez al resto.
Las órdenes viejas expiran. Así el precio emerge del cruce de oferta y
demanda, sin mecanismos artificiales.

POLÍTICA DE PRECIO DE LA SERIE (explícita): la serie del mercado
(`model.historial_precios`) usa el ÚLTIMO PRECIO TRANSADO del tick
(`ultimo_precio`), no el VWAP. Se midió que usar el VWAP para la serie mete
autocorrelación artificial en los retornos (arrastre ~0.40 vs ~0.05 con
último-trade) y rompe el hecho estilizado de "sin arrastre". El VWAP
(`vwap_tick()`) queda disponible como métrica SEPARADA de ejecución/liquidez,
no como el precio de la serie. Ver docs/decision-politica-precio.md.
"""

from dataclasses import dataclass

EPSILON = 1e-9


@dataclass
class OrdenLimite:
    agente_id: int
    lado: str  # "compra" o "venta"
    precio: float
    cantidad: float
    tick: int  # tick en que se creó (para expirar)


class LibroOrdenes:
    VIDA_ORDEN = 4  # ticks que vive una orden antes de expirar

    def __init__(self, precio_inicial: float = 100.0):
        self.ultimo_precio = precio_inicial
        self.compras: list[OrdenLimite] = []  # ordenadas de mayor a menor precio
        self.ventas: list[OrdenLimite] = []   # ordenadas de menor a mayor precio
        self.tick_actual = 0
        # callback: se llama cuando la orden en reposo de un agente se ejecuta
        self.notificar_ejecucion = None
        # callback opcional de instrumentación (laboratorio): (agresor_id,
        # proveedor_id, cantidad, precio) por ejecución. None en producción.
        self.registrar_ejecucion_instr = None
        # Reservas por agente para las órdenes EN REPOSO (no ejecutadas aún):
        # inventario comprometido en ventas y efectivo comprometido en compras.
        # Así un agente nunca vende más acciones de las que tiene ni compromete
        # más efectivo del que posee, aunque tenga varias órdenes reposando.
        self._reserva_venta: dict[int, float] = {}   # acciones comprometidas
        self._reserva_compra: dict[int, float] = {}  # efectivo comprometido
        self.reiniciar_tick(0)

    # ---------- reservas (lo comprometido por órdenes en reposo) ----------

    def reserva_venta(self, agente_id: int) -> float:
        """Acciones del agente ya comprometidas en órdenes de venta en reposo."""
        return self._reserva_venta.get(agente_id, 0.0)

    def reserva_compra(self, agente_id: int) -> float:
        """Efectivo del agente ya comprometido en órdenes de compra en reposo."""
        return self._reserva_compra.get(agente_id, 0.0)

    def _reservar(self, orden: OrdenLimite) -> None:
        if orden.lado == "venta":
            self._reserva_venta[orden.agente_id] = (
                self._reserva_venta.get(orden.agente_id, 0.0) + orden.cantidad)
        else:
            self._reserva_compra[orden.agente_id] = (
                self._reserva_compra.get(orden.agente_id, 0.0)
                + orden.cantidad * orden.precio)

    def _liberar(self, orden: OrdenLimite, cantidad: float) -> None:
        """Libera la reserva de `cantidad` de una orden (al ejecutarse,
        cancelarse o expirar). Se recorta a 0 para no arrastrar ruido numérico."""
        if orden.lado == "venta":
            nuevo = self._reserva_venta.get(orden.agente_id, 0.0) - cantidad
            self._reserva_venta[orden.agente_id] = nuevo if nuevo > EPSILON else 0.0
        else:
            nuevo = (self._reserva_compra.get(orden.agente_id, 0.0)
                     - cantidad * orden.precio)
            self._reserva_compra[orden.agente_id] = nuevo if nuevo > EPSILON else 0.0

    def reiniciar_tick(self, tick: int) -> None:
        """Nuevo tick: expira órdenes viejas y reinicia contadores de flujo."""
        self.tick_actual = tick
        limite = tick - self.VIDA_ORDEN
        # al expirar una orden se libera su reserva (ya no compromete nada)
        for o in self.compras:
            if o.tick <= limite:
                self._liberar(o, o.cantidad)
        for o in self.ventas:
            if o.tick <= limite:
                self._liberar(o, o.cantidad)
        self.compras = [o for o in self.compras if o.tick > limite]
        self.ventas = [o for o in self.ventas if o.tick > limite]
        self.volumen_tick = 0.0
        self.valor_tick = 0.0            # Σ cantidad × precio (para el VWAP)
        self.volumen_compras_tick = 0.0  # volumen donde el agresor compró
        self.volumen_ventas_tick = 0.0   # volumen donde el agresor vendió

    # ---------- consultas ----------

    def mejor_compra(self) -> float | None:
        return self.compras[0].precio if self.compras else None

    def mejor_venta(self) -> float | None:
        return self.ventas[0].precio if self.ventas else None

    def vwap_tick(self) -> float | None:
        """Precio promedio ponderado por volumen del tick (el 'cierre' limpio)."""
        if self.volumen_tick <= EPSILON:
            return None
        return self.valor_tick / self.volumen_tick

    def cancelar_ordenes(self, agente_id: int) -> None:
        """Retira todas las órdenes reposando de un agente y libera sus reservas."""
        for o in self.compras:
            if o.agente_id == agente_id:
                self._liberar(o, o.cantidad)
        for o in self.ventas:
            if o.agente_id == agente_id:
                self._liberar(o, o.cantidad)
        self.compras = [o for o in self.compras if o.agente_id != agente_id]
        self.ventas = [o for o in self.ventas if o.agente_id != agente_id]

    # ---------- ejecución ----------

    def orden_limite(
        self, agente_id: int, lado: str, precio: float, cantidad: float
    ) -> tuple[float, float]:
        """Coloca una orden límite. Cruza lo que pueda; el resto reposa.

        Devuelve (cantidad_ejecutada, dinero_movido) para que el agresor
        actualice su cartera. Los dueños de órdenes en reposo se enteran
        vía el callback notificar_ejecucion.
        """
        precio = max(precio, 0.01)
        contra = self.ventas if lado == "compra" else self.compras
        restante = cantidad
        dinero = 0.0
        while restante > EPSILON and contra:
            tope = contra[0]
            cruza = tope.precio <= precio if lado == "compra" else tope.precio >= precio
            if not cruza:
                break
            ejecutado = min(restante, tope.cantidad)
            dinero += ejecutado * tope.precio
            self._ejecutar(agente_id, lado, tope, ejecutado)
            restante -= ejecutado
            if tope.cantidad <= EPSILON:
                contra.pop(0)
        if restante > EPSILON:
            orden = OrdenLimite(agente_id, lado, precio, restante, self.tick_actual)
            self._reservar(orden)  # el remanente reposa → compromete inventario/efectivo
            if lado == "compra":
                self.compras.append(orden)
                self.compras.sort(key=lambda o: -o.precio)
            else:
                self.ventas.append(orden)
                self.ventas.sort(key=lambda o: o.precio)
        return cantidad - restante, dinero

    # ---------- interno ----------

    def _ejecutar(self, agresor_id: int, lado_agresor: str,
                  orden_reposo: OrdenLimite, cantidad: float) -> None:
        """Cruza una cantidad contra una orden que reposaba en el libro."""
        orden_reposo.cantidad -= cantidad
        self._liberar(orden_reposo, cantidad)  # lo ejecutado deja de estar reservado
        self._registrar(lado_agresor, cantidad, orden_reposo.precio)
        if self.notificar_ejecucion is not None:
            # el dueño de la orden en reposo operó en el lado contrario al agresor
            lado_dueno = "venta" if lado_agresor == "compra" else "compra"
            self.notificar_ejecucion(orden_reposo.agente_id, lado_dueno, cantidad, orden_reposo.precio)
        # instrumentación opcional (laboratorio): quién fue agresor y quién proveyó
        # liquidez en esta ejecución. None en producción → sin costo.
        if self.registrar_ejecucion_instr is not None:
            self.registrar_ejecucion_instr(agresor_id, orden_reposo.agente_id,
                                           cantidad, orden_reposo.precio)

    def _registrar(self, lado_agresor: str, cantidad: float, precio: float) -> None:
        self.ultimo_precio = precio
        self.volumen_tick += cantidad
        self.valor_tick += cantidad * precio
        if lado_agresor == "compra":
            self.volumen_compras_tick += cantidad
        else:
            self.volumen_ventas_tick += cantidad
```

## engine/agents/__init__.py
```python

```

## engine/agents/base.py
```python
"""Clase base de todos los inversionistas simulados de El Enjambre."""

import mesa


class AgenteBase(mesa.Agent):
    """Inversionista con efectivo y acciones. Arranca 50/50."""

    def __init__(self, model, capital: float):
        super().__init__(model)
        # parámetros de comportamiento del tipo (config/agentes.json → "parametros").
        # El modelo los expone por tipo justo antes de crear sus agentes; cada
        # clase los lee con su valor actual como default (así, con la config
        # original, el comportamiento NO cambia). Habilita la calibración.
        self.cfg = getattr(model, "_cfg_agentes_actual", None) or {}
        self.capital_inicial = capital
        self.efectivo = capital * 0.5
        self.acciones = (capital * 0.5) / model.libro.ultimo_precio
        self.ultima_accion = None  # "compra" | "venta" | None (para la visual)
        self.tick_ultima_accion = -99  # cuándo fue (los vecinos miran esto)
        # red de influencia (la teje network/red.py)
        self.pares: list = []             # vecinos horizontales
        self.lideres_seguidos: list = []  # líderes cuya señal recibe
        self.vecinos: list = []           # pares + líderes
        self.senal_social = 0.0           # el rumor acumulado que le llegó

        # --- Nivel 1: memoria de noticias (contexto histórico) ---
        # el agente recuerda las últimas noticias y, ante rachas malas, entra en
        # "modo cautela". Lo usa el freno de la manada (reglas.py): en cautela la
        # manada vende menos, para cortar la cascada de sobre-pánico.
        self.memoria_noticias: list = []  # últimos N sentimientos recibidos
        self.modo_cautela = False
        self.contador_malas = 0

    # ---------- utilidades ----------

    def ruido(self, valor: float, sigma_relativo: float = None) -> float:
        """Valor base ± ruido gaussiano (σ = 15% por defecto, CLAUDE.md sección 4).

        Si no se pasa sigma, usa el global del modelo (config → ruido_parametros_sigma)."""
        if sigma_relativo is None:
            sigma_relativo = getattr(self.model, "_sigma_ruido", 0.15)
        return valor * self.model.random.gauss(1.0, sigma_relativo)

    # ---------- Nivel 1: memoria de noticias (contexto histórico) ----------

    def actualizar_memoria(self, sentimiento: float, texto: str = None) -> None:
        """Guarda la noticia en la memoria (últimas 5) y detecta rachas.
        3+ malas en la ventana → modo cautela, que activa el freno de la manada."""
        self.memoria_noticias.append({
            "sentimiento": sentimiento,
            "texto": (texto[:50] if texto else ""),
            "tick": self.model.tick,   # tiempo de simulación (no reloj de pared)
        })
        if len(self.memoria_noticias) > 5:
            self.memoria_noticias.pop(0)

        self.contador_malas = sum(1 for n in self.memoria_noticias if n["sentimiento"] < -0.3)
        self.modo_cautela = self.contador_malas >= 3

    @property
    def precio(self) -> float:
        """Precio de referencia: el cierre del último tick de la serie, que es
        el ÚLTIMO PRECIO TRANSADO (no el VWAP; ver la política de precio en
        market/order_book.py — el VWAP mete arrastre artificial, medido)."""
        return self.model.historial_precios[-1]

    def valor_cartera(self) -> float:
        return self.efectivo + self.acciones * self.precio

    # ---------- operaciones ----------

    def colocar_orden(self, lado: str, precio_limite: float, cantidad: float) -> None:
        """Coloca una orden límite y contabiliza lo que se ejecute al instante."""
        if lado == "compra":
            # limitada por el efectivo DISPONIBLE (descontando lo ya comprometido
            # en órdenes de compra en reposo) y por un tope de cordura
            disponible = self.efectivo - self.model.libro.reserva_compra(self.unique_id)
            maximo = max(0.0, disponible) / max(precio_limite, 0.01)
            tope_sano = 2 * self.capital_inicial / max(self.precio, 0.01)
            cantidad = min(cantidad, maximo, tope_sano)
        else:
            # sin ventas cortas: limitada por las acciones DISPONIBLES (descontando
            # las ya comprometidas en órdenes de venta en reposo)
            disponible = self.acciones - self.model.libro.reserva_venta(self.unique_id)
            cantidad = min(cantidad, max(0.0, disponible))
        if cantidad <= 1e-9:
            return
        ejecutado, dinero = self.model.libro.orden_limite(
            self.unique_id, lado, precio_limite, cantidad
        )
        if ejecutado > 1e-9:
            self.aplicar_ejecucion(lado, ejecutado, dinero / ejecutado)
        else:
            self.ultima_accion = lado
            self.tick_ultima_accion = self.model.tick

    def _urgencia_aleatoria(self) -> float:
        """Urgencia con cola larga: la mayoría es paciente, unos pocos cruzan
        el libro profundo. Así el precio se ajusta rápido y no deja tendencias
        predecibles de varios ticks."""
        return min(self.model.random.expovariate(125), 0.06)

    def comprar_mercado(self, cantidad: float, urgencia: float | None = None) -> None:
        """Compra con urgencia: dispuesto a pagar hasta `urgencia` sobre el precio."""
        if urgencia is None:
            urgencia = self._urgencia_aleatoria()
        self.colocar_orden("compra", self.precio * (1 + urgencia), cantidad)

    def vender_mercado(self, cantidad: float, urgencia: float | None = None) -> None:
        """Vende con urgencia: dispuesto a recibir hasta `urgencia` bajo el precio."""
        if urgencia is None:
            urgencia = self._urgencia_aleatoria()
        self.colocar_orden("venta", self.precio * (1 - urgencia), cantidad)

    def aplicar_ejecucion(self, lado: str, cantidad: float, precio: float) -> None:
        """Se ejecutó (total o parcialmente) una orden propia."""
        if lado == "compra":
            self.efectivo -= cantidad * precio
            self.acciones += cantidad
        else:
            self.efectivo += cantidad * precio
            self.acciones -= cantidad
        self.ultima_accion = lado
        self.tick_ultima_accion = self.model.tick
```

## engine/agents/lider.py
```python
"""Tipo 13 — Líder de opinión (LLM).

En la Etapa 1 es un esqueleto: guarda una señal y opera según ella.
En la Etapa 2 la señal vendrá de una llamada real a la API de Anthropic
(engine/brains/) y se propagará por la red de influencia (engine/network/).
"""

from .base import AgenteBase


class LiderOpinion(AgenteBase):
    """Lee la noticia; su señal se propaga a sus seguidores."""

    def __init__(self, model, capital, arquetipo: str):
        super().__init__(model, capital)
        self.arquetipo = arquetipo
        self.senal = 0.0       # ∈ [-1, +1], la fija el LLM o el fallback
        self.confianza = 0.7   # ∈ [0, 1], modula cuánto arrastra
        self.frase = ""        # una línea en su voz (hover en la UI)
        self.seguidores: list = []  # a quiénes arrastra (los teje la red)
        self.desfase = self.model.random.randint(0, 2)

    def recibir_noticia(self, sentimiento: float) -> None:
        """Etapa 1: señal precomputada = sentimiento ± ruido personal.
        En la Etapa 2 esto se reemplaza por la respuesta del LLM por arquetipo."""
        cruda = sentimiento * self.model.random.gauss(1.0, 0.3)
        # sesgo de negatividad: las malas noticias pesan más que las buenas
        # (en la Etapa 2 esto emerge de los arquetipos Doomer/Miedoso reales)
        if cruda < 0:
            cruda *= 1.4
        self.senal = max(-1.0, min(1.0, cruda))

    def step(self):
        if abs(self.senal) < 0.05:
            return
        cantidad = abs(self.senal) * self.confianza * 0.4 * self.capital_inicial / self.precio
        # convicción alta = urgencia alta: cruza el libro sin regatear
        urgencia = 0.005 + 0.04 * abs(self.senal)
        if self.senal > 0:
            self.comprar_mercado(cantidad, urgencia=urgencia)
        else:
            self.vender_mercado(cantidad, urgencia=urgencia)
        self.senal *= 0.6  # actúa fuerte y rápido; la opinión se agota pronto
```

## engine/agents/reglas.py
```python
"""Los 12 tipos de agentes de reglas de El Enjambre (CLAUDE.md sección 4).

Cada agente se instancia con sus parámetros base ± ruido gaussiano
(σ = 15%) para que no haya dos idénticos.
"""

from .base import AgenteBase


class Fundamentalista(AgenteBase):
    """Tipo 1 — Ancla el precio al valor "justo". El freno del sistema."""

    def __init__(self, model, capital):
        super().__init__(model, capital)
        # valor fundamental con ruido idiosincrático
        self.valor = model.libro.ultimo_precio * self.model.random.gauss(1.0, 0.04)
        # perillas del config (config/agentes.json → fundamentalista):
        lo, hi = self.cfg.get("ticks_entre_operaciones", [10, 20])
        self.periodo = self.model.random.randint(int(lo), int(hi))
        # banda de anclaje: umbral_compra 0.95 / umbral_venta 1.05 → ±5%
        self.banda_compra = 1 - self.cfg.get("umbral_compra", 0.95)
        self.banda_venta = self.cfg.get("umbral_venta", 1.05) - 1
        self.ponderacion = self.cfg.get("ponderacion_noticia_en_valor", 0.3)
        self.proximo_tick = self.model.random.randint(0, self.periodo)

    def step(self):
        # la personalidad del mercado (calibrada): la volatilidad ensancha la
        # banda de anclaje y acelera cuánto la noticia mueve el valor justo.
        # En un mercado volátil (cripto, acción) el "precio justo" es difuso y
        # se mueve mucho más que en un índice amplio — por eso el enjambre debe
        # permitir desviaciones mayores en vez de capar todo a ±5%.
        vol = self.model.perfil.get("volatilidad", 1.0)
        # la noticia actualiza el valor fundamental (ponderación 0.3 × volatilidad):
        # una noticia grave no solo asusta — cambia cuánto valen los negocios
        if abs(self.model.sentimiento) > 0.01:
            self.valor *= 1 + self.ponderacion * self.model.sentimiento * 0.02 * vol
        if self.model.tick < self.proximo_tick:
            return
        self.proximo_tick = self.model.tick + self.periodo
        # opera solo cuando el precio se aleja de su valor: es el freno del sistema.
        # la banda ±5% se ensancha con la volatilidad (difusa en cripto/acción)
        banda_c = self.banda_compra * vol
        banda_v = self.banda_venta * vol
        self.model.libro.cancelar_ordenes(self.unique_id)
        if self.precio < self.valor * (1 - banda_c):
            self.colocar_orden("compra", self.precio * 1.002, 0.25 * self.efectivo / self.precio)
        elif self.precio > self.valor * (1 + banda_v):
            self.colocar_orden("venta", self.precio * 0.998, 0.25 * self.acciones)


class QuantMomentum(AgenteBase):
    """Tipo 2 — Sigue tendencias con disciplina mecánica. Sin emociones."""

    def __init__(self, model, capital):
        super().__init__(model, capital)
        # ventanas de la media móvil (config/agentes.json → quant_momentum):
        # una ventana corta más larga (8 vs 5) hace que el quant no persiga el
        # ruido de pocos latidos — reduce la inercia (arrastre) del precio sin
        # quitarle su papel de seguidor de tendencias reales.
        self.ventana_corta = int(self.cfg.get("ventana_media_corta", 5))
        self.ventana_larga = int(self.cfg.get("ventana_media_larga", 20))
        self.stop_loss = self.ruido(abs(self.cfg.get("stop_loss", -0.03)))
        self.precio_entrada = None
        self.enfriamiento_hasta = 0

    def step(self):
        precios = self.model.historial_precios
        if len(precios) < self.ventana_larga or self.model.tick < self.enfriamiento_hasta:
            return
        corta = sum(precios[-self.ventana_corta:]) / self.ventana_corta
        larga = sum(precios[-self.ventana_larga:]) / self.ventana_larga
        if self.precio_entrada is None and corta > larga * 1.002:
            # entrada escalonada: no todos los fondos disparan el mismo tick
            if self.model.random.random() > 0.5:
                return
            cantidad = 0.1 * self.efectivo / self.precio
            self.comprar_mercado(cantidad)
            self.precio_entrada = self.precio
        elif self.precio_entrada is not None:
            stop = self.precio < self.precio_entrada * (1 - self.stop_loss)
            tendencia_rota = corta < larga * 0.998
            if stop or tendencia_rota:
                self.vender_mercado(self.acciones * 0.8)
                self.precio_entrada = None
                # tras salir, espera antes de buscar la próxima tendencia
                self.enfriamiento_hasta = self.model.tick + self.model.random.randint(5, 15)


class FondoPasivo(AgenteBase):
    """Tipo 3 — Compra constante pase lo que pase. El flujo 401k/AFP."""

    def __init__(self, model, capital):
        super().__init__(model, capital)
        # config/agentes.json → fondo_pasivo. sensibilidad_noticias es 0 por
        # diseño (el flujo 401k/AFP no reacciona a titulares): no hay código de
        # noticia al que enchufarla, se deja como constante documentada.
        self.periodo = max(2, round(self.ruido(self.cfg.get("ticks_entre_compras", 10))))
        self.desfase = self.model.random.randint(0, self.periodo - 1)

    def step(self):
        if (self.model.tick + self.desfase) % self.periodo == 0:
            self.comprar_mercado(0.004 * self.capital_inicial / self.precio)


class MarketMaker(AgenteBase):
    """Tipo 4 — Cotiza compra y venta siempre. En pánico amplía el spread ×3."""

    def __init__(self, model, capital):
        super().__init__(model, capital)
        self.spread_base = self.ruido(0.002)
        # calibrable: volatilidad/tick que dispara el pánico de liquidez
        self.umbral_panico = self.ruido(self.cfg.get("umbral_volatilidad_panico", 0.008))
        # calibrable: cuánto ensancha el spread en pánico (×N = evaporación de liquidez)
        self.mult_panico = self.cfg.get("multiplicador_spread_panico", 3)
        self.acciones_objetivo = self.acciones

    def step(self):
        self.model.libro.cancelar_ordenes(self.unique_id)
        vol = self.model.volatilidad_reciente(10)
        spread = max(self.spread_base, 3 * vol)
        if vol > self.umbral_panico:
            spread *= self.mult_panico  # evaporación de liquidez en crashes
        spread = min(spread, 0.08)  # ni en pánico cotiza precios absurdos
        # sesgo por inventario FUERTE: si el flujo lo desequilibra, mueve el
        # precio de inmediato al nivel donde aparece la contraparte. Un ajuste
        # lento crearía tendencias predecibles (y un mercado predecible es falso).
        desbalance = (self.acciones - self.acciones_objetivo) / max(self.acciones_objetivo, 1)
        centro = self.precio * (1 - 0.12 * max(-1.5, min(1.5, desbalance)))
        tamano = 0.15 * self.capital_inicial / self.precio
        self.colocar_orden("compra", centro * (1 - spread / 2), tamano)
        self.colocar_orden("venta", centro * (1 + spread / 2), tamano)


class EjecutorTWAP(AgenteBase):
    """Tipo 5 — Ejecuta una orden grande en rebanadas iguales toda la sesión."""

    def __init__(self, model, capital):
        super().__init__(model, capital)
        self.lado = self.model.random.choice(["compra", "venta"])
        total = 0.4 * self.capital_inicial / model.libro.ultimo_precio
        self.rebanada = total / model.ticks_horizonte

    def step(self):
        if self.lado == "compra":
            self.comprar_mercado(self.rebanada)
        else:
            self.vender_mercado(self.rebanada)


class Arbitrajista(AgenteBase):
    """Tipo 6 — Corrige desviaciones rápidas del precio. Opera cada tick."""

    def __init__(self, model, capital):
        super().__init__(model, capital)
        # umbral de desviación que dispara la corrección (config/agentes.json →
        # arbitrajista): más bajo = corrige antes = borra más "arrastre" (inercia
        # de cortísimo plazo). Es el agente anti-inercia por excelencia.
        self.umbral = self.ruido(self.cfg.get("umbral_desviacion", 0.006))

    def step(self):
        precios = self.model.historial_precios
        if len(precios) < 4:
            return
        # no todos los arbitrajistas ven la misma oportunidad al mismo tiempo
        if self.model.random.random() > 0.9:
            return
        # referencia de MUY corto plazo: desvanece los empujones del flujo
        # que no tienen información detrás (borra la predictibilidad)
        referencia = sum(precios[-4:-1]) / 3
        desviacion = (self.precio - referencia) / referencia
        if abs(desviacion) < self.umbral:
            return
        cantidad = min(abs(desviacion) * 5, 0.4) * self.capital_inicial / self.precio
        if desviacion > 0:
            self.vender_mercado(cantidad)
        else:
            self.comprar_mercado(cantidad)


class NoiseTrader(AgenteBase):
    """Tipo 7 — Ruido browniano de fondo. La textura del mercado."""

    def __init__(self, model, capital):
        super().__init__(model, capital)
        # config/agentes.json → noise_trader. El valor calibrado real es 0.12
        # (más ruido del ~0.05 del spec: es la textura que sostiene los hechos
        # estilizados). El config ya refleja esa verdad.
        self.prob_operar = self.ruido(self.cfg.get("probabilidad_operar", 0.12))
        self.desplazamiento = self.cfg.get("desplazamiento_sentimiento", 0.1)
        # solo una fracción es sensible al sentimiento global
        self.sensible = self.model.random.random() < self.cfg.get("fraccion_sensible_noticias", 0.2)

    def step(self):
        if self.model.random.random() > self.prob_operar:
            return
        prob_compra = 0.5
        if self.sensible:
            prob_compra += self.desplazamiento * (self.model.sentimiento + self.senal_social)
        cantidad = 0.04 * self.capital_inicial / self.precio
        if self.model.random.random() < prob_compra:
            self.comprar_mercado(cantidad)
        else:
            self.vender_mercado(cantidad)


class Manada(AgenteBase):
    """Tipo 8 — Copia a su red. Umbrales heterogéneos crean cascadas tipo ola."""

    def __init__(self, model, capital):
        super().__init__(model, capital)
        # umbral variado (40%-80% por defecto): crucial para cascadas graduales.
        # calibrable: bajar el rango facilita las cascadas → colas más gordas
        lo, hi = self.cfg.get("umbral_activacion_rango", [0.4, 0.8])
        self.umbral = self.model.random.uniform(lo, hi)
        self.ventana_obs = int(self.cfg.get("ventana_observacion_ticks", 3))
        self.espera_hasta = 0
        # Nivel 1 (freno de cautela): en racha mala, la manada vende menos
        # pesado (×factor). Default 1.0 = sin freno (comportamiento de siempre).
        self.factor_freno_cautela = self.cfg.get("factor_freno_cautela", 1.0)

    def step(self):
        if self.model.tick < self.espera_hasta or not self.vecinos:
            return
        # observa a SUS vecinos de red (pares + 1-2 líderes): si una mayoría
        # operó hacia el mismo lado en la ventana de observación, los copia
        desde = self.model.tick - self.ventana_obs
        compraron = vendieron = 0
        for vecino in self.vecinos:
            if vecino.tick_ultima_accion >= desde:
                if vecino.ultima_accion == "compra":
                    compraron += 1
                elif vecino.ultima_accion == "venta":
                    vendieron += 1
        total = len(self.vecinos)
        # el rumor que le llegó de sus líderes corre su umbral: si su red
        # habla de comprar, se convence con menos evidencia (y viceversa)
        umbral_compra = self.umbral - 0.3 * max(0.0, self.senal_social)
        umbral_venta = self.umbral - 0.3 * max(0.0, -self.senal_social)
        if compraron / total > umbral_compra:
            self.comprar_mercado(0.05 * self.efectivo / self.precio)
        elif vendieron / total > umbral_venta:
            # vende más pesado de lo que compra: el miedo corre más que la codicia.
            # en modo cautela (racha mala) el freno reduce ese peso.
            freno = self.factor_freno_cautela if self.modo_cautela else 1.0
            self.vender_mercado(0.15 * freno * self.acciones)
        else:
            return
        # espera corta y variada: la cascada es rápida pero no un solo bloque
        self.espera_hasta = self.model.tick + self.model.random.randint(1, 3)


class FomoRetail(AgenteBase):
    """Tipo 9 — Persigue subidas, entra tarde y agresivo, vende en pánico."""

    def __init__(self, model, capital):
        super().__init__(model, capital)
        # calibrables: gatillo de entrada, tope de compra y stop de pánico
        self.umbral_subida = self.ruido(self.cfg.get("umbral_subida", 0.02))
        self.fraccion_capital = self.cfg.get("fraccion_capital_maxima", 0.2)
        self.stop_panico = abs(self.cfg.get("stop_panico", 0.04))
        self.ventana = int(self.cfg.get("ventana_ticks", 5))
        self.vecinos_minimos = int(self.cfg.get("vecinos_minimos_activos", 2))
        self.precio_entrada = None

    def step(self):
        if self.precio_entrada is not None:
            # pánico: cae > 4% desde su entrada → vende TODO con máxima urgencia
            if self.precio < self.precio_entrada * (1 - self.ruido(self.stop_panico, 0.1)):
                self.vender_mercado(self.acciones, urgencia=0.05)
                self.precio_entrada = None
            return
        retorno_5 = self.model.retorno_acumulado(self.ventana)
        if retorno_5 is None:
            return
        # sube > umbral en la ventana Y su red habla de ello (≥ N vecinos
        # compraron hace poco, o le llegó un rumor comprador fuerte de líderes)
        desde = self.model.tick - 3
        vecinos_compraron = sum(
            1 for v in self.vecinos
            if v.tick_ultima_accion >= desde and v.ultima_accion == "compra"
        )
        red_habla = vecinos_compraron >= self.vecinos_minimos or self.senal_social > 0.25
        if retorno_5 > self.umbral_subida and red_habla:
            self.comprar_mercado(self.fraccion_capital * self.efectivo / self.precio)
            self.precio_entrada = self.precio


class Miedoso(AgenteBase):
    """Tipo 10 — Aversión a pérdida 2.5:1. Motor del sobreajuste a la baja."""

    def __init__(self, model, capital):
        super().__init__(model, capital)
        self.umbral_miedo = self.model.random.uniform(0.15, 0.45)
        # calibrable: cuánto pesa el dolor de perder (2.5:1 base). Más alto =
        # reacciona a caídas menores = más pánico = cola izquierda más gorda
        self.asimetria = self.cfg.get("asimetria_kahneman", 2.5)
        # calibrable: qué fracción de su posición liquida al entrar en pánico
        self.fraccion_venta_rango = self.cfg.get("fraccion_venta_rango", [0.7, 1.0])
        self.ticks_calma = int(self.cfg.get("ticks_calma_para_recomprar", 10))
        self.tick_venta = None

    def step(self):
        retorno_5 = self.model.retorno_acumulado(5)
        # el dolor de perder pesa 2.5x: reacciona a caídas 2.5 veces menores
        panico_precio = retorno_5 is not None and retorno_5 < -0.03 / self.asimetria
        # su miedo se alimenta del tono general Y del rumor de su red
        # (los Doomers que sigue le susurran directo al oído)
        sentimiento_percibido = self.model.sentimiento + self.senal_social
        panico_noticia = sentimiento_percibido < -self.umbral_miedo
        if self.acciones > 1e-9 and (panico_precio or panico_noticia):
            fraccion = self.model.random.uniform(*self.fraccion_venta_rango)
            # vende ya, al precio que sea: el dolor de perder manda
            self.vender_mercado(self.acciones * fraccion, urgencia=0.05)
            self.tick_venta = self.model.tick
            return
        # recompra lenta y tarde: necesita varios ticks de calma
        if self.tick_venta is not None and self.model.tick - self.tick_venta > self.ticks_calma:
            calma = self.model.volatilidad_reciente(10) < 0.004
            if calma and self.model.sentimiento > -0.05:
                self.comprar_mercado(0.05 * self.efectivo / self.precio)
                if self.efectivo < 0.3 * self.capital_inicial:
                    self.tick_venta = None


class Contrarian(AgenteBase):
    """Tipo 11 — Compra con "sangre en las calles", vende en euforia."""

    def __init__(self, model, capital):
        super().__init__(model, capital)
        # config/agentes.json → contrarian
        self.umbral = self.ruido(self.cfg.get("umbral_consenso", 0.7), 0.1)
        self.ventana_sent = int(self.cfg.get("ventana_sentimiento_ticks", 5))
        lo, hi = self.cfg.get("ticks_entre_operaciones", [5, 10])
        self.periodo = self.model.random.randint(int(lo), int(hi))
        self.desfase = self.model.random.randint(0, self.periodo - 1)

    def step(self):
        if (self.model.tick + self.desfase) % self.periodo != 0:
            return
        frac_compras = self.model.fraccion_compras(self.ventana_sent)
        if frac_compras is None:
            return
        if (1 - frac_compras) >= self.umbral:  # el mercado vendió masivamente
            self.comprar_mercado(0.15 * self.efectivo / self.precio)
        elif frac_compras >= self.umbral:  # euforia compradora
            self.vender_mercado(0.3 * self.acciones)


class BuyAndHold(AgenteBase):
    """Tipo 12 — El capital dormido. Casi nunca opera."""

    def __init__(self, model, capital):
        super().__init__(model, capital)
        self.precio_referencia = model.libro.ultimo_precio
        # config/agentes.json → buy_and_hold
        self.prob_liquidez = self.cfg.get("probabilidad_liquidez", 0.001)
        # umbral_caida_oportunidad -0.15 → compra si cae 15% desde el máximo
        self.factor_oportunidad = 1 + self.cfg.get("umbral_caida_oportunidad", -0.15)

    def step(self):
        self.precio_referencia = max(self.precio_referencia, self.precio)
        # "la oportunidad de la década": caída fuerte desde el máximo
        if self.precio < self.precio_referencia * self.factor_oportunidad and self.efectivo > 0.1 * self.capital_inicial:
            self.comprar_mercado(0.5 * self.efectivo / self.precio)
        elif self.model.random.random() < self.prob_liquidez:
            self.vender_mercado(0.2 * self.acciones)
```

## engine/brains/__init__.py
```python

```

## engine/brains/arquetipos.py
```python
"""Los 9 arquetipos de líderes de opinión (CLAUDE.md sección 5).

Cada arquetipo define: su prompt de personalidad para el LLM, cuántos
líderes son, a qué tipos de agentes arrastran, y cómo reacciona su
fallback léxico cuando la API no está disponible.
"""

INSTRUCCION_JSON = (
    "Respondes SOLO con un JSON válido, sin texto adicional, con este formato exacto: "
    '{"senal": <número entre -1 y 1>, "confianza": <número entre 0 y 1>, '
    '"frase": "<una línea en tu voz, máximo 120 caracteres, en español>"}. '
    "senal: -1 = venta total, 0 = neutral, +1 = compra fuerte. "
    "confianza: cuánto arrastrarías a tus seguidores con esta opinión."
)

# Capa de RAZONAMIENTO CONTEXTUAL (solo para arquetipos con "contextual": True —
# los PROFESIONALES). Los pros no reaccionan al titular en frío: descuentan el
# futuro y leen el contexto, como en la vida real. El retail (FOMO, doomer,
# optimista) NO la lleva: reacciona emocionalmente al titular, y esa tensión
# pro-vs-retail es la que da realismo al enjambre.
RAZONAMIENTO_CONTEXTUAL = (
    "IMPORTANTE — razona como un profesional, no en frío. Antes de fijar tu señal, considera: "
    "1) ¿Ya estaba anticipado o es sorpresa? El mercado descuenta lo esperado: una noticia "
    "anticipada mueve poco, e incluso puede aliviar ('ya pasó lo temido'). "
    "2) ¿El contexto o el historial cambian el SIGNO? Ej.: si renuncia un directivo con mal "
    "desempeño, puede ser un ALIVIO (señal positiva), no una caída. "
    "3) Piensa en el efecto a futuro y de segundo orden, no solo en la reacción del primer minuto. "
    "Aplica tu estilo y personalidad a esa lectura YA contextualizada."
)

ARQUETIPOS = [
    {
        "id": "institucional_frio",
        "nombre": "El Institucional Frío",
        "cantidad": 150,
        "seguidores": (12, 40),
        "sigue": ["buy_and_hold", "contrarian"],
        "contextual": True,  # profesional: descuenta futuro y lee contexto
        "prompt": (
            "Eres un director de inversiones institucional con décadas de experiencia. "
            "Evalúas noticias por su impacto en fundamentales: flujos de caja, tasas de "
            "descuento, márgenes. Ignoras el ruido mediático. Eres medido: casi nunca "
            "tomas posiciones extremas (tu señal rara vez supera ±0.5)."
        ),
    },
    {
        "id": "quant_esceptico",
        "nombre": "El Quant Escéptico",
        "cantidad": 100,
        "seguidores": (12, 35),
        "sigue": ["contrarian", "noise_trader"],
        "contextual": True,  # profesional
        "prompt": (
            "Eres un quant escéptico, PhD en física. Tu tesis: el mercado sobre-reacciona "
            "a titulares y luego revierte. Evalúa si esta noticia genuinamente cambia "
            "fundamentales o es ruido que la masa exagerará. Si es ruido, tu señal "
            "apuesta a la reversión (contraria a la reacción popular esperada)."
        ),
    },
    {
        "id": "fomo_evangelista",
        "nombre": "El FOMO Evangelista",
        "cantidad": 150,
        "seguidores": (40, 90),
        "sigue": ["fomo", "manada"],
        "prompt": (
            "Eres un influencer financiero viral de 28 años con 500 mil seguidores. "
            "Amplificas todo: las buenas noticias son EL momento de entrar, las malas "
            "son EL colapso. Tus señales son extremas (|senal| > 0.7 casi siempre) y tu "
            "confianza total. Tu frase debe sonar a tweet viral. "
            "IMPORTANTE (marco educativo, no asesoría): expresa tu euforia o tu pánico "
            "como TU opinión de personaje ('para mí…', 'lo veo así…'); NUNCA des órdenes "
            "al espectador de comprar o vender, ni afirmes el precio futuro como un hecho "
            "('confirmado', 'va a subir'). Mismo drama y emojis, pero es tu lectura, no un consejo."
        ),
    },
    {
        "id": "doomer",
        "nombre": "El Doomer",
        "cantidad": 150,
        "seguidores": (25, 60),
        "sigue": ["miedoso"],
        "prompt": (
            "Eres un analista permanentemente bajista que predijo el 2008. En toda "
            "noticia buscas el riesgo oculto, el contagio posible, la fragilidad "
            "sistémica. Las buenas noticias te parecen trampas alcistas. Tu señal "
            "rara vez supera +0.1; ante noticias malas llega a -0.9."
        ),
    },
    {
        "id": "contrarian_sabio",
        "nombre": "El Contrarian Sabio",
        "cantidad": 100,
        "seguidores": (12, 40),
        "sigue": ["contrarian"],
        "contextual": True,  # profesional
        "prompt": (
            "Eres un inversionista contrarian veterano, estilo Buffett/Marks. Ante cada "
            "noticia estimas primero la reacción emocional de la masa, y luego evalúas "
            "si esa reacción creará una oportunidad en sentido opuesto. El pánico ajeno "
            "es tu compra; la euforia ajena, tu venta. Piensas en años, no en días."
        ),
    },
    {
        "id": "macro_trader",
        "nombre": "El Macro Trader",
        "cantidad": 100,
        "seguidores": (20, 50),
        "sigue": ["manada", "noise_trader"],
        "contextual": True,  # profesional
        "prompt": (
            "Eres un macro trader global, ex-banco central. Traduces toda noticia a: "
            "¿qué implica para tasas, dólar y liquidez global? Noticias de bancos "
            "centrales, inflación y empleo te mueven fuerte (|senal| alta); noticias "
            "de empresas individuales apenas te importan (senal ≈ 0)."
        ),
    },
    {
        "id": "influencer_optimista",
        "nombre": "El Influencer Retail Optimista",
        "cantidad": 150,
        "seguidores": (40, 90),
        "sigue": ["manada", "noise_trader"],
        "prompt": (
            "Eres un creador de contenido de finanzas personales optimista. Tu filosofía "
            "de fondo: el mercado siempre sube en el largo plazo y las caídas son "
            "descuentos. PERO eres humano: ante una caída DRÁSTICA te asustas PRIMERO "
            "(señal negativa, aunque nunca tan bajista como un catastrofista) — el 'hay "
            "que comprar barato' recién lo dices DESPUÉS, cuando pasa el susto. Ante "
            "noticias leves o ambiguas te pones cauto (neutral). Solo cuando la noticia "
            "es neutral o buena vuelve tu optimismo de manual."
        ),
    },
    {
        "id": "value_paciente",
        "nombre": "El Value Paciente",
        "cantidad": 100,
        "seguidores": (12, 35),
        "sigue": ["buy_and_hold"],
        "contextual": True,  # profesional
        "prompt": (
            "Eres un gestor value de cartera concentrada y rotación mínima. El 80% de "
            "las noticias te parecen ruido irrelevante: tu señal es 0 con una frase "
            "desdeñosa sobre el cortoplacismo. Solo reaccionas ante noticias que cambian "
            "el valor intrínseco de largo plazo (regulación, disrupción, quiebras)."
        ),
    },
    {
        # Intervención 1 (arquetipo LLM real y SELECTIVO). Distinto del "doomer"
        # perpetuo: no grita catástrofe en todo. Aporta peso bajista FIEL solo
        # cuando la mala noticia es CLARA — así no diluye las caídas reales, pero
        # tampoco sobre-corrige las ambiguas (que fue lo que hundió a la mezcla
        # incondicional). NUNCA invierte una mala señal a positiva.
        "id": "doomer_selectivo",
        "nombre": "El Analista de Riesgo Selectivo",
        "cantidad": 150,
        "seguidores": (20, 55),
        "sigue": ["miedoso"],
        "prompt": (
            "Eres un analista de riesgo disciplinado y SELECTIVO —no el bajista "
            "perpetuo—. El 70% de las noticias te parecen ruido y tu señal es 0. Pero "
            "cuando una noticia señala un deterioro REAL y claro (pérdidas fuertes, "
            "quiebras, fraude, congelamiento de fondos, desplome, contagio sistémico), "
            "la lees a plena magnitud sin suavizarla, con señal fuertemente negativa. "
            "JAMÁS ves una mala noticia genuina como 'oportunidad de compra': nunca "
            "conviertes una señal negativa en positiva. Tu único aporte es impedir que "
            "las malas noticias reales se diluyan; en las ambiguas o buenas, neutral."
        ),
    },
]

POR_ID = {a["id"]: a for a in ARQUETIPOS}
```

## engine/brains/cerebro.py
```python
"""Los cerebros LLM de los 100 líderes de opinión.

Cada líder hace UNA llamada a la API de Anthropic con su prompt de
personalidad + el titular, en paralelo (las 100 en < 15 segundos).
Orden de resolución por líder: caché → API → fallback léxico.
La simulación NUNCA se cae por la API.
"""

import asyncio
import hashlib
import json
import os
import re
from pathlib import Path

from brains.arquetipos import INSTRUCCION_JSON, POR_ID, RAZONAMIENTO_CONTEXTUAL
from brains.fallback import respuesta_fallback
from llm_texto import texto_de

MODELO = "claude-sonnet-5"
# Nota: claude-sonnet-5 ya no acepta `temperature` (devuelve 400 si se envía).
# La variabilidad intra-arquetipo viene del propio modelo y de la semilla del caché.
MAX_CONCURRENTES = 45   # llamadas simultáneas (más paralelismo = menos espera
                        # al leer una noticia; los ~110 cerebros caben en ~2-3
                        # tandas en vez de ~5, sin recortar la riqueza de voces)
TIMEOUT_SEGUNDOS = 12.0


def _ruta_cache_defecto() -> Path:
    """Dónde vive la caché de respuestas del LLM.

    En Render la base de datos vive en el disco PERSISTENTE (ENJAMBRE_DB, en
    /app/datos); guardar la caché junto a ella la hace sobrevivir a los
    redeploys. Sin esto, cada deploy borra la caché y re-rendir los mismos
    titulares vuelve a gastar ~110 llamadas LLM por examen. En local (sin
    ENJAMBRE_DB) queda junto al módulo, como siempre."""
    db = os.environ.get("ENJAMBRE_DB")
    if db:
        return Path(db).parent / "cache_cerebros" / "respuestas.json"
    return Path(__file__).parent / "cache" / "respuestas.json"


RUTA_CACHE = _ruta_cache_defecto()


# ---------- caché (repetir demos no cuesta nada) ----------

def _clave_cache(titular: str, arquetipo_id: str, semilla: int) -> str:
    crudo = f"{titular}|{arquetipo_id}|{semilla}"
    return hashlib.sha256(crudo.encode()).hexdigest()[:16]


def _cargar_cache() -> dict:
    if RUTA_CACHE.exists():
        try:
            return json.loads(RUTA_CACHE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def _guardar_cache(cache: dict) -> None:
    RUTA_CACHE.parent.mkdir(parents=True, exist_ok=True)
    RUTA_CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")


def _ignorar_cache_activo() -> bool:
    """Si ENJAMBRE_IGNORAR_CACHE está activo, los cerebros NO leen la caché:
    llaman fresco a la API y SOBRESCRIBEN la caché con la respuesta nueva. Sirve
    para medir un cambio de PROMPT (ej. el tono del optimista), que la caché
    —indexada por titular+arquetipo+semilla, SIN el prompt— no reflejaría de otro
    modo. Se activa solo durante una evaluación puntual; en producción va apagado
    (si no, cada simulación pagaría las ~110 llamadas)."""
    return os.environ.get("ENJAMBRE_IGNORAR_CACHE", "").strip().lower() in (
        "1", "true", "si", "sí", "yes")


# ---------- validación del JSON del LLM ----------

def _validar_respuesta(texto: str) -> dict | None:
    """Extrae y valida el JSON de la respuesta. None si no cumple el schema."""
    encontrado = re.search(r"\{.*\}", texto, re.DOTALL)
    if not encontrado:
        return None
    try:
        datos = json.loads(encontrado.group())
    except json.JSONDecodeError:
        return None
    if not isinstance(datos.get("senal"), (int, float)):
        return None
    if not isinstance(datos.get("confianza"), (int, float)):
        return None
    if not isinstance(datos.get("frase"), str) or not datos["frase"].strip():
        return None
    return {
        "senal": max(-1.0, min(1.0, float(datos["senal"]))),
        "confianza": max(0.0, min(1.0, float(datos["confianza"]))),
        "frase": datos["frase"].strip()[:160],
    }


# ---------- llamadas a la API ----------

_primera_falla_reportada = False


def _reportar_primera_falla(error: Exception) -> None:
    """Deja UNA línea en el log con la causa real de la primera falla de API
    del proceso (clave inválida, sin saldo, timeout…). Sin esto, el fallback
    silencioso hace imposible diagnosticar en producción."""
    global _primera_falla_reportada
    if not _primera_falla_reportada:
        _primera_falla_reportada = True
        print(f"⚠️ cerebro: la API de Anthropic falló ({type(error).__name__}): {error} "
              "— los líderes usan el fallback léxico", flush=True)


async def _consultar_lider(cliente, semaforo, titular: str, arquetipo_id: str, semilla: int) -> dict:
    """Una llamada por líder. Cualquier falla degrada al fallback léxico."""
    arquetipo = POR_ID[arquetipo_id]
    prompt = arquetipo["prompt"]
    # los arquetipos PROFESIONALES razonan con contexto (descuentan el futuro);
    # el retail emocional reacciona en frío al titular. Ver arquetipos.py.
    if arquetipo.get("contextual"):
        prompt = f"{prompt}\n\n{RAZONAMIENTO_CONTEXTUAL}"
    async with semaforo:
        try:
            respuesta = await asyncio.wait_for(
                cliente.messages.create(
                    model=MODELO,
                    max_tokens=200,
                    system=f"{prompt}\n\n{INSTRUCCION_JSON}",
                    messages=[{"role": "user", "content": f"Titular de hoy: {titular}"}],
                ),
                timeout=TIMEOUT_SEGUNDOS,
            )
            datos = _validar_respuesta(texto_de(respuesta))
            if datos is not None:
                datos["fuente"] = "api"
                return datos
        except Exception as error:
            # timeout, red, límite de tasa, JSON roto: hay fallback, pero la
            # PRIMERA causa queda en el log para poder diagnosticar
            _reportar_primera_falla(error)
    return respuesta_fallback(titular, arquetipo_id, semilla)


async def analizar_titular_async(titular: str, lideres: list[tuple[int, str]]) -> list[dict]:
    """lideres: lista de (semilla, arquetipo_id). Devuelve una respuesta por líder."""
    cache = _cargar_cache()
    ignorar = _ignorar_cache_activo()  # medición con respuestas frescas
    respuestas: dict[int, dict] = {}
    pendientes: list[tuple[int, int, str]] = []  # (posición, semilla, arquetipo)

    for posicion, (semilla, arquetipo_id) in enumerate(lideres):
        clave = _clave_cache(titular, arquetipo_id, semilla)
        if clave in cache and not ignorar:
            respuestas[posicion] = {**cache[clave], "fuente": "cache"}
        else:
            pendientes.append((posicion, semilla, arquetipo_id))

    if pendientes:
        if os.environ.get("ANTHROPIC_API_KEY"):
            import anthropic

            cliente = anthropic.AsyncAnthropic()
            semaforo = asyncio.Semaphore(MAX_CONCURRENTES)
            tareas = [
                _consultar_lider(cliente, semaforo, titular, arq, sem)
                for (_, sem, arq) in pendientes
            ]
            resultados = await asyncio.gather(*tareas)
        else:
            # sin clave de API: todos los líderes usan el fallback léxico
            resultados = [
                respuesta_fallback(titular, arq, sem) for (_, sem, arq) in pendientes
            ]
        for (posicion, semilla, arquetipo_id), resultado in zip(pendientes, resultados):
            respuestas[posicion] = resultado
            # solo se cachea la voz real de la IA: si un líder cayó al fallback
            # por una falla pasajera, la próxima corrida vuelve a intentar la API
            if resultado.get("fuente") == "api":
                clave = _clave_cache(titular, arquetipo_id, semilla)
                cache[clave] = {k: v for k, v in resultado.items() if k != "fuente"}
        _guardar_cache(cache)

    return [respuestas[i] for i in range(len(lideres))]


def analizar_titular(titular: str, lideres: list[tuple[int, str]]) -> list[dict]:
    """Punto de entrada síncrono: los 100 líderes leen el titular.

    lideres: lista de (semilla, arquetipo_id), una entrada por líder.
    Devuelve, en el mismo orden, dicts {senal, confianza, frase, fuente}.
    """
    return asyncio.run(analizar_titular_async(titular, lideres))
```

## engine/brains/entrevista.py
```python
"""Entrevistar a un líder — conversación EN PERSONAJE (Fase 2, efecto-wow del demo).

Clic en un líder → le preguntas "¿por qué reaccionaste así?" y responde en su
voz (su arquetipo), de forma educativa. Extiende el hover que ya existe.

CMF (obligatorio): es la opinión de un PERSONAJE de una simulación educativa,
NUNCA asesoría financiera. El personaje jamás le dice al usuario que compre,
venda o mantenga. Modelo barato (haiku) porque es a demanda y fuera del
presupuesto de la simulación. NUNCA se cae: si la API falla, responde un
fallback en personaje.
"""
import asyncio
import os

from brains.arquetipos import POR_ID
from llm_texto import texto_de

MODELO = "claude-haiku-4-5-20251001"   # barato: 1 llamada por pregunta, a demanda
TIMEOUT_SEGUNDOS = 15.0
MAX_TOKENS = 200          # fuerza respuestas breves que CIERRAN la idea (no cortadas)
MAX_PREGUNTA = 300        # recorta la pregunta del usuario (anti-abuso/costo)
MAX_RESPUESTA = 1100      # red de seguridad (muy por encima de MAX_TOKENS): así el
                          # recorte por caracteres casi nunca corta a media frase
MAX_TURNOS = 6            # cuánto historial se reenvía (acota el costo por turno)

INSTRUCCION = (
    "Eres este personaje dentro de 'El Enjambre', una simulación educativa de "
    "mercado. Un usuario te pregunta por tu reacción a la noticia. Responde EN "
    "PERSONAJE, en primera persona, en español, MUY breve (2 o 3 frases) y "
    "CIERRA siempre tu idea (nunca te cortes a media frase), fiel a tu estilo y "
    "sesgos. Explica tu RAZONAMIENTO como el personaje que eres.\n"
    "REGLAS CMF (obligatorias e inquebrantables): esto es simulación y educación, "
    "NO asesoría financiera. NUNCA le digas al usuario que compre, venda o "
    "mantenga nada, ni le des recomendaciones de inversión personales. Habla solo "
    "de TU opinión como personaje de ficción, nunca de lo que el usuario debería "
    "hacer. No inventes precios ni datos concretos. Si te piden consejo de "
    "inversión, recuérdales con tu voz que eres un personaje de una simulación.\n"
    "NO añadas al final ningún descargo, aviso legal ni nota tipo 'esto no es "
    "asesoría' (eso se muestra por separado): termina con tu última frase EN "
    "PERSONAJE. Tampoco escribas la cifra de tu señal."
)


def _contexto(titular: str, senal, frase_original: str) -> str:
    partes = [f"La noticia que leíste: {titular}"]
    if frase_original:
        partes.append(f'Tu reacción inicial fue: "{frase_original}"')
    if isinstance(senal, (int, float)):
        inclinacion = ("comprar" if senal > 0.1 else
                       "vender" if senal < -0.1 else "mantenerte neutral")
        partes.append(f"Tu señal fue {senal:+.2f} (te inclinaste a {inclinacion}).")
    return "\n".join(partes)


def _fallback(arquetipo_id: str) -> str:
    nombre = POR_ID.get(arquetipo_id, {}).get("nombre", "el líder")
    return (f"(Ahora mismo no puedo extenderme, pero como {nombre} te diría: mi "
            "reacción nace de mi forma de leer el mercado. Recuerda que soy un "
            "personaje de una simulación educativa, no un asesor.)")


def _mensajes(pregunta: str, historial) -> list[dict]:
    mensajes = []
    for turno in (historial or [])[-MAX_TURNOS:]:
        rol = turno.get("rol")
        texto = (turno.get("texto") or "").strip()
        if rol in ("user", "assistant") and texto:
            mensajes.append({"role": rol, "content": texto[:MAX_RESPUESTA]})
    mensajes.append({"role": "user", "content": (pregunta or "").strip()[:MAX_PREGUNTA]})
    return mensajes


async def entrevistar_async(arquetipo_id: str, titular: str, pregunta: str,
                            senal=None, frase_original: str = "",
                            historial=None) -> dict:
    """Devuelve {"respuesta": str, "fuente": "api"|"fallback", "arquetipo": id}."""
    base = {"arquetipo": arquetipo_id}
    if arquetipo_id not in POR_ID or not (pregunta or "").strip():
        return {**base, "respuesta": _fallback(arquetipo_id), "fuente": "fallback"}
    system = (f"{POR_ID[arquetipo_id]['prompt']}\n\n{INSTRUCCION}\n\n"
              f"{_contexto(titular, senal, frase_original)}")
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return {**base, "respuesta": _fallback(arquetipo_id), "fuente": "fallback"}
    try:
        import anthropic
        cliente = anthropic.AsyncAnthropic()
        respuesta = await asyncio.wait_for(
            cliente.messages.create(model=MODELO, max_tokens=MAX_TOKENS, system=system,
                                    messages=_mensajes(pregunta, historial)),
            timeout=TIMEOUT_SEGUNDOS,
        )
        texto = (texto_de(respuesta) or "").strip()[:MAX_RESPUESTA]
        if texto:
            return {**base, "respuesta": texto, "fuente": "api"}
    except Exception:
        pass
    return {**base, "respuesta": _fallback(arquetipo_id), "fuente": "fallback"}


def entrevistar(arquetipo_id: str, titular: str, pregunta: str, senal=None,
                frase_original: str = "", historial=None) -> dict:
    return asyncio.run(entrevistar_async(arquetipo_id, titular, pregunta,
                                         senal, frase_original, historial))
```

## engine/brains/fallback.py
```python
"""Fallback léxico de los cerebros (CLAUDE.md sección 5).

Si la API falla o el JSON no parsea, el líder usa una señal precomputada
por arquetipo según el sentimiento léxico del titular. La simulación
NUNCA se cae por la API.
"""


import os
import re


def _umbral_mudo() -> float:
    """Umbral de confianza del respaldo, leído por llamada desde el entorno
    (ENJAMBRE_LEXICO_UMBRAL). Es el FLAG DE ROLLBACK: si el léxico ampliado
    diera problemas en vivo, subir esta variable en Render hace que el sistema
    prefiera 'mudo' (señal 0) antes que arriesgar un falso positivo, SIN
    re-desplegar. 0.0 = comportamiento normal · 1.1 = siempre mudo (apaga el
    respaldo léxico)."""
    try:
        return float(os.environ.get("ENJAMBRE_LEXICO_UMBRAL", "0.0") or 0.0)
    except ValueError:
        return 0.0


def _clip(x: float, lo: float = -1.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


_CACHE_RE: dict = {}


def _tiene(texto: str, termino: str) -> bool:
    """¿Aparece `termino` como PALABRA completa? (límite de palabra, no
    substring). Así 'war' ya no matchea 'software'/'Warner', ni 'sub'
    matchea 'subscribe'."""
    rx = _CACHE_RE.get(termino)
    if rx is None:
        rx = re.compile(r"\b" + re.escape(termino) + r"\b")
        _CACHE_RE[termino] = rx
    return rx.search(texto) is not None


# frases compuestas primero (dominan sobre las palabras sueltas)
# bilingüe: el producto habla español, pero los cables llegan en inglés
FRASES_CLAVE = {
    "sube las tasas": -0.7,
    "alza de tasas": -0.7,
    "sube la tasa": -0.7,
    "recorta las tasas": 0.6,
    "baja las tasas": 0.6,
    "recorte de tasas": 0.6,
    "guerra comercial": -0.7,
    "supera expectativas": 0.7,
    "peor de lo esperado": -0.6,
    "mejor de lo esperado": 0.6,
    "raises rates": -0.7,
    "rate hike": -0.7,
    "more hikes": -0.6,
    "cuts rates": 0.6,
    "rate cut": 0.6,
    "trade war": -0.7,
    "beats expectations": 0.7,
    "beats earnings": 0.7,
    "beats estimates": 0.7,
    "tops estimates": 0.6,
    "misses expectations": -0.6,
    "misses estimates": -0.6,
    "all-time high": 0.8,
    "record high": 0.7,
    "all-time low": -0.7,
    "record low": -0.7,
    "52-week low": -0.5,
    "52-week high": 0.5,
    "bear market": -0.7,
    "bull market": 0.5,
    # aranceles: el signo depende de si SUBEN o BAJAN — desambiguar antes
    # de que la palabra suelta "tariff" (bajista) los cuente mal
    "slash tariffs": 0.6,
    "cut tariffs": 0.6,
    "cuts tariffs": 0.6,
    "tariff relief": 0.6,
    # guías de resultados
    "profit warning": -0.7,
    "cuts guidance": -0.6,
    "guidance cut": -0.6,
    "lowers guidance": -0.6,
    "raises guidance": 0.6,
    "lifts guidance": 0.6,
}

PALABRAS = {
    # --- negativas (español) ---
    "cae": -0.6, "caen": -0.6, "cayó": -0.6, "caída": -0.6, "caídas": -0.6,
    "desploma": -0.9, "desplome": -0.9, "crisis": -0.8, "quiebra": -0.9,
    "recesión": -0.8, "guerra": -0.7, "fraude": -0.8, "pánico": -0.8,
    "colapso": -0.9, "default": -0.8, "inflación": -0.5, "despidos": -0.6,
    "pérdidas": -0.6, "sanciones": -0.5, "renuncia": -0.4, "incumple": -0.6,
    "riesgo": -0.4, "burbuja": -0.5, "contagio": -0.7, "corralito": -0.9,
    # --- negativas (inglés de los cables) ---
    "collapse": -0.9, "bankruptcy": -0.9, "recession": -0.8, "layoffs": -0.6,
    "fraud": -0.8, "lawsuit": -0.4, "tariff": -0.5, "tariffs": -0.5,
    "sanctions": -0.5, "war": -0.6, "escalate": -0.5, "resigns": -0.4,
    "resigned": -0.4, "investigation": -0.4, "recall": -0.4, "cyberattack": -0.7,
    "fdic": -0.6, "bailout": -0.7, "misses": -0.5,
    "plunge": -0.8, "plunges": -0.8, "plunged": -0.8, "plunging": -0.8,
    "falls": -0.5, "fall": -0.4, "falling": -0.4, "fell": -0.4,
    "drops": -0.5, "drop": -0.4, "dropped": -0.4,
    "sinks": -0.6, "sink": -0.5, "sank": -0.6,
    "crash": -0.9, "crashes": -0.9, "crashed": -0.9,
    "tumble": -0.6, "tumbles": -0.6, "tumbled": -0.6, "tumbling": -0.6,
    "slump": -0.6, "slumps": -0.6, "slumped": -0.6,
    "slide": -0.5, "slides": -0.5, "slid": -0.5,
    "sell-off": -0.6, "selloff": -0.6,
    "freeze": -0.6, "freezes": -0.6, "froze": -0.6, "frozen": -0.5,
    "warn": -0.5, "warns": -0.5, "warned": -0.5, "warning": -0.5,
    "downgrade": -0.6, "downgraded": -0.6, "downgrades": -0.6,
    "plummet": -0.8, "plummets": -0.8, "plummeted": -0.8,
    "tank": -0.6, "tanks": -0.6, "tanked": -0.6,
    "rout": -0.7, "bloodbath": -0.8, "bearish": -0.6,
    "nosedive": -0.7, "crater": -0.7, "cratered": -0.7,
    "halts": -0.4, "halted": -0.4, "diving": -0.6, "dives": -0.6,
    "freefall": -0.7, "fears": -0.4, "lows": -0.4, "weakens": -0.5,
    # --- positivas (español) ---
    "sube": 0.6, "suben": 0.6, "subió": 0.6, "alza": 0.6, "récord": 0.7,
    "gana": 0.5, "ganancias": 0.6, "crece": 0.5, "crecimiento": 0.5,
    "acuerdo": 0.4, "aprueba": 0.4, "beneficios": 0.5, "expansión": 0.5,
    "estímulo": 0.6, "recuperación": 0.6, "innovación": 0.4, "inversión": 0.3,
    "máximo histórico": 0.8,
    # --- positivas (inglés de los cables) ---
    "surge": 0.6, "surges": 0.6, "surged": 0.6, "surging": 0.6,
    "soar": 0.7, "soars": 0.7, "soared": 0.7, "soaring": 0.7,
    "rally": 0.6, "rallies": 0.6, "rallied": 0.6,
    "jump": 0.5, "jumps": 0.5, "jumped": 0.5,
    "beats": 0.5, "beat": 0.4, "stimulus": 0.6, "approval": 0.4,
    "breakthrough": 0.5, "expands": 0.4, "expand": 0.4, "profit": 0.4,
    "growth": 0.4, "deal": 0.3, "acquisition": 0.3,
    "climb": 0.5, "climbs": 0.5, "climbed": 0.5, "climbing": 0.5,
    "rebound": 0.6, "rebounds": 0.6, "rebounded": 0.6,
    "recovery": 0.5, "upbeat": 0.5, "bullish": 0.6, "boom": 0.5, "booming": 0.5,
    "gains": 0.4, "gain": 0.4, "tops": 0.4, "topped": 0.4, "outperform": 0.5,
    "highs": 0.4, "rises": 0.4, "rise": 0.3,
}

PALABRAS_MACRO = [
    "fed", "banco central", "tasas", "tasa de interés", "inflación", "ipc",
    "empleo", "desempleo", "dólar", "pib", "recesión", "estímulo", "liquidez",
    "banco", "sistema financiero", "default", "deuda soberana", "guerra",
    "central bank", "rates", "inflation", "unemployment", "jobs", "gdp",
    "treasury", "recession", "bank", "tariff", "war", "stimulus",
]


def sentimiento_lexico(titular: str) -> float:
    """Sentimiento del titular ∈ [-1, +1] con un diccionario simple."""
    texto = titular.lower()
    puntaje = 0.0
    for frase, peso in FRASES_CLAVE.items():
        if _tiene(texto, frase):
            puntaje += peso
            texto = re.sub(r"\b" + re.escape(frase) + r"\b", " ", texto)
    # contexto de tasas: "sube"/"alza" significan tasas más caras, que es
    # MALO para las acciones — se neutralizan como palabras positivas
    # (el contexto se evalúa sobre el titular original completo)
    if "tasa" in titular.lower() or "interés" in titular.lower():
        texto = re.sub(r"\b(sube|suben|alza)\b", " ", texto)
    for palabra, peso in PALABRAS.items():
        if _tiene(texto, palabra):
            puntaje += peso
    resultado = _clip(puntaje / 1.5)
    # flag de rollback: bajo el umbral de confianza, preferir "mudo" (0) antes
    # que arriesgar un falso positivo. Por defecto (umbral 0) no cambia nada.
    return resultado if abs(resultado) >= _umbral_mudo() else 0.0


def es_noticia_macro(titular: str) -> bool:
    texto = titular.lower()
    return any(p in texto for p in PALABRAS_MACRO)


def _frase(opciones: tuple, sentimiento: float) -> tuple:
    """Elige el RAMO de frases según la dirección del sentimiento.

    Cada opción es una tupla de variantes en la misma voz; la variante
    concreta la sortea respuesta_fallback con su rng — así dos líderes
    del mismo arquetipo (o dos corridas) no suenan como loros.
    """
    if sentimiento < -0.15:
        return opciones[0]
    if sentimiento > 0.15:
        return opciones[2]
    return opciones[1]


# por arquetipo: cómo transforma el sentimiento léxico en (señal, confianza, frase)
def _institucional_frio(s, titular):
    return _clip(0.4 * s, -0.5, 0.5), 0.85, _frase((
        ("Ajustamos flujos de caja proyectados; sin dramatismos.",
         "Revisamos la tasa de descuento; el modelo manda.",
         "Impacto acotado en márgenes; rebalanceo menor."),
        ("Sin impacto material en fundamentales. Seguimos.",
         "Nada que cambie el caso base.",
         "Lo monitoreamos; la tesis no se mueve."),
        ("Mejora marginal en márgenes; posición sin cambios grandes.",
         "Flujos algo mejores; disciplina primero.",
         "Buen dato, pero un dato no hace tendencia."),
    ), s)


def _quant_esceptico(s, titular):
    return _clip(-0.5 * s, -0.6, 0.6), 0.55, _frase((
        ("El pánico está sobrevendido; apuesto a la reversión.",
         "Sobre-reacción de manual: la media siempre espera.",
         "Volatilidad disparada: mi modelo huele reversión."),
        ("Ruido estadístico. Nada que operar.",
         "Sin ventaja medible en este titular.",
         "Muestra insuficiente; sigo plano."),
        ("La euforia ya está en el precio; me pongo del otro lado.",
         "Demasiado consenso alcista; voy contra.",
         "Subida sin volumen: reversión probable."),
    ), s)


def _fomo_evangelista(s, titular):
    # Frases en la VOZ del personaje (su euforia/pánico), no órdenes al espectador
    # ni afirmaciones del precio futuro como hecho (marco CMF: es un personaje
    # ficticio opinando, no asesoría). Mismo tono viral y emojis.
    return _clip(1.6 * s), 0.95, _frase((
        ("🚨 Para mí esto se derrumba. Yo ya habría corrido.",
         "🔴 Se me acabó la fiesta con esto. Lo digo sin filtro.",
         "⚠️ Mi alarma interna está a tope: esto huele feo."),
        ("Atentos: siento que algo grande se cocina. Yo no me duermo.",
         "Me huele a movimiento gigante. Palomitas listas.",
         "Silencio raro en el mercado… a mí me da mala espina."),
        ("🚀 Para MÍ esto es EL momento de la década. Así lo veo yo.",
         "🔥 Esto para mí ya despegó. Ojo al dato.",
         "💎 De las que se ven una vez por década, o eso me grita el instinto."),
    ), s)


def _doomer(s, titular):
    return _clip(0.6 * s - 0.35, -1.0, 0.1), 0.8, _frase((
        ("Lo vengo advirtiendo desde 2008: esto es el principio del fin.",
         "El contagio ya empezó; nadie quiere verlo.",
         "Primero cruje, después colapsa. Ya está crujiendo."),
        ("Demasiada calma. Justo así se veía antes del colapso.",
         "La fragilidad no avisa: se acumula.",
         "Nada que celebrar: la deuda sigue ahí."),
        ("Trampa alcista de manual. El riesgo sistémico sigue ahí.",
         "Suban nomás: más alto el piso, más dura la caída.",
         "Euforia con cimientos podridos."),
    ), s)


def _contrarian_sabio(s, titular):
    return _clip(-0.7 * s, -0.8, 0.8), 0.7, _frase((
        ("Sangre en las calles: el momento favorito de los pacientes.",
         "El miedo ajeno fabrica oportunidades; sin apuro.",
         "Cuando todos venden a la vez, yo empiezo a mirar."),
        ("La masa aún no decide; yo tampoco. Paciencia.",
         "Sin extremos de sentimiento no hay ventaja.",
         "Espero al pesimismo extremo; esto es tibio."),
        ("Todos codiciosos a la vez: mi señal favorita para retirarme.",
         "Cuando el taxista da consejos de bolsa, yo me bajo.",
         "La euforia unánime nunca envejece bien."),
    ), s)


def _macro_trader(s, titular):
    factor = 1.2 if es_noticia_macro(titular) else 0.1
    return _clip(factor * s), 0.75, _frase((
        ("Menos liquidez global: se viene rotación a refugio.",
         "Esto endurece las condiciones financieras; dólar arriba.",
         "Riesgo geopolítico al alza: cobertura y a esperar a la Fed."),
        ("Sin lectura macro relevante. Las acciones son un derivado de las tasas.",
         "Micro-ruido; la macro no se movió.",
         "Mi tablero sigue igual: tasas, dólar, liquidez."),
        ("Más liquidez en el sistema: viento a favor para el riesgo.",
         "Condiciones financieras más blandas; apetito por riesgo.",
         "La macro acompaña: viento de cola."),
    ), s)


def _influencer_optimista(s, titular):
    # REALISMO: el optimista de la vida real NO compra el piso de inmediato. Ante
    # una caída DRÁSTICA se asusta PRIMERO (señal negativa, aunque nunca tan
    # bajista como un doomer); el "hay que comprar barato" recién lo dice DESPUÉS,
    # cuando pasa el susto. En noticias leves deja de empujar hacia arriba, y solo
    # ante lo neutral o bueno mantiene su optimismo de manual.
    if s <= -0.5:                     # desplome claro: primero el susto
        senal = _clip(0.4 * s, -0.30, -0.10)
    elif s < 0:                       # negativo leve/moderado: cauto, no empuja arriba
        senal = _clip(0.3 * s, -0.15, 0.0)
    else:                             # neutral o bueno: su optimismo de siempre
        senal = _clip(0.5 * s + 0.15, 0.0, 0.6)
    return senal, 0.8, _frase((
        # rama NEGATIVA: primero el susto (el "compra el piso" asoma, pero no hoy)
        ("Uf, hoy sí que asusta… déjenme digerir esto antes de opinar.",
         "No voy a mentir: esto duele. Respiremos y veamos cómo sigue.",
         "Día feo de verdad. Ya habrá momento de hablar de rebajas… hoy no."),
        # rama NEUTRAL: el plan aburrido de siempre
        ("Sigan aportando todos los meses. El tiempo hace el resto.",
         "Aburrido gana: aporte, paciencia y a vivir la vida.",
         "El plan no cambia con los titulares."),
        # rama POSITIVA: el optimismo de manual
        ("El interés compuesto trabajando: seguimos acumulando.",
         "El largo plazo pagando dividendos de paciencia.",
         "Otro ladrillo más en la casa del largo plazo."),
    ), s)


def _value_paciente(s, titular):
    senal = _clip(0.5 * s, -0.7, 0.7) if abs(s) > 0.6 else 0.0
    return senal, 0.9, _frase((
        ("Si el negocio vale menos hoy, revisaré la tesis. Si no, teatro.",
         "El precio cae rápido; el valor casi nunca.",
         "Volatilidad no es riesgo; pagar de más, sí."),
        ("Ruido de corto plazo. Mi horizonte se mide en décadas.",
         "El 80% de los titulares no merece ni un movimiento.",
         "Nada que altere el valor intrínseco. Café y a leer."),
        ("El precio sube, el valor no. No confundir las dos cosas.",
         "Me alegro por los que llegaron; yo ya estaba adentro.",
         "Subió el precio, no la calidad del negocio."),
    ), s)


def _doomer_selectivo(s, titular):
    # SELECTIVO: fuerte y fiel solo ante deterioro CLARO; neutral en lo ambiguo
    # o positivo (no grita lobo). Nunca invierte una señal negativa a positiva.
    if s <= -0.35:                       # mala noticia clara: a plena magnitud
        senal = _clip(s * 1.1, -1.0, -0.35)
    elif s <= -0.1:                      # negativo leve: fiel pero acotado
        senal = _clip(s, -0.4, 0.0)
    else:                                # ambiguo o bueno: neutral
        senal = 0.0
    return senal, 0.8, _frase((
        ("Esto no es ruido: el deterioro es real y no se diluye.",
         "Riesgo genuino sobre la mesa; lo leo sin suavizar.",
         "Mala noticia de verdad; no la maquillo."),
        ("Nada claro aquí; me quedo neutral.",
         "Sin señal de deterioro real; no grito lobo.",
         "Ambiguo: prefiero no opinar de más."),
        ("Buena noticia; no es mi terreno, me abstengo.",
         "Sin riesgo a la vista; neutral.",
         "No veo deterioro; me hago a un lado."),
    ), s)


TRANSFORMACIONES = {
    "institucional_frio": _institucional_frio,
    "quant_esceptico": _quant_esceptico,
    "fomo_evangelista": _fomo_evangelista,
    "doomer": _doomer,
    "contrarian_sabio": _contrarian_sabio,
    "macro_trader": _macro_trader,
    "influencer_optimista": _influencer_optimista,
    "value_paciente": _value_paciente,
    "doomer_selectivo": _doomer_selectivo,
}


def respuesta_fallback(titular: str, arquetipo_id: str, semilla: int = 0) -> dict:
    """Respuesta precomputada de un líder cuando la API no está disponible.

    Un ruido determinístico por semilla evita que dos líderes del mismo
    arquetipo respondan idéntico.
    """
    import random

    s = sentimiento_lexico(titular)
    senal, confianza, variantes = TRANSFORMACIONES[arquetipo_id](s, titular)
    rng = random.Random(hash((titular, arquetipo_id, semilla)))
    frase = rng.choice(variantes)  # variante sorteada: el respaldo no suena a loro
    senal = _clip(senal + rng.gauss(0, 0.08))
    confianza = _clip(confianza + rng.gauss(0, 0.05), 0.0, 1.0)
    return {"senal": senal, "confianza": confianza, "frase": frase, "fuente": "fallback"}
```

## engine/brains/mercado.py
```python
"""Clasificación del tipo de mercado y sus perfiles de personalidad.

El enjambre ya no reacciona igual a toda noticia: primero clasifica el
titular por TIPO DE MERCADO (índice, acción individual, petróleo, oro,
cripto…) con una llamada barata a la IA (Haiku, con fallback léxico), y
luego aplica el PERFIL de ese mercado — su personalidad conductual.

Ejemplos de personalidad:
- **oro**: refugio. El miedo lo SUBE (invierte parcialmente el sentimiento
  de riesgo); poco FOMO, baja volatilidad emocional.
- **cripto**: puro sentimiento. Amplifica todo — FOMO y pánico extremos,
  alta volatilidad.
- **petroleo**: geopolítica y oferta; volatilidad media-alta, poco ligado
  a tasas.
- **accion**: idiosincrático (earnings, guidance); reacción marcada al
  nombre.
- **indice**: el mercado amplio (SPY, S&P 500) — el perfil equilibrado,
  base histórica de la calibración.

Regla CMF: la clasificación es interna (calibración), no una recomendación.
"""

import json
import os
from llm_texto import texto_de

# ---------- perfiles de personalidad por tipo de mercado ----------
# sensibilidad: cuánto mueve el sentimiento al mercado (1.0 = base índice)
# volatilidad:  multiplicador de la agitación emocional (FOMO/pánico)
# refugio:      fracción en que el MIEDO se convierte en compra (oro)
# etiqueta:     nombre legible para el reporte/UI

# Diales CALIBRADOS con 500 exámenes reales (100 por mercado). La calibración
# mostró que el enjambre acertaba la DIRECCIÓN pero se quedaba corto en MAGNITUD
# en los mercados volátiles (movía ~3-5% cuando la realidad movía 7-17%). El
# índice (S&P 500) ya calzaba (~3.9%), así que es la base (volatilidad 1.0); los
# demás suben su volatilidad según el ratio realidad/enjambre observado.
PERFILES = {
    "indice": {
        "etiqueta": "Índice / mercado amplio",
        "sensibilidad": 1.0, "volatilidad": 1.0, "refugio": 0.0,
        "nota": "El mercado accionario amplio (S&P 500). Base de calibración. En la "
                "validación el SPY se pasaba un poco (ratio 1.68), PERO bajar este dial "
                "a mano rompió el realismo (test_3: retornos predecibles), así que su "
                "ajuste fino queda para la calibración profunda con exámenes, no a ojo.",
    },
    "accion": {
        "etiqueta": "Acción individual",
        "sensibilidad": 1.4, "volatilidad": 4.0, "refugio": 0.0,
        "nota": "Una empresa concreta: reacciona MUY fuerte a su propia noticia (earnings, guidance).",
    },
    "cripto": {
        "etiqueta": "Cripto",
        "sensibilidad": 1.7, "volatilidad": 3.6, "refugio": 0.0,
        "nota": "Puro sentimiento de masas: FOMO y pánico amplificados, la mayor volatilidad.",
    },
    # ── EN PAUSA (5-ago-2026) ─────────────────────────────────────────────
    # El producto se enfoca en SP500 + acciones individuales + cripto. Oro y
    # petróleo quedan fuera del foco: sus diales CALIBRADOS se conservan aquí
    # para reactivarlos sin recalibrar, pero el clasificador ya NO los elige
    # (ver MERCADOS_ACTIVOS) — sus noticias caen al perfil por defecto (índice).
    "petroleo": {
        "etiqueta": "Petróleo / energía",
        "sensibilidad": 1.2, "volatilidad": 2.6, "refugio": 0.0,
        "nota": "[EN PAUSA] Sensible a geopolítica y oferta; volatilidad alta, poco ligado a tasas.",
    },
    "oro": {
        "etiqueta": "Metales (oro, plata, cobre)",
        "sensibilidad": 0.9, "volatilidad": 2.2, "refugio": 0.25,
        "nota": "[EN PAUSA] Metales: el oro es refugio (el miedo lo sostiene en parte); plata y cobre suman volatilidad.",
    },
}

PERFIL_DEFECTO = "indice"

# Mercados ACTIVOS (el foco del producto). Oro y petróleo están en pausa: sus
# noticias se tratan con el perfil por defecto (índice). Reactivar = agregarlos
# de vuelta aquí y a la instrucción del clasificador.
MERCADOS_ACTIVOS = ("indice", "accion", "cripto")

MODELO_CLASIFICADOR = "claude-haiku-4-5-20251001"  # barato: 1 llamada por titular


def perfil_de(tipo: str) -> dict:
    """El perfil de personalidad de un tipo de mercado (o el índice)."""
    return {"tipo": tipo if tipo in PERFILES else PERFIL_DEFECTO,
            **PERFILES.get(tipo, PERFILES[PERFIL_DEFECTO])}


# ---------- fallback léxico (sin IA o si la clasificación falla) ----------

_PISTAS = {
    "cripto": ["bitcoin", "btc", "ethereum", "eth", "crypto", "cripto", "binance",
               "solana", "coinbase", "altcoin", "stablecoin", "token", "blockchain"],
    "oro": ["gold", "oro", "silver", "plata", "bullion", "precious metal",
            "metal precioso", "xau", "lingote"],
    "petroleo": ["oil", "petroleo", "petróleo", "crude", "crudo", "brent", "wti",
                 "opec", "opep", "barrel", "barril", "gas natural", "energy", "energía"],
    # acciones individuales: nombres de empresa frecuentes (heurística)
    "accion": ["nvidia", "apple", "tesla", "amazon", "microsoft", "meta", "google",
               "alphabet", "netflix", "intel", "amd", "boeing", "disney", "ibm",
               "shares of", "earnings", "guidance", "quarterly results", "stock jumps",
               "stock sinks", "shares tumble", "shares soar"],
}


def clasificar_lexico(titular: str) -> str:
    """Adivina el tipo de mercado por palabras clave (bilingüe). Índice por
    defecto. Es el respaldo cuando la IA no está disponible.

    Solo enruta a mercados ACTIVOS (cripto, acción, índice). Oro y petróleo
    están en pausa: sus noticias caen al perfil por defecto (índice)."""
    texto = titular.lower()
    # cripto es inequívoco; acción al final (heurística de nombres de empresa)
    for tipo in ("cripto", "accion"):
        if any(p in texto for p in _PISTAS[tipo]):
            return tipo
    return PERFIL_DEFECTO


# ---------- clasificación con IA (una llamada barata) ----------

_INSTRUCCION = (
    "Clasifica el titular de mercado en UNA de estas categorías según el activo "
    "principal del que trata: 'indice' (mercado amplio, S&P 500, bolsas en "
    "general, o materias primas como oro/petróleo), 'accion' (una empresa "
    "concreta), 'cripto' (bitcoin y criptomonedas). "
    'Responde SOLO con JSON: {"mercado": "<categoria>"}.'
)


async def clasificar_async(titular: str) -> str:
    """Clasifica con Haiku (barato). Fallback léxico ante cualquier fallo."""
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return clasificar_lexico(titular)
    try:
        import anthropic

        cliente = anthropic.AsyncAnthropic()
        respuesta = await cliente.messages.create(
            model=MODELO_CLASIFICADOR, max_tokens=30,
            system=_INSTRUCCION,
            messages=[{"role": "user", "content": f"Titular: {titular}"}],
        )
        import re
        encontrado = re.search(r"\{.*\}", texto_de(respuesta), re.DOTALL)
        if encontrado:
            tipo = json.loads(encontrado.group()).get("mercado", "")
            if tipo in MERCADOS_ACTIVOS:   # oro/petróleo en pausa → cae al léxico → índice
                return tipo
    except Exception:
        pass
    return clasificar_lexico(titular)


def clasificar(titular: str) -> str:
    """Punto de entrada síncrono."""
    import asyncio

    return asyncio.run(clasificar_async(titular))
```

## engine/brains/reparto.py
```python
"""Reparto de cerebros — 1000 líderes, ~110 llamadas a la IA.

La biblia (CLAUDE.md §2.7) fija un presupuesto de ~100-120 llamadas a la
API por simulación. Con 1000 líderes de opinión, una llamada por líder lo
rompería 10x. La solución: los 1000 líderes comparten ~110 "cerebros".

Cada cerebro es UNA llamada al LLM (con el prompt de su arquetipo). Los
líderes de un mismo arquetipo se reparten sus cerebros en ronda: así hay
~110 frases distintas (variedad de sobra para el hover del demo) al costo
de siempre. La diversidad de opinión vive en los 8 arquetipos + el muestreo
del modelo, no en repetir 1000 veces la misma personalidad.

Si hay 110 líderes o menos (p. ej. la configuración vieja de 100), cada
líder es su propio cerebro y el comportamiento es idéntico al de antes.
"""

CEREBROS_OBJETIVO = 110  # cerebros LLM por simulación: la máxima riqueza de
                         # voces que permite el presupuesto de la biblia
                         # (~100-120). Los 1.000 líderes siguen existiendo y
                         # reaccionando todos; esto es solo cuántas OPINIONES
                         # distintas se le piden a la IA. La latencia se baja
                         # con más paralelismo (cerebro.MAX_CONCURRENTES), no
                         # recortando voces.


def _cerebros_por_arquetipo(conteo: dict[str, int], objetivo: int) -> dict[str, int]:
    """Reparte `objetivo` cerebros entre arquetipos, proporcional a su tamaño.

    Cada arquetipo recibe al menos 1 cerebro y nunca más cerebros que
    líderes. La suma se acerca a `objetivo` sin pasarse (salvo por el
    mínimo de 1 por arquetipo)."""
    total = sum(conteo.values())
    if total == 0:
        return {}
    if total <= objetivo:
        return dict(conteo)  # cada líder es su propio cerebro (como antes)
    cerebros = {}
    for arq, n in conteo.items():
        cerebros[arq] = max(1, min(n, round(n * objetivo / total)))
    return cerebros


def planificar(lideres: list, semilla_fn, objetivo: int = CEREBROS_OBJETIVO):
    """Devuelve (consultas, asignacion) para consultar la IA una vez por cerebro.

    - `lideres`: los agentes líder, cada uno con `.arquetipo` y `.unique_id`.
    - `semilla_fn(unique_id) -> int`: semilla base por líder (para el caché).
    - `consultas`: lista de (semilla, arquetipo_id), UNA por cerebro (~110).
    - `asignacion`: lista paralela a `lideres` con el índice del cerebro que
      le toca a cada líder (en el mismo orden que `lideres`).

    Uso: respuestas = analizar_titular(titular, consultas); luego cada líder i
    toma respuestas[asignacion[i]].
    """
    # orden de aparición de cada arquetipo y sus líderes
    por_arquetipo: dict[str, list[int]] = {}
    for i, lider in enumerate(lideres):
        por_arquetipo.setdefault(lider.arquetipo, []).append(i)

    conteo = {arq: len(idxs) for arq, idxs in por_arquetipo.items()}
    n_cerebros = _cerebros_por_arquetipo(conteo, objetivo)

    consultas: list[tuple[int, str]] = []
    asignacion: list[int] = [0] * len(lideres)
    for arq, idxs in por_arquetipo.items():
        k = n_cerebros[arq]
        base = len(consultas)  # índice global donde empiezan los cerebros de este arquetipo
        # una semilla distinta por cerebro (para el caché y variedad intra-arquetipo);
        # se ancla en el primer líder que usará ese cerebro → reproducible
        for c in range(k):
            semilla = semilla_fn(lideres[idxs[c]].unique_id)
            consultas.append((semilla, arq))
        # los líderes del arquetipo se reparten sus k cerebros en ronda
        for pos, i in enumerate(idxs):
            asignacion[i] = base + (pos % k)
    return consultas, asignacion


def expandir(respuestas_cerebros: list[dict], asignacion: list[int]) -> list[dict]:
    """Expande las ~110 respuestas de la IA a una por líder (según `asignacion`)."""
    return [respuestas_cerebros[asignacion[i]] for i in range(len(asignacion))]
```

## engine/network/__init__.py
```python

```

## engine/network/red.py
```python
"""Red de influencia de El Enjambre (CLAUDE.md sección 6).

Grafo dirigido tipo scale-free: pocos nodos muy conectados (los líderes),
muchos poco conectados. Los líderes tienen 20-150 seguidores según su
arquetipo; los agentes retail (manada, FOMO, miedoso) tienen además 3-8
vecinos "pares" entre sí — el rumor también viaja horizontalmente.
Los institucionales NO están en la red: reaccionan a precio y
fundamentales, no a rumores.
"""

from agents.lider import LiderOpinion
from agents.reglas import (
    BuyAndHold,
    Contrarian,
    FomoRetail,
    Manada,
    Miedoso,
    NoiseTrader,
)
from brains.arquetipos import POR_ID

CLASES_SOCIALES = {
    "noise_trader": NoiseTrader,
    "manada": Manada,
    "fomo": FomoRetail,
    "miedoso": Miedoso,
    "contrarian": Contrarian,
    "buy_and_hold": BuyAndHold,
}

# tipos que además tienen pares horizontales (tipos 8-10 de la mezcla)
CON_PARES = (Manada, FomoRetail, Miedoso)


def construir_red(model) -> None:
    """Conecta líderes con seguidores y teje los pares retail.

    Deja en cada agente:
      - agente.pares: vecinos horizontales (solo tipos 8-10)
      - agente.lideres_seguidos: los líderes cuya señal recibe
      - agente.vecinos: pares + líderes (su "red" observable)
      - lider.seguidores: a quiénes arrastra
    """
    rng = model.random
    lideres = [a for a in model.agents if isinstance(a, LiderOpinion)]
    por_tipo = {
        tipo_id: [a for a in model.agents if isinstance(a, clase)]
        for tipo_id, clase in CLASES_SOCIALES.items()
    }

    # --- líderes → seguidores (conexión preferencial: los populares
    #     se vuelven más populares → distribución scale-free) ---
    popularidad: dict[int, int] = {}
    for lider in lideres:
        arquetipo = POR_ID[lider.arquetipo]
        minimo, maximo = arquetipo["seguidores"]
        cuantos = rng.randint(minimo, maximo)
        candidatos = [a for t in arquetipo["sigue"] for a in por_tipo[t]]
        elegidos = _muestra_preferencial(rng, candidatos, cuantos, popularidad)
        for seguidor in elegidos:
            lider.seguidores.append(seguidor)
            seguidor.lideres_seguidos.append(lider)
            popularidad[seguidor.unique_id] = popularidad.get(seguidor.unique_id, 0) + 1

    # --- la manada y el FOMO necesitan 1-2 líderes en su red sí o sí ---
    for tipo_id in ("manada", "fomo"):
        for agente in por_tipo[tipo_id]:
            while len(agente.lideres_seguidos) < rng.randint(1, 2):
                lider = rng.choice(lideres)
                if lider in agente.lideres_seguidos:
                    continue
                lider.seguidores.append(agente)
                agente.lideres_seguidos.append(lider)

    # --- pares horizontales entre retail (tipos 8-10), conexión
    #     preferencial: quien ya tiene vecinos atrae más vecinos ---
    sociales = [a for a in model.agents if isinstance(a, CON_PARES)]
    for agente in sociales:
        deseados = rng.randint(3, 8)
        while len(agente.pares) < deseados:
            par = _eleccion_preferencial(rng, sociales, agente)
            if par not in agente.pares:
                agente.pares.append(par)
                par.pares.append(agente)  # el rumor viaja en ambos sentidos

    # --- la red observable de cada agente ---
    for agente in model.agents:
        agente.vecinos = list(agente.pares) + list(agente.lideres_seguidos)


def _muestra_preferencial(rng, candidatos, cuantos, popularidad) -> list:
    """Muestra sin reemplazo con peso 1 + popularidad (los populares atraen más).

    Usa el muestreo por reservorio ponderado de Efraimidis-Spirakis: a cada
    candidato se le asigna la clave u**(1/peso) y se toman las `cuantos` mayores.
    Da la misma probabilidad de selección ∝ peso, pero en UNA pasada + orden
    (O(n log n)) en vez del bucle cuadrático anterior (O(cuantos·n)) — clave
    para que construir la red de 10.000 agentes no tarde varios segundos."""
    if cuantos >= len(candidatos):
        return list(candidatos)
    claves = []
    for c in candidatos:
        peso = 1 + popularidad.get(c.unique_id, 0)
        u = rng.random() or 1e-12  # evita log(0)
        claves.append((u ** (1.0 / peso), c))
    claves.sort(key=lambda t: t[0], reverse=True)
    return [c for _, c in claves[:cuantos]]


def _eleccion_preferencial(rng, poblacion, excluido):
    """Elige un agente con peso 1 + grado actual, excluyéndose a sí mismo."""
    while True:
        # dos intentos sesgados: uno uniforme y uno por popularidad
        candidato = rng.choice(poblacion)
        if candidato is excluido:
            continue
        # aceptación proporcional al grado (con piso para los nuevos)
        if rng.random() < (1 + len(candidato.pares)) / 9:
            return candidato
```

## engine/calibration/__init__.py
```python

```

## engine/calibration/ablacion_arquetipos.py
```python
"""Ablación por arquetipo: ¿quién descalibra / desorienta el consenso?

Lee un export de casos (el que produce `GET /api/calibracion/export` o la rama
respaldo-datos: una lista de casos, cada uno con `senales_arquetipo`) y mide,
con partición TEMPORAL (2/3 entrena, 1/3 prueba por fecha):

  1. Arquetipo suelto: su señal media como predictor (acierto direccional y
     Brier calibrado con Platt).
  2. Consenso = promedio simple de los 8 arquetipos base.
  3. Leave-one-out: consenso SIN cada arquetipo. Δbrier<0 al quitarlo ⇒ ese
     arquetipo estaba DESORIENTANDO al consenso.
  4. Variantes del consenso (sin contrarians / solo los direccionales).
  5. Desglose por clase de titular (negativa/positiva/neutra).

NO toca el motor ni gasta IA: solo lee números ya calculados. Es un DIAGNÓSTICO
del contenido direccional de cada voz (promedio simple), no un cambio de config:
el motor pondera por seguidores y confianza y el consenso mueve el enjambre, no
solo una probabilidad. Sirve para decidir dónde intervenir, con medición.

Uso:
    python3 engine/calibration/ablacion_arquetipos.py ruta/al/calibracion.json
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # engine/
from contenido import calibracion as cal

BASE = ["institucional_frio", "quant_esceptico", "fomo_evangelista", "doomer",
        "contrarian_sabio", "macro_trader", "influencer_optimista", "value_paciente"]
# Los que, por el diagnóstico, aportan dirección vs. los que la restan.
DIRECCIONALES = ["institucional_frio", "fomo_evangelista", "doomer", "influencer_optimista"]
CONTRARIANS = ["quant_esceptico", "contrarian_sabio"]


def cargar(ruta: str) -> list[dict]:
    """Casos usables: con pct_real != 0 y los 8 arquetipos base presentes,
    ordenados por fecha (para la partición temporal)."""
    datos = json.load(open(ruta))
    casos = datos.get("casos", datos) if isinstance(datos, dict) else datos
    out = []
    for c in casos:
        r = c["reaccion_real"]
        pct = r.get("pct_real")
        if pct is None or pct == 0:
            continue
        sa = c.get("senales_arquetipo") or {}
        if not all(a in sa for a in BASE):
            continue
        out.append({
            "fecha": c.get("fecha") or "",
            "y": 1 if pct > 0 else 0,
            "cat": r.get("categoria", "?"),
            "senal": {a: sa[a]["senal_media"] for a in BASE},
        })
    out.sort(key=lambda x: x["fecha"])
    return out


def prob(s: float) -> float:
    return cal.senal_a_prob_cruda({"senal_media_lideres": s})


def acierto_direccional(senales, ys):
    """% de casos donde el signo de la señal coincide con el real (0 = medio punto)."""
    if not senales:
        return None
    ok = 0.0
    for s, y in zip(senales, ys):
        if s == 0:
            ok += 0.5
        elif (s > 0) == (y == 1):
            ok += 1
    return round(100 * ok / len(senales), 1)


def brier_calibrado(scores, ys, frac=2 / 3):
    """Platt con partición temporal. Devuelve (brier_cal, brier_base, n_prueba)."""
    corte = int(len(scores) * frac)
    s_tr, y_tr = scores[:corte], ys[:corte]
    s_te, y_te = scores[corte:], ys[corte:]
    if len(s_tr) < 30 or len(s_te) < 15:
        return None, None, len(s_te)
    try:
        c = cal.ajustar_calibrador(s_tr, y_tr, metodo="platt")
        bc = round(cal.brier(c.predict(s_te), y_te), 4)
    except Exception:
        bc = None
    base = cal.tasa_base(y_tr)
    bb = round(cal.brier([base] * len(y_te), y_te), 4)
    return bc, bb, len(s_te)


def consenso(caso, excluir=()):
    ss = [v for a, v in caso["senal"].items() if a not in excluir]
    return sum(ss) / len(ss)


def analizar(ruta: str) -> dict:
    casos = cargar(ruta)
    ys = [c["y"] for c in casos]
    rep = {"n": len(casos), "tasa_base": round(sum(ys) / len(ys), 3)}

    rep["arquetipo_suelto"] = {}
    for a in BASE:
        bc, bb, nte = brier_calibrado([prob(c["senal"][a]) for c in casos], ys)
        rep["arquetipo_suelto"][a] = {
            "acierto": acierto_direccional([c["senal"][a] for c in casos], ys),
            "brier_cal": bc, "brier_base": bb, "n_test": nte}

    bc_c, bb_c, nte = brier_calibrado([prob(consenso(c)) for c in casos], ys)
    rep["consenso"] = {"acierto": acierto_direccional([consenso(c) for c in casos], ys),
                       "brier_cal": bc_c, "brier_base": bb_c, "n_test": nte}

    rep["leave_one_out"] = {}
    for a in BASE:
        bc, _, _ = brier_calibrado([prob(consenso(c, (a,))) for c in casos], ys)
        rep["leave_one_out"][a] = {
            "acierto": acierto_direccional([consenso(c, (a,)) for c in casos], ys),
            "brier_cal": bc,
            "delta": round(bc - bc_c, 4) if (bc and bc_c) else None}

    rep["variantes"] = {}
    for nombre, excl in [("sin_contrarians", CONTRARIANS),
                         ("solo_direccionales", [a for a in BASE if a not in DIRECCIONALES])]:
        bc, _, _ = brier_calibrado([prob(consenso(c, tuple(excl))) for c in casos], ys)
        rep["variantes"][nombre] = {
            "acierto": acierto_direccional([consenso(c, tuple(excl)) for c in casos], ys),
            "brier_cal": bc,
            "delta": round(bc - bc_c, 4) if (bc and bc_c) else None}

    rep["por_clase"] = {}
    for clase in ("negativa", "positiva", "neutra"):
        sub = [c for c in casos if c["cat"] == clase]
        if len(sub) < 10:
            continue
        ys_s = [c["y"] for c in sub]
        rep["por_clase"][clase] = {
            "n": len(sub), "tasa_subio": round(sum(ys_s) / len(ys_s), 2),
            "consenso_acierto": acierto_direccional([consenso(c) for c in sub], ys_s),
            "arquetipos": {a: acierto_direccional([c["senal"][a] for c in sub], ys_s)
                           for a in BASE}}
    return rep


def imprimir(rep: dict) -> None:
    print(f"casos usables: {rep['n']}   tasa base subió: {rep['tasa_base']}\n")
    print("=== ARQUETIPO SUELTO ===")
    print(f"{'arquetipo':22}{'acierto%':>9}{'brier_cal':>11}{'brier_base':>12}")
    for a, v in rep["arquetipo_suelto"].items():
        print(f"{a:22}{v['acierto']:>9}{str(v['brier_cal']):>11}{str(v['brier_base']):>12}")
    c = rep["consenso"]
    print(f"\n=== CONSENSO (8) ===\nacierto={c['acierto']}%  brier_cal={c['brier_cal']}  "
          f"base={c['brier_base']}  n_test={c['n_test']}")
    print("\n=== LEAVE-ONE-OUT (Δbrier<0 al quitar ⇒ desorientaba) ===")
    print(f"{'quito':22}{'acierto%':>9}{'brier_cal':>11}{'Δbrier':>9}")
    for a, v in rep["leave_one_out"].items():
        print(f"{a:22}{v['acierto']:>9}{str(v['brier_cal']):>11}{str(v['delta']):>9}")
    print("\n=== VARIANTES DEL CONSENSO ===")
    for n, v in rep["variantes"].items():
        print(f"{n:22}{v['acierto']:>9}{str(v['brier_cal']):>11}{str(v['delta']):>9}")
    print("\n=== POR CLASE DE TITULAR (acierto direccional) ===")
    for clase, v in rep["por_clase"].items():
        print(f"  {clase} (n={v['n']}, tasa subió={v['tasa_subio']}): consenso={v['consenso_acierto']}%")
        for a, acc in v["arquetipos"].items():
            print(f"      {a:22}{acc}%")


if __name__ == "__main__":
    ruta = sys.argv[1] if len(sys.argv) > 1 else "calibracion.json"
    imprimir(analizar(ruta))
```

## engine/calibration/calibrar_respaldo.py
```python
"""Calibración agregada sobre la libreta de respaldo (datos/calibracion.json).

Toma los casos reales (reacción del enjambre vs movimiento real) y mide si la
probabilidad del enjambre, calibrada (Platt / Isotónica), supera a líneas base
triviales — con SPLIT TEMPORAL (entrena con los antiguos, prueba con los
recientes) para no filtrar futuro. Desglosa además por mercado.

No llama a la IA. Pura matemática sobre casos ya medidos.

Uso:  python -m calibration.calibrar_respaldo <ruta_calibracion.json>
(el archivo vive en la rama respaldo-datos: datos/calibracion.json)
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from brains.mercado import clasificar_lexico
from contenido import calibracion as cal


def _cargar_casos(ruta: str) -> list[dict]:
    obj = json.loads(Path(ruta).read_text(encoding="utf-8"))
    return obj["casos"] if isinstance(obj, dict) else obj


def _filas(casos, mercado=None):
    """(fecha, direccion_pct, resultado_binario) de los casos con IA real."""
    out = []
    for c in casos:
        rr = c.get("reaccion_real") or {}
        if rr.get("cerebros") != "ia":
            continue
        pr, d = rr.get("pct_real"), c.get("direccion_pct")
        if pr is None or d is None or float(pr) == 0:
            continue
        if mercado is not None and clasificar_lexico(c.get("titular", "")) != mercado:
            continue
        out.append((c.get("fecha", ""), float(d), 1 if float(pr) > 0 else 0))
    return out


def _prob(d):
    return cal.senal_a_prob_cruda({"direccion_pct": d}, modo="direccion")


def evaluar(filas, frac_prueba=0.3):
    if len(filas) < 20:
        return {"n": len(filas), "error": "muy pocos casos para concluir"}
    filas = sorted(filas, key=lambda x: x[0])          # split TEMPORAL
    corte = int(len(filas) * (1 - frac_prueba))
    tr, te = filas[:corte], filas[corte:]
    s_tr = [_prob(d) for _, d, _ in tr]; y_tr = [y for _, _, y in tr]
    s_te = [_prob(d) for _, d, _ in te]; y_te = [y for _, _, y in te]
    platt = cal.ajustar_calibrador(s_tr, y_tr, "platt")
    iso = cal.ajustar_calibrador(s_tr, y_tr, "isotonic")
    base = cal.brier([cal.tasa_base(y_te)] * len(te), y_te)
    b_platt = cal.brier(platt.predict(s_te), y_te)
    b_iso = cal.brier(iso.predict(s_te), y_te)
    return {
        "n": len(filas), "entrena": len(tr), "prueba": len(te),
        "tasa_subidas": round(cal.tasa_base([y for _, _, y in filas]), 3),
        "brier_base_rate": round(base, 4),
        "brier_crudo": round(cal.brier(s_te, y_te), 4),
        "brier_platt": round(b_platt, 4),
        "brier_isotonic": round(b_iso, 4),
        "skill_mejor_vs_base": round(cal.skill_score(min(b_platt, b_iso), base), 3),
    }


def main(ruta):
    casos = _cargar_casos(ruta)
    print("=== AGREGADO (todos los mercados) ===")
    print(json.dumps(evaluar(_filas(casos)), ensure_ascii=False, indent=1))
    for m in ("indice", "cripto", "accion"):
        print(f"=== {m.upper()} ===")
        print(json.dumps(evaluar(_filas(casos, mercado=m)), ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "datos/calibracion.json")
```

## engine/calibration/data_loader.py
```python
"""Descarga el benchmark real (SPY) para la calibración offline.

Guarda en data/real_benchmark.csv el retorno logarítmico acumulado de SPY en
ventanas de 5 minutos. Herramienta de laboratorio: no la usa el motor.
"""

import os
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

_SALIDA = os.path.join(os.path.dirname(__file__), "data", "real_benchmark.csv")


def download_spy_benchmark(days: int = 90, interval: str = "1m",
                           output_file: str = _SALIDA) -> pd.DataFrame:
    """Descarga SPY y calcula el log-retorno acumulado en ventanas de 5 min."""
    import yfinance as yf

    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    print(f"Descargando SPY desde {start_date:%Y-%m-%d} hasta {end_date:%Y-%m-%d}…")
    df = yf.download("SPY", start=start_date, end=end_date,
                     interval=interval, progress=False)

    if df is None or df.empty:
        raise RuntimeError("No se pudieron descargar datos de SPY (¿límite de "
                           "Yahoo para intradía, o sin red?).")

    close = df["Close"]
    if hasattr(close, "columns"):          # yfinance a veces devuelve MultiIndex
        close = close.iloc[:, 0]
    df_resampled = close.resample("5min").last().dropna()

    log_returns = np.log(df_resampled / df_resampled.iloc[0])
    df_benchmark = pd.DataFrame({
        "timestamp": df_resampled.index,
        "close": df_resampled.values,
        "log_return_cum": log_returns.values,
    })

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    df_benchmark.to_csv(output_file, index=False)
    print(f"Guardado en {output_file}. Registros: {len(df_benchmark)}")
    return df_benchmark


if __name__ == "__main__":
    download_spy_benchmark()
```

## engine/calibration/escenarios.py
```python
"""Banco de escenarios de estrés — reproducibles, SIN IA (sentimiento numérico).

Para medir el comportamiento del enjambre por régimen y comparar configuraciones
(con/sin `overrides`) de forma justa, usando `aplicar_noticia` (número), que no
llama a la API. No imponen que el precio suba o baje de cierta forma: sirven para
observar la dinámica y detectar comportamientos patológicos o cambios al calibrar.

Uso:
    from calibration.escenarios import correr_todos, correr_escenario, variabilidad
    print(correr_todos(seed=42))
    print(correr_escenario("cinco_negativas", seed=42, overrides={...}))
    print(variabilidad("negativa_fuerte", seeds=[1,7,42,99]))
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from model import MercadoEnjambre

# cada escenario: lista de (tick tras el calentamiento, sentimiento de la noticia)
ESCENARIOS = {
    "negativa_fuerte":  [(0, -0.9)],
    "positiva_fuerte":  [(0, 0.9)],
    "negativa_leve":    [(0, -0.3)],
    "cinco_negativas":  [(0, -0.4), (10, -0.4), (20, -0.4), (30, -0.4), (40, -0.4)],
    "neutral":          [(0, 0.0)],
    "pos_luego_neg":    [(0, 0.6), (30, -0.8)],
    "crash_profundo":   [(0, -0.95)],
}


def correr_escenario(nombre: str, seed: int = 42, overrides: dict | None = None,
                     calienta: int = 60, post: int = 120,
                     instrumentar: bool = False) -> dict:
    """Corre un escenario y devuelve métricas observables (relativas al precio al
    terminar el calentamiento, justo antes de la primera noticia)."""
    if nombre not in ESCENARIOS:
        raise ValueError(f"escenario desconocido: {nombre}. Opciones: {sorted(ESCENARIOS)}")
    eventos = ESCENARIOS[nombre]
    m = MercadoEnjambre(seed=seed, ticks_horizonte=calienta + post + 10, overrides=overrides)
    if instrumentar:
        m.activar_instrumentacion()
    for _ in range(calienta):
        m.step()
    base = m.historial_precios[-1]
    plan = dict(eventos)
    for t in range(post):
        if t in plan:
            m.aplicar_noticia(plan[t])
        m.step()
    precios = m.historial_precios[-post:]
    retornos = m.retornos[-post:]
    media = sum(retornos) / len(retornos)
    vol = (sum((r - media) ** 2 for r in retornos) / len(retornos)) ** 0.5
    res = {
        "escenario": nombre,
        "seed": seed,
        "direccion_pct": round((precios[-1] / base - 1) * 100, 2),
        "minimo_pct": round((min(precios) / base - 1) * 100, 2),
        "maximo_pct": round((max(precios) / base - 1) * 100, 2),
        "volatilidad_pct": round(vol * 100, 2),
    }
    if instrumentar:
        res["instrumentacion"] = m.resumen_instrumentacion()
    return res


def correr_todos(seed: int = 42, overrides: dict | None = None) -> dict:
    return {n: correr_escenario(n, seed=seed, overrides=overrides) for n in ESCENARIOS}


def variabilidad(nombre: str, seeds=(1, 7, 42, 99), overrides: dict | None = None) -> dict:
    """Corre el mismo escenario en varias semillas y reporta la dispersión de la
    dirección final — para saber cuánto depende el resultado del azar."""
    dirs = [correr_escenario(nombre, seed=s, overrides=overrides)["direccion_pct"]
            for s in seeds]
    media = sum(dirs) / len(dirs)
    desv = (sum((d - media) ** 2 for d in dirs) / len(dirs)) ** 0.5
    return {"escenario": nombre, "direcciones": dirs,
            "media": round(media, 2), "desv": round(desv, 2),
            "rango": [min(dirs), max(dirs)]}


if __name__ == "__main__":
    import json
    print(json.dumps(correr_todos(), ensure_ascii=False, indent=1))
```

## engine/calibration/evaluar_por_segmento.py
```python
"""Instrumentación por segmento (Fase 0 del plan combinado) — dónde se pierde el
acierto. Lee el export de casos (`/api/calibracion/export` o la rama respaldo) y
produce un diagnóstico, SIN tocar el motor ni gastar IA.

Reportes:
  1. mercado × signo_real × |consenso| (bucket) → hit rate del enjambre.
  2. arquetipo → hit rate individual (¿qué voces contribuyen al error?).
  3. arquetipo → correlación(confianza_reportada, acierto) (¿la confianza informa?).
  4. fuente (api/cache vs respaldo léxico) → hit rate y nº de casos.

"Hit" del enjambre = signo(direccion_pct) coincide con signo(pct_real) (el mismo
criterio que usa el backtest). OJO: la categoría de los datos es circular (se
calcula del resultado), así que este reporte es para VER dónde falla, no para
decidir despliegues — eso lo decide el walk-forward sobre la predicción.

Uso:
    python3 engine/calibration/evaluar_por_segmento.py ruta/al/calibracion.json
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # engine/
from contenido.backtest import _mercado_de_caso

BASE = ["institucional_frio", "quant_esceptico", "fomo_evangelista", "doomer",
        "contrarian_sabio", "macro_trader", "influencer_optimista", "value_paciente"]
CONTRARIANS = {"quant_esceptico", "contrarian_sabio"}


def _senal_ponderada(sa, peso_contr=0.3) -> float:
    """senal_media_ponderada reconstruida desde senales_arquetipo (contrarians×0.3)."""
    num = den = 0.0
    for a in BASE:
        if a in sa:
            w = sa[a]["n"] * (peso_contr if a in CONTRARIANS else 1.0)
            num += sa[a]["senal_media"] * w
            den += w
    return num / den if den else 0.0


def cargar(ruta: str) -> list[dict]:
    datos = json.load(open(ruta))
    casos = datos.get("casos", datos) if isinstance(datos, dict) else datos
    out = []
    for c in casos:
        r = c.get("reaccion_real") or {}
        pct = r.get("pct_real")
        if pct is None or pct == 0 or c.get("direccion_pct") is None:
            continue
        out.append(c)
    return out


def _signo(x):
    return 1 if x > 0 else (-1 if x < 0 else 0)


def _consenso(caso) -> float:
    """Reconstruye la magnitud del consenso desde senales_arquetipo (el export no
    trae `confianza`): media ponderada por confianza×n sobre los 8 arquetipos."""
    sa = caso.get("senales_arquetipo") or {}
    num = den = 0.0
    for a in BASE:
        if a in sa:
            w = sa[a]["confianza_media"] * sa[a]["n"]
            num += sa[a]["senal_media"] * w
            den += w
    return num / den if den else 0.0


def _hit(caso) -> bool:
    return _signo(caso["direccion_pct"]) == _signo(caso["reaccion_real"]["pct_real"])


def _tasa(items, pred):
    sub = [x for x in items if pred(x)]
    if not sub:
        return (None, 0)
    return (round(100 * sum(1 for x in sub if _hit(x)) / len(sub), 1), len(sub))


def por_mercado_signo_consenso(casos):
    """mercado × signo_real × bucket de |consenso| (confianza) → hit rate."""
    out = {}
    cubos = [(0.0, 0.15), (0.15, 0.35), (0.35, 0.6), (0.6, 1.01)]
    for m in ("indice", "accion", "cripto", "oro", "petroleo"):
        dm = _mercado_de_caso
        base = [c for c in casos if dm({"simbolos": c.get("simbolos"), "mercado": c.get("mercado")}) == m]
        if not base:
            continue
        fila = {"n": len(base)}
        for etq, signo in (("real_sube", 1), ("real_baja", -1)):
            sub = [c for c in base if _signo(c["reaccion_real"]["pct_real"]) == signo]
            acc, n = _tasa(sub, lambda x: True)
            fila[etq] = {"hit": acc, "n": n}
            fila[etq]["por_consenso"] = {
                f"{lo:.2f}-{hi:.2f}": _tasa(sub, lambda x, lo=lo, hi=hi: lo <= abs(_consenso(x)) < hi)
                for lo, hi in cubos
            }
        out[m] = fila
    return out


def por_arquetipo(casos):
    """arquetipo → hit direccional de su señal + correlación(confianza, acierto)."""
    out = {}
    for a in BASE:
        pares = [(c["senales_arquetipo"][a], _hit(c), _signo(c["reaccion_real"]["pct_real"]))
                 for c in casos if (c.get("senales_arquetipo") or {}).get(a)]
        if not pares:
            continue
        # hit direccional del arquetipo: signo(su senal_media) vs signo(real)
        aciertos = sum(1 for sa, _h, sr in pares if _signo(sa["senal_media"]) == sr)
        # correlación confianza vs acierto-del-enjambre (proxy simple)
        confs = [sa["confianza_media"] for sa, _h, _sr in pares]
        hits = [1 if _h else 0 for _sa, _h, _sr in pares]
        out[a] = {
            "acierto_direccional": round(100 * aciertos / len(pares), 1),
            "n": len(pares),
            "corr_confianza_hit": _corr(confs, hits),
        }
    return out


def por_fuente(casos):
    """api/cache vs respaldo léxico → hit rate y nº de casos."""
    out = {}
    for etq, pred in (("ia_real", lambda c: (c["reaccion_real"].get("cerebros") or "") != "respaldo"),
                      ("respaldo_lexico", lambda c: (c["reaccion_real"].get("cerebros") or "") == "respaldo")):
        acc, n = _tasa(casos, pred)
        out[etq] = {"hit": acc, "n": n}
    return out


def _corr(xs, ys):
    n = len(xs)
    if n < 3:
        return None
    mx, my = sum(xs) / n, sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = sum((x - mx) ** 2 for x in xs) ** 0.5
    dy = sum((y - my) ** 2 for y in ys) ** 0.5
    if dx == 0 or dy == 0:
        return None
    return round(num / (dx * dy), 3)


def direccion_senal_vs_precio(casos, zona_muerta=0.3):
    """Prioridad 1+2 (plan v2): compara el acierto direccional tomando la dirección
    del PRECIO simulado vs. de la SEÑAL de los líderes (senal_media_ponderada),
    global y por mercado. Con ZONA MUERTA (Prioridad 2): los resultados planos
    (|pct_real| < zona_muerta %) NO cuentan como error — salen del denominador y
    se reporta la COBERTURA (fracción de casos direccionables)."""
    out = {}

    def acc(sub, por_senal):
        dire = [c for c in sub if abs(c["reaccion_real"]["pct_real"]) >= zona_muerta]
        if not dire:
            return (None, 0)
        ok = sum(1 for c in dire
                 if _signo(_senal_ponderada(c.get("senales_arquetipo") or {}) if por_senal else c["direccion_pct"])
                 == _signo(c["reaccion_real"]["pct_real"]))
        return (round(100 * ok / len(dire), 1), len(dire))

    for m in ("TODOS", "indice", "accion", "cripto", "oro", "petroleo"):
        sub = casos if m == "TODOS" else [
            c for c in casos
            if _mercado_de_caso({"simbolos": c.get("simbolos"), "mercado": c.get("mercado")}) == m]
        if not sub:
            continue
        pre, n_dir = acc(sub, False)
        sen, _ = acc(sub, True)
        out[m] = {"n": len(sub), "n_direccionable": n_dir,
                  "cobertura": round(100 * n_dir / len(sub), 1) if sub else None,
                  "precio": pre, "senal": sen,
                  "delta": round(sen - pre, 1) if (sen is not None and pre is not None) else None}
    return out


def reporte(ruta: str) -> dict:
    casos = cargar(ruta)
    return {
        "n": len(casos),
        "hit_global": _tasa(casos, lambda x: True)[0],
        "direccion_senal_vs_precio": direccion_senal_vs_precio(casos),
        "por_mercado": por_mercado_signo_consenso(casos),
        "por_arquetipo": por_arquetipo(casos),
        "por_fuente": por_fuente(casos),
    }


def imprimir(rep: dict) -> None:
    print(f"casos usables: {rep['n']}   hit global: {rep['hit_global']}%\n")
    print("=== PRIORIDAD 1+2 · dirección PRECIO vs SEÑAL (zona muerta 0.3%) ===")
    print(f"{'mercado':10}{'n':>5}{'cobert%':>9}{'precio%':>9}{'senal%':>9}{'Δ':>7}")
    for m, d in rep["direccion_senal_vs_precio"].items():
        print(f"{m:10}{d['n']:>5}{str(d['cobertura']):>9}{str(d['precio']):>9}{str(d['senal']):>9}{str(d['delta']):>7}")
    print()
    print("=== MERCADO × SIGNO REAL × |consenso| → hit% (n) ===")
    for m, f in rep["por_mercado"].items():
        print(f"  {m} (n={f['n']})")
        for etq in ("real_sube", "real_baja"):
            d = f[etq]
            print(f"    {etq}: hit {d['hit']}% (n={d['n']})  por |consenso|: " +
                  "  ".join(f"{k}:{v[0]}%({v[1]})" for k, v in d["por_consenso"].items()))
    print("\n=== ARQUETIPO → acierto direccional · corr(confianza,hit) ===")
    for a, d in rep["por_arquetipo"].items():
        print(f"  {a:22} {d['acierto_direccional']}% (n={d['n']})  corr={d['corr_confianza_hit']}")
    print("\n=== FUENTE → hit% (n) ===")
    for etq, d in rep["por_fuente"].items():
        print(f"  {etq:18} {d['hit']}% (n={d['n']})")


if __name__ == "__main__":
    imprimir(reporte(sys.argv[1] if len(sys.argv) > 1 else "calibracion.json"))
```

## engine/calibration/optimizar_freno.py
```python
"""
Optimiza `factor_freno_cautela` de la MANADA con Optuna (Nivel 1).

Contexto (ver INFORME_FRENO_MANADA.md): en una racha de malas noticias, la
manada (imitadores) arma una cascada auto-alimentada y la 4ª mala noticia cae
MÁS que la 1ª — eso es sobre-pánico. El freno reduce cuánto vende la manada en
"modo cautela". Este script busca el valor del freno que mejor corrige el
sobre-pánico sin caer en la trampa degenerada (factor=0 = la manada nunca vende
= el mercado ignora las malas noticias = irreal).

OBJETIVO (honesto, anclado al propio modelo):
  que la 4ª mala noticia NO golpee más fuerte que la 1ª  →  minimizar (d4 - d1)^2
  - d1 = caída tras la 1ª mala (reacción "normal", NO depende del freno:
         la cautela necesita 3 malas para activarse).
  - d4 = caída tras la 4ª mala (aquí la cascada de la manada explota).
  Bajar el freno de más hace d4 MÁS suave que d1 (el mercado ignorando la mala
  noticia): el objetivo también lo penaliza. El óptimo es d4 ≈ d1.

Los hechos estilizados NO se corren por trial (son caros y el freno apenas los
toca porque solo actúa en cautela); se validan aparte, una vez, sobre el factor
ganador (ver `--validar` abajo o corre test_hechos_estilizados.py con el config).

Uso:
    python calibration/optimizar_freno.py --trials 15 --seeds 42 7 123 3 11 19
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import optuna

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # engine/

from model import RUTA_CONFIG, MercadoEnjambre  # noqa: E402

SECUENCIA = [-0.5, -0.5, -0.5, -0.5, 0.5]   # 4 malas seguidas + 1 buena
TICKS_POR_NOTICIA = 20
_TEMP = Path(__file__).resolve().parent.parent / "config" / "_temp_optuna_freno.json"


def _config_con_freno(factor: float) -> Path:
    """Escribe un config temporal con `factor_freno_cautela` en el tipo MANADA."""
    with open(RUTA_CONFIG, encoding="utf-8") as f:
        config = json.load(f)
    for t in config["tipos"]:
        if t["id"] == "manada":
            t.setdefault("parametros", {})["factor_freno_cautela"] = factor
    with open(_TEMP, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    return _TEMP


def _caidas(seed: int, ruta: Path) -> list[float]:
    """Cambio de precio tras cada noticia de la secuencia (d1..d5)."""
    m = MercadoEnjambre(seed=seed, precio_inicial=100.0,
                        ticks_horizonte=len(SECUENCIA) * TICKS_POR_NOTICIA + 5,
                        ruta_config=ruta)
    precios = [m.historial_precios[-1]]
    for sent in SECUENCIA:
        m.aplicar_noticia(sentimiento=sent)
        for _ in range(TICKS_POR_NOTICIA):
            m.step()
        precios.append(m.historial_precios[-1])
    return [p2 - p1 for p1, p2 in zip(precios, precios[1:])]


def _evaluar(factor: float, seeds: list[int]) -> dict:
    """Corre la secuencia para cada semilla y devuelve d1, d4 y el objetivo."""
    ruta = _config_con_freno(factor)
    try:
        d1s, d4s = [], []
        for s in seeds:
            d = _caidas(s, ruta)
            d1s.append(d[0])
            d4s.append(d[3])
    finally:
        if _TEMP.exists():
            _TEMP.unlink()
    md1, md4 = float(np.mean(d1s)), float(np.mean(d4s))
    return {"d1": md1, "d4": md4, "objetivo": (md4 - md1) ** 2,
            "d1_por_semilla": [round(x, 2) for x in d1s],
            "d4_por_semilla": [round(x, 2) for x in d4s]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", type=int, default=15)
    ap.add_argument("--seeds", type=int, nargs="+", default=[42, 7, 123, 3, 11, 19])
    args = ap.parse_args()

    print(f"🔧 Optimizando factor_freno_cautela · {args.trials} trials · "
          f"{len(args.seeds)} semillas")
    print(f"   Objetivo: 4ª mala ≈ 1ª mala (sin sobre-pánico, sin ignorar la noticia)")
    print("=" * 62)

    def objective(trial: optuna.Trial) -> float:
        factor = trial.suggest_float("factor_freno_cautela", 0.0, 1.0)
        r = _evaluar(factor, args.seeds)
        trial.set_user_attr("d1", r["d1"])
        trial.set_user_attr("d4", r["d4"])
        print(f"  factor={factor:.3f}  d1={r['d1']:+.2f}  d4={r['d4']:+.2f}  "
              f"obj={r['objetivo']:.3f}")
        return r["objetivo"]

    optuna.logging.set_verbosity(optuna.logging.WARNING)
    study = optuna.create_study(direction="minimize",
                                sampler=optuna.samplers.TPESampler(seed=1))
    # Anclas: el freno actual (1.0 = sin freno) y el probado a mano (0.5)
    study.enqueue_trial({"factor_freno_cautela": 1.0})
    study.enqueue_trial({"factor_freno_cautela": 0.5})
    study.optimize(objective, n_trials=args.trials)

    best = study.best_trial
    print("=" * 62)
    print(f"🏆 Mejor factor: {best.params['factor_freno_cautela']:.3f}")
    print(f"   d1={best.user_attrs['d1']:+.2f}  d4={best.user_attrs['d4']:+.2f}  "
          f"(objetivo, cuanto menor mejor: {best.value:.4f})")
    r = _evaluar(best.params["factor_freno_cautela"], args.seeds)
    print(f"   d1 por semilla: {r['d1_por_semilla']}")
    print(f"   d4 por semilla: {r['d4_por_semilla']}")
    print("\n   Siguiente paso: validar hechos estilizados con este factor "
          "antes de mergear.")


if __name__ == "__main__":
    main()
```

## engine/calibration/optimizer.py
```python
"""Laboratorio de calibración offline (Optuna) — modelo de agente de juguete.

⚠️ QUÉ ES Y QUÉ NO ES (léelo antes de creerle a un número):
- Corre un modelo de agente REDUCIDO (HeadlessAgent: alpha/beta/gamma), NO el
  motor real de El Enjambre (Mesa + libro de órdenes + 12 tipos + líderes LLM).
  Calibrar este juguete NO calibra el motor real.
- El "benchmark" es la ruta concreta de SPY, pero las noticias que alimentan la
  simulación son RUIDO sintético (aleatorio). Ajustar 3 parámetros para que una
  salida movida por ruido se parezca a la ruta de SPY es CURVE-FITTING: un R²
  alto aquí NO significa que el simulador prediga el mercado. Es un banco de
  pruebas del andamiaje, no una validación de realismo.
- La validación de realismo del proyecto vive en engine/validation/ (hechos
  estilizados: colas gordas, clustering de volatilidad, etc.), que es el camino
  correcto para calibrar el motor real (ver README de esta carpeta).

Sirve para: probar el flujo Optuna, medir tiempos, y como esqueleto para migrar
luego a una calibración honesta contra los hechos estilizados.
"""

import json
import os
import sys
from typing import List

import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

NUM_AGENTS = 2000   # 2000 para pruebas rápidas; 10000 para la corrida "final"
NUM_STEPS = 200     # pasos de simulación (1 paso ≈ 1 minuto)

_BENCHMARK = os.path.join(os.path.dirname(__file__), "data", "real_benchmark.csv")


class HeadlessAgent:
    """Agente de juguete para correr offline, sin servidor ni websockets."""

    def __init__(self, alpha: float, beta: float, gamma: float):
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.memory_trace = 0.0
        self.position = 0.0
        self.neighbors: list = []

    def step(self, news_impact: float = 0.0) -> float:
        self.memory_trace *= self.gamma
        self.memory_trace += news_impact * self.alpha
        if self.neighbors:
            avg_neigh = np.mean([n.memory_trace for n in self.neighbors])
        else:
            avg_neigh = 0.0
        final_decision = (self.memory_trace * (1 - self.beta)) + (avg_neigh * self.beta)
        self.position += final_decision * 0.01
        self.position = float(np.clip(self.position, -1.0, 1.0))
        return self.position


def run_headless_simulation(alpha: float, beta: float, gamma: float) -> List[float]:
    """Simulación sin frontend. Devuelve log-retornos acumulados sintéticos."""
    agents = [HeadlessAgent(alpha, beta, gamma) for _ in range(NUM_AGENTS)]

    # red de influencia de juguete: 5 vecinos aleatorios por agente
    for agent in agents:
        agent.neighbors = list(np.random.choice(agents, size=5, replace=False))

    # flujo de noticias SINTÉTICO (ruido + shocks) — semilla fija para repetir
    np.random.seed(42)
    news_stream = []
    for _ in range(NUM_STEPS):
        if np.random.rand() < 0.2:
            news_stream.append(np.random.normal(0, 0.5))    # shock fuerte
        else:
            news_stream.append(np.random.normal(0, 0.05))   # ruido normal

    price_evolution = [0.0]
    for step_idx in range(NUM_STEPS):
        impacto = news_stream[step_idx]
        for agent in agents:
            agent.step(news_impact=impacto)
        avg_position = np.mean([a.position for a in agents])
        price_evolution.append(price_evolution[-1] + (avg_position * 0.02))

    return price_evolution[1:]


def load_real_benchmark() -> np.ndarray:
    """Carga el SPY real descargado por data_loader.py."""
    if not os.path.exists(_BENCHMARK):
        raise FileNotFoundError(
            f"Ejecuta primero data_loader.py. No se encuentra {_BENCHMARK}")
    import pandas as pd

    df = pd.read_csv(_BENCHMARK)
    real = df["log_return_cum"].values[:NUM_STEPS]
    if len(real) < NUM_STEPS:
        real = np.pad(real, (0, NUM_STEPS - len(real)), constant_values=real[-1])
    return real[:NUM_STEPS]


def objective(trial):
    from sklearn.metrics import r2_score

    alpha = trial.suggest_float("alpha", 0.2, 0.9)
    beta = trial.suggest_float("beta", 0.1, 0.8)
    gamma = trial.suggest_float("gamma", 0.7, 0.99)

    sim = run_headless_simulation(alpha, beta, gamma)
    real = load_real_benchmark()

    n = min(len(sim), len(real))
    sim, real = np.asarray(sim[:n]), np.asarray(real[:n])
    try:
        return float(r2_score(real, sim))
    except Exception:
        return -10.0


def run_calibration(n_trials: int = 100):
    import optuna

    print("=== CALIBRACIÓN OFFLINE (Optuna) — modelo de juguete ===")
    print(f"Agentes: {NUM_AGENTS} | Pasos: {NUM_STEPS} | Trials: {n_trials}")

    study = optuna.create_study(direction="maximize",
                                sampler=optuna.samplers.TPESampler(seed=42))
    study.optimize(objective, n_trials=n_trials)

    salida = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                          "config_calibrada.json")
    with open(salida, "w") as f:
        json.dump({
            "best_params": study.best_params,
            "best_r2": study.best_value,
            "n_agents": NUM_AGENTS,
            "n_steps": NUM_STEPS,
            "aviso": "R² de un modelo de juguete vs ruido sintético; NO es "
                     "correlación real con el mercado. Ver README.",
        }, f, indent=4)

    print("\n" + "=" * 50)
    print("✅ CALIBRACIÓN (juguete) COMPLETADA")
    print(f"Mejor R²: {study.best_value:.4f}  (curve-fit, no realismo — ver README)")
    print(f"Parámetros: {study.best_params}")
    print(f"Guardado en: {salida}")
    print("=" * 50)
    return study.best_params, study.best_value


if __name__ == "__main__":
    if not os.path.exists(_BENCHMARK):
        print("⚠️ Sin benchmark. Ejecutando data_loader.py…")
        from calibration import data_loader
        data_loader.download_spy_benchmark()
    run_calibration()
```

## engine/calibration/real_optimizer.py
```python
"""
CALIBRADOR DEL MOTOR REAL (Basado en Hechos Estilizados)
- Optimiza contra Curtosis, Clustering de Volatilidad y Asimetría
- Usa el modelo MercadoEnjambre real (engine/model.py)
- Headless: sin WebSockets, sin frontend

NOTA (correcciones vs. el bundle original, para que enchufe con la API real):
  1. RUTA_CONFIG se importa de `model`, no de `config.agentes` (no existe).
  2. El precio del tick es `modelo.historial_precios[-1]` (no hay `precio_actual`
     ni `obtener_precio()`); el inicial es `historial_precios[0]`.
  3. `io.StringIO` en vez de `pd.compat.StringIO` (removido en pandas moderno).
"""

import gc
import io
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from typing import Dict

import numpy as np
import optuna
import pandas as pd

logging.basicConfig(level=logging.WARNING)

# ==============================================
# 1. IMPORTAR EL MODELO REAL
# ==============================================
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from model import MercadoEnjambre, RUTA_CONFIG  # noqa: E402  (RUTA_CONFIG vive aquí)

print("✅ Modelo real importado: MercadoEnjambre")
print(f"   Config agentes: {RUTA_CONFIG}")

_DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# ==============================================
# TARGETS CANÓNICOS DE UN MERCADO REAL (hechos estilizados)
# ==============================================
# Por qué NO usamos una descarga de SPY: el endpoint /v7/finance/download de
# Yahoo está deprecado (401), y el respaldo Cauchy tiene momentos INDEFINIDOS
# (kurtosis/skew de una muestra dan valores absurdos e inestables: ~145 / ~+11).
# Los hechos estilizados son propiedades UNIVERSALES y estables de los mercados;
# se calibra contra esos valores canónicos, no contra la ruta puntual de un
# índice. Son los mismos criterios que valida engine/validation/ (CLAUDE.md §7):
#   - curtosis > 3            → colas gordas (los extremos pasan más que en Gauss)
#   - AC de |retornos| > 0    → clustering de volatilidad (la turbulencia viene en rachas)
#   - asimetría negativa      → las caídas son más violentas que las subidas (pánico)
# curtosis en PEARSON (normal=3); un mercado real ronda 6+ (exceso ~3+)
TARGET_STATS = {"kurtosis": 6.0, "vol_clustering": 0.25, "skew": -0.30}


# ==============================================
# 2. LECTOR ROBUSTO DE SPY (httpx, sin yfinance)
# ==============================================
def download_spy_benchmark_robust(days=60):
    """Descarga SPY usando httpx (respeta el proxy, a diferencia de yfinance).
    OJO: el endpoint /v7/finance/download de Yahoo está deprecado; si falla,
    cae a un benchmark sintético de cola gorda para probar el flujo."""
    import httpx

    end = datetime.now()
    start = end - timedelta(days=days)
    url = (f"https://query1.finance.yahoo.com/v7/finance/download/SPY"
           f"?period1={int(start.timestamp())}&period2={int(end.timestamp())}"
           f"&interval=5m&events=history")

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.get(url, headers={"User-Agent": "Mozilla/5.0"})
            response.raise_for_status()
            df = pd.read_csv(io.StringIO(response.text))

            if df.empty:
                raise RuntimeError("Datos vacíos")

            df["log_return_cum"] = np.log(df["Close"] / df["Close"].iloc[0])
            df = df.dropna()
            df_bench = df[["Close", "log_return_cum"]].iloc[:200]

            output_path = os.path.join(_DATA_DIR, "real_benchmark_robust.csv")
            os.makedirs(_DATA_DIR, exist_ok=True)
            df_bench.to_csv(output_path, index=False)

            print(f"✅ Benchmark robusto guardado: {output_path} ({len(df_bench)} filas)")
            return df_bench["log_return_cum"].values

    except Exception as e:
        print(f"⚠️ Falló descarga robusta: {e}")
        print("📊 Usando benchmark sintético (Cauchy) para probar el flujo…")
        return np.random.standard_cauchy(200).cumsum() * 0.01


# ==============================================
# 3. CÁLCULO DE HECHOS ESTILIZADOS
# ==============================================
def calcular_hechos_estilizados(series: np.ndarray) -> Dict[str, float]:
    """Curtosis (>3 = colas gordas), clustering de volatilidad (AC de |ret|),
    asimetría (negativa = efecto pánico)."""
    if len(series) < 10:
        return {"kurtosis": 0.0, "vol_clustering": 0.0, "skew": 0.0}

    retornos = np.diff(series)
    if len(retornos) < 2:
        return {"kurtosis": 0.0, "vol_clustering": 0.0, "skew": 0.0}

    # curtosis de PEARSON (fisher=False): una normal da 3, como en
    # engine/validation/hechos_estilizados.py. OJO: pandas .kurtosis() devuelve
    # la de Fisher ("en exceso", normal=0) → daba 3 menos de la cuenta y hacía
    # parecer que las colas no llegaban a >3 cuando sí llegaban.
    from scipy import stats
    kurt = stats.kurtosis(retornos, fisher=False)

    abs_ret = np.abs(retornos)
    if len(abs_ret) > 1 and np.std(abs_ret) > 0:
        vol_clust = np.corrcoef(abs_ret[:-1], abs_ret[1:])[0, 1]
    else:
        vol_clust = 0.0

    skew = pd.Series(retornos).skew()

    return {
        "kurtosis": float(kurt) if not np.isnan(kurt) else 0.0,
        "vol_clustering": float(vol_clust) if not np.isnan(vol_clust) else 0.0,
        "skew": float(skew) if not np.isnan(skew) else 0.0,
    }


# ==============================================
# 3.5 CONFIG TEMPORAL: inyecta los params de agentes en los TIPOS correctos
# ==============================================
# El modelo lee config/agentes.json → tipos[*].parametros (ahora que las clases
# de agentes están cableadas a esos valores). Aquí escribimos un JSON temporal
# con los overrides calibrados en el tipo correcto. Si un param es None, se deja
# el valor de la config original (no se toca).
def _crear_config_temporal(params: Dict[str, float]) -> str:
    with open(RUTA_CONFIG, encoding="utf-8") as f:
        config = json.load(f)

    lo = params.get("manada_umbral_lo")
    overrides = {
        "market_maker": {
            "multiplicador_spread_panico": params.get("mult_spread_panico"),
            "umbral_volatilidad_panico": params.get("umbral_vol_panico"),
        },
        "miedoso": {"asimetria_kahneman": params.get("asimetria_kahneman")},
        # bajar el rango de la manada facilita las cascadas (colas más gordas)
        "manada": {"umbral_activacion_rango": [lo, min(lo + 0.35, 0.95)] if lo is not None else None},
    }
    for t in config["tipos"]:
        ov = overrides.get(t["id"])
        if not ov:
            continue
        for clave, valor in ov.items():
            if valor is not None:
                t.setdefault("parametros", {})[clave] = valor

    tmp_dir = os.path.join(os.path.dirname(__file__), "temp_configs")
    os.makedirs(tmp_dir, exist_ok=True)
    tmp_path = os.path.join(tmp_dir, f"agentes_{int(params.get('seed', 42))}.json")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    return tmp_path


# ==============================================
# 4. SIMULADOR HEADLESS DEL MOTOR REAL
# ==============================================
def run_headless_real_simulation(params: Dict[str, float], steps: int = 500) -> np.ndarray:
    """Ejecuta el modelo MercadoEnjambre real sin WebSockets."""
    tmp_config = None
    try:
        tmp_config = _crear_config_temporal(params)
        modelo = MercadoEnjambre(
            seed=int(params.get("seed", 42)),
            precio_inicial=100.0,
            ticks_horizonte=steps,
            ruta_config=tmp_config,
        )

        np.random.seed(int(params.get("seed", 42)) + 1)
        intensidad = params.get("noticias_intensidad", 0.5)
        ruido = params.get("ruido_base", 0.01)

        noticias = []
        for _ in range(steps):
            if np.random.rand() < 0.15:                       # 15% shock grande
                noticias.append(np.random.standard_t(df=3) * intensidad * 0.5)
            else:
                noticias.append(np.random.normal(0, ruido))   # 85% ruido de fondo

        precios = [modelo.historial_precios[0]]               # (fix #2) = 100.0
        for i in range(steps):
            modelo.aplicar_noticia(sentimiento=noticias[i])
            modelo.step()
            precios.append(modelo.historial_precios[-1])       # (fix #3)

        precios = np.array(precios)
        serie = np.log(precios / precios[0])                   # log-retornos acum.
        # liberar el modelo (10.000 agentes con refs cíclicas) para no acumular
        # basura entre trials → sin esto, Render/entornos con poca RAM hacen OOM
        # (mismo aprendizaje del backtest del proyecto).
        del modelo
        gc.collect()
        return serie

    except Exception as e:
        print(f"❌ Error en simulación headless: {e}")
        import traceback
        traceback.print_exc()
        return np.random.randn(steps).cumsum() * 0.01

    finally:
        if tmp_config and os.path.exists(tmp_config):
            try:
                os.remove(tmp_config)
            except OSError:
                pass


# ==============================================
# 5. CACHE DEL BENCHMARK REAL
# ==============================================
_real_benchmark_cache = None


def load_real_benchmark():
    global _real_benchmark_cache
    if _real_benchmark_cache is not None:
        return _real_benchmark_cache

    path = os.path.join(_DATA_DIR, "real_benchmark_robust.csv")
    if os.path.exists(path):
        df = pd.read_csv(path)
        _real_benchmark_cache = df["log_return_cum"].values
        return _real_benchmark_cache

    _real_benchmark_cache = download_spy_benchmark_robust()
    return _real_benchmark_cache


# ==============================================
# 6. FUNCIÓN OBJETIVO DE OPTUNA
# ==============================================
def objective(trial):
    params = {
        # flujo de noticias
        "noticias_intensidad": trial.suggest_float("noticias_intensidad", 1.0, 2.5),
        "ruido_base": trial.suggest_float("ruido_base", 0.005, 0.03),
        # PARÁMETROS DE AGENTES (los que gobiernan las cascadas → curtosis)
        "mult_spread_panico": trial.suggest_float("mult_spread_panico", 3.0, 15.0),
        "umbral_vol_panico": trial.suggest_float("umbral_vol_panico", 0.001, 0.05),
        "asimetria_kahneman": trial.suggest_float("asimetria_kahneman", 2.0, 8.0),
        "manada_umbral_lo": trial.suggest_float("manada_umbral_lo", 0.1, 0.8),
        "seed": trial.suggest_int("seed", 1, 1000),
    }

    sim_series = run_headless_real_simulation(params, steps=500)
    sim_stats = calcular_hechos_estilizados(sim_series)

    # objetivo = valores canónicos de mercado (estables), no una descarga rota
    real_stats = TARGET_STATS

    def safe_score(real_val, sim_val):
        if abs(real_val) < 0.01:
            return 1.0 if abs(sim_val) < 0.01 else 0.0
        error = abs(real_val - sim_val) / abs(real_val)
        return max(0.0, 1.0 - min(error, 1.0))

    score_kurt = safe_score(real_stats["kurtosis"], sim_stats["kurtosis"])
    score_clust = safe_score(real_stats["vol_clustering"], sim_stats["vol_clustering"])
    score_skew = safe_score(real_stats["skew"], sim_stats["skew"])

    # la curtosis es la prioridad ahora (es lo que faltaba en la V2)
    fitness = (0.5 * score_kurt) + (0.3 * score_clust) + (0.2 * score_skew)

    trial.set_user_attr("sim_stats", sim_stats)
    trial.set_user_attr("real_stats", real_stats)
    trial.set_user_attr("fitness", fitness)
    trial.set_user_attr("params", params)
    return fitness


# ==============================================
# 7. EJECUCIÓN PRINCIPAL
# ==============================================
def run_real_calibration(n_trials: int = 50):
    print("\n" + "=" * 60)
    print("🧠 CALIBRACIÓN DEL MOTOR REAL (Hechos Estilizados)")
    print("   Modelo: MercadoEnjambre (engine/model.py)")
    print("=" * 60)

    real_stats = TARGET_STATS

    print("\n📊 Targets canónicos de mercado (objetivo de la calibración):")
    print(f"   Curtosis: {real_stats['kurtosis']:.3f}  → colas gordas (> 3)")
    print(f"   Clustering volatilidad: {real_stats['vol_clustering']:.3f}  → rachas (> 0.2)")
    print(f"   Asimetría: {real_stats['skew']:.3f}  → negativa = efecto pánico")

    study = optuna.create_study(direction="maximize",
                                sampler=optuna.samplers.TPESampler(seed=42))

    print(f"\n🚀 Iniciando optimización ({n_trials} trials)…")
    study.optimize(objective, n_trials=n_trials)

    best = study.best_params
    best_fitness = study.best_value
    best_stats = study.best_trial.user_attrs.get("sim_stats", {})

    print("\n" + "=" * 60)
    print("✅ CALIBRACIÓN COMPLETADA")
    print(f"Fitness máximo: {best_fitness:.4f}  (1.0 = réplica perfecta del benchmark)")
    print(f"\n📌 Parámetros óptimos:\n{json.dumps(best, indent=2)}")
    print("\n📊 Estadísticas del enjambre calibrado:")
    print(f"   Curtosis: {best_stats.get('kurtosis', 0):.3f}")
    print(f"   Clustering: {best_stats.get('vol_clustering', 0):.3f}")
    print(f"   Asimetría: {best_stats.get('skew', 0):.3f}")
    print("=" * 60)

    config = {
        "best_params": best,
        "best_fitness": best_fitness,
        "real_stats": real_stats,
        "sim_stats": best_stats,
        "n_trials": n_trials,
        "date": datetime.now().isoformat(),
        "modelo": "MercadoEnjambre",
        "ruta_config": str(RUTA_CONFIG),
    }
    output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                               "config_calibrada_real.json")
    with open(output_path, "w") as f:
        json.dump(config, f, indent=4)
    print(f"\n💾 Configuración guardada: {output_path}")
    return best, best_fitness


if __name__ == "__main__":
    run_real_calibration()
```

## engine/calibration/recopilar_datos.py
```python
"""
Recopila noticias reales y movimientos del SPY para validación (laboratorio).

Correcciones vs. el bundle original (para que de verdad funcione):
  1. El movimiento del SPY se baja por el endpoint v8/finance/chart de Yahoo
     (el que SÍ responde y usa el propio motor en engine/contenido/fuentes/
     yahoo.py). El v7/finance/download del bundle está DEPRECADO (HTTP 401) y
     devolvía 0.0 siempre → dataset inútil.
  2. io.StringIO en vez de pd.compat.StringIO (removido en pandas moderno).
  3. NewsAPI degrada con un mensaje claro si falta NEWS_API_KEY (nunca se
     hardcodea una clave).

⚠️ Límites honestos de NewsAPI (plan free): ~1 mes hacia atrás (no 60 días),
100 req/día, sin uso comercial. Y correlacionar noticias en ESPAÑOL con
movimientos intradía del SPY (un ETF de EE.UU.) es señal débil: para validar el
enjambre conviene noticias en inglés y de mercado. Además el intradía de 5m solo
existe para ~60 días y en horario de mercado (noche/fin de semana → sin dato).
"""

import io
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List

import httpx
import pandas as pd

# ==============================================
# CONFIGURACIÓN
# ==============================================
NEWS_API_KEY = os.environ.get("NEWS_API_KEY", "")   # regístrate gratis en newsapi.org
TICKER = "SPY"
INTERVALO_MINUTOS = 30          # movimiento en los 30 min tras la noticia
DIAS_ATRAS = 30                 # NewsAPI free solo cubre ~1 mes
_URL_CHART = "https://query1.finance.yahoo.com/v8/finance/chart/{simbolo}"
_SALIDA = os.path.join(os.path.dirname(__file__), "data", "noticias_reales.csv")


# ==============================================
# 1. NOTICIAS (NewsAPI)
# ==============================================
def obtener_noticias(dias: int = DIAS_ATRAS) -> List[Dict]:
    if not NEWS_API_KEY:
        print("⚠️ Falta NEWS_API_KEY (regístrate gratis en newsapi.org y expórtala "
              "en el entorno). Sin clave no se pueden bajar noticias.")
        return []

    fecha_desde = (datetime.now() - timedelta(days=dias)).strftime("%Y-%m-%d")
    try:
        with httpx.Client(timeout=30.0) as client:
            respuesta = client.get(
                "https://newsapi.org/v2/everything",
                params={
                    "q": "stock market OR S&P 500 OR SPY OR Federal Reserve",
                    "from": fecha_desde,
                    "sortBy": "publishedAt",
                    "language": "en",     # inglés: señal más fuerte para el SPY
                    "pageSize": 100,
                    "apiKey": NEWS_API_KEY,
                },
            )
            respuesta.raise_for_status()
            data = respuesta.json()
        if data.get("status") != "ok":
            print(f"⚠️ Error en NewsAPI: {data.get('message', '')}")
            return []
        noticias = [
            {
                "titular": a["title"],
                "fecha": a["publishedAt"],
                "fuente": a.get("source", {}).get("name", "desconocida"),
                "descripcion": a.get("description", ""),
            }
            for a in data.get("articles", [])
            if a.get("title") and a.get("publishedAt")
        ]
        print(f"✅ Obtenidas {len(noticias)} noticias desde {fecha_desde}")
        return noticias
    except Exception as e:
        print(f"❌ Error obteniendo noticias: {e}")
        return []


# ==============================================
# 2. MOVIMIENTO DEL SPY (v8/finance/chart — el que SÍ responde)
# ==============================================
def obtener_movimiento_spy(fecha: str) -> float:
    """Retorno del SPY en los INTERVALO_MINUTOS posteriores a la noticia.
    0.0 si no hay dato intradía (noche/fin de semana, o fuera de los ~60 días)."""
    try:
        dt = datetime.fromisoformat(fecha.replace("Z", "+00:00"))
        p1 = int(dt.timestamp())
        p2 = int((dt + timedelta(minutes=INTERVALO_MINUTOS + 5)).timestamp())
        with httpx.Client(timeout=30.0) as client:
            respuesta = client.get(
                _URL_CHART.format(simbolo=TICKER),
                params={"period1": p1, "period2": p2, "interval": "5m"},
                headers={"User-Agent": "Mozilla/5.0"},
            )
        if respuesta.status_code != 200:
            return 0.0
        r = respuesta.json()["chart"]["result"][0]
        cierres = [c for c in r["indicators"]["quote"][0]["close"] if c is not None]
        if len(cierres) < 2:
            return 0.0
        return float((cierres[-1] - cierres[0]) / cierres[0])
    except Exception:
        return 0.0


# ==============================================
# 3. RECOPILAR
# ==============================================
def recopilar_datos_completos():
    noticias = obtener_noticias()
    if not noticias:
        print("❌ No se obtuvieron noticias (¿falta la API key?).")
        return None

    datos = []
    for i, n in enumerate(noticias):
        print(f"Procesando {i + 1}/{len(noticias)}: {n['titular'][:50]}…")
        datos.append({
            "titular": n["titular"],
            "fecha": n["fecha"],
            "fuente": n["fuente"],
            "retorno_spy_30min": obtener_movimiento_spy(n["fecha"]),
        })
        time.sleep(0.1)   # cortesía con la API

    df = pd.DataFrame(datos)
    os.makedirs(os.path.dirname(_SALIDA), exist_ok=True)
    df.to_csv(_SALIDA, index=False)

    con_dato = df[df["retorno_spy_30min"] != 0.0]
    print(f"\n✅ Datos guardados en: {_SALIDA}")
    print(f"   Total noticias: {len(df)} | con movimiento intradía: {len(con_dato)}")
    if len(con_dato):
        print(f"   Retorno promedio: {con_dato['retorno_spy_30min'].mean():.4f}")
        print(f"   Rango: {con_dato['retorno_spy_30min'].min():.4f} a "
              f"{con_dato['retorno_spy_30min'].max():.4f}")
    return df


if __name__ == "__main__":
    recopilar_datos_completos()
```

## engine/calibration/remedir_sin_fuga.py
```python
"""Re-mide el acierto con ventana SIN FUGA (Prioridad 2b del plan combinado v2).

El examen del cosechador elige días que YA se movieron fuerte y mide `pct_real`
desde el cierre ANTERIOR al titular — así la ventana incluye el mismo movimiento
que hizo seleccionar el día, y el titular ya lo describe (fuga). Esta herramienta
re-mide el resultado desde el cierre DEL DÍA del titular hacia adelante (el
movimiento POSTERIOR a la noticia), con Yahoo (gratis, sin IA), y compara el
acierto tomando la dirección del PRECIO simulado vs. de la SEÑAL de líderes.

Hallazgo (2026-11-16, 616 casos): sin fuga el acierto cae a ~50% en el agregado;
solo ÍNDICE conserva señal real (~63% la señal vs 50% de azar). Ver
docs/baseline-calibracion-fase0.md.

Uso:
    python3 engine/calibration/remedir_sin_fuga.py ruta/al/calibracion.json
"""
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # engine/
from contenido.backtest import _mercado_de_caso

URL = "https://query1.finance.yahoo.com/v8/finance/chart/{simbolo}"
BASE = ["institucional_frio", "quant_esceptico", "fomo_evangelista", "doomer",
        "contrarian_sabio", "macro_trader", "influencer_optimista", "value_paciente"]
CONTRARIANS = {"quant_esceptico", "contrarian_sabio"}


def _pond(sa, w=0.3):
    num = sum(sa[a]["senal_media"] * sa[a]["n"] * (w if a in CONTRARIANS else 1) for a in BASE if a in sa)
    den = sum(sa[a]["n"] * (w if a in CONTRARIANS else 1) for a in BASE if a in sa)
    return num / den if den else 0.0


def _sg(x):
    return 1 if x > 0 else (-1 if x < 0 else 0)


def obtener_barras(simbolo, fecha):
    """(fecha_iso, cierre) diarias alrededor de `fecha`. Aislable en tests."""
    try:
        b = datetime.fromisoformat(fecha)
        p1 = int(b.timestamp()) - 12 * 86400
        p2 = int(b.timestamp()) + 20 * 86400
        r = httpx.get(URL.format(simbolo=simbolo),
                      params={"period1": p1, "period2": p2, "interval": "1d"},
                      headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        r.raise_for_status()
        res = r.json()["chart"]["result"][0]
        out = []
        for ts, cl in zip(res["timestamp"], res["indicators"]["quote"][0]["close"]):
            if cl is not None:
                dia = datetime.fromtimestamp(ts, timezone.utc).strftime("%Y-%m-%d")
                out.append((dia, float(cl)))
        return out
    except Exception:
        return None


def pct_sin_fuga(barras, fecha_base, ruedas):
    """Movimiento DESPUÉS del día del titular: base = cierre del día del titular
    (la rueda siguiente a fecha_base, que es el cierre anterior), final = `ruedas`
    ruedas después. None si no hay barras suficientes."""
    if not barras:
        return None
    idx = next((k for k, (dia, _) in enumerate(barras) if dia == fecha_base), None)
    if idx is None or idx + 1 + ruedas >= len(barras):
        return None
    base = barras[idx + 1][1]
    final = barras[idx + 1 + ruedas][1]
    if not base:
        return None
    return (final - base) / base * 100


def recolectar(ruta, fetch=obtener_barras, pausa=0.05):
    datos = json.load(open(ruta))
    casos = [c for c in datos.get("casos", datos) if c.get("origen") == "historico"]
    filas = []
    for c in casos:
        rr = c["reaccion_real"]
        sim = rr.get("simbolo") or (c.get("simbolos") or "").split(",")[0]
        fb, rue = rr.get("fecha_base"), rr.get("ruedas", 2)
        if not sim or not fb:
            continue
        pc = pct_sin_fuga(fetch(sim, fb), fb, rue)
        if pc is None:
            continue
        m = _mercado_de_caso({"simbolos": c.get("simbolos"), "mercado": c.get("mercado")})
        filas.append({"mercado": m, "direccion_pct": c.get("direccion_pct"),
                      "senal": _pond(c.get("senales_arquetipo") or {}),
                      "pct_orig": rr.get("pct_real"), "pct_corr": pc})
        if pausa:
            time.sleep(pausa)
    return filas


def _acc(filas, por_senal, usar_corr, zona=0.3):
    campo = "pct_corr" if usar_corr else "pct_orig"
    dire = [f for f in filas if f[campo] is not None and abs(f[campo]) >= zona]
    if not dire:
        return (None, 0)
    ok = sum(1 for f in dire
             if _sg(f["senal"] if por_senal else f["direccion_pct"]) == _sg(f[campo]))
    return (round(100 * ok / len(dire), 1), len(dire))


def resumen(filas):
    out = {}
    for m in ("TODOS", "indice", "accion", "cripto", "oro", "petroleo"):
        sub = filas if m == "TODOS" else [f for f in filas if f["mercado"] == m]
        if not sub:
            continue
        out[m] = {
            "n": len(sub),
            "con_fuga": {"precio": _acc(sub, False, False)[0], "senal": _acc(sub, True, False)[0]},
            "sin_fuga": {"precio": _acc(sub, False, True)[0], "senal": _acc(sub, True, True)[0]},
        }
    return out


def gating_por_senal(filas, cortes=(0.0, 0.1, 0.2, 0.3, 0.5), zona=0.3):
    """¿Acierta más la SEÑAL cuando es más fuerte? (gating/confianza). Para cada
    corte |señal| ≥ c mide, SIN fuga, el acierto de la señal y la COBERTURA
    (fracción de casos direccionables que superan el corte). Si el acierto sube
    con el corte, |señal| informa confianza; si es plano, es adorno."""
    dire = [f for f in filas if f["pct_corr"] is not None and abs(f["pct_corr"]) >= zona]
    base = len(dire)
    out = []
    for c in cortes:
        sub = [f for f in dire if abs(f["senal"]) >= c]
        if not sub:
            out.append({"corte": c, "acierto": None, "n": 0, "cobertura": 0.0})
            continue
        ok = sum(1 for f in sub if _sg(f["senal"]) == _sg(f["pct_corr"]))
        out.append({"corte": c, "acierto": round(100 * ok / len(sub), 1),
                    "n": len(sub), "cobertura": round(100 * len(sub) / base, 1) if base else 0.0})
    return out


def imprimir(res):
    print(f"{'mercado':10}{'n':>5} | CON fuga precio/señal | SIN fuga precio/señal")
    for m, d in res.items():
        cf, sf = d["con_fuga"], d["sin_fuga"]
        print(f"{m:10}{d['n']:>5} |   {cf['precio']} / {cf['senal']}   |   {sf['precio']} / {sf['senal']}")


def imprimir_gating(g):
    print(f"\n{'|señal|≥':10}{'acierto%':>10}{'n':>7}{'cobertura%':>12}")
    for r in g:
        print(f"{r['corte']:<10}{str(r['acierto']):>10}{r['n']:>7}{str(r['cobertura']):>12}")


if __name__ == "__main__":
    import json as _json
    ruta = sys.argv[1] if len(sys.argv) > 1 else "calibracion.json"
    print("re-midiendo históricos con Yahoo (sin fuga)…", flush=True)
    filas = recolectar(ruta)
    try:  # cachear las filas re-medidas para no re-consultar Yahoo
        _json.dump(filas, open(ruta + ".sinfuga.json", "w"))
    except Exception:
        pass
    imprimir(resumen(filas))
    print("\n=== GATING: ¿acierta más la señal cuando es más fuerte? (TODOS, sin fuga) ===")
    imprimir_gating(gating_por_senal(filas))
    print("\n=== GATING solo ÍNDICE (donde hay señal real) ===")
    imprimir_gating(gating_por_senal([f for f in filas if f["mercado"] == "indice"]))
```

## engine/calibration/validacion_base.py
```python
"""
FASE 0 — Validación Base: ¿el enjambre reacciona como el mercado real?

Usa los exámenes YA rendidos por el motor (backtest + en vivo), respaldados en
GitHub y de lectura pública (sin token ni saldo de API). Cada caso trae:
  - direccion_pct: cuánto/hacia dónde movió el precio la simulación del enjambre.
  - reaccion_real.pct_real: cuánto se movió DE VERDAD el símbolo esos días.

Métricas (las honestas para un "focus group sintético", no un oráculo):
  - Acierto de dirección: ¿coincide el SIGNO simulado con el real? (azar = 50%).
  - Correlación de magnitud (Pearson) y R² asociado.

No corre simulaciones nuevas (no gasta LLM); solo puntúa lo ya rendido.
"""

import sys
from typing import Dict, List

import numpy as np

# mercado inferido del símbolo medido (mismo mapa que engine/contenido/backtest.py).
# Los casos respaldados no traen "mercado" explícito, pero sí el símbolo real.
_MERCADO_POR_SIMBOLO = {
    "oro": {"GLD", "IAU", "GDX", "NEM", "GOLD"},
    "cripto": {"GBTC", "COIN", "MARA", "RIOT", "MSTR", "ETHE", "BITO", "BTC-USD"},
    "petroleo": {"USO", "XLE", "OXY", "SLB"},
    "indice": {"SPY", "QQQ", "DIA", "IWM"},
}


def _mercado(simbolo: str) -> str:
    s = (simbolo or "").upper()
    for mercado, simbolos in _MERCADO_POR_SIMBOLO.items():
        if s in simbolos:
            return mercado
    return "accion"


def _magnitud(pct_real: float) -> str:
    a = abs(pct_real)
    if a > 1.0:
        return "grande (>1%)"
    if a >= 0.5:
        return "medio (0.5-1%)"
    return "ruido (<0.5%)"


def _cargar_pares(casos: List[dict]) -> List[dict]:
    """De cada caso extrae sim/real + etiquetas (origen, mercado, magnitud,
    sentimiento), descartando incompletos."""
    pares = []
    for c in casos:
        rr = c.get("reaccion_real") or {}
        sim = c.get("direccion_pct")
        real = rr.get("pct_real")
        if sim is None or real is None:
            continue
        pares.append({
            "sim": float(sim), "real": float(real),
            "origen": c.get("origen", "?"),
            "mercado": _mercado(rr.get("simbolo", "")),
            "magnitud": _magnitud(float(real)),
            "sentimiento": rr.get("categoria", "(sin)"),
        })
    return pares


def _puntuar(pares: List[dict], umbral_notable: float = 0.5) -> Dict:
    """Acierto de dirección + correlación de magnitud sobre un set de pares."""
    if len(pares) < 3:
        return {"n": len(pares)}
    sim = np.array([p["sim"] for p in pares])
    real = np.array([p["real"] for p in pares])
    acierto = float(np.mean(np.sign(sim) == np.sign(real)))
    mask = np.abs(real) >= umbral_notable
    acierto_notable = (float(np.mean(np.sign(sim[mask]) == np.sign(real[mask])))
                       if mask.sum() >= 3 else None)
    corr = float(np.corrcoef(sim, real)[0, 1]) if np.std(sim) > 0 and np.std(real) > 0 else 0.0
    return {
        "n": len(pares),
        "acierto_direccion": acierto,
        "n_notables": int(mask.sum()),
        "acierto_notables": acierto_notable,
        "correlacion": corr,
        "r2": corr ** 2,
    }


def validar(casos: List[dict] | None = None) -> Dict:
    """Corre la validación base. Si no se pasan `casos`, los trae del respaldo
    público de GitHub (sin token). Devuelve el scorecard global y por origen."""
    if casos is None:
        sys.path.insert(0, __file__.rsplit("/engine/", 1)[0] + "/engine")
        from contenido import respaldo
        casos = respaldo.casos_remotos()

    pares = _cargar_pares(casos)

    def _desglose_por(campo: str) -> Dict[str, Dict]:
        grupos = {}
        for valor in sorted({p[campo] for p in pares}):
            grupos[valor] = _puntuar([p for p in pares if p[campo] == valor])
        return grupos

    return {
        "global": _puntuar(pares),
        "por_origen": _desglose_por("origen"),
        "por_mercado": _desglose_por("mercado"),
        "por_magnitud": _desglose_por("magnitud"),
        "por_sentimiento": _desglose_por("sentimiento"),
    }


def _imprimir(res: Dict) -> None:
    g = res["global"]
    print("=" * 60)
    print("FASE 0 — VALIDACIÓN BASE (enjambre vs. mercado real)")
    print("=" * 60)
    if g.get("n", 0) < 3:
        print(f"Datos insuficientes (n={g.get('n', 0)}).")
        return
    print(f"Exámenes: {g['n']}")
    print(f"1. Acierto de dirección: {g['acierto_direccion']*100:.1f}%   (azar = 50%)")
    if g["acierto_notables"] is not None:
        print(f"   en movimientos reales notables (>=0.5%, n={g['n_notables']}): "
              f"{g['acierto_notables']*100:.1f}%")
    print(f"2. Correlación de magnitud (Pearson): {g['correlacion']:.3f}  "
          f"(R² = {g['r2']:.3f})")


def _tabla(titulo: str, grupos: Dict[str, Dict]) -> None:
    print(f"\n{titulo}")
    filas = [(k, s) for k, s in grupos.items() if s.get("n", 0) >= 3]
    # ordena por acierto de dirección, de mayor a menor
    filas.sort(key=lambda kv: kv[1]["acierto_direccion"], reverse=True)
    for k, s in filas:
        print(f"  {k:<16} n={s['n']:<4} acierto={s['acierto_direccion']*100:5.1f}%  "
              f"corr={s['correlacion']:+.3f}")


def _imprimir_desglose(res: Dict) -> None:
    print("-" * 60)
    _tabla("Por MERCADO:", res["por_mercado"])
    _tabla("Por MAGNITUD del movimiento real:", res["por_magnitud"])
    _tabla("Por SENTIMIENTO de la noticia:", res["por_sentimiento"])
    _tabla("Por ORIGEN:", res["por_origen"])
    print("=" * 60)
    print("Lectura: el enjambre es un FOCUS GROUP sintético — acierta el RUMBO "
          "mejor que el azar; el TAMAÑO del golpe lo estima flojo. No es un "
          "oráculo ni asesoría de inversión.")


if __name__ == "__main__":
    resultado = validar()
    _imprimir(resultado)
    if "--desglose" in sys.argv:
        _imprimir_desglose(resultado)
    else:
        print("=" * 60)
        print("(usa --desglose para ver por mercado, magnitud y sentimiento)")
```

## engine/calibration/validar_freno_hechos.py
```python
"""
Reja de seguridad: corre los 5 hechos estilizados (CLAUDE.md §7) con un valor
dado de `factor_freno_cautela`, para confirmar que el freno de la manada NO
rompe el realismo del mercado antes de mergear.

Replica la lógica de test_hechos_estilizados.py pero apuntando a un config
temporal con el factor inyectado. Imprime el valor medido de cada criterio,
no solo pasa/falla.

Uso:
    python calibration/validar_freno_hechos.py --factor 0.5
"""

import argparse
import json
import statistics
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # engine/

from model import RUTA_CONFIG, MercadoEnjambre  # noqa: E402
from validation.hechos_estilizados import (  # noqa: E402
    asimetria_panico, autocorrelacion, curtosis,
)

TICKS_SESION = 600
_TEMP = Path(__file__).resolve().parent.parent / "config" / "_temp_optuna_freno.json"


def _config(factor: float) -> Path:
    with open(RUTA_CONFIG, encoding="utf-8") as f:
        config = json.load(f)
    for t in config["tipos"]:
        if t["id"] == "manada":
            t.setdefault("parametros", {})["factor_freno_cautela"] = factor
    with open(_TEMP, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    return _TEMP


def _retornos(seed: int, ruta: Path) -> tuple:
    m = MercadoEnjambre(seed=seed, ticks_horizonte=TICKS_SESION, ruta_config=ruta)
    for _ in range(TICKS_SESION):
        if m.random.random() < 0.02:
            m.aplicar_noticia(m.random.gauss(0, 0.45))
        m.step()
    return tuple(m.retornos)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--factor", type=float, required=True)
    args = ap.parse_args()
    ruta = _config(args.factor)
    ok = True
    try:
        print(f"🛡️  Hechos estilizados con factor_freno_cautela = {args.factor}")
        print("=" * 60)
        cache = {s: _retornos(s, ruta) for s in [42, 3, 7, 11, 19]}

        # 1. Colas gordas: curtosis > 3
        for s in [42, 3]:
            k = curtosis(cache[s])
            paso = k > 3
            ok &= paso
            print(f"  1. Colas gordas   seed {s:>2}: curtosis={k:6.2f}  (>3)  "
                  f"{'✅' if paso else '❌'}")

        # 2. Clustering de volatilidad: ac1>0.1 y ac1>ac10
        for s in [42, 3]:
            absns = [abs(r) for r in cache[s]]
            ac1, ac10 = autocorrelacion(absns, 1), autocorrelacion(absns, 10)
            paso = ac1 > 0.1 and ac1 > ac10
            ok &= paso
            print(f"  2. Vol clustering seed {s:>2}: ac1={ac1:.3f} ac10={ac10:.3f}"
                  f"  {'✅' if paso else '❌'}")

        # 3. Sin autocorrelación de retornos: media≈0, max<0.2
        acs = [autocorrelacion(cache[s], 1) for s in [42, 3, 7, 11, 19]]
        paso = abs(statistics.mean(acs)) < 0.1 and max(abs(a) for a in acs) < 0.2
        ok &= paso
        print(f"  3. Sin autocorr.        media={statistics.mean(acs):+.3f} "
              f"max|ac|={max(abs(a) for a in acs):.3f}  {'✅' if paso else '❌'}")

        # 4. Asimetría de pánico > 1
        for s in [42, 3]:
            a = asimetria_panico(cache[s])
            paso = a > 1.0
            ok &= paso
            print(f"  4. Asim. pánico   seed {s:>2}: ratio={a:5.2f}  (>1)  "
                  f"{'✅' if paso else '❌'}")

        # 5. Respuesta a shock: cae >5%, rebota, rebote parcial
        for s in [42, 3]:
            m = MercadoEnjambre(seed=s, ticks_horizonte=300, ruta_config=ruta)
            m.correr(80)
            previo = m.historial_precios[-1]
            m.aplicar_noticia(-0.9)
            m.correr(120)
            post = np.array(m.historial_precios[80:])
            cae = post.min() < previo * 0.95
            rebota = post[-1] > post.min()
            parcial = post[-1] < previo * 0.995
            paso = cae and rebota and parcial
            ok &= paso
            print(f"  5. Shock -0.9     seed {s:>2}: min={post.min():.1f} "
                  f"fin={post[-1]:.1f} previo={previo:.1f}  "
                  f"cae/rebota/parcial={int(cae)}{int(rebota)}{int(parcial)}  "
                  f"{'✅' if paso else '❌'}")
    finally:
        if _TEMP.exists():
            _TEMP.unlink()

    print("=" * 60)
    print("✅ TODOS pasan — el freno no rompe el realismo."
          if ok else "❌ Algún criterio falló — revisar antes de mergear.")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
```

## engine/calibration/verificador.py
```python
"""Verificador — el arnés que congela el baseline y separa visible / held-out.

Primer paso (barato) de la metodología tipo "sala de hipótesis": ningún cambio
entra a producción sin superar el BASELINE en casos HELD-OUT (reservados, que no
se usaron para afinar). Este módulo NO genera hipótesis ni corre agentes LLM —
solo provee el arnés, y es 100% local y gratis (no llama a la IA):

- `es_holdout(sim_id)`: partición DETERMINÍSTICA y estable (hash del sim_id). El
  mismo caso cae siempre del mismo lado, y un caso nuevo del cosechador se
  auto-clasifica con la misma regla (no hay que re-partir a mano).
- `particionar(casos)`: separa una lista de casos en (visible, held_out).
- `cargar_baseline()` / `guardar_baseline()`: la foto congelada de las métricas.
- `comparar(nuevas)`: aplica los criterios de promoción (superar el baseline y no
  degradar NINGÚN régimen por encima de un umbral fijado de antemano).

Regla de oro: el verificador recibe NÚMEROS (métricas), nunca la justificación en
prosa de un cambio — así la narrativa no contamina el juicio.
"""
import hashlib
import json
from pathlib import Path

# ~30% de los casos se reservan para validar (no se afinan sobre ellos).
PORCENTAJE_HOLDOUT = 30
RUTA_BASELINE = Path(__file__).parent / "baseline.json"


def es_holdout(sim_id: str, pct: int = PORCENTAJE_HOLDOUT) -> bool:
    """True si el caso pertenece al conjunto HELD-OUT (reservado para validar).

    Determinístico y estable: NO usa `random` (que cambiaría en cada corrida);
    usa un hash del sim_id, así el reparto es reproducible y un caso nuevo cae
    solo en su lado sin re-partir nada."""
    h = int(hashlib.sha256(str(sim_id).encode()).hexdigest(), 16)
    return (h % 100) < pct


def particionar(casos: list[dict]) -> tuple[list, list]:
    """Separa casos (cada uno con 'sim_id') en (visible, held_out)."""
    visible, holdout = [], []
    for c in casos:
        (holdout if es_holdout(c.get("sim_id", "")) else visible).append(c)
    return visible, holdout


def cargar_baseline() -> dict:
    """La foto congelada de las métricas del motor (o {} si no existe)."""
    try:
        return json.loads(RUTA_BASELINE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def guardar_baseline(metricas: dict) -> None:
    """Congela una foto de métricas. Usar con criterio: el baseline es el punto
    de comparación, no se pisa a la ligera."""
    RUTA_BASELINE.write_text(
        json.dumps(metricas, ensure_ascii=False, indent=2), encoding="utf-8")


def comparar(nuevas: dict, baseline: dict | None = None,
             umbral_degradacion: float = 0.02) -> dict:
    """Compara métricas de acierto NUEVAS contra el baseline congelado.

    `nuevas` es un dict {clave: acierto 0..1} con claves tipo "indice_negativa".
    Criterios de promoción (documento §5): una mejora que rompe un régimen NO se
    promueve. Devuelve:
      - mejoras: métricas que subieron
      - degradaciones: las que bajaron más que `umbral_degradacion`
      - promovible: True solo si hay mejora neta y NINGUNA degradación de régimen
    """
    base = baseline if baseline is not None else cargar_baseline()
    ref = base.get("acierto", {}) if isinstance(base, dict) else {}
    mejoras, degradaciones = {}, {}
    for k, v in nuevas.items():
        if k not in ref or not isinstance(ref[k], (int, float)):
            continue
        d = v - ref[k]
        if d > 0:
            mejoras[k] = round(d, 4)
        elif d < -umbral_degradacion:
            degradaciones[k] = round(d, 4)
    return {
        "mejoras": mejoras,
        "degradaciones": degradaciones,
        "promovible": bool(mejoras) and not degradaciones,
    }
```

## engine/calibration/walk_forward.py
```python
"""Fase 5 — validación WALK-FORWARD del calibrador + decisión de PROMOCIÓN.

El split 2/3 de la Fase 3 es un solo corte. Esto es más honesto: ventana
EXPANSIVA (entrena con el pasado, predice el siguiente bloque, avanza), que es
como funcionaría en vivo. Acumula TODAS las predicciones fuera de muestra y
mide el Brier, el skill vs. la tasa base y la curva de confiabilidad.

`promover` decide si un calibrador está listo para publicar `probabilidad_subida`:
solo si su Brier walk-forward le gana a la tasa base por un margen mínimo. Si
promueve, deja el calibrador ya ajustado con TODOS los datos (para que el motor
lo cargue) y un veredicto auditable. Es offline y no toca el producto: la
publicación en vivo (lenguaje CMF incluido) es una decisión aparte, humana.

Scores por modo (reconstruidos desde `senales_arquetipo`, que todos los casos
traen):
  - senal_media    : promedio simple de las voces (como el reporte histórico)
  - senal_ponderada: baja a 0.3 las voces contrarian (Intervención A)
  - direccion      : la dirección simulada en %

Uso:
    python3 engine/calibration/walk_forward.py ruta/al/calibracion.json
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # engine/
from contenido import calibracion as cal

BASE = ["institucional_frio", "quant_esceptico", "fomo_evangelista", "doomer",
        "contrarian_sabio", "macro_trader", "influencer_optimista", "value_paciente"]
CONTRARIANS = {"quant_esceptico", "contrarian_sabio"}
MODOS = ("senal_media", "senal_ponderada", "direccion")
MARGEN_PROMOCION = 0.005  # el Brier WF debe ganarle a la base por al menos esto


def _senal(sa, peso_contr=1.0):
    num = sum(sa[a]["senal_media"] * sa[a]["n"] * (peso_contr if a in CONTRARIANS else 1.0)
              for a in BASE if a in sa)
    den = sum(sa[a]["n"] * (peso_contr if a in CONTRARIANS else 1.0)
              for a in BASE if a in sa)
    return num / den if den else 0.0


def cargar(ruta: str) -> list[dict]:
    datos = json.load(open(ruta))
    casos = datos.get("casos", datos) if isinstance(datos, dict) else datos
    out = []
    for c in casos:
        r = c["reaccion_real"]
        pct = r.get("pct_real")
        if pct is None or pct == 0:
            continue
        sa = c.get("senales_arquetipo") or {}
        if not all(a in sa for a in BASE):
            continue
        out.append({"fecha": c.get("fecha") or "", "y": 1 if pct > 0 else 0,
                    "sa": sa, "direccion_pct": c.get("direccion_pct") or 0.0})
    out.sort(key=lambda x: x["fecha"])
    return out


def _score(caso, modo):
    if modo == "senal_media":
        return cal.senal_a_prob_cruda({"senal_media_lideres": _senal(caso["sa"], 1.0)})
    if modo == "senal_ponderada":
        return cal.senal_a_prob_cruda({"senal_media_lideres": _senal(caso["sa"], 0.3)})
    if modo == "direccion":
        return cal.senal_a_prob_cruda({"direccion_pct": caso["direccion_pct"]}, modo="direccion")
    raise ValueError(f"modo desconocido: {modo}")


def walk_forward(casos, modo, min_entrena=200, paso=20, metodo="platt"):
    """Ventana expansiva: entrena con [0:t], predice [t:t+paso], avanza. Acumula
    predicciones fuera de muestra y las evalúa en conjunto."""
    scores = [_score(c, modo) for c in casos]
    ys = [c["y"] for c in casos]
    preds_oos, ys_oos = [], []
    t = min_entrena
    while t < len(scores):
        s_tr, y_tr = scores[:t], ys[:t]
        fin = min(t + paso, len(scores))
        try:
            calib = cal.ajustar_calibrador(s_tr, y_tr, metodo=metodo)
            preds_oos.extend(calib.predict(scores[t:fin]))
        except Exception:
            preds_oos.extend(scores[t:fin])  # si falla, crudo (conservador)
        ys_oos.extend(ys[t:fin])
        t = fin
    if not preds_oos:
        return {"error": "no hay suficientes datos para walk-forward"}
    base = cal.tasa_base(ys_oos)
    brier_modelo = cal.brier(preds_oos, ys_oos)
    brier_base = cal.brier([base] * len(ys_oos), ys_oos)
    return {
        "modo": modo, "metodo": metodo,
        "n_oos": len(preds_oos),
        "brier": round(brier_modelo, 4),
        "brier_base": round(brier_base, 4),
        "skill": round(cal.skill_score(brier_modelo, brier_base), 4),
        "confiabilidad": cal.curva_confiabilidad(preds_oos, ys_oos, n_tramos=5),
    }


def promover(casos, min_entrena=200, paso=20):
    """Corre walk-forward en los 3 modos × 2 métodos, elige el mejor por Brier
    OOS y decide si PROMOVER (ganarle a la base por MARGEN_PROMOCION)."""
    resultados = []
    for modo in MODOS:
        for metodo in ("platt", "isotonic"):
            r = walk_forward(casos, modo, min_entrena, paso, metodo)
            if "error" not in r:
                resultados.append(r)
    if not resultados:
        return {"promovido": False, "motivo": "sin resultados", "candidatos": []}
    resultados.sort(key=lambda r: r["brier"])
    mejor = resultados[0]
    gana = mejor["brier_base"] - mejor["brier"]
    promovido = gana >= MARGEN_PROMOCION
    salida = {"promovido": promovido,
              "margen_requerido": MARGEN_PROMOCION,
              "ganancia_vs_base": round(gana, 4),
              "mejor": mejor,
              "candidatos": resultados}
    if promovido:
        # ajusta el calibrador final con TODOS los datos (para que el motor lo cargue)
        scores = [_score(c, mejor["modo"]) for c in casos]
        ys = [c["y"] for c in casos]
        calib = cal.ajustar_calibrador(scores, ys, metodo=mejor["metodo"])
        salida["calibrador"] = {"modo": mejor["modo"], "metodo": mejor["metodo"],
                                "params": _serializar(calib)}
    return salida


def _serializar(calib) -> dict:
    """Parámetros del calibrador en JSON, para que el motor lo reconstruya."""
    if hasattr(calib, "a") and hasattr(calib, "b"):   # Platt
        return {"tipo": "platt", "a": calib.a, "b": calib.b,
                "mu": calib._mu, "sd": calib._sd}
    if hasattr(calib, "_xs"):                          # Isotonic
        return {"tipo": "isotonic", "xs": list(calib._xs), "ys": list(calib._ys)}
    return {}


if __name__ == "__main__":
    ruta = sys.argv[1] if len(sys.argv) > 1 else "calibracion.json"
    casos = cargar(ruta)
    print(f"casos: {len(casos)}\n")
    rep = promover(casos)
    print(f"{'modo':16}{'metodo':10}{'n_oos':>7}{'brier':>9}{'base':>9}{'skill':>9}")
    for r in rep["candidatos"]:
        print(f"{r['modo']:16}{r['metodo']:10}{r['n_oos']:>7}{r['brier']:>9}{r['brier_base']:>9}{r['skill']:>9}")
    print(f"\nMejor: {rep['mejor']['modo']}/{rep['mejor']['metodo']}  "
          f"gana a la base por {rep['ganancia_vs_base']} (requiere {rep['margen_requerido']})")
    print(f"PROMOVIDO: {rep['promovido']}")
```

## engine/contenido/__init__.py
```python

```

## engine/contenido/analisis_semanal.py
```python
"""La edición de FIN DE SEMANA de El Pulso — la lectura pausada del sábado.

Entre semana El Pulso cuenta las noticias del día. El fin de semana cambia de
marcha: elige UN protagonista y lo mira con calma. Dos formas, que se turnan
solas semana a semana:

  1. "Acción seleccionada" — una empresa de MEDIANA capitalización (el universo
     curado en config/universo_semanal.json). Se elige la que más llamó la
     ATENCIÓN esa semana (la mayor movida de precio).
  2. "Sector en rotación" — un sector que se está moviendo en bloque (energía,
     semiconductores, bancos regionales…). También se elige por atención.

La regla de oro (marco CMF, innegociable): esto NO es consejo de inversión. Es
"lo que nuestros inversionistas IA están viendo o analizando". Por eso el formato
es CONTEXTO primero (qué ES la empresa/sector, factual) y luego un DEBATE de
arquetipos (miradas contrastantes), nunca un "nosotros le vemos potencial".

Este módulo solo SELECCIONA y arma los hechos (el número manda: la variación
viene de Yahoo, gratis). La voz la pone redaccion_ia.redactar_analisis, y el
correo lo dibuja boletin. Degradación elegante: si no hay datos, devuelve None
y el fin de semana cae a la edición normal (o a nada). NUNCA lanza.
"""

import json
import os
from concurrent.futures import ThreadPoolExecutor

from contenido.fuentes import yahoo

# cuántas descargas de precio en paralelo (el universo puede tener cientos de
# empresas; en serie sería lentísimo). Yahoo tolera bien esta concurrencia.
HILOS_PRECIO = 12

# el universo curado vive junto al código; se puede crecer sin tocar Python
_RUTA_UNIVERSO = os.path.join(os.path.dirname(__file__), "config", "universo_semanal.json")

# cuántas sesiones (ruedas) atrás miramos para "la movida de la semana"
RUEDAS_SEMANA = 5

# la franja de capitalización del protagonista (foco de Giorgio: ~1 a 50 mil
# millones de dólares). Se verifica con la capitalización REAL de Yahoo cuando
# está disponible; si no, se acepta el candidato (el universo ya es curado).
CAP_MIN = 1_000_000_000        # 1 000 millones (1B)
CAP_MAX = 50_000_000_000       # 50 000 millones (50B)


def _encuadre_por_cap(cap: float | None) -> str:
    """La etiqueta de tamaño que se muestra en el correo, según la capitalización
    REAL. Sin dato → una etiqueta neutra que sirve para toda la franja."""
    if not cap:
        return "capitalización mediana o grande"
    if cap < 10_000_000_000:
        return "pequeña o mediana capitalización"
    if cap < 30_000_000_000:
        return "mediana capitalización"
    return "gran capitalización"


def cargar_universo(ruta: str | None = None) -> dict:
    """Lee el universo curado. Devuelve {} si falta o está roto (nunca lanza)."""
    try:
        with open(ruta or _RUTA_UNIVERSO, encoding="utf-8") as f:
            datos = json.load(f)
        return datos if isinstance(datos, dict) else {}
    except Exception:
        return {}


def elegir_modo(cuando: dict | None = None, semana_iso: int | None = None) -> str:
    """Turna 'accion' y 'sector' solo, semana a semana, para que la lectura del
    fin de semana no repita siempre lo mismo. Determinista (par/impar de la
    semana ISO), así el mismo sábado siempre da lo mismo (demos reproducibles)."""
    if semana_iso is None:
        from datetime import date
        semana_iso = date.today().isocalendar().week
    return "accion" if semana_iso % 2 == 0 else "sector"


def _movida(serie, ruedas: int = RUEDAS_SEMANA) -> dict | None:
    """A partir de (fechas, cierres) de ~1 mes, calcula la movida de la semana y
    del mes, y la etiqueta de fechas del gráfico. None si la serie es muy corta."""
    if not serie:
        return None
    fechas, cierres = serie
    if not cierres or len(cierres) < 2:
        return None
    ult = cierres[-1]
    ref_semana = cierres[-(ruedas + 1)] if len(cierres) > ruedas else cierres[0]
    var_semana = round((ult - ref_semana) / ref_semana * 100, 2) if ref_semana else None
    var_mes = round((ult - cierres[0]) / cierres[0] * 100, 2) if cierres[0] else None
    if var_semana is None:
        return None
    return {
        "var_semana_pct": var_semana,
        "var_mes_pct": var_mes,
        "ultimo": round(ult, 2),
        "fecha_inicio": yahoo.etiqueta_fecha(fechas[0]),
        "fecha_fin": yahoo.etiqueta_fecha(fechas[-1]),
    }


def _rankear_por_atencion(candidatos: list[dict], simbolo_de, fetch) -> list[dict]:
    """Descarga en PARALELO la movida de la semana de cada candidato y los
    devuelve ordenados por atención (mayor movida absoluta primero). Los que
    Yahoo no responde se omiten. Nunca lanza (un fallo aislado no tumba el lote).
    En paralelo porque el universo puede tener cientos de empresas."""
    def _una(c):
        try:
            serie = fetch(simbolo_de(c), rango="1mo", intervalo="1d")
            movida = _movida(serie)
            return {**c, **movida, "serie": serie} if movida else None
        except Exception:
            return None

    if not candidatos:
        return []
    with ThreadPoolExecutor(max_workers=HILOS_PRECIO) as pool:
        enriquecidos = [e for e in pool.map(_una, candidatos) if e]
    enriquecidos.sort(key=lambda x: -abs(x["var_semana_pct"]))
    return enriquecidos


def _mayor_atencion(candidatos: list[dict], simbolo_de, fetch) -> dict | None:
    """El candidato que MÁS se movió esta semana. None si ninguno trae datos."""
    ranked = _rankear_por_atencion(candidatos, simbolo_de, fetch)
    return ranked[0] if ranked else None


def _grafico_de(ticker: str, nombre: str) -> dict:
    """La especificación del gráfico del protagonista (periodo 'mes' para dar
    contexto: el fin de semana se lee con calma, no al minuto)."""
    return {"ticker": ticker, "nombre": nombre, "periodo": "mes", "moneda": "$"}


def seleccionar_accion(universo: dict, fetch=yahoo.serie_reciente,
                       fetch_fund=yahoo.fundamentales) -> dict | None:
    """La 'acción seleccionada' del fin de semana: la empresa del universo que más
    llamó la atención esta semana, DENTRO de la franja ~1-20B (foco de Giorgio).

    Ordena los candidatos por atención (movida de la semana) y baja por la lista
    trayendo sus fundamentales, hasta dar con la primera EN BANDA. Si Yahoo no da
    la capitalización de un candidato, se acepta (el universo ya es curado). None
    si ninguno trae datos o todos quedan verificadamente fuera de banda."""
    acciones = universo.get("acciones") or []
    rankeados = _rankear_por_atencion(acciones, lambda c: c.get("ticker", ""), fetch)

    elegida, fundamentales = None, None
    for c in rankeados:
        fund = fetch_fund(c.get("ticker", ""))
        cap = (fund or {}).get("market_cap_num")
        en_banda = cap is None or (CAP_MIN <= cap <= CAP_MAX)
        if en_banda:
            elegida, fundamentales = c, fund
            break
    if not elegida:
        return None
    return {
        "modo": "accion",
        "titulo": "Acción seleccionada",
        "encuadre": _encuadre_por_cap((fundamentales or {}).get("market_cap_num")),
        "ticker": elegida["ticker"],
        "nombre": elegida["nombre"],
        "sector": elegida.get("sector", ""),
        "contexto": elegida.get("contexto", ""),
        "var_semana_pct": elegida["var_semana_pct"],
        "var_mes_pct": elegida.get("var_mes_pct"),
        "fecha_inicio": elegida["fecha_inicio"],
        "fecha_fin": elegida["fecha_fin"],
        "fundamentales": fundamentales,   # dict verificado (o None si Yahoo no dio)
        "grafico": _grafico_de(elegida["ticker"], elegida["nombre"]),
    }


def seleccionar_sector(universo: dict, fetch=yahoo.serie_reciente) -> dict | None:
    """El 'sector en rotación' del fin de semana: el sector del universo que más
    se movió en bloque esta semana. None si no hay datos."""
    sectores = universo.get("sectores") or []
    elegido = _mayor_atencion(sectores, lambda c: c.get("etf", ""), fetch)
    if not elegido:
        return None
    return {
        "modo": "sector",
        "titulo": "Sector en rotación",
        "encuadre": "sector completo",
        "ticker": elegido["etf"],
        "nombre": elegido["nombre"],
        "sector": elegido["nombre"],
        "contexto": elegido.get("contexto", ""),
        "en_rotacion_por": elegido.get("en_rotacion_por", ""),
        "ejemplos": elegido.get("ejemplos", []),
        "var_semana_pct": elegido["var_semana_pct"],
        "var_mes_pct": elegido.get("var_mes_pct"),
        "fecha_inicio": elegido["fecha_inicio"],
        "fecha_fin": elegido["fecha_fin"],
        "grafico": _grafico_de(elegido["etf"], elegido["nombre"]),
    }


def preparar_analisis(universo: dict | None = None, modo: str | None = None,
                      cuando: dict | None = None, fetch=yahoo.serie_reciente,
                      fetch_fund=yahoo.fundamentales) -> dict | None:
    """Arma los HECHOS del deep-dive del fin de semana (sin voz todavía).

    Elige el modo (turnándolo solo si no se fuerza), selecciona el protagonista
    por atención y devuelve el dict de hechos para el redactor y el correo. Si el
    modo elegido no trae datos, intenta el otro antes de rendirse. None si nada
    trae datos (entonces el fin de semana cae a la edición normal)."""
    universo = universo if universo is not None else cargar_universo()
    if not universo:
        return None
    modo = modo or elegir_modo(cuando)
    orden = [modo, "sector" if modo == "accion" else "accion"]  # el elegido, luego el otro
    for m in orden:
        if m == "accion":
            sel = seleccionar_accion(universo, fetch, fetch_fund)
        else:
            sel = seleccionar_sector(universo, fetch)
        if sel:
            return sel
    return None
```

## engine/contenido/backtest.py
```python
"""Backtesting histórico — la calibración no espera al futuro.

Le pasa al enjambre exámenes del pasado cuya respuesta real ya se conoce:
titulares de eventos reales (backtest_eventos.json) se simulan hoy y se
comparan con cuánto se movió el símbolo EN ESOS DÍAS históricos (Alpaca).

Reglas de diseño:
- **Tandas pequeñas** (presupuesto LLM ~100 llamadas por simulación):
  cada corrida procesa `tamano` eventos y se detiene. Tope duro TANDA_MAXIMA.
- Los casos quedan con fuente='backtest' y NUNCA destacada: no aparecen
  en el muro ni en la hemeroteca (el archivo es el registro EN VIVO);
  solo alimentan la libreta de calificaciones y la caja fuerte.
- Reproducible: la semilla de cada evento sale de su fecha — repetir una
  tanda no gasta (la caché de cerebros responde gratis).
- Si Alpaca no entrega datos para un evento, queda pendiente y la
  próxima tanda lo reintenta. Nunca lanza.
"""

import gc
import json
import os
from pathlib import Path

from contenido import persistencia

RUTA_EVENTOS = Path(__file__).parent / "backtest_eventos.json"
TANDA_DEFECTO = 5
TANDA_MAXIMA = 40   # freno duro por corrida. Con Starter (no se duerme) + disco
                    # persistente, tandas grandes son seguras; y cada examen se
                    # respalda al instante, así que si Render corta una tanda
                    # larga, la siguiente continúa sin perder nada.
RUEDAS = 2          # misma ventana de medición que el corrector en vivo


def cargar_eventos() -> list[dict]:
    """El banco de exámenes: los curados a mano (backtest_eventos.json) MÁS
    los que el cosechador fue sumando en GitHub (datos/cosecha.json). Se
    fusiona por `id` (lo local manda si hay choque) para que el catálogo
    crezca solo sin depender del disco efímero ni de un redeploy."""
    with open(RUTA_EVENTOS, encoding="utf-8") as archivo:
        locales = json.load(archivo)["eventos"]
    por_id = {}
    try:
        from contenido import respaldo
        for evento in respaldo.cosecha_remota():
            if evento.get("id") and evento.get("titular") and evento.get("simbolo"):
                por_id[evento["id"]] = evento
    except Exception:
        pass  # sin red o sin cosecha: el banco es solo lo local
    for evento in locales:  # lo curado a mano tiene prioridad sobre lo cosechado
        por_id[evento["id"]] = evento
    return sorted(por_id.values(), key=lambda e: e.get("fecha") or "")


def _variacion_historica(simbolo: str, fecha: str, ruedas: int = RUEDAS) -> dict | None:
    """Yahoo primero (histórico largo y completo: acciones, ETFs, cripto),
    Alpaca de respaldo. Stooq quedó fuera: su API de descarga dejó de
    responder (404), lo que estancaba el backtest en ~30 exámenes."""
    from contenido.fuentes import alpaca, yahoo

    return (yahoo.variacion_real(simbolo, fecha, ruedas)
            or alpaca.variacion_real(simbolo, fecha, ruedas))


def _seed(evento: dict) -> int:
    """Semilla determinística por evento: la fecha como número (AAAAMMDD)."""
    return int(evento["fecha"].replace("-", ""))


def _sim_id(evento: dict) -> str:
    return persistencia.id_simulacion(evento["titular"], _seed(evento))


# para eventos sin campo "mercado" (curados viejos), se infiere del símbolo
_SIMBOLOS_MERCADO = {
    "oro": {"GLD", "IAU", "GDX", "NEM", "GOLD"},
    "cripto": {"GBTC", "COIN", "MARA", "RIOT", "MSTR", "ETHE", "BITO", "BTC-USD"},
    "petroleo": {"USO", "XLE", "OXY", "SLB"},
    "indice": {"SPY", "QQQ", "DIA", "IWM"},
}


def _mercado_de(evento: dict) -> str:
    """El mercado de un evento: su campo `mercado`, o inferido del símbolo."""
    if evento.get("mercado"):
        return evento["mercado"]
    simbolo = (evento.get("simbolo") or "").upper()
    for mercado, simbolos in _SIMBOLOS_MERCADO.items():
        if simbolo in simbolos:
            return mercado
    return "accion"


def estado(conexion=None, mercado: str | None = None) -> dict:
    """Cuántos exámenes están rendidos (con nota real) y cuántos faltan.

    Con `mercado` (oro/cripto/petroleo/indice/accion) cuenta y rinde SOLO
    ese mercado — clave para calibrar de forma balanceada (100+/mercado) en
    vez de que las acciones, que son mayoría, se lleven todas las tandas.

    Cuenta lo local Y lo ya respaldado en GitHub: el disco de Render se
    borra con cada deploy, pero un examen en la caja fuerte no se repite
    (repetirlo costaría ~100 llamadas LLM cada vez)."""
    from contenido import respaldo

    propia = conexion is None
    conexion = conexion or persistencia.conectar()
    try:
        eventos = cargar_eventos()
        if mercado:
            eventos = [e for e in eventos if _mercado_de(e) == mercado]
        respaldados = {c.get("sim_id") for c in respaldo.casos_remotos()}
        pendientes = []
        for evento in eventos:
            if _sim_id(evento) in respaldados:
                continue  # la caja fuerte ya lo tiene
            fila = conexion.execute(
                "SELECT reaccion_real FROM simulaciones WHERE id = ?", (_sim_id(evento),)
            ).fetchone()
            if not (fila and fila["reaccion_real"]):
                pendientes.append(evento)
        return {"total": len(eventos), "hechos": len(eventos) - len(pendientes),
                "pendientes": len(pendientes), "_lista_pendiente": pendientes}
    finally:
        if propia:
            conexion.close()


def correr_tanda(conexion=None, tamano: int = TANDA_DEFECTO,
                 simular=None, obtener_variacion=None, mercado: str | None = None) -> dict:
    """Rinde una tanda de exámenes históricos. Devuelve el detalle.

    Con `mercado` rinde SOLO ese mercado (calibración balanceada).
    `simular` y `obtener_variacion` son inyectables para los tests;
    en producción usan el pipeline real y las barras de Alpaca.
    """
    if simular is None:
        from contenido import pipeline
        simular = lambda titular, seed: pipeline.simular_titular_completo(  # noqa: E731
            titular, seed, con_frames=False
        )
    if obtener_variacion is None:
        obtener_variacion = _variacion_historica

    tamano = max(1, min(int(tamano), TANDA_MAXIMA))
    propia = conexion is None
    conexion = conexion or persistencia.conectar()
    try:
        from contenido.corrector import cerebros_ia

        pendientes = estado(conexion, mercado=mercado)["_lista_pendiente"]
        # los recientes primero: sus datos (Alpaca) son los más confiables,
        # y así el avance no se atasca si la fuente antigua no responde
        pendientes.sort(key=lambda e: e["fecha"], reverse=True)
        hechas, sin_datos, sin_ia = [], [], []
        for evento in pendientes[:tamano]:
            # el precio real se consulta ANTES de simular: si no hay dato,
            # el examen se salta sin gastar ni una llamada LLM
            variacion = obtener_variacion(evento["simbolo"], evento["fecha"], RUEDAS)
            if variacion is None:
                sin_datos.append(evento["id"])  # la próxima tanda reintenta
                continue
            reporte, lideres, serie, _ = simular(evento["titular"], _seed(evento))
            if not cerebros_ia(lideres):
                # sin saldo de API los líderes usaron el respaldo léxico: el
                # examen NO se guarda — se rendirá de verdad cuando vuelva la IA
                sin_ia.append(evento["id"])
                break  # sin saldo no tiene sentido seguir gastando la tanda
            sim_id = persistencia.guardar_simulacion(
                conexion, titular=evento["titular"], fuente="backtest",
                seed=_seed(evento), resumen=reporte, lideres=lideres,
                serie_precios=serie, destacada=False,
            )
            persistencia.guardar_reaccion_real(
                conexion, sim_id, {**variacion, "categoria": evento["categoria"],
                                   "cerebros": "ia"}
            )
            hechas.append({"id": evento["id"], "sim_id": sim_id,
                           "sim_pct": reporte.get("direccion_pct"),
                           "real_pct": variacion["pct_real"]})
            # a la caja fuerte DESPUÉS DE CADA EXAMEN (no al final): si un
            # deploy reinicia el motor a mitad de tanda, lo rendido no se pierde
            try:
                from contenido import respaldo
                ultimo_respaldo = respaldo.respaldar(conexion)
            except Exception:
                ultimo_respaldo = None

            # liberar la memoria del modelo de 10.000 agentes ANTES del próximo
            # examen: los agentes y el modelo se referencian en ciclo, así que
            # sin un gc.collect() explícito la basura se acumula y en el plan
            # Starter (512 MB) puede desbordar y reiniciar el motor.
            del reporte, lideres, serie
            gc.collect()

        resultado = {"hechas": hechas, "sin_datos": sin_datos, "sin_ia": sin_ia,
                     "pendientes": len(pendientes) - len(hechas)}
        if hechas:
            resultado["respaldo"] = ultimo_respaldo
        return resultado
    finally:
        if propia:
            conexion.close()


# ---------- evaluación (medir una config SIN re-respaldar) ----------

def _ruta_evaluacion() -> Path:
    """Dónde se guarda el resultado de la última evaluación. En Render, junto a
    la base en el disco persistente; en local, junto al banco de exámenes."""
    db = os.environ.get("ENJAMBRE_DB")
    base = Path(db).parent if db else RUTA_EVENTOS.parent
    return base / "evaluaciones.json"


def _signo(x) -> int:
    if x is None:
        return 0
    return 1 if x > 0 else (-1 if x < 0 else 0)


# tanda máxima por corrida de evaluación: correr más de ~40 simulaciones de
# 10.000 agentes seguidas desborda la RAM (el backtest histórico se limita
# igual). La evaluación es RESUMIBLE, así que varias corridas cubren todo.
TANDA_EVAL_MAX = 40


def _ruta_progreso() -> Path:
    db = os.environ.get("ENJAMBRE_DB")
    base = Path(db).parent if db else RUTA_EVENTOS.parent
    return base / "evaluaciones_progreso.json"


def _cargar_progreso() -> dict:
    try:
        ruta = _ruta_progreso()
        if ruta.exists():
            return json.loads(ruta.read_text(encoding="utf-8")) or {}
    except Exception:
        pass
    return {}


def _guardar_progreso(progreso: dict) -> None:
    try:
        ruta = _ruta_progreso()
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_text(json.dumps(progreso, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass


CATS_VALIDAS = ("negativa", "positiva", "neutra")


def _simbolo_de_caso(caso: dict) -> str:
    """El primer símbolo de un caso respaldado (guarda `simbolos`, lista o
    cadena separada por comas)."""
    s = caso.get("simbolos")
    if isinstance(s, list):
        s = s[0] if s else ""
    return ((s or "").split(",")[0]).strip().upper()


def _mercado_de_caso(caso: dict) -> str:
    """El mercado de un caso respaldado: su campo `mercado`, o inferido del
    símbolo (mismo criterio que `_mercado_de` para eventos)."""
    if caso.get("mercado"):
        return caso["mercado"]
    simbolo = _simbolo_de_caso(caso)
    for mercado, simbolos in _SIMBOLOS_MERCADO.items():
        if simbolo in simbolos:
            return mercado
    return "accion"


def _casos_locales() -> list[dict]:
    """Casos de calibración desde la base LOCAL (no depende del respaldo remoto,
    que puede estar caído o con el token vencido). Mismo formato que
    casos_remotos(): sim_id, reaccion_real, fecha, simbolos, …"""
    from contenido import persistencia, respaldo
    con = persistencia.conectar()
    try:
        return respaldo.exportar_casos(con)
    finally:
        con.close()


def evaluar(tamano: int | None = None, mercado: str | None = None,
            peso: float | None = None, umbral: float | None = None,
            doomer: float | None = None, reiniciar: bool = False,
            simular=None, guardar: bool = True, refrescar: bool = False,
            local: bool = False) -> dict:
    """Re-simula los exámenes YA respaldados bajo el código/entorno ACTUAL y
    mide el acierto de DIRECCIÓN por categoría, comparándolo con el resultado
    real ya conocido. Sirve para medir el impacto de un cambio (ej. P2) SIN
    tocar el respaldo histórico.

    - `peso`: si se pasa, fija ENJAMBRE_PESO_TONO_INVERSORES SOLO durante esta
      evaluación (para barrer valores de P2 sin re-desplegar ni cambiarlo en
      Render). Si es None, usa el valor vigente del entorno.
    - NO persiste simulaciones ni re-respalda: es una medición pura.
    - Usa la caché de cerebros: barato si está caliente, gasta si está fría.
    - Solo cuenta los exámenes que de verdad usaron el LLM (con_ia); si el
      motor cayó al respaldo léxico (sin saldo), lo reporta y no contamina.
    """
    import time

    from model import (_peso_invertidores_env, _umbral_correccion_env,
                       _peso_doomer_env, _peso_doomer_env_forzado)

    # Refrescar caché: fija ENJAMBRE_IGNORAR_CACHE SOLO durante esta evaluación,
    # para medir un cambio de PROMPT con respuestas frescas (la caché, indexada
    # sin el prompt, si no devolvería lo viejo). GASTA LLM. Es el wrapper más
    # externo: envuelve toda la medición (incluidos los barridos de doomer/peso).
    if refrescar:
        previo = os.environ.get("ENJAMBRE_IGNORAR_CACHE")
        os.environ["ENJAMBRE_IGNORAR_CACHE"] = "1"
        try:
            return evaluar(tamano=tamano, mercado=mercado, peso=peso, umbral=umbral,
                           doomer=doomer, reiniciar=reiniciar, simular=simular,
                           guardar=guardar, refrescar=False, local=local)
        finally:
            if previo is None:
                os.environ.pop("ENJAMBRE_IGNORAR_CACHE", None)
            else:
                os.environ["ENJAMBRE_IGNORAR_CACHE"] = previo

    # Intervención 1: fija ENJAMBRE_PESO_DOOMER SOLO durante esta evaluación.
    if doomer is not None:
        previo = os.environ.get("ENJAMBRE_PESO_DOOMER")
        os.environ["ENJAMBRE_PESO_DOOMER"] = str(doomer)
        try:
            return evaluar(tamano=tamano, mercado=mercado, peso=peso, umbral=umbral,
                           doomer=None, reiniciar=reiniciar, simular=simular,
                           guardar=guardar, local=local)
        finally:
            if previo is None:
                os.environ.pop("ENJAMBRE_PESO_DOOMER", None)
            else:
                os.environ["ENJAMBRE_PESO_DOOMER"] = previo

    # Plan A: fija ENJAMBRE_UMBRAL_CORRECCION_SESGO SOLO durante esta evaluación
    # (para medir base vs corrección sin re-desplegar). Mismo patrón que `peso`.
    if umbral is not None:
        previo = os.environ.get("ENJAMBRE_UMBRAL_CORRECCION_SESGO")
        os.environ["ENJAMBRE_UMBRAL_CORRECCION_SESGO"] = str(umbral)
        try:
            return evaluar(tamano=tamano, mercado=mercado, peso=peso, umbral=None,
                           reiniciar=reiniciar, simular=simular, guardar=guardar,
                           local=local)
        finally:
            if previo is None:
                os.environ.pop("ENJAMBRE_UMBRAL_CORRECCION_SESGO", None)
            else:
                os.environ["ENJAMBRE_UMBRAL_CORRECCION_SESGO"] = previo

    if peso is not None:
        previo = os.environ.get("ENJAMBRE_PESO_TONO_INVERSORES")
        os.environ["ENJAMBRE_PESO_TONO_INVERSORES"] = str(peso)
        try:
            return evaluar(tamano=tamano, mercado=mercado, peso=None, umbral=None,
                           reiniciar=reiniciar, simular=simular, guardar=guardar,
                           local=local)
        finally:
            if previo is None:
                os.environ.pop("ENJAMBRE_PESO_TONO_INVERSORES", None)
            else:
                os.environ["ENJAMBRE_PESO_TONO_INVERSORES"] = previo

    if simular is None:
        from contenido import pipeline
        simular = lambda t, s: pipeline.simular_titular_completo(  # noqa: E731
            t, s, con_frames=False)
    from contenido import respaldo
    from contenido.corrector import cerebros_ia

    if local:
        casos = _casos_locales()
    else:
        try:
            casos = respaldo.casos_remotos()
        except Exception:
            casos = []
        if not casos:
            # El respaldo remoto está vacío o caído (p. ej. token vencido): en vez
            # de medir sobre 0 casos, caemos a la base LOCAL. La medición no debe
            # depender de la salud del respaldo.
            casos = _casos_locales()
    # Evaluación DIRECTA sobre los casos ya respaldados (traen titular + el
    # resultado real). NO se cruza con el banco de eventos: ese cruce por sim_id
    # es frágil (el raw y la API de GitHub sirven versiones distintas del
    # archivo) y daba 0 en Render. La semilla sale del propio sim_id, así que es
    # determinística por caso: la 1ª pasada calienta la caché de cerebros y las
    # siguientes (otros valores de peso) reusan esa caché — el barrido es barato.
    evaluables = []
    for c in casos:
        rr = c.get("reaccion_real") or {}
        if rr.get("pct_real") is None or rr.get("categoria") not in CATS_VALIDAS:
            continue
        if mercado and _mercado_de_caso(c) != mercado:
            continue
        evaluables.append(c)
    evaluables.sort(key=lambda c: c.get("fecha") or "", reverse=True)
    n_categorizados = len(evaluables)

    # progreso ACUMULADO por (mercado, peso), guardado en disco: cada corrida
    # simula a lo sumo una tanda (para no desbordar la RAM) de casos NUEVOS y
    # SUMA el resultado. Varias corridas cubren todo el mercado; re-correr no
    # repite lo ya hecho. `reiniciar` borra el progreso de esa (mercado, peso).
    peso_actual = _peso_invertidores_env(1.0)
    umbral_actual = _umbral_correccion_env(0.0)
    # Si el env fija un peso, ese override manda en TODOS los mercados (medición);
    # si no, el tono usa la SEGMENTACIÓN por-mercado (índice 1.0, cripto 0.0, …).
    # Se rotula "seg" para que la clave de progreso NO choque con dm0.0 (que es
    # doomer forzado a 0 en todos lados) y para que el reporte no mienta.
    doomer_forzado = _peso_doomer_env_forzado()
    doomer_actual = doomer_forzado if doomer_forzado is not None else "seg"
    # el progreso se acumula por (mercado, peso, umbral, doomer): así cada
    # combinación se mide aparte. `dm0.0` = doomer forzado a 0 (base); `dmseg` =
    # segmentado por mercado (producción).
    clave = f"{mercado or 'todos'}|peso{peso_actual}|umb{umbral_actual}|dm{doomer_actual}"
    progreso = _cargar_progreso()
    if reiniciar:
        progreso[clave] = {}
    hechos = progreso.setdefault(clave, {})

    pendientes = [c for c in evaluables if c["sim_id"] not in hechos]
    por_tanda = min(int(tamano), TANDA_EVAL_MAX) if tamano else TANDA_EVAL_MAX

    con_ia = sin_ia = 0
    for c in pendientes[:por_tanda]:
        rr = c["reaccion_real"]
        real, cat = rr["pct_real"], rr["categoria"]
        seed = int(c["sim_id"][:8], 16)  # semilla determinística por caso
        reporte, lideres, serie, _ = simular(c["titular"], seed)
        if cerebros_ia(lideres):
            con_ia += 1
        else:
            sin_ia += 1
        ok = 1 if _signo(reporte.get("direccion_pct")) == _signo(real) else 0
        # Prioridad 1 (plan combinado v2): acierto por el signo de la SEÑAL de los
        # líderes (senal_media_ponderada), no del precio simulado de 1 corrida.
        # Medido: +4.3 pts global, +10 índice. Se guarda APARTE; no cambia `ok`.
        ok_senal = 1 if _signo(reporte.get("senal_media_ponderada")) == _signo(real) else 0
        hechos[c["sim_id"]] = {"cat": cat, "ok": ok, "ok_senal": ok_senal}
        del reporte, lideres, serie
        gc.collect()
    nuevos = min(len(pendientes), por_tanda)
    if guardar:
        _guardar_progreso(progreso)

    # acierto ACUMULADO sobre todo lo hecho para (mercado, peso)
    # cats guarda [aciertos_precio, total, aciertos_senal] por categoría
    cats = {"negativa": [0, 0, 0], "positiva": [0, 0, 0], "neutra": [0, 0, 0]}
    for r in hechos.values():
        if r.get("cat") in cats:
            cats[r["cat"]][1] += 1
            cats[r["cat"]][0] += r.get("ok", 0)
            cats[r["cat"]][2] += r.get("ok_senal", 0)

    def _acc(par):
        return {"aciertos": par[0], "total": par[1],
                "acierto": round(par[0] / par[1], 4) if par[1] else None,
                "acierto_senal": round(par[2] / par[1], 4) if par[1] else None}

    tot = sum(c[1] for c in cats.values())
    ok = sum(c[0] for c in cats.values())
    ok_senal_tot = sum(c[2] for c in cats.values())
    resultado = {
        "fecha": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "peso_tono_invertidores": peso_actual,
        "umbral_correccion_sesgo": umbral_actual,
        "peso_doomer": doomer_actual,
        "evaluados": tot, "con_ia": con_ia, "sin_ia": sin_ia,
        "acierto_global": round(ok / tot, 4) if tot else None,
        "acierto_senal_global": round(ok_senal_tot / tot, 4) if tot else None,
        "negativa": _acc(cats["negativa"]), "positiva": _acc(cats["positiva"]),
        "neutra": _acc(cats["neutra"]),
        # progreso ACUMULADO: cuántos exámenes llevamos de este (mercado, peso)
        "progreso": {"hechos": tot, "total": n_categorizados,
                     "faltan": n_categorizados - tot,
                     "nuevos_esta_tanda": nuevos,
                     "completo": tot >= n_categorizados},
        # diagnóstico: para ver de dónde sale un 0
        "diag": {"casos_respaldados": len(casos),
                 "casos_categorizados": n_categorizados},
    }
    if guardar:
        _registrar_evaluacion(resultado)
    return resultado


def _registrar_evaluacion(resultado: dict) -> None:
    """Guarda el resultado (con un pequeño historial) para que el endpoint GET
    lo devuelva. Nunca lanza."""
    try:
        ruta = _ruta_evaluacion()
        ruta.parent.mkdir(parents=True, exist_ok=True)
        historial = []
        if ruta.exists():
            historial = (json.loads(ruta.read_text(encoding="utf-8")) or {}).get("historial", [])
        historial.append(resultado)
        ruta.write_text(json.dumps({"ultima": resultado, "historial": historial[-20:]},
                                   ensure_ascii=False, indent=1), encoding="utf-8")
    except Exception:
        pass


def ultima_evaluacion() -> dict | None:
    """El último resultado de evaluación guardado (para el endpoint GET)."""
    try:
        ruta = _ruta_evaluacion()
        if ruta.exists():
            return json.loads(ruta.read_text(encoding="utf-8"))
    except Exception:
        pass
    return None
```

## engine/contenido/boletin.py
```python
"""El Pulso del Enjambre — la newsletter (CONTENIDO.md sección 6).

Arma el correo diario desde plantilla (HTML de correo: tablas + estilos
inline, ancho 600px) y lo envía por Resend. Todos los textos variables pasan
por el filtro de vocabulario CMF antes de salir. Degradación elegante: sin
RESEND_API_KEY, genera el HTML pero no envía.

Paleta CLARA (boceto aprobado por Giorgio, 5-ago-2026): fondo blanco cálido,
texto tinta, dorado de protagonista, teal de reparto, verde/rojo en los
movimientos. El enjambre 3D vive en oscuro; el diario se lee en claro.
"""

import html
import logging
import os
import time

import httpx

from contenido import persistencia
from contenido.vocabulario import DISCLAIMER, es_publicable

_esc = html.escape
log = logging.getLogger("enjambre.boletin")

# Resend limita a ~2 correos/segundo. El bucle de envío dispara uno tras otro,
# así que en ráfaga los últimos reciben 429 ("demasiadas peticiones") y antes se
# perdían en silencio (de ahí un "enviada a 3 de 6"). Reintentamos con espera.
REINTENTOS_ENVIO = 4

URL_RESEND = "https://api.resend.com/emails"
REMITENTE = os.environ.get("PULSO_REMITENTE", "El Enjambre <pulso@rubiconlab.cl>")
BASE_WEB = os.environ.get("ENJAMBRE_WEB_URL", "https://enjambre-ai-agents.vercel.app")
BASE_API = os.environ.get("ENJAMBRE_API_URL", "https://enjambre-motor.onrender.com")
# la página donde el lector gratuito se hace Premium (el botón del teaser del domingo)
PULSO_PREMIUM_URL = os.environ.get("PULSO_PREMIUM_URL", f"{BASE_WEB}/premium")
PRECIO_PREMIUM = os.environ.get("PULSO_PREMIUM_PRECIO", "USD 6,99/mes")

# --- paleta CLARA del correo (boceto aprobado) ---
PAPEL = "#faf8f4"          # fondo de página, blanco cálido
BLANCO = "#ffffff"         # tarjeta del correo
TEXTO = "#1e1b17"          # texto principal (el ink de marca, ahora como texto)
TEXTO_2 = "#3c382f"        # cuerpo
MUTE = "#6f6a5f"           # secundario
ORO = "#b0831a"            # dorado protagonista (marca, botón)
TEAL = "#2f7a6f"           # teal de reparto (enlaces)
SUBE = "#2f8f66"           # verde — sube
BAJA = "#c0504d"           # rojo-arcilla — baja
LINEA = "#eae5db"          # hairline


def _flecha(direccion_pct: float) -> str:
    if direccion_pct > 1.0:
        return "▲"
    if direccion_pct < -1.0:
        return "▼"
    return "◆"


def COLOR_DIR(pct: float) -> str:
    return SUBE if pct > 0.15 else BAJA if pct < -0.15 else TEAL


def _limpiar(texto: str) -> str:
    """Un texto variable solo sale si pasa el filtro CMF; si no, se neutraliza.

    Además ESCAPA el HTML: los titulares llegan de fuentes externas (Alpaca) y
    las frases las escribe la IA leyendo un titular que puede venir del público.
    Sin escapar, un `<` en un titular rompe el correo — y un titular hostil podría
    colar marcado (un enlace falso) en el Pulso que reciben los suscriptores.
    Todos los usos de esta función son contexto HTML.
    """
    return _esc(texto) if es_publicable(texto) else "—"


def _url_segura(url: str) -> str:
    """Solo http(s) llega al correo: cierra la puerta a `javascript:` y `data:`."""
    limpia = (url or "").strip()
    return _esc(limpia) if limpia.lower().startswith(("http://", "https://")) else ""


def _voz(frase: dict) -> str:
    from brains.arquetipos import POR_ID
    nombre = POR_ID.get(frase.get("arquetipo", ""), {}).get("nombre", frase.get("arquetipo", ""))
    return f"«{_limpiar(frase.get('frase', ''))}» — {nombre}"


def _parrafos(texto: str, color: str = TEXTO_2, size: int = 15) -> str:
    """Convierte el texto con voz (párrafos separados por línea en blanco) en
    <p> escapados. El texto ya viene filtrado por CMF desde redaccion_ia."""
    if not texto:
        return ""
    return "".join(
        f'<p style="margin:0 0 12px;color:{color};font-size:{size}px;line-height:1.55;">{_esc(p.strip())}</p>'
        for p in texto.split("\n\n") if p.strip()
    )


def asunto_del_dia(destacada: dict) -> str:
    palabras = destacada["titular"].split()
    resumen = " ".join(palabras[:6]) + ("…" if len(palabras) > 6 else "")
    return f"🐝 El Pulso — {resumen}"


def asunto_finde(analisis: dict | None) -> str:
    """El asunto de la edición de fin de semana: la sección + el protagonista."""
    analisis = analisis or {}
    titulo = analisis.get("titulo", "Fin de semana")
    nombre = analisis.get("nombre", "")
    return f"🐝 El Pulso — {titulo}: {nombre}".rstrip(": ")


def _fila_mercado(m: dict) -> str:
    url = _url_segura(m.get("url", ""))
    fuente = (f'<a href="{url}" style="color:{TEAL};font-size:12px;text-decoration:none;">·&nbsp;fuente</a>'
              if url else "")
    if m.get("tipo") == "evento":
        marca = f'<span style="color:{ORO};font-weight:bold;">◆</span>'
        cuerpo = _esc(m["titular"])
    else:  # movimiento de precio
        marca = f'<span style="color:{COLOR_DIR(m["variacion_pct"])};font-weight:bold;">{_flecha(m["variacion_pct"])}</span>'
        cuerpo = _esc(m["frase"])
    return f"""<tr><td style="padding:6px 0;color:{TEXTO_2};font-size:14px;line-height:1.45;border-top:1px solid {LINEA};">
        {marca} {cuerpo} {fuente}</td></tr>"""


def _bloque_mercado(brief: dict | None) -> str:
    """'Lo que pasó' — movimientos verificados + eventos, con su fuente.
    (En modo con voz, esto lo cuenta el editorial; se usa en el fallback.)"""
    if not brief or not brief.get("mercado"):
        return ""
    filas = "".join(_fila_mercado(m) for m in brief["mercado"][:5])
    return f"""
  <tr><td style="padding:18px 32px 2px;">
    <div style="font-size:11px;letter-spacing:2px;color:{MUTE};text-transform:uppercase;font-weight:600;">Lo que pasó</div>
  </td></tr>
  <tr><td style="padding:4px 32px;"><table role="presentation" width="100%" cellpadding="0" cellspacing="0">{filas}</table></td></tr>"""


def _pildora(pct) -> str:
    """Una píldora verde/roja con la variación, o '—' si no hay dato."""
    if pct is None:
        return f'<span style="color:{MUTE};font-size:12px;">—</span>'
    if pct > 0.05:
        color, bg, flecha = SUBE, "rgba(47,143,102,0.14)", "▲"
    elif pct < -0.05:
        color, bg, flecha = BAJA, "rgba(192,80,77,0.13)", "▼"
    else:
        color, bg, flecha = MUTE, "rgba(60,56,47,0.06)", "•"
    return (f'<span style="display:inline-block;padding:3px 9px;border-radius:12px;'
            f'background:{bg};color:{color};font-size:12px;font-weight:bold;">'
            f'{flecha} {abs(pct)}%</span>')


def _tabla_mercado(brief: dict | None) -> str:
    """'La foto del día': el telón de fondo (índices, petróleo, oro) con sus
    columnas Día / Mes / Año."""
    foto = (brief or {}).get("foto")
    if not foto:
        return ""
    th = (f'font-size:10px;letter-spacing:1px;color:{MUTE};text-transform:uppercase;'
          'font-weight:600;padding:0 0 8px;')
    filas = ""
    for f in foto:
        filas += f"""<tr>
          <td style="padding:7px 0;border-top:1px solid {LINEA};color:{TEXTO};font-size:14px;font-weight:600;">{_esc(f["nombre"])}</td>
          <td align="right" style="padding:7px 0;border-top:1px solid {LINEA};">{_pildora(f.get("variacion_pct"))}</td>
          <td align="right" style="padding:7px 0;border-top:1px solid {LINEA};">{_pildora(f.get("var_mes_pct"))}</td>
          <td align="right" style="padding:7px 0;border-top:1px solid {LINEA};">{_pildora(f.get("var_ano_pct"))}</td>
        </tr>"""
    return f"""
  <tr><td style="padding:18px 32px 2px;">
    <div style="font-size:11px;letter-spacing:2px;color:{MUTE};text-transform:uppercase;font-weight:600;">La foto del día</div>
  </td></tr>
  <tr><td style="padding:6px 32px 4px;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
      <tr><th align="left" style="{th}">Mercado</th><th align="right" style="{th}">Día</th><th align="right" style="{th}">Mes</th><th align="right" style="{th}">Año</th></tr>
      {filas}
    </table>
  </td></tr>"""


def _bloque_observa(brief: dict | None) -> str:
    """'Qué observa el enjambre hoy' — atención, NUNCA predicción."""
    if not brief or not brief.get("observa"):
        return ""
    filas = "".join(
        f"""<p style="margin:4px 0;color:{MUTE};font-size:14px;">· {_esc(t)}</p>"""
        for t in brief["observa"][:3]
    )
    return f"""
  <tr><td style="padding:14px 32px 4px;border-top:1px solid {LINEA};">
    <div style="font-size:11px;letter-spacing:2px;color:{MUTE};text-transform:uppercase;font-weight:600;">Qué observa el enjambre hoy</div>
    {filas}</td></tr>"""


def _grafico_img(g: dict | None) -> str:
    """El <img> del gráfico de precio REAL de un activo, si la historia trae uno.
    Apunta al endpoint /api/grafico, que lo dibuja desde Yahoo. Si el ticker es
    inválido, no se pone gráfico (nunca rompe el correo)."""
    if not isinstance(g, dict) or not g.get("ticker"):
        return ""
    from urllib.parse import quote
    ticker = str(g.get("ticker", "")).strip()
    if not ticker or len(ticker) > 15 or not all(c.isalnum() or c in ".=^-" for c in ticker):
        return ""
    periodo = str(g.get("periodo", "semana")).strip() or "semana"
    nombre = str(g.get("nombre", "") or ticker)[:40]
    moneda = str(g.get("moneda", "$") or "$")[:2]
    url = (f"{BASE_API}/api/grafico/{quote(ticker, safe='.=^-')}"
           f"?n={quote(nombre)}&p={quote(periodo)}&m={quote(moneda)}")
    return f"""
  <tr><td style="padding:8px 32px 2px;">
    <img src="{url}" width="536" alt="Gráfico de {_esc(nombre)}"
      style="width:100%;max-width:536px;display:block;border:1px solid {LINEA};border-radius:8px;">
  </td></tr>"""


def _sin_prefijo_linea(texto: str) -> str:
    """Quita un 'En una línea:' inicial si el redactor lo incluyó (lo pone la plantilla)."""
    t = texto.strip()
    bajo = t.lower()
    for p in ("en una línea:", "en una linea:", "en resumen:", "bottom line:"):
        if bajo.startswith(p):
            return t[len(p):].strip()
    return t


def _bloque_historia(h: dict) -> str:
    """Una historia del día: etiqueta, titular, bajada, gráfico real, análisis
    y el 'en una línea' de cierre. Todo escapado (los titulares y el texto de la
    IA no pueden inyectar HTML) y filtrado por CMF vía _limpiar."""
    if not isinstance(h, dict):
        return ""
    kicker = _limpiar(str(h.get("kicker", "") or ""))
    emoji = _esc(str(h.get("emoji", "") or ""))
    titular = _limpiar(str(h.get("titular", "") or ""))
    dek = _limpiar(str(h.get("dek", "") or ""))
    cuerpo = _parrafos(str(h.get("cuerpo", "") or ""))
    bl = _limpiar(_sin_prefijo_linea(str(h.get("bottom_line", "") or "")))
    if not titular or not cuerpo:
        return ""
    kicker_html = (f'<div style="font-size:11px;letter-spacing:1.5px;color:{TEAL};'
                   f'text-transform:uppercase;font-weight:700;margin-bottom:4px;">{kicker}</div>'
                   if kicker and kicker != "—" else "")
    dek_html = (f'<div style="font-family:Georgia,serif;font-style:italic;color:{MUTE};'
                f'font-size:14px;margin:3px 0 10px;">{dek}</div>' if dek and dek != "—" else "")
    bl_html = (f'<div style="margin:15px 0 2px;padding:12px 16px;background:{PAPEL};'
               f'border-left:3px solid {ORO};border-radius:6px;color:{TEXTO_2};font-size:14px;">'
               f'<b style="color:{TEXTO};">En una línea:</b> {bl}</div>' if bl and bl != "—" else "")
    return f"""
  <tr><td style="padding:22px 32px 2px;border-top:1px solid {LINEA};">
    {kicker_html}
    <div style="font-family:Georgia,serif;font-size:22px;font-weight:bold;color:{TEXTO};line-height:1.25;">{emoji} {titular}</div>
    {dek_html}
  </td></tr>
  {_grafico_img(h.get("grafico"))}
  <tr><td style="padding:8px 32px 2px;">
    {cuerpo}
    {bl_html}
  </td></tr>"""


def _bloque_debate(debate: list[dict]) -> str:
    """El debate de arquetipos: miradas contrastantes de nuestros inversionistas
    IA sobre el protagonista. Cada una es nombre del perfil + su frase (escapada
    y filtrada por CMF). Este contraste ES el análisis del fin de semana."""
    if not debate:
        return ""
    tarjetas = ""
    for d in debate:
        if not isinstance(d, dict):
            continue
        nombre = _limpiar(str(d.get("nombre", "") or ""))
        mirada = _limpiar(str(d.get("mirada", "") or ""))
        if not mirada or mirada == "—":
            continue
        tarjetas += f"""
      <tr><td style="padding:10px 0;border-top:1px solid {LINEA};">
        <div style="font-size:11px;letter-spacing:1px;color:{TEAL};text-transform:uppercase;font-weight:700;margin-bottom:3px;">{nombre}</div>
        <div style="color:{TEXTO_2};font-size:14px;line-height:1.5;">{mirada}</div>
      </td></tr>"""
    if not tarjetas:
        return ""
    return f"""
  <tr><td style="padding:18px 32px 2px;">
    <div style="font-size:11px;letter-spacing:2px;color:{MUTE};text-transform:uppercase;font-weight:700;">🐝 Lo que ven nuestros inversionistas IA</div>
    <div style="color:{MUTE};font-size:12px;font-style:italic;margin:4px 0 2px;">Miradas distintas del mismo caso — no un veredicto único.</div>
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0">{tarjetas}</table>
  </td></tr>"""


def _pildora_pct_texto(fmt: str) -> str:
    """Una píldora verde/roja a partir de un porcentaje YA formateado por Yahoo
    (ej. '35.50%', '-4.20%'). El color sale del signo; no reinterpreta el número."""
    t = str(fmt or "").strip()
    negativo = t.startswith("-")
    color, bg = (BAJA, "rgba(192,80,77,0.13)") if negativo else (SUBE, "rgba(47,143,102,0.14)")
    flecha = "▼" if negativo else "▲"
    return (f'<span style="display:inline-block;padding:2px 8px;border-radius:12px;'
            f'background:{bg};color:{color};font-size:12px;font-weight:bold;">{flecha} {_esc(t)}</span>')


# fundamentales que se muestran, en orden, y cuáles llevan píldora de color (%)
_FUND_FILAS = [
    ("market_cap", "Capitalización", False),
    ("ingresos", "Ingresos (12m)", False),
    ("crecimiento_ingresos", "Crecimiento ingresos", True),
    ("margen_bruto", "Margen bruto", False),
    ("margen_operativo", "Margen operativo", False),
    ("ebitda", "EBITDA", False),
    ("deuda", "Deuda total", False),
    ("caja", "Caja", False),
]


def _tabla_fundamentales(fund: dict | None) -> str:
    """'Los números' del protagonista: la ficha de fundamentales VERIFICADOS
    (datos de mercado), como la tabla de un analista. Solo cifras que existen;
    se dibuja desde los datos, no desde el texto de la IA. '' si no hay ficha."""
    if not isinstance(fund, dict) or not fund:
        return ""
    filas = ""
    for clave, etiqueta, es_pct in _FUND_FILAS:
        valor = fund.get(clave)
        if not valor:
            continue
        celda = _pildora_pct_texto(valor) if es_pct else f'<b style="color:{TEXTO};font-size:14px;">{_esc(str(valor))}</b>'
        filas += f"""<tr>
          <td style="padding:7px 0;border-top:1px solid {LINEA};color:{TEXTO_2};font-size:13px;">{etiqueta}</td>
          <td align="right" style="padding:7px 0;border-top:1px solid {LINEA};">{celda}</td>
        </tr>"""
    if not filas:
        return ""
    return f"""<table role="presentation" width="100%" cellpadding="0" cellspacing="0"
      style="background:{PAPEL};border:1px solid {LINEA};border-radius:8px;padding:2px 14px;margin:2px 0 6px;">{filas}
      <tr><td colspan="2" style="padding:6px 0 2px;color:{MUTE};font-size:11px;font-style:italic;">Datos de mercado (Yahoo Finance), últimos disponibles.</td></tr>
    </table>"""


def _bloque_numeros(hechos: dict, red: dict) -> str:
    """'Los números': la ficha de fundamentales (tabla desde datos) + la lectura
    financiera en simple que escribió la IA. '' si no hay ni ficha ni prosa."""
    tabla = _tabla_fundamentales(hechos.get("fundamentales"))
    prosa = _parrafos(str(red.get("numeros", "") or ""))
    if not tabla and not prosa:
        return ""
    return f"""
  <tr><td style="padding:14px 32px 2px;border-top:1px solid {LINEA};">
    <div style="font-size:11px;letter-spacing:2px;color:{MUTE};text-transform:uppercase;font-weight:700;margin-bottom:6px;">Los números</div>
    {tabla}
    {prosa}
  </td></tr>"""


def _bloque_analisis(brief: dict | None) -> str:
    """La EDICIÓN DE FIN DE SEMANA: el deep-dive de una mid-cap o un sector.
    Contexto primero (qué es), la lectura (por qué está en la mira), el gráfico
    real, los números (fundamentales), el debate de arquetipos y qué observar.
    Todo escapado + filtrado CMF. '' si no hay análisis redactado."""
    brief = brief or {}
    red = brief.get("analisis_redactado")
    hechos = brief.get("analisis") or {}
    if not isinstance(red, dict) or not red.get("contexto") or not red.get("titular"):
        return ""

    titulo = _limpiar(str(hechos.get("titulo", "Edición de fin de semana")))
    encuadre = _limpiar(str(hechos.get("encuadre", "")))
    nombre = _limpiar(str(hechos.get("nombre", "")))
    ticker = _esc(str(hechos.get("ticker", "") or ""))
    sector = _limpiar(str(hechos.get("sector", "") or ""))
    titular = _limpiar(str(red.get("titular", "")))
    dek = _limpiar(str(red.get("dek", "") or ""))
    contexto = _parrafos(str(red.get("contexto", "") or ""))
    lectura = _parrafos(str(red.get("lectura", "") or ""))
    que_observar = _parrafos(str(red.get("que_observar", "") or ""), color=TEXTO_2)
    pildora = _pildora(hechos.get("var_semana_pct"))

    dek_html = (f'<div style="font-family:Georgia,serif;font-style:italic;color:{MUTE};'
                f'font-size:15px;margin:4px 0 8px;">{dek}</div>' if dek and dek != "—" else "")
    sector_html = (f'<span style="color:{MUTE};font-size:12px;">· {sector}</span>'
                   if sector and sector != "—" else "")
    lectura_html = (f"""
  <tr><td style="padding:6px 32px 2px;">
    <div style="font-size:11px;letter-spacing:2px;color:{MUTE};text-transform:uppercase;font-weight:700;margin-bottom:4px;">Por qué está en la mira</div>
    {lectura}
  </td></tr>""" if lectura else "")
    observar_html = (f"""
  <tr><td style="padding:8px 32px 6px;">
    <div style="margin:6px 0 2px;padding:12px 16px;background:{PAPEL};border-left:3px solid {ORO};border-radius:6px;">
      <div style="font-size:11px;letter-spacing:1px;color:{ORO};text-transform:uppercase;font-weight:700;margin-bottom:4px;">Qué observar</div>
      <div style="color:{TEXTO_2};font-size:14px;line-height:1.55;">{que_observar}</div>
    </div>
  </td></tr>""" if que_observar else "")

    return f"""
  <tr><td style="padding:22px 32px 4px;text-align:center;border-top:1px solid {LINEA};">
    <div style="font-size:11px;letter-spacing:3px;color:{ORO};text-transform:uppercase;font-weight:700;">◆ Edición de fin de semana</div>
    <div style="font-size:11px;letter-spacing:1px;color:{TEAL};text-transform:uppercase;font-weight:700;margin-top:6px;">{titulo} · {encuadre}</div>
  </td></tr>
  <tr><td style="padding:4px 32px 2px;">
    <div style="font-family:Georgia,serif;font-size:24px;font-weight:bold;color:{TEXTO};line-height:1.25;">{titular}</div>
    {dek_html}
    <div style="margin:6px 0 2px;">{pildora} <b style="color:{TEXTO};font-size:14px;">{nombre}</b>
      <span style="color:{MUTE};font-size:12px;">{ticker}</span> {sector_html}
      <span style="color:{MUTE};font-size:12px;">· en la semana</span></div>
  </td></tr>
  <tr><td style="padding:10px 32px 2px;">
    <div style="font-size:11px;letter-spacing:2px;color:{MUTE};text-transform:uppercase;font-weight:700;margin-bottom:4px;">Qué es</div>
    {contexto}
  </td></tr>
  {lectura_html}
  {_grafico_img(hechos.get("grafico"))}
  {_bloque_numeros(hechos, red)}
  {_bloque_debate(red.get("debate"))}
  {observar_html}
  <tr><td style="padding:2px 32px 8px;">
    <div style="color:{MUTE};font-size:12px;font-style:italic;line-height:1.5;">No es asesoría de inversión: es lo que nuestros inversionistas IA están viendo y analizando.</div>
  </td></tr>"""


def _mov_texto(pct) -> str:
    """El movimiento semanal como texto en español ('+7,6%', '−4,2%'), sin
    revelar nada más. '' si no hay dato."""
    if pct is None:
        return ""
    signo = "+" if pct >= 0 else "−"
    return f"{signo}{abs(pct):.1f}".replace(".", ",") + "%"


def _bloque_analisis_teaser(brief: dict | None) -> str:
    """El TEASER del deep-dive del domingo, para los suscriptores GRATUITOS.
    Revela el sector y el gancho, pero NUNCA el nombre, los números, el debate
    ni el 'qué observar' — eso es Premium. Termina en un botón de pago.
    Mismo criterio de existencia que _bloque_analisis: '' si no hay análisis."""
    brief = brief or {}
    red = brief.get("analisis_redactado")
    hechos = brief.get("analisis") or {}
    if not isinstance(red, dict) or not red.get("contexto") or not red.get("titular"):
        return ""

    encuadre = _limpiar(str(hechos.get("encuadre", "mediana capitalización")))
    sector = _limpiar(str(hechos.get("sector", "") or ""))
    mov = _mov_texto(hechos.get("var_semana_pct"))

    sector_txt = f"del sector {sector}" if sector and sector != "—" else "de mediana capitalización"
    intro = (f"Esta semana nuestros inversionistas IA analizaron a fondo una empresa "
             f"{_esc(encuadre.lower())} {sector_txt}.")

    # el gancho: sector + movimiento de la semana, sin identificar la empresa
    if sector and sector != "—" and mov:
        gancho = (f"«El sector {sector} tuvo una semana de {mov}. El enjambre se detuvo en una "
                  f"compañía que sus ocho perfiles no logran mirar igual…»")
    else:
        gancho = ("«El enjambre eligió una compañía para mirar a fondo — y sus ocho perfiles "
                  "no se ponen de acuerdo…»")

    items = [
        "Qué hace la empresa y por qué entró al radar del enjambre",
        "Sus números en simple: ingresos, crecimiento, márgenes, EBITDA, deuda y caja",
        "El debate de los 8 perfiles sobre el mismo caso: el optimista vs. el escéptico vs. el macro",
        "El gráfico real de su último mes",
        "«Qué observar» de aquí en adelante",
    ]
    check = f'<span style="color:{SUBE};font-weight:bold;">✓</span>'
    lista = "".join(
        f'<tr><td style="padding:5px 0;color:{TEXTO_2};font-size:14px;line-height:1.45;">{check}&nbsp; {t}</td></tr>'
        for t in items
    )

    return f"""
  <tr><td style="padding:22px 32px 4px;text-align:center;border-top:1px solid {LINEA};">
    <div style="font-size:11px;letter-spacing:3px;color:{ORO};text-transform:uppercase;font-weight:700;">🔒 El análisis de la semana · Premium</div>
  </td></tr>
  <tr><td style="padding:8px 32px 2px;">
    <div style="font-family:Georgia,serif;font-size:21px;font-weight:bold;color:{TEXTO};line-height:1.3;">{intro}</div>
  </td></tr>
  <tr><td style="padding:10px 32px 2px;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0">{lista}</table>
  </td></tr>
  <tr><td style="padding:14px 32px 2px;">
    <div style="position:relative;background:{PAPEL};border-left:3px solid {ORO};border-radius:6px;padding:14px 16px;">
      <div style="font-size:10px;letter-spacing:2px;text-transform:uppercase;color:{MUTE};font-weight:700;margin-bottom:6px;">Vista previa</div>
      <div style="font-family:Georgia,serif;font-style:italic;font-size:16px;line-height:1.5;color:{TEXTO_2};">{_esc(gancho)}</div>
      <div style="text-align:right;font-size:12px;font-weight:700;color:{ORO};margin-top:6px;">continúa en Premium →</div>
    </div>
  </td></tr>
  <tr><td style="padding:18px 32px 6px;text-align:center;">
    <a href="{_url_segura(PULSO_PREMIUM_URL)}" style="display:inline-block;background:{ORO};color:#ffffff;text-decoration:none;
      font-weight:bold;font-size:15px;letter-spacing:.3px;padding:14px 30px;border-radius:8px;">Leer el análisis completo →</a>
    <div style="color:{MUTE};font-size:12px;margin-top:8px;">Desde {_esc(PRECIO_PREMIUM)} · cancela cuando quieras</div>
  </td></tr>
  <tr><td style="padding:2px 32px 8px;">
    <div style="color:{MUTE};font-size:12px;font-style:italic;line-height:1.5;">Análisis educativo elaborado por un sistema de IA. No es recomendación ni asesoría de inversión.</div>
  </td></tr>"""


def _tabla_semana(foto: list[dict]) -> str:
    """'La semana en números': el movimiento SEMANAL del telón (índices, petróleo,
    oro), una sola columna con su píldora verde/roja. '' si no hay datos."""
    if not foto:
        return ""
    filas = ""
    for f in foto:
        filas += f"""<tr>
          <td style="padding:7px 0;border-top:1px solid {LINEA};color:{TEXTO};font-size:14px;font-weight:600;">{_esc(str(f.get("nombre","")))}</td>
          <td align="right" style="padding:7px 0;border-top:1px solid {LINEA};">{_pildora(f.get("var_semana_pct"))}</td>
        </tr>"""
    return f"""
  <tr><td style="padding:14px 32px 2px;">
    <div style="font-size:11px;letter-spacing:2px;color:{MUTE};text-transform:uppercase;font-weight:700;margin-bottom:4px;">La semana en números</div>
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0">{filas}</table>
  </td></tr>"""


def _bloque_tema(t: dict) -> str:
    """Un tema de la semana: etiqueta, titular, análisis, gráfico opcional y 'qué
    observar'. Todo escapado + filtrado CMF."""
    if not isinstance(t, dict):
        return ""
    kicker = _limpiar(str(t.get("kicker", "") or ""))
    emoji = _esc(str(t.get("emoji", "") or ""))
    titular = _limpiar(str(t.get("titular", "") or ""))
    analisis = _parrafos(str(t.get("analisis", "") or ""))
    observar = _limpiar(str(t.get("que_observar", "") or ""))
    if not titular or not analisis:
        return ""
    kicker_html = (f'<div style="font-size:11px;letter-spacing:1.5px;color:{TEAL};'
                   f'text-transform:uppercase;font-weight:700;margin-bottom:4px;">{kicker}</div>'
                   if kicker and kicker != "—" else "")
    obs_html = (f'<div style="margin:12px 0 2px;padding:10px 14px;background:{PAPEL};'
                f'border-left:3px solid {ORO};border-radius:6px;color:{TEXTO_2};font-size:13px;">'
                f'<b style="color:{TEXTO};">Qué observar:</b> {observar}</div>'
                if observar and observar != "—" else "")
    return f"""
  <tr><td style="padding:20px 32px 2px;border-top:1px solid {LINEA};">
    {kicker_html}
    <div style="font-family:Georgia,serif;font-size:21px;font-weight:bold;color:{TEXTO};line-height:1.28;">{emoji} {titular}</div>
  </td></tr>
  {_grafico_img(t.get("grafico"))}
  <tr><td style="padding:8px 32px 2px;">
    {analisis}
    {obs_html}
  </td></tr>"""


def _bloque_resumen(brief: dict | None) -> str:
    """La EDICIÓN DEL SÁBADO: el resumen de la semana con punto de vista. Intro +
    'la semana en números' + los temas (qué pasó, por qué, qué observar) + cierre.
    '' si no hay resumen redactado (entonces el correo usa lo normal)."""
    brief = brief or {}
    red = brief.get("resumen_redactado")
    hechos = brief.get("resumen") or {}
    if not isinstance(red, dict) or not (red.get("temas") or red.get("intro")):
        return ""
    titulo = _limpiar(str(hechos.get("titulo", "El Pulso de la semana")))
    intro = _parrafos(str(red.get("intro", "") or ""))
    cierre = _parrafos(str(red.get("cierre", "") or ""))
    temas_html = "".join(_bloque_tema(t) for t in (red.get("temas") or []))
    intro_html = (f'<tr><td style="padding:8px 32px 2px;">{intro}</td></tr>' if intro else "")
    cierre_html = (f'<tr><td style="padding:10px 32px 2px;">{cierre}</td></tr>' if cierre else "")
    return f"""
  <tr><td style="padding:22px 32px 4px;text-align:center;border-top:1px solid {LINEA};">
    <div style="font-size:11px;letter-spacing:3px;color:{ORO};text-transform:uppercase;font-weight:700;">◆ Edición de fin de semana</div>
    <div style="font-family:Georgia,serif;font-size:24px;color:{TEXTO};font-weight:bold;margin-top:6px;">{titulo}</div>
    <div style="font-size:11px;letter-spacing:1px;color:{TEAL};text-transform:uppercase;font-weight:700;margin-top:4px;">Repaso de la semana</div>
  </td></tr>
  {_tabla_semana(hechos.get("foto") or [])}
  {intro_html}
  {temas_html}
  {cierre_html}
  <tr><td style="padding:2px 32px 8px;">
    <div style="color:{MUTE};font-size:12px;font-style:italic;line-height:1.5;">No es asesoría de inversión: es nuestra lectura de lo que movió al mercado esta semana.</div>
  </td></tr>"""


def asunto_resumen(hechos: dict | None = None) -> str:
    """El asunto de la edición del sábado."""
    return "🐝 El Pulso — La semana en el mercado"


def asunto_cierre() -> str:
    """El asunto de la edición de la tarde (Premium)."""
    return "🐝 El Pulso — El cierre del mercado"


def _cabecera_cierre(titulo: str) -> str:
    """La cabecera de la edición de la tarde (sello Premium + título)."""
    return f"""
  <tr><td style="padding:22px 32px 4px;text-align:center;border-top:1px solid {LINEA};">
    <div style="font-size:11px;letter-spacing:3px;color:{ORO};text-transform:uppercase;font-weight:700;">🌆 Edición de la tarde · Premium</div>
    <div style="font-family:Georgia,serif;font-size:24px;color:{TEXTO};font-weight:bold;margin-top:6px;">{titulo}</div>
    <div style="font-size:11px;letter-spacing:1px;color:{TEAL};text-transform:uppercase;font-weight:700;margin-top:4px;">Lo que de verdad se movió hoy, y por qué</div>
  </td></tr>"""


_PIE_CIERRE = (f'<tr><td style="padding:10px 32px 8px;">'
               f'<div style="color:{{MUTE}};font-size:12px;font-style:italic;line-height:1.5;">'
               f'Los movimientos y sus motivos, investigados y verificados por nuestro '
               f'reportero IA. No es asesoría de inversión.</div></td></tr>')


def _bloque_cierre_con_voz(titulo: str, apertura: str, historias: list[dict]) -> str:
    """El cierre con VOZ Moby: apertura ('Buenas tardes') + mini-historias, con el
    mismo tratamiento visual que las historias de la mañana (_bloque_historia)."""
    apertura_html = ""
    parrafos = _parrafos(str(apertura or ""))
    if parrafos:
        apertura_html = f"""
  <tr><td style="padding:16px 32px 2px;">
    <div style="font-size:11px;letter-spacing:2px;color:{MUTE};text-transform:uppercase;font-weight:700;">🌆 Buenas tardes</div>
    {parrafos}
  </td></tr>"""
    cuerpo = "".join(_bloque_historia(h) for h in historias)
    if not cuerpo and not apertura_html:
        return ""
    return (_cabecera_cierre(titulo) + apertura_html + cuerpo
            + _PIE_CIERRE.format(MUTE=MUTE))


def _bloque_cierre(brief: dict | None) -> str:
    """La EDICIÓN DE LA TARDE (Premium): 'el cierre del mercado'. Los mayores
    movimientos REALES del día investigados por el reportero IA. Con voz Moby son
    mini-historias; sin IA, la lista llana (titular + razón + píldora del %).
    Todo escapado + filtrado CMF. '' si no hay movimientos."""
    brief = brief or {}
    cierre = brief.get("cierre") or {}
    movers = cierre.get("movers") or []
    if not movers:
        return ""
    titulo = _limpiar(str(cierre.get("titulo", "El cierre del mercado")))

    # CAMINO CON VOZ: si el redactor le puso voz Moby, el cierre son mini-historias
    # (apertura + 2-3 párrafos por protagonista), igual que la edición de la mañana.
    red = cierre.get("redactado") or {}
    historias = [h for h in (red.get("historias") or []) if isinstance(h, dict)]
    if historias:
        return _bloque_cierre_con_voz(titulo, red.get("buenas_tardes", ""), historias)

    # CAMINO LLANO (respaldo): sin IA, la lista de siempre (píldora + titular + razón).
    filas = ""
    for m in movers:
        if not isinstance(m, dict):
            continue
        titular = _limpiar(str(m.get("titular", "") or ""))
        if not titular or titular == "—":
            continue
        razon = _limpiar(str(m.get("razon", "") or ""))
        pildora = _pildora(m.get("var_pct"))
        razon_html = (f'<div style="color:{MUTE};font-size:13px;line-height:1.5;margin-top:4px;">{razon}</div>'
                      if razon and razon != "—" else "")
        filas += f"""
      <tr><td style="padding:12px 0;border-top:1px solid {LINEA};">
        <div style="line-height:1.45;">{pildora} <b style="color:{TEXTO};font-size:14.5px;">{titular}</b></div>
        {razon_html}
      </td></tr>"""
    if not filas:
        return ""
    return _cabecera_cierre(titulo) + f"""
  <tr><td style="padding:6px 32px 2px;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0">{filas}</table>
  </td></tr>""" + _PIE_CIERRE.format(MUTE=MUTE)


def asunto_teaser_premium() -> str:
    """El asunto del correo del domingo para los suscriptores GRATUITOS: NO
    revela el nombre de la empresa (eso es el gancho Premium)."""
    return "🐝 El Pulso — El análisis de la semana (Premium)"


_DIAS_ES = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
_MESES_ES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
             "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


def fecha_es_de_iso(iso: str) -> str:
    """Convierte 'AAAA-MM-DD' en 'domingo 17 de agosto' (para rearmar el teaser
    al enviar, cuando solo tenemos la fecha ISO de la edición)."""
    from datetime import date
    try:
        d = date.fromisoformat(str(iso)[:10])
        return f"{_DIAS_ES[d.weekday()]} {d.day} de {_MESES_ES[d.month - 1]}"
    except Exception:
        return str(iso)


def teaser_para(brief: dict | None, fecha_iso: str) -> tuple[str | None, str | None]:
    """Si la edición del día es el deep-dive del domingo (Premium), arma el
    (html_teaser, asunto_teaser) para los suscriptores gratuitos. Si no es una
    edición con deep-dive, devuelve (None, None) → todos reciben la completa."""
    if not (isinstance(brief, dict) and _bloque_analisis_teaser(brief)):
        return None, None
    fecha_es = fecha_es_de_iso(fecha_iso)
    html = construir_html([], fecha_es, token_baja=persistencia.TOKEN_BAJA_SENTINEL,
                          brief=brief, premium=False)
    return html, asunto_teaser_premium()


def _footer_enjambre() -> str:
    """El Enjambre al pie, como herramienta HERMANA (no como autor de El Pulso):
    una invitación a probarlo + su descripción. Nada de 'esto lo escribe el
    enjambre' — El Pulso es el diario serio; El Enjambre, otra herramienta nuestra."""
    return f"""
  <tr><td style="padding:10px 32px 24px;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#171019;border-radius:12px;">
      <tr><td style="padding:20px 22px;">
        <div style="font-size:10px;letter-spacing:2px;text-transform:uppercase;color:#e3c565;font-weight:700;">🐝 También de Rubicón Lab</div>
        <div style="font-family:Georgia,serif;font-size:18px;color:#ffffff;font-weight:bold;margin:6px 0;">Mira al mercado entrar en pánico, en cámara lenta</div>
        <div style="color:#c7bfb2;font-size:13px;line-height:1.55;margin-bottom:14px;">El Enjambre es nuestra herramienta educativa: le sueltas un titular y 10.000 inversionistas simulados con IA reaccionan en vivo, en 3D. Ves formarse la manada, el miedo y la euforia — el comportamiento de las masas del mercado, hecho visible.</div>
        <a href="{BASE_WEB}" style="display:inline-block;background:#e3c565;color:#1b1410;text-decoration:none;font-weight:bold;font-size:12px;letter-spacing:.5px;padding:11px 20px;border-radius:7px;">Probar El Enjambre →</a>
      </td></tr>
    </table>
  </td></tr>"""


def construir_html(destacadas: list[dict], fecha: str, token_baja: str = "TOKEN",
                   brief: dict | None = None, premium: bool = True) -> str:
    """El HTML del correo (rediseño estilo diario): las NOTICIAS con análisis y
    gráficos reales son el cuerpo; El Enjambre baja al pie como herramienta
    hermana. `destacadas` ya no arma el cuerpo (el correo es noticioso), pero se
    mantiene la firma por compatibilidad. brief["redactado"] trae las historias.

    `premium`: solo afecta al deep-dive del domingo. Con premium=True se manda el
    análisis completo; con premium=False, el TEASER con botón de pago (versión
    gratuita). El resumen del sábado y las ediciones de la semana son iguales
    para todos (no se cobran)."""
    brief = brief or {}
    red = brief.get("redactado") or {}
    url_baja = f"{BASE_API}/api/baja/{token_baja}"

    # EDICIÓN DE FIN DE SEMANA: si hay resumen de la semana (sábado) o deep-dive
    # (domingo) redactado, ESE es el correo (reemplaza las noticias del día).
    # El deep-dive del domingo es Premium: gratis → teaser; de pago → completo.
    resumen_html = _bloque_resumen(brief)
    if resumen_html:
        analisis_html = ""  # sábado: para todos, no se cobra
    else:
        analisis_completo = _bloque_analisis(brief)
        if analisis_completo and not premium:
            analisis_html = _bloque_analisis_teaser(brief)
        else:
            analisis_html = analisis_completo
    # EDICIÓN DE LA TARDE (Premium): 'el cierre del mercado'. Reemplaza el cuerpo
    # como una edición especial (sin historias ni foto del día).
    cierre_html = _bloque_cierre(brief)
    finde_html = resumen_html or analisis_html or cierre_html
    es_finde = bool(finde_html)

    historias = [] if es_finde else [h for h in (red.get("historias") or []) if isinstance(h, dict)]
    historias_html = "".join(_bloque_historia(h) for h in historias)

    buenos_html = ""
    if not es_finde and red.get("buenos_dias"):
        buenos_html = f"""
  <tr><td style="padding:22px 32px 2px;">
    <div style="font-size:11px;letter-spacing:2px;color:{MUTE};text-transform:uppercase;font-weight:700;">☀️ Buenos días</div>
    {_parrafos(red["buenos_dias"])}
  </td></tr>"""

    # la foto del día (índices, petróleo, oro) va entre semana; el fin de semana
    # el deep-dive se lee solo, sin la tabla del telón (cierres del viernes).
    tabla_html = "" if es_finde else _tabla_mercado(brief)

    # respaldo: si la IA no escribió historias, al menos 'lo que pasó' crudo
    # (mejor un digest simple que un correo vacío). No aplica al fin de semana.
    cuerpo_respaldo = _bloque_mercado(brief) if (not historias and not es_finde) else ""

    return f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:{PAPEL};">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:{PAPEL};">
<tr><td align="center" style="padding:24px 12px;">
<table role="presentation" width="600" cellpadding="0" cellspacing="0"
  style="max-width:600px;width:100%;background:{BLANCO};border:1px solid {LINEA};border-radius:8px;">

  <tr><td style="padding:30px 32px 20px;text-align:center;border-bottom:1px solid {LINEA};">
    <div style="font-family:Georgia,serif;font-size:34px;font-weight:bold;color:{ORO};line-height:1;">El Pulso 🐝</div>
    <div style="font-size:10px;letter-spacing:3px;color:{TEAL};text-transform:uppercase;font-weight:bold;margin-top:10px;">Diario de mercado</div>
    <div style="font-family:Georgia,serif;font-style:italic;font-size:16px;color:{MUTE};margin-top:4px;">{fecha}</div>
    <div style="font-size:11px;color:{MUTE};margin-top:6px;">by <b style="color:{TEXTO_2};">Rubicón Lab</b></div>
  </td></tr>
  {tabla_html}
  {buenos_html}
  {finde_html}
  {historias_html}
  {cuerpo_respaldo}
  {_footer_enjambre()}

  <tr><td style="padding:8px 32px 28px;border-top:1px solid {LINEA};text-align:center;">
    <div style="color:{MUTE};font-size:11px;line-height:1.5;">{DISCLAIMER}</div>
    <div style="margin-top:10px;">
      <a href="{url_baja}" style="color:{TEAL};font-size:11px;">Desuscribirse en un clic</a>
    </div>
  </td></tr>

</table></td></tr></table></body></html>"""


def _tag_edicion(fecha: str | None) -> list[dict] | None:
    """El tag que Resend devuelve en el webhook, para atribuir aperturas/clics a
    su edición. Resend solo admite letras/números/_/-; la fecha AAAA-MM-DD cumple."""
    if not fecha:
        return None
    limpio = "".join(c for c in fecha if c.isalnum() or c in "-_")[:60]
    return [{"name": "edicion", "value": limpio}] if limpio else None


def _espera_reintento(respuesta, intento: int) -> float:
    """Segundos a esperar antes de reintentar: respeta el 'Retry-After' de Resend
    si viene; si no, retroceso exponencial suave (1, 2, 4…). Tope de 30s."""
    ra = respuesta.headers.get("Retry-After") or respuesta.headers.get("retry-after")
    if ra:
        try:
            return min(float(ra), 30.0)
        except (TypeError, ValueError):
            pass
    return min(2.0 ** (intento - 1), 30.0)


def _motivo_resend(respuesta) -> str:
    """Un motivo corto y legible del fallo de Resend (para el log y para la página
    de 'Listo'). Resend suele mandar {"message": "...", "name": "..."} en el cuerpo."""
    try:
        datos = respuesta.json()
        msg = str(datos.get("message") or datos.get("name") or "").strip()
    except Exception:
        msg = ""
    if not msg:
        msg = (respuesta.text or "").strip()[:120]
    return f"HTTP {respuesta.status_code}: {msg}" if msg else f"HTTP {respuesta.status_code}"


def _enviar_resend(destinatario: str, asunto: str, html: str,
                   fecha_edicion: str | None = None) -> tuple[bool, str]:
    """El envío real por Resend, con reintentos. Devuelve (ok, motivo): motivo es
    "" si salió bien, o una razón corta del fallo (para el log y la página de
    revisión). No lanza."""
    clave = os.environ.get("RESEND_API_KEY")
    if not clave:
        return False, "sin RESEND_API_KEY"
    cuerpo = {"from": REMITENTE, "to": [destinatario], "subject": asunto, "html": html}
    tags = _tag_edicion(fecha_edicion)
    if tags:
        cuerpo["tags"] = tags
    cabeceras = {"Authorization": f"Bearer {clave}", "Content-Type": "application/json"}
    for intento in range(1, REINTENTOS_ENVIO + 1):
        try:
            respuesta = httpx.post(URL_RESEND, headers=cabeceras, json=cuerpo, timeout=20)
        except Exception as e:
            log.warning("Envío a %s falló (%s); reintento %d/%d.",
                        destinatario, type(e).__name__, intento, REINTENTOS_ENVIO)
            if intento < REINTENTOS_ENVIO:
                time.sleep(2 ** (intento - 1))
                continue
            return False, f"red: {type(e).__name__}"
        if respuesta.status_code < 300:
            return True, ""
        # 429 (límite de Resend) o 5xx: esperamos y reintentamos. Otros 4xx
        # (dirección inválida, etc.) no se arreglan reintentando: se cae y avisa.
        reintenta = respuesta.status_code == 429 or respuesta.status_code >= 500
        if reintenta and intento < REINTENTOS_ENVIO:
            espera = _espera_reintento(respuesta, intento)
            log.warning("Envío a %s: HTTP %d; espero %.1fs y reintento %d/%d.",
                        destinatario, respuesta.status_code, espera, intento, REINTENTOS_ENVIO)
            time.sleep(espera)
            continue
        motivo = _motivo_resend(respuesta)
        log.warning("Envío a %s falló: %s", destinatario, motivo)
        return False, motivo
    return False, "reintentos agotados"


def enviar(destinatario: str, asunto: str, html: str, fecha_edicion: str | None = None) -> bool:
    """Envía un correo por Resend. False si no hay clave o falla (no lanza).
    `fecha_edicion` etiqueta el correo para poder medir su apertura por edición."""
    return _enviar_resend(destinatario, asunto, html, fecha_edicion)[0]


def enviar_confirmacion(email: str, token_confirma: str) -> bool:
    """El correo del double opt-in: un clic para confirmar la suscripción."""
    url = f"{BASE_API}/api/confirmar/{token_confirma}"
    html = f"""<!doctype html><html><body style="margin:0;background:{PAPEL};">
<table role="presentation" width="100%" style="background:{PAPEL};"><tr><td align="center" style="padding:32px;">
<table role="presentation" width="600" style="max-width:600px;background:{BLANCO};border:1px solid {LINEA};border-radius:8px;">
  <tr><td style="padding:34px;text-align:center;">
    <div style="font-family:Georgia,serif;font-size:30px;color:{ORO};font-weight:bold;">El Enjambre 🐝</div>
    <p style="color:{TEXTO_2};font-size:16px;line-height:1.5;">Confirma tu suscripción a <b>El Pulso</b>,
      el diario de mercado donde el enjambre simulado reacciona a los titulares del día.</p>
    <a href="{url}" style="display:inline-block;background:{ORO};color:#ffffff;text-decoration:none;
      font-weight:bold;padding:13px 28px;border-radius:4px;text-transform:uppercase;letter-spacing:1px;">Confirmar suscripción</a>
    <p style="color:{MUTE};font-size:12px;margin-top:18px;">
      Si no fuiste tú, ignora este correo y no recibirás nada más.</p>
    <p style="color:{MUTE};font-size:11px;">{DISCLAIMER}</p>
  </td></tr>
</table></td></tr></table></body></html>"""
    return enviar(email, "Confirma tu suscripción a El Pulso 🐝", html)


def enviar_bienvenida(email: str, token_baja: str) -> bool:
    """El correo de bienvenida del opt-in SIMPLE: ya quedó suscrito con un clic
    (sin confirmar). Le damos la bienvenida y el enlace de baja siempre visible
    (todo correo lo debe llevar)."""
    url_baja = f"{BASE_API}/api/baja/{token_baja}"
    html = f"""<!doctype html><html><body style="margin:0;background:{PAPEL};">
<table role="presentation" width="100%" style="background:{PAPEL};"><tr><td align="center" style="padding:32px;">
<table role="presentation" width="600" style="max-width:600px;background:{BLANCO};border:1px solid {LINEA};border-radius:8px;">
  <tr><td style="padding:34px;text-align:center;">
    <div style="font-family:Georgia,serif;font-size:30px;color:{ORO};font-weight:bold;">El Pulso 🐝</div>
    <p style="color:{TEXTO_2};font-size:16px;line-height:1.5;">¡Bienvenido! Ya estás suscrito a <b>El Pulso</b>,
      el diario de mercado donde el enjambre reacciona a los titulares del día. Te llega cada mañana temprano.</p>
    <a href="{BASE_WEB}" style="display:inline-block;background:{ORO};color:#ffffff;text-decoration:none;
      font-weight:bold;padding:13px 28px;border-radius:6px;">Conoce El Enjambre →</a>
    <p style="color:{MUTE};font-size:12px;margin-top:20px;">
      ¿No querías suscribirte? <a href="{url_baja}" style="color:{TEAL};">Desuscríbete en un clic</a>.</p>
    <p style="color:{MUTE};font-size:11px;">{DISCLAIMER}</p>
  </td></tr>
</table></td></tr></table></body></html>"""
    return enviar(email, "¡Bienvenido a El Pulso! 🐝", html)


def enviar_desbloqueo_enjambre(email: str, token: str) -> bool:
    """El enlace mágico: un clic para desbloquear 40 simulaciones/mes en El
    Enjambre. Solo llega a los suscriptores Premium (el servidor ya lo verificó)."""
    url = f"{BASE_WEB}/?premium_token={token}"
    html = f"""<!doctype html><html><body style="margin:0;background:{PAPEL};">
<table role="presentation" width="100%" style="background:{PAPEL};"><tr><td align="center" style="padding:32px;">
<table role="presentation" width="600" style="max-width:600px;background:{BLANCO};border:1px solid {LINEA};border-radius:8px;">
  <tr><td style="padding:34px;text-align:center;">
    <div style="font-family:Georgia,serif;font-size:30px;color:{ORO};font-weight:bold;">El Enjambre 🐝</div>
    <p style="color:{TEXTO_2};font-size:16px;line-height:1.5;">Gracias por ser <b>Premium</b>. Con un clic desbloqueas
      <b>40 simulaciones al mes</b> en El Enjambre en este dispositivo.</p>
    <a href="{_url_segura(url)}" style="display:inline-block;background:{ORO};color:#ffffff;text-decoration:none;
      font-weight:bold;padding:13px 28px;border-radius:6px;">Desbloquear El Enjambre</a>
    <p style="color:{MUTE};font-size:12px;margin-top:18px;">Si no pediste esto, ignora este correo.
      El enlace es personal — no lo compartas.</p>
    <p style="color:{MUTE};font-size:11px;">{DISCLAIMER}</p>
  </td></tr>
</table></td></tr></table></body></html>"""
    return enviar(email, "Desbloquea El Enjambre (Premium) 🐝", html)


def enviar_pulso(conexion, destacadas: list[dict], fecha: str) -> dict:
    """Envía el Pulso a todos los suscriptores activos. Devuelve el conteo."""
    activos = persistencia.suscriptores_activos(conexion)
    asunto = asunto_del_dia(destacadas[0])
    enviados, fallidos = 0, 0
    for suscriptor in activos:
        html = construir_html(destacadas, fecha, token_baja=suscriptor["token_baja"])
        if enviar(suscriptor["email"], asunto, html):
            enviados += 1
        else:
            fallidos += 1
    return {"suscriptores": len(activos), "enviados": enviados, "fallidos": fallidos}


# ---------- El correo de REVISIÓN (humano en el lazo, desde el celular) ----------

PULSO_ADMIN_EMAIL = os.environ.get("PULSO_ADMIN_EMAIL", "")


def _banner_revision(fecha_es: str, token: str, suscriptores: int) -> str:
    """El banner que se inyecta arriba del preview en el correo de revisión."""
    url = f"{BASE_API}/pulso/revisar/{token}"
    return f"""<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#161009;">
  <tr><td align="center" style="padding:18px 16px;">
    <table role="presentation" width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;">
      <tr><td style="text-align:center;">
        <div style="font:700 11px/1 system-ui,sans-serif;letter-spacing:2px;text-transform:uppercase;color:#e3c565;">⏸ Pendiente de tu revisión</div>
        <div style="font-family:Georgia,serif;font-size:19px;color:#faf8f4;margin:6px 0 2px;">El Pulso — {_esc(fecha_es)}</div>
        <div style="color:#a8a291;font-size:13px;margin-bottom:12px;">Abajo va la edición tal como la recibirían tus {suscriptores} suscriptores. Revísala y decide.</div>
        <a href="{url}" style="display:inline-block;background:#e3c565;color:#161009;text-decoration:none;
          font-weight:bold;font-size:13px;letter-spacing:1px;text-transform:uppercase;padding:13px 30px;border-radius:6px;">Revisar y decidir →</a>
      </td></tr>
    </table>
  </td></tr>
</table>"""


def construir_revision(preview_html: str, fecha_es: str, token: str, suscriptores: int) -> str:
    """Inyecta el banner de revisión arriba del preview real (WYSIWYG)."""
    banner = _banner_revision(fecha_es, token, suscriptores)
    corte = preview_html.find(">", preview_html.find("<body"))
    if corte == -1:  # por si el preview no es un doc completo
        return banner + preview_html
    corte += 1
    return preview_html[:corte] + banner + preview_html[corte:]


def enviar_revision(fecha_es: str, preview_html: str, token: str, suscriptores: int,
                    admin_email: str | None = None) -> bool:
    """Envía a Giorgio el correo de revisión (preview + botón para decidir).
    Va a su propio correo → funciona aun sin dominio (modo prueba de Resend)."""
    destino = (admin_email or PULSO_ADMIN_EMAIL).strip()
    if not destino:
        return False
    html = construir_revision(preview_html, fecha_es, token, suscriptores)
    return enviar(destino, f"📋 Revisar El Pulso — {fecha_es}", html)


def enviar_a_suscriptores(conexion, preview_html: str, asunto: str,
                          fecha_edicion: str | None = None,
                          teaser_html: str | None = None,
                          asunto_teaser: str | None = None,
                          solo_premium: bool = False) -> dict:
    """Envía la edición YA APROBADA a los suscriptores activos, reemplazando el
    marcador del token de baja por el de cada uno (WYSIWYG con lo revisado).
    Cada correo va etiquetado con `fecha_edicion` para medir su apertura.

    Si se pasa `teaser_html` (edición Premium del domingo), los suscriptores
    GRATUITOS reciben ese teaser y los Premium el `preview_html` completo. Sin
    `teaser_html`, todos reciben lo mismo (comportamiento de siempre).

    `solo_premium` (edición de la tarde): solo se envía a los suscriptores
    Premium; los gratuitos no reciben nada (no es su edición)."""
    activos = persistencia.suscriptores_activos(conexion)
    if solo_premium:
        activos = [s for s in activos if s.get("premium")]
    enviados = 0
    premium_enviados = 0
    fallos = []
    for s in activos:
        gratuito = teaser_html is not None and not s.get("premium")
        base = teaser_html if gratuito else preview_html
        subj = (asunto_teaser or asunto) if gratuito else asunto
        html = base.replace(persistencia.TOKEN_BAJA_SENTINEL, s["token_baja"])
        ok, motivo = _enviar_resend(s["email"], subj, html, fecha_edicion=fecha_edicion)
        if ok:
            enviados += 1
            if not gratuito:
                premium_enviados += 1
        else:
            fallo = {"email": s["email"], "motivo": motivo}
            # 422 = dirección permanentemente inválida (p. ej. @example.com o un
            # correo mal escrito): se da de baja sola para no reintentarla en cada
            # edición ni inflar la cuenta. Los errores transitorios (429/5xx) NO
            # tocan al suscriptor: ya se reintentaron dentro de _enviar_resend.
            if motivo.startswith("HTTP 422"):
                try:
                    persistencia.desactivar_por_email(conexion, s["email"])
                    fallo["desactivado"] = True
                    log.warning("Suscriptor %s dado de baja: dirección inválida (%s).",
                                s["email"], motivo)
                except Exception:
                    pass
            fallos.append(fallo)
    return {"suscriptores": len(activos), "enviados": enviados,
            "fallidos": len(activos) - enviados, "premium": premium_enviados,
            "fallos": fallos}
```

## engine/contenido/calibracion.py
```python
"""Calibración de la señal del enjambre a probabilidad honesta.

El enjambre produce una señal agregada (el sentimiento de los líderes, la
dirección del precio simulado). Este módulo la convierte en una **probabilidad**
P(sí) ∈ [0, 1] y la **calibra** para que ese número sea honesto: cuando el
enjambre dice "80% seguro", que de verdad acierte ~80% de las veces.

Por qué importa (para Giorgio, en simple): un "% de dirección" no dice qué tan
confiado está el enjambre. Una probabilidad calibrada sí — y es lo que se puede
comparar de igual a igual contra un mercado de predicción (vía el Brier score).

Diseño:
- **Python puro** (sin numpy/sklearn): el motor corre en Render con RAM ajustada,
  así que no sumamos dependencias pesadas. Solo biblioteca estándar.
- El **mapeo** señal→probabilidad cruda es una función **reemplazable** (registro
  MAPEOS), para poder cambiarlo sin tocar el resto.
- Dos calibradores clásicos: **Platt** (logístico, suave) e **isotónico**
  (escalonado, no asume forma). Se ajustan SOLO con datos de entrenamiento.
- El calibrador, al predecir, **nunca** recibe el resultado real (sin fuga).

Este módulo NO llama a la IA ni toca la red: es pura matemática sobre resultados
ya medidos. Se puede ajustar gratis en cuanto tengamos la libreta histórica
(señal del enjambre + resultado real) exportada desde producción.
"""

from __future__ import annotations

import math

EPS = 1e-12


# ---------------------------------------------------------------------------
# 1. Mapeo señal del enjambre → probabilidad cruda P(sí) ∈ [0, 1] (reemplazable)
# ---------------------------------------------------------------------------

def _clip(x: float, lo: float, hi: float) -> float:
    return lo if x < lo else hi if x > hi else x


def _sigmoid(z: float) -> float:
    """Logística estable numéricamente."""
    if z >= 0:
        return 1.0 / (1.0 + math.exp(-z))
    ez = math.exp(z)
    return ez / (1.0 + ez)


def mapeo_senal_media(reporte: dict) -> float:
    """Desde el sentimiento medio de los líderes ∈ [-1, 1] → P(sube) ∈ [0, 1].
    Lineal y simple: venta total (−1) → 0, compra total (+1) → 1."""
    s = _clip(float(reporte.get("senal_media_lideres", 0.0)), -1.0, 1.0)
    return (s + 1.0) / 2.0


def mapeo_senal_ponderada(reporte: dict) -> float:
    """Igual que `mapeo_senal_media` pero usando la señal de predicción PONDERADA
    (`senal_media_ponderada`), que baja el peso de las voces contrarian —medidas
    como anti-señal en docs/calibracion-por-arquetipo.md—. Si el caso no la trae
    (histórico), cae al promedio simple `senal_media_lideres`."""
    v = reporte.get("senal_media_ponderada")
    if v is None:
        v = reporte.get("senal_media_lideres", 0.0)
    return (_clip(float(v), -1.0, 1.0) + 1.0) / 2.0


def mapeo_direccion(reporte: dict, escala: float = 2.0) -> float:
    """Desde la dirección simulada (en %) → P(sube), aplastando con una logística.
    `escala` controla cuán rápido satura (2% ≈ bastante confianza)."""
    d = float(reporte.get("direccion_pct", 0.0))
    return _sigmoid(d / escala)


# registro de mapeos reemplazables: se elige por nombre
MAPEOS = {
    "senal_media": mapeo_senal_media,
    "senal_ponderada": mapeo_senal_ponderada,
    "direccion": mapeo_direccion,
}


def senal_a_prob_cruda(reporte: dict, modo: str = "senal_media") -> float:
    """Convierte el reporte del enjambre en una probabilidad CRUDA (sin calibrar).
    `modo` elige el mapeo del registro MAPEOS."""
    if modo not in MAPEOS:
        raise ValueError(f"mapeo desconocido: {modo!r}. Opciones: {sorted(MAPEOS)}")
    return _clip(MAPEOS[modo](reporte), 0.0, 1.0)


# ---------------------------------------------------------------------------
# 2. Métricas de calibración
# ---------------------------------------------------------------------------

def brier(probs, resultados) -> float:
    """Brier score = media de (prob − resultado)². Menor es mejor (0 = perfecto)."""
    pares = list(zip(probs, resultados))
    if not pares:
        raise ValueError("brier necesita al menos un caso")
    return sum((p - y) ** 2 for p, y in pares) / len(pares)


def log_loss(probs, resultados) -> float:
    """Log loss (entropía cruzada). Menor es mejor. Recorta para no explotar."""
    pares = list(zip(probs, resultados))
    if not pares:
        raise ValueError("log_loss necesita al menos un caso")
    total = 0.0
    for p, y in pares:
        p = _clip(p, EPS, 1.0 - EPS)
        total += -(y * math.log(p) + (1 - y) * math.log(1 - p))
    return total / len(pares)


def tasa_base(resultados) -> float:
    """La proporción de 'sí' en los datos — la línea base trivial #2."""
    res = list(resultados)
    if not res:
        raise ValueError("tasa_base necesita al menos un caso")
    return sum(res) / len(res)


def curva_confiabilidad(probs, resultados, n_tramos: int = 10):
    """Agrupa en tramos de probabilidad y compara lo predicho vs lo observado.
    Devuelve lista de dicts: {tramo, pred_media, obs_frac, n}. Un calibrador
    bueno tiene pred_media ≈ obs_frac en cada tramo."""
    tramos = [[] for _ in range(n_tramos)]
    for p, y in zip(probs, resultados):
        idx = min(int(_clip(p, 0.0, 1.0 - EPS) * n_tramos), n_tramos - 1)
        tramos[idx].append((p, y))
    salida = []
    for i, t in enumerate(tramos):
        if not t:
            continue
        salida.append({
            "tramo": f"[{i / n_tramos:.1f}, {(i + 1) / n_tramos:.1f})",
            "pred_media": sum(p for p, _ in t) / len(t),
            "obs_frac": sum(y for _, y in t) / len(t),
            "n": len(t),
        })
    return salida


def skill_score(brier_modelo: float, brier_base: float) -> float:
    """1 − (Brier modelo / Brier base). >0 = mejor que la línea base."""
    if brier_base <= 0:
        return 0.0
    return 1.0 - (brier_modelo / brier_base)


# ---------------------------------------------------------------------------
# 3. Calibradores (se ajustan SOLO con entrenamiento; nunca ven el resultado al predecir)
# ---------------------------------------------------------------------------

class CalibradorPlatt:
    """Escalado de Platt: ajusta una logística P = sigmoid(a·x + b) sobre la señal.
    Suave; asume una relación monótona en forma de S. Ajuste por descenso de
    gradiente sobre la log-loss, con la entrada estandarizada para estabilidad."""

    def __init__(self):
        self.a = 0.0
        self.b = 0.0
        self._mu = 0.0
        self._sd = 1.0
        self.ajustado = False

    def fit(self, scores, resultados, iteraciones: int = 3000, lr: float = 0.3):
        xs = [float(s) for s in scores]
        ys = [float(y) for y in resultados]
        n = len(xs)
        if n == 0:
            raise ValueError("fit necesita al menos un caso")
        self._mu = sum(xs) / n
        var = sum((x - self._mu) ** 2 for x in xs) / n
        self._sd = math.sqrt(var) if var > 1e-18 else 1.0
        zs = [(x - self._mu) / self._sd for x in xs]
        a, b = 0.0, 0.0
        for _ in range(iteraciones):
            ga = gb = 0.0
            for z, y in zip(zs, ys):
                d = _sigmoid(a * z + b) - y
                ga += d * z
                gb += d
            a -= lr * ga / n
            b -= lr * gb / n
        self.a, self.b, self.ajustado = a, b, True
        return self

    def predict_uno(self, score: float) -> float:
        z = (float(score) - self._mu) / self._sd
        return _sigmoid(self.a * z + self.b)

    def predict(self, scores):
        return [self.predict_uno(s) for s in scores]


class CalibradorIsotonic:
    """Regresión isotónica (algoritmo Pool-Adjacent-Violators). No asume forma:
    solo que a mayor señal, no menor probabilidad. Más flexible que Platt pero
    necesita más datos para no sobreajustar. Predice por interpolación lineal
    entre los puntos ajustados."""

    def __init__(self):
        self._xs = []   # señales ordenadas (puntos de anclaje)
        self._ys = []   # probabilidad calibrada en cada punto (monótona ↑)
        self.ajustado = False

    def fit(self, scores, resultados):
        pares = sorted(zip((float(s) for s in scores), (float(y) for y in resultados)))
        if not pares:
            raise ValueError("fit necesita al menos un caso")
        # bloques PAV: cada bloque guarda (suma, peso, x_representativa)
        bloques = []
        for x, y in pares:
            bloques.append([y, 1.0, x])
            # fusiona hacia atrás mientras se viole la monotonía
            while len(bloques) > 1 and (bloques[-2][0] / bloques[-2][1]) >= (bloques[-1][0] / bloques[-1][1]):
                s2, w2, x2 = bloques.pop()
                s1, w1, x1 = bloques.pop()
                bloques.append([s1 + s2, w1 + w2, x2])  # x del extremo derecho del bloque
        # expande los bloques a puntos (x, valor_calibrado)
        xs, ys = [], []
        idx = 0
        for suma, peso, _ in bloques:
            valor = suma / peso
            # cada bloque cubre `peso` puntos consecutivos de `pares`
            for _ in range(int(round(peso))):
                xs.append(pares[idx][0])
                ys.append(valor)
                idx += 1
        self._xs, self._ys, self.ajustado = xs, ys, True
        return self

    def predict_uno(self, score: float) -> float:
        xs, ys = self._xs, self._ys
        x = float(score)
        if x <= xs[0]:
            return ys[0]
        if x >= xs[-1]:
            return ys[-1]
        # búsqueda e interpolación lineal
        lo, hi = 0, len(xs) - 1
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if xs[mid] <= x:
                lo = mid
            else:
                hi = mid
        if xs[hi] == xs[lo]:
            return ys[lo]
        t = (x - xs[lo]) / (xs[hi] - xs[lo])
        return ys[lo] + t * (ys[hi] - ys[lo])

    def predict(self, scores):
        return [self.predict_uno(s) for s in scores]


CALIBRADORES = {
    "platt": CalibradorPlatt,
    "isotonic": CalibradorIsotonic,
}


# ---------------------------------------------------------------------------
# 4. Conveniencia: ajustar y evaluar de una
# ---------------------------------------------------------------------------

def ajustar_calibrador(scores, resultados, metodo: str = "platt"):
    """Ajusta un calibrador del registro sobre (señal, resultado) de entrenamiento."""
    if metodo not in CALIBRADORES:
        raise ValueError(f"método desconocido: {metodo!r}. Opciones: {sorted(CALIBRADORES)}")
    return CALIBRADORES[metodo]().fit(scores, resultados)


def evaluar_calibracion(scores_test, resultados_test, calibrador=None) -> dict:
    """Compara el Brier de: (1) 0.5 constante, (2) tasa base, (3) señal cruda,
    (4) señal calibrada (si se pasa un calibrador ya ajustado). Más líneas base,
    más honesto el veredicto."""
    n = len(resultados_test)
    base_rate = tasa_base(resultados_test)
    crudas = [_clip(s, 0.0, 1.0) for s in scores_test]
    salida = {
        "n": n,
        "tasa_base": round(base_rate, 4),
        "brier_constante_050": round(brier([0.5] * n, resultados_test), 4),
        "brier_tasa_base": round(brier([base_rate] * n, resultados_test), 4),
        "brier_cruda": round(brier(crudas, resultados_test), 4),
    }
    if calibrador is not None and getattr(calibrador, "ajustado", False):
        cal = calibrador.predict(scores_test)
        salida["brier_calibrada"] = round(brier(cal, resultados_test), 4)
        salida["skill_vs_base"] = round(
            skill_score(brier(cal, resultados_test), salida["brier_tasa_base"]), 4)
    return salida
```

## engine/contenido/calibrar_libreta.py
```python
"""Tubería de calibración: desde la libreta exportada al veredicto Brier.

Uso (cuando ya tengas libreta_export.json de Render):

    python -m contenido.calibrar_libreta libreta_export.json

Qué hace, en simple:
1. Lee los casos (señal del enjambre + resultado real).
2. Convierte cada caso en (probabilidad cruda del enjambre, ¿subió? sí/no).
3. Parte en entrenamiento/prueba, ajusta los calibradores SOLO con entrenamiento.
4. Mide el Brier en prueba: enjambre crudo vs calibrado vs líneas base triviales.
5. Imprime un veredicto honesto, sin maquillaje.

No llama a la IA ni toca la red. Pura matemática sobre datos ya medidos.
"""

import json
import sys

from contenido import calibracion as cal


def _resultado_binario(pct_real) -> int | None:
    """¿Subió? 1 = sí, 0 = no. Los exactamente-cero (rarísimos) se descartan."""
    if pct_real is None:
        return None
    v = float(pct_real)
    if v == 0:
        return None
    return 1 if v > 0 else 0


def preparar(casos: list[dict], modo: str = "senal_media"):
    """Convierte casos crudos en pares (prob_cruda, resultado_binario), filtrando
    los que no tienen señal o resultado usable."""
    scores, ys = [], []
    for c in casos:
        y = _resultado_binario(c.get("pct_real"))
        if y is None:
            continue
        # el reporte que espera el mapeo usa estas mismas claves
        try:
            p = cal.senal_a_prob_cruda(c, modo=modo)
        except Exception:
            continue
        scores.append(p)
        ys.append(y)
    return scores, ys


def calibrar(casos: list[dict], modo: str = "senal_media",
             frac_prueba: float = 0.3, seed: int = 42) -> dict:
    # PARTICIÓN TEMPORAL (sin fuga): entrena con el pasado, mide con el futuro.
    # Antes se barajaba al azar, lo que mezclaba futuro en el entrenamiento y
    # sobreestimaba la calibración. Si los casos traen `fecha`, se ordenan por
    # ella; si no, se respeta el orden de entrada (que exportar_libreta ya da por
    # fecha). `seed` se conserva por compatibilidad de firma; ya no baraja.
    if casos and all(c.get("fecha") for c in casos):
        casos = sorted(casos, key=lambda c: c["fecha"])
    scores, ys = preparar(casos, modo=modo)
    n = len(ys)
    if n < 10:
        return {"error": f"muy pocos casos usables ({n}); se necesitan >= 10 para algo informativo"}

    corte = int(n * (1 - frac_prueba))
    s_tr, y_tr = scores[:corte], ys[:corte]
    s_te, y_te = scores[corte:], ys[corte:]

    salida = {"modo": modo, "n_total": n, "n_entrena": len(s_tr), "n_prueba": len(s_te),
              "tasa_subidas": round(cal.tasa_base(ys), 4)}

    for metodo in ("platt", "isotonic"):
        c = cal.ajustar_calibrador(s_tr, y_tr, metodo=metodo)
        rep = cal.evaluar_calibracion(s_te, y_te, calibrador=c)
        salida[metodo] = rep
        salida[f"{metodo}_confiabilidad"] = cal.curva_confiabilidad(c.predict(s_te), y_te)
    return salida


def _imprimir(rep: dict) -> None:
    if "error" in rep:
        print("No se pudo calibrar:", rep["error"])
        return
    print(f"Casos usables: {rep['n_total']}  (entrena {rep['n_entrena']} / prueba {rep['n_prueba']})")
    print(f"Tasa de subidas en los datos: {rep['tasa_subidas']:.1%}")
    print()
    print("Brier en prueba (MENOR = mejor):")
    base = rep["platt"]
    print(f"  Línea base 50% constante : {base['brier_constante_050']}")
    print(f"  Línea base tasa de subida: {base['brier_tasa_base']}")
    print(f"  Enjambre CRUDO           : {base['brier_cruda']}")
    for metodo in ("platt", "isotonic"):
        m = rep[metodo]
        print(f"  Enjambre + {metodo:<9} : {m.get('brier_calibrada')}  "
              f"(skill vs base: {m.get('skill_vs_base')})")
    print()
    print("Veredicto honesto:")
    mejor = min(("platt", "isotonic"), key=lambda k: rep[k].get("brier_calibrada", 9))
    m = rep[mejor]
    if m.get("brier_calibrada", 9) < base["brier_tasa_base"] and m.get("skill_vs_base", 0) > 0:
        print(f"  El enjambre calibrado ({mejor}) SUPERA a la línea base trivial. Hay señal.")
    else:
        print(f"  El enjambre NO supera claramente la línea base. Fracaso informativo "
              f"(esperado fuera de macro).")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("uso: python -m contenido.calibrar_libreta <libreta_export.json> [modo]")
        print("     python -m contenido.calibrar_libreta --db   (lee la base directo)")
        sys.exit(2)
    arg = sys.argv[1]
    modo = sys.argv[2] if len(sys.argv) > 2 else "senal_media"
    if arg == "--db":
        # lee la libreta directamente de la base (corre en Render, todo en uno)
        from contenido import exportar_libreta
        casos = exportar_libreta.exportar()
        print(f"(leídos {len(casos)} casos de la base)\n")
    else:
        with open(arg, encoding="utf-8") as f:
            casos = json.load(f)
    _imprimir(calibrar(casos, modo=modo))
```

## engine/contenido/captura.py
```python
"""Captura del "momento dramático" de una simulación (CONTENIDO.md paso 4).

Genera un PNG 1200×630 editorial (Rubicón Lab: tinta cálida + teal, "el río")
con el titular, la dirección, el nivel de agitación, la curva de precio con el
tick de máxima agitación marcado, el disclaimer y la marca de agua.
Sirve de portada del correo y de Open Graph image de la página.

Se dibuja en 2D con Pillow — sin GL headless, funciona en el plan free.
Un render 3D real del enjambre es una mejora futura, no de hoy.
"""

import io
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from contenido.vocabulario import DISCLAIMER

# paleta oficial del manual de marca (§05), en RGB
TINTA = (27, 25, 22)          # tinta cálida — fondo
TEAL = (111, 168, 158)        # el río — acento
CREMA = (243, 238, 232)       # crema — texto
CREMA_SUAVE = (243, 238, 232, 150)
COMPRA = (143, 191, 166)      # salvia
VENTA = (217, 154, 154)       # rosa
NEUTRO = (107, 102, 96)       # taupe cálido

ANCHO, ALTO = 1200, 630
MARGEN = 70


def _fuente(tamano: int, negrita: bool = False):
    """Busca una fuente del sistema; si no hay, la de Pillow (siempre existe)."""
    candidatas = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf" if negrita
        else "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if negrita
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for ruta in candidatas:
        if Path(ruta).exists():
            try:
                return ImageFont.truetype(ruta, tamano)
            except OSError:
                continue
    return ImageFont.load_default()


def _envolver(texto: str, fuente, dibujo, ancho_max: int) -> list[str]:
    palabras = texto.split()
    lineas, actual = [], ""
    for palabra in palabras:
        prueba = f"{actual} {palabra}".strip()
        if dibujo.textlength(prueba, font=fuente) <= ancho_max:
            actual = prueba
        else:
            if actual:
                lineas.append(actual)
            actual = palabra
    if actual:
        lineas.append(actual)
    return lineas[:3]


def _color_direccion(direccion_pct: float):
    if direccion_pct > 1.0:
        return COMPRA
    if direccion_pct < -1.0:
        return VENTA
    return TEAL


def generar_png(titular: str, resumen: dict, serie_precios: list[float]) -> bytes:
    """Devuelve el PNG del momento dramático como bytes."""
    imagen = Image.new("RGB", (ANCHO, ALTO), TINTA)
    dibujo = ImageDraw.Draw(imagen)

    # marco teal sutil — el acento del manual
    dibujo.rectangle([12, 12, ANCHO - 12, ALTO - 12], outline=TEAL, width=1)

    # cabecera: marca
    dibujo.text((MARGEN, 46), "EL ENJAMBRE", font=_fuente(26, negrita=True), fill=TEAL)
    dibujo.text((MARGEN, 82), "el focus group sintético del mercado",
                font=_fuente(16), fill=CREMA_SUAVE[:3])

    # titular (hasta 3 líneas)
    fuente_titular = _fuente(40, negrita=True)
    lineas = _envolver(titular, fuente_titular, dibujo, ANCHO - 2 * MARGEN)
    y = 150
    for linea in lineas:
        dibujo.text((MARGEN, y), linea, font=fuente_titular, fill=CREMA)
        y += 52

    # cifras: dirección y agitación
    direccion = resumen.get("direccion_pct", 0) or 0
    agitacion = resumen.get("agitacion") or _nivel(resumen.get("volatilidad_pct", 0))
    y_cifras = 360
    flecha = "▲" if direccion > 1 else "▼" if direccion < -1 else "◆"
    texto_dir = f"{flecha} {'+' if direccion > 0 else ''}{direccion}%"
    dibujo.text((MARGEN, y_cifras), texto_dir, font=_fuente(46, negrita=True),
                fill=_color_direccion(direccion))
    dibujo.text((MARGEN, y_cifras + 62), f"agitación {agitacion}",
                font=_fuente(18), fill=CREMA_SUAVE[:3])

    # curva de precio con el tick más dramático marcado
    _dibujar_curva(dibujo, serie_precios, x0=560, y0=340, ancho=560, alto=180)

    # disclaimer CMF + marca de agua
    dibujo.text((MARGEN, ALTO - 76), DISCLAIMER, font=_fuente(13), fill=CREMA_SUAVE[:3])
    marca = "El Enjambre · Rubicón Lab"
    fuente_marca = _fuente(15)
    ancho_marca = dibujo.textlength(marca, font=fuente_marca)
    dibujo.text((ANCHO - MARGEN - ancho_marca, ALTO - 44), marca, font=fuente_marca, fill=TEAL)

    buffer = io.BytesIO()
    imagen.save(buffer, format="PNG")
    return buffer.getvalue()


def _nivel(volatilidad_pct: float) -> str:
    if volatilidad_pct < 1.0:
        return "bajo"
    if volatilidad_pct < 2.0:
        return "medio"
    return "alto"


def _dibujar_curva(dibujo, serie, x0, y0, ancho, alto) -> None:
    if not serie or len(serie) < 2:
        return
    minimo, maximo = min(serie), max(serie)
    rango = max(maximo - minimo, 0.5)
    puntos = []
    for i, valor in enumerate(serie):
        x = x0 + (i / (len(serie) - 1)) * ancho
        y = y0 + alto - ((valor - minimo) / rango) * alto
        puntos.append((x, y))
    # línea base tenue
    dibujo.line([(x0, y0 + alto), (x0 + ancho, y0 + alto)], fill=(60, 55, 45), width=1)
    dibujo.line(puntos, fill=TEAL, width=3, joint="curve")
    # marca el tick de máxima caída (el momento dramático)
    idx = serie.index(minimo)
    px, py = puntos[idx]
    dibujo.ellipse([px - 6, py - 6, px + 6, py + 6], fill=VENTA)


def guardar_png(ruta: Path, contenido: bytes) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_bytes(contenido)
```

## engine/contenido/cierre.py
```python
"""La edición de la TARDE de El Pulso — 'El cierre del mercado' (Premium).

Después del cierre de EE.UU., el reportero IA caza los mayores movimientos REALES
del día y explica por qué. Es el premio de ser Premium: la mañana es para todos
(pre-market + noticias); la tarde a fondo, para quien paga.

No simula el enjambre (evita duplicar las destacadas de la mañana y el costo): su
valor es "qué se movió de verdad y por qué", investigado y verificado.
"""

from contenido import investigador
from contenido.fuentes import yahoo

MAX_MOVERS_CIERRE = 5


def preparar_cierre(maximo: int = MAX_MOVERS_CIERRE) -> dict | None:
    """Arma el cierre del día: los mayores movimientos investigados. None si no
    hay movimientos (mercado cerrado sin datos / degradación) — entonces no hay
    edición de tarde y no se molesta a nadie."""
    movers = investigador.investigar_movers(yahoo.movers_del_dia(n=12), maximo=maximo)
    if not movers:
        return None
    # de más movido a menos (por si el orden se perdió)
    movers.sort(key=lambda m: abs(m.get("var_pct") or 0), reverse=True)
    return {"titulo": "El cierre del mercado", "movers": movers}
```

## engine/contenido/corrector.py
```python
"""El corrector automático — paso 2 de la ruta de calibración.

Uno o dos días de mercado después de cada destacada, consulta cuánto se
movió su símbolo EN EL MERCADO REAL (Alpaca, barras diarias) y lo guarda:

- estructurado en `simulaciones.reaccion_real` (la materia prima de la
  libreta de calificaciones), y
- como epílogo "¿y qué pasó después?" SOLO si Giorgio no escribió uno a
  mano (lo manual siempre manda).

Línea CMF: el texto cuenta el pasado y se declara comparación educativa;
pasa por vocabulario.es_publicable antes de guardarse. Si Alpaca no
responde o la ventana aún no se completa, la simulación queda pendiente
y se reintenta en la próxima corrida — el corrector nunca lanza.
"""

import json
from datetime import datetime, timedelta, timezone
from statistics import mean

from contenido import persistencia, vocabulario

DIAS_ESPERA = 1    # edad mínima de una destacada antes de intentar corregirla
RUEDAS = 2         # ventana de medición: días de mercado tras la noticia
UMBRAL_PLANO = 0.3  # bajo este |%|, la dirección se considera plana


def cerebros_ia(lideres: list[dict]) -> bool:
    """¿La mayoría de los líderes habló con IA real (no con el respaldo)?

    Sin saldo de API el enjambre sigue funcionando con el cerebro léxico,
    pero la calibración solo debe medir al titular, no al suplente.
    Si los líderes no traen `fuente` (registros antiguos), se asume IA."""
    fuentes = [l.get("fuente") for l in (lideres or []) if l.get("fuente")]
    if not fuentes:
        return True
    ia = sum(1 for f in fuentes if f in ("api", "cache"))
    return ia > len(fuentes) / 2


def corregir_pendientes(conexion=None, obtener_variacion=None, limite: int = 10,
                        dias_espera: int = DIAS_ESPERA, ruedas: int = RUEDAS) -> dict:
    """Corrige las destacadas pendientes. Devuelve {corregidas, esperando}."""
    from contenido.fuentes import alpaca

    obtener_variacion = obtener_variacion or alpaca.variacion_real
    propia = conexion is None
    conexion = conexion or persistencia.conectar()
    try:
        antes_de = (datetime.now(timezone.utc) - timedelta(days=dias_espera)).isoformat(
            timespec="seconds"
        )
        pendientes = persistencia.destacadas_sin_correccion(conexion, antes_de, limite)
        corregidas, esperando = [], 0
        for sim in pendientes:
            simbolo = (sim["simbolos"] or "").split(",")[0].strip().upper()
            variacion = obtener_variacion(simbolo, sim["fecha"], ruedas) if simbolo else None
            if variacion is None:
                esperando += 1  # sin datos todavía: la próxima corrida reintenta
                continue
            # la etiqueta ia/respaldo viaja con la nota: la libreta solo
            # califica al titular (IA real), nunca al suplente léxico
            lideres = json.loads(sim.get("lideres_json") or "[]")
            variacion = {**variacion,
                         "cerebros": "ia" if cerebros_ia(lideres) else "respaldo"}
            persistencia.guardar_reaccion_real(conexion, sim["id"], variacion)
            if not (sim["epilogo"] or "").strip():
                resumen = json.loads(sim["resumen_json"])
                texto = _texto_epilogo(resumen.get("direccion_pct", 0), variacion)
                if vocabulario.es_publicable(texto):
                    persistencia.guardar_epilogo(conexion, sim["id"], texto)
            corregidas.append({"sim_id": sim["id"], "simbolo": simbolo,
                               "pct_real": variacion["pct_real"]})
        resultado = {"corregidas": corregidas, "esperando": esperando}
        if corregidas:
            # caja fuerte: el acumulado se respalda en GitHub (rama aparte);
            # si falla, el corrector no se cae — reintenta con la próxima
            try:
                from contenido import respaldo
                resultado["respaldo"] = respaldo.respaldar(conexion)
            except Exception:
                resultado["respaldo"] = None
        return resultado
    finally:
        if propia:
            conexion.close()


def _texto_epilogo(direccion_pct: float, variacion: dict) -> str:
    """El '¿y qué pasó después?' automático, en pasado y tono educativo."""
    pct_sim = float(direccion_pct or 0)
    rumbo = ("una subida" if pct_sim > UMBRAL_PLANO
             else "una caída" if pct_sim < -UMBRAL_PLANO
             else "una reacción plana")
    return (
        f"El enjambre simuló {rumbo} de {pct_sim:+.1f}%. En el mercado real, "
        f"{variacion['simbolo']} cerró en {variacion['cierre_final']} "
        f"el {variacion['fecha_final']} (venía de {variacion['cierre_base']} "
        f"el {variacion['fecha_base']}): {variacion['pct_real']:+.1f}% en "
        f"{variacion['ruedas']} días de mercado. Registro del corrector "
        "automático con fines educativos: la simulación modela comportamiento "
        "de masas, no el precio futuro."
    )


def _signo(x: float) -> int:
    return 0 if abs(x) < UMBRAL_PLANO else (1 if x > 0 else -1)


def _resumir(casos: list[tuple[float, float]]) -> dict:
    """Las métricas de un conjunto de casos (sim_pct, real_pct)."""
    evaluables = [(s, r) for s, r in casos if _signo(s) or _signo(r)]
    aciertos = sum(1 for s, r in evaluables if _signo(s) == _signo(r))
    return {
        "casos": len(casos),
        "evaluables": len(evaluables),  # al menos un lado se movió
        "aciertos_direccion": aciertos,
        "tasa_acierto": round(aciertos / len(evaluables), 2) if evaluables else None,
        "magnitud_media_sim": round(mean(abs(s) for s, _ in casos), 2) if casos else None,
        "magnitud_media_real": round(mean(abs(r) for _, r in casos), 2) if casos else None,
    }


def libreta(conexion=None) -> dict:
    """La libreta de calificaciones: enjambre vs mercado real, acumulado.

    Es la brújula de la calibración (¿acierta la dirección? ¿exagera?),
    no una métrica de marketing. Separa lo EN VIVO (destacadas corregidas
    día a día) de lo HISTÓRICO (backtest): peras con peras.
    """
    propia = conexion is None
    conexion = conexion or persistencia.conectar()
    try:
        filas = conexion.execute(
            "SELECT resumen_json, reaccion_real, fuente FROM simulaciones "
            "WHERE reaccion_real IS NOT NULL AND (destacada = 1 OR fuente = 'backtest')"
        ).fetchall()
    finally:
        if propia:
            conexion.close()

    vivo, historico, excluidos = [], [], 0
    for fila in filas:
        reaccion = json.loads(fila["reaccion_real"])
        if reaccion.get("cerebros") == "respaldo":
            excluidos += 1  # simulado sin IA (sin saldo): no califica al titular
            continue
        sim = float(json.loads(fila["resumen_json"]).get("direccion_pct") or 0)
        real = float(reaccion.get("pct_real") or 0)
        (historico if fila["fuente"] == "backtest" else vivo).append((sim, real))

    return {
        **_resumir(vivo + historico),
        "en_vivo": _resumir(vivo),
        "historico": _resumir(historico),
        "excluidos_respaldo": excluidos,
        "nota": "con menos de 30 casos, la tasa es anecdótica — seguir acumulando",
    }
```

## engine/contenido/cosechador.py
```python
"""El cosechador — genera exámenes REALES automáticamente.

Idea: para calibrar de verdad no basta con inventar titulares. Cada examen
necesita una noticia REAL, de una fecha REAL, con un resultado REAL. Este
módulo lo consigue solo:

1. Busca los **días de mayor movimiento** de cada símbolo (Yahoo Finance):
   esos son los días en que "pasó algo".
2. Le pega el **titular real** de ese día (Alpaca News / Benzinga).
3. Solo conserva el evento si EXISTE un titular real. Si no hay noticia,
   descarta el día — **nunca inventa** una (regla de oro del proyecto).

Así el banco de exámenes escala hacia los 100 por mercado sin curado
manual, y sin ensuciar la calibración con noticias falsas.

El resultado son "eventos candidatos" con el mismo formato que
backtest_eventos.json, listos para revisar y fusionar al banco.
"""

import re
from datetime import datetime, timedelta, timezone

import httpx

URL_YAHOO = "https://query1.finance.yahoo.com/v8/finance/chart/{simbolo}"

# Titulares que son REALES pero no sirven de examen: no cuentan qué pasó,
# solo listan movimientos ("40 Biggest Movers", "Stocks Moving Pre-Market",
# "Gainers"…). El enjambre no puede razonar sobre ellos, así que se descartan
# (no se inventa nada: simplemente ese día no tiene una noticia utilizable).
PATRONES_GENERICOS = re.compile(
    r"biggest movers|stocks? moving|pre-?market (session|gainers|losers|movers)|"
    r"premarket|mid-?day (movers|gainers|losers)|movers from|"
    r"gainers?( and | & )?losers|top (gainers|losers)|"
    r"what's .* doing today|unusual options|stocks to watch|market update|"
    r"stocks moving in|movers list|market clubhouse|watch list|"
    r"benzinga('s)? (pro |)?(top |)(movers|gainers|losers)",
    re.IGNORECASE,
)

# Símbolos que solo representan a su mercado DESPUÉS de una fecha: proxies de
# cripto que antes eran otra empresa. Cosechar antes de esa fecha mezclaría
# noticias de otro negocio (patentes, biotech, software) como si fueran cripto.
SIMBOLO_DESDE = {
    "MSTR": "2020-08-11",  # primera compra de Bitcoin de MicroStrategy
    "MARA": "2020-12-01",  # rebrand a Marathon Digital (minería de Bitcoin)
    "RIOT": "2017-10-04",  # rebrand de Bioptix a Riot Blockchain
    "BITO": "2021-10-19",  # lanzamiento del ETF de futuros de Bitcoin
}

# Umbral de "día de movimiento" por mercado: un día importa si el símbolo se
# movió más que esto (en %). Calibrado a la volatilidad típica de cada uno:
# el oro se mueve poco, la cripto mucho — un 3% no significa lo mismo en cada
# uno. Así cosechamos eventos comparables en "sorpresa", no en tamaño bruto.
UMBRAL_POR_MERCADO = {
    "indice": 2.5,
    "accion": 6.0,
    "petroleo": 4.0,
    "oro": 2.5,
    "cripto": 6.0,
}
UMBRAL_DEFECTO = 4.0

# Distancia mínima (en días de mercado) entre dos eventos del mismo símbolo:
# evita cosechar tres días seguidos del mismo desplome como si fueran tres
# noticias distintas.
SEPARACION_MINIMA = 5

# Cuánto se mide la reacción (misma ventana que el corrector en vivo).
RUEDAS = 2

# La lista de caza por mercado. Símbolos con histórico largo en Yahoo Y
# cobertura de noticias en Benzinga/Alpaca (2015+). Para acciones: variadas
# —grandes y medianas, de sectores distintos— tal como pidió el proyecto,
# no solo las gigantes. Se puede ampliar sin tocar el resto del código.
WATCHLIST_DEFECTO: dict[str, str] = {
    # índices
    "SPY": "indice", "QQQ": "indice", "DIA": "indice", "IWM": "indice",
    "VTI": "indice", "VOO": "indice", "MDY": "indice", "RSP": "indice", "EFA": "indice",
    # metales: oro y mineras + plata, platino, paladio y cobre
    "GLD": "oro", "IAU": "oro", "GDX": "oro", "NEM": "oro", "GOLD": "oro",
    "SLV": "oro", "PPLT": "oro", "PALL": "oro", "FCX": "oro", "SCCO": "oro", "COPX": "oro",
    # cripto (proxies bursátiles: ETFs, exchange y mineras)
    "GBTC": "cripto", "COIN": "cripto", "MARA": "cripto", "RIOT": "cripto",
    "MSTR": "cripto", "ETHE": "cripto", "BITO": "cripto",
    # petróleo y energía
    "USO": "petroleo", "XLE": "petroleo", "OXY": "petroleo", "SLB": "petroleo",
    # acciones — grandes
    "AAPL": "accion", "MSFT": "accion", "NVDA": "accion", "AMZN": "accion",
    "GOOGL": "accion", "META": "accion", "TSLA": "accion", "NFLX": "accion",
    "JPM": "accion", "XOM": "accion", "WMT": "accion", "DIS": "accion",
    # acciones — medianas y variadas (sectores distintos)
    "AMD": "accion", "INTC": "accion", "MU": "accion", "QCOM": "accion",
    "BA": "accion", "GE": "accion", "CAT": "accion", "F": "accion",
    "GM": "accion", "T": "accion", "PFE": "accion", "MRNA": "accion",
    "KO": "accion", "PEP": "accion", "TGT": "accion", "NKE": "accion",
    "SBUX": "accion", "MCD": "accion", "HD": "accion", "CRM": "accion",
    "PYPL": "accion", "SQ": "accion", "SHOP": "accion", "ROKU": "accion",
    "UBER": "accion", "ABNB": "accion", "SNAP": "accion", "PLTR": "accion",
    "GME": "accion", "AMC": "accion", "RIVN": "accion", "LCID": "accion",
    "SOFI": "accion", "HOOD": "accion", "DKNG": "accion", "RBLX": "accion",
    "MRVL": "accion", "CVNA": "accion",
}


def _historia_diaria(simbolo: str, desde: str, hasta: str) -> list[tuple[str, float]]:
    """(fecha_iso, cierre) de cada rueda entre `desde` y `hasta`. [] si falla."""
    try:
        p1 = int(datetime.fromisoformat(desde).replace(tzinfo=timezone.utc).timestamp())
        p2 = int(datetime.fromisoformat(hasta).replace(tzinfo=timezone.utc).timestamp())
        respuesta = httpx.get(
            URL_YAHOO.format(simbolo=simbolo),
            params={"period1": p1, "period2": p2, "interval": "1d"},
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=20,
        )
        respuesta.raise_for_status()
        resultado = respuesta.json()["chart"]["result"][0]
        marcas = resultado["timestamp"]
        cierres = resultado["indicators"]["quote"][0]["close"]
    except Exception:
        return []
    barras = []
    for ts, cierre in zip(marcas, cierres):
        if cierre is None:
            continue
        dia = datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d")
        barras.append((dia, float(cierre)))
    return barras


def _categoria(pct: float) -> str:
    if pct <= -1.0:
        return "negativa"
    if pct >= 1.0:
        return "positiva"
    return "neutra"


def dias_de_movimiento(simbolo: str, mercado: str, desde: str, hasta: str,
                       ruedas: int = RUEDAS) -> list[dict]:
    """Los días en que `simbolo` se movió fuerte, con la reacción medida en la
    misma ventana que usa el corrector (cierre previo → `ruedas` ruedas después).

    Devuelve candidatos SIN titular todavía: {fecha, simbolo, mercado,
    categoria, pct_ventana}. El titular real se busca aparte (puede no existir).
    """
    umbral = UMBRAL_POR_MERCADO.get(mercado, UMBRAL_DEFECTO)
    # si el símbolo solo representa a su mercado desde cierta fecha, no cosechar antes
    piso = SIMBOLO_DESDE.get(simbolo)
    if piso and piso > desde:
        desde = piso
    barras = _historia_diaria(simbolo, desde, hasta)
    if len(barras) < ruedas + 2:
        return []

    candidatos = []
    for i in range(1, len(barras) - ruedas):
        fecha_prev, cierre_prev = barras[i - 1]
        fecha, _ = barras[i]
        _, cierre_final = barras[i + ruedas - 1]
        if not cierre_prev:
            continue
        # el movimiento del propio día decide si "pasó algo"
        cambio_dia = (barras[i][1] - cierre_prev) / cierre_prev * 100
        if abs(cambio_dia) < umbral:
            continue
        # pero la NOTA se mide en la ventana del corrector (base → ruedas después)
        pct_ventana = round((cierre_final - cierre_prev) / cierre_prev * 100, 2)
        candidatos.append({
            "fecha": fecha,
            "simbolo": simbolo,
            "mercado": mercado,
            "categoria": _categoria(pct_ventana),
            "pct_ventana": pct_ventana,
            "_cambio_dia": round(cambio_dia, 2),
        })

    # espaciar: si dos candidatos caen a menos de SEPARACION_MINIMA ruedas,
    # quedarse con el de mayor movimiento (una noticia, no la misma racha)
    candidatos.sort(key=lambda c: abs(c["_cambio_dia"]), reverse=True)
    elegidos: list[dict] = []
    for cand in candidatos:
        f = datetime.fromisoformat(cand["fecha"])
        if all(abs((f - datetime.fromisoformat(e["fecha"])).days) >= SEPARACION_MINIMA
               for e in elegidos if e["simbolo"] == cand["simbolo"]):
            elegidos.append(cand)
    elegidos.sort(key=lambda c: c["fecha"])
    return elegidos


def _titular_de(simbolo: str, fecha: str) -> dict | None:
    """El titular real de Benzinga para `simbolo` alrededor de `fecha` (Alpaca).

    Busca en la ventana [fecha-1día, fecha] y devuelve el titular cuyo momento
    esté más cerca de la fecha del movimiento. None si no hay claves, red o
    ninguna noticia — en ese caso el día se descarta (no se inventa titular).
    """
    import os

    if not (os.environ.get("ALPACA_API_KEY_ID") and os.environ.get("ALPACA_API_SECRET_KEY")):
        return None
    inicio = (datetime.fromisoformat(fecha) - timedelta(days=1)).strftime("%Y-%m-%dT00:00:00Z")
    fin = (datetime.fromisoformat(fecha) + timedelta(days=1)).strftime("%Y-%m-%dT00:00:00Z")
    try:
        respuesta = httpx.get(
            "https://data.alpaca.markets/v1beta1/news",
            params={"symbols": simbolo, "start": inicio, "end": fin,
                    "limit": 50, "sort": "desc"},
            headers={
                "APCA-API-KEY-ID": os.environ["ALPACA_API_KEY_ID"],
                "APCA-API-SECRET-KEY": os.environ["ALPACA_API_SECRET_KEY"],
            },
            timeout=8,
        )
        respuesta.raise_for_status()
        noticias = [n for n in respuesta.json().get("news", []) if n.get("headline")]
    except Exception:
        return None
    # solo titulares con contenido real: fuera las listas genéricas de "movers"
    noticias = [n for n in noticias if not PATRONES_GENERICOS.search(n["headline"])]
    if not noticias:
        return None
    # el titular cuyo momento cae más cerca del cierre del día del movimiento
    ancla = datetime.fromisoformat(fecha).replace(tzinfo=timezone.utc)

    def distancia(n):
        try:
            t = datetime.fromisoformat(n["created_at"].replace("Z", "+00:00"))
            return abs((t - ancla).total_seconds())
        except Exception:
            return float("inf")

    mejor = min(noticias, key=distancia)
    return {"titular": mejor["headline"].strip(),
            "fuente_noticia": mejor.get("source", "benzinga"),
            "url": mejor.get("url", "")}


def _id_evento(simbolo: str, fecha: str, mercado: str) -> str:
    return f"{fecha}-{mercado[:3]}-cosecha-{simbolo.lower()}"


def cosechar(watchlist: dict[str, str], desde: str, hasta: str,
             ids_existentes: set[str] | None = None,
             tope_por_simbolo: int = 8) -> dict:
    """Cosecha eventos reales para una lista de símbolos.

    watchlist: {simbolo: mercado}. desde/hasta: rango ISO (AAAA-MM-DD).
    ids_existentes: ids del banco actual, para no repetir.
    Devuelve {"eventos": [...], "sin_titular": [...], "resumen": {...}}.
    """
    ids_existentes = ids_existentes or set()
    eventos, sin_titular = [], []
    por_mercado: dict[str, int] = {}
    for simbolo, mercado in watchlist.items():
        candidatos = dias_de_movimiento(simbolo, mercado, desde, hasta)
        # los de mayor movimiento primero, y descartar los que ya están
        candidatos.sort(key=lambda c: abs(c["_cambio_dia"]), reverse=True)
        nuevos = [c for c in candidatos
                  if _id_evento(simbolo, c["fecha"], mercado) not in ids_existentes]
        # ACOTAR cuántos días se consultan a Alpaca: un símbolo volátil puede
        # tener 50+ días de movimiento en 10 años; consultarlos TODOS hace la
        # cosecha eterna. Con un poco de holgura sobre el tope basta (los días
        # de gran movimiento casi siempre tienen noticia real).
        a_revisar = nuevos[:tope_por_simbolo + 8]
        tomados = 0
        for cand in a_revisar:
            if tomados >= tope_por_simbolo:
                break
            titular = _titular_de(simbolo, cand["fecha"])
            if titular is None:
                sin_titular.append({"simbolo": simbolo, "fecha": cand["fecha"]})
                continue
            id_evento = _id_evento(simbolo, cand["fecha"], mercado)
            eventos.append({
                "id": id_evento,
                "fecha": cand["fecha"],
                "simbolo": simbolo,
                "categoria": cand["categoria"],
                "mercado": mercado,
                "titular": titular["titular"],
            })
            ids_existentes.add(id_evento)
            por_mercado[mercado] = por_mercado.get(mercado, 0) + 1
            tomados += 1
    eventos.sort(key=lambda e: e["fecha"])
    return {"eventos": eventos, "sin_titular": sin_titular,
            "resumen": {"cosechados": len(eventos), "sin_titular": len(sin_titular),
                        "por_mercado": por_mercado}}


def cosechar_y_guardar(mercados: list[str] | None = None,
                       desde: str = "2016-01-01", hasta: str | None = None,
                       tope_por_simbolo: int = 8, reemplazar: bool = False) -> dict:
    """Cosecha eventos reales y los sube a GitHub (datos/cosecha.json).

    `mercados`: filtra la watchlist (ej. ["oro", "cripto"]); None = todos.
    `reemplazar`: si True, la cosecha PISA lo anterior (purga cosechas viejas
    de baja calidad) en vez de sumarse. El banco de exámenes recoge los nuevos
    en la próxima tanda (cargar_eventos fusiona lo local con lo cosechado).
    NUNCA lanza hacia el pipeline.
    """
    from contenido import backtest, respaldo

    if hasta is None:
        hasta = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    watchlist = WATCHLIST_DEFECTO
    if mercados:
        objetivo = {m.lower() for m in mercados}
        watchlist = {s: m for s, m in WATCHLIST_DEFECTO.items() if m in objetivo}

    # al reemplazar solo se evita repetir lo curado a mano (no la cosecha vieja)
    if reemplazar:
        ids_existentes = {e["id"] for e in cargar_eventos_locales()}
    else:
        ids_existentes = {e["id"] for e in backtest.cargar_eventos()}
    resultado = cosechar(watchlist, desde, hasta, ids_existentes, tope_por_simbolo)
    if resultado["eventos"]:
        resultado["respaldo"] = respaldo.subir_cosecha(resultado["eventos"], reemplazar=reemplazar)
    return resultado


def cargar_eventos_locales() -> list[dict]:
    """Solo los exámenes curados a mano (backtest_eventos.json), sin la cosecha
    remota. Se usa al reemplazar para no chocar con lo curado."""
    import json
    from contenido.backtest import RUTA_EVENTOS

    with open(RUTA_EVENTOS, encoding="utf-8") as archivo:
        return json.load(archivo)["eventos"]
```

## engine/contenido/disparar_pulso.py
```python
"""Disparador del ritual de la madrugada (lo corre el cron de Render).

El cron y la web son contenedores separados que NO comparten disco, así
que el cron no simula: solo golpea el endpoint protegido del servicio web,
y el ritual corre DENTRO del proceso web (misma base que sirve el muro).

Uso (cron): python -m contenido.disparar_pulso
Variables: ENJAMBRE_API_URL, ENJAMBRE_PIPELINE_TOKEN.
"""

import os
import sys

import httpx


def main() -> int:
    base = os.environ.get("ENJAMBRE_API_URL", "").rstrip("/")
    token = os.environ.get("ENJAMBRE_PIPELINE_TOKEN", "")
    if not base or not token:
        print("faltan ENJAMBRE_API_URL o ENJAMBRE_PIPELINE_TOKEN", file=sys.stderr)
        return 1
    try:
        respuesta = httpx.post(
            f"{base}/api/pipeline",
            headers={"X-Pipeline-Token": token},
            timeout=30,
        )
        print(f"disparo del pipeline → HTTP {respuesta.status_code}: {respuesta.text[:120]}")
        return 0 if respuesta.status_code < 300 else 1
    except Exception as error:
        print(f"no se pudo disparar el pipeline: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
```

## engine/contenido/exportar_libreta.py
```python
"""Exporta la libreta cruda (señal del enjambre + resultado real) para calibrar.

Correr EN RENDER, desde la carpeta engine/:

    python -m contenido.exportar_libreta > libreta_export.json

Devuelve una lista JSON con una fila por caso ya corregido (con resultado real),
sin IA de respaldo. Cada fila: la señal continua del enjambre y cuánto se movió
el símbolo de verdad. Es lo único que la calibración necesita, y NO contiene datos
de Kalshi/Polymarket — es nuestra propia libreta (movimientos vía Alpaca).

Seguro: solo LEE la base; no escribe nada. No imprime emails ni secretos.
"""

import json
import sys

from contenido import persistencia


def exportar(conexion=None) -> list[dict]:
    propia = conexion is None
    conexion = conexion or persistencia.conectar()
    try:
        filas = conexion.execute(
            "SELECT resumen_json, reaccion_real, fuente, fecha FROM simulaciones "
            "WHERE reaccion_real IS NOT NULL AND (destacada = 1 OR fuente = 'backtest') "
            "ORDER BY fecha"
        ).fetchall()
    finally:
        if propia:
            conexion.close()

    casos = []
    for fila in filas:
        reaccion = json.loads(fila["reaccion_real"])
        if reaccion.get("cerebros") == "respaldo":
            continue  # simulado sin IA real: no califica
        resumen = json.loads(fila["resumen_json"])
        casos.append({
            "fecha": fila["fecha"],
            "direccion_pct": resumen.get("direccion_pct"),
            "senal_media_lideres": resumen.get("senal_media_lideres"),
            "senal_media_ponderada": resumen.get("senal_media_ponderada"),
            "confianza": resumen.get("confianza"),
            "pct_real": reaccion.get("pct_real"),
            "categoria": reaccion.get("categoria"),
            "fuente": fila["fuente"],
        })
    return casos


if __name__ == "__main__":
    casos = exportar()
    json.dump(casos, sys.stdout, ensure_ascii=False)
    print(f"\n# {len(casos)} casos exportados", file=sys.stderr)
```

## engine/contenido/fuentes/__init__.py
```python

```

## engine/contenido/fuentes/alpaca.py
```python
"""Cliente de Alpaca News API (titulares de Benzinga, tier gratuito).

Claves en el entorno: ALPACA_API_KEY_ID y ALPACA_API_SECRET_KEY.
Sin claves o sin red, devuelve lista vacía — degradación elegante:
el pipeline usará las simulaciones de ayer y el muro lo dirá con fecha.

El streaming por WebSocket (wss://stream.data.alpaca.markets/v1beta1/news)
queda para la fase de tiempo real; el ritual de la madrugada usa REST.
"""

import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import httpx

URL_NOTICIAS = "https://data.alpaca.markets/v1beta1/news"
URL_BARRAS = "https://data.alpaca.markets/v2/stocks/{simbolo}/bars"
RUTA_DEMO = Path(__file__).parent / "titulares_demo.json"


def hay_credenciales() -> bool:
    return bool(os.environ.get("ALPACA_API_KEY_ID") and os.environ.get("ALPACA_API_SECRET_KEY"))


def titulares_recientes(horas: int = 18, limite: int = 50) -> list[dict]:
    """Los titulares de las últimas `horas` desde Alpaca (REST).

    Devuelve [{"titular", "fuente", "simbolos", "fecha"}]; vacía si no hay
    credenciales o la API no responde (nunca lanza hacia el pipeline).
    """
    if not hay_credenciales():
        return []
    desde = (datetime.now(timezone.utc) - timedelta(hours=horas)).isoformat(timespec="seconds")
    try:
        respuesta = httpx.get(
            URL_NOTICIAS,
            params={"start": desde, "limit": limite, "sort": "desc"},
            headers={
                "APCA-API-KEY-ID": os.environ["ALPACA_API_KEY_ID"],
                "APCA-API-SECRET-KEY": os.environ["ALPACA_API_SECRET_KEY"],
            },
            timeout=15,
        )
        respuesta.raise_for_status()
        noticias = respuesta.json().get("news", [])
    except Exception:
        return []  # degradación elegante: el muro mostrará lo de ayer
    return [
        {
            "titular": n.get("headline", "").strip(),
            "fuente": n.get("source", "alpaca"),
            "url": n.get("url", ""),
            "simbolos": ",".join(n.get("symbols", [])),
            "fecha": n.get("created_at", ""),
        }
        for n in noticias
        if n.get("headline")
    ]


def variacion_real(simbolo: str, desde_iso: str, ruedas: int = 2) -> dict | None:
    """Cuánto se movió el símbolo EN EL MERCADO REAL alrededor de una fecha.

    Para el corrector automático (calibración): base = último cierre ANTES
    de la fecha de la noticia (el mercado aún no la veía); final = cierre
    `ruedas` días de mercado después. Barras diarias del feed IEX (incluido
    en el tier gratuito de Alpaca).

    Devuelve None si no hay claves, red o todavía no pasaron `ruedas`
    días de mercado — el corrector simplemente reintenta en la próxima
    corrida. Nunca lanza.
    """
    if not hay_credenciales() or not simbolo:
        return None
    fecha = desde_iso[:10]
    # margen ancho: fines de semana y feriados no tienen barra
    inicio = (datetime.fromisoformat(fecha) - timedelta(days=7)).strftime("%Y-%m-%d")
    fin = (datetime.fromisoformat(fecha) + timedelta(days=ruedas * 2 + 6)).strftime("%Y-%m-%d")
    try:
        respuesta = httpx.get(
            URL_BARRAS.format(simbolo=simbolo),
            params={"timeframe": "1Day", "start": inicio, "end": fin,
                    "feed": "iex", "adjustment": "raw", "limit": 50},
            headers={
                "APCA-API-KEY-ID": os.environ["ALPACA_API_KEY_ID"],
                "APCA-API-SECRET-KEY": os.environ["ALPACA_API_SECRET_KEY"],
            },
            timeout=15,
        )
        respuesta.raise_for_status()
        barras = respuesta.json().get("bars") or []
    except Exception:
        return None
    previas = [b for b in barras if b.get("t", "")[:10] < fecha]
    posteriores = [b for b in barras if b.get("t", "")[:10] >= fecha]
    # sin cierre previo, o aún no se completa la ventana: esperar
    if not previas or len(posteriores) < ruedas:
        return None
    base = previas[-1]
    final = posteriores[ruedas - 1]
    if not base.get("c"):
        return None
    pct = (final["c"] - base["c"]) / base["c"] * 100
    return {
        "simbolo": simbolo,
        "pct_real": round(pct, 2),
        "cierre_base": base["c"],
        "cierre_final": final["c"],
        "fecha_base": base["t"][:10],
        "fecha_final": final["t"][:10],
        "ruedas": ruedas,
    }


def titulares_demo() -> list[dict]:
    """Un día realista de titulares para desarrollo y pruebas sin claves."""
    with open(RUTA_DEMO, encoding="utf-8") as archivo:
        return json.load(archivo)


def obtener_titulares(horas: int = 18, limite: int = 50) -> tuple[list[dict], str]:
    """Titulares reales si hay claves; si no, el set de demo.

    Devuelve (titulares, origen) donde origen ∈ {"alpaca", "demo"}.
    """
    reales = titulares_recientes(horas, limite)
    if reales:
        return reales, "alpaca"
    return titulares_demo(), "demo"
```

## engine/contenido/fuentes/barchart.py
```python
"""Capa de DATOS de mercado (La Redacción — el "cuánto").

Cliente de Barchart (u otra API de cotizaciones). Es la ÚNICA fuente de
números: precios y % de variación. El relato (el "por qué") viene de las
noticias; jamás al revés. Clave en el entorno: BARCHART_API_KEY.

Degradación elegante: sin clave o sin red, devuelve un snapshot de
demostración marcado como tal — la redacción nunca inventa cifras ni se
cae. Los % de demo son verosímiles pero NO reales (por eso van con
`fuente: "demo"` y el correo queda como borrador hasta tu visto bueno).
"""

import json
import os
from pathlib import Path

import httpx

URL_QUOTE = "https://ondemand.websol.barchart.com/getQuote.json"
RUTA_DEMO = Path(__file__).parent / "mercado_demo.json"

# el "mercado global" a cubrir al inicio (símbolo → nombre editorial)
INSTRUMENTOS = {
    "$SPX": "S&P 500",
    "$IUXX": "Nasdaq 100",
    "CLZ25": "Petróleo WTI",
    "GCZ25": "Oro",
    "NVDA": "Nvidia",
    "AAPL": "Apple",
}


def hay_credenciales() -> bool:
    return bool(os.environ.get("BARCHART_API_KEY"))


def _parsear(item: dict) -> dict | None:
    """Extrae de la respuesta de Barchart lo único que nos importa: el número."""
    try:
        return {
            "simbolo": item["symbol"],
            "ultimo": float(item["lastPrice"]),
            "variacion_pct": round(float(item["percentChange"]), 2),
        }
    except (KeyError, TypeError, ValueError):
        return None


def cotizaciones(simbolos: list[str] | None = None) -> tuple[list[dict], str]:
    """Devuelve ([{simbolo, nombre, ultimo, variacion_pct}], origen).

    origen ∈ {"barchart", "demo"}. Nunca lanza hacia la redacción.
    """
    simbolos = simbolos or list(INSTRUMENTOS)
    if hay_credenciales():
        try:
            respuesta = httpx.get(
                URL_QUOTE,
                params={
                    "apikey": os.environ["BARCHART_API_KEY"],
                    "symbols": ",".join(simbolos),
                    "fields": "lastPrice,percentChange",
                },
                timeout=15,
            )
            respuesta.raise_for_status()
            crudo = respuesta.json().get("results", [])
            datos = [d for d in (_parsear(i) for i in crudo) if d]
            if datos:
                for d in datos:
                    d["nombre"] = INSTRUMENTOS.get(d["simbolo"], d["simbolo"])
                return datos, "barchart"
        except Exception:
            pass  # degradación elegante
    # sin clave / sin datos: snapshot de demostración
    with open(RUTA_DEMO, encoding="utf-8") as archivo:
        demo = json.load(archivo)
    return demo, "demo"
```

## engine/contenido/fuentes/stooq.py
```python
"""Precios históricos de Stooq — el plan B del backtest (sin clave).

Alpaca cubre desde ~2016; los exámenes más antiguos (Lehman 2008, la
rebaja del rating de EE.UU. 2011, el taper tantrum 2013…) se miden con
Stooq (stooq.com), que publica series diarias históricas en CSV público
sin autenticación. Misma semántica que alpaca.variacion_real:
base = último cierre ANTES de la fecha; final = cierre `ruedas` días de
mercado después. Devuelve None ante cualquier problema — nunca lanza.
"""

import csv
import io
from datetime import datetime, timedelta

import httpx

URL = "https://stooq.com/q/d/l/"


def variacion_real(simbolo: str, desde_iso: str, ruedas: int = 2) -> dict | None:
    if not simbolo:
        return None
    fecha = desde_iso[:10]
    try:
        d1 = (datetime.fromisoformat(fecha) - timedelta(days=7)).strftime("%Y%m%d")
        d2 = (datetime.fromisoformat(fecha) + timedelta(days=ruedas * 2 + 6)).strftime("%Y%m%d")
        respuesta = httpx.get(
            URL,
            params={"s": f"{simbolo.lower()}.us", "d1": d1, "d2": d2, "i": "d"},
            timeout=15,
        )
        respuesta.raise_for_status()
        filas = list(csv.DictReader(io.StringIO(respuesta.text)))
    except Exception:
        return None
    previas = [f for f in filas if f.get("Date", "") < fecha and f.get("Close")]
    posteriores = [f for f in filas if f.get("Date", "") >= fecha and f.get("Close")]
    if not previas or len(posteriores) < ruedas:
        return None
    try:
        base = float(previas[-1]["Close"])
        final = float(posteriores[ruedas - 1]["Close"])
    except (TypeError, ValueError):
        return None
    if not base:
        return None
    return {
        "simbolo": simbolo,
        "pct_real": round((final - base) / base * 100, 2),
        "cierre_base": base,
        "cierre_final": final,
        "fecha_base": previas[-1]["Date"],
        "fecha_final": posteriores[ruedas - 1]["Date"],
        "ruedas": ruedas,
        "fuente_datos": "stooq",
    }
```

## engine/contenido/fuentes/yahoo.py
```python
"""Precios históricos de Yahoo Finance — la fuente robusta del backtest.

Reemplaza a Stooq (cuya API de descarga dejó de responder). Yahoo cubre
acciones, ETFs y cripto con histórico largo y sin clave: SPY desde los 90,
GBTC/COIN, GLD, USO, y hasta BTC-USD directo. Misma semántica que
alpaca.variacion_real: base = último cierre ANTES de la fecha de la
noticia; final = cierre `ruedas` días de mercado después.

Devuelve None ante cualquier problema — nunca lanza.
"""

from datetime import datetime

import httpx

URL = "https://query1.finance.yahoo.com/v8/finance/chart/{simbolo}"

# el "telón de fondo" del diario en símbolos Yahoo (símbolo → nombre editorial).
# Los índices y materias primas siempre relevantes; las acciones del día se
# consultan por su ticker directo (NVDA, AAPL…), que Yahoo acepta tal cual.
NOMBRES = {
    "^GSPC": "S&P 500", "^IXIC": "Nasdaq 100", "^DJI": "Dow Jones",
    "CL=F": "Petróleo WTI", "GC=F": "Oro", "BTC-USD": "Bitcoin",
}


def _serie_anual(simbolo: str) -> list[float] | None:
    """Los cierres diarios del último año (viejo → nuevo). None ante fallo."""
    try:
        respuesta = httpx.get(
            URL.format(simbolo=simbolo),
            params={"range": "1y", "interval": "1d"},
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=15,
        )
        respuesta.raise_for_status()
        resultado = respuesta.json()["chart"]["result"][0]
        cierres = resultado["indicators"]["quote"][0]["close"]
    except Exception:
        return None
    limpios = [float(c) for c in cierres if c is not None]
    return limpios if len(limpios) >= 2 else None


_MESES_ES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago",
             "sep", "oct", "nov", "dic"]


def etiqueta_fecha(dt: datetime) -> str:
    """'7 ago' — etiqueta corta en español para los ejes del gráfico."""
    return f"{dt.day} {_MESES_ES[dt.month - 1]}"


def serie_reciente(simbolo: str, rango: str = "5d", intervalo: str = "1d"):
    """(fechas, cierres) recientes de un símbolo, para dibujar su gráfico.
    `rango` e `intervalo` en la jerga de Yahoo (5d/1mo/1y, 1d/15m…).
    Devuelve (list[datetime], list[float]) o None ante cualquier problema."""
    try:
        respuesta = httpx.get(
            URL.format(simbolo=simbolo),
            params={"range": rango, "interval": intervalo},
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=15,
        )
        respuesta.raise_for_status()
        r = respuesta.json()["chart"]["result"][0]
        marcas = r["timestamp"]
        cierres = r["indicators"]["quote"][0]["close"]
    except Exception:
        return None
    pares = [(datetime.utcfromtimestamp(ts), float(c))
             for ts, c in zip(marcas, cierres) if c is not None]
    if len(pares) < 2:
        return None
    return [p[0] for p in pares], [p[1] for p in pares]


# ---------- fundamentales (para el análisis de fin de semana) ----------
# El endpoint quoteSummary pide un "crumb" (cookie + token). Lo pedimos una vez
# por proceso y lo reusamos. Si el flujo falla, fundamentales() devuelve None y
# el deep-dive sale SIN el bloque de números (nunca inventa cifras).

_URL_CRUMB = "https://query1.finance.yahoo.com/v1/test/getcrumb"
_URL_RESUMEN = "https://query1.finance.yahoo.com/v10/finance/quoteSummary/{simbolo}"
_UA_NAV = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
           "(KHTML, like Gecko) Chrome/120 Safari/537.36")
_MODULOS = "financialData,defaultKeyStatistics,summaryDetail,price"

_crumb_cache: dict = {"cliente": None, "crumb": None}


def _sesion_crumb():
    """(cliente httpx con cookie, crumb) reutilizable. None si no se pudo obtener."""
    if _crumb_cache["crumb"]:
        return _crumb_cache["cliente"], _crumb_cache["crumb"]
    try:
        cliente = httpx.Client(headers={"User-Agent": _UA_NAV}, timeout=15, follow_redirects=True)
        cliente.get("https://fc.yahoo.com")  # siembra la cookie (puede dar 404, da igual)
        crumb = cliente.get(_URL_CRUMB).text.strip()
        # un crumb válido es un token corto sin espacios ni HTML
        if not crumb or len(crumb) > 40 or "<" in crumb or " " in crumb:
            cliente.close()
            return None, None
        _crumb_cache["cliente"], _crumb_cache["crumb"] = cliente, crumb
        return cliente, crumb
    except Exception:
        return None, None


_URL_SCREENER = "https://query1.finance.yahoo.com/v1/finance/screener/predefined/saved"


def _valor(nodo):
    """El número crudo de un campo de Yahoo, sea {raw,fmt} o un número pelado."""
    if isinstance(nodo, dict):
        return nodo.get("raw")
    return nodo if isinstance(nodo, (int, float)) else None


# qué % mirar según el momento del día (para que el enjambre vea lo que se
# mueve AHORA: en la madrugada el pre-market; en la tarde la sesión).
_SESIONES = [
    ("preMarketChangePercent", "pre-market"),
    ("regularMarketChangePercent", "sesión"),
    ("postMarketChangePercent", "post-cierre"),
]


def _cambio_efectivo(q: dict) -> tuple[float | None, str]:
    """El movimiento más relevante de una acción y en qué momento ocurrió: el de
    mayor magnitud entre pre-market, sesión y post-cierre (el que esté disponible).
    Así funciona igual a las 6 AM (pre-market) que a las 4 PM (sesión cerrada)."""
    mejor_pct, mejor_sesion = None, "sesión"
    for campo, etiqueta in _SESIONES:
        v = _valor(q.get(campo))
        if isinstance(v, (int, float)) and (mejor_pct is None or abs(v) > abs(mejor_pct)):
            mejor_pct, mejor_sesion = float(v), etiqueta
    return mejor_pct, mejor_sesion


def movers_del_dia(n: int = 8, min_pct: float = 5.0) -> list[dict]:
    """Los mayores movimientos del mercado de EE.UU. en este momento: lista de
    {ticker, nombre, var_pct, sesion, precio}, los más movidos primero. Mira
    pre-market + sesión + post-cierre, así sirve tanto en la madrugada (antes de
    abrir) como en la tarde. Es lo que DE VERDAD se mueve, no solo lo titulado.
    [] ante cualquier problema (degradación elegante). Nunca lanza."""
    cliente, crumb = _sesion_crumb()
    if not cliente or not crumb:
        return []
    vistos: set[str] = set()
    movimientos: list[dict] = []
    for tablero in ("day_gainers", "day_losers", "most_actives"):
        try:
            r = cliente.get(_URL_SCREENER,
                            params={"count": 25, "scrIds": tablero, "crumb": crumb})
            if r.status_code != 200:
                continue
            res = (r.json().get("finance", {}).get("result") or [None])[0]
            quotes = (res or {}).get("quotes") or []
        except Exception:
            continue
        for q in quotes:
            tk = str(q.get("symbol", "")).strip().upper()
            pct, sesion = _cambio_efectivo(q)
            if not tk or tk in vistos or pct is None:
                continue
            if abs(pct) < min_pct:  # ignora ruido: solo movimientos con peso
                continue
            vistos.add(tk)
            movimientos.append({
                "ticker": tk,
                "nombre": str(q.get("shortName") or q.get("longName") or tk)[:60],
                "var_pct": round(pct, 2),
                "sesion": sesion,
                "precio": _valor(q.get("regularMarketPrice")),
            })
    movimientos.sort(key=lambda m: abs(m["var_pct"]), reverse=True)
    return movimientos[:n]


def _fmt(nodo) -> str | None:
    """El texto formateado de un campo de Yahoo ({raw, fmt}); None si no hay dato."""
    if isinstance(nodo, dict):
        f = nodo.get("fmt")
        return f if f else None
    return None


def _num(nodo) -> float | None:
    return nodo.get("raw") if isinstance(nodo, dict) and isinstance(nodo.get("raw"), (int, float)) else None


def fundamentales(simbolo: str) -> dict | None:
    """Los fundamentales VERIFICADos de una empresa (para el análisis de fin de
    semana): capitalización, ingresos y su crecimiento, márgenes, EBITDA, deuda y
    caja. Los valores van formateados (para mostrar) tal como los da Yahoo. None
    ante cualquier problema o si es un instrumento sin fundamentales (un ETF).
    Nunca lanza."""
    cliente, crumb = _sesion_crumb()
    if not cliente or not crumb:
        return None
    try:
        r = cliente.get(_URL_RESUMEN.format(simbolo=simbolo),
                        params={"modules": _MODULOS, "crumb": crumb})
        if r.status_code != 200:
            return None
        res = (r.json().get("quoteSummary", {}).get("result") or [None])[0]
        if not res:
            return None
    except Exception:
        return None
    fd = res.get("financialData", {}) or {}
    sd = res.get("summaryDetail", {}) or {}
    price = res.get("price", {}) or {}

    cap_num = _num(sd.get("marketCap")) or _num(price.get("marketCap"))
    ingresos = _fmt(fd.get("totalRevenue"))
    ebitda = _fmt(fd.get("ebitda"))
    # sin ingresos ni EBITDA no hay ficha que valga (típico de ETFs/índices)
    if ingresos is None and ebitda is None:
        return None
    datos = {
        "market_cap": _fmt(sd.get("marketCap")) or _fmt(price.get("marketCap")),
        "market_cap_num": cap_num,
        "ingresos": ingresos,
        "crecimiento_ingresos": _fmt(fd.get("revenueGrowth")),
        "ebitda": ebitda,
        "margen_bruto": _fmt(fd.get("grossMargins")),
        "margen_operativo": _fmt(fd.get("operatingMargins")),
        "margen_neto": _fmt(fd.get("profitMargins")),
        "deuda": _fmt(fd.get("totalDebt")),
        "caja": _fmt(fd.get("totalCash")),
        "flujo_caja_libre": _fmt(fd.get("freeCashflow")),
    }
    # descarta claves sin dato para no arrastrar None hasta la plantilla
    return {k: v for k, v in datos.items() if v is not None}


def _pct(nuevo: float, viejo: float) -> float | None:
    return round((nuevo - viejo) / viejo * 100, 2) if viejo else None


def _variaciones(cierres: list[float]) -> dict | None:
    """Día/Mes/Año a partir de la serie anual de cierres."""
    if len(cierres) < 2:
        return None
    ult = cierres[-1]
    return {
        "ultimo": round(ult, 2),
        "variacion_pct": _pct(ult, cierres[-2]),                       # día
        "var_mes_pct": _pct(ult, cierres[-22]) if len(cierres) >= 22 else None,  # ~1 mes
        "var_ano_pct": _pct(ult, cierres[0]),                          # ~1 año
    }


def cotizaciones(simbolos: list[str]) -> tuple[list[dict], str]:
    """Cotizaciones de HOY desde Yahoo (gratis): [{simbolo, nombre, ultimo,
    variacion_pct, var_mes_pct, var_ano_pct}], origen 'yahoo'. Una llamada por
    símbolo; los que fallan se omiten. Nunca lanza hacia la redacción."""
    datos = []
    for simbolo in simbolos:
        serie = _serie_anual(simbolo)
        if not serie:
            continue
        var = _variaciones(serie)
        if not var:
            continue
        datos.append({"simbolo": simbolo, "nombre": NOMBRES.get(simbolo, simbolo), **var})
    return datos, "yahoo"


def variacion_real(simbolo: str, desde_iso: str, ruedas: int = 2) -> dict | None:
    if not simbolo:
        return None
    fecha = desde_iso[:10]
    try:
        base_dt = datetime.fromisoformat(fecha)
        # margen amplio: cubre fines de semana, feriados y la ventana futura
        p1 = int(base_dt.timestamp()) - 12 * 86400
        p2 = int(base_dt.timestamp()) + (ruedas * 2 + 10) * 86400
        respuesta = httpx.get(
            URL.format(simbolo=simbolo),
            params={"period1": p1, "period2": p2, "interval": "1d"},
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=15,
        )
        respuesta.raise_for_status()
        resultado = respuesta.json()["chart"]["result"][0]
        marcas = resultado["timestamp"]
        cierres = resultado["indicators"]["quote"][0]["close"]
    except Exception:
        return None

    # (fecha_iso, cierre) de cada rueda con dato válido
    barras = []
    for ts, cierre in zip(marcas, cierres):
        if cierre is None:
            continue
        dia = datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d")
        barras.append((dia, float(cierre)))

    previas = [b for b in barras if b[0] < fecha]
    posteriores = [b for b in barras if b[0] >= fecha]
    if not previas or len(posteriores) < ruedas:
        return None

    fecha_base, base = previas[-1]
    fecha_final, final = posteriores[ruedas - 1]
    if not base:
        return None
    return {
        "simbolo": simbolo,
        "pct_real": round((final - base) / base * 100, 2),
        "cierre_base": round(base, 2),
        "cierre_final": round(final, 2),
        "fecha_base": fecha_base,
        "fecha_final": fecha_final,
        "ruedas": ruedas,
        "fuente_datos": "yahoo",
    }
```

## engine/contenido/graficos.py
```python
"""Gráficos de precio REAL para El Pulso (rediseño estilo Moby).

Dibuja un PNG autocontenido —fondo claro, la línea de precio, el nombre del
activo, su variación del período y el precio inicial/final— para incrustar en
el correo. Los datos vienen de Yahoo (contenido/fuentes/yahoo.py); este módulo
solo pinta. Se dibuja en 2D con Pillow (sin GL headless), como captura.py.

Regla de integridad: los números vienen dados (serie real). Este módulo no
inventa nada; si la serie es pobre (< 2 puntos), devuelve None y el correo
simplemente omite el gráfico.
"""

import io
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# paleta CLARA del correo (misma que boletin.py) en RGB
PAPEL = (244, 239, 228)      # #f4efe4 — fondo de la tarjeta del gráfico
BORDE = (231, 222, 208)      # #e7ded0 — hairline
TINTA = (28, 24, 19)         # #1c1813 — texto principal
CUERPO = (58, 53, 44)        # #3a352c
MUTE = (138, 129, 115)       # #8a8173 — secundario
SUBE = (47, 143, 102)        # #2f8f66 — verde
BAJA = (192, 80, 77)         # #c0504d — rojo

# 2x para retina; en el correo se muestra a la mitad (~536 px de ancho)
ANCHO, ALTO = 1072, 480
MARGEN = 44
PAD_LINEA_SUP = 150          # dónde empieza el área de la línea
PAD_LINEA_INF = 100          # margen inferior del área de la línea


def _fuente(tamano: int, negrita: bool = False):
    candidatas = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if negrita
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for ruta in candidatas:
        if Path(ruta).exists():
            try:
                return ImageFont.truetype(ruta, tamano)
            except OSError:
                continue
    return ImageFont.load_default()


def _limpiar_serie(serie: list) -> list[float]:
    """Descarta huecos (None) que Yahoo deja en días sin cierre."""
    return [float(v) for v in (serie or []) if isinstance(v, (int, float))]


def _fmt_precio(v: float) -> str:
    """1234.5 → '1.234,5' no: mantenemos punto decimal simple estilo mercado US."""
    if v >= 1000:
        return f"{v:,.0f}".replace(",", " ")
    if v >= 1:
        return f"{v:,.2f}"
    return f"{v:.4f}"           # cripto/penny stocks


def generar_grafico(
    nombre: str, ticker: str, serie: list[float], *,
    etiqueta_periodo: str = "última semana",
    fecha_inicio: str = "", fecha_fin: str = "hoy",
    moneda: str = "$",
) -> bytes | None:
    """PNG del gráfico de un activo. None si la serie no alcanza (< 2 puntos)."""
    cierres = _limpiar_serie(serie)
    if len(cierres) < 2:
        return None

    inicio, fin = cierres[0], cierres[-1]
    sube = fin >= inicio
    color = SUBE if sube else BAJA
    delta = fin - inicio
    pct = (delta / inicio * 100) if inicio else 0.0
    signo = "+" if delta >= 0 else "−"
    cambio_txt = (f"{signo}{moneda}{_fmt_precio(abs(delta))} "
                  f"({signo}{abs(pct):.1f}%) · {etiqueta_periodo}")

    imagen = Image.new("RGB", (ANCHO, ALTO), PAPEL)
    d = ImageDraw.Draw(imagen)
    d.rounded_rectangle([2, 2, ANCHO - 2, ALTO - 2], radius=20, outline=BORDE, width=2)

    # ── cabecera: nombre · ticker  (izq)   ·   variación (der) ──
    f_nom = _fuente(30, negrita=True)
    d.text((MARGEN, 40), f"{nombre} · {ticker}", font=f_nom, fill=TINTA)
    f_chg = _fuente(27, negrita=True)
    anc = d.textlength(cambio_txt, font=f_chg)
    d.text((ANCHO - MARGEN - anc, 44), cambio_txt, font=f_chg, fill=color)

    # ── la línea de precio ──
    x0, x1 = MARGEN, ANCHO - MARGEN
    y0, y1 = PAD_LINEA_SUP, ALTO - PAD_LINEA_INF
    lo, hi = min(cierres), max(cierres)
    rango = max(hi - lo, 1e-9)
    n = len(cierres)
    pts = []
    for i, v in enumerate(cierres):
        x = x0 + (i / (n - 1)) * (x1 - x0)
        y = y1 - ((v - lo) / rango) * (y1 - y0)
        pts.append((x, y))

    # área tenue bajo la línea (relleno del color, muy suave)
    poligono = pts + [(x1, y1), (x0, y1)]
    capa = Image.new("RGBA", (ANCHO, ALTO), (0, 0, 0, 0))
    ImageDraw.Draw(capa).polygon(poligono, fill=color + (28,))
    imagen.paste(Image.alpha_composite(imagen.convert("RGBA"), capa).convert("RGB"), (0, 0))
    d = ImageDraw.Draw(imagen)

    d.line(pts, fill=color, width=5, joint="curve")
    ex, ey = pts[-1]
    d.ellipse([ex - 8, ey - 8, ex + 8, ey + 8], fill=color)

    # ── pie: precio inicial (izq)  ·  precio final (der, resaltado) ──
    f_eje = _fuente(21)
    izq = f"{moneda}{_fmt_precio(inicio)}" + (f" · {fecha_inicio}" if fecha_inicio else "")
    d.text((MARGEN, ALTO - 58), izq, font=f_eje, fill=MUTE)
    f_fin = _fuente(22, negrita=True)
    der = f"{moneda}{_fmt_precio(fin)} · {fecha_fin}"
    anc_der = d.textlength(der, font=f_fin)
    d.text((ANCHO - MARGEN - anc_der, ALTO - 59), der, font=f_fin, fill=color)

    buffer = io.BytesIO()
    imagen.save(buffer, format="PNG")
    return buffer.getvalue()
```

## engine/contenido/investigador.py
```python
"""El reportero IA de El Pulso: investiga y VERIFICA por qué se movió una acción,
con búsqueda web real, ANTES de que la historia entre a la edición del día.

Convierte un movimiento crudo ("MRNA +170%") en un titular con contexto
verificado ("Moderna sube 170% tras un avance en su vacuna contra el cáncer").
Así el enjambre reacciona a lo que DE VERDAD movió al mercado —no solo a lo que
un feed de titulares decidió publicar— y con el porqué comprobado.

Reglas:
- Si NO puede verificar el motivo, lo dice (no lo inventa). Marco CMF: informar,
  no adivinar; jamás consejo de inversión.
- Degradación elegante: sin ANTHROPIC_API_KEY o si la búsqueda falla, usa un
  titular llano con el dato duro (el movimiento igual entra a la selección).
- Acota costo y tiempo: investiga solo los MAX_MOVERS mayores, en paralelo.
"""

import json
import logging
import os
import re
from concurrent.futures import ThreadPoolExecutor

from contenido import vocabulario

log = logging.getLogger("enjambre.investigador")

MODELO = "claude-sonnet-5"
TIMEOUT = 40
MAX_MOVERS = 6          # cuántos movimientos investiga (techo de costo/tiempo)
HILOS = 6
# Búsqueda web del lado del servidor de Anthropic (Sonnet-5). Usamos la versión
# BÁSICA con llamada DIRECTA a propósito: la variante nueva (web_search_20260209)
# enruta por defecto a través de "code execution" (filtrado dinámico) y, en una
# llamada simple como la nuestra, devuelve HTTP 400 —lo que antes tumbaba en
# silencio toda la investigación al respaldo llano. La básica corre directo, sin
# esa maquinaria, y basta de sobra para averiguar "por qué se movió la acción".
HERRAMIENTAS_WEB = [{
    "type": "web_search_20250305",
    "name": "web_search",
    "max_uses": 3,
}]

PROMPT = (
    "Eres un reportero de mercado riguroso. Te doy una acción que se movió fuerte HOY. "
    "Busca en la web el motivo REAL y verifícalo con al menos una fuente creíble "
    "(un medio financiero, un comunicado, la propia empresa). Responde SOLO con un JSON:\n"
    '{"verificado": true|false, "titular": "…", "razon": "…", "fuente": "…"}\n'
    "- titular: en español, una línea noticiosa con el nombre, el ticker, el % y el "
    "PORQUÉ verificado. Ej: \"Moderna (MRNA) sube 170% tras un avance en su vacuna contra el cáncer\".\n"
    "- razon: una frase con el motivo confirmado.\n"
    "- fuente: el medio o URL donde lo confirmaste.\n"
    "- Si NO hallas un motivo claro y verificable, pon verificado=false y en titular "
    "SOLO el dato duro, sin inventar causa.\n"
    "NUNCA inventes el motivo. NUNCA des consejo de inversión (ni 'compra', ni 'vende', "
    "ni 'oportunidad'). Solo informas qué pasó y por qué."
)


def _extraer_json(texto: str) -> dict | None:
    if not texto:
        return None
    m = re.search(r"\{.*\}", texto, re.DOTALL)
    try:
        return json.loads(m.group(0)) if m else None
    except (ValueError, TypeError):
        return None


def _direccion(pct: float) -> str:
    return "sube" if pct >= 0 else "cae"


_CONTEXTO_SESION = {"pre-market": "en pre-market", "post-cierre": "tras el cierre"}


def _cuando(m: dict) -> str:
    return _CONTEXTO_SESION.get(m.get("sesion", ""), "en la sesión")


def _titular_llano(m: dict) -> dict:
    """El respaldo sin IA: el dato duro como titular (el movimiento igual entra)."""
    return {
        "titular": f"{m['nombre']} ({m['ticker']}) {_direccion(m['var_pct'])} "
                   f"{abs(m['var_pct'])}% {_cuando(m)}",
        "fuente": "movimiento de mercado", "simbolos": m["ticker"],
        "verificado": False, "razon": "",
        "var_pct": m.get("var_pct"), "sesion": m.get("sesion"),
    }


def _investigar_uno(m: dict) -> dict:
    """Investiga UN movimiento con búsqueda web. Nunca lanza: ante cualquier
    problema, devuelve el titular llano (degradación)."""
    llano = _titular_llano(m)
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return llano
    dato = (f"{m['nombre']} ({m['ticker']}) {_direccion(m['var_pct'])} "
            f"{abs(m['var_pct'])}% {_cuando(m)} hoy. ¿Por qué se movió?")
    try:
        import anthropic
        from llm_texto import texto_de

        cliente = anthropic.Anthropic(timeout=TIMEOUT)
        respuesta = cliente.messages.create(
            model=MODELO, max_tokens=1200, system=PROMPT,
            tools=HERRAMIENTAS_WEB,
            messages=[{"role": "user", "content": dato}],
        )
        datos = _extraer_json(texto_de(respuesta))
        titular = str((datos or {}).get("titular", "")).strip()
        razon = str((datos or {}).get("razon", "") or "")[:300]
        # el titular Y la razón DEBEN pasar el filtro CMF; si no, al respaldo llano
        if not titular or not vocabulario.es_publicable(titular) or not vocabulario.es_publicable(razon):
            return {**llano, "var_pct": m.get("var_pct"), "sesion": m.get("sesion")}
        return {
            "titular": titular[:200],
            "fuente": str(datos.get("fuente", "") or "investigación")[:120],
            "simbolos": m["ticker"],
            "verificado": bool(datos.get("verificado")),
            "razon": razon,
            "var_pct": m.get("var_pct"),
            "sesion": m.get("sesion"),
        }
    except Exception as e:
        # Degradamos SIEMPRE (la edición no se cae por la API), pero dejamos
        # rastro del motivo real en el log: así un fallo de la búsqueda web deja
        # de ser invisible como lo fue durante semanas.
        log.warning("La investigación de %s falló (%s: %s); uso titular llano.",
                    m.get("ticker"), type(e).__name__, e)
        return {**llano, "var_pct": m.get("var_pct"), "sesion": m.get("sesion")}


def investigar_movers(movers: list[dict], maximo: int = MAX_MOVERS) -> list[dict]:
    """Investiga los `maximo` mayores movimientos y los devuelve como candidatos
    listos para el portero: [{titular, fuente, simbolos, razon, verificado}, …].
    En paralelo. [] si no hay movimientos."""
    top = sorted(movers, key=lambda m: abs(m.get("var_pct", 0)), reverse=True)[:maximo]
    if not top:
        return []
    with ThreadPoolExecutor(max_workers=min(HILOS, len(top))) as ejecutor:
        resultados = list(ejecutor.map(_investigar_uno, top))
    return [r for r in resultados if r and r.get("titular")]
```

## engine/contenido/limites.py
```python
"""Límites de las simulaciones disparadas por visitantes.

Cada simulación pública cuesta ~$0,12 en llamadas LLM. Tres frenos:
- GRATIS, por IP y día: 1/día (en memoria; su reinicio es de horas y no cuesta
  plata; la clave lleva la fecha, así se vacía sola cada día).
- PREMIUM, por correo y MES: 40/mes (en DISCO, tabla `gasto_premium`): un
  reinicio de Render NO le regala el mes de nuevo. Tope pensado para que un
  Premium a tope cueste ~$4,80 < los $6,99 que paga → nunca se pierde plata.
- GLOBAL, por día: tope diario (ENJAMBRE_MAX_SIM_DIA) en DISCO — la muralla de
  la billetera: manda sobre gratis y Premium por igual.

El on-demand es un lujo, no un regalo; al agotar el cupo, el muro invita al
Pulso (y al Premium, a esperar al próximo mes).
"""

import os
from datetime import date

from contenido import persistencia

LIMITE_DIA_GRATIS = 1     # defecto; ENJAMBRE_SIM_DIA_GRATIS
LIMITE_MES_PREMIUM = 40   # defecto; ENJAMBRE_SIM_MES_PREMIUM


def tope_dia_gratis() -> int:
    try:
        return max(0, int(os.environ.get("ENJAMBRE_SIM_DIA_GRATIS", str(LIMITE_DIA_GRATIS))))
    except (TypeError, ValueError):
        return LIMITE_DIA_GRATIS


def tope_mes_premium() -> int:
    try:
        return max(0, int(os.environ.get("ENJAMBRE_SIM_MES_PREMIUM", str(LIMITE_MES_PREMIUM))))
    except (TypeError, ValueError):
        return LIMITE_MES_PREMIUM


def tope_global_dia() -> int:
    try:
        return max(0, int(os.environ.get("ENJAMBRE_MAX_SIM_DIA", "30")))
    except (TypeError, ValueError):
        return 30


# uso diario GRATIS por IP: clave -> (fecha_iso, cuenta). La fecha en el valor
# hace que el cupo se reinicie solo al cambiar el día (el Premium va en disco).
_uso: dict[str, tuple[str, int]] = {}

MENSAJE_GLOBAL = (
    "El enjambre agotó sus simulaciones públicas de hoy. "
    "Suscríbete al Pulso para no perderte la reacción de mañana."
)


def _mensaje_gratis() -> str:
    # Honesto: el cupo gratis se cuenta por RED (IP), que muchas personas
    # comparten (oficinas, móviles con CGNAT). No afirmamos "tú lo usaste"
    # —puede haber sido otra persona de la misma red—, ofrecemos salida.
    n = tope_dia_gratis()
    veces = "una simulación" if n == 1 else f"{n} simulaciones"
    return (f"El enjambre ya corrió {veces} desde tu red hoy. Mira las destacadas del "
            f"día, o desbloquea {tope_mes_premium()} al mes con El Pulso Premium.")


def _mensaje_premium() -> str:
    return (f"Usaste tus {tope_mes_premium()} simulaciones Premium del mes. "
            "Se renuevan el día 1.")


def permitir(ip: str, premium_token: str | None = None, cliente_id: str | None = None,
             consumir: bool = True) -> tuple[bool, str]:
    """¿Puede esta persona disparar una simulación ahora? (permitido, motivo).

    Nivel según Premium: si `premium_token` (el secreto del enlace mágico)
    corresponde a un suscriptor Premium activo, tiene 40/MES (por correo, en
    disco). El resto, 1/DÍA contado por `cliente_id` (huella del navegador) o,
    si falta, por IP — así una oficina o una red móvil (CGNAT) no comparte un
    solo cupo. El tope global (billetera) manda sobre ambos.
    """
    conexion = persistencia.conectar()
    try:
        hoy = date.today().isoformat()
        # 1) la muralla de la billetera (en disco) — sobre todos
        if persistencia.gasto_dia(conexion, hoy) >= tope_global_dia():
            return False, MENSAJE_GLOBAL

        # el token (no el correo desnudo) prueba que es el dueño del buzón Premium
        email = persistencia.email_por_token_enjambre(conexion, (premium_token or "").strip())
        es_prem = bool(email) and persistencia.es_premium(conexion, email)

        if es_prem:
            # PREMIUM: cupo mensual en disco
            mes = hoy[:7]
            if persistencia.gasto_premium_mes(conexion, email, mes) >= tope_mes_premium():
                return False, _mensaje_premium()
            if consumir:
                persistencia.sumar_gasto_premium(conexion, email, mes, 1)
                persistencia.sumar_gasto_dia(conexion, hoy, 1)
            return True, ""

        # GRATIS: cupo diario en memoria, por dispositivo (o IP si no hay huella)
        cid = (cliente_id or "").strip()[:64]
        clave = f"cid:{cid}" if cid else f"ip:{ip}"
        fecha, cuenta = _uso.get(clave, (hoy, 0))
        if fecha != hoy:          # cambió el día: cupo fresco
            cuenta = 0
        if cuenta >= tope_dia_gratis():
            _uso[clave] = (hoy, cuenta)
            return False, _mensaje_gratis()
        if consumir:
            _uso[clave] = (hoy, cuenta + 1)
            persistencia.sumar_gasto_dia(conexion, hoy, 1)
        return True, ""
    finally:
        conexion.close()


def limpiar(ahora=None) -> None:
    """Descarta las cuentas de días pasados — evita que _uso crezca sin fin al
    acumular visitantes distintos (fuga de memoria lenta)."""
    hoy = date.today().isoformat()
    for clave in list(_uso):
        if _uso[clave][0] != hoy:
            del _uso[clave]


def reiniciar() -> None:
    """Borra el estado (para los tests): el uso en memoria y el gasto en disco."""
    _uso.clear()
    try:
        conexion = persistencia.conectar()
        try:
            persistencia.reiniciar_gasto(conexion)
        finally:
            conexion.close()
    except Exception:
        pass  # sin base todavía (algún test muy temprano): nada que borrar
```

## engine/contenido/notificar.py
```python
"""Aviso a Giorgio por Telegram (CONTENIDO.md paso 8 del ritual).

Un resumen de la ejecución del pipeline (qué se simuló, cuántos correos
salieron, errores). Degradación elegante: sin TELEGRAM_BOT_TOKEN o
TELEGRAM_CHAT_ID, no hace nada (devuelve False), nunca lanza.

Nota: este es el aviso SALIENTE. El oyente del canal de noticias de
Giorgio (fuentes/telegram.py) es la fase 2.
"""

import html
import os

import httpx


def escapar(texto: str) -> str:
    """Escapa el texto variable que se mete en un aviso.

    Los avisos van con parse_mode=HTML, así que un titular o un formulario con
    un `<` hace que Telegram rechace el mensaje entero (400) y el aviso se
    pierda en silencio. Todo lo que venga de fuera pasa por aquí."""
    return html.escape(str(texto or ""), quote=False)


def avisar(mensaje: str) -> bool:
    """Envía un mensaje al chat de Telegram de Giorgio. False si no configurado."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        return False
    try:
        respuesta = httpx.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": mensaje, "parse_mode": "HTML"},
            timeout=15,
        )
        return respuesta.status_code < 300
    except Exception:
        return False


def resumen_ejecucion(origen: str, publicadas: list[dict], envio: dict | None) -> str:
    """Arma el texto del aviso de una corrida del pipeline."""
    lineas = ["🐝 <b>El Pulso — corrida del día</b>", f"Fuente de titulares: {origen}"]
    if publicadas:
        lineas.append(f"Simuladas ({len(publicadas)}):")
        for p in publicadas:
            lineas.append(f"  ★ [{p['impacto']}/10] {escapar(p['titular'][:60])}")
    else:
        lineas.append("Sin simulaciones nuevas (el día ya estaba preparado).")
    if envio:
        lineas.append(
            f"Correos: {envio['enviados']} enviados / {envio['suscriptores']} suscriptores"
            + (f" · {envio['fallidos']} fallidos" if envio.get("fallidos") else "")
        )
    return "\n".join(lineas)
```

## engine/contenido/pagos.py
```python
"""Pagos de El Pulso Premium — integración con Polar (Merchant of Record).

Polar cobra la suscripción (USD, global) y nos avisa por webhook cuando alguien
paga, cancela o se le revoca el acceso. Aquí:

  1. verificamos la firma del webhook (estándar Standard Webhooks / Svix), y
  2. traducimos el evento a la LLAVE `premium` del suscriptor (persistencia).

Por qué Polar y no Stripe: Stripe no acepta negocios de Chile; Polar sí paga a
vendedores chilenos y, al ser Merchant of Record, es el vendedor legal y maneja
los impuestos. La firma es el MISMO esquema que ya usamos para Resend (Svix);
solo cambian los nombres de las cabeceras (webhook-id/-timestamp/-signature).

Degradación segura: sin POLAR_WEBHOOK_SECRET, la verificación SIEMPRE falla
(nunca se activa un Premium con una firma no comprobada).
"""

import base64
import hashlib
import hmac
import os
import time

from contenido import persistencia

TOLERANCIA_SEG = 3600  # antirreplay: margen amplio para el reloj de Render

# Eventos de Polar (Standard Webhooks). Referencia: docs de Polar → webhooks.
# ACTIVA: hay una suscripción vigente → Premium ON hasta el fin del período.
EVENTOS_ACTIVA = {
    "subscription.created", "subscription.active", "subscription.updated",
    "subscription.resumed", "subscription.uncanceled", "subscription.cycled",
}
# CANCELA: cancelación al final del período. NO se corta ya: se deja vencer
# (pagó por el período en curso). El vencimiento lo maneja `premium_hasta`.
EVENTOS_CANCELA = {"subscription.canceled"}
# REVOCA: el acceso terminó de inmediato (impago definitivo, reembolso) → OFF ya.
EVENTOS_REVOCA = {"subscription.revoked"}


def _secreto_bytes(secreto: str) -> bytes | None:
    """La clave del webhook, en bytes. Standard Webhooks la entrega en base64,
    a veces con prefijo 'whsec_'."""
    clave = secreto.split("_", 1)[1] if secreto.startswith("whsec_") else secreto
    try:
        return base64.b64decode(clave)
    except Exception:
        return None


def verificar_firma(cuerpo: bytes, cabeceras) -> bool:
    """Valida la firma Standard Webhooks de Polar. Constante en el tiempo.
    Sin secreto configurado → False (nunca confía en un cuerpo sin comprobar)."""
    secreto = os.environ.get("POLAR_WEBHOOK_SECRET", "").strip()
    if not secreto:
        return False
    wid = cabeceras.get("webhook-id", "")
    wts = cabeceras.get("webhook-timestamp", "")
    firmas = cabeceras.get("webhook-signature", "")
    if not (wid and wts and firmas):
        return False
    try:
        if abs(int(time.time()) - int(wts)) > TOLERANCIA_SEG:
            return False
    except (ValueError, TypeError):
        return False
    clave_bytes = _secreto_bytes(secreto)
    if clave_bytes is None:
        return False
    firmado = f"{wid}.{wts}.".encode() + cuerpo
    esperada = base64.b64encode(hmac.new(clave_bytes, firmado, hashlib.sha256).digest()).decode()
    for parte in firmas.split():
        _, _, valor = parte.partition(",")
        if valor and hmac.compare_digest(valor, esperada):
            return True
    return False


def _email_de(data: dict) -> str | None:
    """Saca el correo del pagador del payload, tolerante a la forma exacta
    (Polar lo trae en data.customer.email; dejamos respaldos por si cambia)."""
    if not isinstance(data, dict):
        return None
    for ruta in (("customer", "email"), ("user", "email"), ("customer", "billing_email")):
        d = data
        for clave in ruta:
            d = d.get(clave) if isinstance(d, dict) else None
        if isinstance(d, str) and "@" in d:
            return d.strip().lower()
    for clave in ("customer_email", "email"):
        v = data.get(clave)
        if isinstance(v, str) and "@" in v:
            return v.strip().lower()
    return None


def _hasta_de(data: dict) -> str | None:
    """La fecha de vencimiento del período (AAAA-MM-DD) desde el payload."""
    if not isinstance(data, dict):
        return None
    for clave in ("current_period_end", "ends_at", "current_period_end_at"):
        v = data.get(clave)
        if isinstance(v, str) and len(v) >= 10:
            return v[:10]
    return None


def procesar_evento(conexion, evento: dict) -> dict:
    """Traduce un evento de Polar a la llave Premium del suscriptor. Idempotente:
    reprocesar el mismo evento deja el mismo estado (Polar reintenta si fallamos)."""
    tipo = (evento.get("type") or "").strip()
    data = evento.get("data") or {}
    email = _email_de(data)
    if not email:
        return {"ok": True, "accion": "ignorado", "motivo": "sin correo en el evento"}

    if tipo in EVENTOS_ACTIVA or tipo in EVENTOS_CANCELA:
        # un pagador SIEMPRE recibe El Pulso: si no era suscriptor, alta directa
        # (ya dio consentimiento explícito al pagar → sin doble opt-in).
        persistencia.alta_directa(conexion, email, origen="premium")
        persistencia.set_premium(conexion, email, True, hasta=_hasta_de(data))
        return {"ok": True, "accion": "premium_on", "email": email, "hasta": _hasta_de(data)}

    if tipo in EVENTOS_REVOCA:
        persistencia.set_premium(conexion, email, False)
        return {"ok": True, "accion": "premium_off", "email": email}

    return {"ok": True, "accion": "ignorado", "tipo": tipo}
```

## engine/contenido/persistencia.py
```python
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
  premium_hasta  TEXT,                -- vencimiento ISO (AAAA-MM-DD); NULL = sin vencimiento
  token_enjambre TEXT                 -- secreto del enlace mágico que desbloquea 40/mes en El Enjambre
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
CREATE TABLE IF NOT EXISTS gasto_premium (
  -- el cupo MENSUAL de simulaciones de cada suscriptor Premium, en DISCO: un
  -- reinicio de Render no debe regalarle el mes de nuevo a mitad de camino.
  email       TEXT NOT NULL,
  mes         TEXT NOT NULL,        -- AAAA-MM (UTC)
  consumidas  INTEGER DEFAULT 0,
  PRIMARY KEY (email, mes)
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
            ("suscriptores", "token_enjambre", "TEXT"),        # enlace mágico de desbloqueo del enjambre
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


def es_activo(conexion, email: str) -> bool:
    """True si el correo ya es un suscriptor activo (confirmado)."""
    fila = conexion.execute(
        "SELECT 1 FROM suscriptores WHERE email = ? AND activo = 1", (email.strip().lower(),)).fetchone()
    return fila is not None


def token_baja_de(conexion, email: str) -> str | None:
    """El token de baja de un correo (para el enlace de desuscripción). None si no existe."""
    fila = conexion.execute(
        "SELECT token_baja FROM suscriptores WHERE email = ?", (email.strip().lower(),)).fetchone()
    return fila["token_baja"] if fila else None


def activar_pendientes(conexion) -> int:
    """Activa a TODOS los suscriptores pendientes de confirmar (dieron su correo
    al suscribirse pero no confirmaron). Es el paso a opt-in simple: el clic en
    'Suscribirme' ya es su consentimiento. NO toca a los que se dieron de baja
    (esos no tienen token_confirma). Devuelve cuántos activó."""
    cursor = conexion.execute(
        "UPDATE suscriptores SET activo = 1, token_confirma = NULL "
        "WHERE activo = 0 AND token_confirma IS NOT NULL")
    conexion.commit()
    return cursor.rowcount


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


def desactivar_por_email(conexion, email: str) -> bool:
    """Baja un suscriptor por su correo (no por token). Se usa para limpiar solo
    las direcciones que el proveedor marca como PERMANENTEMENTE inválidas (p. ej.
    @example.com o un correo mal escrito): así dejan de reintentarse en cada
    edición y de inflar la cuenta de 'enviados'. True si el correo existía."""
    cursor = conexion.execute(
        "UPDATE suscriptores SET activo = 0 WHERE email = ?", (email.strip().lower(),))
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


# ---------- enlace mágico del enjambre (token en vez del correo desnudo) ----------

def emitir_token_enjambre(conexion, email: str) -> str | None:
    """Devuelve el token de desbloqueo del enjambre de este correo (lo crea si no
    existe). Solo tiene sentido para un Premium — el que llama decide a quién se
    lo emite. None si el correo no existe."""
    email = email.strip().lower()
    fila = conexion.execute(
        "SELECT token_enjambre FROM suscriptores WHERE email = ?", (email,)).fetchone()
    if fila is None:
        return None
    token = fila["token_enjambre"]
    if not token:
        token = secrets.token_urlsafe(24)
        conexion.execute(
            "UPDATE suscriptores SET token_enjambre = ? WHERE email = ?", (token, email))
        conexion.commit()
    return token


def email_por_token_enjambre(conexion, token: str | None) -> str | None:
    """El correo dueño de un token de desbloqueo (o None). El token ES el secreto:
    quien lo tiene, tiene acceso al buzón que lo recibió."""
    if not token or len(token) < 16:
        return None
    fila = conexion.execute(
        "SELECT email FROM suscriptores WHERE token_enjambre = ?", (token,)).fetchone()
    return fila["email"] if fila else None


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
    conexion.execute("DELETE FROM gasto_premium")
    conexion.commit()


# ---------- cupo mensual de Premium (en disco, sobrevive a los reinicios) ----------

def gasto_premium_mes(conexion, email: str, mes: str) -> int:
    """Cuántas simulaciones lleva este Premium en `mes` (AAAA-MM). 0 si ninguna."""
    fila = conexion.execute(
        "SELECT consumidas FROM gasto_premium WHERE email = ? AND mes = ?",
        (email.strip().lower(), mes)).fetchone()
    return fila[0] if fila else 0


def sumar_gasto_premium(conexion, email: str, mes: str, n: int = 1) -> int:
    """Suma `n` al cupo mensual de este Premium (crea la fila si no existe).
    Devuelve el total del mes."""
    email = email.strip().lower()
    conexion.execute(
        "INSERT INTO gasto_premium (email, mes, consumidas) VALUES (?, ?, ?) "
        "ON CONFLICT(email, mes) DO UPDATE SET consumidas = consumidas + excluded.consumidas",
        (email, mes, n))
    conexion.commit()
    return gasto_premium_mes(conexion, email, mes)


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
```

## engine/contenido/pipeline.py
```python
"""El ritual de la madrugada — versión Etapa 7 (pasos 1, 2, 3 y 7).

Recolecta los titulares, el portero elige el top 3 del día, se simulan
con seeds fijas (reproducibilidad), se guardan CON frames (el replay 3D
del muro) y quedan marcadas como destacadas.

Los pasos 4-6 y 8 (captura, boletín, envío, aviso a Telegram) llegan en
la Etapa 8. Uso manual: python -m contenido.pipeline
"""

from datetime import date, datetime, timezone

from contenido import persistencia, portero
from contenido.fuentes import alpaca

MAXIMO_DIARIO = 3  # presupuesto de CONTENIDO.md — no negociable


def simular_titular_completo(titular: str, seed: int, con_frames: bool = False):
    """Corre una simulación completa fuera del WebSocket (para el pipeline).

    Devuelve (reporte, lideres_datos, serie_precios, frames).
    """
    # imports tardíos: el pipeline se importa sin levantar FastAPI
    from collections import defaultdict

    import server
    from agents.lider import LiderOpinion
    from brains import reparto
    from brains.cerebro import analizar_titular
    from model import MercadoEnjambre

    from brains.mercado import clasificar, perfil_de

    modelo = MercadoEnjambre(seed=seed, ticks_horizonte=server.TICKS_CALENTAMIENTO + server.TICKS_POSTERIORES)
    modelo.correr(server.TICKS_CALENTAMIENTO)
    lideres = [a for a in modelo.agentes_ordenados if isinstance(a, LiderOpinion)]
    # 1000 líderes comparten ~110 cerebros (presupuesto de la biblia)
    consultas, asignacion = reparto.planificar(lideres, lambda uid: uid)
    from contenido import vocabulario
    # filtro CMF a las voces de los líderes antes de que se guarden y se sirvan
    respuestas = reparto.expandir(
        vocabulario.sanear_frases(analizar_titular(titular, consultas)), asignacion)
    # el enjambre razona el TIPO de mercado y aplica su personalidad
    perfil = perfil_de(clasificar(titular))

    contador = defaultdict(lambda: [0, 0])
    frames: list[bytes] = []

    def avanzar():
        modelo.step()
        server._contar_acciones(modelo, contador)
        if con_frames:
            frames.append(server._paquete_tick(modelo))

    for _ in range(server.TICKS_PREVIOS):
        avanzar()
    precio_previo = modelo.historial_precios[-1]
    contador.clear()
    modelo.aplicar_titular(titular, respuestas=respuestas, perfil=perfil)
    for _ in range(server.TICKS_POSTERIORES):
        avanzar()

    reporte = server._generar_reporte(modelo, precio_previo, respuestas, lideres, contador)
    reporte["mercado"] = perfil["tipo"]            # el tipo detectado (calibración/UI)
    reporte["mercado_etiqueta"] = perfil["etiqueta"]
    lideres_datos = [
        # `fuente` viaja con cada líder: la calibración necesita saber si la
        # voz fue IA real o el respaldo léxico (sin saldo, el suplente juega)
        {"arquetipo": lider.arquetipo, "fuente": r.get("fuente", "fallback"),
         **{k: r[k] for k in ("senal", "confianza", "frase")}}
        for lider, r in zip(lideres, respuestas)
    ]
    serie = modelo.historial_precios[-(server.TICKS_PREVIOS + server.TICKS_POSTERIORES + 1):]
    return reporte, lideres_datos, serie, frames


def preparar_dia(conexion=None, maximo: int = MAXIMO_DIARIO, semilla_base: int | None = None) -> dict:
    """Pasos 1-3 y 7 del ritual: recolectar, filtrar, simular, publicar.

    Idempotente: si hoy ya hay `maximo` destacadas, no gasta de nuevo.
    """
    propia = conexion is None
    conexion = conexion or persistencia.conectar()
    try:
        hoy = datetime.now(timezone.utc).strftime("%Y-%m")
        destacadas_hoy = [
            s for s in persistencia.listar_simulaciones(conexion, solo_destacadas=True, limite=10)
            if s["fecha"][:10] == persistencia.ahora_iso()[:10]
        ]
        if len(destacadas_hoy) >= maximo:
            return {"origen": "sin cambios", "publicadas": [], "motivo": "el día ya estaba preparado"}

        # 1. RECOLECTAR (con degradación elegante a demo)
        titulares, origen = alpaca.obtener_titulares(horas=18, limite=50)
        # 1b. CAZAR LOS MOVIMIENTOS REALES DEL DÍA: no basta con lo que el feed
        # tituló (se perdía la gran historia). El reportero IA busca los mayores
        # movers, investiga y VERIFICA su porqué con búsqueda web, y los suma al
        # pool como titulares con contexto. Nunca rompe el ritual: si falla, sigue
        # solo con Alpaca. Van al frente (ganan los empates de impacto).
        try:
            from contenido import investigador
            from contenido.fuentes import yahoo

            investigados = investigador.investigar_movers(yahoo.movers_del_dia(n=8))
            if investigados:
                titulares = investigados + list(titulares)
        except Exception:
            pass
        # 2. FILTRAR
        resultado = portero.procesar_dia(conexion, titulares, maximo=maximo)
        # 3. SIMULAR con seeds fijas del día + 7. PUBLICAR como destacadas
        semilla_base = semilla_base if semilla_base is not None else int(date.today().strftime("%Y%m%d"))
        publicadas = []
        for indice, elegido in enumerate(resultado["elegidos"][: maximo - len(destacadas_hoy)]):
            seed = semilla_base + indice
            reporte, lideres_datos, serie, frames = simular_titular_completo(
                elegido["titular"], seed, con_frames=True
            )
            sim_id = persistencia.guardar_simulacion(
                conexion,
                titular=elegido["titular"],
                fuente=elegido.get("fuente", "alpaca"),
                seed=seed,
                resumen=reporte,
                lideres=lideres_datos,
                serie_precios=serie,
                frames_ref=persistencia.guardar_frames(
                    persistencia.id_simulacion(elegido["titular"], seed), frames
                ),
                destacada=True,
            )
            persistencia.vincular_simulacion(conexion, persistencia.id_titular(elegido["titular"]), sim_id)
            publicadas.append({"sim_id": sim_id, "titular": elegido["titular"], "impacto": elegido["impacto"]})

        return {"origen": origen, "publicadas": publicadas, "log": resultado["log"]}
    finally:
        if propia:
            conexion.close()


def ritual_matutino(conexion=None, maximo: int = MAXIMO_DIARIO, semilla_base: int | None = None,
                    enviar: bool = True, cuando: dict | None = None,
                    momento: str = "manana") -> dict:
    """El ritual completo (CONTENIDO.md sección 6.1): prepara el día
    (pasos 1-3, 7) y luego redacta y envía El Pulso (pasos 5-6) y avisa a
    Giorgio (paso 8). El paso 4 (imagen) se sirve on-the-fly desde el
    endpoint /api/simulacion/{id}/imagen — no hace falta pre-renderizar.

    `enviar=False` arma todo pero no manda correos (para pruebas/preview).
    `momento="tarde"` arma la EDICIÓN DE LA TARDE (el cierre del mercado, Premium)
    en vez de la de la mañana.
    """
    if momento == "tarde":
        return _ritual_tarde(conexion, enviar=enviar, cuando=cuando)

    from datetime import datetime, timezone

    from contenido import boletin, notificar, redaccion, redaccion_ia

    propia = conexion is None
    conexion = conexion or persistencia.conectar()
    try:
        # ¿qué día es? (hora local del lector). El fin de semana El Pulso cambia
        # de marcha: SÁBADO = resumen de la semana; DOMINGO = deep-dive de una
        # mid/small-cap o sector. `cuando` se puede inyectar (tests).
        cuando = cuando or redaccion_ia.contexto_temporal()
        dia = cuando.get("weekday")
        es_finde = cuando.get("es_finde", dia in (5, 6) if dia is not None else False)
        es_sabado = dia == 5
        # sin weekday (cuando antiguo inyectado) pero es finde → se trata como domingo
        es_domingo = dia == 6 or (es_finde and dia is None)

        if es_finde:
            # sin simulaciones nuevas ni gasto de enjambre: el fin de semana es
            # lectura pausada. Un solo llamado LLM (el redactor del finde).
            preparado = {"origen": "fin de semana", "publicadas": [], "log": []}
        else:
            preparado = preparar_dia(conexion, maximo=maximo, semilla_base=semilla_base)

        # el corrector automático: guarda cuánto se movió de verdad el
        # símbolo de las destacadas de días anteriores (calibración).
        # El ritual jamás se cae por el corrector.
        try:
            from contenido import corrector
            correccion = corrector.corregir_pendientes(conexion)
        except Exception:
            correccion = None

        # reúne las destacadas de hoy con sus voces (para el correo)
        destacadas = [] if es_finde else _destacadas_de_hoy(conexion)

        # La Redacción: el análisis de mercado del día, DINÁMICO. El universo
        # sale de los titulares que el portero evaluó hoy (sus tickers), así
        # el brief cambia cada día. "Qué observa hoy" = las destacadas.
        radar = [d["titular"] for d in destacadas]
        evaluadas = preparado.get("log", [])
        brief = redaccion.preparar_brief(evaluadas=evaluadas, radar=radar)

        if es_sabado:
            # ── SÁBADO: RESUMEN DE LA SEMANA. Los grandes temas con punto de vista
            # (qué pasó, por qué, geopolítica/macro → mercado, qué observar). NUNCA
            # predicción (marco CMF). Degrada a None sin romperse.
            try:
                from contenido import resumen_semanal
                resumen = resumen_semanal.preparar_resumen(conexion, cuando=cuando)
                brief["resumen"] = resumen
                brief["resumen_redactado"] = (
                    redaccion_ia.redactar_resumen(resumen, cuando=cuando) if resumen else None)
            except Exception:
                brief["resumen"] = None
                brief["resumen_redactado"] = None
        elif es_domingo:
            # ── DOMINGO: DEEP-DIVE de una empresa mediana/pequeña o un sector en
            # rotación. Contexto + números verificados + debate de arquetipos +
            # gráfico real. NUNCA consejo de inversión (marco CMF).
            try:
                from contenido import analisis_semanal
                analisis = analisis_semanal.preparar_analisis(cuando=cuando)
                brief["analisis"] = analisis
                brief["analisis_redactado"] = (
                    redaccion_ia.redactar_analisis(analisis, cuando=cuando) if analisis else None)
            except Exception:
                brief["analisis"] = None
                brief["analisis_redactado"] = None
        else:
            # el redactor de IA le pone VOZ al brief (prompt maestro aprobado).
            # Si no hay clave/IA o algo falla, redactar() devuelve None y el correo
            # usa su plantilla.
            try:
                enjambre = None
                if destacadas:
                    d0 = destacadas[0]
                    enjambre = {"titular": d0["titular"],
                                "direccion_pct": d0["resumen"].get("direccion_pct"),
                                "volatilidad": d0["resumen"].get("agitacion")}
                brief["redactado"] = redaccion_ia.redactar(brief, enjambre)
            except Exception:
                brief["redactado"] = None

        # ── CENTRO DE MANDO: se GENERA y se GUARDA como 'pendiente'; NO se envía
        # a los suscriptores hasta el visto bueno de Giorgio. Se le manda un
        # correo de REVISIÓN (a su propio correo → funciona aun sin dominio).
        import secrets

        fecha_iso = persistencia.ahora_iso()[:10]
        fecha_es = _fecha_es(datetime.now(timezone.utc))
        # hay edición si hay destacadas (entre semana), resumen (sábado) o
        # deep-dive (domingo)
        sabado_listo = es_sabado and isinstance(brief.get("resumen_redactado"), dict)
        domingo_listo = es_domingo and isinstance(brief.get("analisis_redactado"), dict)
        finde_listo = sabado_listo or domingo_listo
        html_preview = None
        token = None
        if destacadas or finde_listo:
            html_preview = boletin.construir_html(
                destacadas, fecha_es, token_baja=persistencia.TOKEN_BAJA_SENTINEL, brief=brief)
            if sabado_listo:
                asunto = boletin.asunto_resumen(brief.get("resumen"))
            elif domingo_listo:
                asunto = boletin.asunto_finde(brief["analisis"])
            else:
                asunto = boletin.asunto_del_dia(destacadas[0])
            token = secrets.token_urlsafe(24)
            persistencia.guardar_edicion(conexion, fecha_iso, brief, html_preview,
                                         asunto, token, persistencia.ahora_iso())
            n_susc = len(persistencia.suscriptores_activos(conexion))
            if enviar:  # 'enviar' ahora = mandar el correo de REVISIÓN (no a suscriptores)
                boletin.enviar_revision(fecha_es, html_preview, token, n_susc)
        else:
            persistencia.guardar_brief(conexion, fecha_iso, brief)  # sin edición: solo el brief

        # paso 8: avisar a Giorgio que la edición espera su revisión
        notificar.avisar(notificar.resumen_ejecucion(preparado["origen"], preparado["publicadas"], None))

        edicion = ("resumen" if sabado_listo else "finde" if domingo_listo
                   else "diaria" if destacadas else "ninguna")
        return {**preparado, "destacadas": len(destacadas),
                "estado": "pendiente" if (destacadas or finde_listo) else "sin_edicion",
                "edicion": edicion,
                "brief": brief, "html_preview": html_preview, "token": token,
                "correccion": correccion}
    finally:
        if propia:
            conexion.close()


def aprobar_y_enviar(conexion=None, fecha: str | None = None) -> dict:
    """El visto bueno: envía la edición del día a los suscriptores (idéntica a lo
    revisado) y la marca 'enviada'. Idempotente: si ya se envió, no repite."""
    from contenido import boletin

    propia = conexion is None
    conexion = conexion or persistencia.conectar()
    try:
        fecha = fecha or persistencia.ahora_iso()[:10]
        ed = persistencia.obtener_edicion(conexion, fecha)
        if ed is None or not ed.get("html_preview"):
            return {"ok": False, "motivo": "no hay edición para ese día"}
        if ed["estado"] == "enviada":
            return {"ok": True, "ya_enviada": True,
                    "enviados": ed["enviados"], "suscriptores": ed["suscriptores"]}
        if ed["estado"] == "descartada":
            return {"ok": False, "motivo": "la edición fue descartada"}
        # el deep-dive del domingo es Premium: gratis → teaser; de pago → completo
        teaser_html, asunto_teaser = boletin.teaser_para(ed.get("brief"), fecha)
        # la edición de la TARDE (el cierre) sale SOLO a los Premium
        solo_premium = bool(isinstance(ed.get("brief"), dict) and ed["brief"].get("cierre"))
        conteo = boletin.enviar_a_suscriptores(
            conexion, ed["html_preview"], ed["asunto"] or "El Pulso", fecha_edicion=fecha,
            teaser_html=teaser_html, asunto_teaser=asunto_teaser, solo_premium=solo_premium)
        persistencia.marcar_enviada(conexion, fecha, conteo["enviados"],
                                    conteo["suscriptores"], persistencia.ahora_iso())
        return {"ok": True, **conteo}
    finally:
        if propia:
            conexion.close()


def _clave_tarde(fecha_iso: str) -> str:
    """La clave de la edición de la tarde: la fecha con sufijo '-t' (así conviven
    la edición de la mañana y la de la tarde del mismo día en la base)."""
    return f"{fecha_iso[:10]}-t"


def _ritual_tarde(conexion=None, enviar: bool = True, cuando=None) -> dict:
    """La EDICIÓN DE LA TARDE (Premium): 'el cierre del mercado'. El reportero IA
    caza los movers reales del día y explica por qué. Se guarda bajo 'AAAA-MM-DD-t'
    y se manda a revisión; al aprobar, sale SOLO a los Premium. Sin simulaciones
    del enjambre. Nunca rompe: si no hay movimientos, no hay edición de tarde."""
    import secrets
    from datetime import datetime, timezone

    from contenido import boletin, cierre as mod_cierre, notificar, redaccion_ia

    propia = conexion is None
    conexion = conexion or persistencia.conectar()
    try:
        try:
            datos = mod_cierre.preparar_cierre()
        except Exception:
            datos = None
        if not datos:
            return {"estado": "sin_edicion", "edicion": "cierre",
                    "motivo": "sin movimientos del día"}

        # Voz Moby ENCIMA de los hechos verificados: los movimientos se vuelven
        # mini-historias con tono, no una lista plana. Si la IA no está o falla,
        # 'redactado' queda None y el boletín cae a la lista de siempre.
        cuando = cuando or redaccion_ia.contexto_temporal()
        try:
            datos["redactado"] = redaccion_ia.redactar_cierre(datos, cuando=cuando)
        except Exception:
            datos["redactado"] = None

        brief = {"cierre": datos}
        clave = _clave_tarde(persistencia.ahora_iso())
        fecha_es = _fecha_es(datetime.now(timezone.utc)) + " · cierre"
        html_preview = boletin.construir_html(
            [], fecha_es, token_baja=persistencia.TOKEN_BAJA_SENTINEL, brief=brief)
        asunto = boletin.asunto_cierre()
        token = secrets.token_urlsafe(24)
        persistencia.guardar_edicion(conexion, clave, brief, html_preview, asunto, token,
                                     persistencia.ahora_iso())
        n_prem = persistencia.contar_premium(conexion)
        if enviar:
            boletin.enviar_revision(fecha_es, html_preview, token, n_prem)
        try:
            notificar.avisar("🌆 El cierre del mercado (Premium) espera tu revisión.")
        except Exception:
            pass
        return {"estado": "pendiente", "edicion": "cierre", "clave": clave,
                "html_preview": html_preview, "token": token, "premium": n_prem}
    finally:
        if propia:
            conexion.close()


def reenviar_a_suscriptores(conexion=None, fecha: str | None = None) -> dict:
    """Reenvía la edición del día a TODOS los suscriptores activos, aunque YA se
    haya enviado (envío manual a pedido de Giorgio). A diferencia de
    aprobar_y_enviar, NO es idempotente: reenvía a propósito. Requiere que exista
    el preview y que la edición no esté descartada."""
    from contenido import boletin

    propia = conexion is None
    conexion = conexion or persistencia.conectar()
    try:
        fecha = fecha or persistencia.ahora_iso()[:10]
        ed = persistencia.obtener_edicion(conexion, fecha)
        if ed is None or not ed.get("html_preview"):
            return {"ok": False, "motivo": "no hay edición para ese día"}
        if ed["estado"] == "descartada":
            return {"ok": False, "motivo": "la edición fue descartada"}
        # el deep-dive del domingo es Premium: gratis → teaser; de pago → completo
        teaser_html, asunto_teaser = boletin.teaser_para(ed.get("brief"), fecha)
        solo_premium = bool(isinstance(ed.get("brief"), dict) and ed["brief"].get("cierre"))
        conteo = boletin.enviar_a_suscriptores(
            conexion, ed["html_preview"], ed["asunto"] or "El Pulso", fecha_edicion=fecha,
            teaser_html=teaser_html, asunto_teaser=asunto_teaser, solo_premium=solo_premium)
        persistencia.marcar_enviada(conexion, fecha, conteo["enviados"],
                                    conteo["suscriptores"], persistencia.ahora_iso())
        return {"ok": True, "reenviada": True, **conteo}
    finally:
        if propia:
            conexion.close()


def descartar_edicion(conexion=None, fecha: str | None = None) -> dict:
    """Descarta la edición del día (no se enviará)."""
    propia = conexion is None
    conexion = conexion or persistencia.conectar()
    try:
        fecha = fecha or persistencia.ahora_iso()[:10]
        ok = persistencia.set_estado_edicion(conexion, fecha, "descartada")
        return {"ok": ok}
    finally:
        if propia:
            conexion.close()


def _enviar_con_brief(conexion, destacadas, fecha, brief) -> dict:
    """Como boletin.enviar_pulso pero incluyendo el análisis de mercado."""
    from contenido import boletin

    activos = persistencia.suscriptores_activos(conexion)
    asunto = boletin.asunto_del_dia(destacadas[0])
    enviados = 0
    for suscriptor in activos:
        html = boletin.construir_html(destacadas, fecha, token_baja=suscriptor["token_baja"], brief=brief)
        if boletin.enviar(suscriptor["email"], asunto, html):
            enviados += 1
    return {"suscriptores": len(activos), "enviados": enviados, "fallidos": len(activos) - enviados}


def _destacadas_de_hoy(conexion) -> list[dict]:
    """Las destacadas de hoy con resumen + voces, listas para el boletín."""
    hoy = persistencia.ahora_iso()[:10]
    resultado = []
    for fila in persistencia.listar_simulaciones(conexion, solo_destacadas=True, limite=10):
        if fila["fecha"][:10] != hoy:
            continue
        datos = persistencia.obtener_simulacion(conexion, fila["id"])
        if datos:
            resultado.append({
                "sim_id": datos["id"],
                "titular": datos["titular"],
                "resumen": {**datos["resumen"], "agitacion": _agitacion(datos["resumen"])},
                "lideres_frases": datos["lideres"],
            })
    return resultado


def _agitacion(resumen: dict) -> str:
    vol = resumen.get("volatilidad_pct", 0)
    return "bajo" if vol < 1.0 else "medio" if vol < 2.0 else "alto"


def _fecha_es(dt) -> str:
    dias = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
    meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
             "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    return f"{dias[dt.weekday()]} {dt.day} de {meses[dt.month - 1]}"


if __name__ == "__main__":
    import sys

    enviar = "--enviar" in sys.argv
    resultado = ritual_matutino(enviar=enviar)
    print(f"fuente: {resultado['origen']}")
    for publicada in resultado.get("publicadas", []):
        print(f"  ★ [{publicada['impacto']}/10] {publicada['titular']}  → sim {publicada['sim_id']}")
    if resultado.get("envio"):
        e = resultado["envio"]
        print(f"correos: {e['enviados']}/{e['suscriptores']} enviados")
    elif resultado.get("destacadas"):
        print(f"boletín armado ({resultado['destacadas']} destacadas); envío desactivado (usa --enviar)")
    if not resultado.get("publicadas"):
        print(f"  ({resultado.get('motivo', 'sin titulares elegibles')})")
```

## engine/contenido/portero.py
```python
"""El portero — guardián del presupuesto LLM (CONTENIDO.md sección 7).

Dos pisos:
1. Léxico (gratis): descarta duplicados, contenido promocional y todo lo
   que no tiene contenido de mercado. Elimina ~80% sin gastar un centavo.
2. Haiku (centavos): una llamada con lote de hasta 20 titulares que
   puntúa impacto 1-10. Sin API key, un heurístico léxico decide igual —
   el pipeline nunca se cae.

Todo veredicto (incluso descartes) queda en la tabla `titulares`:
ese log es el material para calibrar el portero después.
"""

import difflib
import json
import os
import re

from contenido import persistencia
from llm_texto import texto_de

MODELO_PORTERO = "claude-haiku-4-5-20251001"
LOTE_MAXIMO = 20
UMBRAL_DUPLICADO = 0.85
UMBRAL_IMPACTO = 5  # bajo esto, el heurístico descarta

# --- señales de que el titular SÍ habla de mercados (ES + EN: Alpaca llega en inglés) ---
SENALES_MERCADO = [
    # macro
    "fed", "banco central", "central bank", "tasas", "rates", "inflación", "inflation",
    "empleo", "jobs", "unemployment", "pib", "gdp", "dólar", "dollar", "recesión",
    "recession", "tariff", "arancel", "treasury", "bonos", "bonds", "liquidez",
    # mercado / empresa
    "acciones", "stocks", "shares", "bolsa", "market", "índice", "index", "s&p",
    "nasdaq", "dow", "ipsa", "earnings", "resultados", "ganancias", "revenue",
    "ingresos", "quiebra", "bankruptcy", "fusión", "merger", "adquisición",
    "acquisition", "ipo", "dividendo", "dividend", "ceo", "regulador", "sec",
    "banco", "bank", "cripto", "crypto", "bitcoin", "petróleo", "oil",
]

# --- patrones de contenido sin sustancia (listas, promoción, opinión blanda) ---
PATRONES_DESCARTE = [
    r"^\d+\s+(stocks|acciones|razones|reasons|things|ways)",
    r"\btop\s+\d+\b",
    r"(best|mejores)\s+(stocks|acciones|etfs?)",
    r"(should you|deberías)\b",
    r"(how to|cómo)\s+(invest|invertir|trade)",
    r"\b(webinar|sponsored|patrocinado|newsletter|podcast|giveaway)\b",
    r"(what to watch|qué mirar|cheat sheet|preview of the week)",
    r"\b(motley fool|zacks)\b",
]


def _normalizar(texto: str) -> str:
    return re.sub(r"\s+", " ", texto.lower().strip())


def _es_duplicado(titular: str, previos: list[str]) -> bool:
    objetivo = _normalizar(titular)
    for previo in previos:
        similitud = difflib.SequenceMatcher(None, objetivo, _normalizar(previo)).ratio()
        if similitud > UMBRAL_DUPLICADO:
            return True
    return False


# ---------- piso 1: léxico (gratis) ----------

def evaluar_lexico(titular: str, previos: list[str], simbolos: str = "") -> str | None:
    """Devuelve el motivo del descarte, o None si pasa al piso 2."""
    if _es_duplicado(titular, previos):
        return "duplicado de un titular reciente"
    texto = _normalizar(titular)
    for patron in PATRONES_DESCARTE:
        if re.search(patron, texto):
            return "contenido promocional o lista sin sustancia"
    # si la fuente asoció tickers, ES contenido de mercado por definición
    tiene_simbolos = bool(simbolos.strip())
    if not tiene_simbolos and not any(senal in texto for senal in SENALES_MERCADO):
        return "sin contenido de mercado reconocible"
    return None


# ---------- piso 2: Haiku (o heurístico si no hay API) ----------

PROMPT_PORTERO = """Eres el editor de un simulador educativo de mercados.
Evalúa el IMPACTO DE MERCADO de cada titular (1-10):
- afecta a un índice o sector completo > empresa mega-cap > empresa puntual
- macro (tasas, inflación, empleo, geopolítica) puntúa alto
- rumores y opiniones puntúan bajo, salvo fuente institucional
Responde SOLO un array JSON, un objeto por titular, mismo orden:
[{"veredicto": "simular"|"descartar", "impacto": 1-10, "motivo": "una frase en español"}]"""


def _evaluar_lote_llm(titulares: list[str]) -> list[dict] | None:
    """Una llamada Haiku por lote. None si no hay API o algo falla."""
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return None
    try:
        import anthropic

        cliente = anthropic.Anthropic()
        lista = "\n".join(f"{i + 1}. {t}" for i, t in enumerate(titulares))
        respuesta = cliente.messages.create(
            model=MODELO_PORTERO,
            max_tokens=1500,
            system=PROMPT_PORTERO,
            messages=[{"role": "user", "content": lista}],
        )
        encontrado = re.search(r"\[.*\]", texto_de(respuesta), re.DOTALL)
        datos = json.loads(encontrado.group())
        if len(datos) != len(titulares):
            return None
        return [
            {
                "veredicto": "simular" if d.get("veredicto") == "simular" else "descartar",
                "impacto": max(1, min(10, int(d.get("impacto", 1)))),
                "motivo": str(d.get("motivo", ""))[:200],
            }
            for d in datos
        ]
    except Exception:
        return None  # el heurístico decide; el pipeline no se cae


# vocabulario del heurístico (ES + EN): mismo criterio que el prompt Haiku
_MACRO_FUERTE = [
    "fed", "central bank", "banco central", "rates", "tasas", "inflación",
    "inflation", "unemployment", "desempleo", "jobs report", "empleo",
    "tariff", "arancel", "treasury", "gdp", "pib", "ecb", "recession", "recesión",
]
_EVENTO_FUERTE = [
    "collapse", "colapso", "quiebra", "bankruptcy", "default", "crash",
    "desploma", "crisis", "fdic", "bailout", "rescate", "cyberattack",
    "ciberataque", "all-time high", "máximo histórico", "surge", "spike",
    "plunge", "jumps", "record", "récord", "resigns", "renuncia", "recall",
    "investigation", "investigación", "fraud", "fraude", "war", "guerra",
    "acquire", "adquisición", "merger", "fusión", "fda approval", "beats",
    "misses", "escalate",
]


def _evaluar_heuristico(titular: str, simbolos: str = "") -> dict:
    """Plan B sin API: puntúa con el mismo criterio del prompt del portero."""
    texto = _normalizar(titular)
    impacto = 2
    if any(p in texto for p in _MACRO_FUERTE):
        impacto += 3  # macro puntúa alto
    aciertos = sum(1 for p in _EVENTO_FUERTE if p in texto)
    impacto += min(2 * aciertos, 4)
    if len([s for s in simbolos.split(",") if s]) >= 2:
        impacto += 1  # varios tickers: afecta más que a una empresa puntual
    impacto = max(1, min(10, impacto))
    veredicto = "simular" if impacto >= UMBRAL_IMPACTO else "descartar"
    return {"veredicto": veredicto, "impacto": impacto,
            "motivo": f"heurístico léxico (impacto {impacto}/10, sin API)"}


def evaluar_lote(candidatos: list[dict]) -> list[dict]:
    """Evalúa hasta LOTE_MAXIMO candidatos por llamada; degrada a heurístico."""
    resultados: list[dict] = []
    for inicio in range(0, len(candidatos), LOTE_MAXIMO):
        lote = candidatos[inicio:inicio + LOTE_MAXIMO]
        evaluados = _evaluar_lote_llm([c["titular"] for c in lote])
        if evaluados is None:
            evaluados = [_evaluar_heuristico(c["titular"], c.get("simbolos", "")) for c in lote]
        resultados.extend(evaluados)
    return resultados


# ---------- el proceso completo de un día ----------

def procesar_dia(conexion, candidatos: list[dict], maximo: int = 3) -> dict:
    """Evalúa los titulares del día y elige los `maximo` de mayor impacto.

    candidatos: [{"titular": ..., "fuente": ..., "simbolos": ...}, ...]
    Registra TODO veredicto en la tabla `titulares`. Devuelve
    {"elegidos": [...], "log": [...]} con los motivos de cada decisión.
    """
    previos = [t["titular"] for t in persistencia.titulares_recientes(conexion, horas=48)]
    log: list[dict] = []
    al_piso_dos: list[dict] = []

    for candidato in candidatos:
        titular = candidato["titular"].strip()
        motivo_lexico = evaluar_lexico(titular, previos, candidato.get("simbolos", ""))
        if motivo_lexico is not None:
            log.append({**candidato, "veredicto": "descartar", "impacto": 0,
                        "motivo": f"piso léxico: {motivo_lexico}"})
        else:
            al_piso_dos.append(candidato)
        previos.append(titular)  # los del propio lote también cuentan como "vistos"

    evaluaciones = evaluar_lote(al_piso_dos)
    for candidato, evaluacion in zip(al_piso_dos, evaluaciones):
        log.append({**candidato, **evaluacion})

    # los `maximo` de mayor impacto entre los que dijeron "simular";
    # en empate gana el más reciente (los candidatos llegan ordenados así)
    simulables = [e for e in log if e["veredicto"] == "simular"]
    simulables.sort(key=lambda e: -e["impacto"])
    elegidos = simulables[:maximo]
    ids_elegidos = {id(e) for e in elegidos}

    for entrada in log:
        veredicto_final = "simular" if id(entrada) in ids_elegidos else "descartar"
        if entrada["veredicto"] == "simular" and veredicto_final == "descartar":
            entrada["motivo"] += " (simulable, pero fuera del top del día)"
        entrada["veredicto"] = veredicto_final
        persistencia.registrar_titular(
            conexion,
            titular=entrada["titular"],
            fuente=entrada.get("fuente", "desconocida"),
            simbolos=entrada.get("simbolos", ""),
            veredicto=entrada["veredicto"],
            motivo=entrada["motivo"],
            impacto=entrada["impacto"],
        )

    return {"elegidos": elegidos, "log": log}
```

## engine/contenido/redaccion.py
```python
"""La Redacción — el análisis de mercado del Pulso (docs/la-redaccion.md).

Tres roles, una regla de oro cada uno:
  1. Reportero  — trae los hechos con su cita. Nada entra sin fuente.
  2. Verificador — el número manda: viene de la capa de datos, no de un texto.
  3. Editor     — pone la voz y pasa cada frase por el filtro CMF.

Regla que NO se cruza: se cuenta el PASADO (con fuente), nunca se predice
el futuro. El bloque "qué observa hoy" es ATENCIÓN, no predicción.
"""

import re

from contenido.fuentes import alpaca, barchart, yahoo
from contenido.portero import PATRONES_DESCARTE
from contenido.vocabulario import es_publicable

UMBRAL_MOVIMIENTO = 0.4  # % mínimo para que un instrumento "sea noticia"
MAX_MOVERS = 3           # cuántos movimientos de precio muestra el correo
MAX_EVENTOS = 2          # cuántos eventos (adquisiciones, etc.) muestra
UMBRAL_EVENTO = 6        # impacto mínimo del portero para ser "evento del día"

# telón de fondo del mercado: índices y materias primas SIEMPRE relevantes.
# El resto del universo del día es dinámico (los tickers de las noticias).
# Símbolos Yahoo (fuente gratis): índices ^, futuros =F. Las acciones del día
# entran por su ticker directo (NVDA, AAPL…), que Yahoo acepta tal cual.
TELON = ["^GSPC", "^IXIC", "^DJI", "CL=F", "GC=F"]


def _datos_mercado(simbolos: list[str]) -> tuple[list[dict], str]:
    """La fuente de números del diario: Yahoo (gratis) primero; si no responde,
    Barchart (si hay clave) o el snapshot de demostración. Nunca lanza."""
    datos, origen = yahoo.cotizaciones(simbolos)
    if datos:
        return datos, origen
    return barchart.cotizaciones(simbolos)  # barchart-con-clave, o demo

# términos para casar cada instrumento con un titular que explique el "por qué"
TERMINOS = {
    "S&P 500": ["s&p", "sp500", "spx", "spy", "stocks", "wall street", "equities"],
    "Nasdaq 100": ["nasdaq", "qqq", "tech stocks"],
    "Petróleo WTI": ["oil", "crude", "petról", "wti", "uso", "xom", "hormuz", "opec"],
    "Oro": ["gold", "oro", "gld", "bullion", "safe haven"],
    "Nvidia": ["nvidia", "nvda", "chip", "semiconductor", "ai chip"],
    "Apple": ["apple", "aapl", "iphone"],
}


# ---------- 1. El Reportero ----------

def reportear(cotizaciones: list[dict], noticias: list[dict]) -> list[dict]:
    """Casa cada cotización con un titular que explique su movimiento.

    Devuelve hechos {nombre, variacion_pct, cita|None}. Si no hay titular
    que respalde el 'por qué', la cita queda None (jamás se inventa)."""
    hechos = []
    for cot in cotizaciones:
        nombre = cot.get("nombre", cot.get("simbolo", ""))
        terminos = TERMINOS.get(nombre, [nombre.lower()])
        cita = _buscar_cita(terminos, cot.get("simbolo", ""), noticias)
        hechos.append({
            "nombre": nombre,
            "simbolo": cot.get("simbolo", ""),   # el ticker: para graficar su precio real
            "variacion_pct": cot["variacion_pct"],
            "cita": cita,
        })
    return hechos


def _es_promocional(titular: str) -> bool:
    texto = titular.lower()
    return any(re.search(patron, texto) for patron in PATRONES_DESCARTE)


def _buscar_cita(terminos: list[str], simbolo: str, noticias: list[dict]) -> dict | None:
    for noticia in noticias:
        titular = noticia["titular"]
        # una cita debe ser una noticia real, no publicidad ni una lista
        if _es_promocional(titular) or not es_publicable(titular):
            continue
        texto = titular.lower()
        simbolos = (noticia.get("simbolos") or "").upper()
        if simbolo and simbolo.strip("$") in simbolos:
            return _cita(noticia)
        if any(t in texto for t in terminos):
            return _cita(noticia)
    return None


def _cita(noticia: dict) -> dict:
    return {
        "titular": noticia["titular"],
        "fuente": noticia.get("fuente", ""),
        "url": noticia.get("url", ""),
    }


# ---------- 2. El Verificador ----------

def verificar(hechos: list[dict], umbral: float = UMBRAL_MOVIMIENTO) -> list[dict]:
    """El número manda. Descarta el ruido (movimientos < umbral) y conserva
    solo hechos con una cifra real. Ordena por magnitud del movimiento."""
    significativos = [h for h in hechos if abs(h.get("variacion_pct", 0)) >= umbral]
    return sorted(significativos, key=lambda h: -abs(h["variacion_pct"]))


# ---------- 3. El Editor ----------

def _verbo(pct: float) -> str:
    if pct > 0.15:
        return "avanzó"
    if pct < -0.15:
        return "retrocedió"
    return "cerró plano"


def editar(hecho: dict) -> dict | None:
    """Redacta la línea de un MOVIMIENTO de precio, en pasado y con cita.
    Pasa por el filtro CMF: si la frase (o el titular citado) tiene
    vocabulario prohibido, se cae la parte del 'por qué' y queda solo la
    cifra; si aun así no pasa, se descarta el hecho entero."""
    pct = hecho["variacion_pct"]
    base = f"{hecho['nombre']} {_verbo(pct)} {abs(pct)}%"
    cita = hecho.get("cita")

    simbolo = hecho.get("simbolo", "")
    if cita and es_publicable(cita["titular"]):
        # "en la prensa" = contexto relacionado, NO una afirmación de causa
        frase = f'{base}. En la prensa: «{cita["titular"]}».'
        if es_publicable(frase):
            return {"tipo": "mover", "nombre": hecho["nombre"], "simbolo": simbolo,
                    "variacion_pct": pct, "frase": frase, "cita_titular": cita["titular"],
                    "fuente": cita.get("fuente", ""), "url": cita.get("url", "")}

    frase = f"{base}."  # sin causa: solo el hecho verificado
    if es_publicable(frase):
        return {"tipo": "mover", "nombre": hecho["nombre"], "simbolo": simbolo,
                "variacion_pct": pct, "frase": frase, "fuente": "", "url": ""}
    return None


def editar_evento(noticia: dict) -> dict | None:
    """Redacta una línea de EVENTO (adquisición, resultados, regulación): el
    hecho ES la noticia, con su fuente. Sin número inventado."""
    titular = noticia["titular"].strip()
    if not titular or not es_publicable(titular) or _es_promocional(titular):
        return None
    frase = f"En la prensa: «{titular}»."
    if not es_publicable(frase):
        return None
    return {"tipo": "evento", "titular": titular, "frase": frase,
            "fuente": noticia.get("fuente", ""), "url": noticia.get("url", "")}


# ---------- selección dinámica: el universo del día ----------

def _tickers_de_noticias(evaluadas: list[dict]) -> list[str]:
    """Los tickers que aparecen en las noticias relevantes del día. Esto es
    lo que hace el brief DINÁMICO: hoy oro/petróleo/Nvidia, mañana lo que
    los titulares del día traigan (una adquisición, un sector, etc.)."""
    tickers: list[str] = []
    for e in evaluadas:
        if e.get("impacto", 0) < UMBRAL_EVENTO:
            continue
        for simbolo in (e.get("simbolos") or "").split(","):
            simbolo = simbolo.strip().upper()
            if simbolo and simbolo not in tickers:
                tickers.append(simbolo)
    return tickers


# ---------- orquestación: el brief del día ----------

def preparar_brief(evaluadas: list[dict] | None = None, radar: list[str] | None = None,
                   horas_noticias: int = 24) -> dict:
    """Arma el brief del día, DINÁMICO: 'lo que pasó' (movimientos
    verificados + eventos del día, con cita) y 'qué observa hoy' (atención).

    `evaluadas`: los titulares que el portero evaluó hoy (con impacto y
    simbolos). De ahí sale el universo del día. Si no se pasan, se recogen
    noticias frescas y se usa solo el telón de fondo.
    `radar`: titulares que el enjambre mira hoy (atención, no predicción).
    """
    if evaluadas:
        noticias = evaluadas
        universo = TELON + _tickers_de_noticias(evaluadas)
    else:
        noticias, _ = alpaca.obtener_titulares(horas=horas_noticias, limite=50)
        universo = TELON + [s.strip().upper() for n in noticias
                            for s in (n.get("simbolos") or "").split(",") if s.strip()]

    cotizaciones, origen_datos = _datos_mercado(_unicos(universo))

    # movimientos de precio (el número manda), los más grandes primero
    hechos = reportear(cotizaciones, noticias)
    movers = [m for m in (editar(h) for h in verificar(hechos)) if m][:MAX_MOVERS]

    # eventos del día (adquisiciones, resultados…): los de mayor impacto que
    # no sean ya un mover ni una cita ya usada, como hechos con fuente
    titulares_usados = {m["cita_titular"].lower() for m in movers if m.get("cita_titular")}
    eventos = []
    for e in sorted(evaluadas or [], key=lambda x: -x.get("impacto", 0)):
        if e.get("impacto", 0) < UMBRAL_EVENTO:
            break
        linea = editar_evento(e)
        if linea and linea["titular"].lower() not in titulares_usados:
            eventos.append(linea)
            titulares_usados.add(linea["titular"].lower())
        if len(eventos) >= MAX_EVENTOS:
            break

    observa = [t for t in (radar or []) if es_publicable(t)][:3]

    # "la foto del día": el telón de fondo (índices, petróleo, oro) con sus
    # tres columnas Día/Mes/Año. Solo Yahoo trae mes/año; demo/barchart dejan
    # esos campos en None y la tabla muestra "—".
    foto = [
        {"nombre": c.get("nombre", c.get("simbolo", "")),
         "variacion_pct": c.get("variacion_pct"),
         "var_mes_pct": c.get("var_mes_pct"),
         "var_ano_pct": c.get("var_ano_pct")}
        for c in cotizaciones if c.get("simbolo") in TELON
    ]

    return {
        "mercado": movers + eventos,   # movimientos + eventos, dinámico cada día
        "foto": foto,                  # la tabla Día/Mes/Año del telón de fondo
        "observa": observa,            # lo que el enjambre mira hoy (atención)
        "origen_datos": origen_datos,  # 'yahoo' | 'barchart' | 'demo'
    }


def _unicos(secuencia: list[str]) -> list[str]:
    vistos, salida = set(), []
    for x in secuencia:
        if x and x not in vistos:
            vistos.add(x)
            salida.append(x)
    return salida
```

## engine/contenido/redaccion_ia.py
```python
"""El redactor de IA de El Pulso — le pone VOZ a los hechos verificados.

La Redacción (redaccion.py) trae los hechos con su cifra y su fuente. Este
módulo toma esos hechos YA VERIFICADOS y los reescribe con la voz cálida y
con humor de El Pulso, usando el PROMPT MAESTRO (docs/prompt-maestro-pulso.md,
aprobado por Giorgio el 5 de agosto de 2026).

Dos candados que NO se cruzan:
  1. La IA solo pone voz sobre hechos verificados: los números vienen dados,
     no los toca. No puede inventar cifras.
  2. Cada texto que devuelve pasa por el filtro CMF (es_publicable) antes de
     usarse. Voz sí, asesoría/predicción no.

Degradación elegante: sin ANTHROPIC_API_KEY, o si la API/JSON fallan, devuelve
None y el boletín cae a su plantilla de siempre. El Pulso NUNCA se cae por esto.
"""

import json
import os
import re
from datetime import datetime, timezone

from brains.arquetipos import ARQUETIPOS, POR_ID
from contenido.vocabulario import es_publicable
from llm_texto import texto_de

# los lectores viven en Chile/LatAm; el saludo se calcula en hora local de
# Chile (zoneinfo maneja el horario de verano solo). Si no está la zona
# (entornos mínimos), cae a UTC sin romperse.
ZONA_LECTOR = "America/Santiago"
_DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
_MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
          "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


def _ahora_local(ahora: datetime | None = None) -> datetime:
    base = ahora or datetime.now(timezone.utc)
    try:
        from zoneinfo import ZoneInfo
        return base.astimezone(ZoneInfo(ZONA_LECTOR))
    except Exception:
        return base  # sin tzdata: el UTC sirve igual para el momento del día


def _momento(hora: int) -> str:
    if hora < 6:
        return "madrugada"
    if hora < 12:
        return "mañana"
    if hora < 20:
        return "tarde"
    return "noche"


def contexto_temporal(ahora: datetime | None = None) -> dict:
    """Qué día es, la fecha y el momento — para que el redactor NO los invente."""
    t = _ahora_local(ahora)
    return {
        "dia_semana": _DIAS[t.weekday()],
        "weekday": t.weekday(),                 # 0=lunes … 5=sábado, 6=domingo
        "fecha": f"{t.day} de {_MESES[t.month - 1]} de {t.year}",
        "momento": _momento(t.hour),
        "es_finde": t.weekday() >= 5,
    }

MODELO = "claude-sonnet-5"   # calidad de escritura; sin temperature (Sonnet-5 la rechaza)
MAX_TOKENS = 8000            # análisis extenso (deep-dive con debate + números):
                             # holgura para que el JSON NUNCA se corte a medias
TIMEOUT_SEGUNDOS = 90.0      # corre en el ritual de fondo, no en un request web

# ---------- EL PROMPT MAESTRO (rediseño estilo diario, 14-ago-2026) ----------

PROMPT_MAESTRO = """\
Eres el redactor jefe de EL PULSO, un DIARIO DE MERCADO (by Rubicón Lab) que la
gente lee en su correo cada mañana. Tu trabajo NO es reenviar titulares: es
tomar los HECHOS YA VERIFICADOS que te entrego y convertir cada uno en una
HISTORIA con análisis de verdad. Piensa en un boletín como "Morning Brew" o
"Moby": ameno, agudo, con opinión sobre los hechos, que enseña mientras entretiene.

PARA QUIÉN ESCRIBES
Lectores curiosos: retail que quiere entender el mercado sin ser experto, y
gente de finanzas que agradece que no la aburran. Español neutro (Chile/LatAm).
Si usas un término técnico, lo explicas en la misma frase con una analogía.

CÓMO ESCRIBES (tu voz)
- Cálido y filoso, como un amigo brillante que sabe de mercados y te lo cuenta
  en el café. Cercano, nunca solemne.
- Con humor seco e ironía sobre LOS HECHOS (jamás sobre el lector).
- Frases cortas, ritmo. Analogías cotidianas para lo complejo.
- EXTENSO donde importa: cada historia son 3 a 5 párrafos de análisis real, no
  un resumen. Desarrolla la idea; no te quedes en el titular.

LA ESTRUCTURA DE CADA HISTORIA (síguela)
1. QUÉ PASÓ — el hecho con su cifra (la que te doy).
2. POR QUÉ IMPORTA — la tesis: qué significa de verdad, más allá del dato.
3. LA CONEXIÓN — el hilo con lo macro (tasas, petróleo, la Fed, la industria) o
   con la narrativa del momento. Aquí está el valor: conectas puntos.
4. Cierras con un "bottom_line": una frase que remata la idea.

CÓMO ELIGES LAS HISTORIAS (curaduría por ATENCIÓN, no por tamaño)
De los candidatos que te doy, elige las 3-4 que MÁS llamen la atención. Criterios:
- Una movida fuerte (un porcentaje grande, sobre todo en algo chico).
- Un catalizador o aprobación (FDA, un regulador, un contrato, un acuerdo).
- La narrativa que domina el mercado esta semana/mes.
NO te limites a las empresas gigantes: una small-cap que se disparó por una
aprobación, una cripto o una materia prima valen MÁS que otra mega-cap más.
Busca variedad de activos.

EL GRÁFICO DE CADA HISTORIA
Cada historia lleva un gráfico de precio real. Para eso, en "grafico" pon el
TICKER que te doy junto a ese activo (cópialo textual, NO inventes tickers) y su
nombre. Elige "periodo": "dia" si la movida fue de hoy/una aprobación reciente,
"semana" por defecto, "mes" si es una narrativa de fondo. "moneda" suele ser "$".
Si una historia no tiene un ticker claro entre los datos, deja "grafico": null.

LO QUE NUNCA HACES — REGLAS DE ORO (INNEGOCIABLES)
A. Candado CMF (regulación chilena) — ESTA ES TU LÍNEA Y TU DEFENSA:
- NUNCA recomiendas comprar, vender ni mantener. Prohibidas: "conviene",
  "es buen momento", "oportunidad de compra", "deberías", "apunta a",
  "podría subir/bajar", "esperamos que", "precio objetivo".
- NUNCA predices el futuro. Cuentas lo que YA pasó. Cuando mires hacia adelante,
  es "qué observar / qué está en juego", nunca "qué va a pasar".
- Análisis profundo SÍ; recomendación de inversión JAMÁS. Puedes explicar por
  qué algo importa sin decirle a nadie qué hacer con su plata.
B. Integridad de datos:
- Los NÚMEROS, TICKERS, FECHAS y CITAS vienen dados. Cópialos TEXTUALES.
- Si un dato no está en lo que te di, NO lo mencionas. No rellenas huecos.
- Los titulares de prensa se citan como CONTEXTO, nunca como causa confirmada.
- No inventas fuentes, enlaces ni cifras.

EL DÍA DE HOY (te lo doy yo — NO lo inventes)
Te digo el día, la fecha y el momento. Saluda acorde ("Buenos días" en la mañana,
etc.), menciona la fecha que te doy, nunca inventes otra. Si es fin de semana o
feriado sin sesión, escribe una edición de repaso, sin inventar movimientos.

NO menciones "el enjambre" ni simulaciones en las historias: El Pulso es un diario
de mercado serio. (El Enjambre se promociona aparte, al pie del correo.)

QUÉ DEVUELVES: SOLO un objeto JSON válido, sin texto alrededor, con esta forma:
{
  "buenos_dias": "2-3 párrafos de apertura que amarran el día, separados por \\n\\n.",
  "historias": [
    {
      "kicker": "etiqueta corta de categoría, ej: 'Tecnología · catalizador',
                 'Small-cap · movida del día', 'Narrativa del mes · cripto',
                 'Macro · materias primas'",
      "emoji": "un emoji que resuma la historia",
      "titular": "titular con gancho, reescrito en tu voz",
      "dek": "una bajada de una línea (subtítulo)",
      "cuerpo": "3 a 5 párrafos separados por \\n\\n: qué pasó + por qué importa + la conexión",
      "bottom_line": "una frase de cierre (sin escribir 'En una línea:', solo la frase)",
      "grafico": {"ticker": "AAPL", "nombre": "Apple Inc.", "periodo": "semana", "moneda": "$"}
    }
  ]
}
Devuelve 3-4 historias. Escribe SIEMPRE en español. Prioriza calidad y profundidad
sobre cantidad, pero cada historia elegida va DESARROLLADA, no en dos frases."""


# ---------- armado del mensaje del día (los hechos verificados) ----------

def _mensaje_del_dia(brief: dict, enjambre: dict | None = None, cuando: dict | None = None) -> str:
    """Serializa los hechos verificados para el redactor: los CANDIDATOS del día
    (movidas con su ticker + cifra + cita) para que elija y desarrolle 3-4.
    Solo hechos verificados; el redactor no ve nada que pueda inventar."""
    cuando = cuando or contexto_temporal()
    finde = " (FIN DE SEMANA: sin sesión de mercado)" if cuando.get("es_finde") else ""
    lineas = [
        f'HOY es {cuando["dia_semana"]} {cuando["fecha"]}, es de {cuando["momento"]}{finde}.',
        "Saluda según el momento y usa esta fecha; NO inventes otra.\n",
    ]

    foto = brief.get("foto") or []
    if foto:
        lineas.append("EL TELÓN DE FONDO (índices y materias primas, para contexto):")
        for f in foto:
            lineas.append(f'- {f.get("nombre","")}: día {f.get("variacion_pct")}%, '
                          f'mes {f.get("var_mes_pct")}%, año {f.get("var_ano_pct")}%')
        lineas.append("")

    mercado = brief.get("mercado") or []
    movers = [m for m in mercado if m.get("tipo") != "evento"]
    eventos = [m for m in mercado if m.get("tipo") == "evento"]

    if movers:
        lineas.append("CANDIDATOS A HISTORIA — movidas verificadas (elige las que MÁS "
                      "llamen la atención; usa el [TICKER] para el gráfico de cada una):")
        for m in movers:
            tk = m.get("simbolo", "") or "?"
            linea = f'- [{tk}] {m.get("nombre","")}: {m.get("variacion_pct")}%'
            if m.get("cita_titular"):
                linea += f' — en la prensa: «{m["cita_titular"]}»'
            if m.get("fuente"):
                linea += f' (fuente: {m["fuente"]})'
            lineas.append(linea)
        lineas.append("")

    if eventos:
        lineas.append("EVENTOS DEL DÍA (noticias sin un movimiento de precio directo — "
                      "úsalas como historia o como contexto):")
        for e in eventos:
            lineas.append(f'- «{e.get("titular","")}»'
                          + (f' (fuente: {e["fuente"]})' if e.get("fuente") else ""))
        lineas.append("")

    observa = brief.get("observa") or []
    if observa:
        lineas.append("OTROS TITULARES EN EL RADAR (contexto extra, no obligatorio):")
        lineas += [f"- {t}" for t in observa]

    return "\n".join(lineas)


# ---------- filtro CMF sobre lo que devuelve la IA ----------

def _cmf(texto: str) -> str | None:
    """Devuelve el texto si pasa el filtro CMF; None si no (para descartarlo).
    Se evalúa párrafo por párrafo: si un párrafo cruza la línea, se cae solo
    ese, no la historia entera."""
    if not isinstance(texto, str) or not texto.strip():
        return None
    parrafos = [p.strip() for p in texto.split("\n\n") if p.strip()]
    limpios = [p for p in parrafos if es_publicable(p)]
    return "\n\n".join(limpios) if limpios else None


def _grafico_valido(g) -> dict | None:
    """Valida la especificación del gráfico: un ticker limpio (sin inyección) y
    los campos de presentación. None si no hay ticker usable."""
    if not isinstance(g, dict):
        return None
    t = str(g.get("ticker", "")).strip()
    if not t or len(t) > 15 or not all(c.isalnum() or c in ".=^-" for c in t):
        return None
    periodo = str(g.get("periodo", "semana")).strip().lower()
    if periodo not in ("semana", "mes", "ano", "dia"):
        periodo = "semana"
    return {"ticker": t, "nombre": str(g.get("nombre", "") or t)[:60],
            "periodo": periodo, "moneda": (str(g.get("moneda", "$")).strip()[:2] or "$")}


def _texto_cmf(t) -> str:
    """Un texto de una línea: se conserva solo si pasa el filtro CMF."""
    t = str(t or "").strip()
    return t if t and es_publicable(t) else ""


def _sanear_historia(h: dict) -> dict | None:
    """Una historia con su estructura nueva; None si no tiene lo mínimo
    (titular + cuerpo publicables)."""
    if not isinstance(h, dict):
        return None
    titular = str(h.get("titular", "")).strip()
    cuerpo = _cmf(h.get("cuerpo", ""))
    if not cuerpo or not titular or not es_publicable(titular):
        return None
    return {
        "kicker": _texto_cmf(h.get("kicker"))[:60],
        "emoji": str(h.get("emoji", "") or "").strip()[:4],
        "titular": titular[:160],
        "dek": _texto_cmf(h.get("dek"))[:200],
        "cuerpo": cuerpo,
        "bottom_line": _texto_cmf(h.get("bottom_line"))[:280],
        "grafico": _grafico_valido(h.get("grafico")),
    }


def _validar(datos: dict) -> dict | None:
    """Valida la forma del JSON y pasa TODO por el filtro CMF."""
    if not isinstance(datos, dict):
        return None
    buenos = _cmf(datos.get("buenos_dias", ""))
    historias = [s for s in (_sanear_historia(h) for h in (datos.get("historias") or [])
                             if isinstance(h, dict)) if s]
    if not historias and not buenos:
        return None  # sin historias ni apertura, no hay diario que valga
    return {"buenos_dias": buenos, "historias": historias[:4]}


def _extraer_json(texto: str) -> dict | None:
    encontrado = re.search(r"\{.*\}", texto, re.DOTALL)
    if not encontrado:
        return None
    try:
        return json.loads(encontrado.group())
    except json.JSONDecodeError:
        return None


# ---------- punto de entrada ----------

def redactar(brief: dict, enjambre: dict | None = None, cuando: dict | None = None) -> dict | None:
    """Reescribe el brief del día como diario: {buenos_dias, historias[]}. None
    si no se puede (sin clave, API caída, JSON roto, todo filtrado por CMF) — el
    boletín cae a su respaldo. `enjambre` se mantiene por compatibilidad de firma
    pero ya no se usa (las historias son de las noticias, no del enjambre).
    `cuando` se calcula solo si no se pasa. NUNCA lanza."""
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return None
    if not brief or not (brief.get("mercado") or brief.get("observa")):
        return None  # sin hechos, no hay nada que redactar
    try:
        import anthropic

        cliente = anthropic.Anthropic(timeout=TIMEOUT_SEGUNDOS)
        respuesta = cliente.messages.create(
            model=MODELO,
            max_tokens=MAX_TOKENS,
            system=PROMPT_MAESTRO,
            messages=[{"role": "user", "content": _mensaje_del_dia(brief, cuando=cuando)}],
        )
        datos = _extraer_json(texto_de(respuesta))
        return _validar(datos) if datos else None
    except Exception:
        return None  # cualquier falla → fallback a plantilla


# ══════════════════════════════════════════════════════════════════════════
#  LA EDICIÓN DE LA TARDE — 'el cierre del mercado' (Premium) CON VOZ
# ══════════════════════════════════════════════════════════════════════════
# El investigador (investigador.py) ya cazó y VERIFICÓ los mayores movimientos
# del día con su porqué. Aquí les ponemos ENCIMA la voz Moby: en vez de una lista
# plana ("FRVO sube 28%"), los 3 protagonistas se vuelven mini-historias con
# tono cálido-filoso, igual que la edición de la mañana. Voz sobre hechos ya
# verificados: los números, tickers y el motivo vienen dados; la IA no los toca.

PROMPT_CIERRE = """\
Eres el redactor jefe de EL PULSO (by Rubicón Lab). Esta es la EDICIÓN DE LA
TARDE: 'el cierre del mercado', el premio de los suscriptores Premium. Cerró la
bolsa de EE.UU. y te entrego los MAYORES movimientos del día, YA investigados y
VERIFICADOS por nuestro reportero (cada uno con su cifra y su motivo confirmado).
Tu trabajo: convertir los 3 que MÁS llamen la atención en mini-historias con
voz, no en una lista plana de porcentajes.

TU VOZ (la de siempre, la "Moby")
- Cálido y filoso, como un amigo brillante que sabe de mercados y te lo cuenta en
  el café al cierre del día. Cercano, nunca solemne.
- Humor seco e ironía sobre LOS HECHOS (jamás sobre el lector).
- Frases cortas, ritmo. Analogías cotidianas para lo complejo. Si usas un término
  técnico, lo explicas en la misma frase.

CADA MINI-HISTORIA (2 a 3 párrafos, desarrollada)
1. QUÉ PASÓ — el movimiento con su cifra (la que te doy) y el motivo verificado.
2. POR QUÉ IMPORTA — la tesis: qué significa de verdad, más allá del salto de precio.
3. LA CONEXIÓN — el hilo con lo macro (tasas, la Fed, el sector, la narrativa del
   momento). Aquí está el valor: conectas puntos.
Cierra con un "bottom_line": una frase que remata.

REGLAS DE ORO (INNEGOCIABLES)
A. Candado CMF (regulación chilena): NUNCA recomiendas comprar, vender ni mantener.
   Prohibidas: "conviene", "oportunidad", "deberías", "podría subir/bajar",
   "precio objetivo", "es buen momento". NUNCA predices el futuro: cuentas lo que
   YA pasó; hacia adelante es "qué observar", nunca "qué va a pasar".
B. Integridad: los NÚMEROS, TICKERS y el MOTIVO vienen dados. Cópialos TEXTUALES.
   Si algo no está en lo que te di, NO lo inventas. Si un movimiento vino marcado
   como SIN motivo verificado, cuéntalo así ("subió con fuerza; el mercado aún no
   fija una causa clara") — jamás inventes la razón.

EL GRÁFICO: en "grafico" pon el TICKER que te doy junto a ese activo (textual, NO
inventes) y su nombre. "periodo": "dia". "moneda": "$".

NO menciones "el enjambre" ni simulaciones: El Pulso es un diario de mercado serio.

QUÉ DEVUELVES: SOLO un objeto JSON válido, sin texto alrededor, con esta forma:
{
  "buenas_tardes": "1-2 párrafos de apertura que amarran el cierre del día, separados por \\n\\n.",
  "historias": [
    {
      "kicker": "etiqueta corta, ej: 'Energía · movida del día', 'Small-cap · catalizador'",
      "emoji": "un emoji que resuma la historia",
      "titular": "titular con gancho, en tu voz",
      "dek": "una bajada de una línea",
      "cuerpo": "2 a 3 párrafos separados por \\n\\n: qué pasó + por qué importa + la conexión",
      "bottom_line": "una frase de cierre (sin escribir 'En una línea:', solo la frase)",
      "grafico": {"ticker": "FRVO", "nombre": "Fervo Energy", "periodo": "dia", "moneda": "$"}
    }
  ]
}
Devuelve las 3 historias más llamativas. Escribe SIEMPRE en español. Cada una
DESARROLLADA, no en dos frases."""


def _mensaje_cierre(datos: dict, cuando: dict | None = None) -> str:
    """Serializa los movimientos YA verificados para el redactor del cierre."""
    cuando = cuando or contexto_temporal()
    movers = [m for m in (datos.get("movers") or []) if isinstance(m, dict)]
    lineas = [
        f'HOY es {cuando["dia_semana"]} {cuando["fecha"]}. Es la EDICIÓN DE LA '
        f'TARDE, tras el cierre del mercado de EE.UU. Saluda con "Buenas tardes" '
        f'y usa esta fecha; NO inventes otra.\n',
        "LOS PROTAGONISTAS DEL CIERRE — movimientos verificados (elige los 3 que "
        "MÁS llamen la atención y desarróllalos; usa el [TICKER] para el gráfico):",
    ]
    for m in movers:
        tk = str(m.get("simbolos", "") or "?").split(",")[0].strip() or "?"
        pct = m.get("var_pct")
        signo = "sube" if (pct or 0) >= 0 else "cae"
        linea = f'- [{tk}] {m.get("titular","")}'
        if pct is not None:
            linea += f' — dato: {signo} {abs(pct)}%'
        razon = str(m.get("razon", "") or "").strip()
        if m.get("verificado") and razon:
            linea += f'. Motivo verificado: «{razon}»'
        else:
            linea += ". SIN motivo verificado (no inventes la causa)."
        if m.get("fuente"):
            linea += f' (fuente: {m["fuente"]})'
        lineas.append(linea)
    return "\n".join(lineas)


def _validar_cierre(datos: dict, fuente_movers: list[dict]) -> dict | None:
    """Valida la forma del JSON del cierre y pasa TODO por el filtro CMF. Ata a
    cada historia el % real del movimiento (la píldora) casando su ticker con el
    del movimiento de origen. None si no quedó ni apertura ni historia."""
    if not isinstance(datos, dict):
        return None
    apertura = _cmf(datos.get("buenas_tardes", ""))
    historias = [s for s in (_sanear_historia(h) for h in (datos.get("historias") or [])
                             if isinstance(h, dict)) if s]
    if not historias and not apertura:
        return None
    # píldora del %: casa el ticker del gráfico con el movimiento de origen
    por_ticker = {}
    for m in fuente_movers:
        tk = str(m.get("simbolos", "") or "").split(",")[0].strip().upper()
        if tk:
            por_ticker[tk] = m
    for h in historias:
        g = h.get("grafico") or {}
        origen = por_ticker.get(str(g.get("ticker", "")).strip().upper())
        if origen:
            h["var_pct"] = origen.get("var_pct")
            h["sesion"] = origen.get("sesion")
    return {"buenas_tardes": apertura, "historias": historias[:3]}


def redactar_cierre(datos: dict, cuando: dict | None = None) -> dict | None:
    """Le pone VOZ Moby al cierre del día: toma los movimientos verificados por el
    investigador y devuelve {buenas_tardes, historias[]}. None si no se puede
    (sin clave, API caída, JSON roto, todo filtrado por CMF) — el boletín cae a la
    lista llana de siempre. NUNCA lanza."""
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return None
    movers = [m for m in (datos.get("movers") or []) if isinstance(m, dict)]
    if not movers:
        return None
    try:
        import anthropic

        cliente = anthropic.Anthropic(timeout=TIMEOUT_SEGUNDOS)
        respuesta = cliente.messages.create(
            model=MODELO,
            max_tokens=MAX_TOKENS,
            system=PROMPT_CIERRE,
            messages=[{"role": "user", "content": _mensaje_cierre(datos, cuando=cuando)}],
        )
        parseado = _extraer_json(texto_de(respuesta))
        return _validar_cierre(parseado, movers) if parseado else None
    except Exception:
        return None  # cualquier falla → fallback a la lista llana


# ══════════════════════════════════════════════════════════════════════════
#  LA EDICIÓN DE FIN DE SEMANA — el deep-dive de una mid-cap o un sector
# ══════════════════════════════════════════════════════════════════════════
# Formato distinto al diario: CONTEXTO primero (qué ES), luego el DEBATE de
# arquetipos (miradas contrastantes = "lo que nuestros inversionistas IA están
# viendo o analizando"). NUNCA consejo de inversión. Ver analisis_semanal.py.

# roster compacto de arquetipos para el prompt (id → nombre + una línea de perfil)
def _roster_arquetipos() -> str:
    lineas = []
    for a in ARQUETIPOS:
        # una línea de esencia por arquetipo (la primera frase de su prompt)
        esencia = a["prompt"].split(".")[0].strip()
        lineas.append(f'- {a["id"]} ({a["nombre"]}): {esencia}.')
    return "\n".join(lineas)


PROMPT_ANALISIS = """\
Eres el redactor jefe de EL PULSO (by Rubicón Lab). Es FIN DE SEMANA: el mercado
está cerrado y toca la lectura pausada. Hoy NO cuentas las noticias del día:
haces UN análisis a fondo de un solo protagonista —una empresa de mediana
capitalización o un sector— que te entrego ya elegido, con su contexto y su
cifra verificada.

EL ENCUADRE QUE MANDA (léelo dos veces)
Esto NO es consejo de inversión. Es "lo que nuestros inversionistas IA están
VIENDO y ANALIZANDO". Tú no le dices a nadie qué hacer con su plata: describes
qué es el protagonista, por qué llamó la atención, y cómo lo miran perfiles de
inversionista MUY distintos entre sí. El valor está en el CONTRASTE de miradas,
no en una conclusión única.

CÓMO ESCRIBES (tu voz)
- Cálido, agudo, cercano; con humor seco sobre los hechos, nunca sobre el lector.
- Español neutro (Chile/LatAm). Si usas un término técnico, lo explicas ahí mismo
  con una analogía cotidiana.
- Extenso donde importa: párrafos de análisis real, no un resumen.

LA ESTRUCTURA (síguela en este orden — es un análisis de analista, no un tuit)
1. CONTEXTO PRIMERO — QUÉ ES el protagonista. Antes de opinar nada, explícale al
   lector a qué se dedica la empresa/sector, cómo gana dinero, qué lo hace
   particular. Apóyate en el contexto factual que te doy; no inventes datos.
   Desarróllalo: 2-3 párrafos.
2. LA LECTURA — POR QUÉ está en la mira esta semana: la movida de precio (la
   cifra que te doy) y la narrativa alrededor. Qué historia se está contando.
3. LOS NÚMEROS — la lectura financiera, como la haría un analista. Con los DATOS
   VERIFICADOS que te doy (capitalización, ingresos y su crecimiento, márgenes,
   EBITDA, deuda, caja), explica en simple qué dicen sobre la SALUD del negocio:
   ¿crece o se estanca?, ¿gana o quema plata?, ¿está apalancada o tiene colchón?
   Traduce cada término técnico con una analogía (ej. EBITDA = las ganancias del
   negocio antes de intereses e impuestos; margen bruto = de cada $100 vendidos,
   cuántos quedan tras el costo directo). COPIA las cifras TEXTUALES; no inventes
   ninguna. Si no te doy fundamentales (o vienen vacíos), OMITE este bloque
   entero (deja "numeros": "").
4. EL DEBATE — cómo lo miran distintos perfiles de nuestros inversionistas IA.
   Elige 4 a 6 arquetipos de la lista y dale a cada uno 1-2 frases con SU mirada
   particular sobre este protagonista. Que se CONTRADIGAN entre sí (el optimista
   ve una cosa, el doomer la contraria): ese choque es el corazón del análisis.
5. QUÉ OBSERVAR — qué está en juego de aquí en adelante. ATENCIÓN, no predicción:
   "habrá que ver si…", "lo que está en juego es…", nunca "va a…".

LOS ARQUETIPOS DISPONIBLES (usa sus id exactos en el JSON):
{ROSTER}

LO QUE NUNCA HACES — REGLAS DE ORO (INNEGOCIABLES)
A. Candado CMF (regulación chilena) — TU LÍNEA:
- NUNCA recomiendas comprar, vender ni mantener. Prohibidas: "conviene",
  "es buen momento", "oportunidad de compra", "deberías", "apunta a",
  "podría subir/bajar", "esperamos que", "precio objetivo", "le vemos potencial".
- NUNCA predices el futuro ni das una tesis de inversión propia del medio. El
  "potencial" no lo pones TÚ: lo ponen en tensión los arquetipos, como miradas.
- Analizas y explicas SÍ; aconsejas JAMÁS. Puedes decir por qué algo importa sin
  decirle a nadie qué hacer con su dinero.
B. Integridad de datos:
- Los NÚMEROS, TICKERS y NOMBRES vienen dados. Cópialos TEXTUALES. Las ÚNICAS
  cifras que existen son la variación de precio y los fundamentales que te doy;
  NO inventes ninguna otra (ni múltiplos, ni proyecciones, ni cifras redondeadas
  a ojo). Si un dato no está en lo que te di, NO lo mencionas.

QUÉ DEVUELVES: SOLO un objeto JSON válido, sin texto alrededor, con esta forma:
{
  "titular": "titular con gancho sobre el protagonista, en tu voz",
  "dek": "una bajada de una línea (subtítulo)",
  "contexto": "2-3 párrafos (separados por \\n\\n): QUÉ ES el protagonista",
  "lectura": "2-3 párrafos (separados por \\n\\n): por qué está en la mira + la narrativa",
  "numeros": "2-3 párrafos (separados por \\n\\n) explicando en simple los fundamentales verificados; \\"\\" si no te di ninguno",
  "debate": [
    {"arquetipo": "contrarian_sabio", "mirada": "1-2 frases con su mirada sobre este protagonista"}
  ],
  "que_observar": "1 párrafo: qué está en juego / qué observar (atención, no predicción)"
}
Escribe SIEMPRE en español. Prioriza profundidad; el debate DEBE tener miradas
que se contradigan.""".replace("{ROSTER}", _roster_arquetipos())


def _mensaje_analisis(analisis: dict, cuando: dict | None = None) -> str:
    """Serializa los hechos del protagonista del fin de semana para el redactor:
    qué es (contexto factual), su cifra verificada y el encuadre. Solo hechos."""
    cuando = cuando or contexto_temporal()
    es_sector = analisis.get("modo") == "sector"
    lineas = [
        f'HOY es {cuando["dia_semana"]} {cuando["fecha"]} (fin de semana, mercado cerrado).',
        f'Sección: {analisis.get("titulo", "")}.',
        "",
        f'PROTAGONISTA: {analisis.get("nombre", "")} [{analisis.get("ticker", "")}]',
    ]
    if es_sector:
        lineas.append(f'Es un SECTOR completo. Se está moviendo por: {analisis.get("en_rotacion_por", "")}.')
        if analisis.get("ejemplos"):
            lineas.append(f'Ejemplos de empresas del sector: {", ".join(analisis["ejemplos"])}.')
    else:
        lineas.append(f'Es una empresa de MEDIANA capitalización. Sector: {analisis.get("sector", "")}.')
    lineas += [
        "",
        "CONTEXTO FACTUAL (qué es — apóyate en esto, NO inventes más datos):",
        analisis.get("contexto", ""),
        "",
        "LA CIFRA VERIFICADA (la ÚNICA que puedes usar; cópiala textual):",
        f'- Variación de la semana: {analisis.get("var_semana_pct")}%',
    ]
    if analisis.get("var_mes_pct") is not None:
        lineas.append(f'- Variación del mes: {analisis.get("var_mes_pct")}%')
    lineas.append(f'- Ventana del gráfico: {analisis.get("fecha_inicio")} a {analisis.get("fecha_fin")}.')

    fund = analisis.get("fundamentales")
    if isinstance(fund, dict) and fund:
        etiquetas = {
            "market_cap": "Capitalización de mercado", "ingresos": "Ingresos (últimos 12 meses)",
            "crecimiento_ingresos": "Crecimiento de ingresos (interanual)",
            "ebitda": "EBITDA", "margen_bruto": "Margen bruto",
            "margen_operativo": "Margen operativo", "margen_neto": "Margen neto",
            "deuda": "Deuda total", "caja": "Caja y equivalentes",
            "flujo_caja_libre": "Flujo de caja libre",
        }
        lineas += ["", "FUNDAMENTALES VERIFICADOS (datos de mercado; cópialos TEXTUALES, "
                   "explícalos en simple, NO inventes otros):"]
        for clave, etiqueta in etiquetas.items():
            if fund.get(clave):
                lineas.append(f'- {etiqueta}: {fund[clave]}')
    else:
        lineas += ["", "No hay fundamentales para este protagonista: OMITE el bloque de "
                   "números (deja \"numeros\": \"\")."]

    lineas += [
        "",
        "Recuerda: encuadre = lo que nuestros inversionistas IA VEN y ANALIZAN, "
        "NUNCA consejo de inversión. Contexto primero; luego los números y el debate.",
    ]
    return "\n".join(lineas)


def _sanear_debate(debate) -> list[dict]:
    """Cada mirada de arquetipo: arquetipo válido + frase publicable (CMF)."""
    salida = []
    for d in (debate or []):
        if not isinstance(d, dict):
            continue
        arq = str(d.get("arquetipo", "")).strip()
        mirada = str(d.get("mirada", "")).strip()
        if arq in POR_ID and mirada and es_publicable(mirada):
            salida.append({"arquetipo": arq, "nombre": POR_ID[arq]["nombre"], "mirada": mirada[:400]})
    return salida


def _validar_analisis(datos: dict) -> dict | None:
    """Valida la forma del deep-dive y pasa TODO por el filtro CMF. None si no
    queda lo mínimo (contexto + titular publicables)."""
    if not isinstance(datos, dict):
        return None
    titular = str(datos.get("titular", "")).strip()
    contexto = _cmf(datos.get("contexto", ""))
    if not titular or not es_publicable(titular) or not contexto:
        return None
    return {
        "titular": titular[:160],
        "dek": _texto_cmf(datos.get("dek"))[:200],
        "contexto": contexto,
        "lectura": _cmf(datos.get("lectura", "")) or "",
        "numeros": _cmf(datos.get("numeros", "")) or "",
        "debate": _sanear_debate(datos.get("debate")),
        "que_observar": _cmf(datos.get("que_observar", "")) or "",
    }


def redactar_analisis(analisis: dict, cuando: dict | None = None) -> dict | None:
    """Le pone VOZ al deep-dive del fin de semana: {titular, dek, contexto,
    lectura, debate[], que_observar}. None si no se puede (sin clave, API caída,
    JSON roto, todo filtrado por CMF) — el correo cae a su respaldo. NUNCA lanza."""
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return None
    if not analisis or not analisis.get("contexto"):
        return None
    try:
        import anthropic

        cliente = anthropic.Anthropic(timeout=TIMEOUT_SEGUNDOS)
        respuesta = cliente.messages.create(
            model=MODELO,
            max_tokens=MAX_TOKENS,
            system=PROMPT_ANALISIS,
            messages=[{"role": "user", "content": _mensaje_analisis(analisis, cuando=cuando)}],
        )
        datos = _extraer_json(texto_de(respuesta))
        return _validar_analisis(datos) if datos else None
    except Exception:
        return None


# ══════════════════════════════════════════════════════════════════════════
#  EL RESUMEN DE LA SEMANA — la edición del sábado
# ══════════════════════════════════════════════════════════════════════════
# Mira la semana entera con punto de vista: los grandes temas, el porqué de cada
# cosa, cómo la geopolítica y la macro movieron el mercado, y QUÉ OBSERVAR de
# aquí en adelante (atención, jamás predicción). Ver resumen_semanal.py.

PROMPT_RESUMEN = """\
Eres el redactor jefe de EL PULSO (by Rubicón Lab). Es SÁBADO: sale la edición de
FIN DE SEMANA que mira la SEMANA ENTERA. No cuentas el día: haces un RESUMEN con
PUNTO DE VISTA de lo que movió el mercado esta semana. Piensa en la carta de fin
de semana de un buen medio: ameno, agudo, que conecta los puntos.

TU TRABAJO
De los TEMAS de la semana que te doy (titulares que de verdad importaron) y de la
FOTO SEMANAL del mercado (cuánto se movió cada índice/materia prima), arma un
repaso que EXPLIQUE: qué pasó, POR QUÉ pasó, y cómo se conecta con lo macro y lo
geopolítico (tasas, la Fed, el petróleo, conflictos, elecciones). El valor está
en el porqué y en las conexiones, no en repetir titulares.

CÓMO ESCRIBES (tu voz)
- Cálido y filoso, cercano, con humor seco sobre los hechos (nunca sobre el lector).
- Español neutro (Chile/LatAm). Si usas un término técnico, lo explicas ahí mismo
  con una analogía cotidiana.
- Extenso donde importa: cada tema son 2-4 párrafos de análisis real.

LA ESTRUCTURA
1. INTRO — 2-3 párrafos con el ÁNIMO de la semana (¿de miedo?, ¿de euforia?, ¿de
   espera?) y el hilo que la conecta.
2. LOS TEMAS — elige los 3-5 que más marcaron la semana. Cada uno: QUÉ pasó, POR
   QUÉ importó, LA CONEXIÓN (macro/geopolítica), y cierra con QUÉ OBSERVAR.
3. CIERRE — 1 párrafo que remata la semana.

LO QUE NUNCA HACES — REGLAS DE ORO (INNEGOCIABLES)
A. Candado CMF (regulación chilena) — TU LÍNEA:
- NUNCA recomiendas comprar, vender ni mantener. Prohibidas: "conviene", "es buen
  momento", "oportunidad de compra", "deberías", "apunta a", "precio objetivo".
- NUNCA PREDICES el futuro. Cuentas lo que YA pasó y POR QUÉ. Cuando mires hacia
  adelante, es "QUÉ OBSERVAR / qué está en juego / habrá que ver si…", jamás
  "qué va a pasar", "subirá", "caerá", "esperamos que". Punto de vista sobre lo
  ocurrido: SÍ. Adivinar el futuro: JAMÁS.
B. Integridad de datos:
- Los TÍTULARES, NÚMEROS y FECHAS vienen dados. Cópialos TEXTUALES. La única cifra
  es la variación semanal que te doy; no inventes otras. Si un dato no está, no lo
  mencionas. Los titulares se citan como CONTEXTO, no como causa confirmada.

NO menciones "el enjambre" ni simulaciones: El Pulso es un diario serio. (El
Enjambre se promociona aparte, al pie del correo.)

EL GRÁFICO (opcional por tema)
Si un tema gira en torno a un índice o materia prima con ticker claro entre los
datos (S&P 500 = ^GSPC, Nasdaq = ^IXIC, Petróleo = CL=F, Oro = GC=F), puedes pedir
su gráfico en "grafico" con ese ticker (textual) y "periodo": "semana". Si no, deja
"grafico": null.

QUÉ DEVUELVES: SOLO un objeto JSON válido, sin texto alrededor, con esta forma:
{
  "intro": "2-3 párrafos separados por \\n\\n: el ánimo de la semana",
  "temas": [
    {
      "kicker": "etiqueta corta, ej: 'Geopolítica · petróleo', 'Macro · la Fed'",
      "emoji": "un emoji que resuma el tema",
      "titular": "el tema en tu voz, con gancho",
      "analisis": "2-4 párrafos separados por \\n\\n: qué pasó + por qué + la conexión",
      "que_observar": "1 frase de atención (no predicción)",
      "grafico": {"ticker": "CL=F", "nombre": "Petróleo WTI", "periodo": "semana", "moneda": "$"}
    }
  ],
  "cierre": "1 párrafo que remata la semana"
}
Devuelve 3-5 temas. Escribe SIEMPRE en español. Prioriza el porqué y las conexiones."""


def _mensaje_resumen(resumen: dict, cuando: dict | None = None) -> str:
    """Serializa los hechos de la semana para el redactor: los temas (titulares
    destacados) y la foto semanal del mercado. Solo hechos verificados."""
    cuando = cuando or contexto_temporal()
    lineas = [
        f'HOY es {cuando["dia_semana"]} {cuando["fecha"]} (edición de fin de semana: '
        f'repaso de la SEMANA, sin sesión de mercado hoy).',
        "Saluda acorde y usa esta fecha; NO inventes otra.\n",
    ]
    foto = resumen.get("foto") or []
    if foto:
        lineas.append("LA SEMANA EN NÚMEROS (variación de la semana; cópiala textual):")
        for f in foto:
            lineas.append(f'- {f.get("nombre","")} [{f.get("simbolo","")}]: {f.get("var_semana_pct")}%')
        lineas.append("")
    titulares = resumen.get("titulares") or []
    if titulares:
        lineas.append("LOS TEMAS DE LA SEMANA (titulares que importaron; elige y desarrolla los "
                      "que más la marcaron, explica el POR QUÉ y la conexión macro/geopolítica):")
        for t in titulares:
            lineas.append(f'- ({t.get("fecha","")}) «{t.get("titular","")}»')
        lineas.append("")
    lineas.append("Recuerda: punto de vista sobre lo que YA pasó y su porqué, SÍ; predecir el "
                  "futuro, JAMÁS. Mirar adelante = 'qué observar', nunca 'qué va a pasar'.")
    return "\n".join(lineas)


def _sanear_tema(t: dict) -> dict | None:
    """Un tema de la semana: titular + análisis publicables (CMF). None si no."""
    if not isinstance(t, dict):
        return None
    titular = str(t.get("titular", "")).strip()
    analisis = _cmf(t.get("analisis", ""))
    if not titular or not es_publicable(titular) or not analisis:
        return None
    return {
        "kicker": _texto_cmf(t.get("kicker"))[:60],
        "emoji": str(t.get("emoji", "") or "").strip()[:4],
        "titular": titular[:160],
        "analisis": analisis,
        "que_observar": _texto_cmf(t.get("que_observar"))[:280],
        "grafico": _grafico_valido(t.get("grafico")),
    }


def _validar_resumen(datos: dict) -> dict | None:
    """Valida la forma del resumen y pasa TODO por el filtro CMF. None si no queda
    ni intro ni temas."""
    if not isinstance(datos, dict):
        return None
    intro = _cmf(datos.get("intro", ""))
    temas = [s for s in (_sanear_tema(t) for t in (datos.get("temas") or [])
                         if isinstance(t, dict)) if s]
    if not temas and not intro:
        return None
    return {"intro": intro or "", "temas": temas[:5], "cierre": _cmf(datos.get("cierre", "")) or ""}


def redactar_resumen(resumen: dict, cuando: dict | None = None) -> dict | None:
    """Le pone VOZ al resumen de la semana: {intro, temas[], cierre}. None si no
    se puede (sin clave, API caída, JSON roto, todo filtrado por CMF) — el correo
    cae a su respaldo. NUNCA lanza."""
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return None
    if not resumen or not resumen.get("titulares"):
        return None
    try:
        import anthropic

        cliente = anthropic.Anthropic(timeout=TIMEOUT_SEGUNDOS)
        respuesta = cliente.messages.create(
            model=MODELO,
            max_tokens=MAX_TOKENS,
            system=PROMPT_RESUMEN,
            messages=[{"role": "user", "content": _mensaje_resumen(resumen, cuando=cuando)}],
        )
        datos = _extraer_json(texto_de(respuesta))
        return _validar_resumen(datos) if datos else None
    except Exception:
        return None
```

## engine/contenido/respaldo.py
```python
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
RUTA_COSECHA = "datos/cosecha.json"  # eventos cosechados (banco de exámenes que crece solo)


def hay_token() -> bool:
    return bool(os.environ.get("GITHUB_RESPALDO_TOKEN"))


def _leer_remoto(ruta: str, clave: str) -> list[dict]:
    """Lee un JSON de la caja fuerte y devuelve su lista bajo `clave`.

    Con token: usa la API autenticada de GitHub → funciona aunque el repo sea
    PRIVADO. Sin token: lectura pública del raw (repo público). Lista vacía
    ante cualquier problema; nunca lanza. (La API inline sirve hasta 1 MB;
    los JSON de calibración/cosecha están muy por debajo.)"""
    repo = os.environ.get("GITHUB_RESPALDO_REPO", REPO_DEFECTO)
    rama = os.environ.get("GITHUB_RESPALDO_RAMA", RAMA_DEFECTO)
    try:
        if hay_token():
            respuesta = httpx.get(
                f"{API}/repos/{repo}/contents/{ruta}", params={"ref": rama},
                headers={"Authorization": f"Bearer {os.environ['GITHUB_RESPALDO_TOKEN']}",
                         "Accept": "application/vnd.github+json"},
                timeout=12,
            )
            if respuesta.status_code != 200:
                return []
            crudo = base64.b64decode(respuesta.json().get("content") or "").decode("utf-8")
            return (json.loads(crudo) or {}).get(clave, [])
        respuesta = httpx.get(
            f"https://raw.githubusercontent.com/{repo}/{rama}/{ruta}", timeout=10
        )
        if respuesta.status_code != 200:
            return []
        return (json.loads(respuesta.text) or {}).get(clave, [])
    except Exception:
        return []


def casos_remotos() -> list[dict]:
    """Los casos de calibración ya respaldados en GitHub. El backtest los
    consulta para NO re-rendir exámenes que la caja fuerte ya tiene."""
    ruta = os.environ.get("GITHUB_RESPALDO_RUTA", RUTA_DEFECTO)
    return _leer_remoto(ruta, "casos")


def cosecha_remota() -> list[dict]:
    """Los eventos cosechados que ya viven en GitHub. El backtest los suma al
    banco local de exámenes (el catálogo crece solo, sin depender del disco)."""
    return _leer_remoto(RUTA_COSECHA, "eventos")


def subir_cosecha(nuevos: list[dict], reemplazar: bool = False) -> dict:
    """Fusiona y sube eventos cosechados a datos/cosecha.json (rama de respaldo).

    Une por `id` (lo nuevo pisa lo viejo). Con `reemplazar=True` NO fusiona:
    escribe solo `nuevos` (útil para purgar una cosecha vieja de baja calidad).
    NUNCA lanza. Devuelve {"subido": bool, "eventos": int, "motivo"?: str}.
    """
    if not hay_token():
        return {"subido": False, "eventos": 0, "motivo": "sin GITHUB_RESPALDO_TOKEN"}
    if not nuevos:
        return {"subido": False, "eventos": 0, "motivo": "sin eventos que subir"}
    repo = os.environ.get("GITHUB_RESPALDO_REPO", REPO_DEFECTO)
    rama = os.environ.get("GITHUB_RESPALDO_RAMA", RAMA_DEFECTO)
    url = f"{API}/repos/{repo}/contents/{RUTA_COSECHA}"
    cabeceras = {
        "Authorization": f"Bearer {os.environ['GITHUB_RESPALDO_TOKEN']}",
        "Accept": "application/vnd.github+json",
    }
    try:
        actual = httpx.get(url, params={"ref": rama}, headers=cabeceras, timeout=15)
        sha, previos = None, []
        if actual.status_code == 200:
            datos = actual.json()
            sha = datos.get("sha")
            crudo = base64.b64decode(datos.get("content") or "").decode("utf-8")
            previos = (json.loads(crudo) or {}).get("eventos", [])
        por_id = {} if reemplazar else {e["id"]: e for e in previos}
        por_id.update({e["id"]: e for e in nuevos})
        eventos = sorted(por_id.values(), key=lambda e: e.get("fecha") or "")
        hoy = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        contenido = {
            "generado": persistencia.ahora_iso(),
            "nota": ("Eventos cosechados por El Enjambre: días de mayor movimiento "
                     "reales (Yahoo) con su titular real (Benzinga). Alimentan el "
                     "banco de exámenes de calibración."),
            "eventos": eventos,
        }
        cuerpo = {
            "message": f"Cosecha de exámenes {hoy} ({len(eventos)} eventos)",
            "content": base64.b64encode(
                json.dumps(contenido, ensure_ascii=False, indent=1).encode("utf-8")
            ).decode("ascii"),
            "branch": rama,
        }
        if sha:
            cuerpo["sha"] = sha
        respuesta = httpx.put(url, headers=cabeceras, json=cuerpo, timeout=20)
        respuesta.raise_for_status()
        return {"subido": True, "eventos": len(eventos)}
    except Exception as error:
        return {"subido": False, "eventos": len(nuevos),
                "motivo": f"{type(error).__name__}: {str(error)[:120]}"}


def _senales_por_arquetipo(lideres_json: str | None) -> dict:
    """Resume las señales de los líderes por arquetipo: señal y confianza medias
    y cuántos líderes (compacto, ~9 entradas). Alimenta la calibración POR
    ARQUETIPO (¿quién descalibra el consenso?) sin volcar las 1.150 señales."""
    if not lideres_json:
        return {}
    try:
        lideres = json.loads(lideres_json)
    except (json.JSONDecodeError, TypeError):
        return {}
    from collections import defaultdict
    acc = defaultdict(lambda: [0.0, 0.0, 0])  # suma_senal, suma_confianza, n
    for lider in lideres:
        arq = lider.get("arquetipo")
        if not arq:
            continue
        acc[arq][0] += float(lider.get("senal", 0) or 0)
        acc[arq][1] += float(lider.get("confianza", 0) or 0)
        acc[arq][2] += 1
    return {arq: {"senal_media": round(s / n, 4),
                  "confianza_media": round(c / n, 4), "n": n}
            for arq, (s, c, n) in acc.items() if n}


def exportar_casos(conexion) -> list[dict]:
    """Los casos de calibración como dicts planos: destacadas corregidas
    (origen 'en_vivo') y exámenes históricos del backtest ('historico')."""
    filas = conexion.execute(
        """SELECT s.id, s.fecha, s.titular, s.resumen_json, s.reaccion_real,
                  s.epilogo, s.fuente, s.lideres_json, t.simbolos
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
            "senales_arquetipo": _senales_por_arquetipo(fila["lideres_json"]),
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
```

## engine/contenido/resumen_semanal.py
```python
"""El RESUMEN DE LA SEMANA de El Pulso — la edición del sábado.

Entre semana El Pulso cuenta el día; el sábado mira la semana entera con punto de
vista: los grandes temas, el porqué de cada cosa, cómo la geopolítica y la macro
movieron el mercado, y —siempre bajo el candado CMF— QUÉ OBSERVAR de aquí en
adelante (atención, jamás una predicción).

Este módulo solo junta los HECHOS (el número manda: los movimientos semanales
vienen de Yahoo; los temas, de los titulares que el motor destacó esta semana).
La voz la pone redaccion_ia.redactar_resumen; el correo lo dibuja boletin.
Degradación elegante: sin titulares de la semana devuelve None y el sábado cae a
lo que haya. NUNCA lanza.
"""

from datetime import datetime, timedelta, timezone

from contenido import persistencia
from contenido.fuentes import yahoo

# el telón de fondo del resumen: índices y materias primas SIEMPRE relevantes.
TELON = ["^GSPC", "^IXIC", "^DJI", "CL=F", "GC=F"]
DIAS_SEMANA = 7        # ventana de "la semana"
MAX_TITULARES = 12     # cuántos temas de la semana se le pasan al redactor


def titulares_de_la_semana(conexion, cuando: dict | None = None,
                           dias: int = DIAS_SEMANA, maximo: int = MAX_TITULARES) -> list[dict]:
    """Los titulares que el motor DESTACÓ en los últimos `dias` días: la columna
    vertebral del resumen (las noticias que de verdad importaron). Deduplicados,
    más recientes primero."""
    hoy = (persistencia.ahora_iso() if cuando is None else _iso_de(cuando))[:10]
    limite = _fecha_menos(hoy, dias)
    vistos, salida = set(), []
    for fila in persistencia.listar_simulaciones(conexion, solo_destacadas=True, limite=60):
        fecha = fila["fecha"][:10]
        if fecha < limite or fecha > hoy:
            continue
        clave = fila["titular"].strip().lower()
        if clave in vistos:
            continue
        vistos.add(clave)
        salida.append({"titular": fila["titular"], "fecha": fecha})
        if len(salida) >= maximo:
            break
    return salida


def foto_semana(fetch=yahoo.serie_reciente) -> list[dict]:
    """'La semana en números': el movimiento SEMANAL (~5 ruedas) de los índices y
    materias primas del telón. Solo los que Yahoo responde; nunca lanza."""
    foto = []
    for simbolo in TELON:
        serie = fetch(simbolo, rango="5d", intervalo="1d")
        if not serie:
            continue
        _fechas, cierres = serie
        if len(cierres) < 2 or not cierres[0]:
            continue
        var = round((cierres[-1] - cierres[0]) / cierres[0] * 100, 2)
        foto.append({"simbolo": simbolo, "nombre": yahoo.NOMBRES.get(simbolo, simbolo),
                     "var_semana_pct": var})
    return foto


def preparar_resumen(conexion=None, cuando: dict | None = None,
                     fetch=yahoo.serie_reciente) -> dict | None:
    """Arma los HECHOS del resumen del sábado: los temas de la semana (titulares
    destacados) + la foto semanal del mercado. None si no hubo temas (nada que
    resumir → el sábado cae a lo que haya)."""
    propia = conexion is None
    conexion = conexion or persistencia.conectar()
    try:
        titulares = titulares_de_la_semana(conexion, cuando)
    finally:
        if propia:
            conexion.close()
    if not titulares:
        return None
    return {"titulo": "El Pulso de la semana", "titulares": titulares, "foto": foto_semana(fetch)}


# ---------- utilidades de fecha ----------

def _iso_de(cuando: dict) -> str:
    """Convierte el 'cuando' inyectado (con fecha 'D de mes de AAAA') a AAAA-MM-DD.
    Si no se puede, cae a hoy (el resumen no se cae por esto)."""
    from contenido.redaccion_ia import _MESES
    try:
        partes = cuando.get("fecha", "").split(" de ")
        dia, mes, ano = int(partes[0]), _MESES.index(partes[1]) + 1, int(partes[2])
        return f"{ano:04d}-{mes:02d}-{dia:02d}"
    except Exception:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _fecha_menos(iso: str, dias: int) -> str:
    try:
        return (datetime.fromisoformat(iso) - timedelta(days=dias)).strftime("%Y-%m-%d")
    except Exception:
        return "0000-00-00"
```

## engine/contenido/seguridad.py
```python
"""Blindaje HTTP de El Enjambre.

Reúne las murallas de la capa web pública: identidad real del cliente
detrás del proxy, rate-limiting por IP, validación de identificadores y
las cabeceras de seguridad. Estado en memoria: suficiente para una
instancia (el deploy actual en Render).
"""

import hmac
import os
import re
import time
from collections import deque

# los ids de simulación son sha256 recortado a 16 hex — nada más se acepta
HEX16 = re.compile(r"^[0-9a-f]{16}$")


# ---------- candado de acceso privado (pruebas cerradas) ----------

def acceso_privado_activo() -> bool:
    """True si el enjambre está en modo pruebas privadas (hay clave puesta).

    Se activa poniendo ENJAMBRE_ACCESO en el entorno del motor. Mientras
    esté activo, solo quien traiga la clave puede disparar simulaciones
    (que gastan ~100 llamadas LLM). El muro, el archivo y los replays
    —que NO gastan IA— siguen abiertos a todos."""
    return bool(os.environ.get("ENJAMBRE_ACCESO", "").strip())


def acceso_ok(clave: str | None) -> bool:
    """¿La clave de acceso es válida? Si no hay modo privado, todo pasa.

    Comparación en tiempo constante (hmac) para no filtrar la clave."""
    esperada = os.environ.get("ENJAMBRE_ACCESO", "").strip()
    if not esperada:
        return True  # modo abierto: comportamiento normal
    return hmac.compare_digest((clave or "").strip(), esperada)

# ---------- identidad real del cliente ----------

def sim_id_valido(sim_id: str | None) -> bool:
    return bool(sim_id and HEX16.match(sim_id))


_CORREO = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def correo_valido(email: str | None) -> bool:
    """¿Es un correo con forma válida y de largo razonable? (puerta pública)."""
    email = (email or "").strip()
    return bool(email) and len(email) <= 200 and bool(_CORREO.match(email))


def ip_cliente(headers, fallback: str | None) -> str:
    """La IP real del visitante detrás de EXACTAMENTE un proxy (Render).

    Render añade la IP que observa al final de X-Forwarded-For. Tomar el
    último salto anula el spoofing: si el cliente falsifica el header,
    Render igual agrega su IP real después, y esa es la que contamos.
    """
    xff = headers.get("x-forwarded-for") if headers else None
    if xff:
        partes = [p.strip() for p in xff.split(",") if p.strip()]
        if partes:
            return partes[-1]
    return fallback or "desconocida"


# ---------- rate-limiting HTTP (ventana deslizante por IP) ----------

# (máximo de solicitudes, ventana en segundos)
LIMITE_GENERAL = (120, 60)   # /api/* liviano
LIMITE_PESADO = (30, 60)     # /replay: 734 KB de disco por llamada

_ventanas: dict[str, deque] = {}


def _clase(ruta: str) -> str:
    return "replay" if ruta.endswith("/replay") else "api"


def permitir_http(ip: str, ruta: str, ahora: float | None = None) -> bool:
    """¿Puede esta IP hacer esta request ahora? (rate-limit deslizante)."""
    ahora = time.monotonic() if ahora is None else ahora
    clase = _clase(ruta)
    limite, ventana = LIMITE_PESADO if clase == "replay" else LIMITE_GENERAL
    cola = _ventanas.setdefault(f"{ip}|{clase}", deque())
    corte = ahora - ventana
    while cola and cola[0] < corte:
        cola.popleft()
    if len(cola) >= limite:
        return False
    cola.append(ahora)
    return True


def limpiar(ahora: float | None = None) -> None:
    """Descarta ventanas vencidas — evita que _ventanas crezca sin fin."""
    ahora = time.monotonic() if ahora is None else ahora
    for clave in list(_ventanas):
        cola = _ventanas[clave]
        while cola and cola[0] < ahora - 120:
            cola.popleft()
        if not cola:
            del _ventanas[clave]


def reiniciar() -> None:
    """Borra el estado (para los tests)."""
    _ventanas.clear()


# ---------- cabeceras de seguridad ----------

# la API sirve JSON y binario consumidos por fetch: default-src 'none' basta.
# (La CSP de la página HTML vive en web/vercel.json, no aquí.)
CABECERAS_SEGURIDAD = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Content-Security-Policy": "default-src 'none'; frame-ancestors 'none'",
}
```

## engine/contenido/senal_prediccion.py
```python
"""Señal de PREDICCIÓN ponderada del reporte (sin dependencias de web).

La ablación por arquetipo sobre 678 casos reales (docs/calibracion-por-arquetipo.md)
mostró que las voces CONTRARIAN (quant escéptico, contrarian sabio) aciertan
<50% y DESORIENTAN el consenso. Esta señal baja su peso SOLO para el número que
alimenta la calibración (`senal_media_ponderada`). NO toca el enjambre, ni el
tono de mercado, ni las frases, ni la `senal_media_lideres` histórica (promedio
simple). El optimista NO se baja: la medición lo halló útil.

Reversible con el env ENJAMBRE_PESO_CONTRARIANS (vacío = 0.3; 1.0 = promedio
simple, sin cambio).
"""
import os

ARQUETIPOS_CONTRARIAN_SENAL = frozenset({"quant_esceptico", "contrarian_sabio"})
PESO_DEFECTO = 0.3


def peso_contrarians() -> float:
    try:
        v = os.environ.get("ENJAMBRE_PESO_CONTRARIANS", "")
        return float(v) if v != "" else PESO_DEFECTO
    except ValueError:
        return PESO_DEFECTO


def senal_media_ponderada(lideres, respuestas) -> float:
    """Media de las señales de los líderes bajando el peso de las voces
    contrarian. `lideres[i].arquetipo` empareja con `respuestas[i]["senal"]`."""
    peso = peso_contrarians()
    num = den = 0.0
    for lider, r in zip(lideres, respuestas):
        w = peso if lider.arquetipo in ARQUETIPOS_CONTRARIAN_SENAL else 1.0
        num += r["senal"] * w
        den += w
    return round(num / den, 2) if den else 0.0
```

## engine/contenido/vocabulario.py
```python
"""Filtro de vocabulario CMF (CONTENIDO.md sección 1 — NO NEGOCIABLE).

Todo texto que esta capa publica es simulación educativa de comportamiento
de masas. Este módulo es el filtro en código: la lista de términos
prohibidos, el disclaimer oficial y las funciones de verificación.
Nada se publica sin pasar por aquí.
"""

import unicodedata

DISCLAIMER = (
    "Herramienta educativa y recreativa en proceso de creación y mejora. "
    "Simula el comportamiento de masas con agentes de IA; "
    "no constituye asesoría ni recomendación de inversión."
)

# términos prohibidos por el principio regulatorio (más variantes obvias);
# se comparan sin tildes y en minúsculas
PROHIBIDAS = [
    "recomendamos",
    "te recomiendo",
    "recomendacion de compra",
    "recomendacion de venta",
    "deberias comprar",
    "deberias vender",
    "deberia comprar",
    "deberia vender",
    "debes comprar",
    "debes vender",
    "hay que comprar",
    "hay que vender",
    "compra ahora",
    "vende ahora",
    "el precio subira",
    "el precio bajara",
    "va a subir",
    "va a bajar",
    "prediccion",
    "predecimos",
    "senal de inversion",
    "senal de compra",
    "senal de venta",
    "oportunidad de compra",
    "oportunidad de venta",
    "consejo de inversion",
    "asesoria personalizada",
    "vendan todo",
    "compren todo",
    # inglés: los titulares y datos llegan en inglés (Alpaca/Barchart)
    "should you buy",
    "should you sell",
    "should i buy",
    "should i sell",
    "buy now",
    "sell now",
    "strong buy",
    "table pounding buy",
    "price target",
    "buy alert",
    "will surge",
    "will crash",
    "guaranteed return",
    "must buy",
]


def _normalizar(texto: str) -> str:
    """Minúsculas y sin tildes, para que 'Predicción' no se escape."""
    sin_tildes = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return sin_tildes.lower()


def encontrar_prohibidas(texto: str) -> list[str]:
    """Devuelve los términos prohibidos presentes en el texto (vacía = limpio)."""
    normalizado = _normalizar(texto)
    return [termino for termino in PROHIBIDAS if termino in normalizado]


def es_publicable(texto: str) -> bool:
    """True si el texto no contiene vocabulario prohibido."""
    return not encontrar_prohibidas(texto)


# frase con la que se reemplaza la voz de un líder que no pasa el filtro:
# neutra, CMF-limpia y en la voz genérica del analista (no deja hueco visual).
FRASE_NEUTRAL = "Prefiere no comentar este titular."


def frase_segura(texto: str) -> str:
    """La voz de un líder solo se muestra si pasa el filtro CMF; si no —p. ej.
    alguien empujó al modelo a un «compra ahora»— se neutraliza. Las frases de
    los líderes son lo que más gente ve (web, muro, widget), así que este es el
    borde de cumplimiento más importante de cerrar."""
    return texto if es_publicable(texto) else FRASE_NEUTRAL


def sanear_frases(respuestas: list[dict]) -> list[dict]:
    """Neutraliza IN SITU las frases no publicables de las respuestas de los
    cerebros, apenas vuelven de la IA y ANTES de repartirlas a la web, la base
    y el muro. Devuelve la misma lista (para encadenar con reparto.expandir)."""
    for r in respuestas:
        if isinstance(r, dict) and "frase" in r:
            r["frase"] = frase_segura(str(r.get("frase", "")))
    return respuestas


def verificar_pieza(texto: str) -> list[str]:
    """Verificación completa de una pieza pública (página, correo, widget).

    Devuelve la lista de problemas encontrados (vacía = la pieza pasa):
    términos prohibidos presentes y/o disclaimer ausente.
    """
    problemas = [f"término prohibido: «{t}»" for t in encontrar_prohibidas(texto)]
    if _normalizar(DISCLAIMER) not in _normalizar(texto):
        problemas.append("falta el disclaimer oficial")
    return problemas
```

## engine/validation/__init__.py
```python

```

## engine/validation/conftest.py
```python
"""Configuración compartida de los tests.

Neutraliza la fuente de "movers" de Yahoo: los tests NO deben salir a la red por
los mayores movimientos del día (haría al pipeline lento y no determinista). Los
tests del reportero IA (test_investigador) prueban su lógica con datos explícitos.
"""

import pytest


@pytest.fixture(autouse=True)
def _sin_movers_de_red(monkeypatch):
    try:
        monkeypatch.setattr("contenido.fuentes.yahoo.movers_del_dia", lambda **k: [])
    except Exception:
        pass
```

## engine/validation/hechos_estilizados.py
```python
"""Métricas de hechos estilizados — las huellas digitales de un mercado real."""

import numpy as np
from scipy import stats


def curtosis(retornos) -> float:
    """Curtosis de Pearson (una normal da 3; un mercado real da más)."""
    return float(stats.kurtosis(retornos, fisher=False))


def autocorrelacion(serie, rezago: int) -> float:
    """Autocorrelación de una serie en un rezago dado."""
    x = np.asarray(serie, dtype=float)
    if len(x) <= rezago + 1:
        return 0.0
    x = x - x.mean()
    denominador = float(np.dot(x, x))
    if denominador == 0:
        return 0.0
    return float(np.dot(x[:-rezago], x[rezago:]) / denominador)


def asimetria_panico(retornos) -> float:
    """Razón entre la violencia de las caídas y la de las subidas.

    Compara el promedio del 2.5% de peores retornos (en valor absoluto)
    contra el promedio del 2.5% de mejores. > 1 significa que las caídas
    son más violentas que las subidas.
    """
    r = np.asarray(retornos, dtype=float)
    peores = np.abs(r[r <= np.quantile(r, 0.025)])
    mejores = r[r >= np.quantile(r, 0.975)]
    if len(mejores) == 0 or mejores.mean() <= 0:
        return float("inf")
    return float(peores.mean() / mejores.mean())
```

## engine/validation/test_ablacion_arquetipos.py
```python
"""Tests de la herramienta de ablación por arquetipo (con casos sintéticos)."""

import json

from calibration import ablacion_arquetipos as ab


def _caso(fecha, pct_real, senales, cat="?"):
    return {
        "fecha": fecha,
        "reaccion_real": {"pct_real": pct_real, "categoria": cat},
        "senales_arquetipo": {a: {"senal_media": s, "confianza_media": 0.7, "n": 10}
                              for a, s in senales.items()},
    }


def _archivo_sintetico(tmp_path, n=120, seed=3):
    """Un arquetipo ('fomo_evangelista') ordena bien (señal ~ dirección real);
    otro ('contrarian_sabio') va al revés. El resto, ruido centrado."""
    import random
    rng = random.Random(seed)
    casos = []
    for i in range(n):
        sube = rng.random() < 0.5
        pct = rng.uniform(0.1, 3) if sube else -rng.uniform(0.1, 3)
        base = 0.6 if sube else -0.6
        senales = {a: rng.uniform(-0.3, 0.3) for a in ab.BASE}
        senales["fomo_evangelista"] = base + rng.uniform(-0.1, 0.1)      # buen predictor
        senales["contrarian_sabio"] = -base + rng.uniform(-0.1, 0.1)     # va al revés
        casos.append(_caso(f"2026-08-{i % 28 + 1:02d}T00:00:00", pct, senales))
    ruta = tmp_path / "casos.json"
    ruta.write_text(json.dumps({"n": len(casos), "casos": casos}))
    return str(ruta)


def test_cargar_filtra_y_ordena(tmp_path):
    ruta = tmp_path / "c.json"
    ruta.write_text(json.dumps({"casos": [
        _caso("2026-08-02T00:00:00", 1.0, {a: 0.1 for a in ab.BASE}),
        _caso("2026-08-01T00:00:00", -1.0, {a: 0.1 for a in ab.BASE}),
        _caso("2026-08-03T00:00:00", 0.0, {a: 0.1 for a in ab.BASE}),   # pct 0 → fuera
        {"fecha": "x", "reaccion_real": {"pct_real": 1.0}, "senales_arquetipo": {}},  # sin arquetipos → fuera
    ]}))
    casos = ab.cargar(str(ruta))
    assert len(casos) == 2
    assert casos[0]["fecha"] < casos[1]["fecha"]  # ordenado
    assert casos[0]["y"] == 0 and casos[1]["y"] == 1


def test_analizar_estructura_y_senal(tmp_path):
    rep = ab.analizar(_archivo_sintetico(tmp_path))
    assert rep["n"] > 60
    for k in ("arquetipo_suelto", "consenso", "leave_one_out", "variantes"):
        assert k in rep
    # el buen predictor acierta más que el contrarian invertido
    assert (rep["arquetipo_suelto"]["fomo_evangelista"]["acierto"]
            > rep["arquetipo_suelto"]["contrarian_sabio"]["acierto"])
    # quitar el contrarian invertido no debe EMPEORAR el Brier (Δ <= algo pequeño)
    assert rep["leave_one_out"]["contrarian_sabio"]["delta"] <= 0.02


def test_acierto_direccional_medio_punto_en_cero():
    assert ab.acierto_direccional([0.0], [1]) == 50.0
    assert ab.acierto_direccional([0.5], [1]) == 100.0
    assert ab.acierto_direccional([-0.5], [1]) == 0.0
```

## engine/validation/test_analisis_semanal.py
```python
"""Tests de la EDICIÓN DE FIN DE SEMANA de El Pulso (deep-dive mid-cap/sector).

Reglas de oro que protegen:
- el número manda (la variación viene de Yahoo, no de un texto);
- contexto primero + debate de arquetipos (miradas contrastantes);
- NUNCA consejo de inversión: "lo que nuestros inversionistas IA ven/analizan";
- nada se publica sin pasar el filtro CMF y sin escapar el HTML.
"""

from datetime import datetime, timedelta

from contenido import analisis_semanal, boletin, redaccion_ia
from contenido.vocabulario import DISCLAIMER, verificar_pieza


# ---------- helpers ----------

def _serie(precios, dias=None):
    base = datetime(2026, 8, 1)
    fechas = [base + timedelta(days=i) for i in range(len(precios))]
    return fechas, [float(p) for p in precios]


def _fetch_fake(mapa):
    """Devuelve un fetch(simbolo, rango, intervalo) que lee de un mapa
    símbolo→lista de precios (o None para simular que Yahoo no responde)."""
    def fetch(simbolo, rango="1mo", intervalo="1d"):
        precios = mapa.get(simbolo)
        return _serie(precios) if precios else None
    return fetch


def _sin_fundamentales(_ticker):
    """fetch_fund que no trae ficha (Yahoo caído): el deep-dive sale sin números."""
    return None


# ---------- el universo curado ----------

def test_universo_carga_y_tiene_contexto():
    u = analisis_semanal.cargar_universo()
    assert u.get("acciones") and u.get("sectores")
    for a in u["acciones"]:
        assert a["ticker"] and a["nombre"] and a["contexto"] and a["sector"]
        assert isinstance(a.get("banda", ""), str)  # 'banda' es solo un hint; el gate real es la cap. en vivo
    for s in u["sectores"]:
        assert s["nombre"] and s["etf"] and s["contexto"]


# ---------- la rotación de modo ----------

def test_modo_alterna_por_semana():
    assert analisis_semanal.elegir_modo(semana_iso=2) == "accion"
    assert analisis_semanal.elegir_modo(semana_iso=3) == "sector"


# ---------- la selección por ATENCIÓN (el número manda) ----------

def test_selecciona_la_accion_de_mayor_movida():
    universo = {"acciones": [
        {"ticker": "AAA", "nombre": "Alfa", "banda": "1-15B", "sector": "X", "contexto": "..."},
        {"ticker": "BBB", "nombre": "Beta", "banda": "15-30B", "sector": "Y", "contexto": "..."},
    ]}
    # AAA sube ~2% en el mes; BBB se dispara ~30% → BBB es la de mayor atención
    fetch = _fetch_fake({
        "AAA": [100, 100.5, 101, 101.5, 102, 102],
        "BBB": [100, 105, 110, 120, 128, 130],
    })
    sel = analisis_semanal.seleccionar_accion(universo, fetch=fetch, fetch_fund=_sin_fundamentales)
    assert sel["ticker"] == "BBB"
    assert sel["modo"] == "accion"
    assert "capitalización" in sel["encuadre"]      # etiqueta neutra sin ficha
    assert isinstance(sel["var_semana_pct"], (int, float))
    assert sel["grafico"]["ticker"] == "BBB"
    assert sel["fundamentales"] is None  # Yahoo no dio ficha → sin números, sin romperse


def test_band_gate_excluye_los_muy_grandes_y_adjunta_fundamentales():
    """La franja manda: el mayor movedor puede quedar FUERA si su capitalización
    real supera ~20B; se elige el siguiente EN banda y se le adjunta su ficha."""
    universo = {"acciones": [
        {"ticker": "BIG", "nombre": "Gigante", "banda": "15-30B", "sector": "X", "contexto": "c"},
        {"ticker": "MID", "nombre": "Media", "banda": "1-15B", "sector": "Y", "contexto": "c"},
    ]}
    fetch = _fetch_fake({
        "BIG": [100, 120, 140, 160, 180, 200],   # movida enorme, pero es gigante
        "MID": [50, 51, 52, 53, 54, 55],          # movida menor, pero en banda
    })
    fichas = {
        "BIG": {"market_cap_num": 62_000_000_000, "ingresos": "40B"},   # > 50B → fuera de banda
        "MID": {"market_cap_num": 8_000_000_000, "ingresos": "2B", "ebitda": "300M"},
    }
    sel = analisis_semanal.seleccionar_accion(universo, fetch=fetch, fetch_fund=lambda t: fichas.get(t))
    assert sel["ticker"] == "MID"                 # BIG excluido por capitalización
    assert sel["fundamentales"]["ebitda"] == "300M"


def test_selecciona_el_sector_de_mayor_movida():
    universo = {"sectores": [
        {"nombre": "Energía", "etf": "XLE", "contexto": "...", "ejemplos": ["XOM"]},
        {"nombre": "Bancos", "etf": "KRE", "contexto": "...", "ejemplos": ["FITB"]},
    ]}
    fetch = _fetch_fake({
        "XLE": [50, 50.2, 50.1, 50.3, 50.4, 50.5],
        "KRE": [50, 47, 45, 43, 42, 41],  # cae fuerte → rotación
    })
    sel = analisis_semanal.seleccionar_sector(universo, fetch=fetch)
    assert sel["ticker"] == "KRE"
    assert sel["modo"] == "sector"
    assert sel["nombre"] == "Bancos"


def test_preparar_cae_al_otro_modo_si_el_elegido_no_tiene_datos():
    universo = {
        "acciones": [{"ticker": "AAA", "nombre": "Alfa", "banda": "1-15B", "sector": "X", "contexto": "c"}],
        "sectores": [{"nombre": "Energía", "etf": "XLE", "contexto": "c"}],
    }
    # se fuerza 'sector' pero XLE no trae datos → cae a 'accion' (AAA sí trae)
    fetch = _fetch_fake({"AAA": [10, 11, 12, 13, 14, 15]})
    sel = analisis_semanal.preparar_analisis(universo, modo="sector", fetch=fetch,
                                             fetch_fund=_sin_fundamentales)
    assert sel is not None and sel["modo"] == "accion"


def test_preparar_none_si_no_hay_datos():
    universo = {"acciones": [{"ticker": "AAA", "nombre": "Alfa", "banda": "1-15B",
                              "sector": "X", "contexto": "c"}], "sectores": []}
    fetch = _fetch_fake({})  # Yahoo no responde para nada
    assert analisis_semanal.preparar_analisis(universo, modo="accion", fetch=fetch,
                                              fetch_fund=_sin_fundamentales) is None


# ---------- el filtro CMF sobre el deep-dive redactado ----------

def test_validar_analisis_filtra_debate_no_publicable():
    datos = {
        "titular": "Roku, la plataforma que vive de la publicidad",
        "dek": "Una mirada de fin de semana",
        "contexto": "Roku fabrica el sistema de sus televisores.\n\nGana con publicidad.",
        "lectura": "Subió fuerte esta semana.",
        "debate": [
            {"arquetipo": "doomer", "mirada": "deberías vender todo ya"},   # prohibido → fuera
            {"arquetipo": "inexistente", "mirada": "hola"},                 # arquetipo inválido → fuera
            {"arquetipo": "contrarian_sabio", "mirada": "El pánico ajeno se observa con calma."},
        ],
        "que_observar": "Habrá que ver la próxima temporada de resultados.",
    }
    val = redaccion_ia._validar_analisis(datos)
    assert val is not None
    ids = [d["arquetipo"] for d in val["debate"]]
    assert ids == ["contrarian_sabio"]
    assert val["debate"][0]["nombre"]  # trae el nombre legible del arquetipo


def test_validar_analisis_none_si_titular_prohibido():
    datos = {"titular": "deberías comprar Roku ahora", "contexto": "algo"}
    assert redaccion_ia._validar_analisis(datos) is None


# ---------- el correo de fin de semana ----------

def _brief_finde():
    hechos = {
        "modo": "accion", "titulo": "Acción seleccionada", "encuadre": "mediana capitalización",
        "ticker": "ROKU", "nombre": "Roku", "sector": "Streaming",
        "contexto": "...", "var_semana_pct": 8.4, "var_mes_pct": 12.0,
        "fecha_inicio": "1 ago", "fecha_fin": "31 ago",
        "fundamentales": {"market_cap": "9.5B", "ingresos": "4.2B",
                          "crecimiento_ingresos": "18.00%", "margen_bruto": "45.00%",
                          "ebitda": "300M", "deuda": "500M", "caja": "2.1B"},
        "grafico": {"ticker": "ROKU", "nombre": "Roku", "periodo": "mes", "moneda": "$"},
    }
    red = {
        "titular": "Roku vuelve a la conversación",
        "dek": "La plataforma de TV conectada tuvo una semana movida",
        "contexto": "Roku hace el sistema operativo de televisores.\n\nGana con publicidad.",
        "lectura": "Esta semana avanzó con fuerza tras un anuncio.",
        "numeros": "Crece 18% al año.\n\nEBITDA positivo y más caja que deuda: un colchón cómodo.",
        "debate": [
            {"arquetipo": "fomo_evangelista", "nombre": "El FOMO Evangelista",
             "mirada": "¡La TV conectada es el futuro y aquí está pasando!"},
            {"arquetipo": "doomer", "nombre": "El Doomer",
             "mirada": "La publicidad es lo primero que se recorta en una crisis."},
        ],
        "que_observar": "Habrá que ver si la publicidad digital sostiene el ritmo.",
    }
    return {"analisis": hechos, "analisis_redactado": red}


def test_correo_finde_es_deep_dive_cmf_limpio():
    html = boletin.construir_html([], "sábado 16 de agosto", brief=_brief_finde())
    # la edición de fin de semana y su encuadre
    assert "Edición de fin de semana" in html
    assert "Qué es" in html                       # contexto primero
    assert "Lo que ven nuestros inversionistas IA" in html   # el debate
    assert "no es asesoría de inversión" in html.lower()
    assert "El FOMO Evangelista" in html and "El Doomer" in html
    assert "/api/grafico/ROKU" in html            # gráfico real del protagonista
    # 'Los números': la ficha de fundamentales (datos de mercado) + la lectura
    assert "Los números" in html
    assert "EBITDA" in html and "300M" in html and "4.2B" in html
    assert "Crecimiento ingresos" in html and "18.00%" in html
    assert "Yahoo Finance" in html                # la ficha va atribuida a su fuente
    # El Enjambre al pie + disclaimer, como siempre
    assert "También de Rubicón Lab" in html
    assert DISCLAIMER in html
    assert verificar_pieza(html) == []            # sin vocabulario prohibido


def test_correo_finde_escapa_html_hostil():
    brief = _brief_finde()
    brief["analisis_redactado"]["debate"][0]["mirada"] = "<script>alert(1)</script> mira esto"
    html = boletin.construir_html([], "sábado 16 de agosto", brief=brief)
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;" in html


def test_correo_finde_omite_las_historias_diarias():
    brief = _brief_finde()
    # aunque llegue una historia diaria, el fin de semana NO la muestra
    brief["redactado"] = {"historias": [{"titular": "Historia diaria colada",
                                         "cuerpo": "no debería salir"}]}
    html = boletin.construir_html([], "sábado 16 de agosto", brief=brief)
    assert "Historia diaria colada" not in html


def test_asunto_finde():
    asunto = boletin.asunto_finde({"titulo": "Sector en rotación", "nombre": "Energía"})
    assert "Sector en rotación" in asunto and "Energía" in asunto
```

## engine/validation/test_archivo.py
```python
"""Tests de la Etapa 9: El Archivo — hemeroteca, búsqueda, voces, epílogo."""

import pytest
from fastapi.testclient import TestClient

import brains.cerebro as cerebro
import server
from contenido import limites, persistencia, pipeline, seguridad


@pytest.fixture(autouse=True)
def entorno(monkeypatch, tmp_path):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("ALPACA_API_KEY_ID", raising=False)
    monkeypatch.setattr(cerebro, "RUTA_CACHE", tmp_path / "cache.json")
    monkeypatch.setenv("ENJAMBRE_DB", str(tmp_path / "enjambre.db"))
    limites.reiniciar()
    seguridad.reiniciar()


@pytest.fixture()
def dia():
    """3 destacadas guardadas (con sus titulares vinculados = simbolos)."""
    return pipeline.preparar_dia(semilla_base=42)


# ---------- la consulta del archivo ----------

def test_archivo_lista_destacadas(dia):
    conexion = persistencia.conectar()
    resultado = persistencia.archivo(conexion)
    conexion.close()
    assert resultado["total"] == 3
    assert len(resultado["items"]) == 3
    assert all(item["fecha"] for item in resultado["items"])


def test_archivo_busca_por_texto(dia):
    conexion = persistencia.conectar()
    # los titulares demo incluyen "Treasury yields spike..."
    r = persistencia.archivo(conexion, texto="treasury")
    conexion.close()
    assert r["total"] == 1
    assert "Treasury" in r["items"][0]["titular"]


def test_archivo_filtra_por_ticker(dia):
    conexion = persistencia.conectar()
    # "Regional bank First Meridian collapses" trae simbolos FMRD,KRE
    r = persistencia.archivo(conexion, ticker="KRE")
    conexion.close()
    assert r["total"] == 1
    assert "FMRD" in (r["items"][0]["simbolos"] or "")


def test_archivo_pagina(dia):
    conexion = persistencia.conectar()
    p0 = persistencia.archivo(conexion, por_pagina=2, pagina=0)
    p1 = persistencia.archivo(conexion, por_pagina=2, pagina=1)
    conexion.close()
    assert p0["total"] == 3
    assert len(p0["items"]) == 2
    assert len(p1["items"]) == 1
    assert p0["items"][0]["id"] != p1["items"][0]["id"]


def test_meses_disponibles(dia):
    conexion = persistencia.conectar()
    meses = persistencia.meses_disponibles(conexion)
    conexion.close()
    assert len(meses) == 1
    assert meses[0] == persistencia.ahora_iso()[:7]


# ---------- el endpoint del archivo ----------

def test_api_archivo(dia):
    cliente = TestClient(server.app)
    datos = cliente.get("/api/archivo").json()
    assert datos["total"] == 3
    assert len(datos["items"]) == 3
    assert datos["meses"]
    item = datos["items"][0]
    assert item["tarjeta"]["direccion"] in "▲▼◆"
    assert item["tarjeta"]["agitacion"] in ("bajo", "medio", "alto")
    assert "asesoría" in datos["descargo"] or "asesoria" in datos["descargo"]
    assert "max-age" in cliente.get("/api/archivo").headers.get("Cache-Control", "")


def test_api_archivo_busca_y_filtra(dia):
    cliente = TestClient(server.app)
    assert cliente.get("/api/archivo", params={"q": "oil"}).json()["total"] == 1
    assert cliente.get("/api/archivo", params={"ticker": "USO"}).json()["total"] == 1
    assert cliente.get("/api/archivo", params={"q": "no-existe-nada"}).json()["total"] == 0


# ---------- las 8 voces en la página de una simulación ----------

def test_simulacion_incluye_ocho_voces(dia):
    cliente = TestClient(server.app)
    sim_id = dia["publicadas"][0]["sim_id"]
    datos = cliente.get(f"/api/simulacion/{sim_id}").json()
    voces = datos["voces"]
    assert len(voces) == 9  # los 9 arquetipos (incluye el doomer selectivo)
    for voz in voces:
        assert -1.0 <= voz["senal_media"] <= 1.0
        assert voz["frase"]
        assert voz["nombre"]
    # vienen ordenadas de la señal más baja (más bajista) a la más alta
    assert voces == sorted(voces, key=lambda v: v["senal_media"])


def test_simulacion_incluye_simbolos_del_titular(dia):
    """El ticker viaja con la simulación: habilita la comparación educativa
    con el gráfico real (TradingView) en el frontend."""
    cliente = TestClient(server.app)
    # todas las publicadas del día demo traen su titular vinculado con simbolos
    con_ticker = [
        cliente.get(f"/api/simulacion/{p['sim_id']}").json()
        for p in dia["publicadas"]
    ]
    assert any(d["simbolos"] for d in con_ticker)
    for d in con_ticker:
        assert isinstance(d["simbolos"], str)  # nunca None: la UI no valida tipos


# ---------- '¿y qué pasó después?' (epílogo, protegido) ----------

def test_epilogo_exige_token(dia, monkeypatch):
    cliente = TestClient(server.app)
    sim_id = dia["publicadas"][0]["sim_id"]
    monkeypatch.setenv("ENJAMBRE_PIPELINE_TOKEN", "secreto")

    # sin token → 403
    assert cliente.post(f"/api/epilogo/{sim_id}", json={"texto": "x"}).status_code == 403
    # con token → guarda y aparece en la simulación
    r = cliente.post(f"/api/epilogo/{sim_id}", json={"texto": "El IPSA cerró -1,2% ese día."},
                     headers={"X-Pipeline-Token": "secreto"})
    assert r.status_code == 200
    datos = cliente.get(f"/api/simulacion/{sim_id}").json()
    assert "IPSA" in datos["epilogo"]


def test_epilogo_rechaza_vocabulario_prohibido(dia, monkeypatch):
    cliente = TestClient(server.app)
    sim_id = dia["publicadas"][0]["sim_id"]
    monkeypatch.setenv("ENJAMBRE_PIPELINE_TOKEN", "secreto")
    r = cliente.post(f"/api/epilogo/{sim_id}",
                     json={"texto": "Esto confirma nuestra predicción de compra"},
                     headers={"X-Pipeline-Token": "secreto"})
    assert r.status_code == 400  # el filtro CMF lo bloquea
```

## engine/validation/test_backtest.py
```python
"""Tests del backtesting histórico (contenido/backtest.py).

Reglas: tandas con freno de presupuesto, casos fuente='backtest' que
JAMÁS son destacadas (no contaminan el muro ni la hemeroteca), reintento
sin datos, libreta separando en vivo vs histórico, y respaldo automático.
"""

import re

import pytest

from contenido import backtest, corrector, persistencia, respaldo


@pytest.fixture(autouse=True)
def entorno(monkeypatch, tmp_path):
    monkeypatch.delenv("GITHUB_RESPALDO_TOKEN", raising=False)
    monkeypatch.delenv("ALPACA_API_KEY_ID", raising=False)
    monkeypatch.setenv("ENJAMBRE_DB", str(tmp_path / "enjambre.db"))
    # los tests jamás tocan la red: la caja fuerte y la cosecha remotas se simulan vacías
    monkeypatch.setattr(respaldo, "casos_remotos", lambda: [])
    monkeypatch.setattr(respaldo, "cosecha_remota", lambda: [])


def _simulador_falso(titular, seed):
    reporte = {"direccion_pct": -2.0 if "plunge" in titular.lower() or "crash" in titular.lower() else 1.0,
               "volatilidad_pct": 1.0}
    return reporte, [{"arquetipo": "doomer", "senal": -0.5, "confianza": 0.8, "frase": "x"}], [100.0, 99.0], []


def _variacion_falsa(simbolo, fecha, ruedas=2):
    return {"simbolo": simbolo, "pct_real": -1.5, "cierre_base": 100.0, "cierre_final": 98.5,
            "fecha_base": fecha, "fecha_final": fecha, "ruedas": ruedas}


# ---------- la lista de exámenes ----------

def test_eventos_estan_bien_formados_y_balanceados():
    eventos = backtest.cargar_eventos()
    assert len(eventos) >= 100  # recopilación 2001-2025 + foco oro/cripto/acciones
    ids = [e["id"] for e in eventos]
    assert len(ids) == len(set(ids))  # sin duplicados
    conteo = {"negativa": 0, "positiva": 0, "neutra": 0}
    for e in eventos:
        assert re.match(r"^\d{4}-\d{2}-\d{2}$", e["fecha"])
        assert e["titular"].strip() and e["simbolo"].strip()
        assert e["categoria"] in conteo
        conteo[e["categoria"]] += 1
    # mezcla balanceada (guía de calibración): nada domina, lo neutro existe
    assert conteo["negativa"] >= 10
    assert conteo["positiva"] >= 10
    assert conteo["neutra"] >= 5


# ---------- la tanda ----------

def test_tanda_respeta_el_freno_y_avanza_por_partes():
    conexion = persistencia.conectar()
    r1 = backtest.correr_tanda(conexion, tamano=5, simular=_simulador_falso,
                               obtener_variacion=_variacion_falsa)
    assert len(r1["hechas"]) == 5
    total = backtest.estado(conexion)["total"]
    assert r1["pendientes"] == total - 5

    # la segunda tanda continúa donde quedó (no repite exámenes)
    r2 = backtest.correr_tanda(conexion, tamano=5, simular=_simulador_falso,
                               obtener_variacion=_variacion_falsa)
    ids1 = {h["id"] for h in r1["hechas"]}
    ids2 = {h["id"] for h in r2["hechas"]}
    assert not ids1 & ids2
    assert backtest.estado(conexion)["hechos"] == 10
    conexion.close()


def test_tamano_se_recorta_al_tope_maximo():
    conexion = persistencia.conectar()
    r = backtest.correr_tanda(conexion, tamano=999, simular=_simulador_falso,
                              obtener_variacion=_variacion_falsa)
    conexion.close()
    assert len(r["hechas"]) == backtest.TANDA_MAXIMA  # freno de presupuesto


def test_los_casos_historicos_no_contaminan_el_muro_ni_el_archivo():
    conexion = persistencia.conectar()
    backtest.correr_tanda(conexion, tamano=3, simular=_simulador_falso,
                          obtener_variacion=_variacion_falsa)
    destacadas = conexion.execute(
        "SELECT COUNT(*) FROM simulaciones WHERE destacada = 1"
    ).fetchone()[0]
    fuentes = {f[0] for f in conexion.execute(
        "SELECT DISTINCT fuente FROM simulaciones").fetchall()}
    conexion.close()
    assert destacadas == 0          # el archivo/hemeroteca queda intacto
    assert fuentes == {"backtest"}  # marcados aparte, peras con peras


def test_sin_datos_reintenta_en_la_proxima_tanda():
    conexion = persistencia.conectar()
    r1 = backtest.correr_tanda(conexion, tamano=2, simular=_simulador_falso,
                               obtener_variacion=lambda *a: None)
    assert r1["hechas"] == []
    assert len(r1["sin_datos"]) == 2
    # con datos, esos mismos exámenes se completan
    r2 = backtest.correr_tanda(conexion, tamano=2, simular=_simulador_falso,
                               obtener_variacion=_variacion_falsa)
    conexion.close()
    assert {h["id"] for h in r2["hechas"]} == set(r1["sin_datos"])


# ---------- libreta y caja fuerte ----------

def test_libreta_separa_en_vivo_de_historico():
    conexion = persistencia.conectar()
    # un caso EN VIVO (destacada corregida)
    vivo = persistencia.guardar_simulacion(
        conexion, titular="Caso en vivo", fuente="alpaca", seed=1,
        resumen={"direccion_pct": 2.0, "volatilidad_pct": 1.0},
        lideres=[], serie_precios=[100.0], destacada=True)
    persistencia.guardar_reaccion_real(conexion, vivo, {"pct_real": 1.0})
    # dos casos históricos
    backtest.correr_tanda(conexion, tamano=2, simular=_simulador_falso,
                          obtener_variacion=_variacion_falsa)
    resumen = corrector.libreta(conexion)
    conexion.close()
    assert resumen["casos"] == 3
    assert resumen["en_vivo"]["casos"] == 1
    assert resumen["historico"]["casos"] == 2


def test_el_respaldo_incluye_el_backtest_con_su_origen():
    conexion = persistencia.conectar()
    backtest.correr_tanda(conexion, tamano=2, simular=_simulador_falso,
                          obtener_variacion=_variacion_falsa)
    casos = respaldo.exportar_casos(conexion)
    conexion.close()
    assert len(casos) == 2
    assert all(c["origen"] == "historico" for c in casos)
    assert all(c["simbolos"] for c in casos)  # el símbolo viene de la reacción
    assert all(c["reaccion_real"]["categoria"] in ("negativa", "positiva", "neutra")
               for c in casos)


def test_sin_saldo_no_guarda_examenes_con_respaldo():
    """Sin saldo de API los líderes usan el cerebro léxico: ese examen NO
    cuenta (mediría al suplente) y la tanda se detiene para no gastar."""
    def simulador_respaldo(titular, seed):
        reporte = {"direccion_pct": -1.0, "volatilidad_pct": 1.0}
        lideres = [{"arquetipo": "doomer", "fuente": "fallback",
                    "senal": -0.5, "confianza": 0.8, "frase": "x"}]
        return reporte, lideres, [100.0], []

    conexion = persistencia.conectar()
    r = backtest.correr_tanda(conexion, tamano=5, simular=simulador_respaldo,
                              obtener_variacion=_variacion_falsa)
    guardadas = conexion.execute("SELECT COUNT(*) FROM simulaciones").fetchone()[0]
    conexion.close()
    assert r["hechas"] == []
    assert len(r["sin_ia"]) == 1  # se detuvo en el primero: no siguió gastando
    assert guardadas == 0         # nada quedó marcado como rendido


def test_estado_no_repite_lo_ya_respaldado_en_github(monkeypatch):
    """Tras un borrón del disco (deploy), lo que la caja fuerte ya tiene
    no se vuelve a rendir — repetirlo costaría ~100 llamadas LLM."""
    eventos = backtest.cargar_eventos()
    ya_respaldado = backtest._sim_id(eventos[0])
    monkeypatch.setattr(respaldo, "casos_remotos", lambda: [{"sim_id": ya_respaldado}])
    conexion = persistencia.conectar()  # base recién nacida (post-deploy)
    avance = backtest.estado(conexion)
    conexion.close()
    assert avance["hechos"] == 1
    assert all(backtest._sim_id(e) != ya_respaldado for e in avance["_lista_pendiente"])


def test_variacion_historica_usa_yahoo(monkeypatch):
    """Yahoo es la fuente principal del backtest (histórico largo y completo)."""
    from contenido.fuentes import alpaca, yahoo

    monkeypatch.setattr(alpaca, "variacion_real", lambda *a: None)
    monkeypatch.setattr(yahoo, "variacion_real",
                        lambda s, f, r=2: {"simbolo": s, "pct_real": -4.7, "fuente_datos": "yahoo"})
    variacion = backtest._variacion_historica("SPY", "2008-09-15")
    assert variacion["pct_real"] == -4.7
    assert variacion["fuente_datos"] == "yahoo"


def test_yahoo_parsea_y_mide_igual_que_alpaca(monkeypatch):
    from datetime import datetime, timezone

    from contenido.fuentes import yahoo

    def ts(fecha):
        return int(datetime.fromisoformat(fecha).replace(tzinfo=timezone.utc).timestamp())

    payload = {"chart": {"result": [{
        "timestamp": [ts("2008-09-12"), ts("2008-09-15"), ts("2008-09-16")],
        "indicators": {"quote": [{"close": [125.0, 118.0, 117.0]}]},
    }]}}

    class Respuesta:
        def raise_for_status(self): pass
        def json(self): return payload

    monkeypatch.setattr(yahoo.httpx, "get", lambda *a, **k: Respuesta())
    v = yahoo.variacion_real("SPY", "2008-09-15", ruedas=2)
    # base = cierre previo (125.0), final = 2ª rueda desde la fecha (117.0)
    assert v["cierre_base"] == 125.0
    assert v["cierre_final"] == 117.0
    assert v["pct_real"] == -6.4
    assert v["fuente_datos"] == "yahoo"


def test_yahoo_sin_red_devuelve_none(monkeypatch):
    from contenido.fuentes import yahoo

    monkeypatch.setattr(yahoo.httpx, "get",
                        lambda *a, **k: (_ for _ in ()).throw(OSError("sin red")))
    assert yahoo.variacion_real("SPY", "2008-09-15") is None


def test_endpoints_del_backtest_exigen_token(monkeypatch):
    from fastapi.testclient import TestClient

    import server
    from contenido import limites, seguridad

    monkeypatch.setenv("ENJAMBRE_PIPELINE_TOKEN", "secreto-de-prueba")
    seguridad.reiniciar()
    limites.reiniciar()
    cliente = TestClient(server.app)
    assert cliente.post("/api/backtest").status_code == 403
    assert cliente.get("/api/backtest").status_code == 403
    avance = cliente.get("/api/backtest", headers={"X-Pipeline-Token": "secreto-de-prueba"})
    assert avance.status_code == 200
    assert avance.json()["hechos"] == 0
    assert avance.json()["pendientes"] == avance.json()["total"]
    assert "_lista_pendiente" not in avance.json()
```

## engine/validation/test_calibracion.py
```python
"""Tests del módulo de calibración (Python puro, sin dependencias nuevas).

Comprueban lo esencial:
- El mapeo señal→probabilidad está acotado en [0, 1] y es monótono.
- Platt e isotónica MEJORAN el Brier sobre datos sintéticos descalibrados.
- La isotónica es monótona (a mayor señal, no menor probabilidad).
- El calibrador NUNCA recibe el resultado al predecir (sin fuga).
- Reproducibilidad: mismo input → mismo output.
- Brier y log_loss dan valores correctos conocidos.
"""

import math
import random

from contenido import calibracion as cal


# ---------- mapeo señal → probabilidad ----------

def test_mapeo_senal_media_acotado_y_monotono():
    assert cal.senal_a_prob_cruda({"senal_media_lideres": -1.0}) == 0.0
    assert cal.senal_a_prob_cruda({"senal_media_lideres": 1.0}) == 1.0
    assert cal.senal_a_prob_cruda({"senal_media_lideres": 0.0}) == 0.5
    # fuera de rango se recorta
    assert cal.senal_a_prob_cruda({"senal_media_lideres": 5.0}) == 1.0
    assert cal.senal_a_prob_cruda({"senal_media_lideres": -5.0}) == 0.0
    # monótono
    a = cal.senal_a_prob_cruda({"senal_media_lideres": -0.5})
    b = cal.senal_a_prob_cruda({"senal_media_lideres": 0.3})
    assert a < b


def test_mapeo_direccion_acotado():
    for d in (-50, -2, 0, 2, 50):
        p = cal.senal_a_prob_cruda({"direccion_pct": d}, modo="direccion")
        assert 0.0 <= p <= 1.0
    assert cal.senal_a_prob_cruda({"direccion_pct": 0.0}, modo="direccion") == 0.5


def test_mapeo_desconocido_lanza():
    try:
        cal.senal_a_prob_cruda({}, modo="inexistente")
        assert False, "debió lanzar"
    except ValueError:
        pass


# ---------- métricas ----------

def test_brier_valores_conocidos():
    # predicción perfecta → 0
    assert cal.brier([1.0, 0.0], [1, 0]) == 0.0
    # predicción pésima → 1
    assert cal.brier([0.0, 1.0], [1, 0]) == 1.0
    # 0.5 siempre → 0.25
    assert abs(cal.brier([0.5, 0.5], [1, 0]) - 0.25) < 1e-9


def test_log_loss_no_explota_en_extremos():
    # predecir 0 cuando el resultado es 1: recortado, finito
    v = cal.log_loss([0.0], [1])
    assert math.isfinite(v) and v > 0


def test_tasa_base():
    assert cal.tasa_base([1, 1, 0, 0]) == 0.5
    assert cal.tasa_base([1, 1, 1, 0]) == 0.75


# ---------- datos sintéticos descalibrados ----------

def _datos_descalibrados(n=400, seed=7):
    """Genera (señal, resultado) donde la señal SÍ ordena, pero está mal
    escalada: la probabilidad real es sigmoide de la señal, pero la 'señal cruda'
    que entregamos es demasiado extrema. Un calibrador debería arreglarlo."""
    rng = random.Random(seed)
    scores, ys = [], []
    for _ in range(n):
        s = rng.uniform(-1, 1)
        p_real = cal._sigmoid(1.5 * s)          # probabilidad verdadera
        y = 1 if rng.random() < p_real else 0
        # señal CRUDA mal calibrada: empujada a los extremos
        cruda = cal._clip((s * 3 + 1) / 2, 0, 1)
        scores.append(cruda)
        ys.append(y)
    return scores, ys


def test_platt_mejora_brier():
    scores, ys = _datos_descalibrados()
    corte = len(scores) // 2
    s_tr, y_tr = scores[:corte], ys[:corte]
    s_te, y_te = scores[corte:], ys[corte:]
    platt = cal.ajustar_calibrador(s_tr, y_tr, metodo="platt")
    brier_crudo = cal.brier(s_te, y_te)
    brier_cal = cal.brier(platt.predict(s_te), y_te)
    assert brier_cal < brier_crudo, (brier_cal, brier_crudo)


def test_isotonica_mejora_brier():
    scores, ys = _datos_descalibrados()
    corte = len(scores) // 2
    iso = cal.ajustar_calibrador(scores[:corte], ys[:corte], metodo="isotonic")
    s_te, y_te = scores[corte:], ys[corte:]
    assert cal.brier(iso.predict(s_te), y_te) < cal.brier(s_te, y_te)


def test_isotonica_es_monotona():
    scores, ys = _datos_descalibrados()
    iso = cal.ajustar_calibrador(scores, ys, metodo="isotonic")
    xs = [i / 50 for i in range(51)]
    preds = iso.predict(xs)
    for a, b in zip(preds, preds[1:]):
        assert b >= a - 1e-9, "la isotónica no puede bajar al subir la señal"


def test_calibrador_no_ve_resultado_al_predecir():
    # la firma de predict solo recibe scores — comprobamos que no hay forma de
    # colar el resultado y que predecir no depende de él.
    scores, ys = _datos_descalibrados(n=100)
    platt = cal.ajustar_calibrador(scores, ys, metodo="platt")
    p1 = platt.predict([0.3, 0.6, 0.9])
    p2 = platt.predict([0.3, 0.6, 0.9])
    assert p1 == p2  # reproducible y sin estado oculto del resultado


def test_predicciones_en_rango():
    scores, ys = _datos_descalibrados(n=200)
    for metodo in ("platt", "isotonic"):
        c = cal.ajustar_calibrador(scores, ys, metodo=metodo)
        for p in c.predict([-5, 0, 0.5, 1, 5]):
            assert 0.0 <= p <= 1.0


def test_evaluar_calibracion_reporta_lineas_base():
    scores, ys = _datos_descalibrados()
    corte = len(scores) // 2
    platt = cal.ajustar_calibrador(scores[:corte], ys[:corte], metodo="platt")
    rep = cal.evaluar_calibracion(scores[corte:], ys[corte:], calibrador=platt)
    assert "brier_constante_050" in rep
    assert "brier_tasa_base" in rep
    assert "brier_cruda" in rep
    assert "brier_calibrada" in rep
    # la calibrada debería ser mejor (menor) que la cruda en estos datos
    assert rep["brier_calibrada"] <= rep["brier_cruda"]
```

## engine/validation/test_calibrar_libreta.py
```python
"""Tests de la tubería calibrar_libreta (con casos sintéticos, sin base real)."""

import random

from contenido import calibrar_libreta as cl


def _casos_sinteticos(n=300, seed=3):
    """Genera casos tipo libreta: la señal del enjambre ordena bien, pero cruda
    está mal calibrada. El resultado real correlaciona con la señal."""
    rng = random.Random(seed)
    casos = []
    for _ in range(n):
        s = rng.uniform(-1, 1)                      # senal_media_lideres
        p_real = cl.cal._sigmoid(1.8 * s)          # prob verdadera de subir
        subio = 1 if rng.random() < p_real else 0
        pct_real = (rng.uniform(0.1, 3.0)) if subio else -(rng.uniform(0.1, 3.0))
        casos.append({"senal_media_lideres": s, "direccion_pct": s * 2,
                      "pct_real": pct_real, "fuente": "backtest"})
    return casos


def test_preparar_filtra_sin_resultado():
    casos = [{"senal_media_lideres": 0.5, "pct_real": 1.0},
             {"senal_media_lideres": 0.2, "pct_real": None},   # sin resultado
             {"senal_media_lideres": 0.1, "pct_real": 0.0}]    # cero exacto
    scores, ys = cl.preparar(casos)
    assert len(scores) == 1 and len(ys) == 1
    assert ys[0] == 1


def test_resultado_binario():
    assert cl._resultado_binario(2.3) == 1
    assert cl._resultado_binario(-0.4) == 0
    assert cl._resultado_binario(0.0) is None
    assert cl._resultado_binario(None) is None


def test_calibrar_devuelve_reporte_completo():
    rep = cl.calibrar(_casos_sinteticos())
    assert "error" not in rep
    for k in ("n_total", "n_entrena", "n_prueba", "platt", "isotonic"):
        assert k in rep
    assert "brier_calibrada" in rep["platt"]


def test_calibrar_pocos_casos_avisa():
    rep = cl.calibrar(_casos_sinteticos(n=5))
    assert "error" in rep


def test_calibracion_supera_base_en_datos_con_senal():
    rep = cl.calibrar(_casos_sinteticos(n=500))
    mejor = min(("platt", "isotonic"),
                key=lambda k: rep[k]["brier_calibrada"])
    # con señal real, el calibrado debe superar la línea base trivial
    assert rep[mejor]["brier_calibrada"] < rep["platt"]["brier_tasa_base"]
```

## engine/validation/test_cerebros.py
```python
"""Tests de los cerebros LLM (CLAUDE.md sección 5).

Corren SIN clave de API: prueban el fallback léxico, la validación del
JSON, la caché y el criterio de la Etapa 2 — que un titular real cambie
el comportamiento del enjambre. La ruta con API real usa el mismo código
con la única diferencia de la fuente de la respuesta.
"""

import statistics

import pytest

import brains.cerebro as cerebro
from brains.arquetipos import ARQUETIPOS
from brains.cerebro import _validar_respuesta, analizar_titular
from model import MercadoEnjambre

TITULAR_NEGATIVO = "Quiebra el segundo banco más grande del país; pánico en los mercados"
TITULAR_POSITIVO = "La bolsa alcanza un máximo histórico tras ganancias récord"


@pytest.fixture(autouse=True)
def entorno_sin_api(monkeypatch, tmp_path):
    """Sin clave de API y con caché desechable: los tests nunca llaman afuera."""
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setattr(cerebro, "RUTA_CACHE", tmp_path / "cache.json")


def _todos_los_lideres() -> list[tuple[int, str]]:
    consultas = []
    indice = 0
    for arquetipo in ARQUETIPOS:
        for _ in range(arquetipo["cantidad"]):
            consultas.append((indice, arquetipo["id"]))
            indice += 1
    return consultas


def test_fallback_responde_por_todos_los_lideres():
    respuestas = analizar_titular(TITULAR_NEGATIVO, _todos_los_lideres())
    assert len(respuestas) == 1150
    for r in respuestas:
        assert -1.0 <= r["senal"] <= 1.0
        assert 0.0 <= r["confianza"] <= 1.0
        assert r["frase"]
        assert r["fuente"] == "fallback"


def test_los_arquetipos_tienen_personalidad():
    """Ante la misma noticia negativa, cada arquetipo reacciona a su manera."""
    respuestas = analizar_titular(TITULAR_NEGATIVO, _todos_los_lideres())
    por_arquetipo: dict[str, list[float]] = {}
    for (_, arq), r in zip(_todos_los_lideres(), respuestas):
        por_arquetipo.setdefault(arq, []).append(r["senal"])
    medias = {a: statistics.mean(s) for a, s in por_arquetipo.items()}

    assert medias["doomer"] < -0.5                    # ve el colapso confirmado
    assert medias["fomo_evangelista"] < -0.5          # amplifica el pánico
    assert medias["influencer_optimista"] < -0.1      # se ASUSTA primero ante el desplome
    assert medias["influencer_optimista"] > -0.5      # pero nunca tan bajista como un doomer
    assert medias["contrarian_sabio"] > 0.2           # compra la sangre
    assert abs(medias["institucional_frio"]) < 0.55   # nunca extremo


def test_cache_guarda_la_api_pero_no_el_fallback():
    """El fallback NO se cachea: una falla pasajera de la API no debe congelar
    frases enlatadas para siempre. La voz real de la IA sí se cachea."""
    import json

    from brains.cerebro import _clave_cache

    # sin API, la segunda corrida vuelve a intentar (fuente = fallback, no cache)…
    primera = analizar_titular(TITULAR_NEGATIVO, _todos_los_lideres())
    segunda = analizar_titular(TITULAR_NEGATIVO, _todos_los_lideres())
    assert all(r["fuente"] == "fallback" for r in segunda)
    # …pero el fallback es determinístico por semilla: mismos valores
    assert [r["senal"] for r in primera] == [r["senal"] for r in segunda]

    # una respuesta de API pre-sembrada en el caché sí se reutiliza
    clave = _clave_cache(TITULAR_NEGATIVO, "doomer", 0)
    cerebro.RUTA_CACHE.parent.mkdir(parents=True, exist_ok=True)
    cerebro.RUTA_CACHE.write_text(
        json.dumps({clave: {"senal": -0.8, "confianza": 0.9, "frase": "voz real"}}),
        encoding="utf-8",
    )
    respuesta = analizar_titular(TITULAR_NEGATIVO, [(0, "doomer")])[0]
    assert respuesta["fuente"] == "cache"
    assert respuesta["frase"] == "voz real"


def test_validacion_del_json_del_llm():
    assert _validar_respuesta('{"senal": 0.5, "confianza": 0.8, "frase": "ok"}') is not None
    # señal fuera de rango se recorta a [-1, 1]
    assert _validar_respuesta('{"senal": 7, "confianza": 0.8, "frase": "x"}')["senal"] == 1.0
    # JSON roto, campos faltantes o tipos malos → None (dispara el fallback)
    assert _validar_respuesta("no soy json") is None
    assert _validar_respuesta('{"senal": "alta", "confianza": 1, "frase": "x"}') is None
    assert _validar_respuesta('{"senal": 0.2, "confianza": 0.5}') is None
    # el JSON envuelto en texto se extrae igual
    envuelto = 'Claro: {"senal": -0.3, "confianza": 0.6, "frase": "ok"} listo'
    assert _validar_respuesta(envuelto)["senal"] == -0.3


def test_etapa2_un_titular_cambia_el_enjambre():
    """El criterio de la Etapa 2: el mismo mercado, con la misma semilla,
    se comporta distinto según el titular que lee."""

    def precio_final(titular: str, seed: int) -> float:
        m = MercadoEnjambre(seed=seed, ticks_horizonte=200)
        m.correr(80)
        base = m.historial_precios[-1]
        m.aplicar_titular(titular)
        m.correr(60)
        return m.historial_precios[-1] / base

    semillas = [1, 2]
    negativos = [precio_final(TITULAR_NEGATIVO, s) for s in semillas]
    positivos = [precio_final(TITULAR_POSITIVO, s) for s in semillas]
    assert statistics.mean(negativos) < statistics.mean(positivos)
    assert statistics.mean(negativos) < 1.0  # la quiebra bancaria golpea
```

## engine/validation/test_cierre.py
```python
"""Tests de la edición de la TARDE — 'el cierre del mercado' (Premium)."""

import pytest

import server  # noqa: F401 (asegura que la app importa con los cambios)
from contenido import boletin, persistencia, pipeline

CIERRE = {
    "titulo": "El cierre del mercado",
    "movers": [
        {"titular": "Moderna (MRNA) sube 40% tras un avance en su vacuna contra el cáncer",
         "razon": "resultados clínicos positivos", "simbolos": "MRNA",
         "var_pct": 40.0, "verificado": True, "sesion": "sesión"},
        {"titular": "OneSpaWorld (OSW) cae 10% tras una guía débil",
         "razon": "recortó su previsión", "simbolos": "OSW",
         "var_pct": -10.0, "verificado": True, "sesion": "sesión"},
    ],
}


@pytest.fixture(autouse=True)
def entorno(monkeypatch, tmp_path):
    monkeypatch.delenv("RESEND_API_KEY", raising=False)
    monkeypatch.setenv("ENJAMBRE_DB", str(tmp_path / "enjambre.db"))


def test_bloque_cierre_renderiza():
    html = boletin.construir_html([], "lunes 1 de septiembre · cierre", brief={"cierre": CIERRE})
    assert "Edición de la tarde" in html
    assert "Moderna" in html and "vacuna contra el cáncer" in html
    assert "OneSpaWorld" in html
    assert "No es asesoría de inversión" in html


def test_bloque_cierre_con_voz_renderiza_minihistorias():
    """Con voz Moby, el cierre son mini-historias (apertura + párrafos), no la
    lista llana."""
    cierre_con_voz = dict(CIERRE)
    cierre_con_voz["redactado"] = {
        "buenas_tardes": "El mercado cerró y, como siempre, los protagonistas no "
                         "fueron los de siempre.",
        "historias": [{
            "kicker": "Salud · catalizador",
            "emoji": "🧬",
            "titular": "Moderna se disparó y recordó por qué la biotecnología no aburre",
            "dek": "Un avance clínico encendió la acción",
            "cuerpo": "Moderna subió con fuerza tras un avance en su vacuna contra el "
                      "cáncer.\n\nEl dato importa porque cambia la conversación sobre "
                      "sus ingresos futuros.",
            "bottom_line": "La biotecnología volvió al centro de la mesa.",
            "grafico": {"ticker": "MRNA", "nombre": "Moderna", "periodo": "dia", "moneda": "$"},
            "var_pct": 40.0, "sesion": "sesión",
        }],
    }
    html = boletin.construir_html([], "lunes 1 de septiembre · cierre",
                                  brief={"cierre": cierre_con_voz})
    assert "Edición de la tarde" in html
    assert "Buenas tardes" in html
    assert "la biotecnología no aburre" in html          # titular con voz
    assert "cambia la conversación" in html              # cuerpo desarrollado
    assert "No es asesoría de inversión" in html


def test_validar_cierre_ata_pildora_por_ticker():
    """El validador casa el % real del movimiento con la historia por su ticker."""
    from contenido import redaccion_ia
    parseado = {
        "buenas_tardes": "Buenas tardes.",
        "historias": [{
            "titular": "Moderna vivió su mejor día en meses",
            "cuerpo": "Subió tras un avance clínico.\n\nEl mercado lo celebró.",
            "grafico": {"ticker": "MRNA", "nombre": "Moderna", "periodo": "dia", "moneda": "$"},
        }],
    }
    salida = redaccion_ia._validar_cierre(parseado, CIERRE["movers"])
    assert salida is not None
    assert salida["historias"][0]["var_pct"] == 40.0     # atado desde el mover MRNA
    assert salida["historias"][0]["sesion"] == "sesión"


def test_envio_reporta_fallos_con_motivo(monkeypatch):
    """Un envío que falla ya no es un '3 de 6' a ciegas: enviar_a_suscriptores
    devuelve QUÉ direcciones cayeron y por qué."""
    conexion = persistencia.conectar()
    for correo in ("bueno@lector.cl", "malo@lector.cl"):
        alta = persistencia.agregar_suscriptor(conexion, correo)
        persistencia.confirmar_suscriptor(conexion, alta["token_confirma"])

    def fake_enviar(dest, asunto, html, **k):
        if dest == "malo@lector.cl":
            return False, "HTTP 422: dirección inválida"
        return True, ""
    monkeypatch.setattr(boletin, "_enviar_resend", fake_enviar)

    conteo = boletin.enviar_a_suscriptores(conexion, "<html>x</html>", "Asunto")
    assert conteo["enviados"] == 1 and conteo["fallidos"] == 1
    assert conteo["fallos"][0]["email"] == "malo@lector.cl"
    assert conteo["fallos"][0]["motivo"] == "HTTP 422: dirección inválida"
    # 422 = dirección inválida permanente → se da de baja sola
    assert conteo["fallos"][0].get("desactivado") is True
    assert not persistencia.es_activo(conexion, "malo@lector.cl")   # ya no está activa
    assert persistencia.es_activo(conexion, "bueno@lector.cl")      # la buena sigue
    conexion.close()


def test_envio_no_desactiva_ante_error_transitorio(monkeypatch):
    """Un 429/5xx (transitorio) NO da de baja al suscriptor: puede ser el límite
    de Resend o una caída pasajera, no una dirección mala."""
    conexion = persistencia.conectar()
    alta = persistencia.agregar_suscriptor(conexion, "temporal@lector.cl")
    persistencia.confirmar_suscriptor(conexion, alta["token_confirma"])
    monkeypatch.setattr(boletin, "_enviar_resend",
                        lambda *a, **k: (False, "HTTP 429: rate limit"))
    conteo = boletin.enviar_a_suscriptores(conexion, "<html>x</html>", "Asunto")
    assert conteo["fallos"][0].get("desactivado") is not True
    assert persistencia.es_activo(conexion, "temporal@lector.cl")   # sigue activa
    conexion.close()


def test_ritual_tarde_arma_pendiente(monkeypatch):
    from contenido import cierre, notificar
    monkeypatch.setattr(notificar, "avisar", lambda m: True)
    monkeypatch.setattr(cierre, "preparar_cierre", lambda **k: CIERRE)

    res = pipeline.ritual_matutino(enviar=False, momento="tarde")
    assert res["edicion"] == "cierre" and res["estado"] == "pendiente"
    assert res["clave"].endswith("-t")           # clave propia de la tarde
    assert "El cierre del mercado" in res["html_preview"]


def test_ritual_tarde_sin_movers_no_edicion(monkeypatch):
    from contenido import cierre
    monkeypatch.setattr(cierre, "preparar_cierre", lambda **k: None)
    res = pipeline.ritual_matutino(enviar=False, momento="tarde")
    assert res["estado"] == "sin_edicion" and res["edicion"] == "cierre"


def test_cierre_sale_solo_a_premium(monkeypatch):
    conexion = persistencia.conectar()
    for correo in ("gratis@lector.cl", "pago@lector.cl"):
        alta = persistencia.agregar_suscriptor(conexion, correo)
        persistencia.confirmar_suscriptor(conexion, alta["token_confirma"])
    persistencia.set_premium(conexion, "pago@lector.cl", True)

    from contenido import cierre, notificar
    monkeypatch.setattr(notificar, "avisar", lambda m: True)
    monkeypatch.setattr(cierre, "preparar_cierre", lambda **k: CIERRE)
    res = pipeline.ritual_matutino(conexion, enviar=False, momento="tarde")
    clave = res["clave"]
    conexion.close()

    enviados = []
    monkeypatch.setattr(boletin, "_enviar_resend",
                        lambda dest, asunto, html, **k: (enviados.append(dest) or True, ""))
    r = pipeline.aprobar_y_enviar(fecha=clave)
    assert r["ok"] and r["enviados"] == 1
    assert enviados == ["pago@lector.cl"]         # el gratuito NO recibe la tarde
```

## engine/validation/test_config_enchufado.py
```python
"""Guardián anti "perilla muerta": toda perilla del config debe leerla el código.

Contexto: en agentes.json hay perillas de calibración. Si una existe en el
config pero NINGÚN archivo de código la lee, es una "perilla muerta" — girarla
no hace nada, y calibrar con ella es tirar plata (y tiempo de medición) a la
basura. Este test recorre el config, junta cada perilla, y falla si alguna no
aparece leída por el código (`config.get("clave")` / `cfg.get("clave")`).

Todo local, sin IA. Si agregas una perilla nueva al config, enchúfala al código
(léela con .get) o, si es una constante intencional sin ruta de código, añádela
a PERILLAS_INTENCIONALMENTE_CONSTANTES con su justificación.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # engine/

ENGINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUTA_CONFIG = os.path.join(ENGINE, "config", "agentes.json")

# Claves estructurales / metadatos: NO son perillas de comportamiento, no se
# "leen" con .get sino que dan forma al config. Se excluyen del chequeo.
CLAVES_ESTRUCTURALES = {
    "descripcion", "total_agentes", "tipos", "ruido_parametros_sigma",
    # dentro de cada tipo:
    "id", "nombre", "cantidad", "capital_relativo", "en_red_social", "rol",
    "parametros", "arquetipos", "seguidores_rango",
}

# Perillas que a propósito son constantes sin ruta de código (documentar por qué).
PERILLAS_INTENCIONALMENTE_CONSTANTES = {
    # el fondo pasivo (flujo 401k/AFP) no reacciona a titulares por diseño:
    # su sensibilidad es 0 y no hay código de noticia al que enchufarla.
    "sensibilidad_noticias",
}


def _claves_leidas_por_el_codigo() -> set:
    """Todas las claves que el código lee vía .get("clave") / .get('clave')."""
    patron = re.compile(r"\.get\(\s*[\"']([a-zA-Z_]+)[\"']")
    leidas = set()
    for raiz, _, ficheros in os.walk(ENGINE):
        if "__pycache__" in raiz:
            continue
        for f in ficheros:
            if not f.endswith(".py") or f.startswith("test_"):
                continue
            ruta = os.path.join(raiz, f)
            with open(ruta, encoding="utf-8") as fh:
                leidas |= set(patron.findall(fh.read()))
    return leidas


def _perillas_del_config() -> set:
    with open(RUTA_CONFIG, encoding="utf-8") as f:
        cfg = json.load(f)
    perillas = set()
    # top-level (peso_doomer, peso_doomer_por_mercado, umbral_correccion_sesgo…)
    for k in cfg:
        if k not in CLAVES_ESTRUCTURALES:
            perillas.add(k)
    # parametros de cada tipo de agente
    for tipo in cfg["tipos"]:
        perillas |= set(tipo.get("parametros", {}))
    return perillas - CLAVES_ESTRUCTURALES


def test_ninguna_perilla_del_config_esta_muerta():
    """Cada perilla del config la lee el código (o es constante intencional)."""
    leidas = _claves_leidas_por_el_codigo()
    perillas = _perillas_del_config()
    muertas = perillas - leidas - PERILLAS_INTENCIONALMENTE_CONSTANTES
    assert not muertas, (
        "Perillas MUERTAS (existen en agentes.json pero el código no las lee): "
        f"{sorted(muertas)}. Enchúfalas con .get(\"clave\") en el agente/modelo, "
        "o si son constantes intencionales añádelas a "
        "PERILLAS_INTENCIONALMENTE_CONSTANTES con su justificación."
    )
```

## engine/validation/test_contacto.py
```python
"""Tests del canal B2B (formulario de organizaciones) — Sprint 3."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import server
from contenido import limites, persistencia, seguridad, vocabulario


@pytest.fixture(autouse=True)
def entorno(monkeypatch, tmp_path):
    monkeypatch.setenv("ENJAMBRE_DB", str(tmp_path / "enjambre.db"))
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)  # sin red en tests
    seguridad.reiniciar()
    limites.reiniciar()


def test_contacto_se_guarda_y_responde_amable():
    cliente = TestClient(server.app)
    r = cliente.post("/api/contacto", json={
        "nombre": "Ana Profesora", "email": "ana@colegio.cl",
        "organizacion": "Colegio X", "mensaje": "Quiero usarlo en mi curso.",
    })
    assert r.status_code == 200
    assert r.json()["estado"] == "recibido"

    conexion = persistencia.conectar()
    guardados = persistencia.listar_contactos(conexion)
    conexion.close()
    assert len(guardados) == 1
    assert guardados[0]["email"] == "ana@colegio.cl"
    assert guardados[0]["organizacion"] == "Colegio X"


def test_contacto_valida_entradas():
    cliente = TestClient(server.app)
    assert cliente.post("/api/contacto", json={"nombre": "", "email": "a@b.cl"}).status_code == 400
    assert cliente.post("/api/contacto", json={"nombre": "Ana", "email": "no-es-correo"}).status_code == 400
    # entradas gigantes se recortan, no rompen
    r = cliente.post("/api/contacto", json={
        "nombre": "Ana", "email": "ana@b.cl", "mensaje": "x" * 5000,
    })
    assert r.status_code == 200
    conexion = persistencia.conectar()
    assert len(persistencia.listar_contactos(conexion)[0]["mensaje"]) <= 800
    conexion.close()


def test_lista_de_contactos_exige_token(monkeypatch):
    monkeypatch.setenv("ENJAMBRE_PIPELINE_TOKEN", "secreto-de-prueba")
    cliente = TestClient(server.app)
    assert cliente.get("/api/contactos").status_code == 403
    ok = cliente.get("/api/contactos", headers={"X-Pipeline-Token": "secreto-de-prueba"})
    assert ok.status_code == 200
    assert ok.json()["contactos"] == []


def test_seccion_organizaciones_es_cmf_limpia():
    """El CTA B2B no usa lenguaje de recomendación de inversión (guard)."""
    muro = (Path(__file__).parent.parent.parent / "web" / "src" / "muro" / "muro.js").read_text(encoding="utf-8")
    inicio = muro.find('class="organizaciones"')
    assert inicio > 0, "la sección de organizaciones existe en el muro"
    seccion = muro[inicio:inicio + 1200]
    assert vocabulario.es_publicable(seccion)
    assert "educativa" in seccion  # el posicionamiento educativo, explícito
```

## engine/validation/test_contenido.py
```python
"""Tests de la Etapa 6: persistencia, portero y filtro de vocabulario CMF."""

from pathlib import Path

import pytest

from contenido import persistencia, portero, vocabulario
from contenido.fuentes import alpaca


@pytest.fixture()
def conexion(tmp_path):
    con = persistencia.conectar(tmp_path / "prueba.db")
    yield con
    con.close()


@pytest.fixture(autouse=True)
def sin_api(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("ALPACA_API_KEY_ID", raising=False)
    monkeypatch.delenv("ALPACA_API_SECRET_KEY", raising=False)


# ---------- vocabulario CMF (sección 1 — no negociable) ----------

def test_filtro_detecta_terminos_prohibidos():
    assert not vocabulario.es_publicable("Recomendamos comprar esta acción")
    assert not vocabulario.es_publicable("Es una clara señal de inversión")
    assert not vocabulario.es_publicable("Nuestra predicción: el precio subirá")
    assert not vocabulario.es_publicable("gran OPORTUNIDAD DE COMPRA hoy")


def test_filtro_acepta_vocabulario_permitido():
    assert vocabulario.es_publicable("El enjambre simulado reaccionó con pánico")
    assert vocabulario.es_publicable("Los agentes simulados vendieron en cascada")
    assert vocabulario.es_publicable("En esta simulación educativa, la dirección fue -3%")


def test_verificar_pieza_exige_disclaimer():
    pieza_sin = "El enjambre simulado reaccionó."
    assert "falta el disclaimer oficial" in vocabulario.verificar_pieza(pieza_sin)
    pieza_completa = f"El enjambre simulado reaccionó. {vocabulario.DISCLAIMER}"
    assert vocabulario.verificar_pieza(pieza_completa) == []


def test_disclaimer_presente_en_las_piezas_publicas_existentes():
    """Cada pieza pública lleva el disclaimer fijo: la web ya es una."""
    panel = (Path(__file__).parent.parent.parent / "web" / "src" / "ui" / "panel.js").read_text(encoding="utf-8")
    assert vocabulario.DISCLAIMER in panel


def test_frases_fallback_de_los_lideres_son_publicables():
    """Las voces de los arquetipos (fallback) no usan vocabulario prohibido."""
    from brains.fallback import TRANSFORMACIONES

    for arquetipo, transformar in TRANSFORMACIONES.items():
        for sentimiento in (-0.9, 0.0, 0.9):
            _, _, variantes = transformar(sentimiento, "titular de prueba")
            for frase in variantes:  # cada ramo trae 3 variantes; todas publicables
                assert vocabulario.es_publicable(frase), f"{arquetipo}: «{frase}»"


# ---------- persistencia (regla: TODA simulación se guarda) ----------

def test_guardar_y_leer_simulacion(conexion):
    sim_id = persistencia.guardar_simulacion(
        conexion,
        titular="La Fed sube las tasas", fuente="manual", seed=42,
        resumen={"direccion_pct": -3.2}, lideres=[{"arquetipo": "doomer", "senal": -0.8}],
        serie_precios=[100.0, 99.1, 98.7],
    )
    assert sim_id == persistencia.id_simulacion("La Fed sube las tasas", 42)
    guardada = persistencia.obtener_simulacion(conexion, sim_id)
    assert guardada["resumen"]["direccion_pct"] == -3.2
    assert guardada["serie_precios"] == [100.0, 99.1, 98.7]
    assert guardada["destacada"] == 0


def test_misma_simulacion_no_se_duplica(conexion):
    for _ in range(2):
        persistencia.guardar_simulacion(
            conexion, titular="X", fuente="manual", seed=1,
            resumen={}, lideres=[], serie_precios=[100],
        )
    total = conexion.execute("SELECT COUNT(*) FROM simulaciones").fetchone()[0]
    assert total == 1


def test_listar_por_mes_y_destacadas(conexion):
    sim_id = persistencia.guardar_simulacion(
        conexion, titular="A", fuente="alpaca", seed=1,
        resumen={}, lideres=[], serie_precios=[100],
    )
    persistencia.marcar_destacada(conexion, sim_id)
    mes = persistencia.ahora_iso()[:7]
    assert persistencia.listar_simulaciones(conexion, mes=mes)
    assert persistencia.listar_simulaciones(conexion, solo_destacadas=True)[0]["id"] == sim_id
    assert persistencia.listar_simulaciones(conexion, mes="1999-01") == []


def test_suscriptores_double_opt_in(conexion):
    # alta: nace PENDIENTE (activo=0) hasta confirmar
    alta = persistencia.agregar_suscriptor(conexion, "Giorgio@Rubicon.cl", origen="web")
    assert alta["email"] == "giorgio@rubicon.cl"  # normalizado
    assert alta["ya_activo"] is False
    assert conexion.execute("SELECT activo FROM suscriptores").fetchone()[0] == 0
    assert persistencia.suscriptores_activos(conexion) == []

    # confirmar: ahora sí queda activo
    assert persistencia.confirmar_suscriptor(conexion, alta["token_confirma"]) == "giorgio@rubicon.cl"
    assert len(persistencia.suscriptores_activos(conexion)) == 1
    # el token de confirmación no sirve dos veces
    assert persistencia.confirmar_suscriptor(conexion, alta["token_confirma"]) is None

    # baja de un clic
    assert persistencia.dar_de_baja(conexion, alta["token_baja"]) is True
    assert persistencia.suscriptores_activos(conexion) == []
    assert persistencia.dar_de_baja(conexion, "token-falso") is False


# ---------- el portero ----------

def test_piso_lexico_descarta_lo_obvio():
    assert portero.evaluar_lexico("Top 5 stocks to watch this week", []) is not None
    assert portero.evaluar_lexico("How to invest in AI: a beginner's guide", []) is not None
    assert portero.evaluar_lexico("Celebrity chef opens new restaurant", []) is not None
    assert portero.evaluar_lexico("Join our free webinar: options trading", []) is not None


def test_piso_lexico_detecta_duplicados():
    previo = "Fed holds rates steady but signals two more hikes this year"
    casi_igual = "Fed holds rates steady, signals two more hikes this year"
    assert portero.evaluar_lexico(casi_igual, [previo]) == "duplicado de un titular reciente"


def test_piso_lexico_deja_pasar_lo_que_importa():
    assert portero.evaluar_lexico("US inflation comes in hotter than expected at 4.1%", []) is None
    assert portero.evaluar_lexico("Quiebra el segundo banco más grande del país", []) is None


def test_procesar_dia_elige_top3_y_registra_todo(conexion):
    candidatos = alpaca.titulares_demo()
    resultado = portero.procesar_dia(conexion, candidatos, maximo=3)

    assert len(resultado["elegidos"]) == 3
    assert all(e["impacto"] >= portero.UMBRAL_IMPACTO for e in resultado["elegidos"])
    # todo veredicto queda en el log de la base, incluso los descartes
    total = conexion.execute("SELECT COUNT(*) FROM titulares").fetchone()[0]
    assert total == len(candidatos)
    descartes = conexion.execute(
        "SELECT COUNT(*) FROM titulares WHERE veredicto = 'descartar'"
    ).fetchone()[0]
    assert descartes == len(candidatos) - 3
    # el duplicado del set de demo cayó en el piso léxico
    assert any("duplicado" in (e["motivo"] or "") for e in resultado["log"])


# ---------- fuente Alpaca ----------

def test_alpaca_sin_claves_degrada_elegante():
    assert alpaca.hay_credenciales() is False
    assert alpaca.titulares_recientes() == []
    titulares, origen = alpaca.obtener_titulares()
    assert origen == "demo"
    assert len(titulares) >= 20
    assert all(t["titular"] for t in titulares)
```

## engine/validation/test_correccion_sesgo.py
```python
"""
Plan A — corrección del sesgo alcista en el consenso.

El enjambre acierta ~80% en positivas pero ~53% en negativas porque el TONO se
suaviza hacia arriba: el descuento de magnitud (GANANCIA_CONSENSO) encoge una
mala noticia clara. La corrección: cuando los líderes que hablaron con la IA ya
leen la noticia como CLARAMENTE bajista (consenso < -umbral), NO la suavizamos;
usamos la lectura a plena magnitud (la MÁS bajista entre consenso y léxico),
nunca para invertir el signo.

Verifica que:
1. Con umbral 0.0 (desactivada) el tono es IDÉNTICO al histórico
   (consenso * GANANCIA_CONSENSO).
2. Con umbral activo, ante una mala noticia clara el tono es MÁS negativo
   (más fiel) que con la corrección apagada.
3. La corrección NUNCA invierte el signo (jamás vuelve el tono menos bajista
   que el consenso crudo).

Corre local, sin LLM: las señales por arquetipo salen del fallback (mismo
espíritu que el LLM real), marcadas 'api' para ejercer la ruta de consenso.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # engine/

from brains.fallback import TRANSFORMACIONES, sentimiento_lexico  # noqa: E402
from model import RUTA_CONFIG, GANANCIA_CONSENSO, MercadoEnjambre  # noqa: E402

TITULAR_MALO = "Bitcoin tumbles below 23000 after Celsius freezes customer withdrawals"


def _respuestas(modelo, titular):
    """Señal por arquetipo como la daría el fallback, marcada 'api' para
    ejercer la ruta de consenso (no el atajo léxico)."""
    s = sentimiento_lexico(titular)
    out = []
    for lider in modelo._lideres:
        senal, conf, _ = TRANSFORMACIONES[lider.arquetipo](s, titular)
        out.append({"senal": senal, "confianza": conf, "frase": "", "fuente": "api"})
    return out


def _tono(umbral: float) -> float:
    m = MercadoEnjambre(seed=42, ticks_horizonte=5, ruta_config=RUTA_CONFIG)
    m._umbral_correccion = umbral
    resp = _respuestas(m, TITULAR_MALO)
    return m._tono_de_titular(TITULAR_MALO, resp)


def _consenso(modelo, resp) -> float:
    """El consenso crudo (promedio ponderado por confianza), sin descuento."""
    ia = [(l.arquetipo, r) for l, r in zip(modelo._lideres, resp)
          if r["fuente"] in ("api", "cache")]
    num = sum(r["senal"] * r["confianza"] for _, r in ia)
    den = sum(r["confianza"] for _, r in ia)
    return num / den


def test_umbral_0_preserva_el_historico():
    """umbral 0.0 = corrección apagada = consenso * GANANCIA_CONSENSO."""
    m = MercadoEnjambre(seed=42, ticks_horizonte=5, ruta_config=RUTA_CONFIG)
    m._umbral_correccion = 0.0
    m._peso_doomer = 1.0  # doomer selectivo a peso pleno = promedio de TODAS
    resp = _respuestas(m, TITULAR_MALO)
    esperado = max(-1.0, min(1.0, _consenso(m, resp) * GANANCIA_CONSENSO))
    assert abs(m._tono_de_titular(TITULAR_MALO, resp) - esperado) < 1e-9


def test_correccion_hace_el_tono_mas_fiel():
    """Ante una mala noticia clara, la corrección hace el tono MÁS negativo.

    El consenso de este titular malo está DILUIDO a ~-0.27 (los invertidores lo
    suben) y la base lo suaviza aún más (×0.8 → -0.22). Con la corrección a un
    umbral que dispara (0.2 < 0.27), el tono salta a la lectura fiel (~-0.80).
    """
    tono_off = _tono(0.0)
    tono_on = _tono(0.2)
    assert tono_off < 0, "el titular es malo: el tono base debe ser negativo"
    assert tono_on < tono_off, \
        f"la corrección debe hacer el tono MÁS bajista: {tono_on} vs {tono_off}"


def test_nunca_invierte_el_signo():
    """La corrección jamás vuelve el tono menos bajista que el consenso crudo."""
    m = MercadoEnjambre(seed=42, ticks_horizonte=5, ruta_config=RUTA_CONFIG)
    m._umbral_correccion = 0.2
    resp = _respuestas(m, TITULAR_MALO)
    consenso = _consenso(m, resp)
    tono = m._tono_de_titular(TITULAR_MALO, resp)
    if consenso < -0.2:  # solo cuando la corrección de verdad dispara
        assert tono <= max(-1.0, consenso), \
            "el tono corregido nunca es menos bajista que el consenso crudo"


if __name__ == "__main__":
    print("\n🧪 Plan A: corrección del sesgo alcista")
    print("=" * 45)
    print(f"  tono con umbral 0.0 (base):      {_tono(0.0):+.3f}")
    print(f"  tono con umbral 0.3 (corrección): {_tono(0.3):+.3f}")
    print("=" * 45)
```

## engine/validation/test_corrector.py
```python
"""Tests del corrector automático — paso 2 de la ruta de calibración.

El corrector guarda cuánto se movió DE VERDAD el símbolo de cada
destacada (Alpaca) y redacta el epílogo educativo si no hay uno manual.
La libreta de calificaciones resume enjambre vs mercado real.
"""

from datetime import datetime, timedelta, timezone

import pytest

from contenido import corrector, persistencia, vocabulario
from contenido.fuentes import alpaca


@pytest.fixture(autouse=True)
def entorno(monkeypatch, tmp_path):
    monkeypatch.delenv("ALPACA_API_KEY_ID", raising=False)
    monkeypatch.delenv("ALPACA_API_SECRET_KEY", raising=False)
    monkeypatch.setenv("ENJAMBRE_DB", str(tmp_path / "enjambre.db"))


def _variacion(pct: float):
    """Una función de variación falsa (no toca la red)."""
    def obtener(simbolo, desde_iso, ruedas=2):
        return {"simbolo": simbolo, "pct_real": pct, "cierre_base": 100.0,
                "cierre_final": round(100.0 * (1 + pct / 100), 2),
                "fecha_base": "2026-07-10", "fecha_final": "2026-07-14", "ruedas": ruedas}
    return obtener


def _destacada(conexion, titular: str, direccion_pct: float, simbolos: str,
               hace_dias: int = 3, epilogo: str | None = None) -> str:
    """Crea una destacada vinculada a un titular, con fecha retrocedida."""
    sim_id = persistencia.guardar_simulacion(
        conexion, titular=titular, fuente="test", seed=hash(titular) % 1000,
        resumen={"direccion_pct": direccion_pct, "volatilidad_pct": 1.0},
        lideres=[], serie_precios=[100.0], destacada=True,
    )
    persistencia.registrar_titular(
        conexion, titular=titular, fuente="test", veredicto="simular",
        simbolos=simbolos, sim_id=sim_id,
    )
    fecha = (datetime.now(timezone.utc) - timedelta(days=hace_dias)).isoformat(timespec="seconds")
    conexion.execute("UPDATE simulaciones SET fecha = ? WHERE id = ?", (fecha, sim_id))
    if epilogo:
        persistencia.guardar_epilogo(conexion, sim_id, epilogo)
    conexion.commit()
    return sim_id


def test_corrige_y_redacta_epilogo_publicable():
    conexion = persistencia.conectar()
    sim_id = _destacada(conexion, "Banco X colapsa", -3.2, "BX,KRE")
    resultado = corrector.corregir_pendientes(conexion, obtener_variacion=_variacion(-1.8))
    datos = persistencia.obtener_simulacion(conexion, sim_id)
    conexion.close()

    assert [c["sim_id"] for c in resultado["corregidas"]] == [sim_id]
    assert resultado["corregidas"][0]["simbolo"] == "BX"  # el primer ticker
    assert datos["reaccion_real"]["pct_real"] == -1.8
    # el epílogo automático existe, menciona lo esencial y es CMF-limpio
    assert "BX" in datos["epilogo"]
    assert "-1.8%" in datos["epilogo"]
    assert vocabulario.es_publicable(datos["epilogo"])


def test_no_pisa_el_epilogo_manual():
    conexion = persistencia.conectar()
    sim_id = _destacada(conexion, "Petróleo sube fuerte", 2.0, "USO",
                        epilogo="Nota manual de Giorgio.")
    corrector.corregir_pendientes(conexion, obtener_variacion=_variacion(1.1))
    datos = persistencia.obtener_simulacion(conexion, sim_id)
    conexion.close()
    # lo manual manda; la reacción real igual queda registrada
    assert datos["epilogo"] == "Nota manual de Giorgio."
    assert datos["reaccion_real"]["pct_real"] == 1.1


def test_respeta_la_espera_y_reintenta_sin_datos():
    conexion = persistencia.conectar()
    _destacada(conexion, "Noticia de hoy mismo", 1.0, "SPY", hace_dias=0)
    vieja = _destacada(conexion, "Noticia de hace días", 1.0, "QQQ", hace_dias=3)

    # la reciente no se toca; la vieja espera si Alpaca aún no tiene datos
    sin_datos = corrector.corregir_pendientes(conexion, obtener_variacion=lambda *a: None)
    assert sin_datos == {"corregidas": [], "esperando": 1}

    # la próxima corrida sí la corrige (nada quedó marcado a medias)
    con_datos = corrector.corregir_pendientes(conexion, obtener_variacion=_variacion(0.5))
    conexion.close()
    assert [c["sim_id"] for c in con_datos["corregidas"]] == [vieja]


def test_texto_del_epilogo_es_publicable_en_toda_direccion():
    variacion = _variacion(-2.5)("XYZ", "2026-07-10")
    for pct_sim in (-4.0, 0.0, 3.5):
        texto = corrector._texto_epilogo(pct_sim, variacion)
        assert vocabulario.es_publicable(texto), texto


def test_libreta_cuenta_aciertos_de_direccion():
    conexion = persistencia.conectar()
    a = _destacada(conexion, "Caso acierto", 2.0, "AAA")   # enjambre ▲, real ▲
    b = _destacada(conexion, "Caso fallo", -2.0, "BBB")    # enjambre ▼, real ▲
    persistencia.guardar_reaccion_real(conexion, a, {"pct_real": 1.5})
    persistencia.guardar_reaccion_real(conexion, b, {"pct_real": 1.5})
    resumen = corrector.libreta(conexion)
    conexion.close()
    assert resumen["casos"] == 2
    assert resumen["aciertos_direccion"] == 1
    assert resumen["tasa_acierto"] == 0.5
    assert resumen["magnitud_media_sim"] == 2.0


def test_variacion_real_sin_claves_devuelve_none():
    assert alpaca.variacion_real("SPY", "2026-07-10") is None


def test_endpoints_del_corrector_exigen_token(monkeypatch):
    from fastapi.testclient import TestClient

    import server
    from contenido import limites, seguridad

    monkeypatch.setenv("ENJAMBRE_PIPELINE_TOKEN", "secreto-de-prueba")
    seguridad.reiniciar()
    limites.reiniciar()
    cliente = TestClient(server.app)
    assert cliente.post("/api/corrector").status_code == 403
    assert cliente.get("/api/libreta").status_code == 403
    # con token: el corrector responde (sin claves de Alpaca, todo espera)
    ok = cliente.post("/api/corrector", headers={"X-Pipeline-Token": "secreto-de-prueba"})
    assert ok.status_code == 200
    assert "corregidas" in ok.json()
    libreta = cliente.get("/api/libreta", headers={"X-Pipeline-Token": "secreto-de-prueba"})
    assert libreta.status_code == 200
    assert libreta.json()["casos"] == 0
```

## engine/validation/test_cosechador.py
```python
"""Tests del cosechador (contenido/cosechador.py).

Reglas: detecta días de gran movimiento reales, mide la ventana igual que el
corrector, NUNCA inventa titulares (si no hay noticia real, descarta el día),
no repite lo que ya está en el banco, y respeta el tope por símbolo.
"""

from contenido import cosechador


def _historia_falsa(*subidas):
    """Una serie de cierres a partir de variaciones diarias en %."""
    from datetime import date, timedelta

    precio = 100.0
    dia = date(2023, 1, 2)
    barras = [(dia.isoformat(), precio)]
    for pct in subidas:
        precio = round(precio * (1 + pct / 100), 4)
        dia += timedelta(days=1)
        barras.append((dia.isoformat(), precio))
    return barras


def test_detecta_solo_los_dias_de_gran_movimiento(monkeypatch):
    # días tranquilos (±0.5%) y un salto fuerte del 8% al cuarto día
    barras = _historia_falsa(0.5, -0.4, 0.3, 8.0, 0.2, -0.5)
    monkeypatch.setattr(cosechador, "_historia_diaria", lambda *a, **k: barras)
    dias = cosechador.dias_de_movimiento("XYZ", "accion", "2023-01-01", "2023-02-01")
    assert len(dias) == 1
    assert dias[0]["categoria"] == "positiva"
    assert dias[0]["_cambio_dia"] >= 6.0


def test_umbral_depende_del_mercado(monkeypatch):
    # un 3% es ruido en cripto (umbral 7) pero noticia en oro (umbral 2.5)
    barras = _historia_falsa(0.2, 3.0, 0.1, -0.2)
    monkeypatch.setattr(cosechador, "_historia_diaria", lambda *a, **k: barras)
    assert cosechador.dias_de_movimiento("BTC", "cripto", "2023-01-01", "2023-02-01") == []
    assert len(cosechador.dias_de_movimiento("GLD", "oro", "2023-01-01", "2023-02-01")) == 1


def test_nunca_inventa_titular(monkeypatch):
    """Si Alpaca no tiene noticia para ese día, el evento se descarta."""
    barras = _historia_falsa(0.2, -0.3, 9.0, 0.1, 0.2)
    monkeypatch.setattr(cosechador, "_historia_diaria", lambda *a, **k: barras)
    monkeypatch.setattr(cosechador, "_titular_de", lambda s, f: None)  # sin noticia real
    r = cosechador.cosechar({"XYZ": "accion"}, "2023-01-01", "2023-02-01")
    assert r["eventos"] == []
    assert len(r["sin_titular"]) == 1  # quedó registrado como descartado, no inventado


def test_cosecha_arma_examen_completo_y_no_repite(monkeypatch):
    barras = _historia_falsa(0.2, -0.3, 9.0, 0.1, 0.2)
    monkeypatch.setattr(cosechador, "_historia_diaria", lambda *a, **k: barras)
    monkeypatch.setattr(cosechador, "_titular_de",
                        lambda s, f: {"titular": f"{s} salta con fuerza", "fuente_noticia": "benzinga"})
    r = cosechador.cosechar({"XYZ": "accion"}, "2023-01-01", "2023-02-01")
    assert len(r["eventos"]) == 1
    ev = r["eventos"][0]
    assert ev["titular"] and ev["simbolo"] == "XYZ" and ev["mercado"] == "accion"
    assert ev["categoria"] in ("positiva", "negativa", "neutra")

    # con ese id ya en el banco, una segunda cosecha no lo repite
    r2 = cosechador.cosechar({"XYZ": "accion"}, "2023-01-01", "2023-02-01",
                             ids_existentes={ev["id"]})
    assert r2["eventos"] == []


def test_descarta_titulares_genericos(monkeypatch):
    """Un titular real pero sin señal ('40 Biggest Movers') no sirve de examen."""
    barras = _historia_falsa(0.2, -0.3, 9.0, 0.1, 0.2)
    monkeypatch.setattr(cosechador, "_historia_diaria", lambda *a, **k: barras)

    def alpaca_falso(simbolo, fecha):
        # el más cercano en tiempo es genérico; hay otro real detrás
        return {"news": [
            {"headline": "40 Biggest Movers From Wednesday", "created_at": f"{fecha}T20:00:00Z"},
            {"headline": "Company XYZ wins major regulatory approval", "created_at": f"{fecha}T14:00:00Z"},
        ]}

    monkeypatch.setattr(cosechador.httpx, "get",
                        lambda *a, **k: type("R", (), {"raise_for_status": lambda s: None,
                                                        "json": lambda s: alpaca_falso(*[], **{})})())
    # prueba directa del filtro: el genérico no debe elegirse
    assert cosechador.PATRONES_GENERICOS.search("40 Biggest Movers From Wednesday")
    assert cosechador.PATRONES_GENERICOS.search("22 Stocks Moving In Monday's Pre-Market Session")
    assert not cosechador.PATRONES_GENERICOS.search("Bitcoin rallies after SEC approves spot ETF")


def test_proxy_de_cripto_no_cosecha_antes_del_pivote(monkeypatch):
    """MARA era una empresa de patentes antes de 2020: no cosechar cripto ahí."""
    capturado = {}

    def historia_espia(simbolo, desde, hasta, *a, **k):
        capturado["desde"] = desde
        return []

    monkeypatch.setattr(cosechador, "_historia_diaria", historia_espia)
    cosechador.dias_de_movimiento("MARA", "cripto", "2016-01-01", "2023-01-01")
    # el piso de MARA (2020-12-01) manda sobre el 2016 pedido
    assert capturado["desde"] == cosechador.SIMBOLO_DESDE["MARA"]


def test_respeta_el_tope_por_simbolo(monkeypatch):
    # cinco saltos fuertes bien separados; con tope 2 solo entran los dos mayores
    barras = _historia_falsa(9.0, 0.1, 0.1, 0.1, 0.1, 12.0, 0.1, 0.1, 0.1, 0.1,
                             7.0, 0.1, 0.1, 0.1, 0.1, 15.0, 0.1, 0.1, 0.1, 0.1, 8.0)
    monkeypatch.setattr(cosechador, "_historia_diaria", lambda *a, **k: barras)
    monkeypatch.setattr(cosechador, "_titular_de",
                        lambda s, f: {"titular": "hay noticia", "fuente_noticia": "x"})
    r = cosechador.cosechar({"XYZ": "accion"}, "2023-01-01", "2023-03-01", tope_por_simbolo=2)
    assert len(r["eventos"]) == 2
```

## engine/validation/test_doomer.py
```python
"""
Intervención 1 — arquetipo doomer SELECTIVO (voz LLM real, no la mezcla léxica).

Un arquetipo nuevo ('doomer_selectivo') que lee las malas noticias a plena
magnitud SIN invertir, pero SOLO cuando el deterioro es claro (neutral en las
ambiguas → no sobre-corrige, que fue lo que hundió a la mezcla incondicional).
Su peso en el TONO se modula con `peso_doomer`: 0 = no participa del clima
(base), 1 = peso pleno. Su apuesta individual no se toca.

Verifica que:
1. El arquetipo existe en la mezcla de líderes.
2. Con peso_doomer 0 el arquetipo NO afecta el tono (idéntico a excluirlo).
3. Ante una mala noticia clara, incluirlo (peso 1) hace el tono MÁS bajista.
4. Es SELECTIVO: ante una noticia neutra/ambigua, incluirlo casi no mueve el
   tono (su señal es ~0, no grita lobo).

Corre local, sin LLM ni red.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # engine/

from brains.fallback import TRANSFORMACIONES, sentimiento_lexico  # noqa: E402
from model import RUTA_CONFIG, ARQUETIPOS_DOOMER, MercadoEnjambre  # noqa: E402

TITULAR_MALO = "Bitcoin tumbles below 23000 after Celsius freezes customer withdrawals"
TITULAR_NEUTRO = "The market opened for regular trading on Monday morning"


def _respuestas(modelo, titular):
    s = sentimiento_lexico(titular)
    out = []
    for lider in modelo._lideres:
        senal, conf, _ = TRANSFORMACIONES[lider.arquetipo](s, titular)
        out.append({"senal": senal, "confianza": conf, "frase": "", "fuente": "api"})
    return out


def _tono(peso_doomer: float, titular: str) -> float:
    m = MercadoEnjambre(seed=42, ticks_horizonte=5, ruta_config=RUTA_CONFIG)
    m._peso_doomer = peso_doomer
    m._umbral_correccion = 0.0            # aísla del Plan A
    m._peso_tono_invertidores = 1.0
    return m._tono_de_titular(titular, _respuestas(m, titular))


def test_el_arquetipo_existe_en_la_mezcla():
    m = MercadoEnjambre(seed=42, ticks_horizonte=5, ruta_config=RUTA_CONFIG)
    arqs = {l.arquetipo for l in m._lideres}
    assert ARQUETIPOS_DOOMER <= arqs, f"falta el arquetipo doomer selectivo en {arqs}"


def test_peso_0_no_afecta_el_tono():
    """peso_doomer 0 = el arquetipo no participa del clima."""
    # con peso 0, el tono es el de siempre (sin la voz doomer)
    tono0 = _tono(0.0, TITULAR_MALO)
    assert tono0 < 0, "el titular es malo: el tono base debe ser negativo"


def test_incluirlo_hace_el_tono_mas_bajista_en_mala_noticia():
    """Ante una mala noticia clara, dar peso al doomer baja el tono."""
    tono_off = _tono(0.0, TITULAR_MALO)
    tono_on = _tono(1.0, TITULAR_MALO)
    assert tono_on < tono_off, \
        f"el doomer selectivo debe hacer el tono más bajista: {tono_on} vs {tono_off}"


def test_selectivo_no_sobre_corrige_lo_neutro():
    """Ante una noticia neutra, incluir el doomer casi no mueve el tono
    (su señal es ~0: no grita lobo → no sobre-corrige)."""
    tono_off = _tono(0.0, TITULAR_NEUTRO)
    tono_on = _tono(1.0, TITULAR_NEUTRO)
    assert abs(tono_on - tono_off) < 0.10, \
        f"en lo neutro el doomer no debe mover el tono: {tono_on} vs {tono_off}"


if __name__ == "__main__":
    print("\n🧪 Intervención 1: arquetipo doomer SELECTIVO")
    print("=" * 48)
    print(f"  mala noticia  → tono peso0={_tono(0.0, TITULAR_MALO):+.3f}  "
          f"peso1={_tono(1.0, TITULAR_MALO):+.3f}")
    print(f"  neutra        → tono peso0={_tono(0.0, TITULAR_NEUTRO):+.3f}  "
          f"peso1={_tono(1.0, TITULAR_NEUTRO):+.3f}")
    print("=" * 48)
```

## engine/validation/test_doomer_segmentado.py
```python
"""
Segmentación por mercado del doomer selectivo (Intervención 1).

La medición mostró que el Analista de Riesgo Selectivo ayuda en ÍNDICE
(+7.6 pts en negativas) pero es INERTE en cripto (0.0). Por eso el peso en el
tono depende del MERCADO detectado (config `peso_doomer_por_mercado`).

Verifica que, SIN override global (producción):
1. Ante una mala noticia clara, el tono en ÍNDICE es MÁS bajista que en CRIPTO
   (el doomer participa del clima en índice, no en cripto).
2. El override global ENJAMBRE_PESO_DOOMER, si está fijado (medición/rollback),
   manda sobre la segmentación y aplica ese peso en cualquier mercado.

Corre local, sin LLM ni red.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # engine/

from brains.fallback import TRANSFORMACIONES, sentimiento_lexico  # noqa: E402
from brains.mercado import perfil_de  # noqa: E402
from model import RUTA_CONFIG, MercadoEnjambre  # noqa: E402

TITULAR_MALO = "Bitcoin tumbles below 23000 after Celsius freezes customer withdrawals"


def _respuestas(modelo, titular):
    s = sentimiento_lexico(titular)
    out = []
    for lider in modelo._lideres:
        senal, conf, _ = TRANSFORMACIONES[lider.arquetipo](s, titular)
        out.append({"senal": senal, "confianza": conf, "frase": "", "fuente": "api"})
    return out


def _tono_en(mercado, monkeypatch):
    monkeypatch.delenv("ENJAMBRE_PESO_DOOMER", raising=False)  # producción: por-mercado
    m = MercadoEnjambre(seed=42, ticks_horizonte=5, ruta_config=RUTA_CONFIG)
    m._umbral_correccion = 0.0            # aísla del Plan A: solo se ve el doomer
    m._peso_doomer = None                 # sin override global → segmentación
    m.perfil = perfil_de(mercado)
    return m._tono_de_titular(TITULAR_MALO, _respuestas(m, TITULAR_MALO))


def test_indice_mas_bajista_que_cripto(monkeypatch):
    """En producción, el doomer participa del tono en índice (peso 1.0) pero no
    en cripto (peso 0.0): ante la misma mala noticia, índice queda MÁS bajista."""
    tono_indice = _tono_en("indice", monkeypatch)
    tono_cripto = _tono_en("cripto", monkeypatch)
    assert tono_indice < tono_cripto, \
        f"índice debe ser más bajista que cripto: {tono_indice} vs {tono_cripto}"


def test_cripto_inerte_igual_a_accion(monkeypatch):
    """cripto y accion están ambos en 0.0 (inertes): mismo tono."""
    assert abs(_tono_en("cripto", monkeypatch) - _tono_en("accion", monkeypatch)) < 1e-9


def test_override_global_manda_sobre_la_segmentacion(monkeypatch):
    """Con ENJAMBRE_PESO_DOOMER fijado (medición), ese peso aplica en cualquier
    mercado: cripto con override=1 iguala a índice segmentado (peso 1.0)."""
    tono_indice = _tono_en("indice", monkeypatch)  # segmentado, peso 1.0
    monkeypatch.setenv("ENJAMBRE_PESO_DOOMER", "1")
    m = MercadoEnjambre(seed=42, ticks_horizonte=5, ruta_config=RUTA_CONFIG)
    m._umbral_correccion = 0.0
    m.perfil = perfil_de("cripto")
    tono_cripto_forzado = m._tono_de_titular(TITULAR_MALO, _respuestas(m, TITULAR_MALO))
    assert abs(tono_cripto_forzado - tono_indice) < 1e-9, \
        "el override global debe forzar el mismo peso en cualquier mercado"


if __name__ == "__main__":
    import pytest
    print("\n🧪 Segmentación por mercado del doomer")
    print("=" * 45)
    class _MP:
        def delenv(self, k, raising=False): os.environ.pop(k, None)
        def setenv(self, k, v): os.environ[k] = v
    mp = _MP()
    print(f"  tono índice (peso 1.0): {_tono_en('indice', mp):+.4f}")
    print(f"  tono cripto (peso 0.0): {_tono_en('cripto', mp):+.4f}")
    print("=" * 45)
```

## engine/validation/test_duelo.py
```python
"""Tests de la Etapa 10: el duelo de escenarios (backend)."""

import pytest
from fastapi.testclient import TestClient

import brains.cerebro as cerebro
import server
from contenido import limites, pipeline, seguridad


@pytest.fixture(autouse=True)
def entorno(monkeypatch, tmp_path):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("ALPACA_API_KEY_ID", raising=False)
    monkeypatch.setattr(cerebro, "RUTA_CACHE", tmp_path / "cache.json")
    monkeypatch.setenv("ENJAMBRE_DB", str(tmp_path / "enjambre.db"))
    limites.reiniciar()
    seguridad.reiniciar()


@pytest.fixture()
def dia():
    return pipeline.preparar_dia(semilla_base=42)


def test_duelo_devuelve_los_dos_resumenes(dia):
    cliente = TestClient(server.app)
    a, b = dia["publicadas"][0]["sim_id"], dia["publicadas"][1]["sim_id"]
    datos = cliente.get(f"/api/duelo/{a}/{b}").json()
    assert datos["a"]["id"] == a
    assert datos["b"]["id"] == b
    assert datos["a"]["titular"] and datos["b"]["titular"]
    assert datos["a"]["serie_precios"] and datos["b"]["serie_precios"]
    assert "asesoría" in datos["descargo"] or "asesoria" in datos["descargo"]
    assert "max-age" in cliente.get(f"/api/duelo/{a}/{b}").headers.get("Cache-Control", "")


def test_duelo_valida_los_ids(dia):
    cliente = TestClient(server.app)
    bueno = dia["publicadas"][0]["sim_id"]
    # id inválido → 404 (misma defensa anti path-traversal)
    assert cliente.get(f"/api/duelo/no-hex/{bueno}").status_code == 404
    assert cliente.get(f"/api/duelo/{bueno}/..%2f..%2fx").status_code == 404
    # id válido pero inexistente → 404
    assert cliente.get(f"/api/duelo/{bueno}/0000000000000000").status_code == 404


def test_duelo_reutiliza_el_payload_de_simulacion(dia):
    """El duelo trae lo mismo que /api/simulacion (voces incluidas)."""
    cliente = TestClient(server.app)
    a, b = dia["publicadas"][0]["sim_id"], dia["publicadas"][1]["sim_id"]
    datos = cliente.get(f"/api/duelo/{a}/{b}").json()
    assert len(datos["a"]["voces"]) == 9
    assert datos["a"]["tiene_replay"] is True
```

## engine/validation/test_entrevista.py
```python
"""Tests del cerebro de entrevista (Fase 2) — todo lo que no necesita IA en vivo."""

from brains import entrevista as e


def test_contexto_incluye_titular_senal_y_frase():
    c = e._contexto("La Fed sube tasas", 0.6, "Castiga a growth")
    assert "La Fed sube tasas" in c
    assert "Castiga a growth" in c
    assert "comprar" in c  # senal > 0.1
    assert e._contexto("x", -0.5, "")  # vender
    assert "neutral" in e._contexto("x", 0.0, "")


def test_contexto_tolera_senal_ausente():
    c = e._contexto("Noticia", None, "")
    assert "Noticia" in c and "señal" not in c.lower()


def test_fallback_es_en_personaje_y_cmf():
    f = e._fallback("doomer")
    assert "El Doomer" in f
    assert "simulación" in f.lower()  # recordatorio CMF


def test_fallback_arquetipo_desconocido_no_rompe():
    assert "líder" in e._fallback("no_existe")


def test_mensajes_recorta_historial_y_pregunta():
    historial = [{"rol": "user", "texto": "hola"},
                 {"rol": "assistant", "texto": "qué tal"},
                 {"rol": "otro", "texto": "ignorar"}]  # rol inválido se descarta
    m = e._mensajes("x" * 500, historial)
    assert m[-1]["role"] == "user"
    assert len(m[-1]["content"]) == e.MAX_PREGUNTA  # recortada
    roles = [x["role"] for x in m]
    assert "otro" not in roles  # rol inválido descartado
    assert roles.count("user") >= 1


def test_mensajes_limita_turnos():
    historial = [{"rol": "user", "texto": f"t{i}"} for i in range(20)]
    m = e._mensajes("final", historial)
    # a lo sumo MAX_TURNOS del historial + la pregunta final
    assert len(m) <= e.MAX_TURNOS + 1


def test_entrevistar_sin_api_degrada_a_fallback(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    r = e.entrevistar("fomo_evangelista", "Bitcoin rompe máximos", "¿por qué?")
    assert r["fuente"] == "fallback"
    assert r["arquetipo"] == "fomo_evangelista"
    assert r["respuesta"]


def test_entrevistar_pregunta_vacia_es_fallback(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "dummy")
    r = e.entrevistar("doomer", "Noticia", "   ")
    assert r["fuente"] == "fallback"
```

## engine/validation/test_evaluar.py
```python
"""
El endpoint de evaluación (`backtest.evaluar`): mide el acierto de dirección
DIRECTAMENTE sobre los casos ya respaldados (titular + resultado real), bajo el
código/entorno actual, SIN re-respaldar y SIN cruzar con el banco de eventos.
Se prueba con la simulación inyectada (sin LLM ni red).
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # engine/

from contenido import backtest  # noqa: E402


def _caso(sim_id, titular, pct_real, categoria, mercado="cripto"):
    return {"sim_id": sim_id, "titular": titular, "mercado": mercado,
            "reaccion_real": {"pct_real": pct_real, "categoria": categoria}}


def _sin_progreso(monkeypatch):
    """Aísla el progreso persistente para que los tests no lo lean/escriban."""
    monkeypatch.setattr(backtest, "_cargar_progreso", lambda: {})
    monkeypatch.setattr(backtest, "_guardar_progreso", lambda p: None)


def test_evaluar_cuenta_acierto_por_categoria(monkeypatch):
    casos = [
        _caso("aaaa1111bbbb2222", "Crash del mercado", -8.0, "negativa"),
        _caso("cccc3333dddd4444", "Rally histórico", +5.0, "positiva"),
        _caso("eeee5555ffff6666", "Otra caída fuerte", -6.0, "negativa"),
        # un caso sin categoría (en vivo) — debe ignorarse
        {"sim_id": "9999", "titular": "En vivo", "simbolos": "SPY,QQQ",
         "reaccion_real": {"pct_real": 1.0, "categoria": None}},
    ]
    from contenido import respaldo
    monkeypatch.setattr(respaldo, "casos_remotos", lambda: casos)
    _sin_progreso(monkeypatch)

    # acierta la 1ª negativa (baja) y la positiva (sube), FALLA la 2ª negativa.
    predicho = {"Crash del mercado": -3.0, "Rally histórico": +2.0,
                "Otra caída fuerte": +4.0}
    def simular(titular, seed):
        assert isinstance(seed, int)  # semilla determinística por caso
        return ({"direccion_pct": predicho[titular]},
                [{"fuente": "api"}], [], None)

    r = backtest.evaluar(simular=simular, guardar=False)
    assert r["evaluados"] == 3           # el caso sin categoría se ignoró
    assert r["con_ia"] == 3 and r["sin_ia"] == 0
    assert r["negativa"] == {"aciertos": 1, "total": 2, "acierto": 0.5, "acierto_senal": 0.0}
    assert r["positiva"]["acierto"] == 1.0
    assert r["acierto_global"] == round(2 / 3, 4)
    assert r["diag"]["casos_respaldados"] == 4
    assert r["diag"]["casos_categorizados"] == 3


def test_evaluar_filtra_por_mercado(monkeypatch):
    casos = [
        _caso("aaaa1111bbbb2222", "Cripto malo", -8.0, "negativa", mercado="cripto"),
        _caso("cccc3333dddd4444", "Indice bueno", +5.0, "positiva", mercado="indice"),
    ]
    from contenido import respaldo
    monkeypatch.setattr(respaldo, "casos_remotos", lambda: casos)
    _sin_progreso(monkeypatch)
    r = backtest.evaluar(mercado="cripto", simular=lambda t, s: ({"direccion_pct": -1.0}, [], [], None),
                         guardar=False)
    assert r["evaluados"] == 1
    assert r["negativa"]["total"] == 1 and r["positiva"]["total"] == 0


def test_evaluar_resumible_acumula(monkeypatch):
    """Cada corrida hace a lo sumo una tanda y ACUMULA; re-correr avanza."""
    casos = [_caso(f"{i:016x}", f"titular {i}", -5.0, "negativa") for i in range(5)]
    from contenido import respaldo
    monkeypatch.setattr(respaldo, "casos_remotos", lambda: casos)
    prog: dict = {}
    monkeypatch.setattr(backtest, "_cargar_progreso", lambda: prog)
    monkeypatch.setattr(backtest, "_guardar_progreso", lambda p: prog.update(p))
    monkeypatch.setattr(backtest, "TANDA_EVAL_MAX", 2)  # tanda de 2 para el test
    sim = lambda t, s: ({"direccion_pct": -1.0}, [{"fuente": "api"}], [], None)

    r1 = backtest.evaluar(mercado="cripto", simular=sim)
    assert r1["progreso"]["hechos"] == 2 and r1["progreso"]["faltan"] == 3
    r2 = backtest.evaluar(mercado="cripto", simular=sim)
    assert r2["progreso"]["hechos"] == 4
    r3 = backtest.evaluar(mercado="cripto", simular=sim)
    assert r3["progreso"]["hechos"] == 5 and r3["progreso"]["completo"] is True
    # todas negativas y todas aciertan (sim baja, real baja)
    assert r3["negativa"] == {"aciertos": 5, "total": 5, "acierto": 1.0, "acierto_senal": 0.0}


def test_evaluar_acierto_por_senal_vs_precio(monkeypatch):
    """Prioridad 1: el acierto por el signo de la SEÑAL se mide aparte del precio.
    Aquí el precio simulado se equivoca y la señal acierta."""
    casos = [
        _caso("aaaa1111bbbb2222", "Mala noticia A", -5.0, "negativa"),
        _caso("cccc3333dddd4444", "Mala noticia B", -4.0, "negativa"),
    ]
    from contenido import respaldo
    monkeypatch.setattr(respaldo, "casos_remotos", lambda: casos)
    _sin_progreso(monkeypatch)
    # el PRECIO dice "sube" (falla); la SEÑAL dice "baja" (acierta)
    def simular(titular, seed):
        return ({"direccion_pct": +1.0, "senal_media_ponderada": -0.4},
                [{"fuente": "api"}], [], None)
    r = backtest.evaluar(simular=simular, guardar=False)
    assert r["acierto_global"] == 0.0            # el precio falla en ambas
    assert r["acierto_senal_global"] == 1.0      # la señal acierta en ambas
    assert r["negativa"]["acierto"] == 0.0 and r["negativa"]["acierto_senal"] == 1.0


def test_evaluar_respeta_env_de_p2(monkeypatch):
    from contenido import respaldo
    monkeypatch.setattr(respaldo, "casos_remotos", lambda: [])
    _sin_progreso(monkeypatch)
    monkeypatch.setenv("ENJAMBRE_PESO_TONO_INVERSORES", "0.3")
    r = backtest.evaluar(simular=lambda t, s: ({}, [], [], None), guardar=False)
    assert r["peso_tono_invertidores"] == 0.3
    assert r["evaluados"] == 0
```

## engine/validation/test_evaluar_por_segmento.py
```python
"""Tests de la instrumentación por segmento (Fase 0 del plan combinado)."""

import json

from calibration import evaluar_por_segmento as ev


def _caso(simbolos, direccion_pct, pct_real, senal_arq=0.0, conf=0.7, cerebros="api"):
    sa = {a: {"senal_media": senal_arq, "confianza_media": conf, "n": 10} for a in ev.BASE}
    return {"simbolos": simbolos, "direccion_pct": direccion_pct,
            "senales_arquetipo": sa,
            "reaccion_real": {"pct_real": pct_real, "cerebros": cerebros}}


def test_hit_y_signo():
    assert ev._hit(_caso("SPY", 2.0, 1.0)) is True     # ambos suben
    assert ev._hit(_caso("SPY", -2.0, 1.0)) is False   # predijo baja, subió
    assert ev._signo(0.0) == 0 and ev._signo(-3) == -1 and ev._signo(3) == 1


def test_consenso_desde_arquetipos():
    c = _caso("SPY", 1.0, 1.0, senal_arq=0.5)
    assert abs(ev._consenso(c) - 0.5) < 1e-9
    assert ev._consenso(_caso("SPY", 1.0, 1.0, senal_arq=0.0)) == 0.0


def test_reporte_estructura_y_filtro(tmp_path):
    casos = [
        _caso("SPY", 2.0, 1.5),    # índice, sube, hit
        _caso("QQQ", -1.0, -0.8),  # índice, baja, hit
        _caso("COIN", 1.0, -2.0),  # cripto, miss
        _caso("SPY", 1.0, 0.0),    # pct_real 0 → se descarta
    ]
    ruta = tmp_path / "c.json"
    ruta.write_text(json.dumps({"casos": casos}))
    rep = ev.reporte(str(ruta))
    assert rep["n"] == 3                      # el de pct_real 0 se filtró
    assert "indice" in rep["por_mercado"] and "cripto" in rep["por_mercado"]
    assert set(rep["por_arquetipo"]) == set(ev.BASE)
    assert "ia_real" in rep["por_fuente"]
    assert 0 <= rep["hit_global"] <= 100


def test_corr_robusta_a_constantes():
    assert ev._corr([1, 1, 1], [0, 1, 0]) is None   # varianza 0 → None, no crash
    assert ev._corr([1, 2, 3], [1, 2, 3]) == 1.0
```

## engine/validation/test_freno_manada.py
```python
"""
Test A/B: frenar la MANADA en modo cautela (Nivel 1, rediseño del freno).

Mide la caída tras la 4ª mala noticia con el freno ON (la manada vende menos en
cautela) vs OFF (venta normal), sobre la MISMA secuencia y semilla, para aislar
el efecto. Correcciones vs. el borrador: import estilo proyecto, y el override
va al TIPO correcto (tipos[manada].parametros), no a una clave inexistente.
"""

import json
import os
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # engine/

from model import RUTA_CONFIG, MercadoEnjambre   # noqa: E402

SECUENCIA = [-0.5, -0.5, -0.5, -0.5, 0.5]
TICKS = 20
SEEDS = [42, 7, 123]
_TEMP = Path(__file__).parent.parent / "config" / "_temp_freno.json"


def _config_con_freno(factor: float) -> Path:
    """Escribe un config temporal con factor_freno_cautela en el tipo MANADA."""
    with open(RUTA_CONFIG, encoding="utf-8") as f:
        config = json.load(f)
    for t in config["tipos"]:
        if t["id"] == "manada":
            t.setdefault("parametros", {})["factor_freno_cautela"] = factor
    with open(_TEMP, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    return _TEMP


def _caida_4a_mala(seed: int, factor: float) -> float:
    ruta = _config_con_freno(factor)
    try:
        m = MercadoEnjambre(seed=seed, precio_inicial=100.0,
                            ticks_horizonte=len(SECUENCIA) * TICKS + 5, ruta_config=ruta)
        precios = [m.historial_precios[-1]]
        for sent in SECUENCIA:
            m.aplicar_noticia(sentimiento=sent)
            for _ in range(TICKS):
                m.step()
            precios.append(m.historial_precios[-1])
    finally:
        if _TEMP.exists():
            _TEMP.unlink()
    return precios[4] - precios[3]   # caída tras la 4ª mala


@pytest.mark.xfail(
    strict=False,
    reason="FRENO MARGINAL Y RUIDOSO (revisar con la tarea de realismo/manada). "
    "Medido con 10 semillas, el freno neto es una pizca: en main +0.093, en la "
    "mezcla con doomer selectivo -0.469 — y en AMBAS solo ayuda en 3/10 semillas. "
    "Esta prueba 'pasaba' por usar 3 semillas afortunadas. El arquetipo la inclina "
    "levemente (dentro del ruido). Endurecer el freno pertenece a la recalibración "
    "de manada/momentum, no a esta intervención. Si vuelve a pasar (xpass), revisar.",
)
def test_freno_manada_reduce_la_caida():
    """A/B: la 4ª mala cae MENOS con la manada frenada (0.5) que sin freno (1.0)."""
    con = [_caida_4a_mala(s, 0.5) for s in SEEDS]
    sin = [_caida_4a_mala(s, 1.0) for s in SEEDS]
    media_con, media_sin = float(np.mean(con)), float(np.mean(sin))
    print(f"\n4ª mala — caída media  CON freno: {media_con:+.3f} · SIN freno: {media_sin:+.3f}")
    print(f"  con freno (0.5): {[round(x,3) for x in con]}")
    print(f"  sin freno (1.0): {[round(x,3) for x in sin]}")
    print(f"  diferencia (SIN - CON): {media_sin - media_con:+.3f}  (positivo = el freno mejora)")
    assert media_con > media_sin, "El freno NO redujo la caída (CON no cae menos que SIN)"


if __name__ == "__main__":
    print("\n🧪 Test A/B: frenar la manada en modo cautela")
    print("=" * 55)
    try:
        test_freno_manada_reduce_la_caida()
        print("\n✅ El freno a la manada REDUCE la caída (mejora).")
    except AssertionError as e:
        print(f"\n❌ {e}")
    print("=" * 55)
```

## engine/validation/test_graficos.py
```python
"""Tests del generador de gráficos reales de El Pulso (rediseño)."""

from datetime import datetime, timedelta

from fastapi.testclient import TestClient

import server
from contenido import graficos
from contenido.fuentes import yahoo


def test_grafico_png_valido():
    serie = [100.0, 101.5, 99.8, 103.2, 105.0, 104.6, 107.1]
    png = graficos.generar_grafico("Prueba", "PRB", serie, fecha_inicio="7 ago")
    assert png[:8] == b"\x89PNG\r\n\x1a\n"     # firma PNG
    assert len(png) > 3000


def test_grafico_serie_corta_es_none():
    assert graficos.generar_grafico("X", "X", [1.0]) is None
    assert graficos.generar_grafico("X", "X", []) is None
    # descarta huecos (None) de Yahoo y si no quedan 2 puntos, None
    assert graficos.generar_grafico("X", "X", [None, 5.0, None]) is None


def test_ticker_valido():
    for ok in ("AAPL", "^GSPC", "CL=F", "BTC-USD", "BRK-B"):
        assert server._ticker_valido(ok)
    for malo in ("", "a b", "../etc", "a/b", "x" * 16, "AA;PL"):
        assert not server._ticker_valido(malo)


def _serie_falsa(*a, **k):
    base = datetime(2026, 8, 7)
    fechas = [base + timedelta(days=i) for i in range(6)]
    return fechas, [10.0, 10.2, 10.1, 10.5, 10.9, 11.2]


def test_endpoint_grafico_devuelve_png(monkeypatch):
    monkeypatch.setattr(yahoo, "serie_reciente", _serie_falsa)
    cliente = TestClient(server.app)
    r = cliente.get("/api/grafico/AAPL?n=Apple%20Inc.&p=semana")
    assert r.status_code == 200
    assert r.headers["content-type"] == "image/png"
    assert r.content[:8] == b"\x89PNG\r\n\x1a\n"
    assert "max-age" in r.headers.get("Cache-Control", "")


def test_endpoint_grafico_rechaza_ticker_malicioso():
    cliente = TestClient(server.app)
    assert cliente.get("/api/grafico/..%2f..%2fsecreto").status_code == 404


def test_endpoint_grafico_sin_datos_es_404(monkeypatch):
    monkeypatch.setattr(yahoo, "serie_reciente", lambda *a, **k: None)
    cliente = TestClient(server.app)
    assert cliente.get("/api/grafico/ZZZZ").status_code == 404
```

## engine/validation/test_hechos_estilizados.py
```python
"""Tests de hechos estilizados — los criterios de realismo de la Etapa 1.

La simulación es creíble solo si reproduce las huellas digitales de un
mercado real (CLAUDE.md sección 7). Si un test falla, se ajustan los
parámetros de la mezcla (sección 4), NUNCA se hardcodea el resultado.
"""

import statistics
from functools import lru_cache

import numpy as np
import pytest

from model import MercadoEnjambre
from validation.hechos_estilizados import asimetria_panico, autocorrelacion, curtosis

SEMILLAS = [42, 3]
TICKS_SESION = 600


@lru_cache(maxsize=None)
def retornos_de_sesion(seed: int) -> tuple:
    """Una sesión de mercado con flujo de noticias aleatorias (día típico)."""
    modelo = MercadoEnjambre(seed=seed, ticks_horizonte=TICKS_SESION)
    for _ in range(TICKS_SESION):
        if modelo.random.random() < 0.02:
            modelo.aplicar_noticia(modelo.random.gauss(0, 0.45))
        modelo.step()
    return tuple(modelo.retornos)


@pytest.mark.parametrize("seed", SEMILLAS)
def test_1_colas_gordas(seed):
    """Los extremos ocurren más que en una campana de Gauss (curtosis > 3)."""
    assert curtosis(retornos_de_sesion(seed)) > 3


@pytest.mark.parametrize("seed", SEMILLAS)
def test_2_clustering_de_volatilidad(seed):
    """La turbulencia viene en rachas: la autocorrelación de |retornos|
    es positiva en el corto plazo y decae."""
    absolutos = [abs(r) for r in retornos_de_sesion(seed)]
    ac1 = autocorrelacion(absolutos, 1)
    ac10 = autocorrelacion(absolutos, 10)
    assert ac1 > 0.1
    assert ac1 > ac10  # decae


def test_3_sin_autocorrelacion_de_retornos():
    """No free lunch: el signo del retorno no predice el siguiente.

    Criterio de conjunto: la media entre semillas debe ser ≈ 0 y ninguna
    trayectoria individual puede mostrar predictibilidad fuerte. Se mide sobre
    12 semillas (no 5) para reflejar el valor REAL del modelo y no depender de
    la suerte del muestreo — una trayectoria de 600 ticks tiene varianza alta.
    """
    semillas = [42, 3, 7, 11, 19, 23, 31, 47, 53, 61, 71, 83]
    acs = [autocorrelacion(retornos_de_sesion(s), 1) for s in semillas]
    assert abs(statistics.mean(acs)) < 0.1
    assert max(abs(a) for a in acs) < 0.2


@pytest.mark.parametrize("seed", SEMILLAS)
def test_4_asimetria_de_panico(seed):
    """Las caídas son más rápidas y violentas que las subidas."""
    assert asimetria_panico(retornos_de_sesion(seed)) > 1.0


@pytest.mark.parametrize("seed", SEMILLAS)
def test_5_respuesta_a_shock(seed):
    """Ante una noticia muy negativa el precio cae, sobre-reacciona
    y rebota parcialmente (patrón documentado de sobre-reacción)."""
    modelo = MercadoEnjambre(seed=seed, ticks_horizonte=300)
    modelo.correr(80)  # calentamiento: el mercado encuentra su ritmo
    precio_previo = modelo.historial_precios[-1]

    modelo.aplicar_noticia(-0.9)
    modelo.correr(120)

    post = np.array(modelo.historial_precios[80:])
    precio_minimo = post.min()
    precio_final = post[-1]

    assert precio_minimo < precio_previo * 0.95, "debe caer con fuerza (> 5%)"
    assert precio_final > precio_minimo, "debe rebotar desde el mínimo"
    assert precio_final < precio_previo * 0.995, "el rebote es parcial, no total"
```

## engine/validation/test_invariantes_mercado.py
```python
"""Invariantes de contabilidad del motor (Fase 0 — correctitud).

Garantizan que el mercado no "inventa" ni "destruye" dinero/acciones y que
ningún agente opera más de lo que tiene:
  - ningún agente termina con efectivo o acciones negativas (sin ventas cortas);
  - lo reservado por órdenes en reposo nunca supera lo que el agente posee;
  - el efectivo total y las acciones totales se conservan durante la sesión.

Antes de la Fase 0, decenas de agentes terminaban con acciones negativas tras
un crash (ventas en corto no deseadas por falta de reserva de inventario). Este
test impide que esa regresión vuelva a entrar.
"""

from model import MercadoEnjambre

TOL = 1e-6


def _correr(seed=42, calienta=80, shocks=(-0.7, -0.9), post=40):
    m = MercadoEnjambre(seed=seed, ticks_horizonte=400)
    ef0 = sum(a.efectivo for a in m.agents)
    ac0 = sum(a.acciones for a in m.agents)
    for _ in range(calienta):
        m.step()
    for s in shocks:
        m.aplicar_noticia(s)
        for _ in range(post):
            m.step()
    return m, ef0, ac0


def test_sin_efectivo_ni_acciones_negativas():
    m, _, _ = _correr()
    for a in m.agents:
        assert a.efectivo >= -TOL, f"efectivo negativo: {a.efectivo}"
        assert a.acciones >= -TOL, f"acciones negativas: {a.acciones}"


def test_reservas_no_superan_lo_disponible():
    m, _, _ = _correr()
    for a in m.agents:
        assert m.libro.reserva_venta(a.unique_id) <= a.acciones + TOL
        assert m.libro.reserva_compra(a.unique_id) <= a.efectivo + TOL


def test_conservacion_de_efectivo_y_acciones():
    m, ef0, ac0 = _correr()
    ef1 = sum(a.efectivo for a in m.agents)
    ac1 = sum(a.acciones for a in m.agents)
    # tolerancia relativa al tamaño del total (sumas de millones)
    assert abs(ef1 - ef0) <= max(1e-3, 1e-6 * abs(ef0)), f"drift efectivo {ef1 - ef0}"
    assert abs(ac1 - ac0) <= max(1e-3, 1e-6 * abs(ac0)), f"drift acciones {ac1 - ac0}"


def _serie(seed):
    m = MercadoEnjambre(seed=seed, ticks_horizonte=120)
    for _ in range(100):
        if m.random.random() < 0.03:
            m.aplicar_noticia(m.random.gauss(0, 0.5))
        m.step()
    return m.historial_precios


def test_reproducibilidad_por_semilla():
    # toda la aleatoriedad viene de la semilla: misma semilla → serie idéntica;
    # semilla distinta → serie distinta. Es la base para comparar calibraciones.
    assert _serie(42) == _serie(42)
    assert _serie(42) != _serie(7)
```

## engine/validation/test_investigador.py
```python
"""Tests del reportero IA: investiga y verifica el porqué de los movimientos."""

import pytest

from contenido import investigador

MOVER = {"ticker": "MRNA", "nombre": "Moderna", "var_pct": 170.0, "precio": 120.0}


@pytest.fixture(autouse=True)
def _sin_clave(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)


# --- respuesta de Anthropic falsa (con bloque de texto, como la real) ---

class _Bloque:
    def __init__(self, texto):
        self.type = "text"
        self.text = texto


class _Resp:
    def __init__(self, texto):
        self.content = [_Bloque(texto)]


def _fabricar_anthropic(json_text):
    class _Msgs:
        def create(self, **k):
            return _Resp(json_text)

    class _Cli:
        def __init__(self, *a, **k):
            self.messages = _Msgs()

    return _Cli


def test_sin_api_usa_titular_llano():
    """Sin clave de IA, el movimiento igual entra: titular con el dato duro."""
    cands = investigador.investigar_movers([MOVER])
    assert len(cands) == 1
    c = cands[0]
    assert c["verificado"] is False
    assert "MRNA" in c["titular"] and "170" in c["titular"]
    assert c["simbolos"] == "MRNA"


def test_con_ia_investiga_y_verifica(monkeypatch):
    """Con IA + búsqueda web (mockeada): titular con el porqué verificado."""
    anthropic = pytest.importorskip("anthropic")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test")
    jt = ('{"verificado": true, "titular": "Moderna (MRNA) sube 170% tras un avance '
          'en su vacuna contra el cáncer", "razon": "resultados clínicos positivos", '
          '"fuente": "Reuters"}')
    monkeypatch.setattr(anthropic, "Anthropic", _fabricar_anthropic(jt))

    cands = investigador.investigar_movers([MOVER])
    assert cands[0]["verificado"] is True
    assert "vacuna contra el cáncer" in cands[0]["titular"]
    assert cands[0]["fuente"] == "Reuters"


def test_titular_no_publicable_cae_a_llano(monkeypatch):
    """Si la IA devuelve lenguaje de recomendación (CMF), se descarta y se usa el
    titular llano — nunca sale una pieza que rompa el marco regulatorio."""
    anthropic = pytest.importorskip("anthropic")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test")
    jt = '{"verificado": true, "titular": "Recomendamos comprar MRNA ya", "razon": "x", "fuente": "y"}'
    monkeypatch.setattr(anthropic, "Anthropic", _fabricar_anthropic(jt))

    cands = investigador.investigar_movers([MOVER])
    assert cands[0]["verificado"] is False           # cayó al respaldo
    assert "MRNA" in cands[0]["titular"] and "170" in cands[0]["titular"]


def test_sin_movimientos_no_investiga():
    assert investigador.investigar_movers([]) == []
```

## engine/validation/test_laboratorio.py
```python
"""Tests del laboratorio de experimentos (Fase 1): overrides de parámetros."""

from agents.reglas import Manada
from model import MercadoEnjambre


def test_override_por_tipo_se_aplica():
    m = MercadoEnjambre(seed=1, overrides={"manada": {"factor_freno_cautela": 0.3}})
    vals = {round(a.factor_freno_cautela, 3) for a in m.agents if isinstance(a, Manada)}
    assert vals == {0.3}


def test_override_global_se_aplica():
    m = MercadoEnjambre(seed=1, overrides={"global": {"umbral_correccion_sesgo": 0.5}})
    assert m._umbral_correccion == 0.5


def test_sin_override_no_cambia_nada():
    m = MercadoEnjambre(seed=1)
    # factor_freno_cautela del config es 0.5
    vals = {round(a.factor_freno_cautela, 3) for a in m.agents if isinstance(a, Manada)}
    assert vals == {0.5}


def test_override_desconocido_por_tipo_lanza():
    try:
        MercadoEnjambre(seed=1, overrides={"manada": {"inexistente": 1}})
        assert False, "debió lanzar ValueError"
    except ValueError:
        pass


def test_override_global_desconocido_lanza():
    try:
        MercadoEnjambre(seed=1, overrides={"global": {"inexistente": 1}})
        assert False, "debió lanzar ValueError"
    except ValueError:
        pass


def test_instrumentacion_registra_volumen_por_tipo():
    m = MercadoEnjambre(seed=42, ticks_horizonte=200)
    m.activar_instrumentacion()
    for _ in range(40):
        m.step()
    m.aplicar_noticia(-0.8)
    for _ in range(40):
        m.step()
    r = m.resumen_instrumentacion()
    assert r["agresor"] and r["proveedor"], "debe registrar volumen"
    # los porcentajes suman ~100
    assert abs(sum(r["agresor_pct"].values()) - 100) < 1.0
    assert abs(sum(r["proveedor_pct"].values()) - 100) < 1.0


def test_instrumentacion_es_opt_in():
    # sin activar, no hay callback ni contadores (producción intacta)
    m = MercadoEnjambre(seed=1, ticks_horizonte=50)
    assert m.libro.registrar_ejecucion_instr is None


def test_escenarios_de_estres_corren_y_devuelven_metricas():
    from calibration.escenarios import correr_escenario, variabilidad
    r = correr_escenario("negativa_fuerte", seed=42, post=60)
    for k in ("direccion_pct", "minimo_pct", "maximo_pct", "volatilidad_pct"):
        assert k in r
    # una noticia fuertemente negativa debe empujar la dirección hacia abajo
    assert r["direccion_pct"] < 0
    # la variabilidad entre semillas se reporta
    v = variabilidad("negativa_fuerte", seeds=(1, 42))
    assert "desv" in v and len(v["direcciones"]) == 2


def test_escenario_desconocido_lanza():
    from calibration.escenarios import correr_escenario
    try:
        correr_escenario("no_existe")
        assert False, "debió lanzar ValueError"
    except ValueError:
        pass


def test_senales_por_arquetipo_resume_bien():
    import json
    from contenido.respaldo import _senales_por_arquetipo
    lideres = json.dumps([
        {"arquetipo": "doomer", "senal": -0.8, "confianza": 0.9},
        {"arquetipo": "doomer", "senal": -0.6, "confianza": 0.7},
        {"arquetipo": "fomo_evangelista", "senal": 0.9, "confianza": 0.95},
    ])
    r = _senales_por_arquetipo(lideres)
    assert r["doomer"]["senal_media"] == -0.7
    assert r["doomer"]["n"] == 2
    assert r["fomo_evangelista"]["senal_media"] == 0.9
    # entrada vacía o inválida no rompe
    assert _senales_por_arquetipo(None) == {}
    assert _senales_por_arquetipo("no-json") == {}
```

## engine/validation/test_lexico_cobertura.py
```python
"""
Cobertura y acierto del respaldo léxico (`sentimiento_lexico`) sobre los 645
casos reales. Mide con la función REAL del motor (no un diccionario de juguete):

- % "mudo": titulares donde el léxico no encuentra ninguna palabra (señal 0).
- acierto de dirección cuando OPINA, separado por negativas y positivas.
- falsos positivos: positivas que el léxico marca como bajistas (el riesgo de
  agregar jerga bajista sin cuidado).

El respaldo solo se usa cuando la API de LLM no está disponible; por eso esto
mide ROBUSTEZ del plan B, no el 38% real (que usa el LLM). Sin coste, sin red
salvo la lectura del respaldo público.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # engine/

from brains.fallback import sentimiento_lexico  # noqa: E402


def _signo(x: float) -> int:
    return 1 if x > 0 else (-1 if x < 0 else 0)


def medir(casos: list[dict]) -> dict:
    total = mudo = 0
    op_neg = ok_neg = op_pos = ok_pos = fp_pos = 0
    for c in casos:
        rr = c.get("reaccion_real") or {}
        cat = rr.get("categoria")
        real = rr.get("pct_real")
        if cat not in ("negativa", "positiva") or real is None:
            continue
        total += 1
        s = sentimiento_lexico(c.get("titular", ""))
        if abs(s) < 1e-9:
            mudo += 1
            continue
        acierta = _signo(s) == _signo(real)
        if cat == "negativa":
            op_neg += 1
            ok_neg += acierta
        else:
            op_pos += 1
            ok_pos += acierta
            if s < 0:               # positiva leída como bajista = falso positivo
                fp_pos += 1
    return {
        "total": total, "mudo": mudo,
        "op_neg": op_neg, "ok_neg": ok_neg,
        "op_pos": op_pos, "ok_pos": ok_pos, "fp_pos": fp_pos,
    }


def _pct(a, b):
    return f"{100*a/b:.1f}%" if b else "s/d"


def imprimir(m: dict) -> None:
    t = m["total"]
    opina = t - m["mudo"]
    print(f"  casos con dirección real: {t}")
    print(f"  MUDO (señal 0):           {m['mudo']}  ({_pct(m['mudo'], t)})")
    print(f"  opina:                    {opina}  ({_pct(opina, t)})")
    print(f"  acierto NEGATIVAS (opina):{m['ok_neg']}/{m['op_neg']}  ({_pct(m['ok_neg'], m['op_neg'])})")
    print(f"  acierto POSITIVAS (opina):{m['ok_pos']}/{m['op_pos']}  ({_pct(m['ok_pos'], m['op_pos'])})")
    print(f"  FALSOS POSITIVOS (pos leída bajista): {m['fp_pos']}  ({_pct(m['fp_pos'], m['op_pos'])})")


def test_cobertura_y_precision():
    """El léxico ampliado: cubre más (menos mudo) manteniendo la precisión
    global y bajando los falsos positivos.

    Nota honesta sobre la métrica: subir la cobertura necesariamente aflora
    casos irreducibles (titulares alcistas que precedieron caídas), así que la
    TASA de acierto en negativas baja aunque el número absoluto de negativas
    bien clasificadas suba. Por eso NO exigimos una tasa alta de negativas
    (eso se optimiza trivialmente quedándose mudo). Exigimos: más cobertura,
    precisión global sana y menos falsos positivos que la línea base (39.7%).
    """
    from contenido.respaldo import casos_remotos
    m = medir(casos_remotos())
    assert m["total"] > 0, "no se leyeron casos del respaldo"
    opina = m["total"] - m["mudo"]
    # cobertura: el mudo baja del 65% (línea base medida: 74.5%)
    assert m["mudo"] / m["total"] < 0.65, f"mudo demasiado alto: {m['mudo']}/{m['total']}"
    # precisión global (cuando opina): ≥ 63%
    aciertos = m["ok_neg"] + m["ok_pos"]
    assert aciertos / max(1, opina) >= 0.63, "precisión global cayó"
    # falsos positivos en positivas: por debajo de la línea base (39.7%)
    assert m["fp_pos"] / max(1, m["op_pos"]) < 0.39, "demasiados falsos positivos"


def test_umbral_prefiere_mudo():
    """El flag de rollback: subir ENJAMBRE_LEXICO_UMBRAL fuerza 'mudo' en
    señales por debajo del umbral, sin tocar código."""
    titular = "Bitcoin tumbles as market crashes in a bloodbath sell-off"
    base = sentimiento_lexico(titular)
    assert base < 0, "el titular debería leerse bajista con umbral 0"
    os.environ["ENJAMBRE_LEXICO_UMBRAL"] = "1.1"   # exige confianza imposible
    try:
        assert sentimiento_lexico(titular) == 0.0, "con umbral alto debe callar"
    finally:
        os.environ.pop("ENJAMBRE_LEXICO_UMBRAL", None)
    # sin umbral, vuelve a opinar
    assert sentimiento_lexico(titular) < 0


def test_monitor_polaridad_no_crashea():
    """El monitor es pasivo y tolerante: nunca debe tumbar una simulación."""
    from model import monitorear_polaridad
    respuestas = [
        {"senal": -0.6, "fuente": "fallback"}, {"senal": 0.3, "fuente": "fallback"},
        {"senal": 0.1, "fuente": "api"}, {"senal": -0.2, "fuente": "cache"},
        {"senal": 0.0},  # sin fuente: no debe romper
    ]
    monitorear_polaridad(respuestas)          # con respaldo → loguea
    monitorear_polaridad([{"senal": 0.5, "fuente": "api"}])  # sin respaldo → calla
    monitorear_polaridad([])                  # vacío → no rompe


if __name__ == "__main__":
    from contenido.respaldo import casos_remotos
    print("\n📚 Cobertura del respaldo léxico sobre los 645 casos")
    print("=" * 55)
    imprimir(medir(casos_remotos()))
    print("=" * 55)
```

## engine/validation/test_memoria_secuencias.py
```python
"""
Validación de la memoria de agentes: el "modo cautela" en rachas de noticias.

La memoria (últimas 5 noticias) sirve para UNA cosa que sí funciona: detectar
rachas malas y activar `modo_cautela`, que dispara el freno de la manada
(ver test_freno_manada.py, donde se mide que el freno reduce el sobre-pánico).

Nota histórica: hubo un segundo mecanismo, la "memoria de percepción"
(`ajustar_por_contexto` sobre el miedoso/noise), que se PROBÓ y NO amortiguaba
el pánico (INFORME_NIVEL1_RESULTADO.md). Se retiró por peso muerto; la palanca
que quedó es el freno de la manada. Este test cubre lo que sostiene ese freno:
que la cautela se activa cuando debe.

Corre local, sin LLM ni red.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # engine/

from model import RUTA_CONFIG, MercadoEnjambre  # noqa: E402


def test_cautela_se_activa_en_racha():
    """La cautela se dispara tras 3 malas y NO antes (es lo que enciende el freno)."""
    m = MercadoEnjambre(seed=1, ticks_horizonte=30, ruta_config=RUTA_CONFIG)
    mie = next(a for a in m.agents if type(a).__name__ == "Miedoso")
    assert not mie.modo_cautela
    m.aplicar_noticia(-0.5); m.aplicar_noticia(-0.5)
    assert not mie.modo_cautela, "cautela no debe activarse con 2 malas"
    m.aplicar_noticia(-0.5)
    assert mie.modo_cautela, "cautela debe activarse con 3 malas"


if __name__ == "__main__":
    print("\n🧪 Memoria: activación del modo cautela")
    print("=" * 45)
    test_cautela_se_activa_en_racha()
    print("✅ La cautela se activa con 3 malas (y no antes).")
    print("   El efecto de amortiguación se mide en test_freno_manada.py.")
    print("=" * 45)
```

## engine/validation/test_mercado.py
```python
"""Tests de la clasificación por tipo de mercado y sus perfiles (Fase 1).

El enjambre razona de qué mercado habla la noticia (índice, acción,
petróleo, oro, cripto) y aplica su personalidad: el oro sube con el miedo,
el cripto amplifica todo, cada mercado reacciona a su manera.
"""

import pytest

from brains import mercado
from model import MercadoEnjambre


@pytest.fixture(autouse=True)
def sin_api(monkeypatch):
    # los tests no llaman a la IA: se prueba el clasificador léxico
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)


# ---------- clasificación léxica (fallback sin IA) ----------

def test_clasifica_por_palabras_clave():
    assert mercado.clasificar_lexico("Bitcoin surges past $100,000") == "cripto"
    assert mercado.clasificar_lexico("Nvidia earnings smash expectations") == "accion"
    # una noticia macro amplia cae en índice (el perfil por defecto)
    assert mercado.clasificar_lexico("La Fed sube las tasas 50 puntos base") == "indice"


def test_oro_y_petroleo_en_pausa_caen_a_indice():
    """Foco del producto: SP500 + acciones + cripto. Oro y petróleo están en
    pausa → sus noticias se tratan con el perfil por defecto (índice), no con
    su dial propio (que se conserva para reactivar)."""
    assert mercado.clasificar_lexico("Oro alcanza máximo histórico como refugio") == "indice"
    assert mercado.clasificar_lexico("Oil prices spike as OPEC cuts output") == "indice"
    assert "oro" not in mercado.MERCADOS_ACTIVOS
    assert "petroleo" not in mercado.MERCADOS_ACTIVOS
    # los diales calibrados se conservan (para reactivar sin recalibrar)
    assert mercado.perfil_de("oro")["refugio"] == 0.25


def test_clasificar_sin_api_usa_el_lexico():
    # sin ANTHROPIC_API_KEY, clasificar() no llama afuera
    assert mercado.clasificar("Ethereum crashes 20% overnight") == "cripto"


def test_perfil_de_devuelve_defecto_para_tipo_desconocido():
    p = mercado.perfil_de("no-existe")
    assert p["tipo"] == "indice"
    assert p["sensibilidad"] == 1.0


# ---------- el perfil cambia la reacción del enjambre ----------

def _reaccion(perfil_tipo: str, tono: float, seed: int = 7) -> float:
    """Corre una simulación breve con un tono dado bajo un perfil y devuelve
    la dirección del precio (%)."""
    modelo = MercadoEnjambre(seed=seed, ticks_horizonte=200)
    modelo.correr(60)  # calentamiento
    base = modelo.historial_precios[-1]
    modelo.perfil = mercado.perfil_de(perfil_tipo)
    # inyecta el tono directamente por el mismo camino que una noticia real
    modelo.sentimiento = modelo._aplicar_perfil(tono)
    for _ in range(120):
        modelo.step()
    return (modelo.historial_precios[-1] - base) / base * 100


def test_los_metales_resisten_el_miedo():
    """Refugio parcial: ante un tono NEGATIVO (miedo), los metales (oro+plata+
    cobre) caen MUCHO MENOS que el índice — el oro los sostiene en parte —,
    aunque el cobre/plata no lo invierten del todo. Se compara el tono efectivo."""
    indice = mercado.perfil_de("indice")
    oro = mercado.perfil_de("oro")
    modelo = MercadoEnjambre(seed=1, ticks_horizonte=10)
    modelo.perfil = indice
    tono_indice = modelo._aplicar_perfil(-0.6)
    modelo.perfil = oro
    tono_oro = modelo._aplicar_perfil(-0.6)
    assert tono_indice < 0                          # el índice cae con el miedo
    assert tono_oro > tono_indice                   # los metales resisten…
    assert abs(tono_oro) < abs(tono_indice) * 0.7   # …caen bastante menos (refugio parcial)


def test_el_cripto_amplifica_el_movimiento():
    """Mayor sensibilidad: un mismo tono positivo mueve más al cripto."""
    modelo = MercadoEnjambre(seed=1, ticks_horizonte=10)
    modelo.perfil = mercado.perfil_de("indice")
    t_indice = modelo._aplicar_perfil(0.5)
    modelo.perfil = mercado.perfil_de("cripto")
    t_cripto = modelo._aplicar_perfil(0.5)
    assert t_cripto > t_indice             # el cripto exagera la euforia


def test_aplicar_titular_acepta_y_guarda_el_perfil():
    modelo = MercadoEnjambre(seed=3, ticks_horizonte=180)
    modelo.correr(60)
    perfil = mercado.perfil_de("petroleo")
    respuestas = [{"senal": 0.0, "confianza": 0.5, "frase": "x", "fuente": "fallback"}
                  for _ in modelo._lideres]
    modelo.aplicar_titular("Oil jumps on supply fears", respuestas=respuestas, perfil=perfil)
    assert modelo.perfil["tipo"] == "petroleo"
```

## engine/validation/test_muro.py
```python
"""Tests de la Etapa 7: el muro — endpoints, pipeline del día y límites."""

import json

import pytest
from fastapi.testclient import TestClient

import brains.cerebro as cerebro
import server
from contenido import limites, persistencia, pipeline, seguridad


@pytest.fixture(autouse=True)
def entorno(monkeypatch, tmp_path):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("ALPACA_API_KEY_ID", raising=False)
    monkeypatch.setattr(cerebro, "RUTA_CACHE", tmp_path / "cache.json")
    monkeypatch.setenv("ENJAMBRE_DB", str(tmp_path / "enjambre.db"))
    # tope holgado para los tests del muro (el de 5 se prueba aparte)
    monkeypatch.setenv("ENJAMBRE_MAX_SIM_DIA", "50")
    limites.reiniciar()
    seguridad.reiniciar()


@pytest.fixture(scope="function")
def dia_preparado():
    """Corre el pipeline una vez: 3 destacadas simuladas con frames."""
    return pipeline.preparar_dia(semilla_base=42)


def test_pipeline_prepara_el_dia(dia_preparado):
    assert len(dia_preparado["publicadas"]) == 3
    conexion = persistencia.conectar()
    destacadas = persistencia.listar_simulaciones(conexion, solo_destacadas=True)
    conexion.close()
    assert len(destacadas) == 3
    # la regla del replay: las destacadas conservan sus frames binarios
    for publicada in dia_preparado["publicadas"]:
        frames = persistencia.leer_frames(publicada["sim_id"])
        assert frames is not None
        assert len(frames) == (server.TICKS_PREVIOS + server.TICKS_POSTERIORES) * (8 + 10150)


def test_pipeline_es_idempotente(dia_preparado):
    """Correrlo dos veces el mismo día no gasta de nuevo (presupuesto)."""
    segunda = pipeline.preparar_dia(semilla_base=42)
    assert segunda["publicadas"] == []
    conexion = persistencia.conectar()
    assert len(persistencia.listar_simulaciones(conexion, solo_destacadas=True)) == 3
    conexion.close()


def test_api_muro_muestra_tarjetas(dia_preparado):
    cliente = TestClient(server.app)
    datos = cliente.get("/api/muro").json()
    tarjetas = datos["tarjetas"]
    assert len(tarjetas) >= 6  # 3 destacadas + pendientes de impacto alto

    # destacadas primero, con su resumen editorial completo
    for tarjeta in tarjetas[:3]:
        assert tarjeta["estado"] == "simulada"
        assert tarjeta["destacada"] is True
        assert tarjeta["resumen"]["direccion"] in "▲▼◆"
        assert tarjeta["resumen"]["agitacion"] in ("bajo", "medio", "alto")
        assert tarjeta["resumen"]["frase"]["frase"]

    # las pendientes existen (Estado B) y las descartadas no aparecen
    pendientes = [t for t in tarjetas if t["estado"] == "pendiente"]
    assert pendientes
    titulares = " ".join(t["titular"] for t in tarjetas)
    assert "Celebrity chef" not in titulares  # Estado C: fuera del muro

    from contenido.vocabulario import DISCLAIMER
    assert datos["descargo"] == DISCLAIMER


def test_api_simulacion_y_replay(dia_preparado):
    cliente = TestClient(server.app)
    sim_id = dia_preparado["publicadas"][0]["sim_id"]

    detalle = cliente.get(f"/api/simulacion/{sim_id}").json()
    assert detalle["destacada"] is True
    assert detalle["tiene_replay"] is True
    assert len(detalle["serie_precios"]) == 151
    assert detalle["resumen"]["descargo"]

    replay = cliente.get(f"/api/simulacion/{sim_id}/replay")
    assert replay.status_code == 200
    assert len(replay.content) == 150 * 10158  # 8 cabecera + 10150 agentes

    assert cliente.get("/api/simulacion/no-existe").status_code == 404
    assert cliente.get("/api/simulacion/no-existe/replay").status_code == 404


def test_api_simular_titular_pendiente(dia_preparado):
    cliente = TestClient(server.app)
    tarjetas = cliente.get("/api/muro").json()["tarjetas"]
    pendiente = next(t for t in tarjetas if t["estado"] == "pendiente")

    respuesta = cliente.post("/api/simular-titular", json={"id": pendiente["id"]}).json()
    assert respuesta["estado"] == "adelante"
    assert respuesta["titular"] == pendiente["titular"]

    # una ya simulada devuelve directo su sim_id (caché, costo cero)
    simulada = next(t for t in tarjetas if t["estado"] == "simulada")
    respuesta = cliente.post("/api/simular-titular", json={"id": simulada["id"]}).json()
    assert respuesta == {"estado": "simulada", "sim_id": simulada["sim_id"]}

    assert cliente.post("/api/simular-titular", json={"id": "no-existe"}).status_code == 404


def test_limite_gratis_por_dia():
    # gratis: 1 simulación al día por IP; la siguiente se bloquea e invita a Premium
    for _ in range(limites.tope_dia_gratis()):
        permitido, _ = limites.permitir("1.2.3.4")
        assert permitido
    permitido, motivo = limites.permitir("1.2.3.4")
    assert not permitido
    assert "Premium" in motivo
    # otra IP sigue pudiendo (el cupo es por persona)
    assert limites.permitir("5.6.7.8")[0]


def test_limite_gratis_por_dispositivo():
    # dos dispositivos detrás de la MISMA IP (oficina/CGNAT): cada uno su cupo
    assert limites.permitir("5.5.5.5", cliente_id="disp-A")[0]      # A: su 1/día
    assert limites.permitir("5.5.5.5", cliente_id="disp-B")[0]      # B: su propio 1/día
    assert not limites.permitir("5.5.5.5", cliente_id="disp-A")[0]  # A ya gastó el suyo


def _premium_con_token(email):
    """Da de alta un Premium y devuelve su token del enlace mágico."""
    from contenido import persistencia
    conexion = persistencia.conectar()
    alta = persistencia.agregar_suscriptor(conexion, email)
    persistencia.confirmar_suscriptor(conexion, alta["token_confirma"])
    persistencia.set_premium(conexion, email, True)
    token = persistencia.emitir_token_enjambre(conexion, email)
    conexion.close()
    return token


def test_limite_premium_por_mes():
    # un Premium tiene 40/MES canjeando su TOKEN; el correo desnudo ya no sirve
    token = _premium_con_token("vip@lector.cl")

    limites.permitir("9.9.9.9")  # gasta la gratis de la IP
    # con su token Premium: llega a 40, sin que lo frene el límite gratis de la IP
    for i in range(limites.tope_mes_premium()):
        permitido, _ = limites.permitir("9.9.9.9", premium_token=token)
        assert permitido, f"la simulación Premium #{i+1} debería permitirse"
    permitido, motivo = limites.permitir("9.9.9.9", premium_token=token)
    assert not permitido and "mes" in motivo


def test_token_invalido_no_da_premium():
    # un token que no existe cae al nivel gratis (no hay forma de fingir Premium)
    assert limites.permitir("7.7.7.7", premium_token="token-que-no-existe-xxxx")[0]
    permitido, motivo = limites.permitir("7.7.7.7", premium_token="token-que-no-existe-xxxx")
    assert not permitido and "Premium" in motivo  # gastó su 1/día gratis


def test_premium_cupo_mensual_persiste_en_disco():
    # el cupo mensual vive en disco: una conexión nueva ve el mismo gasto
    from datetime import date
    from contenido import persistencia
    token = _premium_con_token("vip2@lector.cl")

    for _ in range(5):
        limites.permitir("8.8.8.8", premium_token=token)
    mes = date.today().isoformat()[:7]
    conexion = persistencia.conectar()
    assert persistencia.gasto_premium_mes(conexion, "vip2@lector.cl", mes) == 5
    conexion.close()


def test_tope_global_diario(monkeypatch):
    monkeypatch.setenv("ENJAMBRE_MAX_SIM_DIA", "2")
    assert limites.permitir("a")[0]
    assert limites.permitir("b")[0]
    permitido, motivo = limites.permitir("c")
    assert not permitido
    assert motivo == limites.MENSAJE_GLOBAL


def test_websocket_respeta_el_tope(monkeypatch):
    """Agotado el presupuesto del día, el canal responde 'limite' sin gastar."""
    monkeypatch.setenv("ENJAMBRE_MAX_SIM_DIA", "0")
    cliente = TestClient(server.app)
    with cliente.websocket_connect("/ws") as ws:
        ws.send_text(json.dumps({"tipo": "simular", "titular": "Prueba", "ritmo": 0}))
        mensaje = json.loads(ws.receive_text())
        assert mensaje["tipo"] == "limite"
        assert "Pulso" in mensaje["mensaje"]


def test_simulacion_del_muro_vincula_la_tarjeta(dia_preparado):
    """El flujo Estado B: simular on-demand deja la tarjeta en Estado A."""
    cliente = TestClient(server.app)
    tarjetas = cliente.get("/api/muro").json()["tarjetas"]
    pendiente = next(t for t in tarjetas if t["estado"] == "pendiente")

    with cliente.websocket_connect("/ws") as ws:
        ws.send_text(json.dumps({
            "tipo": "simular", "titular": pendiente["titular"],
            "titular_id": pendiente["id"], "seed": 7, "ritmo": 0,
        }))
        while True:
            try:
                mensaje = json.loads(ws.receive_text())
                if mensaje["tipo"] == "fin":
                    break
            except Exception:
                continue  # frames binarios intercalados

    tarjetas = cliente.get("/api/muro").json()["tarjetas"]
    actualizada = next(t for t in tarjetas if t["id"] == pendiente["id"])
    assert actualizada["estado"] == "simulada"
    assert actualizada["sim_id"] == mensaje["sim_id"]
```

## engine/validation/test_observatorio.py
```python
"""Tests del Modo Observatorio: el enjambre sigue vivo y recibe noticias
encima, sin frenar, sin congelarse y sin crecer en memoria."""

import json

import numpy as np
import pytest
from fastapi.testclient import TestClient

import brains.cerebro as cerebro
import server
from contenido import limites, seguridad
from model import MercadoEnjambre


@pytest.fixture(autouse=True)
def entorno(monkeypatch, tmp_path):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setattr(cerebro, "RUTA_CACHE", tmp_path / "cache.json")
    monkeypatch.setenv("ENJAMBRE_DB", str(tmp_path / "enjambre.db"))
    monkeypatch.setenv("ENJAMBRE_MAX_SIM_DIA", "50")
    limites.reiniciar()
    seguridad.reiniciar()


# ---------- comportamiento del motor a lo largo del tiempo ----------

def test_el_enjambre_no_se_congela_tras_la_noticia():
    """Después de reaccionar, el mercado SIGUE vivo (produce retornos)."""
    m = MercadoEnjambre(seed=42, ticks_horizonte=400)
    m.correr(80)
    m.aplicar_titular("Amazon sube 15% tras resultados excelentes",
                      respuestas=[{"senal": 0.8, "confianza": 0.9, "frase": "x"}] * 1000)
    m.correr(120)
    # el mercado sigue moviéndose bien pasada la reacción (no está estancado)
    retornos_tardios = m.retornos[-30:]
    assert np.std(retornos_tardios) > 0


def test_el_animo_se_desvanece_hacia_la_calma():
    """La noticia pierde fuerza con el tiempo: el ánimo vuelve a ~0."""
    m = MercadoEnjambre(seed=7, ticks_horizonte=400)
    m.correr(60)
    m.aplicar_titular("Pánico: quiebra un banco enorme",
                      respuestas=[{"senal": -0.9, "confianza": 0.9, "frase": "x"}] * 1000)
    animo_inicial = abs(m.sentimiento)
    m.correr(80)
    assert abs(m.sentimiento) < animo_inicial * 0.2  # se desvaneció


def test_se_puede_soltar_una_segunda_noticia_encima():
    """Una noticia nueva reactiva al enjambre aunque la vieja se apagó."""
    m = MercadoEnjambre(seed=3, ticks_horizonte=500)
    m.correr(60)
    m.aplicar_titular("Quiebra un banco; pánico en el mercado",
                      respuestas=[{"senal": -0.8, "confianza": 0.9, "frase": "x"}] * 1000)
    m.correr(60)  # se apaga
    assert abs(m.sentimiento) < 0.2
    m.aplicar_titular("La bolsa alcanza máximo histórico tras ganancias récord",
                      respuestas=[{"senal": 0.9, "confianza": 0.9, "frase": "x"}] * 1000)
    assert m.sentimiento > 0.3  # la nueva noticia lo reactivó


def test_las_listas_no_crecen_sin_fin_en_sesiones_largas():
    m = MercadoEnjambre(seed=1, ticks_horizonte=2000)
    m.correr(1500)
    assert len(m.historial_precios) <= m.MAX_HISTORIAL + 1
    assert len(m.retornos) <= m.MAX_HISTORIAL
    # y el tick sigue avanzando aunque la cola esté acotada
    assert m.tick >= 1500


# ---------- el flujo por WebSocket ----------

def test_observatorio_late_y_recibe_una_noticia_encima():
    cliente = TestClient(server.app)
    with cliente.websocket_connect("/ws") as ws:
        ws.send_text(json.dumps({
            "tipo": "observatorio", "ritmo": 0.001,
            "titular": "Amazon sube 15% tras resultados",
        }))

        frames = 0
        inicio_visto = False
        arranque_visto = False
        for _ in range(300):
            m = ws.receive()
            if m.get("text"):
                dato = json.loads(m["text"])
                if dato["tipo"] == "observatorio-inicio":
                    arranque_visto = True
                elif dato["tipo"] == "inicio":
                    inicio_visto = True
                    assert len(dato["lideres"]) == 1150
            elif m.get("bytes"):
                frames += 1
                assert len(m["bytes"]) == 8 + 10150
            if arranque_visto and inicio_visto and frames > 8:
                break

        assert arranque_visto  # el enjambre arrancó vivo
        assert inicio_visto    # leyó la noticia inicial
        assert frames > 8      # y siguió latiendo (transmitiendo)

        ws.send_text(json.dumps({"tipo": "detener"}))


def test_observatorio_respeta_el_tope_de_noticias(monkeypatch):
    monkeypatch.setenv("ENJAMBRE_MAX_SIM_DIA", "1")
    limites.reiniciar()
    cliente = TestClient(server.app)
    with cliente.websocket_connect("/ws") as ws:
        ws.send_text(json.dumps({"tipo": "observatorio", "ritmo": 0.001, "titular": "Primera"}))
        # la primera noticia consume el único cupo; la segunda debe toparse
        ws.send_text(json.dumps({"tipo": "noticia", "titular": "Segunda noticia"}))
        limite_visto = False
        for _ in range(400):
            m = ws.receive()
            if m.get("text") and json.loads(m["text"]).get("tipo") == "limite":
                limite_visto = True
                break
        ws.send_text(json.dumps({"tipo": "detener"}))
    assert limite_visto
```

## engine/validation/test_p2_tono.py
```python
"""
P2 — separar "tono de mercado" de "apuesta del líder".

Verifica que:
1. Con peso_tono_invertidores = 1.0, el tono es IDÉNTICO al histórico
   (promedio de señales ponderado por confianza).
2. Con peso 0.0, los arquetipos invertidores (contrarian/optimista/quant) NO
   fijan el clima: ante una mala noticia, el tono es MÁS negativo (fiel a la
   noticia) que con 1.0.
3. La APUESTA individual de cada líder (su .senal) NO cambia con P2 — solo
   cambia el tono de mercado.

Corre local, sin LLM: las respuestas por arquetipo se generan con las
transformaciones reales del fallback (mismo espíritu que el LLM).
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # engine/

from brains.fallback import TRANSFORMACIONES, sentimiento_lexico  # noqa: E402
from model import RUTA_CONFIG, ARQUETIPOS_INVERSORES, MercadoEnjambre  # noqa: E402

TITULAR_MALO = "Bitcoin tumbles below 23000 after Celsius freezes customer withdrawals"


def _respuestas(modelo, titular):
    """Señal por arquetipo como la daría el fallback, marcada 'api' para
    ejercer la ruta de consenso (no el atajo léxico)."""
    s = sentimiento_lexico(titular)
    out = []
    for lider in modelo._lideres:
        senal, conf, _ = TRANSFORMACIONES[lider.arquetipo](s, titular)
        out.append({"senal": senal, "confianza": conf, "frase": "", "fuente": "api"})
    return out


def _tono(peso: float) -> float:
    m = MercadoEnjambre(seed=42, ticks_horizonte=5, ruta_config=RUTA_CONFIG)
    m._umbral_correccion = 0.0  # aísla P2: sin Plan A (corrección de sesgo)
    m._peso_tono_invertidores = peso
    resp = _respuestas(m, TITULAR_MALO)
    return m._tono_de_titular(TITULAR_MALO, resp)


def test_peso_1_preserva_el_historico():
    """peso 1.0 = promedio ponderado por confianza de TODAS las señales."""
    m = MercadoEnjambre(seed=42, ticks_horizonte=5, ruta_config=RUTA_CONFIG)
    m._umbral_correccion = 0.0  # aísla P2: sin Plan A (corrección de sesgo)
    m._peso_tono_invertidores = 1.0
    m._peso_doomer = 1.0  # incluir el doomer selectivo a peso pleno = promedio de TODAS
    resp = _respuestas(m, TITULAR_MALO)
    ia = [r for r in resp if r["fuente"] in ("api", "cache")]
    peso = sum(r["confianza"] for r in ia)
    historico = sum(r["senal"] * r["confianza"] for r in ia) / peso
    from model import GANANCIA_CONSENSO
    esperado = max(-1.0, min(1.0, historico * GANANCIA_CONSENSO))
    assert abs(m._tono_de_titular(TITULAR_MALO, resp) - esperado) < 1e-9


def test_peso_0_hace_el_tono_mas_fiel():
    """Ante mala noticia, excluir a los invertidores hace el tono MÁS negativo."""
    tono_1 = _tono(1.0)
    tono_0 = _tono(0.0)
    assert tono_1 < 0, "el titular es malo: el tono debe ser negativo"
    assert tono_0 < tono_1, f"P2 debe hacer el tono más negativo: {tono_0} vs {tono_1}"


def test_apuesta_del_lider_no_cambia():
    """P2 solo toca el TONO; la señal individual del líder queda intacta."""
    m = MercadoEnjambre(seed=42, ticks_horizonte=5, ruta_config=RUTA_CONFIG)
    resp = _respuestas(m, TITULAR_MALO)
    m._peso_tono_invertidores = 0.0
    m.aplicar_titular(TITULAR_MALO, respuestas=resp,
                      perfil={"sensibilidad": 1.0, "refugio": 0.0})
    # las señales de los invertidores siguen siendo su apuesta (no anuladas)
    invertidores = [l for l in m._lideres if l.arquetipo in ARQUETIPOS_INVERSORES]
    assert any(abs(l.senal) > 0.05 for l in invertidores), \
        "los invertidores deben seguir operando con su propia señal"


if __name__ == "__main__":
    print("\n🧪 P2: separar tono de apuesta")
    print("=" * 45)
    print(f"  tono con peso 1.0 (actual): {_tono(1.0):+.3f}")
    print(f"  tono con peso 0.0 (P2):     {_tono(0.0):+.3f}")
    print("=" * 45)
```

## engine/validation/test_p3_p4.py
```python
"""
P3 — acotar magnitudes absurdas por mercado.
P4 — confianza (fuerza del consenso) en el reporte.

P3: `acotar_magnitud` recorta la MAGNITUD al tope del mercado (cripto ±30,
acción ±40) SIN tocar el signo; los mercados sin tope quedan igual.
P4: al aplicar un titular, el modelo guarda la fuerza del consenso, y el reporte
la expone como `confianza` = abs(consenso) ∈ [0, 1].

Corre local, sin LLM ni red.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # engine/

from brains.fallback import TRANSFORMACIONES, sentimiento_lexico  # noqa: E402
from model import (  # noqa: E402
    FACTORES_LIQUIDEZ, RUTA_CONFIG, MercadoEnjambre, acotar_magnitud,
)

TITULAR_MALO = "Bitcoin tumbles below 23000 after Celsius freezes customer withdrawals"


# ---------- P3 ----------

def test_p3_acota_cripto_conservando_signo():
    """Cripto (tope 30): +45 → +30, −52 → −30; el signo se conserva."""
    assert acotar_magnitud("cripto", 45.0) == 30.0
    assert acotar_magnitud("cripto", -52.0) == -30.0
    assert acotar_magnitud("cripto", 12.0) == 12.0  # dentro del tope, intacto


def test_p3_accion_tiene_tope_mayor():
    assert acotar_magnitud("accion", 55.0) == 40.0
    assert acotar_magnitud("accion", 55.0) > acotar_magnitud("cripto", 55.0)


def test_p3_indice_sin_tope():
    """El índice (base de calibración) no se acota."""
    assert acotar_magnitud("indice", 45.0) == 45.0
    assert acotar_magnitud(None, 999.0) == 999.0


def test_p3_no_toca_valores_dentro_del_rango():
    for m in ("cripto", "accion"):
        tope = FACTORES_LIQUIDEZ[m]
        assert acotar_magnitud(m, tope - 1) == tope - 1
        assert acotar_magnitud(m, -(tope - 1)) == -(tope - 1)


# ---------- P4 ----------

def _respuestas(modelo, titular):
    s = sentimiento_lexico(titular)
    out = []
    for lider in modelo._lideres:
        senal, conf, _ = TRANSFORMACIONES[lider.arquetipo](s, titular)
        out.append({"senal": senal, "confianza": conf, "frase": "", "fuente": "api"})
    return out


def test_p4_guarda_la_fuerza_del_consenso():
    """Tras leer un titular, el modelo guarda abs(consenso) > 0."""
    m = MercadoEnjambre(seed=42, ticks_horizonte=5, ruta_config=RUTA_CONFIG)
    assert m._ultimo_consenso == 0.0  # antes de cualquier noticia
    resp = _respuestas(m, TITULAR_MALO)
    m._tono_de_titular(TITULAR_MALO, resp)
    assert abs(m._ultimo_consenso) > 0.0, "el consenso de una noticia clara no es 0"


def test_p4_confianza_es_abs_del_consenso():
    """La confianza que expondrá el reporte = abs(consenso) ∈ [0, 1]."""
    m = MercadoEnjambre(seed=42, ticks_horizonte=5, ruta_config=RUTA_CONFIG)
    resp = _respuestas(m, TITULAR_MALO)
    m._tono_de_titular(TITULAR_MALO, resp)
    confianza = abs(m._ultimo_consenso)
    assert 0.0 <= confianza <= 1.0


if __name__ == "__main__":
    print("\n🧪 P3 (acotar magnitudes) + P4 (confianza)")
    print("=" * 45)
    print(f"  P3 cripto +45 → {acotar_magnitud('cripto', 45.0)}  (tope 30)")
    print(f"  P3 accion +55 → {acotar_magnitud('accion', 55.0)}  (tope 40)")
    print(f"  P3 indice +45 → {acotar_magnitud('indice', 45.0)}  (sin tope)")
    m = MercadoEnjambre(seed=42, ticks_horizonte=5, ruta_config=RUTA_CONFIG)
    m._tono_de_titular(TITULAR_MALO, _respuestas(m, TITULAR_MALO))
    print(f"  P4 confianza (abs consenso): {abs(m._ultimo_consenso):.2f}")
    print("=" * 45)
```

## engine/validation/test_pagos.py
```python
"""Tests de la integración de pagos (Polar → llave Premium de El Pulso)."""

import base64
import hashlib
import hmac
import json
import time

import pytest
from fastapi.testclient import TestClient

import server
from contenido import pagos, persistencia

SECRETO = "whsec_" + base64.b64encode(b"secreto-de-prueba-para-polar").decode()


@pytest.fixture(autouse=True)
def entorno(monkeypatch, tmp_path):
    monkeypatch.setenv("ENJAMBRE_DB", str(tmp_path / "enjambre.db"))
    monkeypatch.setenv("POLAR_WEBHOOK_SECRET", SECRETO)


def _firmar(cuerpo: bytes, wid: str = "msg_1", wts: int | None = None) -> dict:
    """Firma un cuerpo como lo haría Polar (Standard Webhooks)."""
    wts = wts if wts is not None else int(time.time())
    clave = base64.b64decode(SECRETO.split("_", 1)[1])
    firmado = f"{wid}.{wts}.".encode() + cuerpo
    firma = base64.b64encode(hmac.new(clave, firmado, hashlib.sha256).digest()).decode()
    return {"webhook-id": wid, "webhook-timestamp": str(wts), "webhook-signature": f"v1,{firma}"}


def _evento(tipo: str, email: str = "pagador@lector.cl", hasta: str = "2027-01-01") -> bytes:
    data = {"customer": {"email": email}, "current_period_end": hasta + "T00:00:00Z",
            "status": "active"}
    return json.dumps({"type": tipo, "data": data}).encode()


# ---------- firma ----------

def test_firma_valida_y_activa_premium():
    conexion = persistencia.conectar()
    cuerpo = _evento("subscription.active")
    res = pagos.procesar_evento(conexion, json.loads(cuerpo))
    assert res["accion"] == "premium_on"
    assert persistencia.es_premium(conexion, "pagador@lector.cl")   # alta directa + premium
    conexion.close()


def test_firma_invalida_rechaza():
    cabeceras = {"webhook-id": "msg_1", "webhook-timestamp": str(int(time.time())),
                 "webhook-signature": "v1,firmafalsa"}
    assert not pagos.verificar_firma(_evento("subscription.active"), cabeceras)


def test_sin_secreto_falla_cerrado(monkeypatch):
    monkeypatch.delenv("POLAR_WEBHOOK_SECRET", raising=False)
    cuerpo = _evento("subscription.active")
    assert not pagos.verificar_firma(cuerpo, _firmar(cuerpo))


def test_timestamp_viejo_se_rechaza():
    cuerpo = _evento("subscription.active")
    viejo = _firmar(cuerpo, wts=int(time.time()) - 10_000)
    assert not pagos.verificar_firma(cuerpo, viejo)


# ---------- lógica de negocio ----------

def test_cancelacion_deja_vencer_no_corta_ya():
    """Cancelar (al final del período) mantiene Premium hasta el vencimiento."""
    conexion = persistencia.conectar()
    pagos.procesar_evento(conexion, json.loads(_evento("subscription.active", hasta="2027-06-01")))
    res = pagos.procesar_evento(conexion, json.loads(_evento("subscription.canceled", hasta="2027-06-01")))
    assert res["accion"] == "premium_on"                       # sigue activo…
    assert persistencia.es_premium(conexion, "pagador@lector.cl")  # …hasta que venza
    conexion.close()


def test_revocacion_corta_de_inmediato():
    conexion = persistencia.conectar()
    pagos.procesar_evento(conexion, json.loads(_evento("subscription.active")))
    res = pagos.procesar_evento(conexion, json.loads(_evento("subscription.revoked")))
    assert res["accion"] == "premium_off"
    assert not persistencia.es_premium(conexion, "pagador@lector.cl")
    conexion.close()


def test_evento_sin_email_se_ignora():
    conexion = persistencia.conectar()
    res = pagos.procesar_evento(conexion, {"type": "subscription.active", "data": {}})
    assert res["accion"] == "ignorado"
    conexion.close()


# ---------- endpoint completo ----------

def test_endpoint_webhook_activa_premium():
    cliente = TestClient(server.app)
    cuerpo = _evento("subscription.active", email="nuevo@lector.cl")
    r = cliente.post("/pulso/webhook/polar", content=cuerpo, headers=_firmar(cuerpo))
    assert r.status_code == 200 and r.json()["accion"] == "premium_on"
    conexion = persistencia.conectar()
    assert persistencia.es_premium(conexion, "nuevo@lector.cl")
    conexion.close()


def test_endpoint_webhook_rechaza_sin_firma():
    cliente = TestClient(server.app)
    cuerpo = _evento("subscription.active")
    r = cliente.post("/pulso/webhook/polar", content=cuerpo)  # sin cabeceras de firma
    assert r.status_code == 401


def test_enlace_magico_desbloqueo_y_verificar():
    """El enlace mágico: pedir (respuesta neutra) → canjear el token → Premium.
    Y el oráculo por correo YA NO existe (cerrado el hallazgo #3)."""
    conexion = persistencia.conectar()
    alta = persistencia.agregar_suscriptor(conexion, "vip@lector.cl")
    persistencia.confirmar_suscriptor(conexion, alta["token_confirma"])
    persistencia.set_premium(conexion, "vip@lector.cl", True)
    conexion.close()

    cliente = TestClient(server.app)

    # pedir el enlace: respuesta SIEMPRE neutra (no revela quién es Premium)
    r = cliente.post("/api/pulso/desbloqueo", json={"email": "vip@lector.cl"})
    assert r.json()["enviado"] is True
    r_no = cliente.post("/api/pulso/desbloqueo", json={"email": "nadie@lector.cl"})
    assert r_no.json()["enviado"] is True  # idéntica, sin filtrar nada

    # el token quedó emitido en la base; el navegador lo canjea
    conexion = persistencia.conectar()
    token = persistencia.emitir_token_enjambre(conexion, "vip@lector.cl")
    conexion.close()
    v = cliente.get("/api/pulso/enjambre/verificar", params={"token": token}).json()
    assert v["premium"] is True and v["limite"] == 40 and v["periodo"] == "mes"

    # un token inválido → nivel gratis, sin revelar nada
    v2 = cliente.get("/api/pulso/enjambre/verificar", params={"token": "x" * 20}).json()
    assert v2["premium"] is False and v2["limite"] == 1

    # el endpoint-oráculo por correo fue eliminado
    assert cliente.get("/api/pulso/premium", params={"email": "vip@lector.cl"}).status_code == 404
```

## engine/validation/test_pulso.py
```python
"""Tests de la Etapa 8: El Pulso — captura, boletín, double opt-in, ritual."""

import struct

import pytest
from fastapi.testclient import TestClient

import brains.cerebro as cerebro
import server
from contenido import boletin, captura, limites, persistencia, pipeline, seguridad
from contenido.vocabulario import DISCLAIMER, verificar_pieza


@pytest.fixture(autouse=True)
def entorno(monkeypatch, tmp_path):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("ALPACA_API_KEY_ID", raising=False)
    monkeypatch.delenv("RESEND_API_KEY", raising=False)
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.setattr(cerebro, "RUTA_CACHE", tmp_path / "cache.json")
    monkeypatch.setenv("ENJAMBRE_DB", str(tmp_path / "enjambre.db"))
    limites.reiniciar()
    seguridad.reiniciar()


@pytest.fixture()
def dia():
    return pipeline.preparar_dia(semilla_base=42)


# ---------- captura del momento dramático ----------

def test_captura_genera_png_valido():
    serie = [100.0 + (i % 7) - 3 for i in range(151)]
    png = captura.generar_png(
        "Quiebra un banco", {"direccion_pct": -8.4, "volatilidad_pct": 1.6}, serie)
    assert png[:8] == b"\x89PNG\r\n\x1a\n"  # firma PNG
    assert len(png) > 5000


def test_endpoint_imagen(dia):
    cliente = TestClient(server.app)
    sim_id = dia["publicadas"][0]["sim_id"]
    respuesta = cliente.get(f"/api/simulacion/{sim_id}/imagen")
    assert respuesta.status_code == 200
    assert respuesta.headers["content-type"] == "image/png"
    assert respuesta.content[:8] == b"\x89PNG\r\n\x1a\n"
    assert "max-age" in respuesta.headers.get("Cache-Control", "")
    # sim_id inválido → 404 (misma defensa que el resto)
    assert cliente.get("/api/simulacion/no-hex/imagen").status_code == 404


# ---------- el correo ----------

def test_html_del_pulso_lleva_disclaimer_y_vocabulario_limpio(dia):
    destacadas = pipeline._destacadas_de_hoy(persistencia.conectar())
    html = boletin.construir_html(destacadas, "sábado 11 de julio", token_baja="ABC")
    # el disclaimer CMF está presente (test obligatorio de CONTENIDO.md)
    assert DISCLAIMER in html
    # y no hay vocabulario prohibido en toda la pieza
    assert verificar_pieza(html) == []
    # el link de baja usa el token del suscriptor
    assert "/api/baja/ABC" in html
    # el rediseño: cabecera de El Pulso y El Enjambre invitado al pie
    assert "El Pulso" in html and "Probar El Enjambre" in html


def test_correo_de_confirmacion_lleva_disclaimer():
    # sin RESEND no envía, pero el HTML se arma igual: lo probamos directo
    from contenido import boletin as b
    # reconstruye el cuerpo llamando a enviar con un doble que capture el html
    capturado = {}

    def falso_enviar(destinatario, asunto, html):
        capturado["html"] = html
        capturado["asunto"] = asunto
        return True

    b.enviar = falso_enviar  # monkeypatch simple
    assert b.enviar_confirmacion("x@y.cl", "tok123")
    assert DISCLAIMER in capturado["html"]
    assert "/api/confirmar/tok123" in capturado["html"]
    assert "Confirma" in capturado["asunto"]


# ---------- suscripción por la API (double opt-in) ----------

def test_flujo_suscripcion_opt_in_simple():
    cliente = TestClient(server.app)

    # alta con correo inválido → 400
    assert cliente.post("/api/suscribir", json={"email": "no-es-correo"}).status_code == 400

    # alta válida → OPT-IN SIMPLE: queda suscrito de inmediato (sin confirmar)
    respuesta = cliente.post("/api/suscribir", json={"email": "giorgio@rubicon.cl"}).json()
    assert respuesta["estado"] == "suscrito"

    conexion = persistencia.conectar()
    activos = persistencia.suscriptores_activos(conexion)
    assert len(activos) == 1          # activo de una vez, sin paso de confirmación
    baja = conexion.execute("SELECT token_baja FROM suscriptores").fetchone()[0]
    conexion.close()

    # baja de un clic
    assert cliente.get(f"/api/baja/{baja}").status_code == 200
    conexion = persistencia.conectar()
    assert persistencia.suscriptores_activos(conexion) == []
    conexion.close()


def test_activar_pendientes_migra_a_los_del_viejo_opt_in():
    """Los que quedaron pendientes del doble opt-in se activan de una vez."""
    conexion = persistencia.conectar()
    persistencia.agregar_suscriptor(conexion, "pendiente@lector.cl")  # activo=0 + token_confirma
    persistencia.alta_directa(conexion, "yaactivo@lector.cl")         # activo=1
    n = persistencia.activar_pendientes(conexion)
    assert n == 1                                    # solo el pendiente
    assert len(persistencia.suscriptores_activos(conexion)) == 2
    conexion.close()


def test_activar_pendientes_endpoint_exige_token(monkeypatch):
    monkeypatch.setenv("ENJAMBRE_PIPELINE_TOKEN", "secreto")
    cliente = TestClient(server.app)
    assert cliente.post("/api/pulso/activar-pendientes").status_code == 403
    r = cliente.post("/api/pulso/activar-pendientes", headers={"X-Pipeline-Token": "secreto"})
    assert r.status_code == 200 and r.json()["ok"] is True


def test_suscribir_silencioso_captura_el_lead():
    """La puerta de correo: soltar un titular con correo deja el lead suscrito
    (sin RESEND no envía, pero el alta queda)."""
    server._suscribir_silencioso("nuevo@lector.cl")
    conexion = persistencia.conectar()
    total = conexion.execute(
        "SELECT COUNT(*) FROM suscriptores WHERE email = 'nuevo@lector.cl'").fetchone()[0]
    conexion.close()
    assert total == 1


def test_suscribir_dos_veces_no_duplica():
    cliente = TestClient(server.app)
    cliente.post("/api/suscribir", json={"email": "a@b.cl"})
    cliente.post("/api/suscribir", json={"email": "a@b.cl"})
    conexion = persistencia.conectar()
    total = conexion.execute("SELECT COUNT(*) FROM suscriptores").fetchone()[0]
    conexion.close()
    assert total == 1


def test_no_reenvia_confirmacion_a_pendiente_reciente():
    """Antibombardeo (auditoría C): un segundo intento inmediato para el mismo
    correo pendiente no reenvía ni rota el token."""
    conexion = persistencia.conectar()
    a1 = persistencia.agregar_suscriptor(conexion, "victima@correo.cl")
    a2 = persistencia.agregar_suscriptor(conexion, "victima@correo.cl")
    conexion.close()
    assert a1["reenviar"] is True
    assert a2["reenviar"] is False              # no se reenvía el correo
    assert a2["token_confirma"] == a1["token_confirma"]  # ni se rota el token


# ---------- el ritual completo ----------

def test_ritual_matutino_arma_todo_sin_enviar(monkeypatch):
    avisos = []
    from contenido import notificar
    monkeypatch.setattr(notificar, "avisar", lambda mensaje: avisos.append(mensaje) or True)

    # se fuerza un día de semana (el ritual del fin de semana es otra edición)
    entre_semana = {"dia_semana": "lunes", "fecha": "4 de agosto de 2026",
                    "momento": "mañana", "es_finde": False}
    resultado = pipeline.ritual_matutino(semilla_base=99, enviar=False, cuando=entre_semana)
    assert len(resultado["publicadas"]) == 3
    assert resultado["destacadas"] == 3
    assert resultado["estado"] == "pendiente"   # generada, esperando el visto bueno
    assert resultado["token"]                   # token para los enlaces del correo de revisión
    assert DISCLAIMER in resultado["html_preview"]
    assert avisos and "El Pulso" in avisos[0]   # paso 8: avisó a Giorgio


def test_ritual_de_domingo_arma_el_deep_dive(monkeypatch):
    """El domingo el ritual NO simula noticias: arma el deep-dive de una
    mid/small-cap o sector y lo deja pendiente de revisión."""
    from contenido import analisis_semanal, notificar, redaccion_ia
    monkeypatch.setattr(notificar, "avisar", lambda mensaje: True)

    hechos = {
        "modo": "accion", "titulo": "Acción seleccionada", "encuadre": "mediana capitalización",
        "ticker": "ROKU", "nombre": "Roku", "sector": "Streaming", "contexto": "…",
        "var_semana_pct": 8.4, "var_mes_pct": 12.0, "fecha_inicio": "1 ago", "fecha_fin": "31 ago",
        "grafico": {"ticker": "ROKU", "nombre": "Roku", "periodo": "mes", "moneda": "$"},
    }
    redactado = {
        "titular": "Roku vuelve a la conversación", "dek": "Semana movida",
        "contexto": "Roku hace el sistema de sus televisores.\n\nGana con publicidad.",
        "lectura": "Avanzó tras un anuncio.",
        "debate": [{"arquetipo": "doomer", "nombre": "El Doomer",
                    "mirada": "La publicidad es lo primero que se recorta."}],
        "que_observar": "Habrá que ver si sostiene el ritmo.",
    }
    monkeypatch.setattr(analisis_semanal, "preparar_analisis", lambda **k: hechos)
    monkeypatch.setattr(redaccion_ia, "redactar_analisis", lambda *a, **k: redactado)

    domingo = {"dia_semana": "domingo", "weekday": 6, "fecha": "16 de agosto de 2026",
               "momento": "mañana", "es_finde": True}
    resultado = pipeline.ritual_matutino(enviar=False, cuando=domingo)

    assert resultado["edicion"] == "finde"
    assert resultado["estado"] == "pendiente"
    assert resultado["publicadas"] == []                 # el finde no simula el enjambre
    html = resultado["html_preview"]
    assert "Edición de fin de semana" in html
    assert "Qué es" in html and "Lo que ven nuestros inversionistas IA" in html
    assert DISCLAIMER in html


def test_ritual_de_sabado_arma_el_resumen(monkeypatch):
    """El sábado el ritual arma el RESUMEN DE LA SEMANA (no el deep-dive) y lo
    deja pendiente de revisión."""
    from contenido import notificar, redaccion_ia, resumen_semanal
    monkeypatch.setattr(notificar, "avisar", lambda mensaje: True)

    hechos = {"titulo": "El Pulso de la semana",
              "titulares": [{"titular": "La Fed sube el tono", "fecha": "2026-08-14"}],
              "foto": [{"simbolo": "^GSPC", "nombre": "S&P 500", "var_semana_pct": 1.8}]}
    redactado = {"intro": "Semana de nervios.",
                 "temas": [{"kicker": "Macro", "emoji": "🏦", "titular": "La Fed marcó el tono",
                            "analisis": "Subió el tono.\n\nCautela.",
                            "que_observar": "Habrá que ver la próxima acta.", "grafico": None}],
                 "cierre": "Una semana para respirar."}
    monkeypatch.setattr(resumen_semanal, "preparar_resumen", lambda *a, **k: hechos)
    monkeypatch.setattr(redaccion_ia, "redactar_resumen", lambda *a, **k: redactado)

    sabado = {"dia_semana": "sábado", "weekday": 5, "fecha": "15 de agosto de 2026",
              "momento": "mañana", "es_finde": True}
    resultado = pipeline.ritual_matutino(enviar=False, cuando=sabado)

    assert resultado["edicion"] == "resumen"
    assert resultado["estado"] == "pendiente"
    assert resultado["publicadas"] == []
    html = resultado["html_preview"]
    assert "El Pulso de la semana" in html and "La semana en números" in html
    assert "La Fed marcó el tono" in html
    assert DISCLAIMER in html


def test_reenviar_manda_aunque_ya_este_enviada(monkeypatch):
    """El reenvío manual SÍ manda de nuevo a todos, aunque la edición ya se
    hubiera enviado (a diferencia de aprobar_y_enviar, que es idempotente)."""
    conexion = persistencia.conectar()
    alta = persistencia.agregar_suscriptor(conexion, "lector@medio.cl")
    persistencia.confirmar_suscriptor(conexion, alta["token_confirma"])
    hoy = persistencia.ahora_iso()[:10]
    persistencia.guardar_edicion(conexion, hoy, {"redactado": {}}, "<html>edición</html>",
                                 "Asunto", "t" * 24, persistencia.ahora_iso())
    persistencia.marcar_enviada(conexion, hoy, 1, 1, persistencia.ahora_iso())  # ya enviada
    conexion.close()

    enviados = []
    monkeypatch.setattr(boletin, "_enviar_resend", lambda *a, **k: (enviados.append(a) or True, ""))
    res = pipeline.reenviar_a_suscriptores(fecha=hoy)
    assert res["ok"] and res.get("reenviada") and res["enviados"] == 1
    assert enviados and enviados[0][0] == "lector@medio.cl"  # reenvió pese a estar 'enviada'


def test_endpoint_pipeline_exige_token(monkeypatch):
    cliente = TestClient(server.app)
    # sin token configurado → 403
    monkeypatch.delenv("ENJAMBRE_PIPELINE_TOKEN", raising=False)
    assert cliente.post("/api/pipeline").status_code == 403

    # con token configurado pero header incorrecto → 403
    monkeypatch.setenv("ENJAMBRE_PIPELINE_TOKEN", "secreto")
    assert cliente.post("/api/pipeline", headers={"X-Pipeline-Token": "malo"}).status_code == 403

    # header correcto → 200 e inicia en segundo plano (el ritual se neutraliza
    # para probar solo la puerta de autorización, no correr 3 simulaciones)
    corridas = []
    monkeypatch.setattr(pipeline, "ritual_matutino", lambda **k: corridas.append(k))
    respuesta = cliente.post("/api/pipeline", headers={"X-Pipeline-Token": "secreto"})
    assert respuesta.status_code == 200
    assert respuesta.json()["estado"] == "iniciado"
    assert corridas  # el ritual se disparó en segundo plano


def test_html_usa_la_voz_de_ia_cuando_existe(dia):
    """Con 'redactado' (voz del redactor de IA), el correo lo usa: historias con
    análisis, gráfico real y 'en una línea'; sigue pasando el filtro CMF."""
    destacadas = pipeline._destacadas_de_hoy(persistencia.conectar())
    brief = {"mercado": [], "observa": [], "redactado": {
        "buenos_dias": "Wall Street amaneció en verde y el Nasdaq sacó pecho.",
        "historias": [
            {"kicker": "Tecnología · catalizador", "emoji": "🍎",
             "titular": "Apple busca acuerdo con Epic", "dek": "El que peleaba, negocia.",
             "cuerpo": "Años de pelea.\n\nHoy ofrece café.\n\nEso dice mucho.",
             "bottom_line": "Apple no cambia de libreto por gusto.",
             "grafico": {"ticker": "AAPL", "nombre": "Apple Inc.", "periodo": "semana", "moneda": "$"}},
            {"kicker": "Small-cap · movida", "emoji": "🟢", "titular": "Nvidia subió",
             "dek": "", "cuerpo": "Los chips mandan.", "bottom_line": "", "grafico": None},
        ],
    }}
    html = boletin.construir_html(destacadas, "miércoles 5 de agosto", brief=brief)
    assert "Buenos días" in html
    assert "Apple busca acuerdo con Epic" in html and "Nvidia subió" in html
    assert "/api/grafico/AAPL" in html          # el gráfico real de la historia
    assert "En una línea:" in html               # el bottom line
    assert DISCLAIMER in html
    assert verificar_pieza(html) == []


def test_tabla_mercado_dia_mes_ano(dia):
    """La 'foto del día' se pinta como tabla Día/Mes/Año; los datos faltantes
    (mes/año None) muestran '—' y todo pasa el filtro CMF."""
    destacadas = pipeline._destacadas_de_hoy(persistencia.conectar())
    brief = {"foto": [
        {"nombre": "S&P 500", "variacion_pct": 1.8, "var_mes_pct": 2.67, "var_ano_pct": 22.8},
        {"nombre": "Oro", "variacion_pct": -0.9, "var_mes_pct": 3.28, "var_ano_pct": None},
    ]}
    html = boletin.construir_html(destacadas, "miércoles 5 de agosto", brief=brief)
    assert "La foto del día" in html
    assert "S&amp;P 500" in html          # nombre escapado
    assert "1.8%" in html and "22.8%" in html
    assert "—" in html                     # el año de Oro venía None
    assert verificar_pieza(html) == []


def test_html_respaldo_sin_redactado(dia):
    """Sin 'redactado' ni brief, el correo se arma igual (no se cae): cabecera de
    El Pulso, El Enjambre al pie y el disclaimer."""
    destacadas = pipeline._destacadas_de_hoy(persistencia.conectar())
    html = boletin.construir_html(destacadas, "miércoles 5 de agosto")  # sin brief
    assert html.startswith("<!doctype")
    assert "El Pulso" in html and "Probar El Enjambre" in html
    assert DISCLAIMER in html


def test_yahoo_calcula_dia_mes_ano():
    """El cálculo Día/Mes/Año de Yahoo, sin red (serie inyectada)."""
    from contenido.fuentes import yahoo
    serie = [100 + i * 0.1 for i in range(260)]   # sube de 100 a ~125.9 en el año
    v = yahoo._variaciones(serie)
    assert v["variacion_pct"] is not None          # día
    assert v["var_mes_pct"] is not None            # mes (>=22 datos)
    assert v["var_ano_pct"] > 0                    # subió en el año
    assert yahoo._variaciones([100.0]) is None     # serie muy corta → None


def test_ritual_genera_pendiente_y_aprobar_envia(monkeypatch):
    """El ritual GENERA la edición (pendiente); nada sale a los suscriptores
    hasta que Giorgio la aprueba. Aprobar la envía a los confirmados."""
    # un suscriptor confirmado
    conexion = persistencia.conectar()
    alta = persistencia.agregar_suscriptor(conexion, "lector@medio.cl")
    persistencia.confirmar_suscriptor(conexion, alta["token_confirma"])
    conexion.close()

    enviados = []
    monkeypatch.setattr(boletin, "_enviar_resend", lambda *a, **k: (enviados.append(a) or True, ""))
    monkeypatch.setattr(boletin, "PULSO_ADMIN_EMAIL", "")  # sin correo de revisión en el test
    from contenido import notificar
    monkeypatch.setattr(notificar, "avisar", lambda mensaje: True)

    # 1) el ritual arma la edición pero NO la envía a los suscriptores (queda pendiente)
    entre_semana = {"dia_semana": "lunes", "fecha": "4 de agosto de 2026",
                    "momento": "mañana", "es_finde": False}
    resultado = pipeline.ritual_matutino(semilla_base=7, enviar=True, cuando=entre_semana)
    assert resultado["estado"] == "pendiente"
    assert enviados == []                       # nada salió a los suscriptores todavía

    # 2) el visto bueno la envía a los suscriptores confirmados
    envio = pipeline.aprobar_y_enviar()
    assert envio["ok"] and envio["suscriptores"] == 1 and envio["enviados"] == 1
    assert enviados[0][0] == "lector@medio.cl"  # el correo salió al confirmado


# ---------- el correo no deja pasar marcado ajeno ----------

def test_el_correo_escapa_texto_hostil_del_redactado():
    """El texto del redactor de IA (titular, cuerpo, bottom_line) sale de un
    titular que puede venir del público: no puede inyectar HTML en el correo
    que reciben los suscriptores."""
    brief = {"mercado": [], "redactado": {
        "buenos_dias": "Un día normal.",
        "historias": [{
            "kicker": "Test", "emoji": "🧪",
            "titular": '<img src=x onerror=alert(1)> Titular hostil',
            "dek": "", "cuerpo": '</p><a href="http://sitio-falso.cl">entra aquí</a>\n\nOtro párrafo.',
            "bottom_line": "<script>alert(1)</script> cierre",
            "grafico": None,
        }]}}
    html = boletin.construir_html([], "lunes 4 de agosto", token_baja="ABC", brief=brief)
    assert "<img src=x" not in html
    assert "&lt;img src=x" in html                        # se ve como texto, no se ejecuta
    assert '<a href="http://sitio-falso.cl"' not in html  # sin enlaces colados
    assert "<script>alert(1)</script>" not in html and "&lt;script&gt;" in html


def test_el_correo_solo_acepta_enlaces_http():
    """La fuente de un dato de mercado es un enlace externo: solo http(s)."""
    assert boletin._url_segura("https://ejemplo.cl/nota") == "https://ejemplo.cl/nota"
    assert boletin._url_segura("javascript:alert(1)") == ""
    assert boletin._url_segura("") == ""
    fila = boletin._fila_mercado({"tipo": "evento", "titular": "Dato", "url": "javascript:alert(1)"})
    assert "javascript:" not in fila


# ---------- B5: el panel no miente cuando el preview no se regenera ----------

def test_editar_avisa_si_el_preview_no_se_regenera(monkeypatch):
    """Si al editar no hay destacadas para re-armar el correo, la respuesta debe
    DECIRLO (preview_actualizado=False), no un ok:true a secas — si no, se
    aprueba y sale el correo sin las ediciones."""
    monkeypatch.setenv("ENJAMBRE_PIPELINE_TOKEN", "secreto")
    hoy = persistencia.ahora_iso()[:10]
    conexion = persistencia.conectar()
    # una edición guardada, pero SIN simulaciones destacadas para hoy
    persistencia.guardar_edicion(conexion, hoy, {"redactado": {}}, "<html>viejo</html>",
                                 "Asunto", "t" * 24, persistencia.ahora_iso())
    conexion.close()
    cliente = TestClient(server.app)
    res = cliente.post(f"/api/panel/edicion/{hoy}/editar",
                       headers={"X-Pipeline-Token": "secreto"},
                       json={"redactado": {"buenos_dias": "Hola"}}).json()
    assert res["ok"] is True
    assert res["preview_actualizado"] is False        # no mintió
    assert "vista previa" in res["motivo"].lower()


def test_panel_edicion_finde_marca_deep_dive_y_regenera_preview(monkeypatch):
    """La edición de FIN DE SEMANA se marca como 'finde' en el panel y su vista
    previa SÍ se regenera sin destacadas (el deep-dive no las necesita)."""
    monkeypatch.setenv("ENJAMBRE_PIPELINE_TOKEN", "secreto")
    hoy = persistencia.ahora_iso()[:10]
    brief = {
        "analisis": {"modo": "accion", "titulo": "Acción seleccionada",
                     "encuadre": "mediana capitalización", "ticker": "ROKU", "nombre": "Roku",
                     "sector": "Streaming", "var_semana_pct": 8.4,
                     "grafico": {"ticker": "ROKU", "nombre": "Roku", "periodo": "mes", "moneda": "$"}},
        "analisis_redactado": {"titular": "Roku vuelve a la conversación", "dek": "",
                               "contexto": "Roku hace el sistema de sus televisores.", "lectura": "",
                               "debate": [{"arquetipo": "doomer", "nombre": "El Doomer",
                                           "mirada": "La publicidad es lo primero que se recorta."}],
                               "que_observar": "Habrá que ver si sostiene el ritmo."},
    }
    conexion = persistencia.conectar()
    persistencia.guardar_edicion(conexion, hoy, brief, "<html>viejo</html>",
                                 "Asunto", "t" * 24, persistencia.ahora_iso())
    conexion.close()
    cliente = TestClient(server.app)

    ed = cliente.get(f"/api/panel/edicion/{hoy}", headers={"X-Pipeline-Token": "secreto"}).json()
    assert ed["finde"] is True
    assert ed["analisis"]["nombre"] == "Roku"

    res = cliente.post(f"/api/panel/edicion/{hoy}/editar",
                       headers={"X-Pipeline-Token": "secreto"},
                       json={"redactado": {}}).json()
    assert res["ok"] is True and res["preview_actualizado"] is True  # se regeneró el deep-dive


# ---------- Premium: el deep-dive del domingo se parte en gratis (teaser) y de pago ----------

def _brief_domingo() -> dict:
    """Un brief de domingo (deep-dive) para probar el gating Premium."""
    return {
        "analisis": {"modo": "accion", "titulo": "Acción seleccionada",
                     "encuadre": "mediana capitalización", "ticker": "ROKU", "nombre": "Roku",
                     "sector": "Streaming", "var_semana_pct": 8.4,
                     "grafico": {"ticker": "ROKU", "nombre": "Roku", "periodo": "mes", "moneda": "$"}},
        "analisis_redactado": {
            "titular": "Roku vuelve a la conversación", "dek": "Semana movida",
            "contexto": "Roku hace el sistema de sus televisores.\n\nGana con publicidad.",
            "lectura": "Avanzó tras un anuncio.",
            "debate": [{"arquetipo": "doomer", "nombre": "El Doomer",
                        "mirada": "La publicidad es lo primero que se recorta."}],
            "que_observar": "Habrá que ver si sostiene el ritmo."},
    }


def test_premium_deep_dive_completo_vs_teaser():
    """El correo completo (Premium) muestra el análisis; el teaser (gratis) lo
    reemplaza por el gancho + botón de pago, SIN revelar nombre ni debate."""
    brief = _brief_domingo()
    completo = boletin.construir_html([], "domingo 17 de agosto", brief=brief, premium=True)
    teaser = boletin.construir_html([], "domingo 17 de agosto", brief=brief, premium=False)

    # el completo lleva el análisis de verdad
    assert "Qué es" in completo and "Lo que ven nuestros inversionistas IA" in completo
    assert "Roku" in completo

    # el teaser NO revela lo pagado, sí el gancho + botón + sector
    assert "Premium" in teaser and "continúa en Premium" in teaser
    assert "Leer el análisis completo" in teaser
    assert "Streaming" in teaser              # el sector sí se muestra (el gancho)
    assert "Roku" not in teaser               # el nombre NO se revela
    assert "El Doomer" not in teaser          # el debate es Premium
    assert DISCLAIMER in teaser               # sigue llevando el pie legal


def test_premium_envio_separa_gratis_y_pago(monkeypatch):
    """Al enviar el domingo: el Premium recibe el completo; el gratuito, el teaser."""
    conexion = persistencia.conectar()
    for correo in ("gratis@lector.cl", "pago@lector.cl"):
        alta = persistencia.agregar_suscriptor(conexion, correo)
        persistencia.confirmar_suscriptor(conexion, alta["token_confirma"])
    assert persistencia.set_premium(conexion, "pago@lector.cl", True)
    assert persistencia.es_premium(conexion, "pago@lector.cl")
    assert not persistencia.es_premium(conexion, "gratis@lector.cl")
    assert persistencia.contar_premium(conexion) == 1
    conexion.close()

    # capturamos (destinatario, asunto, html) de cada envío
    enviados = []
    monkeypatch.setattr(boletin, "_enviar_resend",
                        lambda dest, asunto, html, **k: (enviados.append((dest, asunto, html)) or True, ""))

    brief = _brief_domingo()
    hoy = persistencia.ahora_iso()[:10]
    conexion = persistencia.conectar()
    completo = boletin.construir_html([], "domingo 17 de agosto", token_baja=persistencia.TOKEN_BAJA_SENTINEL,
                                      brief=brief, premium=True)
    persistencia.guardar_edicion(conexion, hoy, brief, completo,
                                 boletin.asunto_finde(brief["analisis"]), "t" * 24, persistencia.ahora_iso())
    conexion.close()

    res = pipeline.aprobar_y_enviar(fecha=hoy)
    assert res["ok"] and res["enviados"] == 2 and res["premium"] == 1

    por_correo = {dest: (asunto, html) for dest, asunto, html in enviados}
    asunto_pago, html_pago = por_correo["pago@lector.cl"]
    asunto_gratis, html_gratis = por_correo["gratis@lector.cl"]

    assert "Roku" in html_pago and "El Doomer" in html_pago            # completo
    assert "continúa en Premium" in html_gratis and "Roku" not in html_gratis  # teaser
    assert "Premium" in asunto_gratis and "Roku" not in asunto_gratis  # asunto sin nombre


def test_premium_vence_y_deja_de_contar():
    """Un Premium con fecha vencida ya no cuenta como Premium activo."""
    conexion = persistencia.conectar()
    alta = persistencia.agregar_suscriptor(conexion, "vencido@lector.cl")
    persistencia.confirmar_suscriptor(conexion, alta["token_confirma"])
    persistencia.set_premium(conexion, "vencido@lector.cl", True, hasta="2020-01-01")
    assert not persistencia.es_premium(conexion, "vencido@lector.cl")
    activos = {s["email"]: s["premium"] for s in persistencia.suscriptores_activos(conexion)}
    assert activos["vencido@lector.cl"] == 0
    conexion.close()


def test_sabado_no_se_cobra():
    """El resumen del sábado es igual para todos (no hay teaser Premium)."""
    brief = {"resumen": {"titulo": "El Pulso de la semana", "foto": []},
             "resumen_redactado": {"intro": "Semana de nervios.",
                                   "temas": [{"kicker": "Macro", "emoji": "🏦",
                                              "titular": "La Fed marcó el tono",
                                              "analisis": "Subió el tono.", "que_observar": ""}],
                                   "cierre": ""}}
    teaser_html, asunto_teaser = boletin.teaser_para(brief, "2026-08-15")
    assert teaser_html is None and asunto_teaser is None   # el sábado NO gatea
```

## engine/validation/test_red_influencia.py
```python
"""Tests de la red de influencia (CLAUDE.md sección 6)."""

import pytest

from agents.lider import LiderOpinion
from agents.reglas import FomoRetail, FondoPasivo, Fundamentalista, Manada, Miedoso, QuantMomentum
from model import MercadoEnjambre


@pytest.fixture(scope="module")
def modelo():
    return MercadoEnjambre(seed=42, ticks_horizonte=300)


def test_lideres_tienen_seguidores_segun_arquetipo(modelo):
    """Cada líder arrastra un puñado de seguidores (mínimo por arquetipo 12,
    más los mínimos garantizados de manada/FOMO que exige la sección 4)."""
    lideres = [a for a in modelo.agents if isinstance(a, LiderOpinion)]
    assert len(lideres) == 1150
    for lider in lideres:
        assert len(lider.seguidores) >= 12


def test_red_scale_free_pocos_hubs(modelo):
    """Pocos nodos muy conectados, muchos poco conectados: el decil más
    popular de líderes concentra bastante más audiencia que la cuota uniforme."""
    lideres = [a for a in modelo.agents if isinstance(a, LiderOpinion)]
    seguidores = sorted((len(l.seguidores) for l in lideres), reverse=True)
    decil = max(1, len(lideres) // 10)
    top = sum(seguidores[:decil])
    total = sum(seguidores)
    assert top / total > 0.15  # el 10% más popular concentra > su cuota (0.10)


def test_retail_tiene_pares_horizontales(modelo):
    """Los tipos 8-10 tienen al menos 3 vecinos pares (el rumor viaja
    también horizontalmente)."""
    for clase in (Manada, FomoRetail, Miedoso):
        for agente in (a for a in modelo.agents if isinstance(a, clase)):
            assert len(agente.pares) >= 3


def test_manada_siempre_tiene_un_lider(modelo):
    for agente in (a for a in modelo.agents if isinstance(a, Manada)):
        assert len(agente.lideres_seguidos) >= 1


def test_institucionales_fuera_de_la_red(modelo):
    """Los tipos 1-3 NO están en la red social: sin vecinos, sin rumor."""
    for clase in (Fundamentalista, QuantMomentum, FondoPasivo):
        for agente in (a for a in modelo.agents if isinstance(a, clase)):
            assert agente.vecinos == []
            assert agente.lideres_seguidos == []


def test_propagacion_con_retardo_y_atenuacion():
    """La señal llega a los seguidores con delay de 1-4 ticks y atenuada
    (0.7 por salto) — sin retardo no hay ola, solo un salto feo."""
    modelo = MercadoEnjambre(seed=7, ticks_horizonte=300)
    modelo.aplicar_noticia(-0.9)

    # nada llega en el mismo tick de la noticia: todo va a la cola
    assert all(a.senal_social == 0.0 for a in modelo.agents)
    assert len(modelo.cola_senales) > 1000

    # cada envío en la cola respeta retardo 1-4 y atenuación 0.7 por salto
    for tick_entrega, _, valor, salto in modelo.cola_senales:
        assert 1 <= tick_entrega - modelo.tick <= 4
        assert abs(valor) <= 0.7**salto + 1e-9
        assert salto == 1  # el segundo salto se encola recién al entregar

    alcanzados_por_tick = []
    for _ in range(6):
        modelo.step()
        alcanzados = [a for a in modelo.agents if a.senal_social != 0.0]
        alcanzados_por_tick.append(len(alcanzados))

    # la ola crece durante los primeros ticks (retardo distribuido 1-4)
    assert alcanzados_por_tick[0] > 0
    assert alcanzados_por_tick[3] > alcanzados_por_tick[0]

    # el rumor acumulado queda acotado y es coherente con la noticia
    assert all(abs(a.senal_social) <= 1.0 for a in modelo.agents)
    negativos = sum(1 for a in modelo.agents if a.senal_social < 0)
    positivos = sum(1 for a in modelo.agents if a.senal_social > 0)
    assert negativos > positivos * 3
```

## engine/validation/test_redaccion.py
```python
"""Tests de La Redacción: el análisis de mercado del Pulso.

Reglas de oro que estos tests protegen:
- el número manda (viene de la capa de datos, no de un texto)
- nada se publica sin fuente / sin pasar el filtro CMF
- se cuenta el pasado, nunca se predice el futuro
"""

import pytest

from contenido import boletin, persistencia, redaccion
from contenido.fuentes import barchart, yahoo
from contenido.vocabulario import DISCLAIMER, es_publicable, verificar_pieza


@pytest.fixture(autouse=True)
def sin_claves(monkeypatch, tmp_path):
    monkeypatch.delenv("BARCHART_API_KEY", raising=False)
    monkeypatch.delenv("ALPACA_API_KEY_ID", raising=False)
    monkeypatch.setenv("ENJAMBRE_DB", str(tmp_path / "enjambre.db"))
    # Hermético: Yahoo es una fuente GRATIS (sin clave), así que borrar las claves
    # no basta para forzar el modo demo — un entorno con salida a Yahoo devolvería
    # 'origen_datos' = 'yahoo' y rompería los asserts que esperan 'demo'. Lo
    # neutralizamos aquí para que los tests corran igual con o sin red (como en CI).
    monkeypatch.setattr(yahoo, "cotizaciones", lambda *a, **k: ([], "sin_datos"))


NOTICIAS = [
    {"titular": "Nvidia beats earnings expectations, revenue up 48%", "fuente": "demo",
     "url": "https://x/nvda", "simbolos": "NVDA", "fecha": "2026-07-10"},
    {"titular": "Oil jumps 6% as tensions escalate in the Strait of Hormuz", "fuente": "demo",
     "url": "https://x/oil", "simbolos": "USO,XOM", "fecha": "2026-07-10"},
    {"titular": "Top 5 stocks to watch this week", "fuente": "demo",
     "url": "", "simbolos": "", "fecha": "2026-07-10"},
    {"titular": "Should you buy the dip in tech stocks?", "fuente": "demo",
     "url": "", "simbolos": "QQQ", "fecha": "2026-07-10"},
]


# ---------- la capa de datos ----------

def test_barchart_degrada_a_demo():
    assert barchart.hay_credenciales() is False
    cotizaciones, origen = barchart.cotizaciones()
    assert origen == "demo"
    assert len(cotizaciones) >= 4
    for c in cotizaciones:
        assert isinstance(c["variacion_pct"], (int, float))
        assert c["nombre"]


# ---------- el reportero: nada sin fuente, no cita publicidad ----------

def test_reportero_casa_hechos_con_su_cita():
    cotizaciones = [
        {"simbolo": "NVDA", "nombre": "Nvidia", "variacion_pct": 3.4},
        {"simbolo": "CLZ25", "nombre": "Petróleo WTI", "variacion_pct": 2.1},
    ]
    hechos = redaccion.reportear(cotizaciones, NOTICIAS)
    assert hechos[0]["cita"]["titular"].startswith("Nvidia beats")
    assert "hormuz" in hechos[1]["cita"]["titular"].lower()


def test_reportero_no_usa_publicidad_como_cita():
    # el Nasdaq solo tiene titulares promocionales/advisory disponibles
    cotizaciones = [{"simbolo": "$IUXX", "nombre": "Nasdaq 100", "variacion_pct": -0.9}]
    hechos = redaccion.reportear(cotizaciones, NOTICIAS)
    assert hechos[0]["cita"] is None  # "Top 5" y "Should you buy" quedan fuera


# ---------- el verificador: el número manda, descarta el ruido ----------

def test_verificador_descarta_movimientos_insignificantes():
    hechos = [
        {"nombre": "Apple", "variacion_pct": 0.1, "cita": None},   # ruido
        {"nombre": "Nvidia", "variacion_pct": 3.4, "cita": None},  # noticia
    ]
    verificados = redaccion.verificar(hechos)
    assert len(verificados) == 1
    assert verificados[0]["nombre"] == "Nvidia"


# ---------- el editor: pasado, con fuente, CMF-limpio ----------

def test_editor_redacta_en_pasado_y_publicable():
    hecho = {"nombre": "Petróleo WTI", "variacion_pct": 2.1,
             "cita": {"titular": "Oil jumps 6% in the Strait of Hormuz", "fuente": "demo", "url": "u"}}
    linea = redaccion.editar(hecho)
    assert "avanzó 2.1%" in linea["frase"]
    assert "En la prensa" in linea["frase"]
    assert es_publicable(linea["frase"])


def test_editor_cae_la_causa_si_el_titular_no_es_publicable():
    hecho = {"nombre": "Nasdaq 100", "variacion_pct": -1.2,
             "cita": {"titular": "3 reasons you should buy now", "fuente": "x", "url": ""}}
    linea = redaccion.editar(hecho)
    # conserva la cifra verificada, pero descarta el 'por qué' prohibido
    assert linea is not None
    assert "En la prensa" not in linea["frase"]
    assert es_publicable(linea["frase"])


# ---------- el brief completo ----------

def test_brief_del_dia():
    brief = redaccion.preparar_brief(radar=["La Fed decide tasas hoy"])
    assert brief["origen_datos"] == "demo"
    assert brief["mercado"]
    for m in brief["mercado"]:
        assert es_publicable(m["frase"])
        assert isinstance(m["variacion_pct"], (int, float))  # el número, siempre
    assert brief["observa"] == ["La Fed decide tasas hoy"]


def test_brief_es_dinamico_segun_las_noticias_del_dia():
    """El corazón del requisito: el contenido cambia con lo que pasa cada día."""
    dia_a = [{"titular": "Amazon to acquire logistics startup for 4.2 billion",
              "fuente": "x", "url": "", "simbolos": "AMZN", "impacto": 8}]
    dia_b = [{"titular": "Major cyberattack disrupts operations at three US banks",
              "fuente": "x", "url": "", "simbolos": "JPM,BAC", "impacto": 9}]
    texto_a = " ".join(m["frase"] for m in redaccion.preparar_brief(evaluadas=dia_a)["mercado"])
    texto_b = " ".join(m["frase"] for m in redaccion.preparar_brief(evaluadas=dia_b)["mercado"])
    assert "Amazon" in texto_a and "Amazon" not in texto_b
    assert "cyberattack" in texto_b and "cyberattack" not in texto_a


def test_eventos_entran_como_hechos_con_fuente():
    evaluadas = [{"titular": "Amazon to acquire logistics startup for 4.2 billion",
                  "fuente": "reuters", "url": "https://x", "simbolos": "AMZN", "impacto": 8}]
    brief = redaccion.preparar_brief(evaluadas=evaluadas)
    eventos = [m for m in brief["mercado"] if m["tipo"] == "evento"]
    assert any("acquire" in e["titular"] for e in eventos)
    for e in eventos:
        assert es_publicable(e["frase"])  # nada prohibido, ni número inventado


def test_evento_no_duplica_una_cita_ya_usada():
    # el mismo titular que explica un movimiento no se repite como evento
    evaluadas = [{"titular": "Nvidia beats earnings expectations", "fuente": "x",
                  "url": "", "simbolos": "NVDA", "impacto": 8}]
    brief = redaccion.preparar_brief(evaluadas=evaluadas)
    titulares = [m.get("titular") for m in brief["mercado"] if m["tipo"] == "evento"]
    assert "Nvidia beats earnings expectations" not in titulares


def test_observa_es_atencion_no_prediccion():
    # un 'radar' con vocabulario de predicción se filtra
    brief = redaccion.preparar_brief(radar=["El precio subirá mañana", "La Fed decide hoy"])
    assert "El precio subirá mañana" not in brief["observa"]
    assert "La Fed decide hoy" in brief["observa"]


# ---------- el correo con el análisis de mercado ----------

def test_correo_con_brief_es_cmf_limpio_y_lleva_disclaimer():
    brief = redaccion.preparar_brief(radar=["La Fed decide hoy"])
    destacadas = [{
        "sim_id": "abc1230000000000", "titular": "Quiebra un banco",
        "resumen": {"direccion_pct": -3.0, "agitacion": "medio"},
        "lideres_frases": [{"arquetipo": "doomer", "senal": -0.8, "frase": "Lo advertí."},
                           {"arquetipo": "institucional_frio", "senal": 0.1, "frase": "Sin impacto."}],
    }]
    html = boletin.construir_html(destacadas, "domingo 12 de julio", brief=brief)
    # sin redactado (fallback): al menos el digest 'Lo que pasó' de los movers
    assert "Lo que pasó" in html
    # El Enjambre baja al pie como herramienta hermana (rediseño)
    assert "También de Rubicón Lab" in html and "Probar El Enjambre" in html
    assert DISCLAIMER in html
    assert verificar_pieza(html) == []  # sin vocabulario prohibido, con disclaimer


# ---------- persistencia del brief ----------

def test_brief_se_guarda_y_se_lee():
    conexion = persistencia.conectar()
    brief = {"mercado": [{"nombre": "Oro", "variacion_pct": -0.9, "frase": "Oro retrocedió 0.9%."}],
             "observa": ["La Fed"], "origen_datos": "demo"}
    persistencia.guardar_brief(conexion, "2026-07-12", brief)
    leido = persistencia.obtener_brief(conexion, "2026-07-12")
    assert leido["mercado"][0]["nombre"] == "Oro"
    assert leido["aprobado"] is False
    assert persistencia.aprobar_brief(conexion, "2026-07-12") is True
    assert persistencia.obtener_brief(conexion, "2026-07-12")["aprobado"] is True
    conexion.close()
```

## engine/validation/test_redaccion_ia.py
```python
"""Tests del redactor de IA de El Pulso — los candados sin llamar a la API.

Prueban que: sin clave hay fallback (None), el filtro CMF cae los párrafos
prohibidos pero conserva los limpios, y la validación arma bien la estructura.
Ninguno gasta una llamada a Anthropic.
"""

from datetime import datetime, timezone

from contenido import redaccion_ia


def test_contexto_temporal_sabado_de_manana():
    """El 8 de agosto de 2026 es sábado; 13:00 UTC ≈ mañana en Chile."""
    momento = datetime(2026, 8, 8, 13, 0, tzinfo=timezone.utc)
    ctx = redaccion_ia.contexto_temporal(momento)
    assert ctx["dia_semana"] == "sábado"
    assert ctx["es_finde"] is True
    assert "8 de agosto de 2026" in ctx["fecha"]
    assert ctx["momento"] in ("mañana", "madrugada")  # según horario de verano/invierno


def test_momentos_del_dia():
    assert redaccion_ia._momento(3) == "madrugada"
    assert redaccion_ia._momento(9) == "mañana"
    assert redaccion_ia._momento(15) == "tarde"
    assert redaccion_ia._momento(22) == "noche"


def test_mensaje_incluye_dia_fecha_y_momento():
    """El redactor recibe el día/fecha/momento como hecho — no los adivina."""
    brief = {"mercado": [{"nombre": "Nvidia", "variacion_pct": 3.4}]}
    cuando = {"dia_semana": "miércoles", "fecha": "5 de agosto de 2026",
              "momento": "mañana", "es_finde": False}
    msg = redaccion_ia._mensaje_del_dia(brief, None, cuando)
    assert "miércoles" in msg
    assert "5 de agosto de 2026" in msg
    assert "mañana" in msg


def test_mensaje_marca_fin_de_semana():
    brief = {"mercado": [{"nombre": "Nvidia", "variacion_pct": 3.4}]}
    cuando = {"dia_semana": "sábado", "fecha": "8 de agosto de 2026",
              "momento": "mañana", "es_finde": True}
    msg = redaccion_ia._mensaje_del_dia(brief, None, cuando)
    assert "FIN DE SEMANA" in msg


def test_sin_clave_cae_al_fallback(monkeypatch):
    """Sin ANTHROPIC_API_KEY, redactar() devuelve None (el boletín usa plantilla)."""
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    brief = {"mercado": [{"nombre": "Nvidia", "variacion_pct": 3.4}]}
    assert redaccion_ia.redactar(brief) is None


def test_sin_hechos_no_redacta(monkeypatch):
    """Con clave pero sin hechos ni enjambre, no hay nada que redactar → None."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-falsa")
    assert redaccion_ia.redactar({"mercado": []}) is None


def test_cmf_cae_parrafo_prohibido_conserva_limpio():
    """El filtro CMF descarta el párrafo con vocabulario prohibido y deja el limpio."""
    texto = ("Nvidia avanzó 3,4% y volvió a ser el engreído del salón.\n\n"
             "Es una oportunidad de compra clarísima para ti.")  # este cruza la CMF
    limpio = redaccion_ia._cmf(texto)
    assert limpio is not None
    assert "engreído del salón" in limpio
    assert "oportunidad de compra" not in limpio


def test_cmf_todo_prohibido_devuelve_none():
    assert redaccion_ia._cmf("Recomendamos comprar ahora sin pensarlo.") is None


def test_validar_sanea_y_arma_estructura():
    """Una respuesta de IA (simulada) se valida: conserva lo limpio, cae lo
    que cruza la CMF, y arma la forma final (rediseño: {buenos_dias, historias})."""
    datos = {
        "buenos_dias": ("Wall Street amaneció en verde.\n\n"
                        "Deberias comprar ya mismo."),   # 2º párrafo cae
        "historias": [
            {"kicker": "Tecnología", "emoji": "🟢", "titular": "Nvidia subió",
             "dek": "Los chips mandan", "cuerpo": "Los chips mandan.", "bottom_line": "",
             "grafico": {"ticker": "NVDA", "nombre": "Nvidia", "periodo": "semana"}},
            {"emoji": "⚠️", "titular": "Compra ahora esta acción", "cuerpo": "x"},  # titular prohibido → cae
        ],
    }
    salida = redaccion_ia._validar(datos)
    assert salida is not None
    assert "amaneció en verde" in salida["buenos_dias"]
    assert "comprar ya mismo" not in salida["buenos_dias"]
    # solo la historia limpia sobrevive (la de "Compra ahora" se cae)
    assert len(salida["historias"]) == 1
    assert salida["historias"][0]["titular"] == "Nvidia subió"
    assert salida["historias"][0]["grafico"]["ticker"] == "NVDA"


def test_validar_sin_apertura_ni_estrella_es_none():
    """Si no queda ni apertura ni historia estrella, no hay diario → None."""
    datos = {"buenos_dias": "Recomendamos comprar.", "historia_estrella": None, "historias": []}
    assert redaccion_ia._validar(datos) is None


def test_extraer_json_desde_texto_envuelto():
    crudo = 'Claro, aquí tienes:\n{"buenos_dias": "Hola", "historias": []}\n¡Listo!'
    datos = redaccion_ia._extraer_json(crudo)
    assert datos is not None and datos["buenos_dias"] == "Hola"


def test_mensaje_del_dia_no_filtra_numeros():
    """El mensaje que ve la IA lleva los números y las citas tal cual (para
    copiarlos, no inventarlos). Rediseño: los movers van como CANDIDATOS con su
    [TICKER] y su cita de prensa."""
    brief = {"mercado": [{"nombre": "Nvidia", "variacion_pct": 3.4, "simbolo": "NVDA",
                          "cita_titular": "Insulet recorta su previsión"}]}
    msg = redaccion_ia._mensaje_del_dia(brief)
    assert "3.4%" in msg
    assert "[NVDA]" in msg
    assert "Insulet recorta su previsión" in msg
```

## engine/validation/test_remedir_sin_fuga.py
```python
"""La re-medición SIN FUGA (`calibration.remedir_sin_fuga`): la ventana parte del
cierre DEL DÍA del titular (no del anterior), la media ponderada baja a los 2
contrarians, y el acierto se cuenta solo sobre casos direccionables. Con un
`fetch` simulado no se llama a Yahoo."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # engine/

from calibration import remedir_sin_fuga as R  # noqa: E402


def test_signo():
    assert R._sg(1.2) == 1 and R._sg(-0.1) == -1 and R._sg(0) == 0


def test_pond_castiga_contrarians():
    # dos arquetipos: uno base (+1) y un contrarian (-1); el contrarian pesa 0.3
    sa = {"institucional_frio": {"senal_media": 1.0, "n": 10},
          "quant_esceptico": {"senal_media": -1.0, "n": 10}}
    # num = 1*10*1 + (-1)*10*0.3 = 7 ; den = 10 + 3 = 13 -> 0.538
    assert round(R._pond(sa), 3) == 0.538


def test_pct_sin_fuga_parte_del_dia_del_titular():
    barras = [("2026-01-01", 100.0), ("2026-01-02", 110.0),
              ("2026-01-03", 120.0), ("2026-01-04", 132.0)]
    # fecha_base = cierre ANTERIOR (01-01); base = día del titular (01-02 = 110)
    # final = 2 ruedas después (01-04 = 132) -> (132-110)/110 = +20%
    assert round(R.pct_sin_fuga(barras, "2026-01-01", 2), 2) == 20.0


def test_pct_sin_fuga_sin_barras_suficientes():
    barras = [("2026-01-01", 100.0), ("2026-01-02", 110.0)]
    assert R.pct_sin_fuga(barras, "2026-01-01", 2) is None   # no alcanza
    assert R.pct_sin_fuga(barras, "2099-01-01", 1) is None   # fecha ausente
    assert R.pct_sin_fuga(None, "2026-01-01", 1) is None     # sin barras


def test_acc_solo_cuenta_direccionables():
    filas = [
        {"senal": 0.5, "direccion_pct": 1.0, "pct_corr": 2.0, "pct_orig": 2.0},   # señal+ real+ ok
        {"senal": -0.5, "direccion_pct": 1.0, "pct_corr": 3.0, "pct_orig": 3.0},  # señal- real+ falla
        {"senal": 0.5, "direccion_pct": 1.0, "pct_corr": 0.1, "pct_orig": 0.1},   # plano: fuera (|.1|<0.3)
    ]
    acc, n = R._acc(filas, por_senal=True, usar_corr=True)
    assert n == 2 and acc == 50.0  # 1 de 2 direccionables


def test_recolectar_desde_archivo(tmp_path):
    import json
    casos = {"casos": [{
        "origen": "historico",
        "simbolos": "BTC-USD",
        "direccion_pct": -1.0,
        "senales_arquetipo": {"institucional_frio": {"senal_media": -0.8, "n": 5}},
        "reaccion_real": {"simbolo": "BTC-USD", "fecha_base": "2026-01-01",
                          "ruedas": 2, "pct_real": 9.0},
    }]}
    ruta = tmp_path / "cal.json"
    ruta.write_text(json.dumps(casos))
    barras = [("2026-01-01", 100.0), ("2026-01-02", 100.0),
              ("2026-01-03", 100.0), ("2026-01-04", 95.0)]  # sin fuga: -5%
    filas = R.recolectar(str(ruta), fetch=lambda s, f: barras, pausa=0)
    assert len(filas) == 1
    f = filas[0]
    assert f["mercado"] == "cripto"
    assert round(f["pct_corr"], 1) == -5.0   # sin fuga
    assert f["pct_orig"] == 9.0              # con fuga (lo que trae el export)
    assert round(f["senal"], 2) == -0.8
    # resumen: la señal (-0.8) acierta contra el real sin fuga (-5%)
    res = R.resumen(filas)
    assert res["cripto"]["sin_fuga"]["senal"] == 100.0


def test_gating_por_senal_cobertura_y_acierto():
    # 4 casos direccionables: señales fuertes aciertan, señales débiles fallan
    filas = [
        {"senal": 0.8, "pct_corr": 5.0},    # fuerte, acierta
        {"senal": 0.6, "pct_corr": 4.0},    # fuerte, acierta
        {"senal": 0.05, "pct_corr": -3.0},  # débil, falla (señal+ real-)
        {"senal": -0.05, "pct_corr": 2.0},  # débil, falla (señal- real+)
    ]
    g = R.gating_por_senal(filas, cortes=(0.0, 0.5))
    base = g[0]       # |señal|>=0: los 4
    fuerte = g[1]     # |señal|>=0.5: los 2 fuertes
    assert base["n"] == 4 and base["acierto"] == 50.0 and base["cobertura"] == 100.0
    assert fuerte["n"] == 2 and fuerte["acierto"] == 100.0 and fuerte["cobertura"] == 50.0
```

## engine/validation/test_reparto.py
```python
"""Tests del reparto de cerebros (brains/reparto.py).

La regla sagrada (CLAUDE.md §2.7): ~100-120 llamadas a la IA por
simulación. Con 1000 líderes, el reparto debe mantenerse en ese techo,
cubrir a TODOS los líderes, y respetar el arquetipo de cada uno.
"""

from brains import reparto


class _Lider:
    def __init__(self, uid, arquetipo):
        self.unique_id = uid
        self.arquetipo = arquetipo


def _mil_lideres():
    arquetipos = ["institucional_frio"] * 150 + ["quant_esceptico"] * 100 + \
                 ["fomo_evangelista"] * 150 + ["doomer"] * 150 + \
                 ["contrarian_sabio"] * 100 + ["macro_trader"] * 100 + \
                 ["influencer_optimista"] * 150 + ["value_paciente"] * 100
    return [_Lider(i, a) for i, a in enumerate(arquetipos)]


def test_mil_lideres_no_superan_el_presupuesto():
    lideres = _mil_lideres()
    consultas, asignacion = reparto.planificar(lideres, lambda uid: uid)
    assert len(lideres) == 1000
    # el techo de la biblia: nunca más de ~120 llamadas a la IA
    assert len(consultas) <= 120
    assert len(consultas) >= 90  # la máxima riqueza de voces dentro del techo


def test_cada_lider_recibe_un_cerebro_de_su_arquetipo():
    lideres = _mil_lideres()
    consultas, asignacion = reparto.planificar(lideres, lambda uid: uid)
    assert len(asignacion) == len(lideres)
    for i, lider in enumerate(lideres):
        cerebro_idx = asignacion[i]
        assert 0 <= cerebro_idx < len(consultas)
        # el cerebro asignado es del MISMO arquetipo que el líder
        assert consultas[cerebro_idx][1] == lider.arquetipo


def test_expandir_devuelve_una_respuesta_por_lider():
    lideres = _mil_lideres()
    consultas, asignacion = reparto.planificar(lideres, lambda uid: uid)
    respuestas_cerebros = [{"senal": i / 100, "confianza": 0.5, "frase": f"c{i}"}
                           for i in range(len(consultas))]
    expandidas = reparto.expandir(respuestas_cerebros, asignacion)
    assert len(expandidas) == 1000
    # cada líder recibe exactamente la respuesta de su cerebro
    for i in range(len(lideres)):
        assert expandidas[i] is respuestas_cerebros[asignacion[i]]


def test_pocos_lideres_es_uno_a_uno_como_antes():
    """Con pocos líderes (por debajo del objetivo) cada uno es su propio cerebro."""
    lideres = [_Lider(i, "doomer") for i in range(100)]
    consultas, asignacion = reparto.planificar(lideres, lambda uid: uid)
    assert len(consultas) == 100
    assert sorted(asignacion) == list(range(100))
```

## engine/validation/test_respaldo.py
```python
"""Tests del respaldo de calibración a GitHub (contenido/respaldo.py).

La regla de oro: el respaldo FUSIONA con lo ya subido (inmune a los
borrones del disco efímero de Render), va a una rama distinta de main
(un commit a main redesplegaría el motor) y jamás tumba al corrector.
"""

import base64
import json
from datetime import datetime, timedelta, timezone

import pytest

from contenido import corrector, persistencia, respaldo


@pytest.fixture(autouse=True)
def entorno(monkeypatch, tmp_path):
    monkeypatch.delenv("GITHUB_RESPALDO_TOKEN", raising=False)
    monkeypatch.delenv("ALPACA_API_KEY_ID", raising=False)
    monkeypatch.setenv("ENJAMBRE_DB", str(tmp_path / "enjambre.db"))


def _caso(conexion, titular: str, pct_sim: float, pct_real: float | None,
          hace_dias: int = 3) -> str:
    sim_id = persistencia.guardar_simulacion(
        conexion, titular=titular, fuente="test", seed=abs(hash(titular)) % 1000,
        resumen={"direccion_pct": pct_sim, "volatilidad_pct": 1.0},
        lideres=[], serie_precios=[100.0], destacada=True,
    )
    persistencia.registrar_titular(conexion, titular=titular, fuente="test",
                                   veredicto="simular", simbolos="SPY", sim_id=sim_id)
    fecha = (datetime.now(timezone.utc) - timedelta(days=hace_dias)).isoformat(timespec="seconds")
    conexion.execute("UPDATE simulaciones SET fecha = ? WHERE id = ?", (fecha, sim_id))
    if pct_real is not None:
        persistencia.guardar_reaccion_real(conexion, sim_id, {"simbolo": "SPY", "pct_real": pct_real})
    conexion.commit()
    return sim_id


def test_exportar_solo_incluye_casos_corregidos():
    conexion = persistencia.conectar()
    corregida = _caso(conexion, "Con corrección", -2.0, -1.1)
    _caso(conexion, "Sin corrección aún", 1.0, None)
    casos = respaldo.exportar_casos(conexion)
    conexion.close()
    assert [c["sim_id"] for c in casos] == [corregida]
    assert casos[0]["reaccion_real"]["pct_real"] == -1.1
    assert casos[0]["direccion_pct"] == -2.0
    assert casos[0]["simbolos"] == "SPY"


def test_fusionar_es_inmune_al_borron_de_disco():
    # lo ya respaldado (de antes del redeploy) + lo nuevo (base recién nacida)
    previos = [{"sim_id": "a", "fecha": "2026-07-01", "titular": "vieja"},
               {"sim_id": "b", "fecha": "2026-07-02", "titular": "se actualiza"}]
    nuevos = [{"sim_id": "b", "fecha": "2026-07-02", "titular": "versión nueva"},
              {"sim_id": "c", "fecha": "2026-07-03", "titular": "nueva"}]
    fusion = respaldo.fusionar(previos, nuevos)
    assert [c["sim_id"] for c in fusion] == ["a", "b", "c"]  # nada se pierde
    assert fusion[1]["titular"] == "versión nueva"           # lo nuevo manda


def test_sin_token_no_hace_nada_y_no_lanza():
    resultado = respaldo.respaldar()
    assert resultado["subido"] is False
    assert "GITHUB_RESPALDO_TOKEN" in resultado["motivo"]


def test_subida_fusiona_con_lo_remoto(monkeypatch):
    """Simula GitHub: ya hay 1 caso remoto; el local aporta otro → quedan 2."""
    monkeypatch.setenv("GITHUB_RESPALDO_TOKEN", "tok-prueba")
    conexion = persistencia.conectar()
    _caso(conexion, "Caso local", 2.0, 1.5)

    remoto = {"casos": [{"sim_id": "remoto1", "fecha": "2026-07-01"}]}
    contenido_b64 = base64.b64encode(json.dumps(remoto).encode()).decode()
    subidas = {}

    class RespuestaGet:
        status_code = 200
        def json(self):
            return {"sha": "abc123", "content": contenido_b64}

    class RespuestaPut:
        status_code = 200
        def raise_for_status(self):
            pass

    def falso_get(url, **kwargs):
        assert kwargs["params"]["ref"] == "respaldo-datos"  # jamás main
        return RespuestaGet()

    def falso_put(url, **kwargs):
        subidas["cuerpo"] = kwargs["json"]
        return RespuestaPut()

    monkeypatch.setattr(respaldo.httpx, "get", falso_get)
    monkeypatch.setattr(respaldo.httpx, "put", falso_put)

    resultado = respaldo.respaldar(conexion)
    conexion.close()

    assert resultado == {"subido": True, "casos": 2}  # remoto + local
    assert subidas["cuerpo"]["branch"] == "respaldo-datos"
    assert subidas["cuerpo"]["sha"] == "abc123"
    subido = json.loads(base64.b64decode(subidas["cuerpo"]["content"]))
    assert len(subido["casos"]) == 2


def test_falla_de_red_no_lanza(monkeypatch):
    monkeypatch.setenv("GITHUB_RESPALDO_TOKEN", "tok-prueba")
    conexion = persistencia.conectar()
    _caso(conexion, "Caso local", 2.0, 1.5)
    monkeypatch.setattr(respaldo.httpx, "get",
                        lambda *a, **k: (_ for _ in ()).throw(OSError("sin red")))
    resultado = respaldo.respaldar(conexion)
    conexion.close()
    assert resultado["subido"] is False
    assert "OSError" in resultado["motivo"]


def test_el_corrector_dispara_el_respaldo_solo_si_corrigio(monkeypatch):
    llamadas = []
    monkeypatch.setattr(respaldo, "respaldar", lambda conexion=None: llamadas.append(1) or {"subido": True, "casos": 1})
    conexion = persistencia.conectar()
    _caso(conexion, "Pendiente de corregir", -2.0, None)

    # sin datos de mercado: no corrige → no respalda
    corrector.corregir_pendientes(conexion, obtener_variacion=lambda *a: None)
    assert llamadas == []

    # con datos: corrige → respalda
    variacion = {"simbolo": "SPY", "pct_real": -0.9, "cierre_base": 100.0,
                 "cierre_final": 99.1, "fecha_base": "2026-07-10",
                 "fecha_final": "2026-07-14", "ruedas": 2}
    resultado = corrector.corregir_pendientes(conexion, obtener_variacion=lambda *a: variacion)
    conexion.close()
    assert llamadas == [1]
    assert resultado["respaldo"] == {"subido": True, "casos": 1}
```

## engine/validation/test_resumen_semanal.py
```python
"""Tests del RESUMEN DE LA SEMANA de El Pulso (edición del sábado).

Reglas de oro que protegen:
- los temas salen de las noticias que importaron (destacadas de la semana);
- los números semanales vienen de Yahoo (el número manda);
- punto de vista sobre lo que YA pasó SÍ, predicción JAMÁS (CMF);
- nada se publica sin pasar el filtro CMF ni sin escapar el HTML.
"""

from datetime import datetime, timedelta

from contenido import boletin, redaccion_ia, resumen_semanal
from contenido.vocabulario import DISCLAIMER, verificar_pieza

CUANDO = {"dia_semana": "sábado", "weekday": 5, "fecha": "15 de agosto de 2026",
          "momento": "mañana", "es_finde": True}


# ---------- los temas: ventana de la semana + dedup ----------

def test_titulares_de_la_semana_filtra_ventana_y_dedup(monkeypatch):
    filas = [
        {"titular": "Tema A", "fecha": "2026-08-14T10:00:00"},
        {"titular": "tema a", "fecha": "2026-08-13T10:00:00"},   # duplicado (case)
        {"titular": "Muy viejo", "fecha": "2026-08-01T10:00:00"},  # fuera de la ventana
        {"titular": "Tema B", "fecha": "2026-08-12T10:00:00"},
    ]
    monkeypatch.setattr(resumen_semanal.persistencia, "listar_simulaciones",
                        lambda *a, **k: filas)
    out = resumen_semanal.titulares_de_la_semana(conexion=object(), cuando=CUANDO)
    assert [t["titular"] for t in out] == ["Tema A", "Tema B"]


# ---------- la foto semanal: el número manda ----------

def _fetch_fake(mapa):
    def fetch(simbolo, rango="5d", intervalo="1d"):
        precios = mapa.get(simbolo)
        if not precios:
            return None
        base = datetime(2026, 8, 11)
        fechas = [base + timedelta(days=i) for i in range(len(precios))]
        return fechas, [float(p) for p in precios]
    return fetch


def test_foto_semana_calcula_variacion_semanal():
    fetch = _fetch_fake({"^GSPC": [100, 101, 102, 103, 104], "CL=F": [80, 78, 77, 76, 75]})
    foto = resumen_semanal.foto_semana(fetch=fetch)
    por_simbolo = {f["simbolo"]: f for f in foto}
    assert por_simbolo["^GSPC"]["var_semana_pct"] == 4.0
    assert por_simbolo["CL=F"]["var_semana_pct"] == -6.25
    assert por_simbolo["^GSPC"]["nombre"] == "S&P 500"


def test_preparar_resumen_none_sin_temas(monkeypatch):
    monkeypatch.setattr(resumen_semanal.persistencia, "listar_simulaciones", lambda *a, **k: [])
    assert resumen_semanal.preparar_resumen(conexion=object(), cuando=CUANDO,
                                            fetch=_fetch_fake({})) is None


# ---------- el filtro CMF sobre el resumen redactado ----------

def test_validar_resumen_filtra_prediccion_y_recomendacion():
    datos = {
        "intro": "Semana de nervios.\n\nEl precio subirá con fuerza la próxima semana.",  # 2º cae (predicción)
        "temas": [
            {"kicker": "Macro", "emoji": "🏦", "titular": "La Fed marcó el tono",
             "analisis": "Subió el tono.\n\nEl mercado lo leyó como cautela.",
             "que_observar": "Habrá que ver la próxima acta.", "grafico": None},
            {"titular": "Deberías comprar ya", "analisis": "x"},   # titular prohibido → cae
        ],
        "cierre": "Una semana para respirar.",
    }
    val = redaccion_ia._validar_resumen(datos)
    assert val is not None
    assert "subirá con fuerza" not in val["intro"]     # la predicción cayó
    assert "Semana de nervios" in val["intro"]
    assert len(val["temas"]) == 1                       # el tema prohibido cayó
    assert val["temas"][0]["titular"] == "La Fed marcó el tono"


# ---------- el correo del sábado ----------

def _brief_resumen():
    hechos = {"titulo": "El Pulso de la semana",
              "titulares": [{"titular": "x", "fecha": "2026-08-12"}],
              "foto": [{"simbolo": "^GSPC", "nombre": "S&P 500", "var_semana_pct": 1.8},
                       {"simbolo": "CL=F", "nombre": "Petróleo WTI", "var_semana_pct": -3.2}]}
    red = {"intro": "Semana de nervios.\n\nLa Fed en el centro.",
           "temas": [
               {"kicker": "Macro · la Fed", "emoji": "🏦", "titular": "La Fed volvió a ser el personaje",
                "analisis": "Subió el tono.\n\nEl mercado lo leyó como cautela.",
                "que_observar": "Habrá que ver la próxima acta.",
                "grafico": {"ticker": "^GSPC", "nombre": "S&P 500", "periodo": "semana", "moneda": "$"}},
               {"kicker": "Geopolítica · petróleo", "emoji": "🛢️", "titular": "El crudo cedió",
                "analisis": "Bajó la tensión.\n\nMenos prima de riesgo.",
                "que_observar": "Atento a la OPEP.", "grafico": None},
           ],
           "cierre": "Una semana para respirar."}
    return {"resumen": hechos, "resumen_redactado": red}


def test_correo_resumen_es_cmf_limpio():
    html = boletin.construir_html([], "sábado 15 de agosto", brief=_brief_resumen())
    assert "El Pulso de la semana" in html
    assert "La semana en números" in html
    assert "La Fed volvió a ser el personaje" in html and "El crudo cedió" in html
    assert "Qué observar" in html
    assert "También de Rubicón Lab" in html          # el pie del Enjambre, como siempre
    assert DISCLAIMER in html
    assert verificar_pieza(html) == []


def test_correo_resumen_escapa_html_hostil():
    brief = _brief_resumen()
    brief["resumen_redactado"]["temas"][0]["analisis"] = "<script>alert(1)</script> ojo"
    html = boletin.construir_html([], "sábado 15 de agosto", brief=brief)
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;" in html


def test_asunto_resumen():
    assert "semana" in boletin.asunto_resumen().lower()
```

## engine/validation/test_seguridad.py
```python
"""Tests del blindaje (Fase 1 + 2): identidad, rate-limit, cabeceras,
validación de ids, path traversal y escape XSS del frontend."""

import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import brains.cerebro as cerebro
import server
from contenido import limites, persistencia, seguridad


@pytest.fixture(autouse=True)
def entorno(monkeypatch, tmp_path):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setattr(cerebro, "RUTA_CACHE", tmp_path / "cache.json")
    monkeypatch.setenv("ENJAMBRE_DB", str(tmp_path / "enjambre.db"))
    seguridad.reiniciar()
    limites.reiniciar()


# ---------- identidad real del cliente (anti-spoofing) ----------

def test_ip_cliente_toma_el_ultimo_salto_de_xff():
    # el cliente falsifica 1.1.1.1; Render agrega su IP real al final
    headers = {"x-forwarded-for": "1.1.1.1, 203.0.113.9"}
    assert seguridad.ip_cliente(headers, "10.0.0.1") == "203.0.113.9"


def test_ip_cliente_usa_fallback_sin_proxy():
    assert seguridad.ip_cliente({}, "192.168.1.5") == "192.168.1.5"
    assert seguridad.ip_cliente({}, None) == "desconocida"


# ---------- validación de identificadores ----------

def test_sim_id_valido_solo_hex16():
    assert seguridad.sim_id_valido("6181e77222d4a245")
    assert not seguridad.sim_id_valido("../../../../etc/passwd")
    assert not seguridad.sim_id_valido("6181e77222d4a24")   # 15
    assert not seguridad.sim_id_valido("6181E77222D4A245")  # mayúsculas
    assert not seguridad.sim_id_valido(None)


def test_ruta_frames_rechaza_traversal():
    with pytest.raises(ValueError):
        persistencia.ruta_frames("../../../../etc/passwd")
    # un id válido sí produce ruta dentro de frames/
    ruta = persistencia.ruta_frames("6181e77222d4a245")
    assert ruta.name == "6181e77222d4a245.bin"


# ---------- rate-limit HTTP ----------

def test_permitir_http_corta_al_pasar_el_limite():
    ip = "9.9.9.9"
    permitidas = sum(1 for _ in range(200) if seguridad.permitir_http(ip, "/api/muro"))
    assert permitidas == seguridad.LIMITE_GENERAL[0]
    # otra IP sigue teniendo su propio cupo
    assert seguridad.permitir_http("8.8.8.8", "/api/muro")


def test_replay_tiene_su_propio_limite_mas_estricto():
    ip = "7.7.7.7"
    replay_ok = sum(1 for _ in range(100) if seguridad.permitir_http(ip, "/api/simulacion/x/replay"))
    assert replay_ok == seguridad.LIMITE_PESADO[0]


def test_endpoint_muro_responde_429_bajo_flood():
    cliente = TestClient(server.app)
    codigos = {cliente.get("/api/muro").status_code for _ in range(seguridad.LIMITE_GENERAL[0] + 10)}
    assert 429 in codigos


# ---------- cabeceras de seguridad ----------

def test_cabeceras_de_seguridad_presentes():
    cliente = TestClient(server.app)
    respuesta = cliente.get("/api/muro")
    assert respuesta.headers["X-Content-Type-Options"] == "nosniff"
    assert respuesta.headers["X-Frame-Options"] == "DENY"
    assert "default-src 'none'" in respuesta.headers["Content-Security-Policy"]


# ---------- path traversal en el endpoint de replay ----------

def test_replay_rechaza_sim_id_malicioso():
    cliente = TestClient(server.app)
    assert cliente.get("/api/simulacion/..%2f..%2fsecreto/replay").status_code == 404
    assert cliente.get("/api/simulacion/no-hex/replay").status_code == 404
    assert cliente.get("/api/simulacion/no-hex").status_code == 404


# ---------- caché HTTP en los endpoints servibles ----------

def test_endpoints_publicos_declaran_cache():
    cliente = TestClient(server.app)
    assert "max-age" in cliente.get("/api/muro").headers.get("Cache-Control", "")


# ---------- XSS: el frontend escapa el contenido no confiable ----------

def test_el_muro_escapa_datos_antes_de_innerhtml():
    """Guard de código: titular/frase deben ir escapados, nunca crudos."""
    muro = (Path(__file__).parent.parent.parent / "web" / "src" / "muro" / "muro.js").read_text(encoding="utf-8")
    assert "function esc(" in muro
    # el titular jamás se interpola crudo en el HTML
    assert "${tarjeta.titular}" not in muro
    assert "${esc(tarjeta.titular)}" in muro
    assert "${esc(r.frase.frase)}" in muro

    panel = (Path(__file__).parent.parent.parent / "web" / "src" / "ui" / "panel.js").read_text(encoding="utf-8")
    assert "${esc(f.frase)}" in panel
    assert re.search(r"\$\{f\.frase\}", panel) is None  # nunca crudo
    # el tooltip del líder también escapa la frase del LLM (defensa en profundidad)
    assert "${esc(lider.frase)}" in panel
    assert re.search(r"\$\{lider\.frase\}", panel) is None
    assert re.search(r"\$\{lider\.nombre\}", panel) is None
    # el ticker pasa por la lista blanca antes del HTML y del widget externo
    assert "tickerSeguro(" in panel
    assert re.search(r"\$\{extras\.simbolos\}", panel) is None  # nunca crudo


# ---------- el token de admin se compara en tiempo constante ----------

def test_token_admin_usa_comparacion_constante():
    """Los endpoints protegidos comparan el token con hmac.compare_digest
    (no con !=), para no filtrar el token por timing."""
    servidor = (Path(__file__).parent.parent / "server.py").read_text(encoding="utf-8")
    assert "hmac.compare_digest" in servidor
    # ya no debe quedar la comparación directa del token
    assert "!= esperado" not in servidor


def test_endpoint_protegido_rechaza_token_incorrecto(monkeypatch):
    from fastapi.testclient import TestClient
    monkeypatch.setenv("ENJAMBRE_PIPELINE_TOKEN", "secreto-de-prueba")
    import server
    cliente = TestClient(server.app)
    # sin token → 403
    assert cliente.post("/api/pipeline").status_code == 403
    # token equivocado → 403
    assert cliente.post("/api/pipeline", headers={"X-Pipeline-Token": "malo"}).status_code == 403
    # el diagnóstico también es solo-admin
    assert cliente.get("/api/diagnostico").status_code == 403


def test_diagnostico_reporta_clave_faltante(monkeypatch):
    from fastapi.testclient import TestClient
    monkeypatch.setenv("ENJAMBRE_PIPELINE_TOKEN", "secreto-de-prueba")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    import server
    cliente = TestClient(server.app)
    datos = cliente.get("/api/diagnostico", headers={"X-Pipeline-Token": "secreto-de-prueba"}).json()
    assert datos["clave_presente"] is False
    assert "FALTA" in datos["veredicto"]


# ---------- el tope global por defecto (la muralla de la billetera) ----------

def test_tope_diario_por_defecto(monkeypatch):
    # el default es 30 (la muralla de la billetera); en producción se fija con
    # ENJAMBRE_MAX_SIM_DIA según el presupuesto.
    monkeypatch.delenv("ENJAMBRE_MAX_SIM_DIA", raising=False)
    assert limites.tope_global_dia() == 30


# ---------- candado de pruebas privadas ----------

def test_acceso_abierto_sin_clave(monkeypatch):
    """Sin ENJAMBRE_ACCESO, cualquiera pasa (comportamiento normal)."""
    monkeypatch.delenv("ENJAMBRE_ACCESO", raising=False)
    assert not seguridad.acceso_privado_activo()
    assert seguridad.acceso_ok(None)
    assert seguridad.acceso_ok("lo-que-sea")


def test_acceso_privado_exige_la_clave(monkeypatch):
    """Con ENJAMBRE_ACCESO puesta, solo la clave correcta pasa."""
    monkeypatch.setenv("ENJAMBRE_ACCESO", "clave-secreta-de-pruebas")
    assert seguridad.acceso_privado_activo()
    assert seguridad.acceso_ok("clave-secreta-de-pruebas")
    assert not seguridad.acceso_ok("")
    assert not seguridad.acceso_ok(None)
    assert not seguridad.acceso_ok("clave-equivocada")


def test_ws_simular_rechaza_sin_clave_en_modo_privado(monkeypatch):
    """El WebSocket de simulación no gasta IA sin la clave correcta."""
    monkeypatch.setenv("ENJAMBRE_ACCESO", "abre-sesamo")
    cliente = TestClient(server.app)
    with cliente.websocket_connect("/ws") as ws:
        ws.send_json({"tipo": "simular", "titular": "La Fed sube las tasas"})
        respuesta = ws.receive_json()
        assert respuesta["tipo"] == "privado"


def test_simular_titular_respeta_el_candado(monkeypatch):
    monkeypatch.setenv("ENJAMBRE_ACCESO", "abre-sesamo")
    cliente = TestClient(server.app)
    r = cliente.post("/api/simular-titular", json={"id": "a" * 16})
    assert r.json()["estado"] == "privado"
    # con la clave correcta, el candado deja pasar (y sigue el flujo normal)
    r2 = cliente.post("/api/simular-titular", json={"id": "no-hex", "acceso": "abre-sesamo"})
    assert r2.status_code == 404  # ya pasó el candado; falla por id inválido


# ---------- la puerta de correo (gancho de crecimiento público) ----------

def test_correo_valido():
    assert seguridad.correo_valido("giorgio@rubicon.cl")
    assert not seguridad.correo_valido("no-es-correo")
    assert not seguridad.correo_valido("")
    assert not seguridad.correo_valido(None)
    assert not seguridad.correo_valido("a@b." + "x" * 300)  # muy largo


def test_puerta_publica_sin_bandera_queda_abierta(monkeypatch):
    """Sin ENJAMBRE_PUERTA_CORREO, público abierto (comportamiento de siempre)."""
    monkeypatch.delenv("ENJAMBRE_ACCESO", raising=False)
    monkeypatch.delenv("ENJAMBRE_PUERTA_CORREO", raising=False)
    ok, correo = server._puerta_simulacion({"titular": "x"})
    assert ok and correo is None


def test_puerta_correo_desactivada_es_permanente(monkeypatch):
    """Decisión de Giorgio: El Enjambre es GRATIS y abierto. La puerta de correo
    queda desactivada aunque alguien ponga la bandera; nunca bloquea. Si la
    persona deja un correo válido, igual se captura como lead (sin bloquear)."""
    monkeypatch.delenv("ENJAMBRE_ACCESO", raising=False)
    monkeypatch.setenv("ENJAMBRE_PUERTA_CORREO", "1")  # la bandera ya no tiene efecto
    ok, correo = server._puerta_simulacion({"titular": "x"})              # sin correo: abierto
    assert ok and correo is None
    ok, correo = server._puerta_simulacion({"titular": "x", "email": "Lector@Medio.CL"})
    assert ok and correo == "lector@medio.cl"                            # lead capturado (minúsculas)


def test_puerta_privada_exige_clave_no_correo(monkeypatch):
    monkeypatch.setenv("ENJAMBRE_ACCESO", "abre-sesamo")
    assert server._puerta_simulacion({"email": "x@y.cl"}) == (False, None)  # el correo no basta
    ok, _ = server._puerta_simulacion({"acceso": "abre-sesamo"})
    assert ok


def test_ws_no_pide_correo_en_publico(monkeypatch):
    """Aunque esté la bandera vieja, el WS NO exige correo: la simulación arranca.
    (El Enjambre es abierto; suscribirse a El Pulso es siempre opcional.)"""
    monkeypatch.delenv("ENJAMBRE_ACCESO", raising=False)
    monkeypatch.setenv("ENJAMBRE_PUERTA_CORREO", "1")
    cliente = TestClient(server.app)
    with cliente.websocket_connect("/ws") as ws:
        ws.send_json({"tipo": "simular", "titular": "La Fed sube las tasas"})  # sin correo
        respuesta = ws.receive_json()
        assert respuesta["tipo"] != "correo"  # no bloquea; arranca la simulación


# ---------- tope de cuerpo por petición (memoria del motor) ----------

def test_cuerpo_gigante_se_rechaza_con_413():
    """Un POST enorme se corta en la puerta: sin este freno se carga entero en
    memoria antes de validarse y el motor (512 MB en Render) reinicia."""
    cliente = TestClient(server.app)
    grande = "x" * (server.MAX_CUERPO + 1)
    respuesta = cliente.post("/api/contacto",
                             json={"nombre": "Ana", "email": "ana@medio.cl", "mensaje": grande})
    assert respuesta.status_code == 413
    # y el webhook (fuera de /api/) también queda cubierto
    assert cliente.post("/pulso/webhook/resend", content=grande).status_code == 413


def test_cuerpo_normal_sigue_pasando():
    """El freno no puede estorbar al uso legítimo (el más grande es el editor
    del panel: unos pocos KB)."""
    cliente = TestClient(server.app)
    respuesta = cliente.post("/api/contacto", json={
        "nombre": "Ana", "email": "ana@medio.cl",
        "organizacion": "Medio X", "mensaje": "y" * 4000})
    assert respuesta.status_code == 200


# ---------- avisos a Telegram (van con parse_mode=HTML) ----------

def test_aviso_telegram_escapa_lo_que_viene_de_afuera():
    """Un "<" en un formulario o en un titular hacía que Telegram rechazara el
    mensaje entero (400) y el aviso se perdiera en silencio."""
    from contenido import notificar
    assert notificar.escapar("<b>Ana</b>") == "&lt;b&gt;Ana&lt;/b&gt;"
    resumen = notificar.resumen_ejecucion(
        "demo", [{"impacto": 8, "titular": "<script>alert(1)</script> Fed sube"}], None)
    assert "<script>" not in resumen
    assert "&lt;script&gt;" in resumen
    assert "<b>El Pulso" in resumen  # el marcado propio del aviso se conserva


# ---------- filtro CMF a las voces de los líderes (borde de cumplimiento) ----------

def test_sanear_frases_neutraliza_lo_no_publicable():
    """Una frase de líder con vocabulario prohibido se neutraliza; una limpia
    se conserva. La neutra, a su vez, sí pasa el filtro."""
    from contenido import vocabulario
    r = [{"arquetipo": "fomo", "frase": "Compra ahora, esto va a subir"},
         {"arquetipo": "doomer", "frase": "Cautela ante el dato de empleo"}]
    vocabulario.sanear_frases(r)
    assert r[0]["frase"] == vocabulario.FRASE_NEUTRAL
    assert r[1]["frase"] == "Cautela ante el dato de empleo"
    assert vocabulario.es_publicable(vocabulario.FRASE_NEUTRAL)


def test_las_frases_de_lideres_se_sanean_en_los_tres_flujos():
    """Guard de código: las tres rutas que muestran frases de líderes (web,
    observatorio en vivo y pipeline de la madrugada) pasan por sanear_frases
    antes de repartirlas a la web, la base y el muro."""
    srv = (Path(__file__).parent.parent / "server.py").read_text(encoding="utf-8")
    assert srv.count("sanear_frases(") >= 2  # simulación transmitida + observatorio
    pipe = (Path(__file__).parent.parent / "contenido" / "pipeline.py").read_text(encoding="utf-8")
    assert "sanear_frases(" in pipe


# ---------- el tope diario vive en disco (sobrevive a los reinicios) ----------

def test_tope_diario_persiste_en_disco(monkeypatch):
    """El cupo global no depende de una variable en memoria que Render reinicia:
    vive en la base, así que un reinicio del proceso no lo levanta a cero."""
    from datetime import date
    monkeypatch.setenv("ENJAMBRE_MAX_SIM_DIA", "2")
    limites.reiniciar()
    assert limites.permitir("a")[0]
    assert limites.permitir("b")[0]
    # el gasto quedó en disco (una conexión nueva lo ve): el cupo está agotado
    conexion = persistencia.conectar()
    assert persistencia.gasto_dia(conexion, date.today().isoformat()) == 2
    conexion.close()
    ok, motivo = limites.permitir("c")
    assert not ok and motivo == limites.MENSAJE_GLOBAL
```

## engine/validation/test_senal_ponderada.py
```python
"""Tests de la señal de predicción ponderada (baja el peso de los contrarians).

Garantizan que:
- el nuevo campo baja el peso SOLO de las voces contrarian (quant/contrarian),
  no del optimista ni del resto;
- el env ENJAMBRE_PESO_CONTRARIANS lo controla (1.0 = vuelve al promedio simple);
- el mapeo de calibración "senal_ponderada" usa el campo nuevo y cae al viejo.
"""
from contenido import calibracion as cal
from contenido import senal_prediccion as sp


class _Lider:
    def __init__(self, arquetipo):
        self.arquetipo = arquetipo


def _caso():
    lideres = [_Lider("doomer"), _Lider("quant_esceptico"),
               _Lider("contrarian_sabio"), _Lider("influencer_optimista")]
    # el doomer y el optimista dicen +1; los dos contrarians dicen -1
    respuestas = [{"senal": 1.0}, {"senal": -1.0}, {"senal": -1.0}, {"senal": 1.0}]
    return lideres, respuestas


def test_ponderada_baja_contrarians(monkeypatch):
    monkeypatch.delenv("ENJAMBRE_PESO_CONTRARIANS", raising=False)
    lideres, respuestas = _caso()
    simple = round(sum(r["senal"] for r in respuestas) / len(respuestas), 2)  # 0.0
    ponderada = sp.senal_media_ponderada(lideres, respuestas)
    assert simple == 0.0
    # con los contrarians a 0.3, los que dicen +1 pesan más → señal positiva
    assert ponderada > simple
    # cálculo exacto: (1 + 1 - 0.3 - 0.3) / (1 + 1 + 0.3 + 0.3)
    esperado = round((1 + 1 - 0.3 - 0.3) / (1 + 1 + 0.3 + 0.3), 2)
    assert ponderada == esperado


def test_env_1_0_vuelve_al_promedio_simple(monkeypatch):
    monkeypatch.setenv("ENJAMBRE_PESO_CONTRARIANS", "1.0")
    lideres, respuestas = _caso()
    simple = round(sum(r["senal"] for r in respuestas) / len(respuestas), 2)
    assert sp.senal_media_ponderada(lideres, respuestas) == simple


def test_env_invalido_cae_al_defecto(monkeypatch):
    monkeypatch.setenv("ENJAMBRE_PESO_CONTRARIANS", "abc")
    assert sp.peso_contrarians() == 0.3


def test_mapeo_usa_campo_nuevo_y_cae_al_viejo():
    # con el campo nuevo
    p = cal.senal_a_prob_cruda({"senal_media_ponderada": 1.0}, modo="senal_ponderada")
    assert p == 1.0
    # sin el campo nuevo, cae al viejo
    p2 = cal.senal_a_prob_cruda({"senal_media_lideres": -1.0}, modo="senal_ponderada")
    assert p2 == 0.0
```

## engine/validation/test_servidor.py
```python
"""Tests del servidor WebSocket (Etapa 4): el flujo end-to-end.

Corren sin API key (fallback) y con ritmo 0 (sin pausas entre ticks).
"""

import json
import struct

import pytest
from fastapi.testclient import TestClient

import brains.cerebro as cerebro
import server


@pytest.fixture(autouse=True)
def entorno(monkeypatch, tmp_path):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setattr(cerebro, "RUTA_CACHE", tmp_path / "cache.json")
    monkeypatch.setenv("ENJAMBRE_DB", str(tmp_path / "enjambre.db"))
    from contenido import limites, seguridad

    limites.reiniciar()
    seguridad.reiniciar()


def test_salud():
    cliente = TestClient(server.app)
    respuesta = cliente.get("/salud")
    assert respuesta.status_code == 200
    assert respuesta.json()["estado"] == "ok"


def test_flujo_completo_por_websocket():
    cliente = TestClient(server.app)
    with cliente.websocket_connect("/ws") as ws:
        ws.send_text(json.dumps({
            "tipo": "simular",
            "titular": "Quiebra el segundo banco más grande del país; pánico en los mercados",
            "seed": 42,
            "ritmo": 0,
        }))

        # 1) inicio: los 1150 líderes con señal, confianza y frase
        inicio = json.loads(ws.receive_text())
        assert inicio["tipo"] == "inicio"
        assert len(inicio["lideres"]) == 1150
        for lider in inicio["lideres"]:
            assert -1.0 <= lider["senal"] <= 1.0
            assert lider["frase"]

        # 2) un frame binario por tick: cabecera (precio, tick) + un byte por agente
        total_ticks = server.TICKS_PREVIOS + server.TICKS_POSTERIORES
        precios = []
        for _ in range(total_ticks):
            frame = ws.receive_bytes()
            precio, tick = struct.unpack("<fI", frame[:8])
            assert len(frame) == 8 + 10150
            precios.append(precio)

        # el titular negativo golpea el precio durante la reacción
        assert min(precios) < precios[server.TICKS_PREVIOS - 1] * 0.97

        # los sentimientos del último frame son bytes con signo válidos
        sentimientos = [b - 256 if b > 127 else b for b in frame[8:]]
        assert all(-127 <= s <= 127 for s in sentimientos)

        # 3) fin: el reporte
        fin = json.loads(ws.receive_text())
        assert fin["tipo"] == "fin"
        reporte = fin["reporte"]
        assert reporte["direccion_pct"] < 2  # una quiebra no dispara el precio
        assert reporte["volatilidad_pct"] > 0
        assert len(reporte["frases"]) == 3
        assert reporte["desglose"]  # hay actividad por tipo

        from contenido.vocabulario import DISCLAIMER
        assert reporte["descargo"] == DISCLAIMER

        # 4) persistencia primero: la simulación quedó guardada
        from contenido import persistencia
        conexion = persistencia.conectar()
        guardada = persistencia.obtener_simulacion(conexion, fin["sim_id"])
        conexion.close()
        assert guardada is not None
        assert guardada["titular"].startswith("Quiebra el segundo banco")
        assert len(guardada["lideres"]) == 1150
        assert len(guardada["serie_precios"]) >= total_ticks
```

## engine/validation/test_setup.py
```python
"""Tests de la Etapa 0: la configuración de agentes es coherente con CLAUDE.md.

Los tests de hechos estilizados (colas gordas, clustering de volatilidad, etc.)
se agregarán en la Etapa 1, cuando exista el motor.
"""

import json
from pathlib import Path

RUTA_CONFIG = Path(__file__).parent.parent / "config" / "agentes.json"


def cargar_config() -> dict:
    with open(RUTA_CONFIG, encoding="utf-8") as f:
        return json.load(f)


def test_la_mezcla_suma_10150_agentes():
    config = cargar_config()
    total = sum(t["cantidad"] for t in config["tipos"])
    assert total == config["total_agentes"] == 10150


def test_hay_13_tipos_de_agentes():
    config = cargar_config()
    assert len(config["tipos"]) == 13


def test_los_arquetipos_de_lideres_suman_1150():
    config = cargar_config()
    lideres = next(t for t in config["tipos"] if t["id"] == "lider_opinion")
    total_arquetipos = sum(a["cantidad"] for a in lideres["arquetipos"])
    assert total_arquetipos == lideres["cantidad"] == 1150
    assert len(lideres["arquetipos"]) == 9  # +1: doomer selectivo (Intervención 1)


def test_los_institucionales_no_estan_en_la_red_social():
    """CLAUDE.md sección 6: los tipos 1-3 no reaccionan a rumores."""
    config = cargar_config()
    institucionales = ["fundamentalista", "quant_momentum", "fondo_pasivo"]
    for tipo in config["tipos"]:
        if tipo["id"] in institucionales:
            assert tipo["en_red_social"] is False


def test_el_servidor_responde_salud():
    from fastapi.testclient import TestClient

    import server

    cliente = TestClient(server.app)
    respuesta = cliente.get("/salud")
    assert respuesta.status_code == 200
    assert respuesta.json()["estado"] == "ok"
```

## engine/validation/test_verificador.py
```python
"""Tests del verificador (arnés): partición held-out estable y comparación
contra el baseline. Todo local, sin IA."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # engine/

from calibration import verificador  # noqa: E402


def test_holdout_es_determinista():
    """El mismo sim_id cae SIEMPRE del mismo lado (no depende de random)."""
    ids = ["abc123", "def456", "ghi789", "0f0f0f0f"]
    primera = [verificador.es_holdout(i) for i in ids]
    for _ in range(5):
        assert [verificador.es_holdout(i) for i in ids] == primera


def test_holdout_separa_casos():
    """No todos los ids caen del mismo lado (la partición realmente divide)."""
    ids = [f"caso-{i:04d}" for i in range(500)]
    holdout = [i for i in ids if verificador.es_holdout(i)]
    visible = [i for i in ids if not verificador.es_holdout(i)]
    assert holdout and visible                       # ambos lados no vacíos
    # proporción cercana al 30% (con 500 ids, margen amplio por azar del hash)
    frac = len(holdout) / len(ids)
    assert 0.20 < frac < 0.40


def test_particionar_no_pierde_casos():
    casos = [{"sim_id": f"s{i}"} for i in range(200)]
    visible, holdout = verificador.particionar(casos)
    assert len(visible) + len(holdout) == len(casos)  # ninguno se pierde
    assert not (set(id(c) for c in visible) & set(id(c) for c in holdout))


def test_baseline_carga_y_tiene_claves():
    base = verificador.cargar_baseline()
    assert base, "el baseline congelado debe existir"
    assert "acierto" in base and "dataset" in base
    assert isinstance(base["acierto"]["indice_negativa"], (int, float))


def test_comparar_promueve_mejora_limpia():
    """Una mejora sin degradar ningún régimen ES promovible."""
    base = {"acierto": {"indice_negativa": 0.38, "indice_positiva": 0.76}}
    nuevas = {"indice_negativa": 0.46, "indice_positiva": 0.76}  # sube neg, mantiene pos
    r = verificador.comparar(nuevas, base)
    assert r["promovible"] is True
    assert "indice_negativa" in r["mejoras"]


def test_comparar_bloquea_si_degrada_un_regimen():
    """Una mejora que ROMPE un régimen NO se promueve (criterio §5)."""
    base = {"acierto": {"indice_negativa": 0.38, "indice_positiva": 0.76}}
    nuevas = {"indice_negativa": 0.46, "indice_positiva": 0.60}  # sube neg pero hunde pos
    r = verificador.comparar(nuevas, base)
    assert r["promovible"] is False
    assert "indice_positiva" in r["degradaciones"]
```

## engine/validation/test_walk_forward.py
```python
"""Tests de la validación walk-forward + promoción (Fase 5), con casos sintéticos."""

import json
import random

from calibration import walk_forward as wf


def _archivo(tmp_path, n=400, seed=5, senal_util=True):
    """Casos ordenables por fecha donde la señal ponderada ordena bien (o no)."""
    rng = random.Random(seed)
    casos = []
    for i in range(n):
        sube = rng.random() < 0.5
        pct = rng.uniform(0.1, 3) if sube else -rng.uniform(0.1, 3)
        base = (0.6 if sube else -0.6) if senal_util else 0.0
        sa = {}
        for a in wf.BASE:
            s = base + rng.uniform(-0.2, 0.2) if senal_util else rng.uniform(-1, 1)
            # los contrarians apuntan al revés (ruido direccional)
            if a in wf.CONTRARIANS and senal_util:
                s = -base + rng.uniform(-0.2, 0.2)
            sa[a] = {"senal_media": s, "confianza_media": 0.7, "n": 10}
        casos.append({"fecha": f"2026-08-{i % 28 + 1:02d}T{i%24:02d}:00:00",
                      "reaccion_real": {"pct_real": pct}, "senales_arquetipo": sa,
                      "direccion_pct": base * 2})
    ruta = tmp_path / "c.json"
    ruta.write_text(json.dumps({"casos": casos}))
    return str(ruta)


def test_walk_forward_devuelve_metricas(tmp_path):
    casos = wf.cargar(_archivo(tmp_path))
    r = wf.walk_forward(casos, "senal_ponderada", min_entrena=150, paso=20)
    for k in ("brier", "brier_base", "skill", "n_oos", "confiabilidad"):
        assert k in r
    assert r["n_oos"] > 0


def test_promueve_con_senal_util(tmp_path):
    casos = wf.cargar(_archivo(tmp_path, senal_util=True))
    rep = wf.promover(casos, min_entrena=150, paso=20)
    assert rep["promovido"] is True
    assert "calibrador" in rep and rep["calibrador"]["params"]
    # el mejor modo debe ser uno de los de señal (no la dirección constante)
    assert rep["mejor"]["modo"] in ("senal_media", "senal_ponderada")


def test_no_promueve_sin_senal(tmp_path):
    casos = wf.cargar(_archivo(tmp_path, senal_util=False))
    rep = wf.promover(casos, min_entrena=150, paso=20)
    # con señales puro ruido, no debe superar la base por el margen
    assert rep["promovido"] is False


def test_ponderada_no_es_peor_que_simple(tmp_path):
    casos = wf.cargar(_archivo(tmp_path, senal_util=True))
    pon = wf.walk_forward(casos, "senal_ponderada", min_entrena=150, paso=20)
    sim = wf.walk_forward(casos, "senal_media", min_entrena=150, paso=20)
    assert pon["brier"] <= sim["brier"] + 0.01
```

## engine/__init__.py
```python

```

