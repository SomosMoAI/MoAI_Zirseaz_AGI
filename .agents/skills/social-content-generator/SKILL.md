---
name: social-content-generator
description: Generates a complete social media content grid, writes SEO optimized text for social networks (like Instagram and LinkedIn), and drafts image prompts. It outputs the finalized post blueprints into a reviewable Markdown document.
---

# Generador de Grilla y Contenido RRSS (Social Content Generator)

## Goal
Crear una grilla de contenido basada en el requerimiento del usuario y generar la redacción (copy) más los visuales que la componen. El agente NO publicará nada, simplemente formateará la idea lista para revisión.

## Instructions
1. Analizar el nicho o tema que solicita el usuario (ej. "Quiero RRSS de IA").
2. Pensar en 3 pilares de contenido según el tema.
3. Generar una **Grilla de X Posts** (según solicite el usuario). Para cada post, especifica:
    - **Plataforma:** (Instagram o LinkedIn).
    - **Objetivo:** (Educar, Entretener, Vender).
    - **Copys/Textos:** El texto final de la publicación utilizando buen SEO y ganchos.
    - **Visual/Prompt:** El prompt de generación de imagen (bastante detallado en inglés de ser posible, listo para un motor LLM o imagen).
4. Guardarás el resultado completo en un archivo llamado `revision_rrss.md` en el directorio actual.
5. Luego, infórmale al usuario: *"He generado tu contenido en revision_rrss.md. Por favor revisa los textos e imágenes. Si estás conforme con esto, pídeme que lo publique a través de la interfaz de 'social-publisher'."*

## Constraints
- **NO DEBES PUBLICAR** mediante APIs externas. Sólo creas el esquema.
- Cumplir estrictamente con las directrices de `AGENTS.md`.

## Example
**User:** Genera 1 post de prueba para LinkedIn sobre "Agentes IA en 2026"  
**Agent Action:** Crea el markdown con el copy SEO exacto ("Descubre el futuro de la IA...") y el prompt generador ("A futuristic glowing robotic node..."). Finalmente notifica al usuario.
