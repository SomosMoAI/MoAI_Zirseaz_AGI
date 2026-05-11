"""
Zirseaz Goal Decomposition — Descompone objetivos complejos en sub-pasos.

Cuando se agrega un micro-objetivo complejo, lo analiza y genera sub-objetivos
más pequeños y accionables automáticamente.
"""
import os, sys, re

_SKILL_ROOT = os.path.join(os.getcwd(), ".agents", "skills", "zirseaz")
_SKILLS_REPO = os.path.join(_SKILL_ROOT, "skills_repo")
if _SKILLS_REPO not in sys.path:
    sys.path.insert(0, _SKILLS_REPO)


def estimate_complexity(task_description):
    """Estima la complejidad de un objetivo (1-5)."""
    text = task_description.lower()
    score = 1
    
    # Señales de complejidad
    complex_words = ["crear", "construir", "investigar", "analizar", "pipeline",
                     "completo", "integrar", "desplegar", "arquitectura", "sistema"]
    score += sum(1 for w in complex_words if w in text)
    
    # Longitud
    if len(text.split()) > 15: score += 1
    if len(text.split()) > 30: score += 1
    
    return min(score, 5)


def decompose_objective(task_description):
    """
    Descompone un objetivo en sub-pasos basándose en heurísticas.
    Para descomposición más inteligente, usar el LLM via Cortex.
    
    Returns:
        Lista de sub-objetivos si es complejo, o None si es simple
    """
    complexity = estimate_complexity(task_description)
    
    if complexity <= 2:
        return None  # Suficientemente simple, no descomponer
    
    text = task_description.lower()
    steps = []
    
    # Heurística: si contiene "y", separar
    if " y " in text:
        parts = text.split(" y ")
        for i, part in enumerate(parts):
            steps.append(f"Sub-paso {i+1}: {part.strip().capitalize()}")
    
    # Heurística: si menciona investigar + crear
    if "investigar" in text or "buscar" in text:
        steps.append("Investigacion: Buscar informacion relevante")
    if "crear" in text or "construir" in text or "generar" in text:
        steps.append("Construccion: Implementar la solucion")
    if "desplegar" in text or "deploy" in text:
        steps.append("Despliegue: Publicar el resultado")
    if "test" in text or "verificar" in text or "probar" in text:
        steps.append("Verificacion: Comprobar que funciona")
    
    # Si no se generaron pasos heurísticos, crear genéricos por complejidad
    if not steps:
        steps = [
            "Paso 1: Analizar requisitos y contexto",
            f"Paso 2: {task_description}",
            "Paso 3: Verificar resultado"
        ]
    
    return steps


def smart_add_objective(task_description, priority="normal"):
    """
    Agrega un objetivo con auto-descomposición si es complejo.
    
    Returns:
        String con el resultado
    """
    import memory_manager
    
    complexity = estimate_complexity(task_description)
    sub_steps = decompose_objective(task_description)
    
    if sub_steps and complexity >= 3:
        # Agregar objetivo padre
        result = memory_manager.add_objective(f"[META] {task_description}", priority)
        results = [result]
        
        # Agregar sub-objetivos
        sub_priority = "normal" if priority == "high" else "low"
        for step in sub_steps:
            r = memory_manager.add_objective(step, sub_priority)
            results.append(r)
        
        return (
            f"Objetivo complejo (complejidad {complexity}/5) descompuesto en {len(sub_steps)} sub-pasos:\n"
            + "\n".join(results)
        )
    else:
        result = memory_manager.add_objective(task_description, priority)
        return f"Objetivo simple agregado (complejidad {complexity}/5):\n{result}"
