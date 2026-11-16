# Plan de aquí al sábado — ETMday (21 nov 2026)

> Para Giorgio. Hoy es **lunes 16 nov**; el evento es **sábado 21** (5 min por
> inversionista). La meta de estos días NO es agregar features nuevas, sino que
> **el demo no falle jamás** y que **tengas las palabras exactas** para vender en
> 5 minutos. Lo técnico de modelo (calibración, memoria) ya no mueve la aguja del
> evento: lo que la mueve es el demo y tu relato.

## Principio
Antes del sábado: **cero features nuevas arriesgadas**. Solo (1) desplegar lo ya
construido y probado, (2) blindar el demo contra todo lo que pueda salir mal en
vivo, y (3) darte un guion y un libreto de demo que puedas repetir dormido.

## Calendario

| Día | Foco | Entregable |
|---|---|---|
| **Lun 16** | Cerrar Fase 1 (doomer, en curso, sola) · guion de pitch · plan | `pitch-etmday.md` ✅ · este plan ✅ |
| **Mar 17** | Desplegar TODO (entrevista + doomer) a producción · probar el demo en vivo de punta a punta | demo en vivo verificado · bugs listados |
| **Mié 18** | Arreglar lo que falle en vivo · 3 escenarios pre-cargados "asesinos" para el demo · plan B si Render duerme | demo pulido · libreto de demo |
| **Jue 19** | Una página para inversionistas (one-pager) · FAQ de objeciones · tú ensayas el pitch | one-pager · FAQ |
| **Vie 20** | Smoke test final · congelar (no más cambios) · ensayo cronometrado contigo | checklist final en verde |
| **Sáb 21** | **Evento.** Yo en standby por si algo se cae | — |

## Lo que hay que desplegar (gate: cuando termine el A/B del doomer)
- **Entrevistar a un líder** (Fase 2, ya en la rama, build OK). Desplegar reinicia
  Render, por eso espera a que no haya medición en vuelo.
- **`peso_doomer_por_mercado`** según lo que mida la Fase 1 (acción/oro/petróleo).
- Tras desplegar: probar la IA de la entrevista en vivo (la sesión no puede, Render sí).

## Blindaje del demo (lo que puede salir mal en vivo y su cura)
1. **Render dormido** (plan gratis duerme a los ~15 min): el motor tarda ~1 min en
   despertar → el enjambre aparece "muerto". **Cura:** despertarlo 10 min antes del
   evento (abrir el link) y/o dejar el modo demo local como respaldo visible.
2. **Sin saldo de IA** a mitad del evento → los líderes caen al léxico. **Cura:**
   verificar saldo el viernes; el tope global no debe cortar en pleno demo.
3. **WiFi del evento malo** → tener el demo corriendo ya cargado y, si se puede,
   un video de 30 s del enjambre como respaldo.
4. **Móvil del inversionista** → confirmar 60fps y que el hover/entrevista funcione
   en pantalla táctil (ya hay degradación elegante; verificar).

## Fuera de alcance antes del sábado (a propósito)
- Experimento de **memoria (RAG/Lever B)** — grande e incierto, va después.
- Semilla por **PDF** — útil para vender, pero no indispensable para el demo; si
  sobra tiempo el jueves, se evalúa.

---
*Si el sábado algo se cae, el objetivo no es la perfección técnica: es que tú
puedas contar la historia y que el enjambre se vea vivo 30 segundos. Todo lo
demás es secundario ese día.*
