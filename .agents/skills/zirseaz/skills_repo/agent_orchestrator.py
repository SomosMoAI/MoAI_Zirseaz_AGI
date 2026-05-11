import os
import sys

def orchestrate_agent(agent_name, task_description):
    """
    Invoca a un sub-agente específico, le asigna una tarea y devuelve su respuesta.
    Requiere que el sub-agente exista en .agents/skills/ y tenga un SKILL.md.
    """
    base_dir = os.path.join(os.getcwd(), ".agents", "skills", agent_name)
    skill_path = os.path.join(base_dir, "SKILL.md")
    
    if not os.path.exists(skill_path):
        return f"Error: No se encontró el agente '{agent_name}'. Revisa si está forjado."
        
    try:
        with open(skill_path, "r", encoding="utf-8") as f:
            skill_content = f.read()
            
        # Extraer el system prompt (simplificado, asumiendo que todo el archivo sirve de contexto)
        agent_system_prompt = f"Eres un sub-agente especializado llamado {agent_name}.\nTu configuración es la siguiente:\n{skill_content}\nResuelve la tarea que se te asigne basándote estrictamente en tu rol."
        
        # Importar el módulo evolve_skills que tiene la lógica de LLM
        zirseaz_scripts_dir = os.path.join(os.getcwd(), ".agents", "skills", "zirseaz", "scripts")
        if zirseaz_scripts_dir not in sys.path:
            sys.path.append(zirseaz_scripts_dir)
            
        import evolve_skills
        import resource_hunter
        
        # Obtener un LLM disponible
        success, provider = resource_hunter.survival_check()
        if not success:
            return "Error crítico: El enjambre no tiene créditos/API keys para operar."
            
        client, model_name = evolve_skills.get_llm_client(provider)
        
        # Invocar al sub-agente
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": agent_system_prompt},
                {"role": "user", "content": f"TAREA: {task_description}"}
            ]
        )
        
        return f"[Respuesta de {agent_name}]:\n{response.choices[0].message.content}"
        
    except Exception as e:
        return f"Error al orquestar al agente {agent_name}: {e}"
