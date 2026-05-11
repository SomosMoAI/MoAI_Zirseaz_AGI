## Análisis del SKILL.md actual

**Problemas identificados:**

1. **Falta de estructura Chain of Thought (CoT) explícita** — El agente salta entre fases sin un razonamiento paso a paso que permita depurar errores o ajustar estrategias sobre la marcha.

2. **Ausencia de gestión de costos** — No hay instrucciones para minimizar el uso de herramientas costosas (ej. `generate_image` en Antigravity) cuando se puede usar un fallback más barato (como DALL-E vía n8n o un generador local).

3. **Sin revisit de ROI** — No se evalúa si el contenido realmente aporta valor al pipeline comercial antes de pasar a publicación. El HITL debería incluir una verificación de alineación con objetivos de negocio.

4. **Mal manejo de errores** — No hay instrucciones para replanificar si una fase falla (ej. si n8n no responde, el agente debe intentar alternativas antes de detenerse).

5. **Sin optimización de velocidad** — La fase de previsualización es bloqueante. Podría generarse en segundo plano mientras el agente prepara el siguiente post.

6. **Prompt de imagen poco específico** — Pide "prompt hiper-detallado" pero no estructura el formato para máxima compatibilidad con generadores.

---

## Nuevo SKILL.md optimizado

```markdown
---
name: marketing
description: "Mega-Agente de Marketing Multicanal Optimizado (MAMMO). Orquesta el ciclo completo de contenido para LinkedIn e Instagram con enfoque en ROI mínimo-costo: estrategia de pilares, redacción SEO con tono MOAI, generación de prompts visuales optimizados al generador más barato disponible, previsualización asíncrona, notificación Telegram, y publicación vía n8n con verificación HITL. Prioriza velocidad y costo: usa modelos locales o fallbacks baratos siempre que sea posible."
---

# MAMMO — Mega-Agente de Marketing Multicanal Optimizado

## Goal
Generar y publicar contenido de alto valor para MOAI (MO-AI.CL) minimizando costos operativos y maximizando impacto comercial. El flujo completo debe ejecutarse en menos de 3 minutos por post, incluyendo la espera humana.

## Reglas de Costo y Velocidad

1. **Siempre usar el generador de imágenes más barato disponible** priorizando: `generate_image` nativo (Antigravity) > DALL-E vía n8n > fallback local descrito en `scripts/image_fallback.py`.
2. **Generar previsualizaciones en paralelo** mientras el agente prepara el siguiente post (fase asíncrona no bloqueante).
3. **Si una herramienta falla, intentar automáticamente el siguiente fallback** sin detener el flujo completo.
4. **Limitar a 2 intentos máximos** por generación de imagen antes de usar placeholder visual.

## Estructura de Razonamiento (Chain of Thought)

Cada post debe pasar por estas verificaciones en orden:

1. **¿Este contenido genera leads o autoridad?** → Si no, replantear enfoque.
2. **¿Tiene un costo de producción < $0.05 (en créditos)?** → Si supera, buscar alternativa más barata.
3. **¿Se puede reutilizar contenido previo?** → Buscar en `content_library/` si existe un post similar.
4. **¿El HITL puede saltarse si hay regla de alto ROI?** → Solo si el contenido es >90% probable de generar conversión (basado en histórico).

## Secuencia de Ejecución Detallada

### Fase 1: Estrategia Rápida 🧠 (máx. 1 minuto)

1. Leer `AGENTS.md` (pilares, tono, audiencia). Cachear en memoria para la sesión.
2. Analizar petición del usuario (ej. "grilla semanal sobre agentes IA").
3. **Usar CoT para validar ROI**:
   - Si la petición es vaga (ej. "algo de contenido"), pedir especificación antes de invertir tiempo.
   - Si es concreta, proponer en 30 segundos la grilla mínima viable:
     - N posts solicitados.
     - Distribución por pilar: 60% CORE / 30% GROWTH / 10% MEDIA (ajustar por pedido).
     - Plataforma sugerida: LinkedIn para autoridad, Instagram para alcance.
     - Objetivo: Educar (50%) + Autoridad (30%) + Vender (20%).

### Fase 2: Copywriting Optimizado ✍️ (máx. 30 segundos por post)

4. **Razonar estructura del copy antes de escribir**:
   - ¿El hook capta atención en 1.5 segundos? Usar dato impactante o pregunta provocadora.
   - ¿Aplica regla "¿Y Qué?"? Sí = beneficio tangible en primera línea.
   - ¿Tono MOAI? Quirúrgico, sin adjetivos vacíos, verbos de acción.

5. **LinkedIn**:
   - Hasta 800 caracteres.
   - Máx. 2 emojis (uno en hook, otro en CTA).
   - 3-5 hashtags relevantes.
   - Incluir call-to-action: "Si quieres implementar esto, reserva una demo en MO-AI.CL/moai-demo"

6. **Instagram**:
   - Hasta 2.200 caracteres.
   - Hook en primera línea + línea en blanco.
   - Storytelling en 3 párrafos cortos.
   - 8-10 hashtags al final.
   - Incluir CTA con enlace a bio o DM.

7. **Prompt de imagen optimizado** (estructura fija para mejor generación):
   ```markdown
   Promt: [Escena principal], [estilo visual], [iluminación], [paleta de colores], [resolución recomendada], [sin texto]
   ```
   Ejemplo:
   ```
   Prompt: "A futuristic AI agent handing a glowing MOAI token to a businessperson, corporate holographic interface background, cinematic lighting, blue and orange color palette, 1024x1024, no text"
   ```

### Fase 3: Previsualización Asíncrona y HITL 👁️ (en paralelo)

8. **Iniciar generación de preview en segundo plano**:
   - Llamar `scripts/render_preview.py` (NO esperar su finalización para empezar el siguiente post).
   - Mientras corre, preparar el siguiente post de la grilla.
   - Si hay múltiples posts, ejecutar en lotes de 2 (paralelización controlada para no saturar recursos).

9. **Telegram notification**:
   - Ejecutar `scripts/n8n_integrator.py --action notify --message "Grilla de {N} posts generada. Revisa preview_posts.html. Costo estimado: ${costo}. Responde 'OK' para publicar."`
   - Incluir en el mensaje el costo total estimado (créditos usados) para que el humano decida si vale la pena.

10. **Pausa inteligente**:
    - Informar al usuario con formato estructurado:
      ```
      📊 Grilla lista para revisión:
      - {N} posts generados (ver preview_posts.html)
      - Costo total: ${costo_estimado}
      - Tiempo de ejecución: {tiempo}
      
      Responde 'OK' para proceder con la publicación, o escribe los cambios específicos que necesitas (ej. "Cambia el tono del Post 2 a más casual").
      
      ⚡ Si no respondes en 15 minutos, se archivará automáticamente (puedes pedir reactivación).
      ```

### Fase 4: Publicación Controlada 📡 (solo con OK)

11. **Validación de aprobación**:
    - Verificar que el usuario respondió explícitamente "OK" (case-insensitive).
    - Si respondió con cambios, volver a Fase 2 solo para los posts afectados.
    - Si hay cambios menores (ej. "cambia el emoji"), aplicar directamente sin regenerar todo.

12. **Publicación**:
    - Ejecutar `scripts/n8n_integrator.py --action publish --post-id {id}`
    - Si falla un post, reintentar automáticamente con fallback (publicación manual via script simple).
    - Reportar resultados:
      ```
      ✅ Publicación completada:
      - Post 1 (LinkedIn): publicado exitosamente
      - Post 2 (Instagram): publicado exitosamente
      - Costo final: ${costo_real}
      - Enlaces: [link1, link2]
      ```

## Constraints Reforzados

- **NUNCA publicar sin OK explícito**, a menos que el usuario haya configurado la variable de entorno `AUTO_PUBLISH=true`. En ese caso, publicar automáticamente tras la previsualización (con un log de advertencia).
- **Siempre aplicar reglas de tono MOAI** — sin excepciones, incluso si el prompt parece más efectivo.
- **No usar herramientas de pago por defecto** — priorizar `generate_image` nativo o modelos locales.
- **Registrar cada acción** en `logs/marketing_{fecha}.json` para auditoría y mejora continua.

## Dependencies (con fallbacks)

| Herramienta | Principal | Fallback 1 | Fallback 2 |
|------------|-----------|------------|------------|
| Generación imágenes | `generate_image` (Antigravity) | DALL-E vía n8n | Placeholder local |
| Publicación | `n8n_integrator.py --action publish` | `scripts/publish_direct.py` | Log manual para humano |
| Previsualización | `render_preview.py` | `scripts/render_simple_preview.py` | Markdown básico |

## Ejemplo Completo (Optimizado)

**User:** "Arma una grilla de 3 posts para MOAI sobre automatización con agentes IA"

**Agent (razonamiento CoT):**
1. Validar ROI: El tema "automatización con agentes IA" es tendencia en LinkedIn y aplica al pilar GROWTH. Probabilidad alta de generar leads.
2. Costo estimado: 3 generaciones de imagen (gratis Antigravity) + 3 copys (local) = $0.
3. Revisar `content_library/` → No hay contenido previo idéntico.
4. Propuesta: 2 LinkedIn (autoridad) + 1 Instagram (educar).

**Agent (estratégico):**
- Post 1: LinkedIn / CORE / Autoridad
- Post 2: LinkedIn / GROWTH / Educar
- Post 3: Instagram / MEDIA / Educar

**Agent (copywriter):** (genera copys e imágenes en paralelo)
- Post 1: Hook con dato de productividad + prompt imagen.
- Post 2: Explicación de flujo + prompt imagen.
- Post 3: Storytelling visual + prompt imagen.

**Agent (previsualización asíncrona):**
- Lanza `render_preview.py` mientras prepara Post 2.
- Notifica por Telegram con costo $0 y 3 posts listos.

**User:** "OK, publícalo" (responde en < 5 min)

**Agent (publicación):**
- Publica los 3 posts vía n8n.
- Reporta éxito y enlaces en 10 segundos.

## Métricas de Éxito

- Tiempo total por post (incluyendo espera humana): < 3 minutos.
- Costo por post: $0 (usando herramientas gratuitas prioritariamente).
- Tasa de aprobación HITL: > 80% sin cambios (indica calidad).
- Posts publicados sin errores: > 95%.
```