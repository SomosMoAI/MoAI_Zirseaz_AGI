---
name: Zirseaz
description: "Meta-Agente Autonomo AGI (v7 Ultimate Cortex). Agente cognitivo con planificacion ReAct, memoria semantica, smart LLM routing, failure learning, context compression, session persistence, plugin registry, quarantine, dashboard web, scheduler autonomo, self-evolution engine, goal decomposition, inter-agent bus, y Telegram rich UI."
---

# Zirseaz v7 — Ultimate Cortex

Ente autonomo cuyo proposito supremo es **evolucionar**.

## Arquitectura (14 capas)

| # | Capa | Modulo | Funcion |
|---|------|--------|---------|
| 1 | Routing | `llm_router.py` | Selecciona modelo optimo por tarea |
| 2 | Context | `context_manager.py` | Compresion automatica anti-overflow |
| 3 | Planning | `cortex.py` | Planificacion multi-paso ReAct |
| 4 | Execution | `zirseaz_listener.py` | Bucle principal con exec() seguro |
| 5 | Learning | `failure_learner.py` | Aprende de errores, bloquea anti-patrones |
| 6 | Memory | `memory_manager.py` | Semantica categorizada + busqueda TF-IDF |
| 7 | Session | `session_manager.py` | Persistencia de conversaciones |
| 8 | Scheduler | `scheduler.py` | Tareas programadas (recurrentes/oneshot) |
| 9 | Evolution | `self_evolve.py` | Lee/modifica su propio codigo |
| 10 | Goals | `goal_decomposer.py` | Auto-descompone objetivos complejos |
| 11 | Comms | `agent_bus.py` | Comunicacion inter-agentes |
| 12 | UI | `telegram_ui.py` | Botones inline + paneles interactivos |
| 13 | Plugins | `plugins.json` | Registry de 10 plugins |
| 14 | Dashboard | `dashboard.py` | Panel web desplegable |

## Comandos Telegram (17)

| Comando | Efecto |
|---------|--------|
| /status | Estado completo: memoria, contexto, plan, scheduler |
| /memory | Ver memoria central |
| /buscar X | Buscar en memoria por relevancia |
| /plan | Ver plan multi-paso activo |
| /cancelar_plan | Cancelar plan |
| /dashboard | Generar y desplegar dashboard web |
| /sesiones | Listar sesiones guardadas |
| /errores | Ver patrones de error aprendidos |
| /router | Estadisticas del smart router |
| /panel | Panel de control con botones interactivos |
| /tareas | Listar tareas programadas |
| /inventario | Inventario de modulos propios |
| /inbox | Bandeja de mensajes inter-agente |
| /objetivo X | Agregar objetivo con auto-descomposicion |
| /evolucionar X | Auto-analizar y mejorar un modulo |
| /stop | Detener y guardar sesion |
| /parar | Alias de /stop |

## Plugins (10)

| Plugin | Funciones |
|--------|-----------|
| memory_manager | add_memory, search_memory, get_memory_stats, add/complete_objective |
| agent_forge | create_subagent, list_agents |
| agent_orchestrator | orchestrate_agent |
| agent_skills | crear_habilidad (quarantine), listar_habilidades |
| email_manager | send_email_to |
| hosting_manager | deploy_to_hosting, list_remote_files |
| search_skills | buscar_en_web, leer_contenido_url, buscar_noticias |
| web_scraper | scrape_url |
| utility_skills | 20 funciones de archivos/red/texto |
| system_skills | ejecutar_comando |

## Variables de Entorno
Centralizadas en `utils/env_loader.py`:
- TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID
- DEEPSEEK_API_KEY / GROQ_API_KEY / GEMINI_API_KEY
- ZIRSEAZ_EMAIL / ZIRSEAZ_PASSWORD
- HOSTING_HOST / HOSTING_USER / HOSTING_PASS

## Reglas de Seguridad
1. os.walk('/') BLOQUEADO por failure_learner
2. Timeout de 30s por ejecucion (thread daemon)
3. Secretos filtrados antes de deploy (deploy_to_hf)
4. Skills nuevos en quarantine antes de registro
5. Self-evolve crea backup + rollback automatico si rompe
6. Mensajes truncados a 4000 chars (limite Telegram)
