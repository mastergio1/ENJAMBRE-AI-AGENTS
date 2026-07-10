# El Enjambre 🐝

Simulador de escenarios del mercado bursátil: ingresas una noticia y observas en una escena 3D cómo 5.000 inversionistas simulados reaccionan — el pánico se contagia, las manadas se forman, el precio emerge.

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

**Etapa 1 completada** — el motor simula los 5.000 agentes sobre un libro de órdenes real y reproduce los 5 hechos estilizados de mercados reales (tests en `engine/validation/`). Ver el roadmap en [CLAUDE.md](CLAUDE.md#9-roadmap-referencia-rápida).

Para explorar el mercado simulado:

```bash
cd engine && source .venv/bin/activate
python simular.py 42   # corre una sesión y reporta los hechos estilizados
```

---
*Rubicón Lab · Julio 2026*
