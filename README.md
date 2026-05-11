# Proyecto: Automatización de RRSS con Antigravity

Bienvenido a tu Agente Inteligente de Redes Sociales, diseñado bajo los estandares de Antigravity (2026).
Este Agente se compone de dos módulos principales con una validación humana en medio para que **NUNCA** publique nada sin tu revisión (Human-In-The-Loop).

## Estructura del Proyecto

```text
📁 c:\Users\cueva\OneDrive\Escritorio\Agentes\
│
├── 📄 AGENTS.md                  <-- Las "reglas de negocio" (Tono y reglas que el Agente debe respetar)
│
└── 📁 .agents/
    └── 📁 skills/
        ├── 📁 social-content-generator/
        │   └── 📄 SKILL.md       <-- Módulo 1: Crea la grilla, los textos con SEO y los prompts de imágenes. Guardará todo en un archivo temporal.
        │
        └── 📁 social-publisher/
            ├── 📄 SKILL.md       <-- Módulo 2: Lee el contenido aprobado y orquesta el posteo automatizado.
            └── 📁 scripts/
                └── 📄 deploy_post.py  <-- Este script enviará el posteo a tu Webhook de Make.com o conexión externa.
```

## ¿Cómo utilizar este Agente?

Es tan simple como abrir tu chat de agente en Antigravity y decirle:

> *"Utilizando tus skills, crea una grilla de 1 post para LinkedIn sobre la nueva tendencia de Machine Learning"*

El agente utilizará el módulo `social-content-generator`, y terminará creando un archivo `revision_rrss.md`.

## Validación Humana y Despliegue

La política del `social-publisher` prohíbe el auto-despliegue. Una vez que hayas leído el documento, para postear simplemente escríbele en tu chat:

> *"Ya revisé la grilla. Puedes proceder y usar tu skill de distribución para postearlo"*

### NOTA TÉCNICA PARA DESPLIEGUE FINAL (Integración Make.com)
Si deseas publicarlo literalmente en tus cuentas, abre `.agents/skills/social-publisher/scripts/deploy_post.py` y reemplaza la variable `MAKE_WEBHOOK_URL` por de tu webhook en Make.com que creamos en el proyecto pasado (_fd2a177e-ffc4-4c49-8365-a39b72545fc1_).
