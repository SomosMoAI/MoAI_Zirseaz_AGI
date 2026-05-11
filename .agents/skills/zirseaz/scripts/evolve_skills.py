import os
import argparse
import sys
from openai import OpenAI
import resource_hunter

def get_llm_client(provider_tuple):
    provider_name, api_key = provider_tuple
    
    if provider_name == "deepseek":
        return OpenAI(api_key=api_key, base_url="https://api.deepseek.com"), "deepseek-chat"
    elif provider_name == "groq":
        return OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1"), "llama3-70b-8192"
    elif provider_name == "gemini":
        # Nota: Por simplicidad, y si el usuario lo configuró así, 
        # OpenAI SDK puede enrutar a Gemini si se tiene un proxy, 
        # pero asumiremos uso directo en el caso de groq/deepseek.
        # Fallback de Gemini asume OpenAI compat o se avisa que no soporta.
        return OpenAI(api_key=api_key, base_url="https://generativelanguage.googleapis.com/v1beta/openai/"), "gemini-1.5-pro"
        
    raise ValueError(f"Proveedor no soportado: {provider_name}")

def analyze_skill(skill_name):
    success, provider = resource_hunter.survival_check()
    if not success:
        print("Zirseaz ha detenido la evolución. Esperando recursos del Líder.")
        sys.exit(1)
        
    skill_path = os.path.join(".agents", "skills", skill_name, "SKILL.md")
    if not os.path.exists(skill_path):
        raise FileNotFoundError(f"No se encontró SKILL.md para {skill_name}")
        
    with open(skill_path, "r", encoding="utf-8") as f:
        skill_content = f.read()

    # Cargar código Python (scripts) para analizar
    scripts_content = ""
    scripts_dir = os.path.join(".agents", "skills", skill_name, "scripts")
    if os.path.exists(scripts_dir):
        for py_file in os.listdir(scripts_dir):
            if py_file.endswith(".py"):
                with open(os.path.join(scripts_dir, py_file), "r", encoding="utf-8") as pf:
                    scripts_content += f"\n--- Archivo: {py_file} ---\n"
                    scripts_content += pf.read()
                    
    client, model_name = get_llm_client(provider)
    
    system_prompt = """Eres Zirseaz, el Meta-Agente Evolutivo y Arquitecto Jefe (MO-AI.CL).
    Tu objetivo es auditar el SKILL.md y los scripts de un sub-agente y proponer optimizaciones de CÓDIGO REAL.
    Tus directrices:
    1. Busca cuellos de botella en el código Python y sugiere refactorizaciones que ahorren tokens o tiempo.
    2. Identifica si el agente está cumpliendo la Regla del '¿Y Qué?' y no usa vocabulario prohibido.
    3. Tu propuesta debe incluir código listo para copiar y pegar (o ejecutar vía <CMD_EXECUTE> por ti mismo).
    
    Salida requerida:
    Devuelve un informe con:
    - [DIAGNÓSTICO]: Qué ineficiencias encontraste.
    - [PARCHES]: Bloques de código (Python) para arreglar los scripts, indicando qué archivo reemplazar.
    - [SKILL_UPDATE]: Si el SKILL.md necesita ser actualizado, pon la nueva versión completa en Markdown.
    """
    
    print(f"Analizando {skill_name} con {model_name}...")
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Aquí está el SKILL.md actual:\n\n{skill_content}\n\nAquí está el código de los scripts:\n{scripts_content}"}
        ]
    )
    
    proposal = response.choices[0].message.content
    print("Análisis completado.")
    
    # Save proposal to a temporary file
    output_path = os.path.join(".agents", "skills", "zirseaz", f"proposal_{skill_name}.md")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(proposal)
        
    print(f"Propuesta guardada en: {output_path}")
    return output_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Zirseaz Evaluator")
    parser.add_argument("skill_name", help="Nombre de la skill a evaluar (ej. marketing)")
    args = parser.parse_args()
    
    try:
        analyze_skill(args.skill_name)
    except Exception as e:
        print(f"Error: {e}")
