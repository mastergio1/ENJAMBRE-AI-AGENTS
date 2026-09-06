# El Enjambre 🐝

Simulador de escenarios del mercado bursátil: ingresas una noticia y observas en una escena 3D cómo 10.000 inversionistas simulados reaccionan — el pánico se contagia, las manadas se forman, el precio emerge.

> **Herramienta de simulación y educación. No es asesoría financiera.**

📖 **La biblia del proyecto es [CLAUDE.md](CLAUDE.md).** Léela antes de tocar código.

## Estructura

- `engine/` — motor de simulación (Python 3.11+, Mesa, FastAPI)
- `web/` — frontend (Vite + Three.js + GSAP + Tailwind)
- `docs/` — documentación

## Cómo correr el motor (engine)

```bash
cd engine
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Correr los tests
pytest validation/ -v

# Levantar el servidor
uvicorn server:app --reload
# → http://localhost:8000/salud
```

## Cómo correr el frontend (web)

```bash
cd web
npm install
npm run dev
# → http://localhost:5173
```

## Estado del proyecto

**Etapas 0-10 completadas y en producción.** El motor Python corre la simulación real y la transmite por WebSocket al enjambre 3D: escribes un titular, los 1.000 líderes lo leen (compartiendo ~110 cerebros de IA), la ola se propaga por 10.000 inversionistas y al final aparece el reporte (dirección esperada, volatilidad, desglose por tipo). Sin motor, la web funciona sola en modo demo.

Sobre esa base está construida la capa de contenido (ver [CONTENIDO.md](CONTENIDO.md)): **el muro** (portada con las 3 noticias del día ya simuladas), **el archivo** (hemeroteca buscable), **El Pulso** (newsletter diaria), **La Redacción** (análisis verificado), **el duelo** (dos escenarios enfrentados) y **el widget** embebible.

Fase actual: **calibración** — se contrastan las reacciones del enjambre contra movimientos reales del mercado, con foco en acciones USA, SPY y cripto.

Deploy: ver [docs/despliegue.md](docs/despliegue.md) · Roadmap en [CLAUDE.md](CLAUDE.md#9-roadmap-referencia-rápida) · Foto detallada del avance en [docs/estado-del-proyecto.md](docs/estado-del-proyecto.md) y el traspaso técnico en [docs/contexto.md](docs/contexto.md).

Para explorar el mercado simulado:

```bash
cd engine && source .venv/bin/activate
python simular.py 42        # una sesión con los hechos estilizados
python demo_titular.py "La Fed sube las tasas 50 puntos base"
# con ANTHROPIC_API_KEY en el entorno usa los cerebros LLM reales;
# sin clave usa el fallback léxico por arquetipo
```

---
*Rubicón Lab · Agosto 2026*
