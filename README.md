# Zirseaz AGI — La IA Hija de Zirseaz

Bienvenido a la **infraestructura** de la IA Hija de Zirseaz. Este repositorio contiene la **arquitectura** de un Meta-Agente Autónomo diseñado para operar con máxima **eficiencia** y **rentabilidad** en tareas de marketing multicanal y automatización de procesos.

Este proyecto es un sistema **Plug & Play**. Para interactuar con este agente y desplegar su potencial, necesitas dotarlo de sus propios accesos y canales de comunicación.

## 🧠 Arquitectura y Enfoque

Zirseaz AGI está diseñado bajo el pilar de la autonomía controlada (**Human-In-The-Loop**). El agente propone y orquesta, pero el humano mantiene el control final.

### Capacidades Core:
- **Operaciones & Data**: Automatización de procesos y manejo de información estructurada.
- **Growth**: Generación de contenido estratégico y adquisición programática.
- **Media**: Orquestación de copys y prompts para contenido sintético.

## 🚀 Despliegue Rápido (Protocolo Plug & Play)

Para poner a operar a la IA Hija de Zirseaz, sigue este protocolo de configuración:

### 1. Clonar el Repositorio
```bash
git clone https://github.com/SomosMoAI/MoAI_Zirseaz_AGI.git
cd MoAI_Zirseaz_AGI
```

### 2. Blindaje de Credenciales (Archivo .env)
El sistema requiere un archivo `.env` para operar de manera segura. Este archivo contiene tus secretos y **NUNCA** debe ser subido a repositorios públicos.

1. Crea tu archivo `.env` a partir de la plantilla:
   ```bash
   cp .env.example .env
   ```
2. Abre el archivo `.env` y completa tus datos:
   - **Telegram Chatbot**: Para hablar conmigo y recibir notificaciones, necesitas crear un bot en Telegram. Habla con `@BotFather` para obtener tu `TELEGRAM_BOT_TOKEN`. Luego, obtén tu `TELEGRAM_CHAT_ID` hablando con `@userinfobot`.
   - **Correo Electrónico**: Ya configurado en el sistema para envíos automáticos.
   - **APIs y Webhooks**: Configura las URLs de tus webhooks (por ejemplo, en n8n) para las tareas de generación de imágenes y publicación automatizada.

## 📡 Modularidad y Skills

Este agente opera mediante un sistema de **Skills** modulares ubicadas en la carpeta `.agents/skills/`. Puedes activar, modificar o expandir estas capacidades según la necesidad de tu negocio.

---
*Desarrollado bajo los estándares de ingeniería de MOAI.*
