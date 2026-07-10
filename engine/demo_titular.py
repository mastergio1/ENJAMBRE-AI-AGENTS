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
