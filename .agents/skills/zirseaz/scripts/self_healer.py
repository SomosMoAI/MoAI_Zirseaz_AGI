"""
Zirseaz Self-Healing Engine — Recuperacion automatica de errores.

Intercepta errores de ejecucion en el loop de ReAct, envia el stacktrace al LLM
junto con el codigo original, y solicita una correccion. Se reintenta hasta N veces.
"""
import os, sys, time

_UTILS_DIR = os.path.join(os.getcwd(), ".agents", "skills", "zirseaz", "utils")
if _UTILS_DIR not in sys.path:
    sys.path.insert(0, _UTILS_DIR)

import env_loader
import llm_router

def attempt_heal(original_code, error_output, model_name=""):
    """
    Solicita al LLM que arregle el codigo que fallo.
    """
    if not model_name:
        return None
        
    system_prompt = (
        "Eres el motor de auto-reparacion de Zirseaz. "
        "Se ejecuto un codigo Python que fallo con un error. "
        "Tu unica tarea es reescribir el codigo para que funcione correctamente.\n\n"
        "REGLAS:\n"
        "1. Devuelve SOLO codigo Python, nada mas.\n"
        "2. No uses formato markdown (```python), solo el codigo crudo.\n"
        "3. Maneja excepciones si es necesario."
    )
    
    user_prompt = f"CODIGO ORIGINAL:\n{original_code}\n\nERROR:\n{error_output}\n\nREESCRITURA CORRECTA:"
    
    try:
        provider_name = next((p for p, c in llm_router.PROVIDERS.items() if c["model"] == model_name), "deepseek")
        client = llm_router.get_client(provider_name, llm_router.PROVIDERS[provider_name]["api_key_env"])
        if not client: return None
        
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2
        )
        
        healed_code = response.choices[0].message.content.strip()
        if healed_code.startswith("```python"): healed_code = healed_code[9:]
        elif healed_code.startswith("```"): healed_code = healed_code[3:]
        if healed_code.endswith("```"): healed_code = healed_code[:-3]
        
        return healed_code.strip()
    except Exception as e:
        return None
