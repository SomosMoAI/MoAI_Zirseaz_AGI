---
name: social-publisher
description: Publica el contenido aprobado de las Redes Sociales enviándolo mediante scripts a las plataformas correspondientes. Debe usarse únicamente cuando el humano ha revisado y aprobado una grilla generada.
manual: true 
---

# Publicador Automatizado RRSS (Social Publisher H-I-T-L)

## Goal
Toma un archivo pre-existente con contenido aprobado por el humano (por ejemplo `revision_rrss.md`) y procede a ejecutar un script local que "orquesta" el posteo publicándolo en Make.com o la API deseada.

## Instructions
1. Verifica que el humano ha revisado el documento, o si dio la orden afirmativa (Ej: "Dale, publícalo").
2. Lee el contenido estructurado que el usuario ha aprobado.
3. Extrae la Plataforma, El Texto y la Imagen/URL de imagen.
4. Invoca el script `scripts/deploy_post.py` (bajo confirmación del IDE o política Manual de HITL) con los argumentos adecuados.
5. Emite un resumen del estado del webhook y celebra la automatización con un mensaje agradable para el humano.

## Execution Constraints
- Este Skill depende intrínsecamente del permiso explícito. Si alguna directriz de Auto-Execution de Antigravity o el IDE frena el script, diles que eso está diseñado A PROPÓSITO para esperar confirmación del humano.

## Execution Command
Te basarás en ejecutar esto:
`python .agents/skills/social-publisher/scripts/deploy_post.py --platform "<plataforma>" --text "<copy resumido>"`
