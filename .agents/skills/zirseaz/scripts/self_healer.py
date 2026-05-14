"""
Zirseaz Self-Healing Engine — Recuperacion automatica de errores.

Intercepta errores de ejecucion en el loop de ReAct, envia el stacktrace al LLM
junto con el codigo original, y solicita una correccion. Se reintenta hasta N veces.
"""
import os, sys, time

_SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_UTILS_DIR = os.path.join(_SKILL_ROOT, "utils")
_SCRIPTS_DIR = os.path.join(_SKILL_ROOT, "scripts")
for _d in [_UTILS_DIR, _SCRIPTS_DIR]:
    if _d not in sys.path:
        sys.path.insert(0, _d)

import env_loader
import llm_router


def attempt_heal(original_code, error_output, model_name=""):
    """
    Solicita al LLM que arregle el codigo que fallo.
    
    Args:
        original_code: Codigo Python que fallo
        error_output: Mensaje de error / stacktrace
        model_name: Modelo actual (usado como hint, no obligatorio)
    
    Returns:
        str con codigo corregido, o None si falla
    """
    system_prompt = (
        "Eres el motor de auto-reparacion de Zirseaz. "
        "Se ejecuto un codigo Python que fallo con un error. "
        "Tu unica tarea es reescribir el codigo para que funcione correctamente.\n\n"
        "REGLAS:\n"
        "1. Devuelve SOLO codigo Python, nada mas.\n"
        "2. No uses formato markdown (```python), solo el codigo crudo.\n"
        "3. Maneja excepciones si es necesario.\n"
        "4. No cambies la logica, solo arregla el error."
    )
    
    user_prompt = f"CODIGO ORIGINAL:\n{original_code}\n\nERROR:\n{error_output}\n\nREESCRITURA CORRECTA:"
    
    try:
        # Usar el router para obtener el mejor provider disponible
        best = llm_router.get_best_provider("medium")
        if not best:
            return None
        
        provider_name, api_key = best
        client = llm_router.get_client(provider_name, api_key)
        heal_model = llm_router.get_model_name(provider_name)
        
        response = client.chat.completions.create(
            model=heal_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2
        )
        
        healed_code = response.choices[0].message.content.strip()
        
        # Limpiar wrappers de markdown si el LLM los agrega
        if healed_code.startswith("```python"):
            healed_code = healed_code[9:]
        elif healed_code.startswith("```"):
            healed_code = healed_code[3:]
        if healed_code.endswith("```"):
            healed_code = healed_code[:-3]
        
        return healed_code.strip()
    except Exception as e:
        print(f"[Self-Healer] Error intentando reparar: {e}")
        return None
