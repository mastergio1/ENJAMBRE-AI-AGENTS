# Plan de aquí al sábado — ETMday (21 nov 2026) · v2

> Para Giorgio. Hoy es **martes 17 nov**; el evento es **sábado 21** (5 min por
> inversionista). Actualizado tras cerrar Fase 0 (seguridad), Fase 2 (ciencia) y el
> benchmark de Fase 3. La meta de estos días NO es agregar features arriesgadas:
> es **desplegar lo que importa, que el demo no falle jamás, y que tengas las
> palabras exactas** para vender en 5 minutos.

## El dato clave del repaso (define todo)
- **Motor vivo (Render):** OK, pero corre `main` (commit viejo). **No tiene** el
  arreglo del P0, ni el gating, ni la Ventana A — todo eso está en la rama
  `claude/m-d-file-6z1e63`, probado y en verde, pero **sin desplegar**.
- **Web viva (Vercel):** OK (200).
- **Consecuencia:** la credencial insegura `revisar-pulso-2026` **sigue viva en
  producción**. Hay que desplegar al menos el arreglo de seguridad.

## Las 2 decisiones que solo tú tomas
1. **¿Qué desplegamos antes del sábado?** (ver "Alcance de despliegue" abajo). Mi
   recomendación: **el P0 de seguridad SÍ o SÍ**, y el **gating + badge de convicción**
   si queremos el "80% en índices" visible en el demo. El resto (rigor de
   calibración) NO necesita desplegarse: es la historia de due-diligence, ya vive
   en el repo para que un inversionista técnico la revise.
2. **Los números del pedido (pitch §8):** monto, uso y meta a 6 meses. El guion
   tiene el hueco marcado ⚠️ — nadie más puede ponerlos.

## Alcance de despliegue (elige una)
- **A — Mínimo seguro (recomendado si andamos justos):** solo el **P0 de seguridad**.
  Riesgo casi nulo, quita la credencial expuesta. El demo se ve igual que hoy.
- **B — Demo con el ángulo honesto (recomendado si hay tiempo):** P0 + **gating/
  Ventana A en el backend + badge de convicción en el frontend**. Así el demo
  muestra, cuando el enjambre está muy convencido en un índice, "lectura confiable"
  — el 80% hecho visible. Es la pieza que conecta el rigor con lo que ven.
- **C — Todo:** B + el resto de la rama. Más superficie de cambio a 4 días; solo si
  todo pasa el smoke test del jueves. Lo técnico de calibración no cambia el demo.

## Calendario (bloques reales)

| Día | Bloque | Foco | Entregable |
|---|---|---|---|
| **Mar 17 (hoy)** | — | Repaso + este plan. Decidir alcance de despliegue (A/B/C) | plan v2 ✅ · decisión tomada |
| **Mié 18** | AM | Desplegar el alcance elegido a producción (merge a `main` → Render/Vercel) | P0 vivo · (si B) gating vivo |
| | PM | **Probar el demo en vivo de punta a punta** (3 escenarios, enjambre 3D, entrevista) | lista de bugs |
| **Jue 19** | AM | Arreglar lo que falle en vivo · (si B) **badge de convicción en el frontend** | demo pulido |
| | PM | One-pager para inversionistas · FAQ de objeciones · **tú completas los números del pedido** | one-pager · §8 lleno |
| **Vie 20** | AM | **Smoke test final** + congelar (no más cambios) | checklist en verde |
| | PM | **Ensayo cronometrado contigo** (5 min, con los 3 titulares) | pitch fluido |
| **Sáb 21** | — | **Evento.** Yo en standby por si algo se cae | — |

## Blindaje del demo (lo que puede salir mal en vivo y su cura)
1. **Render dormido** (plan gratis duerme ~15 min): el motor tarda ~1 min en
   despertar → el enjambre aparece "muerto". **Cura:** abrir el link 10 min antes
   del evento para despertarlo; tener el modo demo local como respaldo visible.
2. **Sin saldo de IA** a mitad del evento → los líderes caen al léxico. **Cura:**
   verificar saldo el viernes. (El tope global ahora es **atómico**: aunque mucha
   gente dispare simulaciones en el evento, el gasto no se dispara por carrera.)
3. **WiFi del evento malo** → demo ya cargado y, si se puede, un video de 30 s del
   enjambre como respaldo.
4. **Móvil del inversionista** → confirmar 60fps y que hover/entrevista funcionen
   en táctil (hay degradación elegante; verificar).

## El ángulo honesto del pitch (ajuste fino, §6)
El guion ya es honesto ("medimos, no adivinamos"). Con lo de esta semana podemos
reforzarlo SIN sobre-afirmar: *"medimos nuestro modelo contra el mercado real, y
somos tan rigurosos que detectamos y corregimos nuestras propias fugas de medición.
Donde tenemos señal real —índices, con alta convicción— acertamos la dirección el
~80% de las veces. Donde no, lo decimos: es visualización."* Eso es verdad,
defendible ante la CMF, y desarma al inversionista técnico.

## Fuera de alcance antes del sábado (a propósito)
- Fase 1 (cola durable/workers), Fase 3 (microestructura), Fase 5 (modularizar):
  son la hoja de ruta **post-evento**. No mueven la aguja del sábado.
- Experimento de memoria (RAG), semilla por PDF: después.

---
*Si el sábado algo se cae, el objetivo no es la perfección técnica: es que tú
puedas contar la historia y que el enjambre se vea vivo 30 segundos. Todo lo demás
es secundario ese día.*
