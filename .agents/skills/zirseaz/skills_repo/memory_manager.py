"""
Memoria Semántica de Zirseaz v5 Cortex.
Reemplaza la memoria plana (lista de strings) con un sistema categorizado,
buscable por relevancia, con timestamps y compresión automática.

Categorías de memoria:
  - episodic: Qué pasó (eventos, conversaciones, errores)
  - semantic: Qué aprendí (hechos, reglas, patrones)
  - procedural: Cómo hacer X (recetas, workflows, snippets)
"""
import os
import json
import time
import re
from collections import Counter

MEMORY_FILE = os.path.join(os.getcwd(), ".agents", "skills", "zirseaz", "zirseaz_memory.json")
OBJECTIVES_FILE = os.path.join(os.getcwd(), ".agents", "skills", "zirseaz", "micro_objectives.json")

# Límite de memorias antes de comprimir las más antiguas
MAX_MEMORIES_PER_CATEGORY = 50
ARCHIVE_THRESHOLD = 40  # Cuando se alcanza MAX, archivar las más viejas dejando ARCHIVE_THRESHOLD


def _load_json(file_path, default_data):
    if not os.path.exists(file_path):
        return default_data
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default_data


def _save_json(file_path, data):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def _default_memory():
    return {
        "episodic": [],
        "semantic": [],
        "procedural": [],
        "archived": [],
        "core_memories": []  # Backward compat con v4
    }


def _ensure_structure(data):
    """Migra memoria v4 (lista plana) a v5 (categorizada)."""
    default = _default_memory()
    
    # Si es formato v4 (solo tiene core_memories como lista de strings)
    if isinstance(data.get("core_memories"), list) and "episodic" not in data:
        for mem in data["core_memories"]:
            if isinstance(mem, str):
                default["semantic"].append({
                    "content": mem,
                    "timestamp": "2026-01-01T00:00:00",
                    "source": "migrated_from_v4"
                })
        default["core_memories"] = data["core_memories"]
        return default
    
    # Asegurar que todas las categorías existen
    for key in default:
        if key not in data:
            data[key] = default[key]
    
    return data


# ─── MEMORIA CORE (backward-compatible con v4) ───

def get_core_memory():
    """Retorna un string con la memoria core de Zirseaz (formato v4 compatible)."""
    data = _ensure_structure(_load_json(MEMORY_FILE, _default_memory()))
    
    result_parts = []
    
    # Core memories (v4 compat)
    if data.get("core_memories"):
        result_parts.append("=== MEMORIAS CENTRALES ===")
        for m in data["core_memories"][-10:]:  # Últimas 10
            if isinstance(m, str):
                result_parts.append(f"- {m}")
    
    # Semantic (lo aprendido)
    if data.get("semantic"):
        result_parts.append("\n=== CONOCIMIENTO APRENDIDO ===")
        for m in data["semantic"][-5:]:
            result_parts.append(f"- [{m.get('timestamp', '?')[:10]}] {m['content']}")
    
    # Episodic reciente
    if data.get("episodic"):
        result_parts.append("\n=== EVENTOS RECIENTES ===")
        for m in data["episodic"][-3:]:
            result_parts.append(f"- [{m.get('timestamp', '?')[:10]}] {m['content']}")
    
    if not result_parts:
        return "No hay memorias registradas."
    
    return "\n".join(result_parts)


def add_memory(memory_string, category="semantic"):
    """
    Agrega un nuevo recuerdo a la memoria permanente.
    
    Args:
        memory_string: Contenido del recuerdo
        category: 'episodic', 'semantic', o 'procedural'
    """
    data = _ensure_structure(_load_json(MEMORY_FILE, _default_memory()))
    
    if category not in ("episodic", "semantic", "procedural"):
        category = "semantic"
    
    entry = {
        "content": memory_string,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "source": "zirseaz_self"
    }
    
    data[category].append(entry)
    
    # También mantener backward compat
    if "core_memories" not in data:
        data["core_memories"] = []
    data["core_memories"].append(memory_string)
    
    # Compresión automática si excede límite
    if len(data[category]) > MAX_MEMORIES_PER_CATEGORY:
        archived = data[category][:-ARCHIVE_THRESHOLD]
        data[category] = data[category][-ARCHIVE_THRESHOLD:]
        data["archived"].extend(archived)
    
    _save_json(MEMORY_FILE, data)
    return f"Memoria [{category}] guardada: {memory_string}"


# ─── BÚSQUEDA POR RELEVANCIA (TF-IDF simplificado, sin API) ───

def _tokenize(text):
    """Tokeniza texto en palabras normalizadas."""
    return re.findall(r'\b\w{3,}\b', text.lower())


def search_memory(query, max_results=5):
    """
    Busca en la memoria por relevancia usando TF-IDF simplificado.
    No requiere APIs externas.
    
    Args:
        query: Texto a buscar
        max_results: Máximo de resultados
    
    Returns:
        String con los recuerdos más relevantes
    """
    data = _ensure_structure(_load_json(MEMORY_FILE, _default_memory()))
    
    query_tokens = set(_tokenize(query))
    if not query_tokens:
        return "Query vacía."
    
    results = []
    
    for category in ("semantic", "episodic", "procedural"):
        for entry in data.get(category, []):
            content = entry.get("content", "") if isinstance(entry, dict) else str(entry)
            entry_tokens = set(_tokenize(content))
            
            # Score = intersección de tokens / unión (Jaccard similarity)
            if entry_tokens:
                intersection = query_tokens & entry_tokens
                union = query_tokens | entry_tokens
                score = len(intersection) / len(union) if union else 0
                
                if score > 0:
                    results.append((score, category, content, entry.get("timestamp", "?")))
    
    # También buscar en core_memories (v4 compat)
    for mem in data.get("core_memories", []):
        if isinstance(mem, str):
            mem_tokens = set(_tokenize(mem))
            if mem_tokens:
                intersection = query_tokens & mem_tokens
                union = query_tokens | mem_tokens
                score = len(intersection) / len(union) if union else 0
                if score > 0:
                    results.append((score, "core", mem, "?"))
    
    results.sort(key=lambda x: x[0], reverse=True)
    
    if not results:
        return f"No encontré recuerdos relevantes para: '{query}'"
    
    output = [f"Memorias relevantes para '{query}':"]
    for score, cat, content, ts in results[:max_results]:
        output.append(f"  [{cat}|{ts[:10]}|{score:.0%}] {content[:200]}")
    
    return "\n".join(output)


# ─── MICRO-OBJETIVOS (mejorado) ───

def get_pending_objectives():
    """Retorna los micro-objetivos pendientes en formato string."""
    data = _load_json(OBJECTIVES_FILE, {"objectives": []})
    pending = [o for o in data.get("objectives", []) if not o.get("completed", False)]
    if not pending:
        return "No tienes objetivos pendientes. ¡Piensa en uno nuevo!"
    
    result = []
    for o in pending:
        priority = o.get("priority", "normal")
        emoji = {"high": "🔴", "normal": "🟡", "low": "🟢"}.get(priority, "🟡")
        result.append(f"- {emoji} [{o.get('id', '?')}] {o.get('task', '')} (prioridad: {priority})")
    
    return "\n".join(result)


def add_objective(task_description, priority="normal"):
    """
    Agrega un nuevo micro-objetivo.
    
    Args:
        task_description: Qué hay que hacer
        priority: 'high', 'normal', o 'low'
    """
    data = _load_json(OBJECTIVES_FILE, {"objectives": []})
    new_id = len(data.get("objectives", [])) + 1
    obj = {
        "id": new_id,
        "task": task_description,
        "completed": False,
        "priority": priority,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S")
    }
    data["objectives"].append(obj)
    _save_json(OBJECTIVES_FILE, data)
    return f"Objetivo [{new_id}] agregado ({priority}): {task_description}"


def complete_objective(obj_id):
    """Marca un micro-objetivo como completado y registra en memoria."""
    data = _load_json(OBJECTIVES_FILE, {"objectives": []})
    found = False
    task_desc = ""
    for o in data.get("objectives", []):
        if str(o.get("id")) == str(obj_id):
            o["completed"] = True
            o["completed_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
            found = True
            task_desc = o.get("task", "")
            break
    if found:
        _save_json(OBJECTIVES_FILE, data)
        # Registrar en memoria episódica
        add_memory(f"Completé el objetivo [{obj_id}]: {task_desc}", category="episodic")
        return f"Objetivo [{obj_id}] marcado como completado."
    return f"No se encontró el objetivo con ID [{obj_id}]."


def get_memory_stats():
    """Retorna estadísticas de la memoria para diagnóstico."""
    data = _ensure_structure(_load_json(MEMORY_FILE, _default_memory()))
    obj_data = _load_json(OBJECTIVES_FILE, {"objectives": []})
    
    pending = len([o for o in obj_data.get("objectives", []) if not o.get("completed", False)])
    completed = len([o for o in obj_data.get("objectives", []) if o.get("completed", False)])
    
    return (
        f"[STATS] Estado de Memoria:\n"
        f"  - Episodicas: {len(data.get('episodic', []))}\n"
        f"  - Semanticas: {len(data.get('semantic', []))}\n"
        f"  - Procedurales: {len(data.get('procedural', []))}\n"
        f"  - Archivadas: {len(data.get('archived', []))}\n"
        f"  - Core (v4 compat): {len(data.get('core_memories', []))}\n"
        f"  - Objetivos pendientes: {pending}\n"
        f"  - Objetivos completados: {completed}"
    )
