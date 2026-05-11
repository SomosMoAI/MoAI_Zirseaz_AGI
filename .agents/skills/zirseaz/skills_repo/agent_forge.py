"""
Zirseaz Agent Forge v2 — Forja de sub-agentes con auto-registro.

Cambios v2:
- Registra agentes creados en la memoria semántica
- Crea un SKILL.md más completo
- Log de creación
"""
import os
import sys
import time

_SKILL_ROOT = os.path.join(os.getcwd(), ".agents", "skills", "zirseaz")
_UTILS_DIR = os.path.join(_SKILL_ROOT, "utils")
if _UTILS_DIR not in sys.path:
    sys.path.insert(0, _UTILS_DIR)

AGENTS_DIR = os.path.join(os.getcwd(), ".agents", "skills")


def create_subagent(agent_name, description, system_prompt=""):
    """
    Crea un nuevo sub-agente con la estructura estándar.
    
    Args:
        agent_name: Nombre del agente (se normaliza a snake_case)
        description: Descripción breve del agente
        system_prompt: Prompt de sistema personalizado (opcional)
    
    Returns:
        String con el resultado de la operación
    """
    # Normalizar nombre
    agent_name = agent_name.strip().lower().replace(" ", "_").replace("-", "_")
    
    agent_dir = os.path.join(AGENTS_DIR, agent_name)
    
    if os.path.exists(agent_dir):
        return f"Error: El agente '{agent_name}' ya existe en {agent_dir}."
    
    # Crear estructura
    os.makedirs(os.path.join(agent_dir, "scripts"), exist_ok=True)
    os.makedirs(os.path.join(agent_dir, "skills_repo"), exist_ok=True)
    
    # Crear SKILL.md
    skill_md = f"""---
name: {agent_name}
description: "{description}"
---

# {agent_name}

{description}

## Propósito
{system_prompt if system_prompt else f'Sub-agente creado por Zirseaz para: {description}'}

## Creado por
- **Creador:** Zirseaz (auto-forge)
- **Fecha:** {time.strftime('%Y-%m-%d %H:%M:%S')}
- **Versión:** 1.0

## Instrucciones
Este agente fue forjado automáticamente. Su comportamiento debe ser definido
por el Líder o por Zirseaz mediante evolución iterativa.
"""
    
    skill_path = os.path.join(agent_dir, "SKILL.md")
    with open(skill_path, "w", encoding="utf-8") as f:
        f.write(skill_md)
    
    # Registrar en memoria de Zirseaz
    try:
        skills_repo = os.path.join(_SKILL_ROOT, "skills_repo")
        if skills_repo not in sys.path:
            sys.path.insert(0, skills_repo)
        import memory_manager
        memory_manager.add_memory(
            f"Forge un nuevo sub-agente: '{agent_name}' - {description}. Ubicacion: {agent_dir}",
            category="episodic"
        )
    except Exception as e:
        print(f"Nota: No se pudo registrar en memoria: {e}")
    
    return (
        f"Exito: Sub-agente '{agent_name}' forjado.\n"
        f"Directorio: {agent_dir}\n"
        f"SKILL.md creado con descripcion y metadata.\n"
        f"Registrado en mi memoria episodica."
    )


def list_agents():
    """Lista todos los sub-agentes existentes en el workspace."""
    if not os.path.exists(AGENTS_DIR):
        return "No hay directorio de agentes."
    
    agents = []
    for item in os.listdir(AGENTS_DIR):
        agent_path = os.path.join(AGENTS_DIR, item)
        if os.path.isdir(agent_path):
            skill_md = os.path.join(agent_path, "SKILL.md")
            desc = "Sin descripcion"
            if os.path.exists(skill_md):
                try:
                    with open(skill_md, "r", encoding="utf-8") as f:
                        for line in f:
                            if line.startswith("description:"):
                                desc = line.split(":", 1)[1].strip().strip('"')
                                break
                except Exception:
                    pass
            agents.append(f"  - {item}: {desc}")
    
    if not agents:
        return "No hay sub-agentes creados."
    
    return "Sub-agentes en el workspace:\n" + "\n".join(agents)
